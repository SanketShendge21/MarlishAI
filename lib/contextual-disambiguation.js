/**
 * CONTEXTUAL DISAMBIGUATION ENGINE
 * 
 * Solves: "kal" → tomorrow vs yesterday
 *         "bro/bhai" → vocative slang vs family noun
 *         "scene" → plan vs situation
 *         slash-separated meanings → single best pick
 * 
 * Uses a context-window approach: examine neighboring tokens
 * to score which meaning is most likely.
 */

// ============================================================
// AMBIGUOUS WORD DEFINITIONS
// Each word has multiple meanings with context signals
// ============================================================
const AMBIGUOUS_WORDS = {
  kal: {
    meanings: [
      {
        value: 'tomorrow',
        score: 0.55, // slight default bias toward future
        signals: {
          boost: ['milte', 'milenge', 'milna', 'chalte', 'plan', 'scene', 'aana', 'aao', 'aa',
                  'jayenge', 'karenge', 'hoga', 'hogi', 'dekhte', 'dekhenge', 'pakka',
                  'chalega', 'done', 'meeting', 'call', 'baad', 'subah', 'sham', 'raat'],
          inhibit: ['gaya', 'gayi', 'gaye', 'tha', 'thi', 'the', 'aaya', 'aayi', 'aaye',
                    'kiya', 'ki', 'bola', 'boli', 'bole', 'mila', 'mili', 'mile', 'dekha',
                    'dekhi', 'suna', 'suni', 'khaya', 'khayi', 'pehle', 'pichle'],
        },
      },
      {
        value: 'yesterday',
        score: 0.45,
        signals: {
          boost: ['gaya', 'gayi', 'gaye', 'tha', 'thi', 'the', 'aaya', 'aayi', 'aaye',
                  'kiya', 'ki', 'bola', 'boli', 'bole', 'mila', 'mili', 'mile', 'dekha',
                  'dekhi', 'suna', 'suni', 'khaya', 'khayi', 'pehle', 'pichle', 'raha'],
          inhibit: ['milte', 'milenge', 'plan', 'scene', 'hoga', 'hogi', 'karenge', 'jayenge'],
        },
      },
    ],
  },

  bro: {
    meanings: [
      {
        value: 'Bro',
        score: 0.9, // almost always vocative in chat
        tag: 'vocative',
        signals: {
          boost: ['kidhar', 'kya', 'chal', 'sun', 'yaar', 'scene', 'milte', 'bol', 'bata',
                  'kaise', 'tu', 'tera', 'tere', 'aaja', 'chill'],
          inhibit: ['mera', 'uska', 'ka', 'ke'],
        },
      },
      {
        value: 'brother',
        score: 0.1,
        tag: 'noun',
        signals: {
          boost: ['mera', 'uska', 'bada', 'chhota', 'ka', 'ke', 'ki', 'hai', 'naam'],
          inhibit: ['kidhar', 'kya', 'scene', 'milte', 'chal'],
        },
      },
    ],
  },

  bhai: {
    meanings: [
      {
        value: 'Bro',
        score: 0.7,
        tag: 'vocative',
        signals: {
          boost: ['kidhar', 'kya', 'chal', 'sun', 'yaar', 'scene', 'milte', 'bol', 'bata',
                  'kaise', 'tu', 'aaja', 'sab'],
          inhibit: ['mera', 'uska', 'bada', 'chhota', 'ka', 'ke', 'naam'],
        },
      },
      {
        value: 'brother',
        score: 0.3,
        tag: 'noun',
        signals: {
          boost: ['mera', 'uska', 'bada', 'chhota', 'ka', 'ke', 'ki', 'hai', 'naam'],
          inhibit: ['kidhar', 'kya', 'scene', 'milte', 'chal'],
        },
      },
    ],
  },

  yaar: {
    meanings: [
      { value: 'dude', score: 0.8, tag: 'vocative',
        signals: { boost: ['kya', 'chal', 'sun', 'bol', 'milte'], inhibit: ['mera', 'ka'] }},
      { value: 'friend', score: 0.2, tag: 'noun',
        signals: { boost: ['mera', 'accha', 'purana', 'ka'], inhibit: ['kya', 'chal'] }},
    ],
  },

  scene: {
    meanings: [
      { value: 'plan', score: 0.6,
        signals: { boost: ['kya', 'hai', 'batao', 'kal', 'aaj', 'koi'], inhibit: ['dekh', 'movie', 'film'] }},
      { value: 'situation', score: 0.3,
        signals: { boost: ['yeh', 'woh', 'kaisa', 'bura', 'accha'], inhibit: ['kya', 'hai', 'batao'] }},
      { value: 'scene', score: 0.1,
        signals: { boost: ['movie', 'film', 'show', 'drama'], inhibit: ['kya', 'hai'] }},
    ],
  },

  chal: {
    meanings: [
      { value: "let's go", score: 0.5,
        signals: { boost: ['chalo', 'chalte', 'hai', 'ab', 'jaldi'], inhibit: ['raha', 'rahi'] }},
      { value: 'going on', score: 0.3,
        signals: { boost: ['kya', 'raha', 'rahi'], inhibit: ['ab', 'jaldi'] }},
      { value: 'move', score: 0.2,
        signals: { boost: ['idhar', 'udhar', 'yahan', 'wahan'], inhibit: ['kya', 'raha'] }},
    ],
  },

  acha: {
    meanings: [
      { value: 'good', score: 0.4,
        signals: { boost: ['bahut', 'kitna', 'hai', 'lagta', 'laga', 'tha'], inhibit: [] }},
      { value: 'okay', score: 0.4,
        signals: { boost: ['theek', 'chal', 'ho', 'gaya'], inhibit: ['bahut'] }},
      { value: 'really?', score: 0.2,
        signals: { boost: ['kya', 'sach', 'sachme', 'matlab'], inhibit: ['bahut', 'hai'] }},
    ],
  },
};

