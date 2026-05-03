'use client';

import { ArrowRightLeft } from 'lucide-react';

export function SwapButton({ onClick, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center w-10 h-10 rounded-full bg-[var(--color-surface)] border border-[var(--color-border)] shadow-sm transition-all duration-300
        ${disabled 
          ? 'opacity-50 cursor-not-allowed' 
          : 'hover:bg-[var(--color-border)] hover:rotate-180 active:scale-95 cursor-pointer'
        }
      `}
      aria-label="Swap languages"
    >
      <ArrowRightLeft className="w-4 h-4 text-[var(--color-text-primary)]" />
    </button>
  );
}
