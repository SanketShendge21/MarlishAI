/**
 * =====================================================
 * Marlish.AI — DICTIONARY TRANSLATION ENGINE v6.0
 * 
 * Context-Aware 7-Layer Translation Pipeline:
 * 
 *   L1: Input normalization (typo-map.js)
 *       → kr→kar, rha→raha, collapse repeated chars
 * 
 *   L2: Full sentence intent match (phrase-intent-rules.js)
 *       → "kya kar raha hai" → "What are you doing?"
 * 
 *   L3: Compound verb assembly (phrase-intent-rules.js)
 *       → "ja raha hu" matched as unit → "am going"
 *       → "ho gaya" → "it's done"
 * 
 *   L4: Context-aware word translation
 *       → Disambiguates: kal→tomorrow vs yesterday
 *       → Resolves slash meanings: "brother/bro" → "bro"
 *       → Entity preservation: names, numbers kept as-is
 *       → Fuzzy match for typos (Levenshtein ≤1)
 * 
 *   L5: Grammar reordering (grammar-rules.js)
 *       → SOV→SVO, auxiliary insertion, question formation
 * 
 *   L6: Vocative + Punctuation
 *       → "bro where are you" → "Bro, where are you?"
 *       → Auto question marks, periods
 * 
 *   L7: Beautification + Confidence scoring
 *       → Capitalize, fix spacing, score output
 * 
 * Data: public/dictionary.json (words + phrases + reverse)
 * =====================================================
 */

import { normalizeInput } from './typo-map';
import { applyGrammarRules } from './grammar-rules';
import { matchIntent, getCompoundVerbs, getTenseVerb } from './phrase-intent-rules';
import { disambiguate, resolveSlash, isVocative } from './contextual-disambiguation';
import { calculateScore } from './scoring-engine';

let store = null;
let isLoaded = false;
let isLoading = false;
let loadPromise = null;

/* =====================================================
   LOAD DICTIONARY (JSON)
===================================================== */
export async function loadDictionary(path = "/dictionary.json") {
  if (isLoaded) return store;
  if (isLoading) return loadPromise;

  isLoading = true;
  loadPromise = (async () => {
    try {
      const t0 = performance.now();
      const res = await fetch(path);
      if (!res.ok) throw new Error(`Failed to fetch dictionary: ${res.status}`);
      store = await res.json();
      isLoaded = true;
      isLoading = false;
      const t1 = performance.now();

      const stats = Object.entries(store).map(([k, v]) => `${k}:${Object.keys(v).length}`).join(", ");
      console.log(`[Dict] Loaded in ${(t1 - t0).toFixed(0)}ms — ${stats}`);
      return store;
    } catch (err) {
      console.error("[Dict] Load failed:", err);
      isLoading = false;
      throw err;
    }
  })();

  return loadPromise;
}

export function isDictLoaded() {
  return isLoaded;
}

/* =====================================================
   ROUTE: Pick the right dictionaries for a lang pair
===================================================== */
function getRoute(source, target) {
  const s = source.toLowerCase();
  const t = target.toLowerCase();

  if (s === "hinglish" && t === "english")
    return { phraseDict: "hinglish_phrases", wordDict: "hinglish_words", mode: "forward" };
  if (s === "marlish" && t === "english")
    return { phraseDict: "marlish_phrases", wordDict: "marlish_words", mode: "forward" };
  if (s === "english" && t === "hinglish")
    return { phraseDict: "english_to_hinglish_phrases", wordDict: "english_to_hinglish_words", mode: "forward" };
  if (s === "english" && t === "marlish")
    return { phraseDict: "english_to_marlish_phrases", wordDict: "english_to_marlish_words", mode: "forward" };
  if (s === "hinglish" && (t === "marathi" || t === "marlish"))
    return { pivot: "english", first: getRoute("hinglish", "english"), second: getRoute("english", "marlish") };
  if (s === "marlish" && (t === "hindi" || t === "hinglish"))
    return { pivot: "english", first: getRoute("marlish", "english"), second: getRoute("english", "hinglish") };
  if (s === "marathi" && t === "english")
    return { phraseDict: "marlish_phrases", wordDict: "marlish_words", mode: "forward" };
  if (s === "hindi" && t === "english")
    return { phraseDict: "hinglish_phrases", wordDict: "hinglish_words", mode: "forward" };

  return { phraseDict: "hinglish_phrases", wordDict: "hinglish_words", mode: "forward" };
}

