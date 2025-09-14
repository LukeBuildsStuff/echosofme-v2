#!/usr/bin/env python3
"""
Clean friendships_social category duplicates and add engaging friendship & social questions
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

def generate_engaging_friendships_social_questions():
    """Generate 60 thought-provoking questions about the difficult realities of friendship and social connection"""
    return [
        # Friendship Failures and Disappointments
        "What friend disappointed you in a way that changed how you see friendship?",
        "What friendship ended that you still don't understand why?",
        "What friend did you realize you cared about more than they cared about you?",
        "What friendship became one-sided without you realizing it?",
        "What friend betrayed your trust in a way you can't forgive?",
        "What friendship do you maintain out of guilt rather than genuine connection?",
        "What friend consistently lets you down but you keep giving them chances?",
        "What friendship ended over something that seems trivial now but felt huge then?",
        "What friend did you outgrow but feel guilty about leaving behind?",
        "What friendship fell apart when you needed them most?",

        # Social Anxiety and Performance
        "What social situation makes you feel like you're wearing a mask?",
        "What do you pretend to enjoy socially to fit in?",
        "What social skill do you wish came more naturally to you?",
        "What social gathering always drains your energy?",
        "What do you rehearse in your head before social interactions?",
        "What social anxiety do you hide behind humor or other defenses?",
        "What social expectation exhausts you?",
        "What do you do differently when you're alone versus with others?",
        "What social role do you play that doesn't feel authentic?",
        "What social fear prevents you from being yourself around others?",

        # Loneliness in Crowds
        "When do you feel most lonely despite being surrounded by people?",
        "What social situation makes you feel more isolated than being alone?",
        "What makes you feel disconnected even when you're with friends?",
        "What do you wish people understood about your need for solitude?",
        "What social group do you feel like an outsider in?",
        "What conversation topic makes you feel left out?",
        "What social experience makes you question your belonging?",
        "What do you crave from social connection that you rarely find?",
        "What makes you feel misunderstood by people who think they know you?",
        "What social moment made you realize how alone you actually felt?",

        # Toxic Friendships and Boundaries
        "What friend takes more energy than they give?",
        "What friendship dynamic do you participate in despite knowing it's unhealthy?",
        "What friend consistently crosses your boundaries?",
        "What do you tolerate from friends that you wouldn't tolerate from strangers?",
        "What friend makes you feel worse about yourself after spending time together?",
        "What friendship do you stay in because ending it feels too hard?",
        "What friend guilt-trips you when you try to set boundaries?",
        "What toxic pattern shows up in multiple friendships?",
        "What friend do you enable in ways that aren't helping either of you?",
        "What friendship boundary do you struggle to maintain?",

        # Social Masks and Facades
        "What personality do you put on in different social groups?",
        "What part of yourself do you hide to be liked by others?",
        "What do you exaggerate about yourself to seem more interesting?",
        "What insecurity do you cover up with social performance?",
        "What authentic part of yourself do you suppress in social settings?",
        "What do you pretend to care about to maintain friendships?",
        "What opinion do you keep to yourself to avoid social conflict?",
        "What aspect of your life do you present differently than it actually is?",
        "What social media version of yourself is most different from reality?",
        "What do you perform socially that requires emotional labor?",

        # Friendship Jealousy and Competition
        "What friend's success triggers jealousy you don't want to admit?",
        "What do you compete with friends about even though you wish you didn't?",
        "What friend achievement made you feel inadequate?",
        "What friendship dynamic involves unhealthy comparison?",
        "What do you envy about a friend's life that you pretend not to care about?",
        "What friend makes you feel insecure about your own choices?",
        "What friendship competition exhausts you but you can't seem to stop?",
        "What friend's lifestyle makes you question your own decisions?",
        "What do you feel you have to prove to certain friends?",
        "What friendship involves keeping score in ways that aren't healthy?",

        # Social Exhaustion and Introvert Struggles
        "What social obligation drains you but you feel you can't decline?",
        "What do you need to recover from after social interactions?",
        "What misunderstanding do people have about your social needs?",
        "What social commitment do you dread but feel obligated to maintain?",
        "What do you wish people understood about your social energy?",
        "What social activity do others love that completely exhausts you?",
        "What do you need from friendship that most people don't understand?",
        "What social pressure do you feel to be more outgoing than you naturally are?",
        "What social recharge time do you need that others might judge?",
        "What social norm conflicts with your natural personality?"
    ]

def clean_friendships_social():
    """Clean friendships_social category duplicates and add engaging questions"""
    print("🧹 Cleaning friendships_social category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all friendships_social questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'friendships_social'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} friendships_social questions")

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

            # Add new engaging friendship & social questions
            print(f"\n🌟 Adding engaging friendship and social connection questions...")
            new_questions = generate_engaging_friendships_social_questions()

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
                        VALUES (%s, %s, 'friendships_social')
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
                WHERE category = 'friendships_social'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 FRIENDSHIPS & SOCIAL CLEANUP COMPLETE!")
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
    clean_friendships_social()