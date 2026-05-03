'use client';

import { useState, useEffect } from 'react';
import { WifiOff, Wifi } from 'lucide-react';

export function OfflineIndicator() {
  const [isOffline, setIsOffline] = useState(false);
  const [backOnline, setBackOnline] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check initial state
    if (!navigator.onLine) {
      setIsOffline(true);
    }

    const handleOnline = () => {
      setIsOffline(false);
      setBackOnline(true);
      setTimeout(() => setBackOnline(false), 3000);
    };

    const handleOffline = () => {
      setIsOffline(true);
      setBackOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOffline && !backOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 flex justify-center pointer-events-none p-2 animate-slide-down">
      <div 
        className={`flex flex-col md:flex-row items-center gap-2 px-4 py-2 rounded-full shadow-lg text-sm font-medium backdrop-blur-md pointer-events-auto transition-colors
          ${isOffline 
            ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20' 
            : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
          }
        `}
      >
        {isOffline ? (
          <>
            <div className="flex items-center gap-2">
              <WifiOff className="w-4 h-4" />
              <span>Offline</span>
            </div>
            <span className="opacity-80 text-xs hidden sm:inline">— translations may be unavailable</span>
          </>
        ) : (
          <>
            <Wifi className="w-4 h-4" />
            <span>Back online</span>
          </>
        )}
      </div>
    </div>
  );
}
