export const MAX_PERSONALIZATION_GRAPHEMES = 24

const arabicScript = /^\p{Script=Arabic}$/u
const letter = /^\p{L}$/u
const mark = /^\p{M}$/u

export function normalizeAndValidateArabicText(value: string): { value: string; error: string } {
  const normalized = value.normalize('NFC')
  if (!normalized) return { value: normalized, error: 'Enter personalized Arabic text.' }

  const graphemeCount = [...new Intl.Segmenter('ar', { granularity: 'grapheme' }).segment(normalized)].length
  if (graphemeCount > MAX_PERSONALIZATION_GRAPHEMES) {
    return { value: normalized, error: `Use ${MAX_PERSONALIZATION_GRAPHEMES} graphemes or fewer.` }
  }

  let hasArabicLetter = false
  for (const character of normalized) {
    if (arabicScript.test(character) && letter.test(character)) {
      hasArabicLetter = true
      continue
    }
    if (mark.test(character) || character === ' ' || character === '-') continue
    if (/^[0-9\u0660-\u0669\u06F0-\u06F9]$/.test(character)) continue
    return { value: normalized, error: 'Use Arabic letters, diacritics, spaces, hyphens, and Arabic or Western digits only.' }
  }

  return hasArabicLetter
    ? { value: normalized, error: '' }
    : { value: normalized, error: 'Include at least one Arabic letter.' }
}

export function normalizeAndValidateArabicLetter(value: string): { value: string; error: string } {
  const result = normalizeAndValidateArabicText(value)
  if (result.error) return result
  const graphemes = [...new Intl.Segmenter('ar', { granularity: 'grapheme' }).segment(result.value)]
  if (graphemes.length !== 1 || !/^\p{Script=Arabic}\p{M}*$/u.test(result.value)) {
    return { value: result.value, error: 'Use one Arabic letter, with optional diacritics.' }
  }
  return result
}
