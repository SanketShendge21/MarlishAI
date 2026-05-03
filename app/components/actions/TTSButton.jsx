import { Volume2 } from 'lucide-react';
import { useTTS } from '@/hooks/useTTS';

export function TTSButton({ text, targetLanguage }) {
  const { speak, speaking, supported } = useTTS();

  if (!supported) return null;

  return (
    <button
      onClick={() => speak(text, targetLanguage)}
      disabled={!text}
      className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium transition-all
        ${!text 
          ? 'opacity-50 cursor-not-allowed text-[var(--color-text-secondary)]' 
          : speaking 
            ? 'bg-indigo-500/10 text-[var(--color-primary)]'
            : 'hover:bg-[var(--color-surface)] text-[var(--color-text-primary)] hover:text-[var(--color-primary)] active:scale-95'
        }
      `}
      aria-label={speaking ? "Stop speaking" : "Listen to translation"}
    >
      <Volume2 className={`w-4 h-4 ${speaking ? 'animate-pulse text-[var(--color-primary)]' : ''}`} />
      <span className="hidden sm:inline">Listen</span>
    </button>
  );
}
