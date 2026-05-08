'use client';

import { LoadingSkeleton } from '../ui/LoadingSkeleton';
import { AlertCircle, CheckCircle2, Lightbulb, Wrench } from 'lucide-react';

const LABEL_CONFIG = {
  exact_match: {
    text: 'Exact Match',
    icon: CheckCircle2,
    color: 'text-emerald-500',
    bg: 'bg-emerald-500/10',
  },
  smart_guess: {
    text: 'Smart Guess',
    icon: Lightbulb,
    color: 'text-amber-500',
    bg: 'bg-amber-500/10',
  },
  typo_fixed: {
    text: 'Typo Fixed',
    icon: Wrench,
    color: 'text-blue-400',
    bg: 'bg-blue-400/10',
  },
  partial: {
    text: 'Partial',
    icon: Lightbulb,
    color: 'text-orange-400',
    bg: 'bg-orange-400/10',
  },
};

export function OutputArea({ text, isLoading, isDictLoading, error, tier, matchLabel, confidence, targetLanguage }) {
  const isDevanagari = targetLanguage === 'hindi' || targetLanguage === 'marathi';
  const fontFamilyClass = isDevanagari ? 'font-devanagari tracking-wide' : 'font-sans';
  const labelCfg = LABEL_CONFIG[matchLabel];

  return (
    <div className="relative w-full rounded-b-[var(--radius-card)] overflow-hidden bg-[var(--color-surface)]/40 min-h-[160px] p-4 md:p-6 transition-all border-t border-[var(--color-border)]/50">

      <div className="w-full mt-2">
        {isLoading && !text ? (
          <LoadingSkeleton />
        ) : isDictLoading ? (
          <div className="flex flex-col gap-3 animate-pulse">
            <div className="h-4 w-3/4 bg-[var(--color-border)] rounded shadow-sm"></div>
            <div className="h-4 w-1/2 bg-[var(--color-border)] rounded shadow-sm"></div>
            <p className="text-xs text-[var(--color-text-secondary)] mt-2">Loading language engine...</p>
          </div>
        ) : error ? (
          <div className="flex items-start gap-2 text-[var(--color-error)] animate-fade-in bg-red-50 dark:bg-red-900/10 p-3 rounded-lg border border-red-100 dark:border-red-900/20">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p className="text-sm md:text-base">{error}</p>
          </div>
        ) : text ? (
          <div className="animate-fade-in">
            <div className={`text-lg md:text-xl text-[var(--color-text-primary)] leading-relaxed whitespace-pre-wrap ${fontFamilyClass}`}>
              {text}
            </div>

            {/* Match label badge */}
            {labelCfg && (
              <div className="flex items-center gap-2 mt-4">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${labelCfg.color} ${labelCfg.bg}`}>
                  <labelCfg.icon className="w-3 h-3" />
                  {labelCfg.text}
                </span>
                {confidence > 0 && (
                  <span className="text-xs text-[var(--color-text-secondary)]/60">
                    {Math.round(confidence * 100)}% confidence
                  </span>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="text-[var(--color-text-secondary)]/60 text-lg md:text-xl font-medium mt-4">
            Interpreted output will appear here...
          </div>
        )}
      </div>
    </div>
  );
}
