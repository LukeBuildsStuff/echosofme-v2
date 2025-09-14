#!/usr/bin/env python3
"""
Check question IDs and references
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

def check_question_ids():
    """Check question IDs and their relationships"""
    print("🔍 Checking question IDs and references...\n")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check question ID range
            cur.execute("""
                SELECT MIN(id) as min_id, MAX(id) as max_id, COUNT(*) as total
                FROM questions
            """)
            result = cur.fetchone()
            print(f"📊 Question IDs:")
            print(f"   Range: {result['min_id']} to {result['max_id']}")
            print(f"   Total questions: {result['total']}")
            print(f"   Expected if continuous: {result['max_id'] - result['min_id'] + 1}")
            print(f"   Gaps in IDs: {result['max_id'] - result['min_id'] + 1 - result['total']}")

            # Check for responses referencing deleted questions
            cur.execute("""
                SELECT r.id, r.question_id, r.user_id, u.email
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                JOIN users u ON r.user_id = u.id
                WHERE q.id IS NULL
            """)
            orphaned = cur.fetchall()

            if orphaned:
                print(f"\n⚠️ WARNING: Found {len(orphaned)} responses referencing deleted questions!")
                for resp in orphaned[:5]:
                    print(f"   Response {resp['id']}: Question {resp['question_id']} (user: {resp['email']})")
            else:
                print(f"\n✅ No orphaned responses - all responses have valid question references")

            # Check how responses are linked
            cur.execute("""
                SELECT COUNT(*) as total_responses,
                       COUNT(DISTINCT question_id) as unique_questions_answered,
                       COUNT(DISTINCT user_id) as unique_users
                FROM responses
            """)
            resp_stats = cur.fetchone()
            print(f"\n📝 Response Statistics:")
            print(f"   Total responses: {resp_stats['total_responses']}")
            print(f"   Unique questions answered: {resp_stats['unique_questions_answered']}")
            print(f"   Active users: {resp_stats['unique_users']}")

            # Check recently added questions
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                WHERE id > 3500
                ORDER BY id DESC
                LIMIT 5
            """)
            recent = cur.fetchall()
            print(f"\n🆕 Recently added questions (sample):")
            for q in recent:
                print(f"   ID {q['id']} [{q['category']}]: {q['question_text'][:60]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_question_ids()