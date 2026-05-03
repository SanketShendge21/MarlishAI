import { useState, useEffect } from 'react';
import { getHistory, clearHistory } from '@/lib/local-cache';
import { X, Clock, Trash2 } from 'lucide-react';

export function HistoryDrawer({ isOpen, onClose, onSelect }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    const data = await getHistory(20);
    setHistory(data);
  };

  const handleClear = async () => {
    await clearHistory();
    setHistory([]);
  };

  const handleSelect = (item) => {
    onSelect(item.input, item.source, item.target);
    onClose();
  };

  // Helper to get relative time
  const getRelativeTime = (timestamp) => {
    const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
    const daysDifference = Math.round((timestamp - Date.now()) / (1000 * 60 * 60 * 24));
    const minsDifference = Math.round((timestamp - Date.now()) / (1000 * 60));
    
    if (Math.abs(minsDifference) < 60) return rtf.format(minsDifference, 'minute');
    if (Math.abs(daysDifference) < 1) return rtf.format(Math.round(minsDifference / 60), 'hour');
    return rtf.format(daysDifference, 'day');
  };

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 animate-fade-in"
        onClick={onClose}
      />
      
      <div className="fixed bottom-0 left-0 right-0 max-h-[60vh] bg-[var(--color-surface)] border-t border-[var(--color-border)] rounded-t-3xl shadow-2xl z-50 flex flex-col animate-slide-up">
        
        <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
          <div className="flex items-center gap-2 font-medium text-[var(--color-text-primary)]">
            <Clock className="w-5 h-5 text-[var(--color-primary)]" />
            Translation History
          </div>
          <div className="flex items-center gap-2">
            {history.length > 0 && (
              <button 
                onClick={handleClear}
                className="p-2 text-[var(--color-text-secondary)] hover:text-rose-500 transition-colors"
                aria-label="Clear history"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
            <button 
              onClick={onClose}
              className="p-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors bg-[var(--color-background)] rounded-full"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="overflow-y-auto p-4 space-y-3 flex-1 custom-scrollbar">
          {history.length === 0 ? (
            <div className="text-center py-8 text-[var(--color-text-secondary)]">
              No translations yet. Start typing to get started!
            </div>
          ) : (
            history.map((item) => (
              <div 
                key={item.id}
                onClick={() => handleSelect(item)}
                className="group p-3 rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] hover:border-[var(--color-primary)] cursor-pointer transition-all active:scale-[0.99]"
              >
                <div className="flex justify-between items-start mb-1 text-xs text-[var(--color-text-secondary)]">
                  <span className="bg-[var(--color-surface)] px-2 py-0.5 rounded-md">
                    {item.source} → {item.target}
                  </span>
                  <span>{getRelativeTime(item.timestamp)}</span>
                </div>
                <div className="text-sm font-medium text-[var(--color-text-primary)] line-clamp-2 mb-1">
                  {item.input}
                </div>
                <div className="text-sm text-[var(--color-primary)] line-clamp-2">
                  {item.output}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
