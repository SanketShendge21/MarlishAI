const DEVANAGARI_REGEX = /[\u0900-\u097F]/;
const MARATHI_MARKERS = ['aahe', 'ahe', 'mala', 'kuthe', 'kay', 'tuza', 'mazha', 'jato', 'yeto', 'karto'];
const HINDI_MARKERS = ['hai', 'hain', 'kya', 'mujhe', 'tum', 'mera', 'karo', 'raha', 'wala', 'jaunga'];

export function detectLanguage(text) {
  if (!text) return 'english';

  const lower = text.toLowerCase().trim();
  
  // Check for Devanagari script
  if (DEVANAGARI_REGEX.test(text)) {
    return 'devanagari'; // Could be Hindi or Marathi
  }
  
  const words = lower.split(/\s+/);
  const marathiScore = words.filter(w => MARATHI_MARKERS.includes(w)).length;
  const hindiScore = words.filter(w => HINDI_MARKERS.includes(w)).length;
  
  if (marathiScore > hindiScore) return 'marlish';
  if (hindiScore > 0) return 'hinglish';
  return 'english';
}
