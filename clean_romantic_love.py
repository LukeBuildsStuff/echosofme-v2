#!/usr/bin/env python3
"""
Clean romantic_love category duplicates and add engaging romantic love questions
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

def generate_engaging_romantic_love_questions():
    """Generate 60 thought-provoking questions about the uncomfortable truths of romantic love"""
    return [
        # Uncomfortable Truths About Romantic Love
        "What romantic fantasy are you afraid to let go of?",
        "What do you pretend to feel in relationships that you don't actually feel?",
        "What aspect of love disappoints you that you don't admit to anyone?",
        "What romantic lie do you keep telling yourself?",
        "What part of being in love feels like performing rather than being authentic?",
        "What do you sacrifice of yourself to be loveable to others?",
        "What romantic expectation has consistently let you down?",
        "What do you find exhausting about romantic relationships?",
        "What aspect of love makes you feel most vulnerable in an uncomfortable way?",
        "What romantic pattern do you repeat despite knowing it's unhealthy?",

        # Love's Contradictions and Paradoxes
        "What do you love and hate about the same person?",
        "How do you reconcile wanting independence while craving connection?",
        "What romantic desire conflicts with your other values?",
        "What do you want from love that you judge others for wanting?",
        "How do you handle loving someone more than they love you?",
        "What aspect of love feels both necessary and suffocating?",
        "What romantic truth would hurt your partner but might help your relationship?",
        "How do you balance being yourself with being who your partner needs?",
        "What part of love requires you to be someone you're not sure you want to be?",
        "What romantic compromise feels like losing yourself?",

        # Romantic Delusions vs Reality
        "What romantic story do you tell about your relationship that isn't entirely true?",
        "What red flag did you ignore because you were in love?",
        "What did you think love would fix about you that it hasn't?",
        "What romantic expectation from media has damaged your real relationships?",
        "What do you wish someone had told you about love before you experienced it?",
        "What romantic advice sounds good but doesn't work in practice?",
        "What love song or movie represents everything wrong with how we think about love?",
        "What aspect of your romantic life looks nothing like what you imagined?",
        "What romantic milestone felt anticlimactic when you reached it?",
        "What part of being in love is nothing like the stories we're told?",

        # Heartbreak and Loss
        "What heartbreak changed you in ways you didn't expect?",
        "What relationship ending do you still don't fully understand?",
        "What person did you love who was completely wrong for you?",
        "What breakup revealed something about yourself you didn't want to know?",
        "What lost love do you idealize that probably wasn't as perfect as you remember?",
        "What relationship do you grieve that others wouldn't understand?",
        "What part of yourself did you lose in a relationship that you never got back?",
        "What do you miss about being heartbroken that you can't admit?",
        "What ex do you compare everyone else to unfairly?",
        "What ended relationship still affects how you love now?",

        # Toxic Patterns in Love
        "What unhealthy thing do you do when you're in love?",
        "What toxic behavior do you excuse in relationships because of love?",
        "What self-destructive pattern shows up in every relationship?",
        "What do you become in romantic relationships that you don't like about yourself?",
        "What boundary do you consistently cross when you're in love?",
        "What warning signs do you ignore when you're romantically interested in someone?",
        "What part of yourself do you hide to keep someone's love?",
        "What do you tolerate in romantic relationships that you wouldn't tolerate elsewhere?",
        "What jealousy or possessiveness do you struggle with in love?",
        "What way of loving hurts both you and your partner?",

        # Sexual Vulnerability and Intimacy
        "What aspect of physical intimacy makes you feel most emotionally exposed?",
        "What do you wish you could communicate about sex but struggle to express?",
        "What sexual insecurity affects your romantic relationships?",
        "What intimate moment made you feel most vulnerable with someone?",
        "What do you pretend to want sexually to please someone you love?",
        "What aspect of physical intimacy do you find more difficult than expected?",
        "What sexual experience changed how you think about love?",
        "What do you wish your partner understood about your physical needs?",
        "What intimate boundary do you struggle to maintain?",
        "What aspect of sexual connection feels most emotionally risky to you?"
    ]

def clean_romantic_love():
    """Clean romantic_love category duplicates and add engaging questions"""
    print("🧹 Cleaning romantic_love category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all romantic_love questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'romantic_love'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} romantic_love questions")

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

            # Show the massive duplication
            if duplicate_groups:
                for text, ids in sorted(duplicate_groups.items(), key=lambda x: len(x[1]), reverse=True):
                    print(f"\n📝 MASSIVE DUPLICATION FOUND:")
                    print(f"   [{len(ids)} copies] {text}")

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

                # Delete duplicate questions in batches for efficiency
                if duplicate_ids_to_remove:
                    ids_to_delete = ','.join(map(str, duplicate_ids_to_remove))
                    cur.execute(f"DELETE FROM questions WHERE id IN ({ids_to_delete})")
                    questions_deleted += len(duplicate_ids_to_remove)
                    print(f"   ❌ Deleted {len(duplicate_ids_to_remove)} duplicate questions")

            print(f"\n✅ Phase 1 Complete:")
            print(f"   📤 Responses moved: {responses_moved}")
            print(f"   ❌ Questions deleted: {questions_deleted}")

            # Add new engaging romantic love questions
            print(f"\n🌟 Adding engaging romantic love and relationship questions...")
            new_questions = generate_engaging_romantic_love_questions()

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
                        VALUES (%s, %s, 'romantic_love')
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
                WHERE category = 'romantic_love'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 ROMANTIC LOVE CLEANUP COMPLETE!")
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
    clean_romantic_love()