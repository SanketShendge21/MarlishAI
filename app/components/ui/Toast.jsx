'use client';

import { useState, useCallback } from 'react';

// This acts as a simple singleton state manager for the toast.
// In a real app, you might use context or a state management library.
let globalToastSetter = null;

export function useToast() {
  const showToast = useCallback((message, type = 'info') => {
    if (globalToastSetter) {
      globalToastSetter({ message, type });
    }
  }, []);

  return { showToast };
}

export function ToastContainer() {
  const [toast, setToast] = useState(null);

  // Register the setter function globally
  globalToastSetter = setToast;

  return <Toast toast={toast} onClose={() => setToast(null)} />;
}

export function Toast({ toast, onClose }) {
  if (!toast) return null;

  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 animate-slide-up">
      <div className={`px-4 py-2 rounded-full shadow-lg border backdrop-blur-md text-sm font-medium flex items-center gap-2
        ${toast.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400' : ''}
        ${toast.type === 'error' ? 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400' : ''}
        ${toast.type === 'info' ? 'bg-blue-500/10 border-blue-500/20 text-blue-600 dark:text-blue-400' : ''}
      `}>
        {toast.message}
        <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">×</button>
      </div>
    </div>
  );
}
