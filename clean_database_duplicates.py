#!/usr/bin/env python3
"""
Clean up duplicate questions in the database
Remove duplicate "How do you approach first dates?" questions
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host='host.docker.internal',
        database='echosofme_dev',
        user='echosofme',
        password='secure_dev_password',
        port=5432
    )

def clean_dating_duplicates():
    """Remove duplicate dating questions from database"""
    print("🧹 Cleaning duplicate questions from database...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Find all dating_experiences questions
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                WHERE category = 'dating_experiences'
                ORDER BY id ASC
            """)

            dating_questions = cur.fetchall()
            print(f"📊 Found {len(dating_questions)} dating_experiences questions in database")

            # Group by question text
            from collections import defaultdict
            question_groups = defaultdict(list)

            for q in dating_questions:
                question_groups[q['question_text']].append(q)

            # Find duplicates
            duplicates_to_delete = []
            for text, questions in question_groups.items():
                if len(questions) > 1:
                    print(f"🔍 Found {len(questions)} copies of: '{text[:50]}...'")
                    # Keep the first one (lowest ID), delete the rest
                    for q in questions[1:]:
                        duplicates_to_delete.append(q['id'])

            if duplicates_to_delete:
                print(f"🗑️ Processing {len(duplicates_to_delete)} duplicate questions...")

                # First, update responses to reference the primary question
                for text, questions in question_groups.items():
                    if len(questions) > 1:
                        primary_id = questions[0]['id']  # Keep first question
                        duplicate_ids = [q['id'] for q in questions[1:]]

                        print(f"   Moving responses from duplicates to question {primary_id}")
                        cur.execute("""
                            UPDATE responses
                            SET question_id = %s
                            WHERE question_id = ANY(%s)
                        """, (primary_id, duplicate_ids))

                        updated_responses = cur.rowcount
                        if updated_responses > 0:
                            print(f"   Updated {updated_responses} responses")

                # Now delete duplicate questions
                cur.execute("""
                    DELETE FROM questions
                    WHERE id = ANY(%s)
                """, (duplicates_to_delete,))

                deleted_count = cur.rowcount
                conn.commit()

                print(f"✅ Successfully deleted {deleted_count} duplicate questions")

                # Verify cleanup
                cur.execute("""
                    SELECT COUNT(*) as total,
                           COUNT(DISTINCT question_text) as unique_texts
                    FROM questions
                    WHERE category = 'dating_experiences'
                """)

                result = cur.fetchone()
                print(f"🎯 Final count: {result['total']} total questions, {result['unique_texts']} unique texts")

                if result['total'] == result['unique_texts']:
                    print("✨ Success! All dating questions are now unique!")
                else:
                    print("⚠️ Warning: Still have duplicates remaining")
            else:
                print("✅ No duplicates found - database is clean!")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_dating_duplicates()