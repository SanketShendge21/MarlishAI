# 🌐 Marlish.AI

**Marlish.AI** is an AI-powered translation engine built for Indian chat languages. It translates Marlish (romanized Marathi), Hinglish (romanized Hindi), pure Marathi, pure Hindi, and English — in all directions.

Unlike generic translators, Marlish.AI understands how Indians actually type in chat — handling romanized scripts, colloquial phrases, and code-mixed text that Google Translate fails on.

---

## ✨ Key Features

- **🔄 10 Language Directions:** Marathi, Hindi, Marlish, Hinglish ↔ English (all pairs)
- **🤖 NLLB-200-1.3B:** Meta's 200-language neural translation model
- **✍️ Smart Transliteration:** Custom 3-tier pipeline converts romanized chat to proper Devanagari
- **📝 Grammar Correction:** Gemini 2.5-flash-lite polishes English output (free tier API)
- **⚡ Real-Time UI:** Adaptive debounced translation as you type
- **🎨 Premium UI:** Modern dark-mode design with glassmorphism

---

## 🏗️ Architecture

```
┌─────────────────────────────┐
│     Next.js Frontend        │ ← Vercel (free)
│     (React 19, Tailwind 4)  │
└──────────┬──────────────────┘
           │ POST /translate
           ▼
┌─────────────────────────────┐
│     FastAPI Backend         │ ← HF Spaces (free)
│                             │
│  ┌───────────────────────┐  │
│  │  Transliteration      │  │  Romanized → Devanagari
│  │  Pipeline (3-tier)    │  │  (IndicXlit → Seed Map → Phoneme Rules)
│  └───────────┬───────────┘  │
│              ▼              │
│  ┌───────────────────────┐  │
│  │  NLLB-200-1.3B        │  │  Neural Machine Translation
│  │  (Meta)               │  │  200 languages, 1.3B params
│  └───────────┬───────────┘  │
│              ▼              │
│  ┌───────────────────────┐  │
│  │  Gemini GEC           │  │  Grammar + fluency polish
│  │  (optional)           │  │  (English output only)
│  └───────────────────────┘  │
└─────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS v4 |
| **API** | FastAPI, Uvicorn |
| **Translation** | NLLB-200-1.3B (Meta), PyTorch |
| **Transliteration** | Custom pipeline (400+ word seed map + phoneme rules) |
| **GEC** | Gemini 2.5-flash-lite (free tier) |
| **Hosting** | Vercel (frontend), HF Spaces Docker (API) |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ (frontend)
- **Python** 3.11+ (API backend)
- **GPU** recommended (RTX 4050 or similar) for fast inference; CPU works but slower

### Frontend Setup

```bash
git clone https://github.com/SanketShendge21/MarlishAI.git
cd MarlishAI
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### API Backend Setup

```bash
# Create Python virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install PyTorch (GPU — adjust for your CUDA version)
pip install torch --index-url https://download.pytorch.org/whl/cu124

# Install API dependencies
pip install -r requirements-api.txt

# Set Gemini API key (optional, for GEC)
# Create .local.env with: Marlish_Gemini_API_Key=your_key_here

# Start the API server
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

The model downloads automatically on first start (~2.5GB).

---

## 🧪 Testing

### Translation Quality Test (104 segments, all 8 directions)
```bash
python scripts/test_carnival_tours.py
```

Results written to `docs/test-results/CARNIVAL_TEST_RESULTS.md`

### Current Quality (June 2026)

| Direction | Score |
|-----------|-------|
| Hindi → English | 12/13 |
| English → Hindi | 13/13 |
| Marathi → English | 11/13 |
| English → Marathi | 12/13 |
| Marlish → English | 11/13 |
| Hinglish → English | 11/13 |
| English → Marlish | 10/13 |
| English → Hinglish | 10/13 |

---

## 📁 Project Structure

```
MarlishAI/
├── app/                          # Next.js frontend
│   ├── components/
│   │   ├── translator/           # TranslatorPanel, InputArea, OutputArea
│   │   ├── actions/              # ActionBar (history, copy, share)
│   │   └── ui/                   # Header, Footer, OfflineIndicator
│   ├── page.js                   # Main page
│   └── layout.js                 # Root layout
├── api/
│   └── app.py                    # FastAPI translation API
├── scripts/
│   ├── transliterator/           # Transliteration pipeline
│   │   ├── pipeline.py           # 3-tier orchestrator
│   │   ├── phoneme_rules.py      # Character-level rules (Tier 3)
│   │   ├── fallback_map.py       # 400+ word seed map (Tier 2)
│   │   ├── reverse_transliterate.py  # Devanagari → romanized
│   │   └── token_classifier.py   # English vs Marlish detection
│   ├── test_carnival_tours.py    # 104-segment quality test
│   └── test_translation_quality.py
├── hooks/
│   └── useTranslation.js         # React hook → API calls
├── docs/                         # Project documentation
│   ├── test-results/             # Test output files
│   └── progress_tracker.md       # Development roadmap
├── Dockerfile                    # HF Spaces deployment
├── requirements-api.txt          # Python API deps
├── vercel.json                   # Vercel frontend config
└── package.json                  # Node.js deps
```

---

## 🌍 Supported Languages

| Language | Code | Input Example | Direction |
|----------|------|---------------|-----------|
| **English** | `english` | "How are you?" | ↔ all |
| **Marathi** | `marathi` | "तू कसा आहेस?" | ↔ English |
| **Hindi** | `hindi` | "तुम कैसे हो?" | ↔ English |
| **Marlish** | `marlish` | "tu kasa ahes?" | ↔ English |
| **Hinglish** | `hinglish` | "tum kaise ho?" | ↔ English |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ for the Indian multilingual community.*
