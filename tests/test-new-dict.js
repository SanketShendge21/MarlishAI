// Testing the new dictionary engine with the 50k CSV data
// Run with: node tests/test-new-dict.js

// We need to mock the import of dictionary.json since we're in Node
const fs = require('fs');
const path = require('path');

// Manually load dictionary for testing in Node
const dictionary = JSON.parse(fs.readFileSync(path.join(__dirname, '../lib/dictionary.json'), 'utf8'));

/**
 * Copy of the engine logic (simplified for node test)
 */
function translateWithDictionary(text, sourceLang) {
  if (!text || !sourceLang) return null;
  
  const dict = dictionary[sourceLang];
  if (!dict) return null;

  const tokens = text.split(/([a-zA-Z\u0900-\u097F]+)/);
  const wordEntries = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (/[a-zA-Z\u0900-\u097F]/.test(t)) {
      wordEntries.push({ text: t, index: i });
    }
  }

  if (wordEntries.length === 0) return null;

  const translations = new Map();
  const skipIndices = new Set();
  
  let wordIdx = 0;
  while (wordIdx < wordEntries.length) {
    let matched = false;
    for (let len = 6; len >= 1; len--) {
      if (wordIdx + len > wordEntries.length) continue;
      const slice = wordEntries.slice(wordIdx, wordIdx + len);
      const phrase = slice.map(e => e.text.toLowerCase()).join(' ');
      
      if (dict[phrase]) {
        translations.set(slice[0].index, dict[phrase]);
        for (let k = 1; k < len; k++) {
          skipIndices.add(slice[k].index);
        }
        wordIdx += len;
        matched = true;
        break;
      }
    }
    if (!matched) wordIdx++;
  }

  const result = [];
  for (let i = 0; i < tokens.length; i++) {
    if (skipIndices.has(i)) continue;
    if (translations.has(i)) {
      result.push(translations.get(i));
    } else {
      result.push(tokens[i]);
    }
  }
  return result.join('');
}

// Test cases
const tests = [
    { input: "kal scene kya hai", lang: "hinglish" },
    { input: "tu kidhar hai bhai", lang: "hinglish" }, // should match "tu kidhar hai" and leave "bhai"
    { input: "main aa raha hu jaldi", lang: "hinglish" },
    { input: "tukidharhai", lang: "hinglish" }, // Variant test
];

console.log("--- New Dictionary Engine Test ---");
for (const t of tests) {
    const result = translateWithDictionary(t.input, t.lang);
    console.log(`Input: "${t.input}"`);
    console.log(`Output: "${result}"`);
    console.log('---');
}
