/**
 * TYPO MAP — Layer 1: Input Normalization
 * 
 * Maps common Hinglish/Marlish spelling variations,
 * abbreviations, and repeated-letter typos to their
 * canonical dictionary form.
 * 
 * This runs BEFORE dictionary lookup so that
 * "rha hai" is normalized to "raha hai" and matches
 * the phrase dictionary entry.
 */

// Common shorthand → canonical form
const TYPO_MAP = {
  // Hinglish common shortenings
  'kr':    'kar',
  'krr':   'kar',
  'kro':   'karo',
  'krte':  'karte',
  'rha':   'raha',
  'rhi':   'rahi',
  'rhe':   'rahe',
  'h':     'hai',
  'hu':    'hoon',
  'hn':    'haan',
  'hna':   'haan',
  'nhi':   'nahi',
  'nai':   'nahi',
  'ni':    'nahi',
  'mt':    'mat',
  'bht':   'bahut',
  'bhut':  'bahut',
  'bol':   'bolo',
  'chl':   'chal',
  'chlo':  'chalo',
  'acha':  'accha',
  'aaj':   'aaj',
  'ky':    'kya',
  'kyu':   'kyun',
  'kyuu':  'kyun',
  'kaise': 'kaise',
  'kese':  'kaise',
  'sb':    'sab',
  'sbko':  'sabko',
  'tujhe': 'tujhe',
  'tuje':  'tujhe',
  'muje':  'mujhe',
  'mje':   'mujhe',
  'mjhe':  'mujhe',
  'vo':    'woh',
  'wo':    'woh',
  'ye':    'yeh',
  'y':     'yeh',
  'thk':   'theek',
  'thik':  'theek',
  'tik':   'theek',
  'abhi':  'abhi',
  'ab':    'ab',
  'bhai':  'bhai',
  'bro':   'bro',
  'yar':   'yaar',
  'yr':    'yaar',
  'pls':   'please',
  'plz':   'please',
  'msg':   'message',
  'pic':   'picture',
  'pics':  'pictures',
  'ghr':   'ghar',
  'ghri':  'ghari',
  'gari':  'ghari',
  'kidhr': 'kidhar',
  'kidr':  'kidhar',

  // Marlish common shortenings
  'ahs':    'ahes',
  'ahe':    'aahe',
  'mla':    'mala',
  'tla':    'tula',
  'kth':    'kuthe',
  'kuthe':  'kuthe',
  'kt':     'kuthe',
  'ghari':  'ghari',
  'ghri':   'ghari',
  'jto':    'jato',
  'yto':    'yeto',
  'krt':    'karto',
  'krto':   'karto',
  'naav':   'nav',
  'aahe':   'aahe',
  'ahee':   'aahe',
};

/**
 * Normalize a single token using the typo map.
 * Returns the canonical form, or the original if no mapping exists.
 */
export function normalizeToken(token) {
  const lower = token.toLowerCase();
  return TYPO_MAP[lower] || lower;
}

/**
 * Normalize an entire input string:
 * 1. Collapse repeated letters (aaaaj → aaj, pleeeease → please)
 * 2. Apply typo map to each word
 * 3. Return cleaned string
 */
export function normalizeInput(text) {
  // Step 1: Collapse 3+ repeated letters to 2 (preserves "aa" which is valid)
  let cleaned = text.replace(/(.)\1{2,}/g, '$1$1');

  // Step 2: Split, normalize each word, rejoin
  const words = cleaned.split(/(\s+)/); // preserve whitespace
  const normalized = words.map(segment => {
    // Skip whitespace segments
    if (/^\s+$/.test(segment)) return segment;
    // Skip punctuation-only segments
    if (/^[^\w]+$/.test(segment)) return segment;
    return normalizeToken(segment);
  });

  return normalized.join('');
}

export { TYPO_MAP };
