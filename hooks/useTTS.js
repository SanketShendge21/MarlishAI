import { useState, useEffect, useCallback } from 'react';

export function useTTS() {
  const [speaking, setSpeaking] = useState(false);
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    if (typeof window !== 'undefined' && !window.speechSynthesis) {
      setSupported(false);
    }
  }, []);

  const speak = useCallback((text, targetLang) => {
    if (!supported || !window.speechSynthesis || !text) return;

    // Stop any current speech
    window.speechSynthesis.cancel();
    setSpeaking(false);

    if (speaking) {
      // If we were already speaking, just cancel and return (toggle off)
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Select Voice
    const voices = window.speechSynthesis.getVoices();
    let selectedVoice = null;
    
    const langCode = targetLang === 'hindi' ? 'hi-IN' : 
                     targetLang === 'marathi' ? 'mr-IN' : 
                     'en-IN'; // Default to Indian English for Hinglish/Marlish/English
                     
    // Find preferred voice
    selectedVoice = voices.find(v => v.lang.includes(langCode));
    
    // Fallback logic
    if (!selectedVoice && targetLang === 'marathi') {
      selectedVoice = voices.find(v => v.lang.includes('hi-IN')); // Hindi fallback for Marathi
    }
    if (!selectedVoice) {
      selectedVoice = voices.find(v => v.lang.includes('en')); // English fallback
    }

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, [supported, speaking]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return { speak, speaking, supported };
}
