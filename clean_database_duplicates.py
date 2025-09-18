#!/usr/bin/env python3
"""
Clean duplicate questions from the database
Keep only the first occurrence (lowest ID) of each unique question text
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict

def get_db_connection():
    return psycopg2.connect(
        host='host.docker.internal',
        database='echosofme_dev',
        user='echosofme',
        password='secure_dev_password',
        port=5432
    )

def clean_all_duplicates():
    """Remove ALL duplicate question texts from database"""
    print("🧹 Cleaning ALL duplicate questions from database...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get initial count
            cur.execute("SELECT COUNT(*) as count FROM questions")
            initial_count = cur.fetchone()['count']
            print(f"📊 Initial question count: {initial_count}")

            # Find ALL questions
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                ORDER BY id ASC
            """)

            all_questions = cur.fetchall()
            print(f"📊 Found {len(all_questions)} total questions in database")

            # Group by question text
            question_groups = defaultdict(list)
            for q in all_questions:
                question_groups[q['question_text']].append(q)

            # Find duplicates
            duplicates_to_delete = []
            duplicate_count = 0
            for text, questions in question_groups.items():
                if len(questions) > 1:
                    duplicate_count += 1
                    print(f"🔍 Found {len(questions)} copies of: '{text[:60]}...'")
                    # Keep the first one (lowest ID), delete the rest
                    for q in questions[1:]:
                        duplicates_to_delete.append(q['id'])

            if duplicates_to_delete:
                print(f"\n🗑️ Processing {len(duplicates_to_delete)} duplicate questions from {duplicate_count} question texts...")

                # First, move responses from duplicates to the primary question
                # Handle unique constraint by only moving responses where user doesn't already have one for primary question
                response_moves = 0
                response_conflicts = 0
                for text, questions in question_groups.items():
                    if len(questions) > 1:
                        primary_id = questions[0]['id']  # Keep first question
                        duplicate_ids = [q['id'] for q in questions[1:]]

                        # Move responses that won't conflict with existing ones
                        cur.execute("""
                            UPDATE responses
                            SET question_id = %s
                            WHERE question_id = ANY(%s)
                            AND user_id NOT IN (
                                SELECT user_id FROM responses WHERE question_id = %s
                            )
                        """, (primary_id, duplicate_ids, primary_id))

                        updated_responses = cur.rowcount
                        response_moves += updated_responses

                        # Count conflicting responses that we'll delete
                        cur.execute("""
                            SELECT COUNT(*) as conflicts
                            FROM responses
                            WHERE question_id = ANY(%s)
                            AND user_id IN (
                                SELECT user_id FROM responses WHERE question_id = %s
                            )
                        """, (duplicate_ids, primary_id))

                        conflicts = cur.fetchone()['conflicts']
                        response_conflicts += conflicts

                        if updated_responses > 0:
                            print(f"   Moved {updated_responses} responses from duplicates to question {primary_id}")
                        if conflicts > 0:
                            print(f"   Will delete {conflicts} conflicting responses (user already answered primary question)")

                if response_moves > 0:
                    print(f"✅ Moved {response_moves} total responses to primary questions")
                if response_conflicts > 0:
                    print(f"⚠️  Will delete {response_conflicts} responses due to conflicts")

                # Delete remaining responses to duplicate questions that couldn't be moved
                remaining_responses = 0
                for text, questions in question_groups.items():
                    if len(questions) > 1:
                        duplicate_ids = [q['id'] for q in questions[1:]]

                        cur.execute("""
                            DELETE FROM responses
                            WHERE question_id = ANY(%s)
                        """, (duplicate_ids,))

                        deleted_responses = cur.rowcount
                        remaining_responses += deleted_responses

                if remaining_responses > 0:
                    print(f"🗑️  Deleted {remaining_responses} remaining responses to duplicate questions")

                # Now delete duplicate questions
                cur.execute("""
                    DELETE FROM questions
                    WHERE id = ANY(%s)
                """, (duplicates_to_delete,))

                deleted_count = cur.rowcount
                conn.commit()

                print(f"✅ Successfully deleted {deleted_count} duplicate questions")

                # Get final count
                cur.execute("SELECT COUNT(*) as count FROM questions")
                final_count = cur.fetchone()['count']

                print(f"\n📊 Results:")
                print(f"  Initial:  {initial_count} questions")
                print(f"  Deleted:  {deleted_count} duplicates")
                print(f"  Final:    {final_count} unique questions")

                # Verify cleanup
                cur.execute("""
                    SELECT COUNT(*) as total,
                           COUNT(DISTINCT question_text) as unique_texts
                    FROM questions
                """)

                result = cur.fetchone()
                if result['total'] == result['unique_texts']:
                    print("✨ Success! All questions are now unique!")
                else:
                    print(f"⚠️ Warning: Still have {result['total'] - result['unique_texts']} duplicates remaining")
            else:
                print("✅ No duplicates found - database is already clean!")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    clean_all_duplicates()