// ============================================================
// TENSE MARKERS — classify tokens as past/present/future
// ============================================================
const PAST_MARKERS = new Set([
  'tha', 'thi', 'the', 'gaya', 'gayi', 'gaye', 'aaya', 'aayi', 'aaye',
  'kiya', 'ki', 'kiye', 'bola', 'boli', 'bole', 'mila', 'mili', 'mile',
  'dekha', 'dekhi', 'suna', 'suni', 'khaya', 'khayi', 'liya', 'li',
  'diya', 'di', 'chala', 'chali', 'chale', 'raha', 'rahi', 'rahe',
  'hua', 'hui', 'hue', 'para', 'padha', 'likha',
]);

const FUTURE_MARKERS = new Set([
  'milte', 'milenge', 'jayenge', 'karenge', 'hoga', 'hogi', 'honge',
  'aayenge', 'dekhenge', 'bolenge', 'chalenge', 'khayenge',
  'plan', 'scene', 'pakka', 'done', 'meeting', 'chalega',
]);

// ============================================================
// CORE: Disambiguate a word using its context window
// ============================================================
export function disambiguate(word, allTokens, tokenIndex) {
  const lower = word.toLowerCase();
  const entry = AMBIGUOUS_WORDS[lower];
  if (!entry) return null;

  // Build context window (±3 tokens)
  const windowSize = 3;
  const contextTokens = [];
  for (let i = Math.max(0, tokenIndex - windowSize); i < Math.min(allTokens.length, tokenIndex + windowSize + 1); i++) {
    if (i !== tokenIndex) contextTokens.push(allTokens[i].toLowerCase());
  }

  // Score each meaning
  let bestMeaning = entry.meanings[0];
  let bestScore = -Infinity;

  for (const meaning of entry.meanings) {
    let score = meaning.score;

    for (const ctx of contextTokens) {
      if (meaning.signals.boost.includes(ctx)) score += 0.25;
      if (meaning.signals.inhibit.includes(ctx)) score -= 0.3;
    }

    if (score > bestScore) {
      bestScore = score;
      bestMeaning = meaning;
    }
  }

  return {
    value: bestMeaning.value,
    tag: bestMeaning.tag || null,
    confidence: Math.min(1.0, Math.max(0, bestScore)),
  };
}

// ============================================================
// SLASH RESOLVER — pick best meaning from "tomorrow/yesterday"
// ============================================================
export function resolveSlash(rawMeaning, word, allTokens, tokenIndex) {
  if (!rawMeaning || !rawMeaning.includes('/')) return rawMeaning;

  const options = rawMeaning.split('/').map(s => s.trim());
  if (options.length < 2) return rawMeaning;

  // Build context window
  const contextTokens = [];
  for (let i = Math.max(0, tokenIndex - 3); i < Math.min(allTokens.length, tokenIndex + 4); i++) {
    if (i !== tokenIndex) contextTokens.push(allTokens[i].toLowerCase());
  }

  // Detect tense from context
  let pastScore = 0, futureScore = 0;
  for (const ctx of contextTokens) {
    if (PAST_MARKERS.has(ctx)) pastScore++;
    if (FUTURE_MARKERS.has(ctx)) futureScore++;
  }

  // For known slash patterns
  if (options.includes('tomorrow') && options.includes('yesterday')) {
    return futureScore >= pastScore ? 'tomorrow' : 'yesterday';
  }
  if (options.includes('brother') && options.includes('bro')) {
    return 'bro'; // always prefer casual in chat
  }
  if (options.includes('he') && options.includes('she')) {
    return 'they'; // safe fallback
  }

  // Default: pick first option (most common meaning)
  return options[0];
}

// ============================================================
// VOCATIVE DETECTION — should this word get a comma?
// ============================================================
export function isVocative(word, position, totalTokens) {
  const vocatives = new Set(['bro', 'bhai', 'yaar', 'dude', 'boss', 're', 'didi', 'behen']);
  if (!vocatives.has(word.toLowerCase())) return false;
  // Vocative at start or end of sentence
  return position === 0 || position === totalTokens - 1;
}

export { AMBIGUOUS_WORDS, PAST_MARKERS, FUTURE_MARKERS };
