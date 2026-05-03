/**
 * Full integration test for the 7-layer engine.
 * Simulates the complete pipeline in CommonJS.
 */
const fs = require('fs');
const store = JSON.parse(fs.readFileSync('public/dictionary.json', 'utf8'));

// ============================================================
// INLINE MODULES (since we can't import ESM in Node test)
// ============================================================

// --- TYPO MAP ---
const TYPO_MAP = {
  'kr': 'kar', 'krr': 'kar', 'kro': 'karo', 'rha': 'raha', 'rhi': 'rahi',
  'h': 'hai', 'hu': 'hoon', 'nhi': 'nahi', 'nai': 'nahi', 'mt': 'mat',
  'bht': 'bahut', 'ky': 'kya', 'kyu': 'kyun', 'yr': 'yaar', 'ghr': 'ghar',
  'ghri': 'ghari', 'ahs': 'ahes', 'kth': 'kuthe', 'kt': 'kuthe',
  'plz': 'please', 'pls': 'please',
};

function normalizeInput(text) {
  let cleaned = text.replace(/(.)\1{2,}/g, '$1$1');
  return cleaned.split(/(\s+)/).map(s => /^\s+$/.test(s) ? s : (TYPO_MAP[s.toLowerCase()] || s.toLowerCase())).join('');
}

// --- CONTEXTUAL DISAMBIGUATION ---
const AMBIGUOUS = {
  kal: [
    { value: 'tomorrow', score: 0.55, boost: ['milte','milenge','plan','scene','hoga','meeting','chalega','aana'],
      inhibit: ['gaya','gayi','tha','thi','aaya','kiya','bola','mila','dekha'] },
    { value: 'yesterday', score: 0.45, boost: ['gaya','gayi','tha','thi','aaya','kiya','bola','mila','dekha','raha'],
      inhibit: ['milte','milenge','plan','scene','hoga'] },
  ],
  bro: [
    { value: 'Bro', score: 0.9, boost: ['kidhar','kya','scene','milte','kaise','tu'], inhibit: ['mera','uska','ka'] },
    { value: 'brother', score: 0.1, boost: ['mera','uska','bada','ka','naam'], inhibit: ['kidhar','kya','scene'] },
  ],
  bhai: [
    { value: 'Bro', score: 0.7, boost: ['kidhar','kya','scene','milte','kaise','tu'], inhibit: ['mera','uska','ka','naam'] },
    { value: 'brother', score: 0.3, boost: ['mera','uska','bada','ka','naam'], inhibit: ['kidhar','kya','scene'] },
  ],
  scene: [
    { value: 'plan', score: 0.6, boost: ['kya','hai','kal','aaj'], inhibit: ['movie','film'] },
    { value: 'situation', score: 0.3, boost: ['yeh','woh','kaisa'], inhibit: ['kya','hai'] },
  ],
};

function disambiguate(word, tokens, idx) {
  const entry = AMBIGUOUS[word.toLowerCase()];
  if (!entry) return null;
  const ctx = [];
  for (let i = Math.max(0, idx - 3); i < Math.min(tokens.length, idx + 4); i++) {
    if (i !== idx) ctx.push(tokens[i].toLowerCase());
  }
  let best = entry[0], bestScore = -Infinity;
  for (const m of entry) {
    let s = m.score;
    for (const c of ctx) { if (m.boost.includes(c)) s += 0.25; if (m.inhibit.includes(c)) s -= 0.3; }
    if (s > bestScore) { bestScore = s; best = m; }
  }
  return best.value;
}

