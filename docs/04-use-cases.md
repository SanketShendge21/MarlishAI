# Marlish.AI — Use Cases

> **Version:** 4.0 | **Date:** June 2026 | **Status:** Production

---

## 1. Primary Use Cases

### UC-1: WhatsApp/Chat Translation
**User:** Someone receives a Marlish or Hinglish message they can't read.
**Flow:** Paste romanized text → Get English translation instantly.
**Example:** `"udya party ahe bro, tu yeshil ka?"` → `"There's a party tomorrow, bro. Will you come?"`

### UC-2: Formal Document Translation
**User:** Business user translating tour itineraries, notices, or announcements.
**Flow:** Paste Marathi/Hindi Devanagari text → Get English translation.
**Example:** Carnival Tours itinerary (tested with 13 real segments — 11-12/13 accurate)

### UC-3: English to Regional Language
**User:** Someone writing a message in Marathi/Hindi for a regional audience.
**Flow:** Type in English → Get Marathi or Hindi Devanagari output.
**Example:** `"If you want a personal room, pay Rs 5000 extra"` → `"तुम्हाला वैयक्तिक खोली हवी असेल तर ५००० रुपये अतिरिक्त भरावे लागतील."`

### UC-4: Romanized Output for Chat
**User:** Someone who reads Devanagari but types in Latin script.
**Flow:** English → Marlish/Hinglish romanized output.
**Example:** `"Pure vegetarian meals"` → `"shuddha shakahari jevan"`

### UC-5: Cross-Language Learning
**User:** Language learner comparing translations across Hindi/Marathi/English.
**Flow:** Type in one language, swap direction, compare outputs.

## 2. Real-World Test: Carnival Tours

The entire system was tested with a real-world Carnival Tours travel itinerary covering:
- Temple visits (Suchindram, Kanyakumari Devi, Padmanabh)
- Travel logistics (railway sleeper class, hotel arrangements)
- Pricing (Rs 17500, Rs 20500, 5000 extra)
- Dates and schedules

**Result:** 10-13/13 segments accurate across all 8 language directions.

## 3. Target Users

| User Type | Language Direction | Use Case |
|-----------|-------------------|----------|
| Marathi speakers abroad | Marlish → English | Understanding chat messages |
| Hindi speakers abroad | Hinglish → English | Understanding chat messages |
| Business communicators | English → Marathi/Hindi | Writing regional notices |
| Students | Any → English | Academic translation |
| Tour operators | Marathi → English | Translating itineraries |
| Social media managers | English → Hinglish/Marlish | Writing relatable posts |
