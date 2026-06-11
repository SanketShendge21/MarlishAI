'use client';

import { X } from 'lucide-react';
import { useRef, useEffect, useCallback } from 'react';

export function InputArea({ value = '', onValueChange, onClear, sourceLanguage, maxLength = 500 }) {
  const textareaRef = useRef(null);

  // Auto-focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Auto-resize when value changes
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(Math.max(el.scrollHeight, 120), 300)}px`;
    }
  }, [value]);

  const handleChange = useCallback((e) => {
    onValueChange?.(e.target.value);
  }, [onValueChange]);

  const handleClear = useCallback(() => {
    onClear?.();
    textareaRef.current?.focus();
  }, [onClear]);

  const getPlaceholder = () => {
    switch (sourceLanguage) {
      case 'hinglish': return 'Paste Hinglish chat... e.g., kal scene kya hai';
      case 'marlish':  return 'Paste Marlish chat... e.g., mi ghari jato';
      case 'english':  return 'Type in English... e.g., where are you';
      case 'marathi':  return 'Type in Marathi...';
      case 'hindi':    return 'Type in Hindi...';
      default:         return 'Paste your chat...';
    }
  };

  return (
    <div className="relative w-full rounded-t-[var(--radius-card)] overflow-hidden group border-b border-[var(--color-border)]/50">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        maxLength={maxLength}
        placeholder={getPlaceholder()}
        className="w-full min-h-[120px] max-h-[300px] resize-none p-4 md:p-6 bg-transparent text-[var(--color-text-primary)] text-base md:text-lg focus:outline-none font-sans placeholder-[var(--color-text-secondary)]/50 transition-all scrollbar-hide"
        spellCheck="false"
        autoComplete="off"
        id="translator-input"
      />

      {value.length > 0 && (
        <button
          onClick={handleClear}
          className="absolute top-4 right-4 p-1.5 rounded-full text-[var(--color-text-secondary)] hover:bg-[var(--color-border)] hover:text-[var(--color-text-primary)] transition-colors z-20"
          aria-label="Clear text"
        >
          <X className="w-4 h-4 md:w-5 md:h-5" />
        </button>
      )}

      <div className="absolute bottom-3 right-4 text-xs font-medium text-[var(--color-text-secondary)]/80 select-none pointer-events-none">
        {value.length} <span className="opacity-50">/ {maxLength}</span>
      </div>
    </div>
  );
}
