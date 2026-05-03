import { Share2 } from 'lucide-react';

export function ShareButton({ text, originalText }) {
  const handleShare = async () => {
    if (!text) return;
    
    const message = `Original: ${originalText}\nTranslation: ${text}\n\n— Translated by Marlish.AI`;
    
    // Use Native Web Share API if available (Mobile)
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Marlish.AI Translation',
          text: message,
        });
        return;
      } catch (err) {
        console.warn('Native share failed/cancelled', err);
        // Fallback to WhatsApp if share API fails
      }
    }

    // Fallback: WhatsApp share link
    const url = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <button
      onClick={handleShare}
      disabled={!text}
      className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium transition-all
        ${!text 
          ? 'opacity-50 cursor-not-allowed text-[var(--color-text-secondary)]' 
          : 'hover:bg-[var(--color-surface)] text-[var(--color-text-primary)] hover:text-[var(--color-primary)] active:scale-95'
        }
      `}
      aria-label="Share via WhatsApp"
    >
      <Share2 className="w-4 h-4" />
      <span className="hidden sm:inline">Share</span>
    </button>
  );
}
