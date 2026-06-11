import { useState, useEffect, useRef, useCallback } from 'react';
import { useAdaptiveDebounce } from './useDebounce';

/**
 * useTranslation — Core translation hook (v6 — Pure ML API)
 * 
 * Calls the Marlish.AI FastAPI backend for translation.
 * The API handles: Marlish → Devanagari (transliteration) → English (NLLB-200)
 * 
 * Uses adaptive debounce (300ms–800ms based on input length).
 * Returns the same shape as v5 so UI components need zero changes.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

  // Check API health on mount (replaces dictionary loading)
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(res => res.json())
      .then(data => {
        if (data.ready) {
          setIsDictReady(true);
        } else {
          setError('Translation model is still loading. Please wait...');
        }
      })
      .catch(() => {
        // API might not be reachable yet — still allow typing
        // Will retry on first translate call
        setIsDictReady(true);
      });
  }, []);

  // Core translate function — calls the API
  const doTranslate = useCallback(async (text, src, tgt, ready) => {
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

    // Abort previous request
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.trim(), source: src, target: tgt }),
        signal: controller.signal,
      });

      if (controller.signal.aborted) return;

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `API error: ${response.status}`);
      }

      const data = await response.json();

      if (controller.signal.aborted) return;

      setTranslation(data.translation);
      setTier(3); // API tier
      setTierSource('api');
      setMatchLabel('ml_translation');
      setConfidence(0.9);
      setLatencyMs(data.latency_ms || 0);
      setError(null);
    } catch (err) {
      if (err.name === 'AbortError' || controller.signal.aborted) return;
      setError('Translation failed. Is the API server running?');
      setTranslation('');
      setTier(0);
      setTierSource('');
      setMatchLabel('');
      setConfidence(0);
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
    matchLabel,   // 'ml_translation'
    confidence,   // 0.0 – 1.0
    latencyMs,
    isDictReady,
  };
}