function resolveSlash(meaning, word, tokens, idx) {
  if (!meaning || !meaning.includes('/')) return meaning;
  const opts = meaning.split('/').map(s => s.trim());
  if (opts.includes('tomorrow') && opts.includes('yesterday')) {
    let past = 0, future = 0;
    const PAST = new Set(['gaya','gayi','tha','thi','aaya','kiya','bola','mila','dekha']);
    const FUTURE = new Set(['milte','milenge','plan','scene','hoga','meeting']);
    for (let i = Math.max(0, idx - 3); i < Math.min(tokens.length, idx + 4); i++) {
      if (PAST.has(tokens[i])) past++;
      if (FUTURE.has(tokens[i])) future++;
    }
    return future >= past ? 'tomorrow' : 'yesterday';
  }
  if (opts.includes('bro') && opts.includes('brother')) return 'bro';
  return opts[0];
}

// --- COMPOUND VERBS ---
const COMPOUNDS = {
  'kar raha hai': 'is doing', 'kar raha hu': 'am doing', 'kar rahi hai': 'is doing',
  'kar rahe hai': 'are doing', 'kar raha tha': 'was doing', 'kar raha': 'doing',
  'ja raha hai': 'is going', 'ja raha hu': 'am going', 'ja rahi hai': 'is going',
  'jata hai': 'goes', 'jata hu': 'go', 'jana hai': 'have to go',
  'aa raha hai': 'is coming', 'aa raha hu': 'am coming', 'aa rahi hai': 'is coming',
  'aata hai': 'comes', 'aana hai': 'have to come',
  'ho gaya': "it's done", 'ho jayega': 'it will happen', 'ho raha hai': 'is happening',
  'mil gaya': 'found it', 'milte hai': "let's meet", 'milna hai': 'need to meet',
  'pata hai': 'I know', 'pata nahi': "don't know",
  'chal raha hai': 'is going on', 'chalte hai': "let's go",
  'so gaya': 'fell asleep', 'so ja': 'go to sleep',
  'dekh lo': 'see for yourself', 'dekhte hai': "let's see",
  'bol raha hai': 'is saying', 'bola tha': 'had said',
  'kha raha hai': 'is eating', 'kha liya': 'finished eating',
};

// --- INTENT PATTERNS ---
const INTENTS = {
  'kya kar raha hai': 'What are you doing?',
  'kya kar raha': 'What are you doing?',
  'kya chal raha hai': "What's going on?",
  'kya chal raha': "What's going on?",
  'kya ho raha hai': "What's happening?",
  'scene kya hai': "What's the plan?",
  'kya scene hai': "What's the plan?",
  'kaise ho': 'How are you?',
  'kidhar hai': 'Where are you?',
  'tu kidhar hai': 'Where are you?',
  'kahan hai': 'Where is it?',
  'milte hai': "Let's meet.",
  'kal milte hai': "Let's meet tomorrow.",
  'ho gaya': "It's done.",
  'ho jayega': 'It will be done.',
  'mat kar': "Don't do it.",
  'rehne de': 'Leave it.',
  'tension mat le': "Don't worry.",
  'pata nahi': "I don't know.",
  'theek hai': "It's okay.",
  'main aa raha hu': "I'm coming.",
  'main aa raha hoon': "I'm coming.",
  'main aa raha': "I'm coming.",
  'main ja raha hu': "I'm leaving.",
  'main ja raha hoon': "I'm leaving.",
  'ghar ja raha hu': "I'm going home.",
  'ghar ja raha hoon': "I'm going home.",
  'tu kuthe ahes': 'Where are you?',
  'kuthe ahes': 'Where are you?',
  'mi ghari jato': "I'm going home.",
  'kasa ahes': 'How are you?',
  'kaay challay': "What's going on?",
  'majha nav': 'My name is',
};

// --- TENSE VERBS ---
const TENSE_VERBS = {
  'gaya': 'went', 'gayi': 'went', 'gaye': 'went',
  'aaya': 'came', 'aayi': 'came', 'kiya': 'did',
  'bola': 'said', 'mila': 'met', 'dekha': 'saw',
  'suna': 'heard', 'khaya': 'ate', 'liya': 'took',
  'diya': 'gave', 'hua': 'happened',
  'aayega': 'will come', 'aaoge': 'will come'
};

