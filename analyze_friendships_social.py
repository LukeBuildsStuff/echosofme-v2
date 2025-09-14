#!/usr/bin/env python3
"""
Detailed analysis of friendships_social category for duplicates
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

def analyze_friendships_social():
    """Analyze friendships_social category for duplicates"""
    print("🔍 Analyzing friendships_social category...\n")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check if category exists
            cur.execute("""
                SELECT DISTINCT category
                FROM questions
                WHERE category LIKE '%friend%' OR category LIKE '%social%'
                ORDER BY category
            """)
            categories = cur.fetchall()
            print("📂 Found categories related to friendship/social:")
            for cat in categories:
                print(f"   - {cat['category']}")

            # Get all friendships_social questions (or similar category)
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                WHERE category = 'friendships_social'
                   OR category = 'friendships'
                   OR category = 'social'
                ORDER BY category, question_text, id ASC
            """)

            questions = cur.fetchall()

            if not questions:
                print("\n❌ No questions found in friendships_social, friendships, or social categories")
                return

            print(f"\n📊 Total friendships/social questions: {len(questions)}")

            # Group by category
            by_category = {}
            for q in questions:
                cat = q['category']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(q)

            for cat, qs in by_category.items():
                print(f"\n   Category '{cat}': {len(qs)} questions")

            # Count duplicates across all friendship/social questions
            question_texts = [q['question_text'] for q in questions]
            text_counts = Counter(question_texts)

            # Find unique and duplicate questions
            unique_questions = [text for text, count in text_counts.items() if count == 1]
            duplicate_groups = [(text, count) for text, count in text_counts.items() if count > 1]

            print(f"\n✅ Unique questions: {len(unique_questions)}")
            print(f"⚠️  Duplicate groups: {len(duplicate_groups)}")
            print(f"🔄 Total duplicate entries: {sum(count - 1 for text, count in duplicate_groups)}")

            if duplicate_groups:
                print("\n📝 All Duplicate Questions:")
                print("=" * 80)
                for text, count in sorted(duplicate_groups, key=lambda x: x[1], reverse=True):
                    print(f"\n[{count} copies] {text}")
            else:
                print("\n🎉 NO DUPLICATES FOUND - All questions are unique!")

            # Summary
            print("\n" + "=" * 80)
            print("📈 SUMMARY:")
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
    analyze_friendships_social()