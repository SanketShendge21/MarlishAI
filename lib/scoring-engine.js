/**
 * SCORING ENGINE — Layer 7
 * 
 * Calculates the confidence score and assigns a match label
 * based on the NLP features triggered during translation.
 * 
 * Labels used by UI badges:
 * - exact_match (Green): Phrases, intents, compound verbs
 * - smart_guess (Blue): High word-match ratio + context disambiguation
 * - typo_fixed (Orange): Relied on Levenshtein fuzzy matching
 * - partial (Gray): Significant passthrough of unknown words
 */

export function calculateScore(matchTypes, totalTokens) {
  if (totalTokens === 0) return { confidence: 0, label: 'empty' };

  // Count how many tokens were actually mapped (not passthrough)
  const matched = matchTypes.filter(t => t !== 'passthrough').length;
  const matchRatio = matched / totalTokens;

  // Identify features used
  const hasIntent = matchTypes.includes('intent');
  const hasPhrases = matchTypes.includes('phrase') || matchTypes.includes('compound_verb');
  const hasDisambig = matchTypes.includes('disambiguated') || matchTypes.includes('vocative') || matchTypes.includes('tense_verb');
  const hasFuzzy = matchTypes.includes('typo_fixed');

  // Base score is the raw translation ratio
  let confidence = matchRatio;

  // Apply NLP confidence bonuses
  if (hasIntent) confidence += 0.30;
  if (hasPhrases) confidence += 0.15;
  if (hasDisambig) confidence += 0.10;

  // Apply approximation penalties
  if (hasFuzzy) confidence -= 0.05;

  // Clamp between 0.0 and 1.0
  confidence = Math.min(1.0, Math.max(0.0, confidence));

  // Determine user-facing badge label
  let label = 'partial';
  if (hasIntent || hasPhrases) {
    label = 'exact_match';
  } else if (hasFuzzy) {
    label = 'typo_fixed';
  } else if (matchRatio >= 0.8 || hasDisambig) {
    label = 'smart_guess';
  }

  // Overrides for 100% literal matches
  if (matchRatio === 1.0 && label === 'partial') {
    label = 'exact_match';
  }

  return { confidence, label };
}