// --- GRAMMAR REORDER ---
function applyGrammar(text) {
  let r = text;
  // Question patterns
  r = r.replace(/^what\s+(you|he|she|they|we|I|it|this|that)\s+(will|can|could|should|would|do|does|did|are|is|am|was|were)\b/gi,
    (_, subj, aux) => `${aux.charAt(0).toUpperCase() + aux.slice(1)} ${subj}`);

  r = r.replace(/^(.+?)\s+(where|what|how|when|why|who|which)\s+(are|is|am|was|were|will|can|could|should|would|have|has|had)\s*([.?!]*)$/gi,
    (_, subj, qw, aux, punct) => {
      const isPronoun = /^(you|he|she|they|we|i|it|this|that|these|those|everyone|someone|nobody|everything)$/i.test(subj.trim());
      const article = isPronoun ? '' : 'the ';
      return `${qw.charAt(0).toUpperCase() + qw.slice(1)} ${aux} ${article}${subj}${punct}`;
    });

  r = r.replace(/^(.+?)\s+(where|what|how|when|why|who|which)\s+(will|can|could|should|would|do|does|did|is|are|am|was|were)\s+(\w+(?:ing|ed|s)?)\s*([.?!]*)$/gi,
    (_, subj, qw, aux, verb, punct) => {
      const isPronoun = /^(you|he|she|they|we|i|it|this|that|these|those|everyone|someone|nobody|everything)$/i.test(subj.trim());
      const article = isPronoun ? '' : 'the ';
      return `${qw.charAt(0).toUpperCase() + qw.slice(1)} ${aux} ${article}${subj} ${verb}${punct}`;
    });

  r = r.replace(/^(.+?)\s+(where|what|how|when|why|who|which)\s+(\w+)\s*([.?!]*)$/gi,
    (_, subj, qw, verb, punct) => `${qw.charAt(0).toUpperCase() + qw.slice(1)} ${subj} ${verb}${punct}`);
  // SOV → SVO for -ing verbs
  r = r.replace(/\b(I|you|he|she|we|they|it)\s+(.+?)\s+(am|is|are|was|were|will|can|could|should|would)\s+(\w+(?:ing|ed|s)?)\s*([.?!]*)$/gi,
    (_, s, o, aux, v, p) => `${s} ${aux} ${v} ${o}${p}`);
    
  r = r.replace(/\b(I|you|he|she|we|they|it)\s+(.+?)\s+(\w+(?:ing|ed|s)?)\s+(am|is|are|was|were|will|can|could|should|would)\s*([.?!]*)$/gi,
    (_, s, o, v, aux, p) => `${s} ${aux} ${v} ${o}${p}`);

  r = r.replace(/\b(I|you|he|she|we|they)\s+(.+?)\s+(going|coming|leaving|eating|doing|working|sleeping)\s*([.?!]*)$/gi,
    (_, s, o, v, p) => {
      const aux = s.toLowerCase() === 'i' ? 'am' : ['he','she','it'].includes(s.toLowerCase()) ? 'is' : 'are';
      return `${s} ${aux} ${v} ${o}${p}`;
    });
    
  // Generic verb
  r = r.replace(/\b(I|you|he|she|we|they|it)\s+(.+?)\s+(go|went|come|came|eat|ate|do|did|say|said|tell|told|see|saw|look|looked|take|took|give|gave)\s*([.?!]*)$/gi,
    (_, s, o, v, p) => `${s} ${v} ${o}${p}`);

  // "I going" → "I am going"
  // "tomorrow meet" → "Meet tomorrow"
  r = r.replace(/\b(tomorrow|yesterday|today)\s+(meet|go|come|call|talk|eat|sleep)\b/gi,
    (_, t, v) => `${v.charAt(0).toUpperCase() + v.slice(1)} ${t}`);
  // Vocative comma
  r = r.replace(/^(Bro|Dude|Boss)\s+(?!,)/i, (_, v) => `${v}, `);
  r = r.replace(/\s+(bro|dude|boss|yaar)([?.!]?)$/i, (_, v, p) => `, ${v.toLowerCase()}${p}`);
  // Punctuation
  r = r.trim();
  if (/^(where|what|how|when|why|who|which|is|are|do|does|did|will|can)\b/i.test(r) && !/[?!.]$/.test(r)) r += '?';
  else if (!/[.!?]$/.test(r)) r += '.';
  return r;
}

