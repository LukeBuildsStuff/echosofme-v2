#!/usr/bin/env python3
"""
Clean marriage_partnerships category duplicates and add engaging partnership questions
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

def generate_engaging_marriage_partnership_questions():
    """Generate 45 raw, honest questions about the unspoken realities of marriage and partnerships"""
    return [
        # The Unspoken Truths
        "What resentment do you harbor that you've never fully expressed to your partner?",
        "What aspect of your partner did you hope would change but never has?",
        "What dealbreaker are you pretending isn't a dealbreaker?",
        "What version of yourself do you suppress to keep the peace?",
        "What about your partner annoys you more now than when you first met?",
        "What compromise in your relationship do you regret making?",
        "What truth about your relationship would shock people who know you?",
        "What pattern in your relationship do you recognize but feel powerless to change?",
        "What aspect of your partner's personality do you find increasingly difficult to tolerate?",
        "What relationship expectation have you quietly abandoned?",

        # Sexual & Intimate Realities
        "What sexual need goes unmet in your relationship?",
        "What intimate connection did you have with someone else that you wish you had with your partner?",
        "What physical attraction has faded that you don't know how to address?",
        "What sexual fantasy do you keep to yourself because it involves someone else?",
        "What intimacy issue do you avoid discussing because it feels too vulnerable?",
        "What physical aspect of your relationship has become routine in a way that disappoints you?",
        "What sexual expectation do you have that feels impossible to communicate?",
        "What intimate moment with your partner do you wish you could recreate but can't?",

        # Financial Tensions
        "What financial decision does your partner make that secretly infuriates you?",
        "What money secret are you keeping from your partner?",
        "What lifestyle sacrifice do you resent making for the relationship?",
        "What financial goal of yours conflicts with your partner's priorities?",
        "What money-related habit of your partner's do you find irresponsible?",
        "What financial stress are you carrying alone to protect your partner?",
        "What economic disparity between you and your partner creates hidden tension?",

        # Emotional Labor Imbalances
        "What emotional burden do you carry alone in your relationship?",
        "What invisible work do you do that your partner doesn't acknowledge?",
        "What mental load exhausts you that your partner doesn't even notice?",
        "What emotional support do you provide that you don't receive in return?",
        "What relationship maintenance falls entirely on your shoulders?",
        "What emotional labor do you perform that you wish your partner would share?",
        "What family or social responsibility do you handle solo despite it affecting both of you?",

        # Doubts & What-Ifs
        "What alternative life do you sometimes imagine without your partner?",
        "What ex still occupies mental space you don't admit to?",
        "What opportunity did you sacrifice for this relationship that you sometimes regret?",
        "What person in your life represents a path not taken that still appeals to you?",
        "What relationship timeline pressure do you feel that creates internal conflict?",
        "What independence did you give up that you miss more than you expected?",
        "What dream did you modify or abandon to accommodate your partner's needs?",

        # Power Dynamics
        "What decision-making power imbalance exists in your relationship?",
        "What do you comply with to avoid conflict rather than from agreement?",
        "What control does your partner exert that you've normalized but shouldn't have?",
        "What area of your life does your partner influence more than they should?",
        "What boundary of yours gets crossed regularly without consequence?",
        "What manipulation tactic does your partner use that you recognize but don't address?",
        "What way does your partner make you feel small that you haven't confronted?",

        # Growth and Stagnation
        "What personal growth has your relationship prevented rather than supported?",
        "What version of yourself emerged in this relationship that you don't particularly like?",
        "What aspect of your identity have you compromised to fit your partner's preferences?",
        "What potential in yourself do you feel your partner doesn't see or encourage?"
    ]

def clean_marriage_partnerships():
    """Clean marriage_partnerships category duplicates and add engaging questions"""
    print("🧹 Cleaning marriage_partnerships category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all marriage_partnerships questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'marriage_partnerships'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} marriage_partnerships questions")

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
                print(f"\n📝 Duplicate question:")
                for text, ids in duplicate_groups.items():
                    print(f"   [{len(ids)} copies] {text}")
                    print(f"   IDs: {ids}")

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

            # Add new engaging marriage & partnership questions
            print(f"\n🌟 Adding engaging marriage and partnership questions...")
            new_questions = generate_engaging_marriage_partnership_questions()

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
                        VALUES (%s, %s, 'marriage_partnerships')
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
                WHERE category = 'marriage_partnerships'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 MARRIAGE & PARTNERSHIPS CLEANUP COMPLETE!")
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
    clean_marriage_partnerships()