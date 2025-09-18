#!/usr/bin/env python3
"""Quick script to check for duplicate questions in the database"""

import psycopg2
from psycopg2.extras import RealDictCursor
from collections import Counter

def get_db_connection():
    DATABASE_CONFIG = {
        'host': 'host.docker.internal',
        'database': 'echosofme_dev',
        'user': 'echosofme',
        'password': 'secure_dev_password',
        'port': 5432
    }
    return psycopg2.connect(**DATABASE_CONFIG)

def check_duplicates():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all questions
            cur.execute("SELECT id, question_text FROM questions ORDER BY id")
            questions = cur.fetchall()

            print(f"Total questions in database: {len(questions)}")

            # Find duplicates by text
            question_texts = Counter(q['question_text'] for q in questions)
            duplicates = {text: count for text, count in question_texts.items() if count > 1}

            if duplicates:
                print(f"\nFound {len(duplicates)} questions with duplicate text:")
                for text, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"\n  Count: {count} - Text: {text[:100]}...")
                    # Get IDs of duplicates
                    cur.execute("SELECT id FROM questions WHERE question_text = %s ORDER BY id", (text,))
                    ids = [row['id'] for row in cur.fetchall()]
                    print(f"  IDs: {ids}")
            else:
                print("\nNo duplicate questions found!")

            # Check specific known duplicate
            cur.execute("SELECT id, question_text FROM questions WHERE id IN (1, 176)")
            known = cur.fetchall()
            if len(known) == 2:
                print(f"\n⚠️  Known duplicate check (IDs 1 and 176):")
                for q in known:
                    print(f"  ID {q['id']}: {q['question_text'][:100]}...")
                if known[0]['question_text'] == known[1]['question_text']:
                    print("  ✓ Still duplicates!")
                else:
                    print("  ✗ No longer duplicates")

    finally:
        conn.close()

if __name__ == "__main__":
    check_duplicates()