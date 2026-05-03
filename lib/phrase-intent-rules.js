/**
 * PHRASE INTENT ENGINE
 * 
 * Detects full idiomatic patterns in Hinglish/Marlish input
 * and maps them directly to natural English output.
 * 
 * This runs BEFORE word-by-word translation.
 * A match here skips the word pipeline entirely.
 * 
 * Patterns are ordered longest-first and support:
 *   - Exact multi-word matches
 *   - Partial matches with remainder translation
 *   - Compound verb detection (kar raha, ho gaya, etc.)
 */

// ============================================================
// COMPOUND VERB PATTERNS
// These are multi-word verb forms that must be translated as units
// ============================================================
const COMPOUND_VERBS = {
  // kar + tense
  'kar raha hai': 'is doing',
  'kar raha hu': 'am doing',
  'kar raha hoon': 'am doing',
  'kar rahi hai': 'is doing',
  'kar rahe hai': 'are doing',
  'kar rahe hain': 'are doing',
  'kar raha tha': 'was doing',
  'kar rahi thi': 'was doing',
  'kar rahe the': 'were doing',
  'kar raha': 'doing',
  'kar rahi': 'doing',
  'kar rahe': 'doing',
  'karte hai': 'do',
  'karte hain': 'do',
  'karti hai': 'does',
  'karna hai': 'have to do',
  'karna tha': 'had to do',
  'kar diya': 'did it',
  'kar dunga': 'will do',
  'kar dena': 'do it',
  'kar liya': 'done',
  'kar lo': 'do it',

  // ja + tense
  'ja raha hai': 'is going',
  'ja raha hu': 'am going',
  'ja raha hoon': 'am going',
  'ja rahi hai': 'is going',
  'ja rahe hai': 'are going',
  'ja rahe hain': 'are going',
  'ja raha tha': 'was going',
  'ja rahi thi': 'was going',
  'jata hai': 'goes',
  'jata hu': 'go',
  'jata hoon': 'go',
  'jati hai': 'goes',
  'jana hai': 'have to go',
  'jana tha': 'had to go',
  'ja sakta hu': 'can go',
  'ja sakta hai': 'can go',

  // aa + tense
  'aa raha hai': 'is coming',
  'aa raha hu': 'am coming',
  'aa raha hoon': 'am coming',
  'aa rahi hai': 'is coming',
  'aa rahe hai': 'are coming',
  'aata hai': 'comes',
  'aata hu': 'come',
  'aati hai': 'comes',
  'aana hai': 'have to come',
  'aa gaya': 'has arrived',
  'aa gayi': 'has arrived',
  'aa jao': 'come over',
  'aa ja': 'come over',

  // kha + tense
  'kha raha hai': 'is eating',
  'kha raha hu': 'am eating',
  'kha rahi hai': 'is eating',
  'kha liya': 'finished eating',
  'khana kha': 'eat food',
  'khana khaya': 'ate food',

  // de + tense
  'de raha hai': 'is giving',
  'de raha hu': 'am giving',
  'de diya': 'gave',
  'de dunga': 'will give',
  'de do': 'give',
  'de de': 'give',

  // le + tense
  'le raha hai': 'is taking',
  'le raha hu': 'am taking',
  'le liya': 'took',
  'le lo': 'take it',
  'le aao': 'bring',

  // bol + tense
  'bol raha hai': 'is saying',
  'bol raha hu': 'am saying',
  'bol raha tha': 'was saying',
  'bol rahi hai': 'is saying',
  'bola tha': 'had said',

  // dekh + tense
  'dekh raha hai': 'is watching',
  'dekh raha hu': 'am watching',
  'dekh rahi hai': 'is watching',
  'dekha hai': 'have seen',
  'dekh lena': 'check it',
  'dekh lo': 'see for yourself',
  'dekhte hai': "let's see",

  // sun + tense
  'sun raha hai': 'is listening',
  'sun raha hu': 'am listening',
  'suna hai': 'have heard',
  'sun lo': 'listen',

  // ho + completive
  'ho gaya': "it's done",
  'ho gayi': "it's done",
  'ho gaye': 'done',
  'ho raha hai': 'is happening',
  'ho raha': 'happening',
  'ho rahi hai': 'is happening',
  'ho jayega': 'it will happen',
  'ho jaega': 'it will happen',
  'hone wala hai': 'about to happen',

  // mil + tense
  'mil gaya': 'found it',
  'mil gayi': 'found it',
  'mil jayega': 'will get it',
  'milte hai': "let's meet",
  'milte hain': "let's meet",
  'milna hai': 'need to meet',

  // so + tense
  'so raha hai': 'is sleeping',
  'so raha hu': 'am sleeping',
  'so gaya': 'fell asleep',
  'so ja': 'go to sleep',

  // baith + tense
  'baith ja': 'sit down',
  'baithe hai': 'are sitting',
  'baithe hain': 'are sitting',

  // chal + tense
  'chal raha hai': 'is going on',
  'chal rahi hai': 'is going on',
  'chal raha': 'going on',
  'chalte hai': "let's go",
  'chalte hain': "let's go",

  // samajh
  'samajh aa gaya': 'understood',
  'samajh nahi aaya': "didn't understand",
  'samajh aata hai': 'understand',

  // pata
  'pata hai': 'I know',
  'pata nahi': "don't know",
  'pata chal gaya': 'found out',
  'pata chala': 'came to know',
};

