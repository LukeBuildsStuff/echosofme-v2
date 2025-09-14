#!/usr/bin/env python3
"""
Clean personal_history category duplicates and generate engaging life history and memory questions
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

def generate_engaging_memory_questions():
    """Generate 100+ deeply engaging life history and memory questions"""
    return [
        # Sensory Memories & Triggers
        "What sound instantly transports you to a specific moment in your past?",
        "What taste brings back your strongest childhood memory?",
        "What texture reminds you of someone you've lost?",
        "What fragrance makes you feel like you're home again?",
        "What song makes you remember exactly where you were when you first heard it?",
        "What visual triggers a memory so vivid it feels like time travel?",
        "What physical sensation takes you back to being a child?",
        "What flavor combination exists nowhere but in your memory?",
        "What weather condition brings back your most peaceful memory?",
        "What everyday object holds an entire story from your past?",

        # Forgotten & Resurfaced Memories
        "What memory surprised you by suddenly returning after years of forgetting?",
        "What moment from your past feels like it happened to someone else?",
        "What memory do you wish you could experience again with your current awareness?",
        "What detail from a childhood memory turned out to be completely wrong?",
        "What memory feels more vivid now than it did when it happened?",
        "What forgotten moment would your family be surprised you remember?",
        "What memory came back to you in a dream and felt more real than reality?",
        "What childhood fear do you remember with perfect clarity?",
        "What moment of pure joy have you almost forgotten but desperately want to preserve?",
        "What memory do you return to when you need to feel brave?",

        # Emotional Imprints & Life-Changing Moments
        "What ordinary Tuesday changed the entire direction of your life?",
        "What moment made you realize you weren't a child anymore?",
        "What conversation with a stranger affected you more than they'll ever know?",
        "What memory makes you feel most grateful for the life you've lived?",
        "What moment of kindness from someone unexpected still warms your heart?",
        "What experience taught you that people are more complex than you thought?",
        "What moment of your own courage surprises you when you think about it?",
        "What memory reminds you of your own resilience?",
        "What moment showed you what unconditional love actually feels like?",
        "What experience changed how you see your parents as people?",

        # Memory Evolution & Changing Perspectives
        "What memory has completely changed meaning as you've gotten older?",
        "What childhood trauma do you now understand from the adult's perspective?",
        "What happy memory now makes you sad, and why?",
        "What embarrassing moment from your past now makes you proud?",
        "What memory do you remember differently than everyone else who was there?",
        "What story from your past sounds unbelievable when you tell it now?",
        "What moment that seemed devastating at the time now seems like a blessing?",
        "What memory of your parents do you finally understand now that you're older?",
        "What childhood certainty do you remember losing, and when?",
        "What moment revealed that an adult you trusted was just winging it too?",

        # Mundane Magic & Ordinary Extraordinary
        "What completely ordinary day from your childhood feels magical in memory?",
        "What routine from your past do you miss more than you expected?",
        "What simple pleasure from childhood can you no longer access?",
        "What everyday moment with someone you've lost has become precious?",
        "What boring family tradition do you now wish you'd paid more attention to?",
        "What mundane conversation turned out to be the last one with someone important?",
        "What ordinary object from your childhood home do you wish you still had?",
        "What simple ritual from your past brought you comfort you didn't recognize then?",
        "What unremarkable day with a friend now represents your entire friendship?",
        "What routine interaction with a neighbor or cashier do you miss?",

        # Memory Gaps & What You Wish You Remembered
        "What moment do you wish you had been more present for?",
        "What person from your past do you wish you'd asked more questions?",
        "What phase of your life feels like a blur that you'd like to remember better?",
        "What conversation do you wish you could replay to hear what you missed?",
        "What moment of your parents' lives do you wish you'd witnessed?",
        "What experience did you not realize was important until it was too late?",
        "What person's voice can you no longer remember, and it breaks your heart?",
        "What tradition ended without you realizing it was the last time?",
        "What moment of someone's pride in you do you wish you'd absorbed better?",
        "What phase of a relationship do you wish you'd savored instead of rushed through?",

        # Collective Memories & Shared Experiences
        "What shared family memory do you all remember differently?",
        "What group experience created a bond that still exists today?",
        "What collective trauma brought your community together?",
        "What celebration involved everyone you cared about in one place?",
        "What shared secret with siblings still makes you laugh?",
        "What family crisis revealed everyone's true character?",
        "What tradition created the feeling that you truly belonged somewhere?",
        "What shared adventure with friends feels like it happened to characters in a movie?",
        "What group experience taught you something about loyalty?",
        "What collective memory does your generation share that younger people won't understand?",

        # Memory Artifacts & Objects That Hold Stories
        "What object from your past holds an entire relationship?",
        "What possession of a deceased loved one makes you feel their presence?",
        "What childhood toy represented more than just play to you?",
        "What piece of clothing holds a memory you can't let go of?",
        "What book from your past contains more than just the story on its pages?",
        "What photograph captures a feeling that words never could?",
        "What handwritten note do you keep because of what it represents?",
        "What broken thing do you keep because of the memory it holds?",
        "What gift received or given carries the weight of an entire relationship?",
        "What ordinary household object tells the story of your family?",

        # Time, Identity & Personal Evolution Through Memory
        "What memory makes you feel most connected to your younger self?",
        "What moment from your past shows you've become exactly who you needed to be?",
        "What memory proves you were braver than you gave yourself credit for?",
        "What experience from your past explains a quirk you have today?",
        "What childhood dream have you never told anyone about?",
        "What moment of your past would you want to tell your current self about?",
        "What memory shows the moment you started becoming who you are now?",
        "What experience taught you something about yourself that you still rely on?",
        "What memory makes you proud of how far you've come?",
        "What moment from your past do you finally understand was actually perfect?",

        # Dreams, Imagination & the Line Between Memory and Fantasy
        "What memory feels too perfect to have actually happened?",
        "What childhood 'memory' might actually have been a vivid dream?",
        "What story told to you so many times feels like your own memory?",
        "What imagined scenario from childhood still influences your decisions?",
        "What daydream from your past came true in an unexpected way?",
        "What 'what if' scenario from your past do you still think about?",
        "What alternative version of a memory do you sometimes prefer?",
        "What moment do you remember that cameras or witnesses say happened differently?",
        "What memory have you embellished so much it's become its own story?",
        "What dream from childhood do you remember better than most real experiences?"
    ]

def clean_personal_history():
    """Clean personal_history category duplicates and add engaging questions"""
    print("🧹 Cleaning personal_history category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all personal_history questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'personal_history'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} personal_history questions")

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
            print("\n📝 Top duplicate groups:")
            for text, ids in sorted(duplicate_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
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

            # Add new engaging memory questions
            print(f"\n🌟 Adding engaging memory and life history questions...")
            new_questions = generate_engaging_memory_questions()

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
                        VALUES (%s, %s, 'personal_history')
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
                WHERE category = 'personal_history'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 PERSONAL_HISTORY CLEANUP COMPLETE!")
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
    clean_personal_history()