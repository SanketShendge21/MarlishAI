import { useMemo } from 'react';
import { romanToDevanagari, devanagariToRoman } from '@/lib/aksharamukha';

export function useTransliterate(target) {
  // Determine if target uses Devanagari script
  const isDevanagariTarget = target === 'hindi' || target === 'marathi';

  // Return transliteration function based on target
  const transliterate = useMemo(() => {
    return (text) => {
      if (!text) return '';
      if (isDevanagariTarget) {
        return romanToDevanagari(text);
      }
      return text;
    };
  }, [isDevanagariTarget]);

  return { transliterate, isDevanagariTarget };
}
