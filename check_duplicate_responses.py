#!/usr/bin/env python3
"""
Check which users have answered the duplicate dating questions
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host='host.docker.internal',
        database='echosofme_dev',
        user='echosofme',
        password='secure_dev_password',
        port=5432
    )

def check_duplicate_responses():
    """Check who has answered the duplicate questions"""
    print("🔍 Checking responses to duplicate dating questions...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Find duplicate question IDs
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'dating_experiences'
                AND question_text = 'How do you approach first dates?'
                ORDER BY id ASC
            """)

            duplicate_questions = cur.fetchall()
            print(f"📊 Found {len(duplicate_questions)} duplicate questions")

            if duplicate_questions:
                question_ids = [q['id'] for q in duplicate_questions]

                # Check responses to these questions
                cur.execute("""
                    SELECT r.question_id, u.email, r.response_text, r.created_at
                    FROM responses r
                    JOIN users u ON r.user_id = u.id
                    WHERE r.question_id = ANY(%s)
                    ORDER BY r.created_at DESC
                """, (question_ids,))

                responses = cur.fetchall()
                print(f"💬 Found {len(responses)} responses to duplicate questions")

                # Group by user
                user_responses = {}
                for resp in responses:
                    email = resp['email']
                    if email not in user_responses:
                        user_responses[email] = []
                    user_responses[email].append(resp)

                print(f"\n👥 Users who have answered duplicate questions:")
                for email, user_resps in user_responses.items():
                    print(f"   {email}: {len(user_resps)} responses")
                    for resp in user_resps[:2]:  # Show first 2 responses
                        print(f"     - Q{resp['question_id']}: {resp['response_text'][:50]}... ({resp['created_at']})")
                    if len(user_resps) > 2:
                        print(f"     ... and {len(user_resps) - 2} more")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_duplicate_responses()