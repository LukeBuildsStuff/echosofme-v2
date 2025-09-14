#!/usr/bin/env python3
"""
Detailed analysis of hobbies category after cleanup
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from collections import Counter

def get_db_connection():
    return psycopg2.connect(
        host='host.docker.internal',
        database='echosofme_dev',
        user='echosofme',
        password='secure_dev_password',
        port=5432
    )

def analyze_hobbies():
    """Analyze hobbies category for duplicates"""
    print("🔍 Analyzing hobbies category...\n")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all hobbies questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'hobbies'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Total hobbies questions: {len(questions)}")

            # Count duplicates
            question_texts = [q['question_text'] for q in questions]
            text_counts = Counter(question_texts)

            # Find unique and duplicate questions
            unique_questions = [text for text, count in text_counts.items() if count == 1]
            duplicate_groups = [(text, count) for text, count in text_counts.items() if count > 1]

            print(f"✅ Unique questions: {len(unique_questions)}")
            print(f"⚠️  Duplicate groups: {len(duplicate_groups)}")
            print(f"🔄 Total duplicate entries: {sum(count - 1 for text, count in duplicate_groups)}")

            if duplicate_groups:
                print("\n📝 Remaining Duplicate Questions:")
                print("=" * 80)
                for text, count in sorted(duplicate_groups, key=lambda x: x[1], reverse=True):
                    print(f"\n[{count} copies] {text}")
            else:
                print("\n🎉 NO DUPLICATES FOUND - All questions are unique!")

            # Show some sample new questions (questions with high IDs are likely new)
            cur.execute("""
                SELECT question_text
                FROM questions
                WHERE category = 'hobbies'
                ORDER BY id DESC
                LIMIT 10
            """)
            new_questions = cur.fetchall()

            print("\n" + "=" * 80)
            print("📌 Sample of newest questions (likely added during cleanup):")
            for i, q in enumerate(new_questions):
                print(f"   {i+1}. {q['question_text'][:80]}...")

            # Summary
            print("\n" + "=" * 80)
            print("📈 SUMMARY:")
            print(f"   Category: hobbies")
            print(f"   Total questions: {len(questions)}")
            print(f"   Unique questions: {len(text_counts)}")
            if duplicate_groups:
                print(f"   ❌ Duplicates remaining: {sum(count - 1 for text, count in duplicate_groups)}")
            else:
                print(f"   ✅ All questions are unique!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_hobbies()