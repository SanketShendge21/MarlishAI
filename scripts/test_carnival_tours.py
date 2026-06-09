"""
Real-world translation test: Carnival Tours itinerary
Tests ALL language directions supported by Marlish.AI:
  - Marathi → English
  - Marlish → English
  - Hindi → English
  - Hinglish → English
  - English → Marathi
  - English → Marlish
  - English → Hindi
  - English → Hinglish

Results written to docs/CARNIVAL_TEST_RESULTS.md
"""

import sys
import os
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8000"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "test-results", "CARNIVAL_TEST_RESULTS.md")


def translate(text: str, source: str, target: str) -> dict:
    """Call the translation API."""
    resp = requests.post(f"{API_URL}/translate", json={
        "text": text, "source": source, "target": target
    }, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ═══════════════════════════════════════════════════════════
# MARATHI (Pure Devanagari)
# ═══════════════════════════════════════════════════════════
MARATHI_SEGMENTS = [
    "कार्निवल टूर्स आयोजित कन्याकुमारी रामेश्वर मदुराई त्रिवेंद्रम",
    "समाविष्ट - त्रिवेंद्रम, कन्याकुमारी, रामेश्वरम्, मदुराई.",
    "8 रात्री, 9 दिवस",
    "रु 17500/- नॉन एसी रेल्वे",
    "रु 20500/- एसी रेल्वे",
    "सहल दिनांक: 18 ऑगस्ट, 27 सप्टेंबर, 18 नोव्हेंबर, 04 डिसेंबर, 30 डिसेंबर",
    "दिवस 1: पुणे ते त्रिवेंद्रम",
    "दिवस 3: त्रिवेंद्रम पोच व स्थानिक स्थलदर्शन करून मुक्काम. स्थलदर्शन: अझीमाला शिव मंदिर, पद्मनाभ मंदिर, केरळ बिच.",
    "दिवस 4: कन्याकुमारी स्थानिक स्थळ दर्शन व मुक्काम कन्याकुमारी. स्थलदर्शन: सुचींद्रम मंदिर, कन्याकुमारी देवी मंदिर, विवेकानंद रॉक, गांधी मंडपम.",
    "जाता-येता रेल्वे स्लीपर क्लास प्रवास, शहरांतर्गत बस प्रवास, चहा, नाष्टा, 2 वेळ जेवण",
    "शुद्ध शाकाहारी जेवण. रेल्वेतील जेवण वैयक्तिक.",
    "डिलक्स हॉटेल व्यवस्था एका रूम मध्ये 3/4 व्यक्ति.",
    "वैयक्तिक रूम पाहिजे असल्यास 5000/- अधिक द्यावे लागतील",
]

# ═══════════════════════════════════════════════════════════
# MARLISH (Romanized Marathi)
# ═══════════════════════════════════════════════════════════
MARLISH_SEGMENTS = [
    "Carnival tours ayojit kanyakumari rameshwar madurai trivandrum",
    "Samavishta - trivandrum, kanyakumari, rameshwaram, madurai.",
    "8 ratri, 9 divas",
    "Rs 17500 non AC railway",
    "Rs 20500 AC railway",
    "Sahal dinank: 18 August, 27 September, 18 November, 04 December, 30 December",
    "Divas 1: Pune te trivandrum",
    "Divas 3: trivandrum poch va sthanik sthaldarshan karun mukkam.",
    "Divas 4: kanyakumari sthanik sthal darshan. va mukkam kanyakumari.",
    "Jata-yeta railway sleeper class pravas, shaharantar bus pravas, chaha, nashta, 2 vel jevan",
    "Shuddha shakahari jevan. Railwetil jevan vaiyaktik.",
    "Deluxe hotel vyavastha eka room madhye 3/4 vyakti.",
    "Vaiyaktik room pahije asalyaas 5000 adhik dyave lagtil",
]

# ═══════════════════════════════════════════════════════════
# HINDI (Pure Devanagari)
# ═══════════════════════════════════════════════════════════
HINDI_SEGMENTS = [
    "कार्निवल टूर्स द्वारा आयोजित कन्याकुमारी रामेश्वरम् मदुरई त्रिवेन्द्रम यात्रा",
    "शामिल - त्रिवेन्द्रम, कन्याकुमारी, रामेश्वरम्, मदुरई.",
    "8 रातें, 9 दिन",
    "रु 17500/- नॉन एसी रेलवे",
    "रु 20500/- एसी रेलवे",
    "यात्रा तारीखें: 18 अगस्त, 27 सितंबर, 18 नवंबर, 04 दिसंबर, 30 दिसंबर",
    "दिन 1: पुणे से त्रिवेन्द्रम",
    "दिन 3: त्रिवेन्द्रम पहुँचना और स्थानीय दर्शन करके ठहराव. दर्शन: अझीमाला शिव मंदिर, पद्मनाभ मंदिर, केरल बीच.",
    "दिन 4: कन्याकुमारी स्थानीय दर्शन और ठहराव. दर्शन: सुचींद्रम मंदिर, कन्याकुमारी देवी मंदिर, विवेकानंद रॉक, गांधी मंडपम.",
    "आने-जाने में रेलवे स्लीपर क्लास यात्रा, शहर के अंदर बस यात्रा, चाय, नाश्ता, 2 बार खाना",
    "शुद्ध शाकाहारी भोजन. रेलवे में भोजन व्यक्तिगत.",
    "डीलक्स होटल व्यवस्था एक कमरे में 3/4 व्यक्ति.",
    "व्यक्तिगत कमरा चाहिए तो 5000/- अतिरिक्त देने होंगे",
]

# ═══════════════════════════════════════════════════════════
# HINGLISH (Romanized Hindi)
# ═══════════════════════════════════════════════════════════
HINGLISH_SEGMENTS = [
    "Carnival tours dwara ayojit kanyakumari rameshwaram madurai trivandrum yatra",
    "Shamil - trivandrum, kanyakumari, rameshwaram, madurai.",
    "8 raatein, 9 din",
    "Rs 17500 non AC railway",
    "Rs 20500 AC railway",
    "Yatra tarikhen: 18 August, 27 September, 18 November, 04 December, 30 December",
    "Din 1: Pune se trivandrum",
    "Din 3: trivandrum pahunchna aur sthaniya darshan karke thehra. Darshan: Azhimala Shiv mandir, Padmanabh mandir, Kerala beach.",
    "Din 4: kanyakumari sthaniya darshan aur thehra kanyakumari. Darshan: Suchindram mandir, kanyakumari devi mandir, Vivekanand rock, Gandhi mandapam.",
    "Aane jaane mein railway sleeper class yatra, shahar ke andar bus yatra, chai, nashta, 2 baar khana",
    "Shuddh shakahari bhojan. Railway mein bhojan vyaktigat.",
    "Deluxe hotel vyavastha ek kamre mein 3/4 vyakti.",
    "Vyaktigat kamra chahiye toh 5000 extra dene honge",
]

# ═══════════════════════════════════════════════════════════
# ENGLISH (for reverse translations)
# ═══════════════════════════════════════════════════════════
ENGLISH_SEGMENTS = [
    "Carnival Tours organized trip to Kanyakumari, Rameshwar, Madurai, Trivandrum",
    "Includes - Trivandrum, Kanyakumari, Rameshwaram, Madurai.",
    "8 nights, 9 days",
    "Rs 17500 non-AC railway",
    "Rs 20500 AC railway",
    "Tour dates: 18 August, 27 September, 18 November, 04 December, 30 December",
    "Day 1: Pune to Trivandrum",
    "Day 3: Arrive Trivandrum and local sightseeing. Sightseeing: Azhimala Shiv temple, Padmanabh temple, Kerala beach.",
    "Day 4: Kanyakumari local sightseeing. Sightseeing: Suchindram temple, Kanyakumari Devi temple, Vivekanand Rock, Gandhi Mandapam.",
    "Round trip railway sleeper class travel, intercity bus travel, tea, breakfast, 2 meals per day",
    "Pure vegetarian meals. Railway meals are personal expense.",
    "Deluxe hotel arrangement, 3-4 people per room.",
    "If you want a personal room, you have to pay Rs 5000 extra",
]


# ═══════════════════════════════════════════════════════════
# All test directions
# ═══════════════════════════════════════════════════════════
TEST_DIRECTIONS = [
    # Indic → English
    ("marathi",  "english",  MARATHI_SEGMENTS,  "Marathi → English"),
    ("marlish",  "english",  MARLISH_SEGMENTS,  "Marlish → English"),
    ("hindi",    "english",  HINDI_SEGMENTS,    "Hindi → English"),
    ("hinglish", "english",  HINGLISH_SEGMENTS, "Hinglish → English"),
    # English → Indic
    ("english",  "marathi",  ENGLISH_SEGMENTS,  "English → Marathi"),
    ("english",  "marlish",  ENGLISH_SEGMENTS,  "English → Marlish"),
    ("english",  "hindi",    ENGLISH_SEGMENTS,  "English → Hindi"),
    ("english",  "hinglish", ENGLISH_SEGMENTS,  "English → Hinglish"),
]


def run_tests():
    results = []

    # Check health
    try:
        health = requests.get(f"{API_URL}/health", timeout=5).json()
        gec_status = health.get("gec_enabled", False)
    except Exception:
        print("ERROR: API server not running. Start it first:")
        print('  $env:PYTHONIOENCODING="utf-8"; .\\venv\\Scripts\\uvicorn api.app:app --host 0.0.0.0 --port 8000')
        return

    print(f"API Status: {health}")
    print(f"GEC Enabled: {gec_status}")
    total_tests = sum(len(segs) for _, _, segs, _ in TEST_DIRECTIONS)
    print(f"\nRunning {total_tests} translation tests across {len(TEST_DIRECTIONS)} directions...")
    print("=" * 70)

    test_count = 0

    for source, target, segments, label in TEST_DIRECTIONS:
        print(f"\n--- {label} ({len(segments)} segments) ---")
        direction_results = []

        for i, seg in enumerate(segments):
            test_count += 1
            try:
                r = translate(seg, source, target)
                entry = {
                    "direction": label,
                    "source_lang": source,
                    "target_lang": target,
                    "input": seg,
                    "output": r["translation"],
                    "latency": r["latency_ms"],
                }
                if r.get("devanagari"):
                    entry["devanagari"] = r["devanagari"]
                direction_results.append(entry)
                print(f"  [{i+1}/{len(segments)}] ✓ ({r['latency_ms']:.0f}ms)")
            except Exception as e:
                print(f"  [{i+1}/{len(segments)}] ✗ {e}")
                direction_results.append({
                    "direction": label,
                    "source_lang": source,
                    "target_lang": target,
                    "input": seg,
                    "output": f"ERROR: {e}",
                    "latency": 0,
                })

        results.extend(direction_results)

    # Write results
    write_results(results, gec_status, total_tests)
    print(f"\n{'=' * 70}")
    print(f"Total: {test_count} tests across {len(TEST_DIRECTIONS)} directions")
    print(f"Results written to: {OUTPUT_FILE}")


def write_results(results, gec_enabled, total_tests):
    from datetime import datetime

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Carnival Tours — Real-World Translation Test (All Languages)\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**GEC Enabled:** {gec_enabled}\n")
        f.write(f"**Total tests:** {total_tests}\n")
        f.write(f"**Directions tested:** 8 (all supported pairs)\n\n")
        f.write("**Languages:** Marathi, Marlish, Hindi, Hinglish, English\n\n")
        f.write("---\n\n")

        current_dir = ""
        test_num = 0
        for r in results:
            if r["direction"] != current_dir:
                current_dir = r["direction"]
                f.write(f"## {current_dir}\n\n")
                test_num = 0

            test_num += 1
            f.write(f"### Segment {test_num}\n")
            f.write(f"- **Input:** `{r['input']}`\n")
            if r.get("devanagari"):
                f.write(f"- **Devanagari:** {r['devanagari']}\n")
            f.write(f"- **Output:** {r['output']}\n")
            f.write(f"- **Latency:** {r['latency']:.0f}ms\n\n")

        # Summary table
        f.write("---\n\n")
        f.write("## Summary\n\n")
        f.write("| Direction | Segments | Avg Latency |\n")
        f.write("|-----------|----------|-------------|\n")

        directions_seen = []
        for r in results:
            if r["direction"] not in directions_seen:
                directions_seen.append(r["direction"])

        for d in directions_seen:
            d_results = [r for r in results if r["direction"] == d]
            avg_lat = sum(r["latency"] for r in d_results) / len(d_results) if d_results else 0
            f.write(f"| {d} | {len(d_results)} | {avg_lat:.0f}ms |\n")

        f.write(f"\n- GEC post-processing: **{'enabled' if gec_enabled else 'disabled'}**\n")
        f.write("- Review translations above for accuracy\n")


if __name__ == "__main__":
    run_tests()
