# Marlish.AI — Detailed Prompts for Language Conversion Research

> **Version:** 1.0 | **Date:** 2026-04-19 | **Status:** Draft
>
> This document contains carefully crafted prompts you can use with AI assistants
> (ChatGPT, Gemini, Claude, etc.) to gather deep information about each language
> conversion pair, NLP challenges, and implementation strategies.

---

## 1. Understanding Code-Mixed Languages

### Prompt 1.1: Hinglish Deep Dive

```
I am building a real-time translation web app called "Marlish.AI" that 
handles code-mixed Indian languages. I need a comprehensive understanding 
of "Hinglish" (Hindi typed in Roman/Latin script, often mixed with English 
words in the same sentence).

Please explain:
1. What are the most common code-switching patterns in Hinglish? 
   (intra-sentential, inter-sentential, tag-switching)
2. What is the Matrix Language Frame Model (MLFM) and how does it apply 
   to Hinglish? Which language is typically the "matrix" vs "embedded"?
3. List 30 common Hinglish phrases with their:
   - Roman spelling variations (e.g., "kya" / "kia" / "kiya")
   - Correct English translation
   - Correct Marathi translation (Devanagari)
4. What are the top 10 ambiguous words in Hinglish that have different 
   meanings in Hindi vs English vs Marathi? (e.g., "mai", "kal", "me")
5. How do vowel omission patterns work in informal Hinglish typing?
6. What slang terms are commonly used in Mumbai/Delhi Hinglish that a 
   translation model must understand?
7. What publicly available datasets exist for Hinglish NLP research?
   (mention L3Cube-HingCorpus, AI4Bharat BPCC, etc.)
```

### Prompt 1.2: Marlish (Marathi in Roman Script) Deep Dive

```
I am building a translation app that handles "Marlish" — Marathi language 
typed in English/Roman letters (e.g., "mi ghari jato" instead of 
"मी घरी जातो"). This is how millions of Marathi speakers type on 
QWERTY keyboards daily.

Please explain:
1. What are the unique challenges of Romanized Marathi compared to 
   Romanized Hindi?
2. List 30 common Marlish phrases with:
   - Common Roman spelling variations (including vowel-dropped versions)
   - Devanagari equivalent
   - English translation
   - Hindi translation (Devanagari)
3. What Marathi-specific grammatical structures make translation harder?
   (e.g., post-positions, verb conjugation patterns, gender agreement)
4. How does Marathi vocabulary differ from Hindi for the same concepts?
   (false friends and cognates)
5. What are Pune/Mumbai-specific Marathi slang terms that a model must 
   understand? (Puneri/Mumbaikar dialect differences)
6. What transliteration ambiguities exist specifically in Marlish?
   (e.g., "aahe" vs "ahe" vs "ahey" for आहे)
7. What are the best open-source resources for Marathi NLP?
   (mention L3Cube-MeCorpus, MeBERT, AI4Bharat IndicXlit, etc.)
8. How should the system handle Marathi words that have no direct 
   English equivalent? (culturally-specific concepts)
```

---

## 2. Translation Pair Research

### Prompt 2.1: Hinglish → English Translation Strategies

```
I am implementing a Hinglish-to-English translation feature in my web app.
The user types informal Hinglish like "kal office late jaunga, urgent 
kaam hai" and expects clean English output like "I will be late to the 
office tomorrow, I have urgent work."

Please help me with:
1. What is the best approach for Hinglish→English: rule-based, NMT, or 
   LLM-based? Compare pros/cons for a real-time web app.
2. How should I handle temporal ambiguity? ("kal" = yesterday OR tomorrow)
   What contextual clues resolve this?
3. How should I handle tone preservation? (casual Hinglish should produce 
   casual English, formal should produce formal)
4. Give me 20 challenging Hinglish→English test cases that would stress-test 
   a translation model, including:
   - Heavy code-switching
   - Slang and abbreviations
   - Sarcasm and idiomatic expressions
   - Vowel-dropped input
5. What few-shot prompting strategy works best with GPT-4o-mini or 
   Gemini Flash-Lite for this specific language pair?
6. What are common failure modes? (hallucination, over-formalization, 
   literal translation of idioms)
```

### Prompt 2.2: Hinglish → Marathi Translation Strategies

