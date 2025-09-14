#!/usr/bin/env python3
"""
Detailed analysis of philosophy_values category duplicates
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

def analyze_philosophy_values():
    """Analyze philosophy_values category for duplicates"""
    print("🔍 Analyzing philosophy_values category...\n")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all philosophy_values questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'philosophy_values'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Total philosophy_values questions: {len(questions)}")

            # Count duplicates
            question_texts = [q['question_text'] for q in questions]
            text_counts = Counter(question_texts)

            # Find unique and duplicate questions
            unique_questions = [text for text, count in text_counts.items() if count == 1]
            duplicate_groups = [(text, count) for text, count in text_counts.items() if count > 1]

            print(f"✅ Unique questions: {len(unique_questions)}")
            print(f"⚠️  Duplicate groups: {len(duplicate_groups)}")
            print(f"🔄 Total duplicate entries to remove: {sum(count - 1 for text, count in duplicate_groups)}")

            # Show all duplicate questions sorted by count
            print("\n📝 All Duplicate Questions (sorted by frequency):")
            print("=" * 80)

            for text, count in sorted(duplicate_groups, key=lambda x: x[1], reverse=True):
                print(f"\n[{count} copies] {text}")

                # Find IDs for this duplicate
                duplicate_ids = [q['id'] for q in questions if q['question_text'] == text]
                print(f"   IDs: {duplicate_ids[:5]}{'...' if len(duplicate_ids) > 5 else ''}")

            # Check for responses to these duplicates
            print("\n" + "=" * 80)
            print("📊 Checking for user responses to duplicate questions...")

            all_duplicate_ids = []
            for text, count in duplicate_groups:
                ids = [q['id'] for q in questions if q['question_text'] == text]
                all_duplicate_ids.extend(ids[1:])  # Keep first, mark rest for deletion

            if all_duplicate_ids:
                cur.execute("""
                    SELECT COUNT(*) as response_count,
                           COUNT(DISTINCT user_id) as unique_users
                    FROM responses
                    WHERE question_id = ANY(%s)
                """, (all_duplicate_ids,))

                result = cur.fetchone()
                print(f"💬 Responses to duplicate questions: {result['response_count']}")
                print(f"👥 Unique users affected: {result['unique_users']}")

            # Summary
            print("\n" + "=" * 80)
            print("📈 SUMMARY:")
            print(f"   Category: philosophy_values")
            print(f"   Total questions: {len(questions)}")
            print(f"   Unique questions: {len(text_counts)}")
            print(f"   Duplicates to remove: {sum(count - 1 for text, count in duplicate_groups)}")
            print(f"   Questions after cleanup: {len(text_counts)}")
            print(f"   Reduction: {(1 - len(text_counts)/len(questions)) * 100:.1f}%")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_philosophy_values()