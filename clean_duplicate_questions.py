#!/usr/bin/env python3
"""
Clean duplicate questions from the JSON source file
Keep only the first occurrence of each unique question text
"""

import json
import shutil
from datetime import datetime

def clean_json_duplicates():
    """Remove duplicate question texts from the JSON file"""

    # Backup the original file first
    backup_path = f"src/data/questions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy2('src/data/questions.json', backup_path)
    print(f"✅ Created backup: {backup_path}")

    # Load questions
    with open('src/data/questions.json', 'r') as f:
        questions = json.load(f)

    print(f"📊 Original count: {len(questions)} questions")

    # Track seen question texts and keep unique ones
    seen_texts = set()
    unique_questions = []
    removed_count = 0

    for question in questions:
        question_text = question['question']

        if question_text not in seen_texts:
            # First time seeing this question text - keep it
            seen_texts.add(question_text)
            unique_questions.append(question)
        else:
            # Duplicate question text - skip it
            removed_count += 1
            print(f"🗑️  Removing duplicate (ID {question['id']}): {question_text[:60]}...")

    print(f"\n📊 Results:")
    print(f"  Original: {len(questions)} questions")
    print(f"  Removed:  {removed_count} duplicates")
    print(f"  Final:    {len(unique_questions)} unique questions")

    # Sort by ID to maintain order
    unique_questions.sort(key=lambda x: x['id'])

    # Write the cleaned file
    with open('src/data/questions.json', 'w') as f:
        json.dump(unique_questions, f, indent=2, ensure_ascii=False)

    print(f"✅ Cleaned JSON saved with {len(unique_questions)} unique questions")

    # Verify the result
    print("\n🔍 Verifying clean file...")
    with open('src/data/questions.json', 'r') as f:
        verified = json.load(f)

    texts = [q['question'] for q in verified]
    unique_texts = set(texts)

    if len(texts) == len(unique_texts):
        print("✅ Verification passed: No duplicates in cleaned file!")
    else:
        print(f"❌ Verification failed: Found {len(texts) - len(unique_texts)} duplicates still exist")

    return len(unique_questions), removed_count

if __name__ == "__main__":
    clean_json_duplicates()