import { getCached, setCached } from './local-cache';
import { translate, isDictLoaded } from './dictionary-engine';

/**
 * Translation Router — Offline JSON-First
 * 
 * Tier 1: IndexedDB cache (instant)
 * Tier 2: 8-layer dictionary engine (< 50ms)
 */
export async function routeTranslation(input, source, target, context) {
  const start = performance.now();

  if (!input || input.trim().length < 1) {
    return { tier: 0, result: '', source: 'empty', label: '', confidence: 0 };
  }

  // Tier 1: Cache
  try {
    const cached = await getCached(input, source, target);
    if (cached) {
      return {
        tier: 1, result: cached, source: 'cache',
        label: 'exact_match', confidence: 1.0,
        latencyMs: performance.now() - start,
      };
    }
  } catch (e) { /* cache miss */ }

  // Tier 2: Dictionary engine
  if (context.isDictReady && isDictLoaded()) {
    const result = translate(input, source, target);
    if (result && result.text) {
      setCached(input, source, target, result.text, 2).catch(() => {});
      return {
        tier: 2, result: result.text, source: 'dictionary',
        label: result.label || 'smart_guess',
        confidence: result.confidence || 0.5,
        latencyMs: performance.now() - start,
      };
    }
  }

  return { tier: 0, result: '', source: 'unavailable', label: '', confidence: 0 };
}
