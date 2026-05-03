'use client';

import { useState } from 'react';
import { CopyButton } from './CopyButton';
import { TTSButton } from './TTSButton';
import { ShareButton } from './ShareButton';
import { HistoryDrawer } from './HistoryDrawer';
import { Clock } from 'lucide-react';

export function ActionBar({ translation, originalText, targetLanguage, onHistorySelect }) {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  return (
    <>
      <div className="flex items-center justify-between w-full mt-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full p-2 shadow-sm glass-panel mx-auto max-w-xl md:inline-flex md:w-auto">
        
        <div className="flex items-center gap-1 md:gap-2">
          <CopyButton text={translation} />
          <TTSButton text={translation} targetLanguage={targetLanguage} />
          <ShareButton text={translation} originalText={originalText} />
        </div>

        <div className="h-6 w-px bg-[var(--color-border)] mx-2"></div>

        <button
          onClick={() => setIsHistoryOpen(true)}
          className="flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-all active:scale-95"
          aria-label="View history"
        >
          <Clock className="w-4 h-4" />
          <span className="hidden sm:inline">History</span>
        </button>
      </div>

      <HistoryDrawer 
        isOpen={isHistoryOpen} 
        onClose={() => setIsHistoryOpen(false)} 
        onSelect={onHistorySelect}
      />
    </>
  );
}
