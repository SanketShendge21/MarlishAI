'use client';

import { useTheme } from '@/hooks/useTheme';
import { Sun, Moon } from 'lucide-react';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="w-10 h-10" />; // placeholder

  return (
    <button
      onClick={toggleTheme}
      className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-[var(--color-border)] transition-colors"
      aria-label="Toggle dark mode"
    >
      <div className={`transition-transform duration-300 ${theme === 'dark' ? 'rotate-180' : 'rotate-0'}`}>
        {theme === 'dark' ? (
          <Sun className="w-5 h-5 text-[var(--color-text-primary)]" />
        ) : (
          <Moon className="w-5 h-5 text-[var(--color-text-primary)]" />
        )}
      </div>
    </button>
  );
}
