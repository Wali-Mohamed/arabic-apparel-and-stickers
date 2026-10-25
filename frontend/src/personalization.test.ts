import { describe, expect, it } from 'vitest'

import { MAX_PERSONALIZATION_GRAPHEMES, normalizeAndValidateArabicLetter, normalizeAndValidateArabicText } from './personalization'

describe('normalizeAndValidateArabicText', () => {
  it('accepts Arabic text with diacritics, hyphens, and digits', () => {
    expect(normalizeAndValidateArabicText('مَرْحَبًا-١٢ 3').error).toBe('')
  })

  it('rejects invalid characters and text over the grapheme limit', () => {
    expect(normalizeAndValidateArabicText('مرحبا!').error).toContain('Arabic letters')
    expect(normalizeAndValidateArabicText('ا'.repeat(MAX_PERSONALIZATION_GRAPHEMES + 1)).error).toContain('graphemes')
  })
})

it('accepts one Arabic letter and rejects multiple letters for letter-only tags', () => {
  expect(normalizeAndValidateArabicLetter('\u0628\u0650').error).toBe('')
  expect(normalizeAndValidateArabicLetter('\u0628\u062a').error).toContain('one Arabic letter')
})
