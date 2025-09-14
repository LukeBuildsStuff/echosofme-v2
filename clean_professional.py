#!/usr/bin/env python3
"""
Clean professional category duplicates and add engaging professional development questions
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

def generate_engaging_professional_questions():
    """Generate 45 raw, honest questions about the uncomfortable realities of professional life"""
    return [
        # Career Regrets & Mistakes
        "What career decision do you regret but can't undo?",
        "What professional bridge did you burn that still affects you?",
        "What career advice did you ignore that you wish you'd taken?",
        "What opportunity did you let slip away out of fear?",
        "What professional relationship did you mishandle that cost you?",
        "What career path did you abandon that you still wonder about?",
        "What professional mistake keeps you awake at night?",
        "What job did you quit too hastily and later regret?",

        # Workplace Politics & Power
        "What office politics game do you play despite hating it?",
        "What professional relationship do you maintain purely for strategic reasons?",
        "What workplace injustice do you tolerate to keep your job?",
        "What unethical behavior have you witnessed but stayed silent about?",
        "What political alliance at work goes against your values?",
        "What workplace discrimination have you ignored to avoid conflict?",
        "What unfair advantage do you have that you don't acknowledge?",
        "What corrupt practice in your industry do you participate in?",

        # Imposter Syndrome & Insecurity
        "What professional skill do you fake having?",
        "What achievement feels undeserved when you think about it?",
        "What expertise do people credit you with that you know is shallow?",
        "What professional confidence do you perform but don't feel?",
        "What industry knowledge gap are you desperately trying to hide?",
        "What professional reputation do you fear is built on false premises?",
        "What competency do you bluff your way through daily?",
        "What career success do you attribute more to luck than skill?",

        # Work-Life Deception
        "What work-life balance lie do you tell yourself?",
        "What personal sacrifice for work do you pretend was worth it?",
        "What professional success came at too high a personal cost?",
        "What family moment did you miss that you can't get back?",
        "What health issue are you ignoring for your career?",
        "What relationship did your career ambition damage?",
        "What personal value have you compromised for professional gain?",
        "What life experience are you postponing indefinitely for work?",

        # Ethical Compromises
        "What ethical line have you crossed for professional advancement?",
        "What principle did you abandon when money was on the table?",
        "What lie have you told that benefited your career?",
        "What corner did you cut that you hope no one discovers?",
        "What unethical request from a boss did you comply with?",
        "What moral compromise do you rationalize as 'just business'?",
        "What professional betrayal are you capable of if pushed?",

        # Career Stagnation & Fear
        "What professional dream have you quietly given up on?",
        "What career pivot are you too scared to attempt?",
        "What comfort zone is killing your professional growth?",
        "What risk would advance your career but terrifies you?",
        "What professional limitation have you accepted as permanent?",
        "What industry change are you too afraid to adapt to?",
        "What career leap do you want to make but lack courage for?",
        "What professional routine has become a prison you won't escape?"
    ]

def clean_professional():
    """Clean professional category duplicates and add engaging questions"""
    print("🧹 Cleaning professional category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all professional questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'professional'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} professional questions")

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

            # Show duplicate details
            if duplicate_groups:
                print(f"\n📝 Duplicate questions:")
                for text, ids in sorted(duplicate_groups.items(), key=lambda x: len(x[1]), reverse=True):
                    print(f"   [{len(ids)} copies] {text[:60]}...")
                    print(f"   IDs: {ids[:10]}{'...' if len(ids) > 10 else ''}")

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

            # Add new engaging professional questions
            print(f"\n🌟 Adding engaging professional development questions...")
            new_questions = generate_engaging_professional_questions()

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
                        VALUES (%s, %s, 'professional')
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
                WHERE category = 'professional'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 PROFESSIONAL CATEGORY CLEANUP COMPLETE!")
            print(f"   📊 Final count: {final_stats['total_questions']} questions")
            print(f"   ✅ All unique: {final_stats['unique_questions']} questions")
            print(f"   📤 User responses preserved: {responses_moved}")
            print(f"   🆕 New engaging questions added: {added_count}")
            print(f"   🗑️  Duplicates removed: {questions_deleted}")

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
    clean_professional()