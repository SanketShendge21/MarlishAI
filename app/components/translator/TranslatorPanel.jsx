'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { addToHistory } from '@/lib/local-cache';
import { LanguageSelector } from './LanguageSelector';
import { InputArea } from './InputArea';
import { OutputArea } from './OutputArea';
import { ActionBar } from '@/app/components/actions/ActionBar';

export function TranslatorPanel() {
  const [source, setSource] = useState('hinglish');
  const [target, setTarget] = useState('english');
  const [inputText, setInputText] = useState('');

  const {
    translation, isLoading, error, tier, tierSource,
    matchLabel, confidence, latencyMs, isDictReady,
  } = useTranslation(inputText, source, target);

  // SWAP: swap languages + move translation → input, instant re-translate
  const handleSwap = useCallback(() => {
    const prevTranslation = translation;
    const prevSource = source;
    const prevTarget = target;

    setSource(prevTarget);
    setTarget(prevSource);

    if (prevTranslation) {
      setInputText(prevTranslation);
    }
  }, [source, target, translation]);

  const handleClear = useCallback(() => {
    setInputText('');
  }, []);

  const handleHistorySelect = useCallback((hInput, hSource, hTarget) => {
    setSource(hSource);
    setTarget(hTarget);
    setInputText(hInput);
  }, []);

  // Save to history on successful translation
  useEffect(() => {
    if (translation && inputText && !isLoading && tier > 0) {
      addToHistory(inputText, translation, source, target, tier);
    }
  }, [translation, inputText, isLoading, source, target, tier]);

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col pt-20 px-4 md:px-0">
      <div className="glass-panel rounded-[var(--radius-card)] w-full flex flex-col shadow-[var(--shadow-card)]">

        <div className="p-4 md:p-6 pb-2 border-b border-[var(--color-border)]">
          <LanguageSelector
            source={source}
            target={target}
            onSourceChange={setSource}
            onTargetChange={setTarget}
            onSwap={handleSwap}
          />
        </div>

        <div className="flex flex-col">
          <InputArea
            value={inputText}
            onValueChange={setInputText}
            onClear={handleClear}
            sourceLanguage={source}
          />

          <OutputArea
            text={translation}
            isLoading={isLoading}
            isDictLoading={!isDictReady && inputText.length > 0}
            error={error}
            tier={tier}
            tierSource={tierSource}
            matchLabel={matchLabel}
            confidence={confidence}
            targetLanguage={target}
          />
        </div>

      </div>

      <ActionBar
        translation={translation}
        originalText={inputText}
        targetLanguage={target}
        onHistorySelect={handleHistorySelect}
      />
    </div>
  );
}