function beautify(t) {
  t = t.replace(/\s+/g, ' ').trim();
  if (!t) return '';
  t = t.charAt(0).toUpperCase() + t.slice(1);
  t = t.replace(/\bi\b/g, 'I');
  t = t.replace(/\s+([.,!?;:])/g, '$1');
  t = t.replace(/([.!?])\1+/g, '$1');
  t = t.replace(/\.\?/g, '?');
  return t;
}

// --- FULL TRANSLATE ---
function translate(text, src) {
  const phrases = src === 'marlish' ? store.marlish_phrases : store.hinglish_phrases;
  const words = src === 'marlish' ? store.marlish_words : store.hinglish_words;
  const normalized = normalizeInput(text);
  const lower = normalized.toLowerCase().trim();

  // L2: Exact phrase
  if (phrases[lower]) return { out: beautify(phrases[lower]), layer: 'PHRASE' };

  // L2: Intent match
  if (INTENTS[lower]) return { out: INTENTS[lower], layer: 'INTENT' };

  // Strip LEADING vocative and re-check intents
  const vocPfx = lower.match(/^(bro|bhai|yaar|boss|dude)\s+/i);
  if (vocPfx) {
    const rest = lower.slice(vocPfx[0].length).trim();
    const vocLabel = vocPfx[1] === 'yaar' ? 'Dude' : 'Bro';
    if (INTENTS[rest]) {
      return { out: vocLabel + ', ' + INTENTS[rest].charAt(0).toLowerCase() + INTENTS[rest].slice(1), layer: 'INTENT+VOC' };
    }
    // Also strip trailing particles from rest
    const restStripped = rest.replace(/\s+(hai|na)$/i, '').trim();
    if (restStripped !== rest && INTENTS[restStripped]) {
      return { out: vocLabel + ', ' + INTENTS[restStripped].charAt(0).toLowerCase() + INTENTS[restStripped].slice(1), layer: 'INTENT+VOC' };
    }
  }

  // Try with trailing particles stripped
  const stripped = lower.replace(/\s+(hai|na|bro|yaar|bhai|re)$/i, '').trim();
  if (stripped !== lower && INTENTS[stripped]) {
    const suffix = lower.slice(stripped.length).trim();
    let base = INTENTS[stripped];
    if (['bro', 'yaar', 'bhai'].includes(suffix)) {
      const voc = suffix === 'yaar' ? 'Dude' : 'Bro';
      base = voc + ', ' + base.charAt(0).toLowerCase() + base.slice(1);
    }
    return { out: base, layer: 'INTENT+VOC' };
  }

  // Partial intent: check start/end
  const sortedIntents = Object.entries(INTENTS).sort((a, b) => b[0].length - a[0].length);
  for (const [pat, meaning] of sortedIntents) {
    if (lower.endsWith(' ' + pat)) {
      const rem = lower.slice(0, lower.length - pat.length - 1).trim();
      if (['bro','bhai','yaar'].includes(rem)) {
        const voc = rem === 'yaar' ? 'Dude' : 'Bro';
        return { out: voc + ', ' + meaning.charAt(0).toLowerCase() + meaning.slice(1), layer: 'INTENT+VOC' };
      }
    }
  }

  // L3+L4: Compound verbs + word translation
  const rawWords = lower.split(/\s+/);
  const translated = [];
  let i = 0;

  while (i < rawWords.length) {
    let matched = false;

    // Compound verbs (up to 4 words)
    const sortedCompounds = Object.entries(COMPOUNDS).sort((a, b) => b[0].split(' ').length - a[0].split(' ').length);
    for (const [pat, meaning] of sortedCompounds) {
      const pw = pat.split(' ');
      if (i + pw.length > rawWords.length) continue;
      if (rawWords.slice(i, i + pw.length).join(' ') === pat) {
        translated.push(meaning);
        i += pw.length;
        matched = true;
        break;
      }
    }
    if (matched) continue;

    // Phrase dict (up to 4 words)
    for (let len = Math.min(4, rawWords.length - i); len >= 2; len--) {
      const p = rawWords.slice(i, i + len).join(' ');
      if (phrases[p]) { translated.push(phrases[p]); i += len; matched = true; break; }
    }
    if (matched) continue;

    const w = rawWords[i];

    // Disambiguation
    const d = disambiguate(w, rawWords, i);
    if (d) { translated.push(d); i++; continue; }

    // Tense verbs
    if (TENSE_VERBS[w]) { translated.push(TENSE_VERBS[w]); i++; continue; }

    // Word dict
    if (words[w]) {
      translated.push(resolveSlash(words[w], w, rawWords, i));
      i++; continue;
    }

    // Passthrough
    translated.push(w);
    i++;
  }

  let output = translated.join(' ');
  output = applyGrammar(output);
  return { out: beautify(output), layer: 'WORDS+GRAMMAR' };
}

