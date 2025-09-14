#!/usr/bin/env python3
"""
Clean hypotheticals category duplicates and add engaging hypothetical questions
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

def generate_engaging_hypothetical_questions():
    """Generate 60 thought-provoking hypothetical questions that reveal character and challenge assumptions"""
    return [
        # Moral Dilemmas That Reveal Character
        "Would you betray your best friend to save a stranger's life?",
        "If you could prevent a tragedy by ruining an innocent person's reputation, would you?",
        "Would you steal medicine to save your child if you couldn't afford it?",
        "If you witnessed your boss commit a crime, would you report them knowing you'd lose your job?",
        "Would you lie to protect someone you love from a painful truth?",
        "If you could erase one person's memory to prevent them from suffering, would you?",
        "Would you sacrifice your own happiness to ensure your parent's approval?",
        "If telling the truth would destroy your family, would you still do it?",
        "Would you choose to save 10 strangers or 1 person you love?",
        "If you could prevent your own future heartbreak by causing someone else's, would you?",

        # Uncomfortable "Would You Rather" Scenarios
        "Would you rather live knowing everyone's true opinion of you or never know what anyone really thinks?",
        "Would you rather have everyone you've ever loved forget you or remember only the worst version of yourself?",
        "Would you rather relive your most embarrassing moment daily or never feel embarrassment again but lose all empathy?",
        "Would you rather know the exact date of your death or the exact cause?",
        "Would you rather be able to change your past but lose all your current relationships, or keep everything but never change anything?",
        "Would you rather have your thoughts broadcast to everyone or never be able to express yourself again?",
        "Would you rather be genuinely happy but completely ordinary, or miserable but extraordinarily accomplished?",
        "Would you rather have everyone always lie to you or never be able to trust anyone again?",
        "Would you rather lose all your memories after age 18 or before age 18?",
        "Would you rather be feared by everyone you love or ignored by everyone you respect?",

        # Reality-Bending Thought Experiments
        "If you discovered your entire life was a simulation, would you choose to stay or exit to an unknown reality?",
        "If you could restart your life with all your current knowledge, would you make the same major decisions?",
        "If everyone else disappeared and you were alone forever, how would you spend your time?",
        "If you could experience someone else's entire life in a dream, whose would you choose?",
        "If you could eliminate one human emotion from existence, which would cause the most change?",
        "If you could choose to be reborn as any person in history, would you stay as yourself?",
        "If you could know the answer to any question but never share it, what would you ask?",
        "If you had to choose one day to relive forever, which day would it be?",
        "If you could observe but not change any moment in history, what would you watch?",
        "If you could switch lives with someone for exactly one year, who would it be?",

        # Dark Hypotheticals About Human Nature
        "What would you do if laws didn't exist for 24 hours?",
        "If everyone's internet history became public, whose would surprise you most?",
        "What secret would ruin your life if it came out tomorrow?",
        "If you could get away with one crime perfectly, what would tempt you most?",
        "What would you sacrifice to guarantee your deepest insecurity was never exposed?",
        "If you could make one person disappear from existence without consequences, would you?",
        "What lie do you tell yourself that you know isn't true?",
        "If you could read minds but couldn't turn it off, would you want that power?",
        "What would you do if you discovered you were the villain in someone else's story?",
        "If everyone acted exactly like you, what would the world look like?",

        # Personal Sacrifice Scenarios
        "Would you give up your best memory to erase your worst one?",
        "If you could guarantee world peace but had to live in solitary confinement forever, would you?",
        "Would you accept never falling in love again to ensure you never experience heartbreak?",
        "If you could cure all disease but had to sacrifice your ability to feel joy, would you?",
        "Would you give up all your possessions to guarantee your loved ones' safety?",
        "If you could end all suffering but had to experience everyone's worst pain first, would you?",
        "Would you trade 20 years of your life to prevent a loved one's death?",
        "If you could eliminate poverty by giving up your ability to feel pleasure, would you?",
        "Would you accept blindness to give sight to someone born without it?",
        "If saving humanity required you to be forgotten by everyone you've ever known, would you do it?",

        # Power and Corruption Questions
        "If you became dictator of the world, what would you change first?",
        "What would you do if you inherited unlimited wealth but it came from immoral sources?",
        "If you could control one person completely for a day, who would it be and what would you make them do?",
        "What power would corrupt you fastest if you possessed it?",
        "If you could make one law that everyone had to follow, what would it be?",
        "Would you accept a position of great power knowing it would change you for the worse?",
        "If you could decide who gets to reproduce, would you want that responsibility?",
        "What would you do if you discovered you could manipulate anyone's emotions?",
        "If you had infinite resources, what would you be tempted to do that you know is wrong?",
        "Would you rule through fear if it created a safer world for everyone?"
    ]

def clean_hypotheticals():
    """Clean hypotheticals category duplicates and add engaging questions"""
    print("🧹 Cleaning hypotheticals category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all hypotheticals questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'hypotheticals'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} hypotheticals questions")

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
            print(f"\n📝 Top 5 most duplicated questions:")
            for text, ids in sorted(duplicate_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
                print(f"   [{len(ids)} copies] {text[:60]}...")

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

            # Add new engaging hypothetical questions
            print(f"\n🌟 Adding engaging hypothetical and thought experiment questions...")
            new_questions = generate_engaging_hypothetical_questions()

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
                        VALUES (%s, %s, 'hypotheticals')
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
                WHERE category = 'hypotheticals'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 HYPOTHETICALS CLEANUP COMPLETE!")
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
    clean_hypotheticals()