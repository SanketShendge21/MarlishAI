import { useState, useEffect, useRef, useCallback } from 'react';
import { useAdaptiveDebounce } from './useDebounce';
import { routeTranslation } from '@/lib/tier-router';
import { loadDictionary } from '@/lib/dictionary-engine';

/**
 * useTranslation — Core translation hook (v5)
 * 
 * Uses adaptive debounce (300ms–800ms based on input length).
 * Returns confidence label: 'exact_match' | 'smart_guess' | 'typo_fixed' | 'partial'
 * 
 * Triggers on EVERY change to:
 *   - inputText (via adaptive debounce)
 *   - source language (instant, no debounce)
 *   - target language (instant, no debounce)
 *   - dictionary readiness
 */
export function useTranslation(inputText, source, target) {
  const [translation, setTranslation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tier, setTier] = useState(0);
  const [tierSource, setTierSource] = useState('');
  const [matchLabel, setMatchLabel] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [latencyMs, setLatencyMs] = useState(0);
  const [isDictReady, setIsDictReady] = useState(false);

  const abortRef = useRef(null);

  // Adaptive debounce: short input = fast, long input = slower
  const debouncedText = useAdaptiveDebounce(inputText);

  // Load dictionary once on mount
  useEffect(() => {
    loadDictionary('/dictionary.json')
      .then(() => setIsDictReady(true))
      .catch(err => {
        console.error('[useTranslation] Dict load failed:', err);
        setError('Dictionary failed to load.');
      });
  }, []);

  // Core translate function
  const doTranslate = useCallback(async (text, src, tgt, dictReady) => {
    // Clear on empty
    if (!text || text.trim().length < 1) {
      setTranslation('');
      setTier(0);
      setTierSource('');
      setMatchLabel('');
      setConfidence(0);
      setIsLoading(false);
      setError(null);
      return;
    }

    if (!dictReady) {
      setIsLoading(true);
      return;
    }

    // Abort previous
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setError(null);

    try {
      const result = await routeTranslation(text, src, tgt, {
        isDictReady: dictReady,
        signal: controller.signal,
      });

      if (controller.signal.aborted) return;

      if (result.tier > 0 && result.result) {
        setTranslation(result.result);
        setTier(result.tier);
        setTierSource(result.source);
        setMatchLabel(result.label || '');
        setConfidence(result.confidence || 0);
        setLatencyMs(result.latencyMs || 0);
        setError(null);
      } else {
        setTranslation('');
        setTier(0);
        setTierSource(result.source || '');
        setMatchLabel('');
        setConfidence(0);
      }
    } catch (err) {
      if (err.name !== 'AbortError' && !controller.signal.aborted) {
        setError('Translation failed.');
        setTranslation('');
      }
    } finally {
      if (!controller.signal.aborted) setIsLoading(false);
    }
  }, []);

  // Re-translate on every relevant state change
  useEffect(() => {
    doTranslate(debouncedText, source, target, isDictReady);
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [debouncedText, source, target, isDictReady, doTranslate]);

  return {
    translation,
    isLoading,
    error,
    tier,
    tierSource,
    matchLabel,   // 'exact_match' | 'smart_guess' | 'typo_fixed' | 'partial'
    confidence,   // 0.0 – 1.0
    latencyMs,
    isDictReady,
  };
}
