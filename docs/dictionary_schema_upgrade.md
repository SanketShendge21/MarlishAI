# Dictionary Schema & Engine Upgrade (v6.0)

To achieve the contextual intelligence requested without destroying the offline-first performance constraints (<50ms latency), the dictionary and engine architecture was upgraded.

Instead of bloating the `dictionary.json` file with millions of duplicate context permutations, we kept the O(1) hash map for base words and introduced **Contextual NLP Overlays** in the application code.

## 1. The Problem with the V1 Dictionary
The original JSON schema stored ambiguous words with slash-separated meanings:
```json
{
  "kal": "tomorrow/yesterday",
  "bro": "bro/brother",
  "acha": "okay/good/really"
}
```
This forced the translation layer to dump "tomorrow/yesterday" into the sentence, ruining the natural flow.

## 2. The Contextual NLP Upgrade

We introduced `lib/contextual-disambiguation.js`, which acts as an in-memory rule engine that sits on top of the base dictionary.

### The New Data Structure (In-Memory)
Instead of a flat JSON string, ambiguous words are now mapped to a confidence-based scoring model:

```javascript
const AMBIGUOUS_WORDS = {
  kal: {
    meanings: [
      {
        value: 'tomorrow',
        score: 0.55, 
        signals: {
          boost: ['milte', 'milenge', 'plan', 'hoga', 'meeting', 'aana'],
          inhibit: ['gaya', 'tha', 'aaya', 'kiya', 'bola', 'mila']
        }
      },
      {
        value: 'yesterday',
        score: 0.45,
        signals: {
          boost: ['gaya', 'tha', 'aaya', 'kiya', 'bola', 'mila'],
          inhibit: ['milte', 'plan', 'hoga', 'jayenge']
        }
      }
    ]
  }
}
```

### How It Works
When the engine encounters an ambiguous word (e.g., `kal`), it:
1. Opens a **context window** of ±3 tokens.
2. Evaluates the neighboring tokens against the `boost` and `inhibit` arrays.
3. Automatically maps tense helpers (e.g. `tha`, `gaya`) to the past meaning.
4. Returns the single highest-confidence string.

## 3. Phrase Intent & Compound Verb Dictionary

Instead of just word-to-word mappings, the engine now contains a massive library of **Intent Templates** and **Compound Verbs** inside `lib/phrase-intent-rules.js`.

### Compound Verbs
Hindi/Marathi use multi-word verbs that break literal translation. We now map them as atomic units:
```javascript
{
  "kar raha hai": "is doing",
  "ja raha hu": "am going",
  "ho gaya": "it's done"
}
```

### Intent Matching
For idioms and chat phrases, the `phrase-intent-rules.js` dictionary matches full sentences *while stripping dynamic vocatives* (like "bro"):
```javascript
{
  "scene kya hai": "What's the plan?",
  "kya chal raha hai": "What's going on?",
  "tu kuthe ahes": "Where are you?"
}
```

By decoupling the *contextual logic* from the *static dictionary JSON*, the app maintains a tiny 1.2MB payload while achieving deep NLP intelligence without relying on a slow Python backend or external API.