// ============================================================
// FULL SENTENCE INTENT PATTERNS
// These bypass word-by-word translation entirely
// ============================================================
const INTENT_PATTERNS = {
  // Greetings / Status
  'kya haal hai': 'How are you?',
  'kaise ho': 'How are you?',
  'kaise ho bro': 'Bro, how are you?',
  'kaise ho bhai': 'Bro, how are you?',
  'kaise ho yaar': 'Dude, how are you?',
  'sab theek': "Everything's fine.",
  'sab accha': "Everything's good.",
  'main theek hu': "I'm fine.",
  'main theek hoon': "I'm fine.",

  // Plans / Status
  'scene kya hai': "What's the plan?",
  'kya scene hai': "What's the plan?",
  'kya chal raha hai': "What's going on?",
  'kya chal raha': "What's going on?",
  'kya ho raha hai': "What's happening?",
  'kya ho raha': "What's happening?",
  'kya kar raha hai': 'What are you doing?',
  'kya kar raha': 'What are you doing?',
  'kya kar rahi hai': 'What are you doing?',
  'kya kar rahi': 'What are you doing?',
  'kya kar rahe ho': 'What are you doing?',
  'kya kar rahe': 'What are you doing?',

  // Location
  'kidhar hai': 'Where are you?',
  'kahan hai': 'Where is it?',
  'kahan ho': 'Where are you?',
  'kahan hai tu': 'Where are you?',
  'tu kidhar hai': 'Where are you?',
  'tu kahan hai': 'Where are you?',

  // Time
  'kab aayega': 'When will you come?',
  'kab aaoge': 'When will you come?',
  'kab aa rahe ho': 'When are you coming?',
  'kab milenge': 'When will we meet?',
  'kitna time lagega': 'How long will it take?',

  // Meeting
  'milte hai': "Let's meet.",
  'milte hain': "Let's meet.",
  'kal milte hai': "Let's meet tomorrow.",
  'aaj milte hai': "Let's meet today.",
  'chalo milte hai': "Come on, let's meet.",

  // Going
  'ghar ja raha hu': "I'm going home.",
  'ghar ja raha hoon': "I'm going home.",
  'ghar ja rahi hu': "I'm going home.",
  'main ghar ja raha hu': "I'm going home.",
  'main aa raha hu': "I'm coming.",
  'main aa raha hoon': "I'm coming.",
  'main aa raha': "I'm coming.",
  'main ja raha hu': "I'm leaving.",
  'main ja raha hoon': "I'm leaving.",

  // Responses
  'sahi hai': "That's right.",
  'bilkul': 'Absolutely.',
  'pakka': 'For sure.',
  'done hai': "It's done.",
  'ho gaya': "It's done.",
  'ho jayega': 'It will be done.',
  'theek hai': "It's okay.",
  'chal theek hai': "Alright, fine.",
  'mat kar': "Don't do it.",
  'rehne de': 'Leave it.',
  'chill kar': 'Relax.',
  'tension mat le': "Don't worry.",
  'chod de': 'Let it go.',
  'koi baat nahi': 'No problem.',
  'koi nahi': 'No one. / Never mind.',
  'pata nahi': "I don't know.",
  'mujhe nahi pata': "I don't know.",

  // Marlish intent patterns
  'tu kuthe ahes': 'Where are you?',
  'kuthe ahes': 'Where are you?',
  'kuthe aahe': 'Where is it?',
  'kaay challay': "What's going on?",
  'kaay zhalay': 'What happened?',
  'kasa ahes': 'How are you?',
  'kashi ahes': 'How are you?',
  'mi ghari jato': "I'm going home.",
  'mi ghari yeto': "I'm coming home.",
  'ghari jato': 'Going home.',
  'ghari yeto': 'Coming home.',
  'kiti vaajle': 'What time is it?',
  'jevlas ka': 'Have you eaten?',
  'jevlis ka': 'Have you eaten?',
  'majha nav': 'My name is',
  'baher aahe': 'Is outside.',
  'office madhe aahe': 'Is in the office.',
  'office madhe': 'In the office.',
};

