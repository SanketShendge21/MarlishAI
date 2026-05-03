'use client';

import { SwapButton } from './SwapButton';
import { LANGUAGES, getValidTargets, isValidPair } from '@/lib/languages';

export function LanguageSelector({ source, target, onSourceChange, onTargetChange, onSwap }) {
  // Show all languages that have at least one valid target
  const sourceLangs = LANGUAGES.filter(l => getValidTargets(l.code).length > 0);
  
  const validTargets = getValidTargets(source);

  return (
    <div className="flex items-center justify-between w-full mb-4 px-2">
      <div className="flex-1 relative">
        <select
          value={source}
          onChange={(e) => {
            const newSource = e.target.value;
            onSourceChange(newSource);
            // If current target is not valid for new source, pick the first valid one
            const newValidTargets = getValidTargets(newSource);
            if (!newValidTargets.some(t => t.code === target)) {
              onTargetChange(newValidTargets[0].code);
            }
          }}
          className="w-full appearance-none bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full px-4 py-2 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] font-medium text-[var(--color-text-primary)] cursor-pointer"
        >
          {sourceLangs.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.flag} {lang.label}
            </option>
          ))}
        </select>
      </div>

      <div className="px-3 flex-shrink-0">
        <SwapButton 
          onClick={onSwap} 
          disabled={!isValidPair(target, source)} 
        />
      </div>

      <div className="flex-1 relative">
        <select
          value={target}
          onChange={(e) => onTargetChange(e.target.value)}
          className="w-full appearance-none bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full px-4 py-2 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] font-medium text-[var(--color-text-primary)] cursor-pointer"
        >
          {validTargets.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.flag} {lang.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
