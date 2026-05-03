import { useState, useEffect, useRef } from 'react';

/**
 * useAdaptiveDebounce — Smart debounce that adapts to user behavior
 * 
 * Short input (< 15 chars):  300ms  (quick words)
 * Medium input (< 50 chars): 500ms  (phrases)
 * Long input (50+ chars):    800ms  (sentences, let them finish)
 * 
 * The delay is based on the current text length, not a fixed value.
 * Instant triggers (swap, dropdown, clear) bypass debounce entirely
 * because those change source/target state directly, not the text.
 */
export function useAdaptiveDebounce(value, baseDelay = 400) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  const timerRef = useRef(null);

  useEffect(() => {
    // Clear on empty (instant)
    if (!value || value.trim().length === 0) {
      setDebouncedValue(value);
      return;
    }

    // Adaptive delay based on input length
    const len = value.length;
    let delay;
    if (len < 15) delay = 300;       // Short: fast response
    else if (len < 50) delay = 500;  // Medium: let phrase form
    else delay = 800;                 // Long: let sentence finish

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setDebouncedValue(value), delay);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [value, baseDelay]);

  return debouncedValue;
}

/**
 * Legacy fixed debounce (kept for backward compat)
 */
export function useDebounce(value, delay = 250) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