// ============================================================
// TENSE VERB MAP — single past/present/future verbs
// that the flat dictionary misses
// ============================================================
const TENSE_VERBS = {
  // Past tense
  'gaya': 'went',
  'gayi': 'went',
  'gaye': 'went',
  'aaya': 'came',
  'aayi': 'came',
  'aaye': 'came',
  'kiya': 'did',
  'ki': 'did',
  'kiye': 'did',
  'bola': 'said',
  'boli': 'said',
  'bole': 'said',
  'mila': 'met',
  'mili': 'met',
  'mile': 'met',
  'dekha': 'saw',
  'dekhi': 'saw',
  'suna': 'heard',
  'suni': 'heard',
  'khaya': 'ate',
  'khayi': 'ate',
  'liya': 'took',
  'li': 'took',
  'diya': 'gave',
  'di': 'gave',
  'chala': 'walked',
  'chali': 'walked',
  'chale': 'walked',
  'padha': 'read',
  'likha': 'wrote',
  'socha': 'thought',
  'roya': 'cried',
  'hasa': 'laughed',
  'bhaga': 'ran',
  'hua': 'happened',
  'hui': 'happened',
  'hue': 'happened',
  'baitha': 'sat',
  'baithi': 'sat',
  'khela': 'played',
  'seekha': 'learned',

  // Present continuous helpers
  'raha': '-ing',
  'rahi': '-ing',
  'rahe': '-ing',

  // Future markers
  'dunga': 'will give',
  'lunga': 'will take',
  'jaunga': 'will go',
  'aaunga': 'will come',
  'karunga': 'will do',
  'dekhunga': 'will see',
  'bolunga': 'will say',
  'milenge': 'will meet',
  'jayenge': 'will go',
  'karenge': 'will do',
  'aayenge': 'will come',
  'dekhenge': 'will see',
  'bolenge': 'will say',
  'chalenge': 'will walk',
  'khayenge': 'will eat',

  // Modal
  'sakta': 'can',
  'sakti': 'can',
  'sakte': 'can',
  'chahiye': 'should',
  'chahte': 'want to',
  'chahta': 'want to',
  'chahti': 'want to',
};

// ============================================================
// EXPORTS
// ============================================================

/**
 * Try to match the full (normalized) input against intent patterns.
 * Returns { text, label } or null if no match.
 */
