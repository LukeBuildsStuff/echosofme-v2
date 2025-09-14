#!/usr/bin/env python3
"""
Detailed analysis of creative_expression category for duplicates
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

def analyze_creative_expression():
    """Analyze creative_expression category for duplicates"""
    print("🔍 Analyzing creative_expression category...\n")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all creative_expression questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'creative_expression'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Total creative_expression questions: {len(questions)}")

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
                print("\n📝 Top 10 Most Duplicated Questions:")
                print("=" * 80)
                for text, count in sorted(duplicate_groups, key=lambda x: x[1], reverse=True)[:10]:
                    print(f"\n[{count} copies] {text}")

                if len(duplicate_groups) > 10:
                    print(f"\n... and {len(duplicate_groups) - 10} more duplicate groups")
            else:
                print("\n🎉 NO DUPLICATES FOUND - All questions are unique!")

            # Summary
            print("\n" + "=" * 80)
            print("📈 SUMMARY:")
            print(f"   Category: creative_expression")
            print(f"   Total questions: {len(questions)}")
            print(f"   Unique questions: {len(text_counts)}")
            if duplicate_groups:
                print(f"   ❌ Duplicates to remove: {sum(count - 1 for text, count in duplicate_groups)}")
                print(f"   📉 Duplication rate: {(sum(count - 1 for text, count in duplicate_groups) / len(questions) * 100):.1f}%")
            else:
                print(f"   ✅ All questions are unique!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_creative_expression()