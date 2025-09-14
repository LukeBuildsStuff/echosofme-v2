#!/usr/bin/env python3
"""
Clean personal category duplicates and generate engaging personal identity questions
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

def generate_engaging_personal_identity_questions():
    """Generate 60 deeply engaging personal identity questions"""
    return [
        # Hidden Selves & Multiple Identities
        "What part of your personality only emerges in specific situations?",
        "What contradictory traits do you possess that confuse people who know you?",
        "What aspect of who you are took you the longest to accept?",
        "What do you pretend to be bad at because being good at it would change how people see you?",
        "What version of yourself do you only show to certain people?",
        "What part of your identity feels performative rather than authentic?",
        "What mask do you wear most often, and why is it necessary?",
        "What would people be most surprised to learn about your inner world?",
        "What part of yourself do you keep hidden because it doesn't fit your image?",
        "What identity from your past still influences decisions you make today?",

        # Identity Evolution & Change
        "What belief about yourself turned out to be completely wrong?",
        "What part of your personality has changed the most since adolescence?",
        "What aspect of yourself are you still discovering?",
        "What old version of yourself do you sometimes miss?",
        "What would your 16-year-old self think of who you've become?",
        "What identity crisis taught you the most about who you really are?",
        "What part of yourself did you have to kill to become who you are now?",
        "What transformation surprised you the most about your own character?",
        "What aspect of growing older has been most unexpected for your sense of self?",
        "What core part of yourself has remained unchanged despite everything?",

        # Self-Perception vs. Reality
        "What do others see in you that you struggle to see in yourself?",
        "What feedback about yourself initially made you defensive but was actually accurate?",
        "What compliment do you receive that you genuinely don't understand?",
        "What assumption do people make about you that's completely wrong?",
        "What blind spot about yourself did someone recently point out?",
        "What quality do you think you hide well but others can easily spot?",
        "What's the biggest gap between how you see yourself and how others see you?",
        "What harsh truth about yourself did you learn from someone else's perspective?",
        "What positive trait do you have that you consistently undervalue?",
        "What defense mechanism do you use that everyone can see through?",

        # Authentic Self vs. Social Self
        "When do you feel most authentically yourself?",
        "What social situation makes you feel least like yourself?",
        "What would you do differently if you weren't afraid of judgment?",
        "What part of your personality gets suppressed in professional settings?",
        "What would change about your behavior if you stopped caring what others thought?",
        "What aspect of yourself do you edit out of conversations?",
        "What would your closest friends say is your most endearing quirk?",
        "What unconventional thing about you do you wish was more socially acceptable?",
        "What do you do when you're completely alone that reveals who you really are?",
        "What would you express more of if you felt completely safe to do so?",

        # Core Identity & Values
        "What principle would you never compromise, even under pressure?",
        "What part of your identity is absolutely non-negotiable?",
        "What would have to change about the world for you to feel like you no longer belonged?",
        "What aspect of yourself do you hope never changes?",
        "What do you stand for that others don't always understand?",
        "What makes you feel most proud of who you are as a person?",
        "What values do you hold that sometimes make life harder for you?",
        "What would you be willing to be disliked for in order to stay true to yourself?",
        "What part of your character was forged by your biggest challenges?",
        "What would you want people to remember about your character after you're gone?",

        # Relational Identity
        "How do different people bring out different versions of you?",
        "What role do you naturally take on in groups that you didn't choose?",
        "What type of person brings out your worst tendencies?",
        "Who in your life sees the most authentic version of you?",
        "What do you become when you're with your family that you're not elsewhere?",
        "How does being in love change your sense of identity?",
        "What aspect of yourself only emerges in close friendships?",
        "What do you need from others to feel like yourself?",
        "How do you adapt your personality in different social contexts?",
        "What relationship taught you the most about who you really are?"
    ]

def clean_personal():
    """Clean personal category duplicates and add engaging questions"""
    print("🧹 Cleaning personal category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all personal questions
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                WHERE category = 'personal'
                ORDER BY id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} personal questions")

            # Group by question text
            question_groups = defaultdict(list)
            for q in questions:
                question_groups[q['question_text']].append(q)

            # Find duplicates to delete
            duplicates_to_delete = []
            responses_to_update = []

            for text, question_list in question_groups.items():
                if len(question_list) > 1:
                    primary_id = question_list[0]['id']  # Keep first
                    duplicate_ids = [q['id'] for q in question_list[1:]]

                    print(f"🔍 Found {len(question_list)} copies of: '{text[:50]}...'")

                    # Track duplicates to delete
                    duplicates_to_delete.extend(duplicate_ids)

                    # Track responses to move
                    for dup_id in duplicate_ids:
                        responses_to_update.append((primary_id, dup_id))

            if duplicates_to_delete:
                print(f"🔄 Processing {len(duplicates_to_delete)} duplicate questions...")

                # Move responses to primary questions (avoiding constraint violations)
                responses_moved = 0
                for primary_id, duplicate_id in responses_to_update:
                    # First check if moving would create conflicts
                    cur.execute("""
                        UPDATE responses
                        SET question_id = %s
                        WHERE question_id = %s
                        AND NOT EXISTS (
                            SELECT 1 FROM responses r2
                            WHERE r2.user_id = responses.user_id
                            AND r2.question_id = %s
                        )
                    """, (primary_id, duplicate_id, primary_id))

                    responses_moved += cur.rowcount

                # Delete any remaining responses that couldn't be moved (due to conflicts)
                if duplicates_to_delete:
                    cur.execute("""
                        DELETE FROM responses
                        WHERE question_id = ANY(%s)
                    """, (duplicates_to_delete,))

                if responses_moved > 0:
                    print(f"📝 Moved {responses_moved} responses to primary questions")

                # Delete duplicate questions
                cur.execute("""
                    DELETE FROM questions
                    WHERE id = ANY(%s)
                """, (duplicates_to_delete,))

                deleted_count = cur.rowcount
                print(f"🗑️ Deleted {deleted_count} duplicate questions")

            # Generate new engaging questions
            new_questions = generate_engaging_personal_identity_questions()

            # Get next available ID
            cur.execute("SELECT MAX(id) FROM questions")
            max_id = cur.fetchone()['max'] or 0
            next_id = max_id + 1

            # Insert new questions
            print(f"✨ Adding {len(new_questions)} engaging new identity questions...")

            for i, question_text in enumerate(new_questions):
                cur.execute("""
                    INSERT INTO questions (id, question_text, category)
                    VALUES (%s, %s, %s)
                """, (next_id + i, question_text, 'personal'))

            conn.commit()

            # Final count
            cur.execute("""
                SELECT COUNT(*) as total,
                       COUNT(DISTINCT question_text) as unique_texts
                FROM questions
                WHERE category = 'personal'
            """)

            result = cur.fetchone()
            print(f"\n✅ Personal category cleanup complete!")
            print(f"   Final count: {result['total']} questions (all unique)")
            print(f"   Added: {len(new_questions)} engaging new questions")
            print(f"   Removed: {len(duplicates_to_delete)} duplicates")

            if result['total'] == result['unique_texts']:
                print("   🎯 All questions are now unique and engaging!")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_personal()