/* =====================================================
   ENTITY DETECTION
===================================================== */
const NUMBER_PATTERN = /^\d+$/;
const COMMON_NAMES = new Set([
  'rahul', 'priya', 'amit', 'neha', 'arjun', 'ananya', 'rohan', 'sneha',
  'vivek', 'pooja', 'raj', 'simran', 'vikram', 'kajal', 'deepak', 'riya',
  'suresh', 'sanjay', 'nisha', 'ankita', 'kiran', 'mohit', 'swati', 'ajay',
  'sachin', 'virat', 'dhoni', 'rohit', 'hardik', 'aarav', 'aditya', 'harsh',
]);

function isEntity(word) {
  if (NUMBER_PATTERN.test(word)) return true;
  if (/^[A-Z][a-z]{2,}$/.test(word)) return true;
  if (COMMON_NAMES.has(word.toLowerCase())) return true;
  return false;
}

/* =====================================================
   MAIN TRANSLATE FUNCTION
===================================================== */
export function translate(text, source, target) {
  if (!text || !source || !target || !isLoaded || !store) return null;
  if (source === target) return { text, label: 'same', confidence: 1.0 };

  const input = text.trim();
  if (input.length < 1) return null;

  const route = getRoute(source, target);

  // Handle pivot translations (e.g. Hinglish → Marlish via English)
  if (route.pivot) {
    const intermediate = translateDirect(input, route.first);
    if (intermediate) {
      const final = translateDirect(intermediate.text, route.second);
      return final || intermediate;
    }
    return null;
  }

  return translateDirect(input, route);
}

/* =====================================================
   DIRECT TRANSLATION (all 7 layers)
===================================================== */
function translateDirect(text, route) {
  const phrases = store[route.phraseDict] || {};
  const words = store[route.wordDict] || {};

  // =========================================
  // L1: NORMALIZE INPUT
  // =========================================
  const normalized = normalizeInput(text);
  const lower = normalized.toLowerCase().trim();

  // =========================================
  // L2: FULL SENTENCE INTENT MATCH
  // =========================================

  // First try exact phrase dictionary match
  if (phrases[lower]) {
    return { text: beautify(phrases[lower]), label: 'exact_match', confidence: 1.0 };
  }

  // Then try curated intent patterns
  const intentResult = matchIntent(lower);
  if (intentResult) {
    if (!intentResult.remainder) {
      return { text: intentResult.text, label: intentResult.label, confidence: intentResult.confidence };
    }
    // Partial intent match: translate the remainder
    const remainderResult = translateTokens(intentResult.remainder, phrases, words);
    const combined = intentResult.text.replace(/[.?!]$/, '') + ' ' + remainderResult.text;
    return { text: beautify(combined), label: 'smart_guess', confidence: 0.85 };
  }

  // =========================================
  // L3 + L4: COMPOUND VERB + WORD TRANSLATION
  // =========================================
  return translateTokens(lower, phrases, words);
}

