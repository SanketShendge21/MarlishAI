import { Copy, Check } from 'lucide-react';
import { useClipboard } from '@/hooks/useClipboard';
import { useToast } from '@/app/components/ui/Toast';

export function CopyButton({ text }) {
  const { copy, copied } = useClipboard();
  const { showToast } = useToast();

  const handleCopy = async () => {
    if (!text) return;
    const success = await copy(text);
    if (success) {
      showToast('Copied to clipboard!', 'success');
    } else {
      showToast('Failed to copy', 'error');
    }
  };

  return (
    <button
      onClick={handleCopy}
      disabled={!text}
      className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium transition-all
        ${!text 
          ? 'opacity-50 cursor-not-allowed text-[var(--color-text-secondary)]' 
          : 'hover:bg-[var(--color-surface)] text-[var(--color-text-primary)] hover:text-[var(--color-primary)] active:scale-95'
        }
      `}
      aria-label="Copy translation"
    >
      <div className="relative w-4 h-4">
        <div className={`absolute inset-0 transition-all duration-200 ${copied ? 'opacity-0 scale-50' : 'opacity-100 scale-100'}`}>
          <Copy className="w-4 h-4" />
        </div>
        <div className={`absolute inset-0 text-emerald-500 transition-all duration-200 ${copied ? 'opacity-100 scale-100' : 'opacity-0 scale-50'}`}>
          <Check className="w-4 h-4" />
        </div>
      </div>
      <span className="hidden sm:inline">{copied ? 'Copied!' : 'Copy'}</span>
    </button>
  );
}
