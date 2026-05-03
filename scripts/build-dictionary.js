const fs = require('fs');

const v1 = JSON.parse(fs.readFileSync('docs/Dictionary_Refs/hinglish_marlish_10000_dataset.json', 'utf8'));
const v2 = JSON.parse(fs.readFileSync('docs/Dictionary_Refs/hinglish_marlish_v2_25000_dataset.json', 'utf8'));

const dict = {
  hinglish_words: {},
  marlish_words: {},
  hinglish_phrases: {},
  marlish_phrases: {},
  english_to_hinglish_words: {},
  english_to_marlish_words: {},
  english_to_hinglish_phrases: {},
  english_to_marlish_phrases: {},
};

// ============================================================
// ESSENTIAL WORDS — manually curated high-frequency additions
// that the v1 dataset is missing
// ============================================================
const EXTRA_HINGLISH_WORDS = {
  // Verbs / auxiliaries
  'hai': 'is',
  'hain': 'are',
  'tha': 'was',
  'the': 'were',
  'hoga': 'will be',
  'hogi': 'will be',
  'ho': 'are',
  'hoon': 'am',
  'hun': 'am',
  'kar': 'do',
  'karo': 'do',
  'karna': 'to do',
  'karte': 'doing',
  'karti': 'doing',
  'raha': '-ing',
  'rahi': '-ing',
  'rahe': '-ing',
  'ja': 'go',
  'jao': 'go',
  'jaa': 'go',
  'jana': 'to go',
  'jata': 'goes',
  'jati': 'goes',
  'aa': 'come',
  'aao': 'come',
  'aana': 'to come',
  'aaya': 'came',
  'aayi': 'came',
  'aaye': 'came',
  'gaya': 'went',
  'gayi': 'went',
  'gaye': 'went',
  'kiya': 'did',
  'kiye': 'did',
  'de': 'give',
  'do': 'give',
  'dena': 'to give',
  'diya': 'gave',
  'di': 'gave',
  'le': 'take',
  'lo': 'take',
  'lena': 'to take',
  'liya': 'took',
  'li': 'took',
  'bol': 'say',
  'bolo': 'say',
  'bolna': 'to say',
  'bola': 'said',
  'boli': 'said',
  'dekh': 'see',
  'dekho': 'look',
  'dekhna': 'to see',
  'dekha': 'saw',
  'sun': 'listen',
  'suno': 'listen',
  'sunna': 'to listen',
  'suna': 'heard',
  'kha': 'eat',
  'khao': 'eat',
  'khana': 'food',
  'khaya': 'ate',
  'pee': 'drink',
  'peena': 'to drink',
  'ruk': 'stop',
  'ruko': 'wait',
  'chal': 'move',
  'chalo': 'come on',
  'chalte': 'going',
  'baith': 'sit',
  'baitho': 'sit',
  'baitha': 'sat',
  'uth': 'get up',
  'utho': 'get up',
  'so': 'sleep',
  'sona': 'to sleep',
  'soya': 'slept',
  'soyi': 'slept',
  'mil': 'meet',
  'milo': 'meet',
  'milna': 'to meet',
  'milte': 'meeting',
  'mila': 'met',
  'mili': 'met',
  'pata': 'know',
  'puch': 'ask',
  'pucho': 'ask',
  'samajh': 'understand',
  'samjha': 'understood',
  // Future tense
  'hoga': 'will be',
  'karunga': 'will do',
  'jaunga': 'will go',
  'aaunga': 'will come',
  'aayega': 'will come',
  'aaoge': 'will come',
  'milenge': 'will meet',
  'jayenge': 'will go',
  'karenge': 'will do',
  // Modal
  'sakta': 'can',
  'sakti': 'can',
  'chahiye': 'should',


  // Pronouns
  'main': 'I',
  'mai': 'I',
  'mein': 'I',
  'tu': 'you',
  'tum': 'you',
  'aap': 'you',
  'woh': 'he/she',
  'wo': 'he/she',
  'yeh': 'this',
  'ye': 'this',
  'hum': 'we',
  'log': 'people',

  // Possessives
  'mera': 'my',
  'meri': 'my',
  'mere': 'my',
  'tera': 'your',
  'teri': 'your',
  'tere': 'your',
  'tumhara': 'your',
  'tumhari': 'your',
  'uska': 'his/her',
  'uski': 'his/her',
  'hamara': 'our',
  'hamari': 'our',
  'apna': 'own',

  // Question words
  'kya': 'what',
  'kaise': 'how',
  'kyun': 'why',
  'kab': 'when',
  'kahan': 'where',
  'kidhar': 'where',
  'kaun': 'who',
  'kitna': 'how much',
  'kitne': 'how many',
  'konsa': 'which',

  // Common nouns
  'ghar': 'home',
  'office': 'office',
  'school': 'school',
  'college': 'college',
  'kaam': 'work',
  'paisa': 'money',
  'time': 'time',
  'din': 'day',
  'raat': 'night',
  'subah': 'morning',
  'sham': 'evening',
  'khana': 'food',
  'paani': 'water',
  'dost': 'friend',
  'bhai': 'brother',
  'behen': 'sister',
  'log': 'people',
  'jagah': 'place',
  'raasta': 'road',
  'gaadi': 'car',
  'phone': 'phone',
  'message': 'message',
  'number': 'number',

  // Adjectives
  'accha': 'good',
  'acha': 'good',
  'bura': 'bad',
  'bada': 'big',
  'chhota': 'small',
  'naya': 'new',
  'purana': 'old',
  'sahi': 'right',
  'galat': 'wrong',
  'theek': 'fine',

  // Adverbs / connectors
  'bahut': 'very',
  'thoda': 'a little',
  'abhi': 'now',
  'ab': 'now',
  'phir': 'then',
  'aur': 'and',
  'ya': 'or',
  'lekin': 'but',
  'par': 'but',
  'bhi': 'also',
  'sirf': 'only',
  'sab': 'all',
  'kuch': 'some',
  'koi': 'someone',
  'yahan': 'here',
  'wahan': 'there',
  'andar': 'inside',
  'bahar': 'outside',
  'upar': 'up',
  'neeche': 'down',
  'pehle': 'before',
  'baad': 'after',

  // Negation
  'nahi': 'no',
  'na': 'no',
  'mat': 'don\'t',

  // Time
  'kal': 'tomorrow',
  'aaj': 'today',
  'parso': 'day after',
  'abhi': 'now',

  // Slang / Chat
  'bro': 'bro',
  'yaar': 'dude',
  'boss': 'boss',
  'dude': 'dude',
  'chill': 'relax',
  'scene': 'plan',
  'setting': 'arrangement',
  'jhol': 'problem',
  'bakwas': 'nonsense',
  'mast': 'awesome',
  'zabardast': 'amazing',
  'shaadi': 'wedding',
  'party': 'party',
  'meeting': 'meeting',
  'plan': 'plan',
  'exam': 'exam',

  // English borrowings common in Hinglish
  'ok': 'ok',
  'yes': 'yes',
  'no': 'no',
  'please': 'please',
  'sorry': 'sorry',
  'thanks': 'thanks',
  'bye': 'bye',
  'hello': 'hello',
  'hi': 'hi',

  // Prepositions
  'mein': 'in',
  'pe': 'on',
  'se': 'from',
  'ko': 'to',
  'ke': 'of',
  'ka': 'of',
  'ki': 'of',
  'tak': 'until',
  'saath': 'with',
  'liye': 'for',
  'wala': 'one who',
};