// ============================================================
// TEST CASES
// ============================================================
const tests = [
  // Your exact examples from the request
  { input: 'kal milte hai', src: 'hinglish', expect: "Let's meet tomorrow" },
  { input: 'kal gaya tha', src: 'hinglish', expect: 'yesterday' },
  { input: 'bro kidhar hai', src: 'hinglish', expect: 'Bro, where are you' },
  { input: 'bro kal milte hai', src: 'hinglish', expect: "Bro, let's meet tomorrow" },
  { input: 'kya kar raha hai', src: 'hinglish', expect: 'What are you doing' },
  { input: 'scene kya hai', src: 'hinglish', expect: "What's the plan" },
  // Additional
  { input: 'tu kuthe ahes', src: 'marlish', expect: 'Where are you' },
  { input: 'mi ghari jato', src: 'marlish', expect: "going home" },
  { input: 'kaise ho bro', src: 'hinglish', expect: 'Bro, how are you' },
  { input: 'main aa raha hu', src: 'hinglish', expect: "I'm coming" },
  { input: 'ho gaya', src: 'hinglish', expect: "done" },
  { input: 'tension mat le', src: 'hinglish', expect: "worry" },
  { input: 'kal meeting hai bro', src: 'hinglish', expect: 'tomorrow meeting' },
  { input: 'majha nav Rahul aahe', src: 'marlish', expect: 'name' },
  { input: 'pata nahi', src: 'hinglish', expect: "don't know" },
  { input: 'bahut accha hai', src: 'hinglish', expect: 'good' },
  { input: 'meeting kab hai', src: 'hinglish', expect: 'When is the meeting' },
  { input: 'train kab aayega', src: 'hinglish', expect: 'When will the train come' },
  { input: 'kya tum aaoge', src: 'hinglish', expect: 'Will you come' },
];

console.log('╔══════════════════════════════════════════════════════════════════╗');
console.log('║        Marlish.AI — TRANSLATION ENGINE v6.0 TEST              ║');
console.log('╚══════════════════════════════════════════════════════════════════╝\n');

let pass = 0, fail = 0;
for (const t of tests) {
  const { out, layer } = translate(t.input, t.src);
  const ok = out.toLowerCase().includes(t.expect.toLowerCase());
  if (ok) pass++; else fail++;
  const icon = ok ? '✅' : '❌';
  console.log(`  ${icon}  "${t.input}"`);
  console.log(`      → [${layer}] "${out}"`);
  if (!ok) console.log(`      ⚠  Expected to contain: "${t.expect}"`);
  console.log('');
}

console.log('─'.repeat(68));
console.log(`  Result: ${pass} passed, ${fail} failed out of ${tests.length}`);
console.log('─'.repeat(68));
