#!/usr/bin/env python3
"""
Analyze all duplicate questions across all categories in the database
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from collections import Counter, defaultdict

def get_db_connection():
    return psycopg2.connect(
        host='host.docker.internal',
        database='echosofme_dev',
        user='echosofme',
        password='secure_dev_password',
        port=5432
    )

def analyze_all_duplicates():
    """Analyze all duplicate questions in the database"""
    print("🔍 Analyzing all questions for duplicates...\n")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all questions
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                ORDER BY category, id ASC
            """)

            all_questions = cur.fetchall()
            print(f"📊 Total questions in database: {len(all_questions)}")

            # Group by category
            categories = defaultdict(list)
            for q in all_questions:
                categories[q['category']].append(q)

            # Analyze each category
            total_duplicates = 0
            duplicate_details = []

            print("\n📁 Category Analysis:")
            print("=" * 70)

            for category, questions in sorted(categories.items()):
                # Count duplicates in this category
                question_texts = [q['question_text'] for q in questions]
                text_counts = Counter(question_texts)

                # Find duplicates
                duplicates = {text: count for text, count in text_counts.items() if count > 1}

                category_duplicate_count = sum(count - 1 for count in duplicates.values())
                total_duplicates += category_duplicate_count

                print(f"\n📂 {category}:")
                print(f"   Total questions: {len(questions)}")
                print(f"   Unique questions: {len(text_counts)}")

                if duplicates:
                    print(f"   ⚠️  Duplicates found: {category_duplicate_count} duplicate entries")
                    print(f"   📝 Duplicate questions:")
                    for text, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"      - '{text[:60]}...' appears {count} times")
                        duplicate_details.append({
                            'category': category,
                            'text': text,
                            'count': count
                        })
                    if len(duplicates) > 5:
                        print(f"      ... and {len(duplicates) - 5} more duplicate questions")
                else:
                    print(f"   ✅ No duplicates - all questions are unique!")

            # Summary
            print("\n" + "=" * 70)
            print("📊 SUMMARY:")
            print(f"   Total questions: {len(all_questions)}")
            print(f"   Total categories: {len(categories)}")
            print(f"   Total duplicate entries: {total_duplicates}")

            if total_duplicates > 0:
                print(f"\n⚠️  ACTION NEEDED: {total_duplicates} duplicate questions need to be cleaned up")
                print("\n🔝 Top duplicates across all categories:")
                for detail in sorted(duplicate_details, key=lambda x: x['count'], reverse=True)[:10]:
                    print(f"   [{detail['category']}] '{detail['text'][:50]}...' - {detail['count']} copies")
            else:
                print("\n✨ EXCELLENT! No duplicates found in the entire database!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_all_duplicates()