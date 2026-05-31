"""Quick test for reverse transliteration."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.transliterator.reverse_transliterate import reverse_transliterate
from scripts.transliterator.fallback_map import SEED_MAP

tests = [
    ("तू कुठे आहेस", "tu kuthe ahes"),
    ("कसा आहेस मित्र", "kasa ahes mitra"),
    ("मला माहित नाही", "mala mahit nahi"),
    ("तुझा नाव काय आहे", "tuza nav kay ahe"),
    ("उद्या काय scene आहे", "udya kay scene ahe"),
    ("मी college ला जातो आहे", "mi college la jato ahe"),
]

print("=" * 70)
print("  Reverse Transliteration Test (with seed map)")
print("=" * 70)

for deva, expected in tests:
    result = reverse_transliterate(deva, SEED_MAP)
    match = "PASS" if result.lower().strip() == expected.lower().strip() else "DIFF"
    print(f"\n  [{match}] {deva}")
    print(f"         -> {result}")
    print(f"    expect: {expected}")

print("\n" + "=" * 70)
