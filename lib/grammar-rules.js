/**
 * GRAMMAR REORDER ENGINE v2
 * 
 * Converts literal word-by-word translated output from
 * SOV (Hindi/Marathi) order to natural SVO (English) order.
 * 
 * Also inserts missing auxiliaries and handles:
 *   - Question formation
 *   - Sentence-ending punctuation
 *   - Vocative comma placement (Bro, ...)
 *   - Continuous tense assembly (am/is/are + verb-ing)
 */

// ============================================================
// REORDERING RULES (applied sequentially)
// ============================================================
const REORDER_RULES = [
  // ---- QUESTION REORDERING ----

  // "what you will come" → "Will you come" (Hindi 'kya' used as yes/no marker)
  {
    pattern: /^what\s+(you|he|she|they|we|I|it|this|that)\s+(will|can|could|should|would|do|does|did|are|is|am|was|were)\b/gi,
    replace: (_, subj, aux) => `${cap(aux)} ${subj}`
  },

  // "meeting when is" → "When is the meeting"
  // "you where are" → "Where are you"
  {
    pattern: /^(.+?)\s+(where|what|how|when|why|who|which)\s+(are|is|am|was|were|will|can|could|should|would|have|has|had)\s*([.?!]*)$/gi,
    replace: (_, subj, qw, aux, punct) => {
      const isPronoun = /^(you|he|she|they|we|i|it|this|that|these|those|everyone|someone|nobody|everything)$/i.test(subj.trim());
      const article = isPronoun ? '' : 'the ';
      return `${cap(qw)} ${aux} ${article}${subj}${punct}`;
    }
  },

  // "train when will come" → "When will the train come"
  {
    pattern: /^(.+?)\s+(where|what|how|when|why|who|which)\s+(will|can|could|should|would|do|does|did|is|are|am|was|were)\s+(\w+(?:ing|ed|s)?)\s*([.?!]*)$/gi,
    replace: (_, subj, qw, aux, verb, punct) => {
      const isPronoun = /^(you|he|she|they|we|i|it|this|that|these|those|everyone|someone|nobody|everything)$/i.test(subj.trim());
      const article = isPronoun ? '' : 'the ';
      return `${cap(qw)} ${aux} ${article}${subj} ${verb}${punct}`;
    }
  },

  // "you there why went" → "Why you there went" (SOV will later fix to "Why you went there")
  {
    pattern: /^(.+?)\s+(where|what|how|when|why|who|which)\s+(\w+)\s*([.?!]*)$/gi,
    replace: (_, subj, qw, verb, punct) => {
      return `${cap(qw)} ${subj} ${verb}${punct}`;
    }
  },

  // ---- SOV → SVO (Subject + Object + Verb → Subject + Verb + Object) ----

  // "I my home am going." → "I am going my home."
  {
    pattern: /\b(I|you|he|she|we|they|it)\s+(.+?)\s+(am|is|are|was|were|will|can|could|should|would)\s+(\w+(?:ing|ed|s)?)\s*([.?!]*)$/gi,
    replace: (_, subj, obj, aux, verb, punct) => `${subj} ${aux} ${verb} ${obj}${punct}`
  },
  
  // "I my home going am." → "I am going my home."
  {
    pattern: /\b(I|you|he|she|we|they|it)\s+(.+?)\s+(\w+(?:ing|ed|s)?)\s+(am|is|are|was|were|will|can|could|should|would)\s*([.?!]*)$/gi,
    replace: (_, subj, obj, verb, aux, punct) => `${subj} ${aux} ${verb} ${obj}${punct}`
  },

  // "I my home going." → "I am going my home." (missing aux)
  {
    pattern: /\b(I|you|he|she|we|they)\s+(.+?)\s+(going|coming|leaving|running|walking|sitting|eating|doing|making|watching|reading|writing|playing|working|studying|sleeping|driving|cooking|cleaning|taking|giving|buying|selling|waiting|looking|reaching|thinking|trying)\s*([.?!]*)$/gi,
    replace: (_, subj, obj, verb, punct) => `${subj} ${getAux(subj)} ${verb} ${obj}${punct}`
  },

  // "I office in am." → "I am in the office."
  {
    pattern: /\b(I|you|he|she|we|they|it)\s+(.+?)\s+(in|at|on|from|to|near|inside|outside|behind|above|below)\s+(am|is|are|was|were)\s*([.?!]*)$/gi,
    replace: (_, subj, place, prep, aux, punct) => `${subj} ${aux} ${prep} the ${place}${punct}`
  },

  // Generic Subject + Object + Verb (Past/Present Tense) -> Subject + Verb + Object
  {
    pattern: /\b(I|you|he|she|we|they|it)\s+(.+?)\s+(go|went|come|came|eat|ate|do|did|say|said|tell|told|see|saw|look|looked|take|took|give|gave|want|wanted|like|liked|need|needed|know|knew|meet|met|make|made|find|found|think|thought|bring|brought)\s*([.?!]*)$/gi,
    replace: (_, subj, obj, verb, punct) => `${subj} ${verb} ${obj}${punct}`
  },

  // "home go" → "Go home" (imperative)
  {
    pattern: /^(?!.*\b(I|you|he|she|they|we|it|where|what|how|when|why|who|which|is|are|am|was|were|will|can|could|should|would|did|does|do)\b)(.+?)\s+(go|come|eat|sleep|sit|stand|run|walk|drive|stop|wait|leave|stay)\s*([.?!]*)$/i,
    replace: (_, obj, verb, punct) => `${cap(verb)} ${obj}${punct}`
  },

  // ---- TIME-VERB FLIP ----
  // "tomorrow meet" → "Meet tomorrow"
  {
    pattern: /\b(tomorrow|yesterday|today|later|now|soon)\s+(meet|go|come|call|talk|eat|sleep|leave|start|stop|play|work|study|drive|walk|run)\b/gi,
    replace: (_, time, verb) => `${cap(verb)} ${time}`
  },

  // ---- AUXILIARY INSERTION for -ing verbs ----
  // "I going" → "I am going"
  {
    pattern: /\b(I)\s+(going|coming|eating|sleeping|working|studying|playing|running|sitting|standing|talking|doing|making|looking|watching|waiting|thinking|trying|leaving|driving|cooking|cleaning|reading|writing|reaching)\b/gi,
    replace: '$1 am $2'
  },
  {
    pattern: /\b(he|she|it)\s+(going|coming|eating|sleeping|working|studying|playing|running|sitting|standing|talking|doing|making|looking|watching|waiting|thinking|trying|leaving|driving|cooking|cleaning|reading|writing|reaching)\b/gi,
    replace: '$1 is $2'
  },
  {
    pattern: /\b(you|we|they)\s+(going|coming|eating|sleeping|working|studying|playing|running|sitting|standing|talking|doing|making|looking|watching|waiting|thinking|trying|leaving|driving|cooking|cleaning|reading|writing|reaching)\b/gi,
    replace: '$1 are $2'
  },

  // ---- NEGATIVE PATTERNS ----
  // "don't do" is already correct
  // "no go" → "Don't go" (imperative negative)
  {
    pattern: /^(no|not)\s+(go|come|eat|sleep|sit|talk|do|say|run|walk|stop|wait|leave)\b/i,
    replace: (_, _neg, verb) => `Don't ${verb}`
  },
];

