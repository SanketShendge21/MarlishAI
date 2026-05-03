# Marlish.AI — AI/ML Models & NLP Strategy

> **Version:** 2.0 | **Date:** 2026-04-19 | **Status:** Updated (Open-Source First)
>
> **REVISION NOTE:** Model strategy revised from commercial APIs (Gemini/GPT) to
> open-source, client-side-first models. See [08-tech-stack.md](file:///d:/Learning-Tutorials/Apni%20Bhasha/docs/08-tech-stack.md) for full stack details.

---

## 1. The Core NLP Challenge

Marlish.AI must solve three interconnected NLP problems simultaneously:

```
Problem 1: TRANSLITERATION
  Roman script → Native script
  "aahe" → "आहे"
  "kya" → "क्या"

Problem 2: TRANSLATION
  Source language → Target language
  "mi ghari jato" → "I am going home"
  "kal meeting hai bro" → "उद्या मिटिंग आहे भाऊ"

Problem 3: CODE-SWITCH RESOLUTION
  Mixed-language input → Single-language output
  "bro kal office late jaunga, urgent kaam hai"
  → "Bro, I will be late to the office tomorrow, I have urgent work."
```

Traditional NMT (Neural Machine Translation) models fail here because they expect monolingual, properly-scripted input. Our users type **Romanized, code-switched, vowel-dropped, slang-heavy text**. This requires LLM-level contextual understanding.

---

## 2. Model Evaluation Matrix

### 2.1 Translation Models

| Model | Type | Role in Marlish.AI | Strengths | Weaknesses |
|-------|------|---------------------|-----------|------------|
| **NLLB-200 (Distilled 600M)** | Open-source (Meta) | **PRIMARY — In-browser via Transformers.js v4** | 200 language coverage. Quantized ONNX weights run in browser via WebGPU. Cached in IndexedDB after first load. $0 per-query cost. | ~150MB initial download (q4). Struggles with highly informal code-switched Romanized input. |
| **IndicTrans3** | Open-source (AI4Bharat) | **TIER 3 FALLBACK — Edge/server** | SOTA for 15+ Indic languages. Built on Gemma-3 architecture. Best cultural accuracy for Hindi/Marathi/English. Document-level and sentence-level. | Requires server compute. Expects Devanagari input — needs preprocessing for Roman. |
| **Gemma 3 (4B)** | Open-weight (Google) | **TIER 3 FALLBACK — Complex code-mixed** | 4B params, 140+ languages, excellent for Romanized Hinglish/Marlish parsing. Can run at the edge or locally. | ~2.5GB (q4). Too large for in-browser on most devices. |
| **Gemini 3.1 Flash-Lite** | Commercial API | **OPTIONAL — Pay-as-you-go backup** | 363 tok/s, $0.25/1M input. Best speed-to-cost if open-source models are insufficient. | Proprietary, vendor lock-in, recurring cost. |
| **GPT-4o-mini** | Commercial API | **OPTIONAL — Pay-as-you-go backup** | $0.15/1M input. Strong code-mixed understanding. | Vendor lock-in. |
| **Llama 4 8B** | Open-source (Meta) | **Phase 3 — Fine-tuning base** | Fine-tunable with LoRA. Strong general reasoning. | Requires GPU hosting. |
| **SeamlessM4T** | Open-source (Meta) | **Out of scope** | Multimodal (text + speech). | Overkill for text-only MVP. |

### 2.2 Transliteration Models

| Model | Type | Role in Marlish.AI | Accuracy | Size |
|-------|------|---------------------|----------|------|
| **Aksharamukha.js** | Rule-based, browser JS | **PRIMARY — Tier 1 instant transliteration** | Very high for standard text. Supports 100+ Indic scripts. 100% offline. | < 1MB |
| **Indic-Xlit** (AI4Bharat) | ML-based, Python/API | **TIER 3 — Server-side for ad-hoc spelling** | High for colloquially typed Roman text. Handles vowel-dropped input. | ~50MB |
| **RomanSetu** (AI4Bharat) | Open-source | Alternative to Indic-Xlit | High bidirectional accuracy | ~30MB |
| **Custom N-gram Trie** | Custom | Future: vowel-dropped Roman → candidates | Medium-High | < 5MB |

### 2.3 Language Identification (LID) Models

| Model | Source | Languages | Size | Use |
|-------|--------|-----------|------|-----|
| **L3Cube-MeLID** | L3Cube-Pune | Marathi-English token LID | ~10MB | Detect Marlish vs English tokens |
| **HingBERT** | L3Cube-Pune | Hindi-English code-mixed BERT | ~110MB | Hinglish understanding |
| **MeBERT** | L3Cube-Pune | Marathi-English code-mixed BERT | ~110MB | Marlish understanding |
| **fastText LID** | Meta | 170+ languages | ~1MB | Quick sentence-level detection |

---

## 3. Recommended Model Strategy (by Phase)

### Phase 1: MVP (Launch — Month 0-3)

```
┌──────────────────────────────────────────────────────────┐
│  STRATEGY: Open-Source Client-Side First                  │
│                                                          │
│  Tier 1:   Aksharamukha.js (transliteration, instant)    │
│  Tier 2:   NLLB-200 via Transformers.js v4 + WebGPU      │
│  Tier 3:   IndicTrans3 on Supabase Edge (fallback)       │
│                                                          │
│  Method:   In-browser inference for 80%+ of requests.    │
│            Edge fallback for complex code-mixed input     │
│            and devices without WebGPU.                    │
│                                                          │
│  Cost:     $0 — $5/month for 10,000 MAU                  │
│  Latency:  < 200ms (Tier 2), < 10ms (Tier 1)             │
│  Accuracy: 75-85% for common phrases (NLLB-200)          │
│            85-90% for Tier 3 (IndicTrans3)                │
│                                                          │
│  NO API keys needed for core flow. NO recurring costs.   │
│  Full offline capability after model download.            │
└──────────────────────────────────────────────────────────┘
```

### Phase 2: Crowdsourced Improvement (Month 3-9)

```
┌──────────────────────────────────────────────────────────┐
│  STRATEGY: Human-in-the-Loop Feedback                     │
│                                                          │
│  Addition: User correction UI                            │
│            - Thumbs up/down on translations               │
│            - "Suggest better translation" input            │
│            - All feedback stored in Supabase              │
│                                                          │
│  Data:     Accumulate 10,000+ verified pairs              │
│  Purpose:  Build proprietary training dataset             │
│  Model:    Still using NLLB-200 + IndicTrans3             │
│                                                          │
│  Prompts for Tier 3 improved weekly based on failure      │
│  patterns identified in user corrections.                 │
│                                                          │
│  Optional: Add Gemini Flash-Lite / GPT-4o-mini as         │
│  commercial Tier 3 alternative for better code-mixed      │
│  accuracy during data collection phase.                   │
└──────────────────────────────────────────────────────────┘
```

### Phase 3: Custom Fine-Tuned Model (Month 9+)

```
┌──────────────────────────────────────────────────────────┐
│  STRATEGY: LoRA Fine-Tuning + ONNX Export                 │
│                                                          │
│  Base:     Gemma 3 4B or Llama 4 8B                      │
│  Method:   LoRA (Low-Rank Adaptation) / QLoRA             │
│  Data:     10,000+ verified code-mixed pairs              │
│  Training: Modal / RunPod / Google Colab (free GPU)       │
│                                                          │
│  Result:   Fine-tuned model exported to ONNX → runs       │
│            in-browser via Transformers.js, replacing       │
│            NLLB-200 with domain-specific accuracy.         │
│            Proprietary model = competitive moat.           │
│                                                          │
│  Cost:     ~$50-200/month (training + occasional hosting) │
│  Latency:  < 100ms (optimized ONNX in browser)            │
│  Accuracy: 90-95% (domain-specific)                       │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Prompt Engineering Deep Dive

### 4.1 System Prompt Design Principles

Each prompt follows a strict template:

```
1. PERSONA:     Define the AI as a computational linguist
2. TASK:        Explicit translation direction (source → target)
3. RULES:       Hard constraints (output only, no explanations)
4. EXAMPLES:    5-10 curated few-shot pairs
5. DELIMITERS:  User input wrapped in """ for injection defense
6. EDGE CASES:  Handle ambiguity, slang, vowel drops
```

### 4.2 Complete Prompt Library

#### Prompt 1: Hinglish → English

```
SYSTEM: You are an expert computational linguist specializing in Indian 
digital communication. Translate code-mixed "Hinglish" input (Hindi + 
English typed in Roman/Latin script) into natural, grammatically correct 
English.

RULES:
1. Output ONLY the translated English text. No explanations, notes, or 
   formatting.
2. Identify the Matrix Language (Hindi grammar with English embeddings).
3. Resolve phonetic ambiguity contextually ("kal" = yesterday/tomorrow 
   based on verb tense).
4. Map slang and idioms to natural English equivalents.
5. Preserve tone: formal input → formal output, casual → casual.

EXAMPLES:
INPUT: """kal meeting hai bro"""
OUTPUT: We have a meeting tomorrow, bro.

INPUT: """kya kar raha hai tu?"""
OUTPUT: What are you doing?

INPUT: """kal office late jaunga, urgent kaam hai"""
OUTPUT: I'll be late to office tomorrow, I have urgent work.

INPUT: """yaar ye bohot mushkil hai"""
OUTPUT: Dude, this is really difficult.

INPUT: """mujhe lagta hai ye sahi nahi hai"""
OUTPUT: I think this isn't right.
```

#### Prompt 2: Hinglish → Marathi

```
SYSTEM: You are an expert computational linguist. Translate code-mixed 
"Hinglish" input (Hindi + English in Roman script) into formal, native 
Devanagari Marathi.

RULES:
1. Output ONLY the translated Marathi text in Devanagari script. No 
   explanations or transliterations.
2. Map Hindi vocabulary to Marathi equivalents (not transliterated Hindi).
3. Use proper Marathi grammar and verb conjugations.
4. Preserve the casual/formal register of the input.

EXAMPLES:
INPUT: """kal meeting hai bro"""
OUTPUT: उद्या मीटिंग आहे भाऊ

INPUT: """mujhe bohot bhook lagi hai"""
OUTPUT: मला खूप भूक लागली आहे

INPUT: """ye kaam kab tak hoga?"""
OUTPUT: हे काम कधीपर्यंत होईल?

INPUT: """bhai, samjha karo thoda"""
OUTPUT: भाऊ, थोडं समजून घ्या

INPUT: """party mein aana hai kya?"""
OUTPUT: पार्टीला यायचं आहे का?
```

#### Prompt 3: English → Marathi

```
SYSTEM: You are a professional English-to-Marathi translator. Translate 
the given English text into natural, fluent Marathi in Devanagari script.

RULES:
1. Output ONLY the Marathi translation in Devanagari. No explanations.
2. Use natural Marathi phrasing, not literal word-for-word translation.
3. Preserve the tone and formality level of the input.
4. For technical terms with no Marathi equivalent, use the English word 
   in Devanagari transliteration.

EXAMPLES:
INPUT: """What are the plans for tomorrow?"""
OUTPUT: उद्याचे काय प्लॅन आहेत?

INPUT: """I will be arriving late to the office tomorrow."""
OUTPUT: मी उद्या ऑफिसला उशिरा येईन.

INPUT: """This situation is very difficult."""
OUTPUT: ही परिस्थिती खूप कठीण आहे.

INPUT: """Can you help me with this project?"""
OUTPUT: तुम्ही मला या प्रोजेक्टमध्ये मदत करू शकता का?

INPUT: """The weather is really nice today."""
OUTPUT: आज हवामान खरंच छान आहे.
```

#### Prompt 4: Marlish → English

```
SYSTEM: You are an expert translator. Convert "Marlish" text (Marathi 
typed in English/Roman letters) into natural, grammatically correct 
English.

RULES:
1. Output ONLY the final English translation. No Devanagari, no notes.
2. Understand that users may omit vowels or use phonetic spelling 
   (e.g., "mzh nv" = "majha nav" = "my name").
3. Resolve Marathi-specific grammar (e.g., post-positions, verb endings).
4. Handle common Marathi slang and informal expressions.

EXAMPLES:
INPUT: """mi ghari jato"""
OUTPUT: I am going home.

INPUT: """tu kuthe ahes?"""
OUTPUT: Where are you?

INPUT: """mala khup bhuk lagli aahe"""
OUTPUT: I am very hungry.

INPUT: """udya office la yeu shakat nahi"""
OUTPUT: I cannot come to the office tomorrow.

INPUT: """he kaam kadhi honar?"""
OUTPUT: When will this work be done?
```

#### Prompt 5: Marlish → Hindi

```
SYSTEM: You are an expert translator. Convert "Marlish" text (Marathi 
typed in English/Roman letters) into natural Hindi in Devanagari script.

RULES:
1. Output ONLY the Hindi translation in Devanagari. No explanations.
2. Handle phonetic Romanized Marathi input with spelling variations.
3. Map Marathi vocabulary and grammar to Hindi equivalents properly.
4. Preserve casual/formal register.

EXAMPLES:
INPUT: """mi ghari jato"""
OUTPUT: मैं घर जा रहा हूँ।

INPUT: """tu kuthe ahes?"""
OUTPUT: तुम कहाँ हो?

INPUT: """mala khup bhuk lagli aahe"""
OUTPUT: मुझे बहुत भूख लगी है।

INPUT: """udya office la yaycha aahe"""
OUTPUT: कल ऑफिस आना है।

INPUT: """ha vishay khup kathin aahe"""
OUTPUT: यह विषय बहुत कठिन है।
```

---

## 5. Handling the Hardest Problem: Romanized Ambiguity

### 5.1 Ambiguity Categories

| Category | Example | Challenge |
|----------|---------|-----------|
| **Cross-lingual homophones** | "mai" = Hindi "I" (मैं), Marathi "mother" (माई), English "my" | Same string, 3 different meanings |
| **Temporal polysemy** | "kal" = "yesterday" or "tomorrow" (Hindi) | Requires verb tense analysis |
| **Vowel omission** | "mzh nv" = "majha nav" = "my name" | Extreme abbreviation |
| **Spelling variation** | "aahe" / "ahe" / "aahey" = same Marathi word | No standardized Roman spelling |
| **Script collision** | "me" = English pronoun OR Hindi postposition "में" | Context-dependent |

### 5.2 Resolution Strategy

```
Step 1: SENTENCE-LEVEL ANALYSIS (not token-level)
  └── Feed the ENTIRE sentence to the LLM, not individual words
  └── Transformer attention mechanism resolves ambiguity from context

Step 2: LANGUAGE PAIR CONTEXT
  └── User has already selected source→target pair
  └── This eliminates Hindi vs Marathi ambiguity for "mai"

Step 3: FEW-SHOT PRIMING
  └── System prompt examples demonstrate correct disambiguation
  └── LLM learns pattern: "mai udya yein" → "I" not "mother"

Step 4: OUTPUT VALIDATION
  └── If output length > 3x input length → suspect prompt injection
  └── If output contains code/markdown → reject and retry

Step 5: MINIMUM INPUT THRESHOLD
  └── < 3 characters → don't call LLM (too ambiguous)
  └── Show placeholder: "Keep typing for translation..."
```

---

## 6. Available Training Datasets

For Phase 2-3 when building custom models:

| Dataset | Source | Size | Content |
|---------|--------|------|---------|
| **L3Cube-HingCorpus** | L3Cube-Pune | 52.93M sentences | Hindi-English code-mixed Twitter data (Roman script) |
| **L3Cube-MeCorpus** | L3Cube-Pune | 10M sentences | Marathi-English code-mixed social media |
| **L3Cube-MeSent** | L3Cube-Pune | Annotated subset | Sentiment-annotated Marathi-English |
| **BPCC** | AI4Bharat | 230M bitext pairs | 22 Indic languages parallel corpus |
| **IndicXlit training data** | AI4Bharat | Varies | Roman↔Devanagari transliteration pairs |
| **User corrections** (proprietary) | Marlish.AI users | 0 → 10K+ | Real-world code-mixed corrections (Phase 2) |

---

## 7. Cost Analysis: Model Comparison

### Per-Translation Cost (assuming 40 input + 40 output tokens average)

| Model | Execution | Cost per Translation | Cost per 1K Translations |
|-------|-----------|---------------------|-------------------------|
| **NLLB-200 (Transformers.js)** | Client-side (browser) | $0.000000 | **$0.00 (FREE)** |
| **Aksharamukha.js** | Client-side (browser) | $0.000000 | **$0.00 (FREE)** |
| **IndicTrans3 (Supabase Edge)** | Server-side (free tier) | $0.000000* | **$0.00*** |
| **Gemma 3 4B (Modal)** | Server-side GPU | ~$0.001000 | **$1.00** |
| **Gemini 3.1 Flash-Lite** | Commercial API | $0.000070 | **$0.07** |
| **GPT-4o-mini** | Commercial API | $0.000030 | **$0.03** |

*Within Supabase/HuggingFace free tier limits.

**Winner for MVP:** NLLB-200 in-browser at **$0.00 per translation** is unbeatable. IndicTrans3 on free-tier edge functions handles the remaining 20% at zero cost.

### Monthly Cost Projections (Open-Source Stack)

| DAU | Translations/day | Client-Side (80%) | Edge Fallback (20%) | Total Monthly Cost |
|-----|------------------|--------------------|--------------------|-----------------|
| 100 | 2,000 | **$0** | **$0** (free tier) | **$0** |
| 1,000 | 20,000 | **$0** | **$0** (free tier) | **$0 — $1** |
| 10,000 | 200,000 | **$0** | **~$5** (Supabase Pro) | **$5 — $10** |
| 100,000 | 2,000,000 | **$0** | **~$30** (compute) | **$30 — $50** |

---

## 8. Model Evaluation Criteria

When testing and comparing models during development, use these benchmarks:

### Test Cases (run against each model)

```
# Hinglish → English
1. "kal meeting hai bro" → "We have a meeting tomorrow, bro."
2. "mujhe lagta hai ye sahi nahi hai" → "I think this isn't right."
3. "yaar party mein bohot maza aaya" → "Dude, the party was so much fun."
4. "kya scene hai aaj?" → "What's the plan today?"
5. "bhai samjha karo" → "Bro, try to understand."

# Marlish → English
6. "mi ghari jato" → "I am going home."
7. "tu kuthe ahes bro?" → "Where are you, bro?"
8. "mala khup bhuk lagli" → "I am very hungry."
9. "he kaam kadhi honar?" → "When will this work be done?"
10. "aaj office la jaycha nahi" → "I don't want to go to office today."

# Edge Cases
11. "mai" (in Hindi context) → "I"
12. "mai" (in Marathi context) → "mother"  
13. "kal" (past context: "kal gaya tha") → "yesterday"
14. "kal" (future context: "kal jaunga") → "tomorrow"
15. "mzh nv XYZ aahe" → "My name is XYZ."
```

### Scoring Rubric

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Semantic Accuracy** | 40% | Does the translation preserve the original meaning? |
| **Grammatical Correctness** | 20% | Is the output grammatically proper in the target language? |
| **Tone Preservation** | 15% | Does casual input yield casual output (and vice versa)? |
| **Ambiguity Resolution** | 15% | Does the model correctly resolve "kal", "mai", etc.? |
| **Latency (TTFT)** | 10% | Time to first token in streaming mode |

---

## 9. Future ML Roadmap

```
Now ────────────────────────────────────────────────────────── Future

[MVP]               [Crowdsource]           [Fine-Tune]        [Multimodal]
│                   │                       │                  │
├─ NLLB-200 in      ├─ User corrections     ├─ LoRA on         ├─ Voice input
│  browser (free)   │  (thumbs up/down)     │  Gemma3/Llama4   │  (Whisper)
│                   │                       │                  │
├─ Aksharamukha     ├─ Accumulate 10K+      ├─ ONNX export     ├─ Voice output
│  transliteration  │  verified pairs       │  for browser     │  (TTS APIs)
│                   │                       │                  │
├─ IndicTrans3      ├─ Improve Tier 3       ├─ Replace NLLB    ├─ Camera OCR
│  edge fallback    │  prompts weekly       │  with custom     │  translation
│                   │                       │                  │
└─ $0/mo            └─ $0-5/mo + Supabase   └─ ~$50-200/mo     └─ Custom pricing
```
