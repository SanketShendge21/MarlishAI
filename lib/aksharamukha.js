// Custom lightweight phonetic mapper for Roman ↔ Devanagari

const ROMAN_TO_DEVANAGARI = {
  // Vowels
  'a': 'अ', 'aa': 'आ', 'i': 'इ', 'ee': 'ई', 'u': 'उ', 'oo': 'ऊ', 'e': 'ए', 'ai': 'ऐ', 'o': 'ओ', 'au': 'औ', 'am': 'अं', 'ah': 'अः',
  // Consonants
  'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ',
  'ch': 'च', 'chh': 'छ', 'j': 'ज', 'jh': 'झ',
  't': 'ट', 'th': 'ठ', 'd': 'ड', 'dh': 'ढ', 'n': 'न',
  'p': 'प', 'ph': 'फ', 'f': 'फ़', 'b': 'ब', 'bh': 'भ', 'm': 'म',
  'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व', 'w': 'व',
  'sh': 'श', 'shh': 'ष', 's': 'स', 'h': 'ह',
  'ksh': 'क्ष', 'tr': 'त्र', 'gy': 'ज्ञ'
};

const MATRAS = {
  'a': '', 'aa': 'ा', 'i': 'ि', 'ee': 'ी', 'u': 'ु', 'oo': 'ू', 'e': 'े', 'ai': 'ै', 'o': 'ो', 'au': 'ौ', 'am': 'ं', 'ah': 'ः'
};

// Simple rule-based transliteration for MVP
export function romanToDevanagari(text) {
  if (!text) return '';
  
  let result = '';
  let i = 0;
  const lower = text.toLowerCase();
  
  while (i < lower.length) {
    // Check 3-char chunks (e.g. ksh)
    if (i + 2 < lower.length && ROMAN_TO_DEVANAGARI[lower.substring(i, i + 3)]) {
      result += ROMAN_TO_DEVANAGARI[lower.substring(i, i + 3)];
      i += 3;
      continue;
    }
    // Check 2-char chunks (e.g. kh, aa)
    if (i + 1 < lower.length && ROMAN_TO_DEVANAGARI[lower.substring(i, i + 2)]) {
      result += ROMAN_TO_DEVANAGARI[lower.substring(i, i + 2)];
      i += 2;
      continue;
    }
    // Check 1-char chunk
    if (ROMAN_TO_DEVANAGARI[lower[i]]) {
      result += ROMAN_TO_DEVANAGARI[lower[i]];
    } else {
      result += text[i]; // keep original character if not found (like spaces or punctuation)
    }
    i++;
  }
  
  // Note: This is a highly simplified phonetic mapper for MVP.
  // Full Aksharamukha integration handles halants and matras properly.
  // For the sake of the offline sub-5KB requirement, this gives a rough approximation.
  return result;
}

export function isDevanagari(text) {
  return /[\u0900-\u097F]/.test(text);
}

export function isRoman(text) {
  return /^[a-zA-Z\s.,!?]+$/.test(text);
}
