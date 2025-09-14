#!/usr/bin/env python3
"""
Clean hobbies category duplicates and add engaging hobby questions
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

def generate_engaging_hobby_questions():
    """Generate 50 engaging hobby and interest questions"""
    return [
        # Hidden Hobbies & Secret Interests
        "What hobby do you hide from certain people in your life?",
        "What interest embarrasses you but brings you genuine joy?",
        "What skill do you pretend not to have?",
        "What hobby would your colleagues be shocked to discover?",
        "What interest do you indulge in when no one's watching?",
        "What hobby makes you feel like a different person?",
        "What passion of yours confuses the people who know you?",
        "What activity do you enjoy that doesn't fit your image?",
        "What hobby do you wish was more socially acceptable?",
        "What interest connects you to a side of yourself others don't see?",

        # Hobby Evolution & Change
        "What interest did you abandon that you wish you'd stuck with?",
        "What hobby took you completely by surprise when you discovered it?",
        "What activity did you hate as a child but love now?",
        "What interest connects you to your younger self?",
        "What hobby did you pick up during a difficult time in your life?",
        "What activity has evolved from obligation to passion for you?",
        "What interest did you inherit from someone important to you?",
        "What hobby represents the biggest change in your personality?",
        "What activity did you discover too late in life?",
        "What interest has taught you the most about yourself?",

        # Passion vs Skill Gap
        "What hobby do you love despite being terrible at it?",
        "What activity makes you feel like a complete beginner every time?",
        "What interest do you pursue purely for the joy, not the results?",
        "What hobby humbles you every time you try it?",
        "What skill do you admire in others but can't seem to master?",
        "What activity proves that passion doesn't always equal talent for you?",
        "What hobby teaches you patience with yourself?",
        "What interest makes you comfortable with being imperfect?",
        "What activity do you return to despite repeated failure?",
        "What hobby reminds you that effort matters more than outcome?",

        # Dream Hobbies & Constraints
        "What hobby would you pursue if money wasn't a factor?",
        "What interest would you dive into if you had unlimited time?",
        "What activity are you saving for retirement?",
        "What hobby requires resources you don't currently have?",
        "What interest would you pursue if you lived somewhere else?",
        "What activity did you give up due to practical constraints?",
        "What hobby would you start if you weren't worried about judgment?",
        "What interest appeals to you but intimidates you too much to try?",
        "What activity would you do if you had unlimited energy?",
        "What hobby represents your 'someday' list?",

        # Hobby Identity & Connection
        "What hobby makes you lose all sense of time?",
        "What activity feels like meditation to you?",
        "What interest makes you feel most alive?",
        "What hobby connects you to something larger than yourself?",
        "What activity puts you in a flow state every time?",
        "What interest has shaped who you are as a person?",
        "What hobby gives you a sense of purpose beyond yourself?",
        "What activity makes you feel most authentically yourself?",
        "What interest has introduced you to your closest friends?",
        "What hobby defines a core part of your identity?"
    ]

def clean_hobbies():
    """Clean hobbies category duplicates and add engaging questions"""
    print("🧹 Cleaning hobbies category duplicates...")

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
            print(f"📊 Found {len(questions)} hobbies questions")

            # Group by question text to find duplicates
            question_groups = defaultdict(list)
            for q in questions:
                question_groups[q['question_text']].append(q['id'])

            # Identify duplicates (groups with more than 1 question)
            duplicate_groups = {text: ids for text, ids in question_groups.items() if len(ids) > 1}
            unique_questions = {text: ids for text, ids in question_groups.items() if len(ids) == 1}

            total_duplicates = sum(len(ids) - 1 for ids in duplicate_groups.values())
            print(f"⚠️  Found {len(duplicate_groups)} duplicate groups")
            print(f"🔄 Total duplicate entries to remove: {total_duplicates}")
            print(f"✅ Unique questions: {len(unique_questions)}")

            # Show duplicate examples
            print("\n📝 All duplicate groups:")
            for text, ids in sorted(duplicate_groups.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"   [{len(ids)} copies] {text[:80]}...")

            # Process each duplicate group
            responses_moved = 0
            questions_deleted = 0

            for question_text, duplicate_ids in duplicate_groups.items():
                primary_id = duplicate_ids[0]  # Keep first occurrence
                duplicate_ids_to_remove = duplicate_ids[1:]  # Remove rest

                print(f"\n🔄 Processing: '{question_text[:60]}...'")
                print(f"   Keeping ID {primary_id}, removing {len(duplicate_ids_to_remove)} duplicates")

                # Move responses from duplicates to primary, avoiding conflicts
                for dup_id in duplicate_ids_to_remove:
                    cur.execute("""
                        UPDATE responses SET question_id = %s
                        WHERE question_id = %s
                        AND NOT EXISTS (
                            SELECT 1 FROM responses r2
                            WHERE r2.user_id = responses.user_id
                            AND r2.question_id = %s
                        )
                    """, (primary_id, dup_id, primary_id))

                    moved = cur.rowcount
                    responses_moved += moved
                    if moved > 0:
                        print(f"   📤 Moved {moved} responses from ID {dup_id} to {primary_id}")

                    # Delete any remaining responses that couldn't be moved
                    cur.execute("DELETE FROM responses WHERE question_id = %s", (dup_id,))
                    if cur.rowcount > 0:
                        print(f"   🗑️  Deleted {cur.rowcount} conflicting responses from ID {dup_id}")

                # Delete duplicate questions
                for dup_id in duplicate_ids_to_remove:
                    cur.execute("DELETE FROM questions WHERE id = %s", (dup_id,))
                    questions_deleted += 1
                    print(f"   ❌ Deleted duplicate question ID {dup_id}")

            print(f"\n✅ Phase 1 Complete:")
            print(f"   📤 Responses moved: {responses_moved}")
            print(f"   ❌ Questions deleted: {questions_deleted}")

            # Add new engaging hobby questions
            print(f"\n🌟 Adding engaging hobby and interest questions...")
            new_questions = generate_engaging_hobby_questions()

            # Get current max ID
            cur.execute("SELECT MAX(id) FROM questions")
            max_id = cur.fetchone()['max'] or 0

            added_count = 0
            for question_text in new_questions:
                # Check if question already exists
                cur.execute(
                    "SELECT COUNT(*) FROM questions WHERE question_text = %s",
                    (question_text,)
                )

                if cur.fetchone()['count'] == 0:
                    max_id += 1
                    cur.execute("""
                        INSERT INTO questions (id, question_text, category)
                        VALUES (%s, %s, 'hobbies')
                    """, (max_id, question_text))
                    added_count += 1
                else:
                    print(f"   ⚠️  Skipped duplicate: {question_text[:50]}...")

            print(f"   ✨ Added {added_count} new engaging questions")

            # Commit all changes
            conn.commit()

            # Final verification
            cur.execute("""
                SELECT COUNT(*) as total_questions,
                       COUNT(DISTINCT question_text) as unique_questions
                FROM questions
                WHERE category = 'hobbies'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 HOBBIES CLEANUP COMPLETE!")
            print(f"   📊 Final count: {final_stats['total_questions']} questions")
            print(f"   ✅ All unique: {final_stats['unique_questions']} questions")
            print(f"   📤 User responses preserved: {responses_moved}")
            print(f"   🆕 New engaging questions added: {added_count}")

            if final_stats['total_questions'] == final_stats['unique_questions']:
                print("   ✨ SUCCESS: No duplicates remain!")
            else:
                print("   ⚠️  WARNING: Some duplicates may still exist")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    clean_hobbies()