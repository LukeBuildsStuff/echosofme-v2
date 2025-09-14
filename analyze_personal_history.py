#!/usr/bin/env python3
"""
Detailed analysis of personal_history category after cleanup
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

def analyze_personal_history():
    """Analyze personal_history category for duplicates"""
    print("🔍 Analyzing personal_history category...\n")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all personal_history questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'personal_history'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Total personal_history questions: {len(questions)}")

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

            # Show some sample questions
            print("\n" + "=" * 80)
            print("📌 Sample of questions (first 15):")
            for i, text in enumerate(unique_questions[:15]):
                print(f"   {i+1}. {text[:80]}...")

            # Summary
            print("\n" + "=" * 80)
            print("📈 SUMMARY:")
            print(f"   Category: personal_history")
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
    analyze_personal_history()