// ============================================================
// SENTENCE TEMPLATES — high-priority full-pattern rewrites
// ============================================================
const SENTENCE_TEMPLATES = [
  // "plan/scene what is" → "What's the plan?"
  {
    pattern: /\b(plan|scene|idea|situation|matter|issue|problem)\s+(what|kya)\s+(is|hai)\b/gi,
    output: "What's the $1?"
  },
  // "name my X is" → "My name is X"
  {
    pattern: /\bname\s+my\s+(\w+)\s+is\b/gi,
    output: 'My name is $1.'
  },
  // "my name X is" → "My name is X"
  {
    pattern: /\bmy\s+name\s+(\w+)\s+is\b/gi,
    output: 'My name is $1.'
  },
  // "very good is" → "It's very good"
  {
    pattern: /\b(very|really|so)\s+(good|bad|nice|great|awesome|amazing|beautiful|terrible)\s+(is|are|was|were)\b/gi,
    output: "It's $1 $2."
  },
  // "is done" / "done is" → "It's done."
  {
    pattern: /\b(done)\s+(is|hai)\b/gi,
    output: "It's done."
  },
];

// ============================================================
// VOCATIVE COMMA PLACEMENT
// ============================================================
function handleVocatives(text) {
  // "Bro where are you" → "Bro, where are you"
  // "Dude what's up" → "Dude, what's up"
  let result = text;
  result = result.replace(/^(Bro|Dude|Boss|Yaar|Bhai)\s+(?!,)/i, (_, voc) => `${cap(voc)}, `);
  // Also handle vocative at end: "where are you bro" → "Where are you, bro?"
  result = result.replace(/\s+(bro|dude|boss|yaar|bhai)([?.!]?)$/i, (_, voc, punct) => `, ${voc.toLowerCase()}${punct}`);
  return result;
}

// ============================================================
// QUESTION MARK & PUNCTUATION
// ============================================================
const QUESTION_STARTERS = /^(where|what|how|when|why|who|which|is|are|am|do|does|did|will|can|could|should|would|have|has|had)\b/i;
const QUESTION_ENDERS = /\b(where|what|how|when|why|who|which)\??\s*$/i;

function addPunctuation(text) {
  let t = text.trim();
  // Already has punctuation
  if (/[.!?]$/.test(t)) return t;
  // Question detection
  if (QUESTION_STARTERS.test(t) || QUESTION_ENDERS.test(t)) return t + '?';
  // Imperative detection (starts with verb)
  if (/^(Don't|Go|Come|Eat|Sleep|Sit|Stand|Run|Walk|Stop|Wait|Leave|Meet|Let's|Look|Listen|Give|Take|Tell|Ask|Try|Check|Call|Send)/i.test(t)) {
    return t + '.';
  }
  // Statement
  return t + '.';
}

// ============================================================
// HELPERS
// ============================================================
function cap(s) {
  if (!s) return '';
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

function getAux(subject) {
  const s = subject.toLowerCase();
  if (s === 'i') return 'am';
  if (['he', 'she', 'it'].includes(s)) return 'is';
  return 'are';
}

// ============================================================
// MAIN EXPORT
// ============================================================
export function applyGrammarRules(text) {
  let result = text;

  // Step 1: Sentence templates (highest priority)
  for (const tmpl of SENTENCE_TEMPLATES) {
    result = result.replace(tmpl.pattern, tmpl.output);
  }

  // Step 2: Reordering rules
  for (const rule of REORDER_RULES) {
    result = result.replace(rule.pattern, rule.replace);
  }

  // Step 3: Vocative commas
  result = handleVocatives(result);

  // Step 4: Punctuation
  result = addPunctuation(result);

  return result;
}
