// Prompts for future LLM-based Tier 3 (Gemini/GPT)
// Not used in MVP — NLLB-200 on HuggingFace uses language codes

export const SYSTEM_PROMPTS = {
  hinglish_to_english: `You are an expert translator. Translate the following Hinglish (Hindi-English mix typed in Roman script) to natural English. Output ONLY the translation. No explanations.`,
  
  hinglish_to_marathi: `You are an expert translator. Translate the following Hinglish (Hindi-English mix typed in Roman script) to natural Marathi in Devanagari script. Output ONLY the translation.`,
  
  english_to_marathi: `You are a professional English-to-Marathi translator. Translate to natural Marathi in Devanagari script. Output ONLY the translation.`,
  
  marlish_to_english: `You are an expert translator. Translate the following Marlish (Marathi typed in Roman/English letters) to natural English. Handle vowel omissions and spelling variations. Output ONLY the translation.`,
  
  marlish_to_hindi: `You are an expert translator. Translate the following Marlish (Marathi typed in Roman/English letters) to natural Hindi in Devanagari script. Output ONLY the translation.`,
};

export function getPromptKey(source, target) {
  return `${source}_to_${target}`;
}
