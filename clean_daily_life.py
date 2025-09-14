#!/usr/bin/env python3
"""
Clean daily_life category duplicates and add engaging daily life questions
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

def generate_engaging_daily_life_questions():
    """Generate 80 thought-provoking questions about the honest realities of daily life"""
    return [
        # Hidden Daily Rituals & Secret Routines
        "What daily ritual do you never tell anyone about?",
        "What weird thing do you do when you're completely alone?",
        "What daily habit would embarrass you if people knew about it?",
        "What comfort routine do you refuse to give up despite judgment?",
        "What secret daily indulgence do you justify to yourself?",
        "What daily ritual makes you feel like you're taking care of yourself?",
        "What morning habit sets the tone for your entire day?",
        "What bedtime routine calms your mind when nothing else will?",
        "What daily practice do you do that your past self would judge?",
        "What routine do you perform that connects you to your childhood?",

        # The Gap Between Ideal vs Actual Daily Life
        "What daily routine do you wish you had but can't seem to maintain?",
        "What aspect of your daily life looks nothing like what you planned?",
        "What daily habit did you think would change your life but didn't?",
        "What part of your ideal day never actually happens?",
        "What daily goal do you set every morning but rarely achieve?",
        "What aspect of your routine makes you feel like you're failing at life?",
        "What daily practice do you know you should do but avoid?",
        "What healthy habit have you tried to start dozens of times?",
        "What daily activity do you do out of guilt rather than choice?",
        "What routine change would dramatically improve your life but feels impossible?",

        # Small Daily Lies & Compromises
        "What do you pretend to enjoy in your daily routine?",
        "What daily compromise with yourself makes you feel defeated?",
        "What small daily choice consistently disappoints you?",
        "What do you tell yourself every day that you know isn't true?",
        "What daily decision do you make that conflicts with your values?",
        "What aspect of your routine do you perform for others' approval?",
        "What daily habit do you maintain just to avoid judgment?",
        "What part of your day do you spend pretending to be someone else?",
        "What daily activity drains your energy but you can't stop doing?",
        "What routine makes you feel authentic versus performative?",

        # Procrastination Patterns & Avoidance Behaviors
        "What daily task do you procrastinate on that would take 5 minutes?",
        "What do you do instead of the thing you know you should be doing?",
        "What daily responsibility makes you want to hide under the covers?",
        "What simple daily task feels insurmountable to you?",
        "What do you avoid doing that accumulates into bigger problems?",
        "What daily activity do you dread for no rational reason?",
        "What task do you put off until the absolute last possible moment?",
        "What daily chore makes you question your life choices?",
        "What simple habit would solve problems but you won't do it?",
        "What daily avoidance pattern costs you more energy than just doing it?",

        # Daily Masks & Performance
        "What personality do you wear during different parts of your day?",
        "What daily social interaction exhausts you the most?",
        "What part of your day requires the most emotional labor?",
        "What daily conversation do you have on autopilot?",
        "What aspect of your daily life feels like performing a role?",
        "What daily social expectation do you resent meeting?",
        "What part of your routine makes you feel most like yourself?",
        "What daily interaction makes you feel misunderstood?",
        "What social routine do you go through that feels meaningless?",
        "What daily behavior do you perform to keep the peace?",

        # Time Wasters vs Time Treasures
        "What daily time-waster do you refuse to feel guilty about?",
        "What do you spend too much time on but can't seem to stop?",
        "What daily activity makes you lose track of time in the best way?",
        "What mindless daily habit consumes more time than you'd admit?",
        "What daily moment do you always rush through but shouldn't?",
        "What part of your day feels like stolen time that's just for you?",
        "What daily activity do you do that feels like a complete waste?",
        "What routine gives you energy versus drains it?",
        "What daily practice makes you feel connected to something larger?",
        "What small daily pleasure do you never allow yourself enough of?",

        # Daily Anxieties & Micro-Stresses
        "What small daily decision causes you disproportionate anxiety?",
        "What daily worry occupies your mind but you never voice?",
        "What routine interaction makes you more nervous than it should?",
        "What daily responsibility weighs on you throughout the day?",
        "What aspect of your daily life makes you feel like you're behind?",
        "What daily task triggers your perfectionism in an unhealthy way?",
        "What small daily failure makes you question everything else?",
        "What routine creates more stress than it should logically cause?",
        "What daily comparison steals your peace of mind?",
        "What aspect of your routine makes you feel inadequate?",

        # Comfort Zones & Daily Escapes
        "What daily escape do you use when reality feels too heavy?",
        "What comfort zone do you retreat to when you're overwhelmed?",
        "What daily distraction do you use to avoid difficult emotions?",
        "What routine helps you feel safe when the world feels chaotic?",
        "What daily practice grounds you when anxiety takes over?",
        "What small daily pleasure helps you cope with bigger problems?",
        "What routine do you do when you need to feel in control?",
        "What daily habit serves as your emotional regulation?",
        "What part of your day do you use to process difficult experiences?",
        "What daily ritual helps you feel connected to who you really are?"
    ]

def clean_daily_life():
    """Clean daily_life category duplicates and add engaging questions"""
    print("🧹 Cleaning daily_life category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all daily_life questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'daily_life'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} daily_life questions")

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

            # Add new engaging daily life questions
            print(f"\n🌟 Adding engaging daily life and routine questions...")
            new_questions = generate_engaging_daily_life_questions()

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
                        VALUES (%s, %s, 'daily_life')
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
                WHERE category = 'daily_life'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 DAILY LIFE CLEANUP COMPLETE!")
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
    clean_daily_life()