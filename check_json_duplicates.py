#!/usr/bin/env python3
"""Check for duplicate questions in the JSON source file"""

import json
from collections import Counter

def check_json_duplicates():
    # Load JSON file
    with open('src/data/questions.json', 'r') as f:
        questions = json.load(f)

    print(f"Total questions in JSON: {len(questions)}")

    # Check for duplicate IDs
    ids = [q['id'] for q in questions]
    id_counts = Counter(ids)
    duplicate_ids = {id: count for id, count in id_counts.items() if count > 1}

    if duplicate_ids:
        print(f"\n⚠️  Found {len(duplicate_ids)} duplicate IDs in JSON:")
        for id, count in duplicate_ids.items():
            print(f"  ID {id}: appears {count} times")
    else:
        print("\n✅ No duplicate IDs in JSON")

    # Check for duplicate question texts
    texts = [q['question'] for q in questions]
    text_counts = Counter(texts)
    duplicate_texts = {text: count for text, count in text_counts.items() if count > 1}

    if duplicate_texts:
        print(f"\n⚠️  Found {len(duplicate_texts)} duplicate question texts in JSON:")
        for text, count in sorted(duplicate_texts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  Count: {count} - Text: {text[:80]}...")
            # Find IDs with this text
            matching_ids = [q['id'] for q in questions if q['question'] == text]
            print(f"    IDs: {matching_ids}")
    else:
        print("\n✅ No duplicate question texts in JSON")

    # Check the specific known duplicate
    q1 = next((q for q in questions if q['id'] == 1), None)
    q176 = next((q for q in questions if q['id'] == 176), None)

    if q1 and q176:
        print(f"\n📊 Checking known duplicates (IDs 1 and 176):")
        print(f"  ID 1: {q1['question'][:80]}...")
        print(f"  ID 176: {q176['question'][:80]}...")
        if q1['question'] == q176['question']:
            print("  ⚠️ These are duplicates in the JSON source!")
        else:
            print("  ✅ These are different questions in JSON")

if __name__ == "__main__":
    check_json_duplicates()