const EXTRA_MARLISH_WORDS = {
  // Pronouns
  'mi': 'I',
  'tu': 'you',
  'to': 'he',
  'ti': 'she',
  'aamhi': 'we',
  'tumhi': 'you all',
  'te': 'they',

  // Possessives
  'majha': 'my',
  'majhi': 'my',
  'tujha': 'your',
  'tujhi': 'your',
  'tyacha': 'his',
  'ticha': 'her',
  'aamcha': 'our',

  // Question words
  'kay': 'what',
  'kaay': 'what',
  'kuthe': 'where',
  'kasa': 'how',
  'kashi': 'how',
  'ka': 'why',
  'kadhi': 'when',
  'kon': 'who',
  'kiti': 'how much',

  // Verbs
  'aahe': 'is',
  'ahes': 'are',
  'aahes': 'are',
  'aahet': 'are',
  'hota': 'was',
  'hoti': 'was',
  'jato': 'go',
  'jate': 'goes',
  'yeto': 'come',
  'yete': 'comes',
  'karto': 'do',
  'karte': 'does',
  'khato': 'eat',
  'pito': 'drink',
  'basto': 'sit',
  'ubha': 'stand',
  'zhopto': 'sleep',
  'bolto': 'speak',
  'mhanto': 'say',
  'bghto': 'see',
  'aikto': 'listen',
  'milto': 'meet',
  'det': 'give',
  'gheto': 'take',
  'khelto': 'play',
  'shikto': 'learn',

  // Common nouns
  'ghar': 'home',
  'ghari': 'home',
  'nav': 'name',
  'naav': 'name',
  'kaam': 'work',
  'paani': 'water',
  'jevhan': 'food',
  'vel': 'time',
  'divas': 'day',
  'ratra': 'night',
  'mitra': 'friend',
  'gaadi': 'car',
  'rasta': 'road',
  'shahar': 'city',
  'gaav': 'village',

  // Adjectives
  'chaan': 'nice',
  'changla': 'good',
  'vaait': 'bad',
  'motha': 'big',
  'lahan': 'small',
  'nava': 'new',
  'juna': 'old',

  // Adverbs / connectors
  'khup': 'very',
  'thoda': 'a little',
  'aata': 'now',
  'mag': 'then',
  'ani': 'and',
  'kinva': 'or',
  'pan': 'but',
  'sudha': 'also',
  'fakta': 'only',
  'sarv': 'all',
  'kahi': 'some',
  'ithe': 'here',
  'tithe': 'there',
  'aat': 'inside',
  'baher': 'outside',
  'var': 'up',
  'khali': 'down',

  // Negation
  'nahi': 'no',
  'nako': 'don\'t want',

  // Prepositions
  'madhe': 'in',
  'var': 'on',
  'pasun': 'from',
  'la': 'to',
  'cha': 'of',
  'chi': 'of',
  'sobat': 'with',
  'sathi': 'for',

  // Slang
  'bhau': 'bro',
  're': 'hey',
  'ga': 'hey (fem)',
  'mhanje': 'means',
  'barobar': 'correct',
};

