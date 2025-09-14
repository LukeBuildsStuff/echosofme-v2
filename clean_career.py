#!/usr/bin/env python3
"""
Clean career category duplicates and add engaging career questions
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

def generate_engaging_career_questions():
    """Generate 50 thought-provoking career and work questions"""
    return [
        # Career Regrets & What-Ifs
        "What career path did you abandon that sometimes haunts you?",
        "What professional opportunity do you regret not taking?",
        "What industry did you almost enter that you wonder about?",
        "What career decision do you wish you could undo?",
        "What professional risk were you too scared to take?",
        "What job offer did you turn down that you now regret?",
        "What career advice did you ignore that you wish you'd followed?",
        "What professional relationship did you let slip away?",
        "What skill did you not develop when you had the chance?",
        "What career move did you make for the wrong reasons?",

        # Work Identity Crisis
        "What professional mask exhausts you the most to wear?",
        "What part of your job conflicts with your personal values?",
        "What workplace expectation feels impossible to meet authentically?",
        "What professional persona do you perform that isn't really you?",
        "What aspect of your career makes you feel like an imposter?",
        "What work achievement felt hollow when you accomplished it?",
        "What part of your professional identity do you want to shed?",
        "What career success came at too high a personal cost?",
        "What professional standard do you hold yourself to that's unrealistic?",
        "What workplace role do you play that drains your energy?",

        # Career Sacrifices & Trade-offs
        "What did you sacrifice for your career that you can't get back?",
        "What personal relationship suffered because of your work ambitions?",
        "What part of yourself did you compromise to succeed professionally?",
        "What principle did you bend to advance your career?",
        "What dream did you defer for practical career considerations?",
        "What aspect of work-life balance do you struggle with most?",
        "What personal interest did you abandon for professional growth?",
        "What family moment did you miss for work that you regret?",
        "What health consequence have you experienced from career stress?",
        "What friendship ended because of professional competition?",

        # Workplace Politics & Unwritten Rules
        "What workplace dynamic makes you question your career choices?",
        "What unwritten rule at work do you refuse to follow?",
        "What office politics situation taught you the most about human nature?",
        "What workplace inequality have you witnessed that bothers you?",
        "What professional boundary do you wish you'd set earlier?",
        "What workplace behavior do you see rewarded that shouldn't be?",
        "What career advice do you give but don't follow yourself?",
        "What workplace relationship complicated your professional life?",
        "What office culture norm makes you feel like an outsider?",
        "What professional conflict are you avoiding that you should address?",

        # Success, Fulfillment & Meaning
        "What success of yours feels hollow when you really think about it?",
        "What promotion felt like a loss disguised as a win?",
        "What professional achievement impressed others but disappointed you?",
        "What aspect of your current job makes you lose sight of why you started?",
        "What career milestone felt anticlimactic when you reached it?",
        "What work accomplishment do you wish your younger self could see?",
        "What professional legacy do you want to leave but aren't building?",
        "What career goal did you achieve only to realize it wasn't what you wanted?",
        "What aspect of your work gives you the most genuine satisfaction?",
        "What professional impact do you hope to have beyond making money?"
    ]

def clean_career():
    """Clean career category duplicates and add engaging questions"""
    print("🧹 Cleaning career category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all career questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'career'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} career questions")

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

            # Add new engaging career questions
            print(f"\n🌟 Adding engaging career and work questions...")
            new_questions = generate_engaging_career_questions()

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
                        VALUES (%s, %s, 'career')
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
                WHERE category = 'career'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 CAREER CLEANUP COMPLETE!")
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
    clean_career()