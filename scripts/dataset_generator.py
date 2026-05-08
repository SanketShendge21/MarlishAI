import google.generativeai as genai
import asyncio
import aiofiles
import json
import os
import random
import hashlib
import re
import csv
import numpy as np
from google.api_core import exceptions
from concurrent.futures import ThreadPoolExecutor
from asyncio import Queue
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =====================================================
# CONFIG
# =====================================================

API_KEY = "YOUR_API_KEY"

MODEL_NAME = "gemini-3-flash-preview"

TOTAL_ROWS = 30000
ROWS_PER_REQUEST = 15
MAX_CONCURRENT_REQUESTS = 5
QUEUE_SIZE = 100
SIMILARITY_THRESHOLD = 0.92

OUTPUT_DIR = "dataset_output"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "apni_bhasha_dataset.csv"
)

CATEGORIES = [
    "Everyday conversations",
    "Tech & Work",
    "Slang & Idioms",
    "Travel & Logistics",
    "Emotional/Sentiments",
    "Gaming",
    "College Life",
    "Arguments",
    "Social Media",
    "Family"
]

HEADERS = [
    "hinglish",
    "marlish",
    "hindi_devanagari",
    "marathi_devanagari",
    "english",
    "category"
]

# =====================================================
# INIT
# =====================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(MODEL_NAME)

embedding_model = SentenceTransformer(
    'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
)

executor = ThreadPoolExecutor(
    max_workers=MAX_CONCURRENT_REQUESTS
)

queue = Queue(maxsize=QUEUE_SIZE)

# =====================================================
# GLOBAL STATE
# =====================================================

seen_hashes = set()
seen_embeddings = []

generated_count = 0
counter_lock = asyncio.Lock()
embedding_lock = asyncio.Lock()

# =====================================================
# REGEX VALIDATION
# =====================================================

DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')


def has_devanagari(text):
    return bool(DEVANAGARI_PATTERN.search(text))

# =====================================================
# HASHING
# =====================================================


def hash_row(row):
    joined = "|".join(row)
    return hashlib.sha256(joined.encode()).hexdigest()

# =====================================================
# PROMPT
# =====================================================


def build_prompt():

    category = random.choice(CATEGORIES)

    return f'''
Generate EXACTLY {ROWS_PER_REQUEST} highly diverse multilingual conversational examples.

Return ONLY valid JSON array.

Schema:
[
  {{
    "hinglish": "",
    "marlish": "",
    "hindi_devanagari": "",
    "marathi_devanagari": "",
    "english": "",
    "category": "{category}"
  }}
]

STRICT RULES:
- Natural human conversations.
- Use realistic slang sometimes.
- Avoid repetitive sentence structures.
- Include emotional variance.
- Use varied sentence lengths.
- No markdown.
- No explanations.
- No duplicate entries.
- Marathi must sound native.
- Hindi must sound native.
- Avoid robotic language.
- Make all rows semantically unique.
'''

# =====================================================
# JSON EXTRACTION
# =====================================================


def extract_json(text):

    start = text.find('[')
    end = text.rfind(']')

    if start == -1 or end == -1:
        return None

    return text[start:end+1]

# =====================================================
# SEMANTIC DEDUPLICATION
# =====================================================


async def semantic_duplicate(text):

    global seen_embeddings

    embedding = embedding_model.encode([text])[0]

    async with embedding_lock:

        if len(seen_embeddings) == 0:
            seen_embeddings.append(embedding)
            return False

        similarities = cosine_similarity(
            [embedding],
            seen_embeddings
        )[0]

        max_similarity = np.max(similarities)

        if max_similarity > SIMILARITY_THRESHOLD:
            return True

        seen_embeddings.append(embedding)

    return False

# =====================================================
# VALIDATION
# =====================================================


async def validate_item(item):

    required = [
        "hinglish",
        "marlish",
        "hindi_devanagari",
        "marathi_devanagari",
        "english",
        "category"
    ]

    if not all(k in item for k in required):
        return None

    row = [
        str(item["hinglish"]).strip(),
        str(item["marlish"]).strip(),
        str(item["hindi_devanagari"]).strip(),
        str(item["marathi_devanagari"]).strip(),
        str(item["english"]).strip(),
        str(item["category"]).strip()
    ]

    if any(len(x) < 3 for x in row):
        return None

    if row[-1] not in CATEGORIES:
        return None

    if not has_devanagari(row[2]):
        return None

    if not has_devanagari(row[3]):
        return None

    row_hash_value = hash_row(row)

    if row_hash_value in seen_hashes:
        return None

    combined_text = " ".join(row[:5])

    is_duplicate = await semantic_duplicate(combined_text)

    if is_duplicate:
        return None

    seen_hashes.add(row_hash_value)

    return row

# =====================================================
# GENERATION
# =====================================================


async def generate_rows():

    prompt = build_prompt()

    loop = asyncio.get_running_loop()

    try:

        response = await loop.run_in_executor(
            executor,
            lambda: model.generate_content(
                prompt,
                generation_config={
                    "temperature": 1.15,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192
                }
            )
        )

        raw_text = response.text.strip()

        json_text = extract_json(raw_text)

        if not json_text:
            return []

        data = json.loads(json_text)

        cleaned = []

        for item in data:

            validated = await validate_item(item)

            if validated:
                cleaned.append(validated)

        return cleaned

    except json.JSONDecodeError:
        return []

    except exceptions.ResourceExhausted:

        wait_time = random.randint(8, 20)

        print(f"Rate limited. Sleeping {wait_time}s")

        await asyncio.sleep(wait_time)

        return []

    except Exception as e:

        print(f"Generation Error: {e}")

        await asyncio.sleep(2)

        return []

# =====================================================
# PRODUCER
# =====================================================


async def producer(worker_id):

    global generated_count

    while True:

        async with counter_lock:

            if generated_count >= TOTAL_ROWS:
                break

        rows = await generate_rows()

        if rows:

            await queue.put(rows)

            async with counter_lock:
                generated_count += len(rows)

            print(
                f"[Worker {worker_id}] "
                f"+{len(rows)} rows | "
                f"Total={generated_count}"
            )

# =====================================================
# CONSUMER
# =====================================================


async def consumer():

    file_exists = os.path.isfile(OUTPUT_FILE)

    async with aiofiles.open(
        OUTPUT_FILE,
        mode='a',
        encoding='utf-8',
        newline=''
    ) as f:

        if not file_exists:

            header_line = ",".join(HEADERS) + "\n"
            await f.write(header_line)

        while True:

            rows = await queue.get()

            output_lines = []

            for row in rows:

                escaped = []

                for value in row:
                    value = value.replace('"', '""')
                    escaped.append(f'"{value}"')

                output_lines.append(
                    ",".join(escaped)
                )

            await f.write(
                "\n".join(output_lines) + "\n"
            )

            queue.task_done()

# =====================================================
# DATASET STATS
# =====================================================


def print_dataset_stats():

    print("\n========== DATASET STATS ==========")
    print(f"Total unique rows: {generated_count}")
    print(f"Semantic embeddings stored: {len(seen_embeddings)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("===================================")

# =====================================================
# MAIN
# =====================================================


async def main():

    consumer_task = asyncio.create_task(
        consumer()
    )

    producer_tasks = [
        asyncio.create_task(producer(i))
        for i in range(MAX_CONCURRENT_REQUESTS)
    ]

    await asyncio.gather(*producer_tasks)

    await queue.join()

    consumer_task.cancel()

    print_dataset_stats()

# =====================================================
# ENTRY
# =====================================================


if __name__ == "__main__":

    asyncio.run(main())
