export const LANGUAGES = [
  { code: 'hinglish', label: 'Hinglish', script: 'Latin', flag: '🇮🇳' },
  { code: 'english',  label: 'English',  script: 'Latin', flag: '🇬🇧' },
  { code: 'marlish',  label: 'Marlish',  script: 'Latin', flag: '🇮🇳' },
  { code: 'marathi',  label: 'Marathi',  script: 'Devanagari', flag: '🇮🇳' },
  { code: 'hindi',    label: 'Hindi',    script: 'Devanagari', flag: '🇮🇳' },
];

// All valid translation pairs (direct + pivot-based)
export const VALID_PAIRS = [
  // Hinglish ↔ English (direct)
  ['hinglish', 'english'],
  ['english',  'hinglish'],

  // Marlish ↔ English (direct)
  ['marlish',  'english'],
  ['english',  'marlish'],

  // Cross-family (pivot through English)
  ['hinglish', 'marlish'],
  ['marlish',  'hinglish'],

  // Script-based
  ['marathi',  'english'],
  ['hindi',    'english'],
  ['english',  'marathi'],
  ['english',  'hindi'],
];

export function isValidPair(source, target) {
  return VALID_PAIRS.some(([s, t]) => s === source && t === target);
}

export function getLanguage(code) {
  return LANGUAGES.find(lang => lang.code === code);
}

export function getValidTargets(sourceCode) {
  return VALID_PAIRS
    .filter(([s]) => s === sourceCode)
    .map(([, t]) => getLanguage(t))
    .filter(Boolean);
}
