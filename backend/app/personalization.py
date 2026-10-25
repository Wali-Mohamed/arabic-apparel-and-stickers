import unicodedata

import regex
from fastapi import HTTPException

MAX_PERSONALIZATION_GRAPHEMES = 24
ARABIC_SCRIPT = regex.compile(r"\A\p{Script=Arabic}\Z")


def normalize_and_validate_arabic_text(value: object) -> str:
    if not isinstance(value, str):
        raise HTTPException(status_code=422, detail="Personalized text is required")

    text = unicodedata.normalize("NFC", value)
    if not text:
        raise HTTPException(status_code=422, detail="Personalized text is required")

    grapheme_count = len(regex.findall(r"\X", text))
    if grapheme_count > MAX_PERSONALIZATION_GRAPHEMES:
        raise HTTPException(
            status_code=422,
            detail=f"Personalized text must be {MAX_PERSONALIZATION_GRAPHEMES} graphemes or fewer",
        )

    has_arabic_letter = False
    for character in text:
        category = unicodedata.category(character)
        if category.startswith("L") and ARABIC_SCRIPT.fullmatch(character):
            has_arabic_letter = True
            continue
        if category.startswith("M") or character == " " or character == "-":
            continue
        if "0" <= character <= "9" or "\u0660" <= character <= "\u0669" or "\u06F0" <= character <= "\u06F9":
            continue
        raise HTTPException(
            status_code=422,
            detail="Personalized text may contain Arabic letters, diacritics, spaces, hyphens, and Arabic or Western digits only",
        )

    if not has_arabic_letter:
        raise HTTPException(status_code=422, detail="Personalized text must include at least one Arabic letter")

    return text


def normalize_and_validate_arabic_letter(value: object) -> str:
    text = normalize_and_validate_arabic_text(value)
    graphemes = regex.findall(r"\X", text)
    if len(graphemes) != 1:
        raise HTTPException(status_code=422, detail="Small Arabic letter-only tags accept one Arabic letter only")

    base_letters = [
        character
        for character in text
        if unicodedata.category(character).startswith("L") and ARABIC_SCRIPT.fullmatch(character)
    ]
    if len(base_letters) != 1 or any(
        not unicodedata.category(character).startswith(("L", "M")) for character in text
    ):
        raise HTTPException(status_code=422, detail="Small Arabic letter-only tags accept one Arabic letter only")
    return text
