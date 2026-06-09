"""
Comprehensive translation quality test — realistic everyday messages.
Writes results to a UTF-8 file for proper rendering.
"""
import requests
import json
import time

API = "http://localhost:8000/translate"
OUTPUT_FILE = "docs/test-results/TRANSLATION_TEST_RESULTS.md"

# ─────────────────────────────────────────────────────────
# Test cases: (source_lang, target_lang, input_text, expected_meaning)
# ─────────────────────────────────────────────────────────
TESTS = [
    # ── Marlish → English (everyday chat) ──
    ("marlish", "english", "Aaj office madhe khup kaam hota, ekdum thaklo mi",
     "There was a lot of work in the office today, I'm very tired"),
    ("marlish", "english", "Udya amhi picnic la janar aahot, tu yeshil ka?",
     "We are going for a picnic tomorrow, will you come?"),
    ("marlish", "english", "Mala ek coffee de, khup thandi ahe baher",
     "Give me a coffee, it's very cold outside"),
    ("marlish", "english", "Tuza phone ka lagat nahi? Mi tula 10 vela call kela",
     "Why isn't your phone connecting? I called you 10 times"),
    ("marlish", "english", "Jevayला काय बनवलं आज? mala bhuk lagli ahe",
     "What did you cook for lunch today? I'm hungry"),
    ("marlish", "english", "Bhai paisa de, mala urgent lagto",
     "Bro give me money, I need it urgently"),
    ("marlish", "english", "Mi exam pass zalo, khup khush ahe",
     "I passed the exam, I'm very happy"),
    ("marlish", "english", "Ghari ye lavkar, aai vaat baghte ahe",
     "Come home early, mom is waiting"),

    # ── Hinglish → English (everyday chat) ──
    ("hinglish", "english", "Bhai aaj mera mood off hai, kuch mat bol",
     "Bro my mood is off today, don't say anything"),
    ("hinglish", "english", "Kal exam hai aur maine kuch nahi padha",
     "There's an exam tomorrow and I haven't studied anything"),
    ("hinglish", "english", "Yaar wo movie dekhne chalte hain weekend pe",
     "Dude let's go watch that movie on the weekend"),
    ("hinglish", "english", "Mummy ne poha banaya hai, tu aa ja ghar pe",
     "Mom made poha, come over to my house"),
    ("hinglish", "english", "Bhai tera phone kidhar hai? Call nahi lag raha",
     "Bro where is your phone? The call isn't going through"),
    ("hinglish", "english", "College mein aaj bahut boring tha, koi nahi aaya",
     "College was very boring today, nobody came"),

    # ── English → Marlish ──
    ("english", "marlish", "I will come to your house tomorrow evening",
     "Mi udya sandhyakali tuzhya ghari yein"),
    ("english", "marlish", "What time does the train leave?",
     "Train kadhi sutte?"),
    ("english", "marlish", "Please send me the photos from yesterday",
     "Mala kalche photos pathav"),

    # ── English → Hinglish ──
    ("english", "hinglish", "I will come to your house tomorrow evening",
     "Main kal shaam ko tere ghar aaunga"),
    ("english", "hinglish", "The food was really delicious",
     "Khana bahut tasty tha"),

    # ── Marathi (Devanagari) → English ──
    ("marathi", "english", "मला आज ऑफिसला जायचं नाही, खूप थकवा आलाय",
     "I don't want to go to the office today, I'm very tired"),
    ("marathi", "english", "तुझा भाऊ काय करतो? तो कुठे राहतो?",
     "What does your brother do? Where does he live?"),

    # ── Hindi (Devanagari) → English ──
    ("hindi", "english", "मुझे आज बहुत नींद आ रही है, रात को सो नहीं पाया",
     "I'm very sleepy today, I couldn't sleep last night"),
    ("hindi", "english", "क्या तुम कल मेरे साथ बाजार चलोगे?",
     "Will you come to the market with me tomorrow?"),
]


def run_tests():
    results = []
    total = len(TESTS)
    passed = 0

    print(f"Running {total} translation tests...")
    print("=" * 60)

    for i, (src, tgt, text, expected) in enumerate(TESTS, 1):
        try:
            resp = requests.post(API, json={
                "text": text,
                "source": src,
                "target": tgt,
            }, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            translation = data.get("translation", "")
            devanagari = data.get("devanagari", "")
            latency = data.get("latency_ms", 0)

            # Simple quality check: is the translation non-empty and different from input?
            ok = bool(translation) and translation.strip() != text.strip()
            if ok:
                passed += 1

            results.append({
                "num": i,
                "src": src,
                "tgt": tgt,
                "input": text,
                "expected": expected,
                "got": translation,
                "devanagari": devanagari,
                "latency": latency,
                "ok": ok,
            })
            print(f"  [{i}/{total}] {src}→{tgt}: {'✓' if ok else '✗'} ({latency:.0f}ms)")

        except Exception as e:
            results.append({
                "num": i, "src": src, "tgt": tgt,
                "input": text, "expected": expected,
                "got": f"ERROR: {e}", "devanagari": "",
                "latency": 0, "ok": False,
            })
            print(f"  [{i}/{total}] {src}→{tgt}: ERROR - {e}")

    # Write results to markdown file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Translation Quality Test Results\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Model:** NLLB-200 (check /health for exact variant)\n")
        f.write(f"**Tests:** {passed}/{total} produced output\n\n")
        f.write("---\n\n")

        # Group by direction
        directions = {}
        for r in results:
            key = f"{r['src']} → {r['tgt']}"
            directions.setdefault(key, []).append(r)

        for direction, tests in directions.items():
            f.write(f"## {direction}\n\n")
            for r in tests:
                status = "✅" if r["ok"] else "❌"
                f.write(f"### Test {r['num']} {status}\n")
                f.write(f"- **Input:** `{r['input']}`\n")
                if r["devanagari"]:
                    f.write(f"- **Devanagari:** {r['devanagari']}\n")
                f.write(f"- **Got:** {r['got']}\n")
                f.write(f"- **Expected:** {r['expected']}\n")
                f.write(f"- **Latency:** {r['latency']:.0f}ms\n\n")

        f.write("---\n\n")
        f.write("## Summary\n\n")
        f.write(f"- {passed}/{total} tests produced non-empty translations\n")
        f.write("- Review each result above to assess semantic accuracy\n")

    print("=" * 60)
    print(f"Results: {passed}/{total} passed")
    print(f"Written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_tests()