```
I am implementing Hinglish-to-Marathi translation. The user types in 
Hinglish (Roman script Hindi-English mix) and expects output in formal 
Devanagari Marathi.

Key challenge: The input is Hindi-influenced but the output must be 
proper MARATHI, not just Hindi in Devanagari.

Please help me with:
1. What vocabulary mappings are critical? (Hindi "kaam" → Marathi "काम" 
   but Hindi "samajhna" → Marathi "समजणे", not "समझना")
2. How do Hindi and Marathi grammar structures differ? 
   (verb conjugation, gender rules, honorifics)
3. Give me 20 test cases where naive Hindi→Marathi mapping fails 
   (where the Marathi output requires genuine Marathi phrasing, not 
   transliterated Hindi)
4. How should the system handle English words embedded in Hinglish 
   when translating to Marathi? (keep in English? transliterate to 
   Devanagari? translate to Marathi equivalent?)
5. What cultural nuances differ between Hindi and Marathi expression?
6. How to handle honorifics: Hindi "aap" vs Marathi "tumhi/aapan"?
```

### Prompt 2.3: English → Marathi Translation Strategies

```
I am implementing English-to-Marathi translation for my web app. This 
is the most "standard" pair but still has unique challenges for a 
real-time typing experience.

Please help me with:
1. What is the current state-of-the-art for English→Marathi MT?
   (Compare IndicTrans3, Google Translate API, Gemini, GPT for this pair)
2. What English constructs are hardest to translate to Marathi?
   (passive voice, compound sentences, phrasal verbs, idioms)
3. How should technical/modern English terms be handled when there 
   is no Marathi equivalent? (use English in Devanagari? create 
   Marathi neologism? provide both?)
4. Give me 20 test cases ranging from simple to complex English 
   sentences with their ideal Marathi translations.
5. What Marathi script rendering issues should I be aware of in 
   web browsers? (conjunct characters, matras, halant rendering)
6. How should the system handle English idioms?
   (literal vs cultural equivalent mapping)
```

### Prompt 2.4: Marlish → English Translation Strategies

```
I am implementing Marlish-to-English translation. Users type Marathi 
in Roman/English letters ("mi ghari jato") and expect English output 
("I am going home").

This is arguably the hardest pair because:
- Input is Romanized (non-standard spelling)
- Source language is Marathi (less resourced than Hindi)
- Output must be natural English

Please help me with:
1. What is the two-step vs one-step approach?
   a. Two-step: Marlish → Devanagari Marathi → English
   b. One-step: Marlish → English directly via LLM
   Which is better for real-time use? Why?
2. What are the most common spelling variations in Marlish?
   Create a table of 30 Marathi words with all their common 
   Roman spellings.
3. How does Marathi sentence structure differ from English?
   (SOV vs SVO, post-positions vs prepositions)
4. Give me 20 challenging Marlish→English test cases including:
   - Vowel-dropped input ("mzh nv" = "majha nav")
   - Pune slang
   - Mumbai slang
   - Formal Marathi in Roman script
5. What transliteration model (IndicXlit, RomanSetu) would you 
   recommend as a preprocessing step before LLM translation?
6. How to handle Marathi-specific concepts that don't map to English?
   (e.g., "जुगाड", "ताई/दादा" as social titles)
```

### Prompt 2.5: Marlish → Hindi Translation Strategies

```
I am implementing Marlish-to-Hindi translation. Users type Marathi 
in Roman letters and expect Hindi output in Devanagari.

This pair is interesting because:
- Marathi and Hindi share Devanagari script
- Many words are similar but not identical
- Grammar structures differ significantly

Please help me with:
1. What are the key grammatical differences between Marathi and Hindi?
   (verb forms, cases, post-positions, auxiliaries)
2. Create a vocabulary mapping table: 30 common Marathi words with 
   their Hindi equivalents (highlighting false friends and cognates)
3. How should the system handle Marathi-specific vocabulary that has 
   no Hindi equivalent? (transliterate? approximate? explain?)
4. Give me 20 test cases for Marlish→Hindi translation.
5. What happens when the Romanized input is ambiguous — could be 
   either Hindi or Marathi? How should the system disambiguate?
6. What role does the Matrix Language Frame Model play here?
```

---

## 3. Technical Implementation Research

### Prompt 3.1: Real-Time Streaming Architecture

```
I am building a real-time translation web app using Next.js 16 with 
Edge Functions. The app must provide translation output as the user 
types, with sub-400ms perceived latency.

My planned architecture:
- 250ms debounce on input
- AbortController to cancel stale requests
- Server-Sent Events (SSE) for streaming LLM output
- Vercel Edge Functions for API routing
- Gemini 3.1 Flash-Lite as primary LLM

Please help me with:
1. Show me a complete implementation of the debounce + AbortController 
   pattern in React (Next.js App Router) using a custom hook.
2. How to implement SSE streaming from a Next.js Edge API route that 
   proxies Gemini API's streaming response?
3. How to handle race conditions when the user types faster than the 
   API responds? (request ordering, stale response detection)
4. What is the optimal debounce interval for Indian mobile networks?
   (considering 3G/4G latency)
5. How to implement a TransformStream to convert Gemini's response 
   format to SSE events?
6. What error states must be handled in the streaming pipeline?
   (network drop, API timeout, rate limit, malformed response)
```