// ============================================================
// BUILD DICTIONARY
// ============================================================

// 1. Index v1 words (original dataset)
v1.hinglish.forEach(w => {
  const key = w.word.toLowerCase().trim();
  if (!key) return;
  dict.hinglish_words[key] = w.meaning_en;
  const enKey = w.meaning_en.toLowerCase().trim();
  if (!dict.english_to_hinglish_words[enKey]) dict.english_to_hinglish_words[enKey] = key;
  (w.variants || []).forEach(v => {
    const vk = v.toLowerCase().trim();
    if (vk && vk !== key) dict.hinglish_words[vk] = w.meaning_en;
  });
});

v1.marlish.forEach(w => {
  const key = w.word.toLowerCase().trim();
  if (!key) return;
  dict.marlish_words[key] = w.meaning_en;
  const enKey = w.meaning_en.toLowerCase().trim();
  if (!dict.english_to_marlish_words[enKey]) dict.english_to_marlish_words[enKey] = key;
  (w.variants || []).forEach(v => {
    const vk = v.toLowerCase().trim();
    if (vk && vk !== key) dict.marlish_words[vk] = w.meaning_en;
  });
});

// 2. Add/override essential words (curated words take priority over v1)
for (const [k, v] of Object.entries(EXTRA_HINGLISH_WORDS)) {
  dict.hinglish_words[k] = v;
  const enKey = v.toLowerCase();
  if (!dict.english_to_hinglish_words[enKey]) {
    dict.english_to_hinglish_words[enKey] = k;
  }
}

for (const [k, v] of Object.entries(EXTRA_MARLISH_WORDS)) {
  dict.marlish_words[k] = v;
  const enKey = v.toLowerCase();
  if (!dict.english_to_marlish_words[enKey]) {
    dict.english_to_marlish_words[enKey] = k;
  }
}

// 3. Index v2 phrases
v2.hinglish_phrases.forEach(p => {
  const key = p.text.toLowerCase().trim();
  if (!key) return;
  dict.hinglish_phrases[key] = p.meaning_en;
  const enKey = p.meaning_en.toLowerCase().trim();
  if (!dict.english_to_hinglish_phrases[enKey]) dict.english_to_hinglish_phrases[enKey] = key;
});

v2.marlish_phrases.forEach(p => {
  const key = p.text.toLowerCase().trim();
  if (!key) return;
  dict.marlish_phrases[key] = p.meaning_en;
  const enKey = p.meaning_en.toLowerCase().trim();
  if (!dict.english_to_marlish_phrases[enKey]) dict.english_to_marlish_phrases[enKey] = key;
});

// ============================================================
// STATS
// ============================================================
console.log('\n=== DICTIONARY BUILD STATS ===');
for (const [k, v] of Object.entries(dict)) {
  console.log(`  ${k}: ${Object.keys(v).length} entries`);
}

// Write
fs.writeFileSync('public/dictionary.json', JSON.stringify(dict));
const sz = fs.statSync('public/dictionary.json').size;
console.log(`\n  Output: public/dictionary.json (${(sz/1024).toFixed(0)} KB)`);
console.log('  Done!\n');
