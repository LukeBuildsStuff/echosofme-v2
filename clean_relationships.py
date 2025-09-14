#!/usr/bin/env python3
"""
Clean relationships category duplicates and add engaging relationship questions
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

def generate_engaging_relationship_questions():
    """Generate 60 deeply engaging relationship questions about the messy realities of human connections"""
    return [
        # Relationship Ghosts & Unfinished Business
        "What person do you miss who probably doesn't think about you?",
        "What conversation do you wish you could have with someone from your past?",
        "What relationship ended in a way that still bothers you?",
        "What person did you let slip away without fighting for them?",
        "What love did you not recognize until it was gone?",
        "What friendship do you mourn that others wouldn't understand?",
        "What relationship ghost appears when you least expect it?",
        "What person shaped you more than they'll ever know?",
        "What connection felt incomplete in a way that haunts you?",
        "What relationship do you idealize that was probably flawed?",

        # Toxic Patterns & Self-Sabotage
        "What relationship pattern do you keep repeating despite knowing better?",
        "What unhealthy dynamic do you find yourself gravitating toward?",
        "What relationship role exhausts you but you can't stop playing?",
        "What family dynamic do you perpetuate despite not liking it?",
        "What way of loving hurts both you and the other person?",
        "What relationship boundary do you struggle to maintain?",
        "What self-sabotaging behavior ruins your connections?",
        "What insecurity do you project onto your relationships?",
        "What defense mechanism damages your closest relationships?",
        "What relationship fear becomes a self-fulfilling prophecy?",

        # Unspoken Truths & Hidden Needs
        "What truth about a relationship are you avoiding?",
        "What do you need from relationships that you're afraid to ask for?",
        "What do you pretend to be okay with in your relationships?",
        "What relationship need do you meet through unhealthy means?",
        "What do you give in relationships hoping to get something back?",
        "What relationship truth would hurt people you care about?",
        "What do you secretly resent about someone you love?",
        "What emotional labor do you provide that goes unrecognized?",
        "What relationship standard do you have that you don't communicate?",
        "What do you sacrifice for others that they don't appreciate?",

        # Connection Paradoxes & Complicated Feelings
        "What relationship are you holding onto that you should let go?",
        "What person do you love in a way that doesn't serve either of you?",
        "What connection feels both necessary and toxic?",
        "What relationship makes you feel more alone than being alone?",
        "What person brings out the worst in you despite your best intentions?",
        "What relationship feels like work when it should feel easy?",
        "What connection do you value more than the other person does?",
        "What relationship do you stay in out of obligation rather than love?",
        "What person do you care about who consistently disappoints you?",
        "What relationship dynamic confuses even you?",

        # Love vs Reality & Relationship Disillusionment
        "What romantic expectation has reality consistently failed to meet?",
        "What relationship advice sounds good but doesn't work in practice?",
        "What about love disappoints you that you don't admit?",
        "What relationship myth did you believe that hurt you?",
        "What do you find exhausting about maintaining relationships?",
        "What aspect of love feels more like performance than authenticity?",
        "What relationship skill do you wish came more naturally?",
        "What do you fake in relationships to keep the peace?",
        "What relationship reality conflicts with your ideals?",
        "What about human connection feels harder as you get older?",

        # Relationship Regrets & Missed Opportunities
        "What relationship did you take for granted until it was too late?",
        "What person did you hurt in a way you can't take back?",
        "What relationship opportunity did fear prevent you from taking?",
        "What connection did you mishandle due to your own issues?",
        "What relationship did you prioritize over one that mattered more?",
        "What person deserved better from you than what you gave?",
        "What relationship did you end prematurely out of stubbornness?",
        "What love did you walk away from that you shouldn't have?",
        "What relationship bridge did you burn that you wish you could rebuild?",
        "What person would you apologize to if you knew they'd listen?"
    ]

def clean_relationships():
    """Clean relationships category duplicates and add engaging questions"""
    print("🧹 Cleaning relationships category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all relationships questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'relationships'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} relationships questions")

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

            # Add new engaging relationship questions
            print(f"\n🌟 Adding engaging relationship questions...")
            new_questions = generate_engaging_relationship_questions()

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
                        VALUES (%s, %s, 'relationships')
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
                WHERE category = 'relationships'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 RELATIONSHIPS CLEANUP COMPLETE!")
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
    clean_relationships()