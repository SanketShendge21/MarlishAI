# 🌐 Marlish.AI

**Marlish.AI** is an AI that understands how Indians actually chat online. It is a blazing-fast, offline-first chat language engine designed specifically to decode messy Hinglish and Marlish into clear, meaningful language.

Turn messy Hinglish & Marlish into clear, natural language — instantly. Powered by a custom 8-layer NLP pipeline, it interprets chat-style inputs into standard English, Hindi, and Marathi in real-time—all while remaining entirely private and functional without an internet connection.

---

## ✨ Key Features

- **🚀 Real-Time Interpretation:** Instant results as you type with adaptive debouncing.
- **offline-first:** No cloud APIs. No latency. No data tracking. Everything happens on your device.
- **🧩 8-Layer NLP Engine:** Goes beyond word-by-word mapping to understand context, intent, and grammar.
- **🔄 Bidirectional Support:** Handles complex pairs like Hinglish → English, Marlish → Marathi, and more.
- **📱 PWA Ready:** Install it on your mobile device for a native-app feel.
- **🎨 Premium UI:** Modern, responsive design with Dark Mode support and visual confidence scoring.

---

## 🧠 The 8-Layer Translation Pipeline

Traditional translation systems fail at "Hinglish" because they treat it like a simple code-switch. Marlish.AI uses a sophisticated multi-stage pipeline:

1.  **L1: Normalization** – Standardizes typos (e.g., `kr` ➔ `kar`) and collapses repeated characters.
2.  **L2: Intent Matching** – Identifies full-sentence idiomatic patterns (e.g., `kya scene hai` ➔ `What's the plan?`).
3.  **L3: Compound Verb Assembly** – Combines fragments like `ja raha hu` into single semantic units (`am going`).
4.  **L4: Contextual Disambiguation** – Uses surrounding words to pick meanings (e.g., `kal` as `tomorrow` vs `yesterday`).
5.  **L5: Grammar Reordering** – Converts Subject-Object-Verb (SOV) structure to Subject-Verb-Object (SVO).
6.  **L6: Vocative Handling** – Intelligently places commas for slang and names (e.g., `bro kidhar hai` ➔ `Bro, where are you?`).
7.  **L7: Confidence Scoring** – Real-time feedback on how accurate the engine feels the interpretation is.
8.  **L8: Beautification** – Final pass for capitalization, punctuation, and spacing.

---

## 🛠️ Tech Stack

- **Framework:** [Next.js 16](https://nextjs.org/)
- **UI Logic:** React 19
- **Styling:** Tailwind CSS v4
- **Engine:** Custom JavaScript Rule-Based NLP
- **State:** Local-First (JSON Dictionary based)

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18.x or higher
- npm / yarn / pnpm

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SanketShendge21/Marlish.ai.git
    cd Marlish.ai
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Build the dictionary:**
    The engine relies on a compiled JSON dictionary. Generate it by running:
    ```bash
    npm run build-dict
    ```

4.  **Run the development server:**
    ```bash
    npm run dev
    ```

Open [http://localhost:3000](http://localhost:3000) to see the app in action!

---

## 🧪 Testing the Engine

You can run the standalone NLP engine test suite to verify interpretation accuracy:
```bash
node tests/test-engine.js
```

---

## 📦 Legacy: mT5 Scratch Training (Pre-Pivot)

The `legacy/` folder and the `pre-pivot-mt5-training` git branch preserve the
original mT5-small fine-tuning attempt. Training on 18.4M pairs yielded BLEU ~3,
establishing that scratch training on this noisy dataset is not a viable path.
This diagnostic work directly informed the pivot to the IndicXlit + opus-mt
architecture documented in `docs/ARCHITECTURE_ANALYSIS_AND_PLAN.md`.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for the Indian Multilingual Community.*