export function matchIntent(normalizedInput) {
  const lower = normalizedInput.toLowerCase().trim();

  // Exact match
  if (INTENT_PATTERNS[lower]) {
    return { text: INTENT_PATTERNS[lower], label: 'exact_match', confidence: 1.0 };
  }

  // Strip LEADING vocative (bro kidhar hai → kidhar hai)
  const vocativePrefix = lower.match(/^(bro|bhai|yaar|boss|dude|re)\s+/i);
  if (vocativePrefix) {
    const withoutVoc = lower.slice(vocativePrefix[0].length).trim();
    const vocWord = vocativePrefix[1].toLowerCase();
    const vocLabel = vocWord === 'yaar' ? 'Dude' : vocWord === 're' ? '' : 'Bro';

    // Try exact match on the remainder
    if (INTENT_PATTERNS[withoutVoc]) {
      let base = INTENT_PATTERNS[withoutVoc];
      if (vocLabel) base = vocLabel + ', ' + base.charAt(0).toLowerCase() + base.slice(1);
      return { text: base, label: 'exact_match', confidence: 0.95 };
    }
    // Try stripping trailing particles from remainder too
    const strippedRem = withoutVoc.replace(/\s+(hai|na)$/i, '').trim();
    if (strippedRem !== withoutVoc && INTENT_PATTERNS[strippedRem]) {
      let base = INTENT_PATTERNS[strippedRem];
      if (vocLabel) base = vocLabel + ', ' + base.charAt(0).toLowerCase() + base.slice(1);
      return { text: base, label: 'exact_match', confidence: 0.90 };
    }
  }

  // Try without trailing particles (hai, na, bro, yaar, bhai)
  const stripped = lower.replace(/\s+(hai|na|bro|yaar|bhai|re)$/i, '').trim();
  if (stripped !== lower && INTENT_PATTERNS[stripped]) {
    const suffix = lower.slice(stripped.length).trim();
    let base = INTENT_PATTERNS[stripped];
    if (['bro', 'yaar', 'bhai', 're'].includes(suffix)) {
      const vocative = suffix === 'yaar' ? 'Dude' : suffix === 're' ? '' : 'Bro';
      if (vocative) base = vocative + ', ' + base.charAt(0).toLowerCase() + base.slice(1);
    }
    return { text: base, label: 'exact_match', confidence: 0.95 };
  }

  // Partial intent: check if input starts/ends with any pattern
  const sortedPatterns = Object.entries(INTENT_PATTERNS)
    .sort((a, b) => b[0].length - a[0].length);
  for (const [pattern, meaning] of sortedPatterns) {
    if (lower.startsWith(pattern + ' ') || lower.endsWith(' ' + pattern)) {
      const remainder = lower.startsWith(pattern + ' ')
        ? lower.slice(pattern.length).trim()
        : lower.slice(0, lower.length - pattern.length).trim();
      // If remainder is a vocative, attach it
      if (['bro', 'bhai', 'yaar', 'dude', 'boss'].includes(remainder.toLowerCase())) {
        const voc = remainder === 'yaar' ? 'Dude' : 'Bro';
        const text = voc + ', ' + meaning.charAt(0).toLowerCase() + meaning.slice(1);
        return { text, label: 'exact_match', confidence: 0.90 };
      }
      return { text: meaning, remainder, label: 'smart_guess', confidence: 0.85 };
    }
  }

  return null;
}

/**
 * Try to match compound verbs in a token sequence.
 * Returns the sorted entries (longest first) for greedy matching.
 */
export function getCompoundVerbs() {
  return Object.entries(COMPOUND_VERBS)
    .sort((a, b) => b[0].split(' ').length - a[0].split(' ').length);
}

/**
 * Get tense verb translation for a single word.
 */
export function getTenseVerb(word) {
  return TENSE_VERBS[word.toLowerCase()] || null;
}

export { INTENT_PATTERNS, COMPOUND_VERBS, TENSE_VERBS };