/* =====================================================
   TOKEN-LEVEL TRANSLATION (L3 + L4 + L5 + L6 + L7)
   
   Handles compound verbs, contextual disambiguation,
   slash resolution, entity preservation, fuzzy matching,
   then grammar reordering and beautification.
===================================================== */
function translateTokens(text, phrases, words) {
  const rawWords = text.split(/\s+/).filter(Boolean);
  if (rawWords.length === 0) return { text: '', label: 'empty', confidence: 0 };

  // ---- L3: COMPOUND VERB MATCHING ----
  // Try to match multi-word verb forms first (longest first)
  const compoundVerbs = getCompoundVerbs();
  const translated = [];
  const matchTypes = [];
  let i = 0;

  while (i < rawWords.length) {
    let compoundMatched = false;

    // Try compound verbs (up to 4 words)
    for (const [pattern, meaning] of compoundVerbs) {
      const patternWords = pattern.split(' ');
      if (i + patternWords.length > rawWords.length) continue;

      const slice = rawWords.slice(i, i + patternWords.length);
      if (slice.join(' ') === pattern) {
        translated.push(meaning);
        matchTypes.push('compound_verb');
        i += patternWords.length;
        compoundMatched = true;
        break;
      }
    }

    if (compoundMatched) continue;

    // Try phrase dict (up to 6 words)
    let phraseMatched = false;
    for (let len = Math.min(6, rawWords.length - i); len >= 2; len--) {
      const phrase = rawWords.slice(i, i + len).join(' ');
      if (phrases[phrase]) {
        translated.push(phrases[phrase]);
        matchTypes.push('phrase');
        i += len;
        phraseMatched = true;
        break;
      }
    }

    if (phraseMatched) continue;

    // ---- L4: SINGLE WORD TRANSLATION ----
    const word = rawWords[i];

    // Entity preservation
    if (isEntity(word)) {
      translated.push(word);
      matchTypes.push('entity');
      i++;
      continue;
    }

    // Contextual disambiguation (kal, bro, bhai, scene, etc.)
    const disamb = disambiguate(word, rawWords, i);
    if (disamb) {
      translated.push(disamb.value);
      matchTypes.push(disamb.tag === 'vocative' ? 'vocative' : 'disambiguated');
      i++;
      continue;
    }

    // Tense verb lookup (gaya→went, aaya→came, etc.)
    const tenseVerb = getTenseVerb(word);
    if (tenseVerb) {
      translated.push(tenseVerb);
      matchTypes.push('tense_verb');
      i++;
      continue;
    }

    // Dictionary word lookup
    if (words[word]) {
      let meaning = words[word];
      // Resolve slash meanings using context
      meaning = resolveSlash(meaning, word, rawWords, i);
      translated.push(meaning);
      matchTypes.push('word');
      i++;
      continue;
    }

    // Fuzzy match (Levenshtein ≤1)
    const fuzzy = fuzzyMatch(word, words);
    if (fuzzy) {
      let meaning = fuzzy;
      meaning = resolveSlash(meaning, word, rawWords, i);
      translated.push(meaning);
      matchTypes.push('typo_fixed');
      i++;
      continue;
    }

    // Passthrough (unknown word kept as-is)
    translated.push(word);
    matchTypes.push('passthrough');
    i++;
  }

  // Count matches
  const totalTokens = rawWords.length;
  const matched = matchTypes.filter(t => t !== 'passthrough').length;
  if (matched === 0) return { text: text, label: 'passthrough', confidence: 0 };

  // ---- L5: GRAMMAR REORDERING ----
  let output = translated.join(' ');
  output = applyGrammarRules(output);

  // ---- L7: CONFIDENCE + LABEL ----
  const { confidence, label } = calculateScore(matchTypes, totalTokens);

  return { text: beautify(output), label, confidence };
}

/* =====================================================
   FUZZY MATCH (Levenshtein distance ≤ 1)
===================================================== */
function fuzzyMatch(word, dict) {
  if (word.length < 3) return null;
  const keys = Object.keys(dict);
  for (const key of keys) {
    if (Math.abs(key.length - word.length) > 1) continue;
    if (levenshtein(word, key) <= 1 && dict[key]) {
      return dict[key];
    }
  }
  return null;
}

function levenshtein(a, b) {
  if (a === b) return 0;
  const m = [];
  for (let i = 0; i <= b.length; i++) m[i] = [i];
  for (let j = 0; j <= a.length; j++) m[0][j] = j;
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      m[i][j] = b[i - 1] === a[j - 1]
        ? m[i - 1][j - 1]
        : Math.min(m[i - 1][j - 1] + 1, m[i][j - 1] + 1, m[i - 1][j] + 1);
    }
  }
  return m[b.length][a.length];
}

/* =====================================================
   BEAUTIFY (L7)
===================================================== */
function beautify(text) {
  let t = text.replace(/\s+/g, ' ').trim();
  if (!t) return '';
  // Capitalize first letter
  t = t.charAt(0).toUpperCase() + t.slice(1);
  // Fix standalone "i" → "I"
  t = t.replace(/\bi\b/g, 'I');
  // Fix "i'm" → "I'm"
  t = t.replace(/\bi'm\b/gi, "I'm");
  t = t.replace(/\bi've\b/gi, "I've");
  t = t.replace(/\bi'll\b/gi, "I'll");
  // Clean double spaces around punctuation
  t = t.replace(/\s+([.,!?;:])/g, '$1');
  t = t.replace(/([.,!?;:])\s*([A-Z])/g, '$1 $2');
  // Remove duplicate punctuation
  t = t.replace(/([.!?])\1+/g, '$1');
  // Ensure single sentence-ending punctuation
  t = t.replace(/\.\?/g, '?');
  t = t.replace(/\?\.$/g, '?');
  return t;
}