### Prompt 3.2: Prompt Engineering for Translation

```
I am using LLMs (Gemini Flash-Lite / GPT-4o-mini) for real-time 
code-mixed Indian language translation. I need to craft system prompts 
that maximize translation quality while minimizing hallucination.

My translation pairs:
1. Hinglish → English
2. Hinglish → Marathi
3. English → Marathi
4. Marlish → English
5. Marlish → Hindi

Please help me with:
1. What is the optimal system prompt structure for translation tasks?
   (persona, rules, examples, delimiters)
2. How many few-shot examples should I include? What quality criteria 
   should they meet?
3. How to prevent prompt injection when user input is part of the prompt?
   (delimiter strategies, instruction hierarchy)
4. How to handle the model wanting to "explain" or "note" things 
   instead of just translating?
5. What temperature and max_tokens settings work best for translation?
6. How to implement a fallback strategy when the primary model fails?
7. Show me a complete, production-ready system prompt for each of 
   my 5 translation pairs.
```

### Prompt 3.3: Edge Caching Strategy

```
I am implementing an edge caching layer for my translation app using 
Vercel KV (Redis). I want to cache translated phrases to reduce LLM 
API calls and cost.

Please help me with:
1. What is the optimal cache key strategy for translations?
   (How to normalize input text before hashing)
2. What TTL should I use for different types of translations?
   (common phrases vs unique sentences)
3. How to handle cache invalidation when prompts are updated?
4. What is the expected cache hit rate for a translation app?
5. Should I cache at the full-response level or token level?
6. How to implement cache warming for the top 1000 common phrases?
7. Show me a complete Vercel KV caching implementation in a Next.js 
   Edge Function.
```

---

## 4. UI/UX Research

### Prompt 4.1: Mobile-First Translation UI

```
I am designing a mobile-first UI for a real-time Indian language 
translation web app. The target users are Indian smartphone users 
(primarily Android, budget to mid-range devices).

Design requirements:
- Dual-panel: input (top 40%) + output (bottom 60%)
- Language selector dropdowns with swap button
- Action bar: Copy, TTS, Share to WhatsApp
- Dark/Light mode
- Must feel like a native app (PWA)

Please help me with:
1. What 2026 mobile UI trends should I incorporate?
   (Neumorphism, glassmorphism, micro-animations)
2. What is the optimal font for Devanagari rendering on the web?
   (Noto Sans Devanagari? Tiro Devanagari? font size?)
3. How to handle the virtual keyboard pushing content up on mobile?
   (viewport management, scroll behavior)
4. What accessibility considerations are critical for Indian users?
   (font size, contrast ratios, touch target sizes)
5. How to implement a smooth swap animation between languages?
6. What color palette works well for a translation app targeting 
   Indian users? (cultural color associations)
7. How to design the streaming text output so it feels natural 
   (not jarring) as tokens appear?
```

---

## 5. Competitive Intelligence

### Prompt 5.1: Market Analysis

```
I am building "Marlish.AI" — a real-time web app that translates 
code-mixed Indian languages (Hinglish, Marlish). I need to understand 
my competitive landscape.

Please analyze:
1. How does Google Translate handle Hinglish and Marlish input today?
   What are its specific failure modes?
2. What are the top 5 Hinglish/Marathi translation apps on Google 
   Play Store? What do users complain about in their reviews?
3. How do AI assistants (ChatGPT, Gemini, Claude) perform on 
   code-mixed translation compared to dedicated translation tools?
4. What niche features would differentiate a new translation app 
   from Google Translate in the Indian market?
5. What monetization models work for translation apps in India?
   (freemium, ads, API licensing, premium features)
6. What is the Total Addressable Market (TAM) for code-mixed 
   Indian language translation tools?
```

---

## 6. How to Use These Prompts

### Strategy

1. **Run each prompt** through ChatGPT-4, Gemini Advanced, or Claude
2. **Save responses** in the `docs/research/` folder
3. **Extract actionable data:**
   - Test cases → add to `tests/` directory
   - Vocabulary mappings → add to prompt few-shot examples
   - Failure modes → add to error handling logic
4. **Iterate prompts** — if answers are too generic, add more specific context
5. **Cross-reference** — run the same prompt on multiple models to compare quality

### Recommended Research Order

```
1. Prompt 1.1 + 1.2  → Understand the languages
2. Prompt 2.1 — 2.5  → Deep dive into each translation pair
3. Prompt 3.2         → Craft the system prompts
4. Prompt 3.1         → Build the technical architecture
5. Prompt 3.3         → Optimize with caching
6. Prompt 4.1         → Design the UI
7. Prompt 5.1         → Validate market positioning
```
