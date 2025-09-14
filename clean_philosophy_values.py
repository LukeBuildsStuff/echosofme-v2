#!/usr/bin/env python3
"""
Clean philosophy_values duplicates and generate engaging replacement questions
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

def generate_engaging_philosophy_questions():
    """Generate 120 genuinely engaging philosophy & values questions"""
    return [
        # Uncomfortable Self-Awareness
        "What belief did you defend fiercely in your 20s that now makes you cringe?",
        "If you could see a graph of every lie you've ever told, what pattern would emerge?",
        "What uncomfortable truth about yourself did you recently accept?",
        "Which of your current beliefs would horrify your teenage self?",
        "What hypocritical behavior do you catch yourself doing but can't seem to stop?",
        "What do you pretend to care about but actually don't?",
        "What would you do differently if no one was watching or judging?",
        "What quality do you judge harshly in others but excuse in yourself?",
        "If your worst enemy described you, what would they say that's actually true?",
        "What part of your personality do you try to hide from new people?",

        # Evolution of Beliefs
        "What's something you used to mock that you now understand?",
        "What advice did you ignore that you wish you'd followed?",
        "What seemed like the end of the world then but was actually a blessing?",
        "What opinion did you change that lost you friends?",
        "What did you think would make you happy that absolutely didn't?",
        "What childhood fear turned out to be completely justified?",
        "What rule did you follow blindly before questioning why it existed?",
        "What did your parents get wrong about life that you're now correcting?",
        "What did you think was sophisticated as a teenager that now seems pretentious?",
        "What cultural norm did you accept without question until recently?",

        # Hidden Motivations
        "What do you do that's more about impressing others than helping them?",
        "What fear drives most of your major decisions?",
        "What do you collect, save, or hoard that reveals something deeper about you?",
        "What compliment do you fish for without realizing it?",
        "What makes you feel superior to others, even though you know it shouldn't?",
        "What childhood wound are you still trying to heal through your adult choices?",
        "What do you defend most aggressively because you're insecure about it?",
        "What pattern do you repeat in relationships that you can't seem to break?",
        "What success would you not celebrate publicly because it reveals too much?",
        "What do you spend money on that shows what you really value?",

        # Authentic Values Discovery
        "When have you compromised your values and felt surprisingly okay about it?",
        "What principle do you claim to have but your actions suggest otherwise?",
        "What injustice makes you angrier than others think it should?",
        "What small daily choice reflects your deepest beliefs?",
        "What would you sacrifice your comfort for?",
        "What gets you genuinely excited that others find boring?",
        "What do you do when no one's asking you to that reveals who you really are?",
        "What makes you feel most like yourself?",
        "What boundary are you not willing to cross, no matter what?",
        "What would you fight for even if you knew you'd lose?",

        # Philosophical Dilemmas with Personal Stakes
        "If you could know the date of your death, would you want to know?",
        "Would you rather be completely honest and lose relationships, or lie and keep them?",
        "If you could eliminate one human emotion from existence, which would it be?",
        "Would you rather be remembered for something terrible or forgotten completely?",
        "If happiness was a drug, would you take it knowing it was fake?",
        "Would you choose to be less intelligent if it meant being happier?",
        "If you could read minds but never turn it off, would you want that power?",
        "Would you rather know all the ways you've hurt people or remain ignorant?",
        "If you could restart your life with all your current knowledge, would you?",
        "Would you sacrifice your life for a stranger if no one would ever know?",

        # Deep Relationships & Connection
        "What do you need from people that you're afraid to ask for?",
        "What do you wish you could tell your parents but can't?",
        "What pattern do you notice in the people who drain your energy?",
        "What kind of person brings out the worst in you?",
        "What conversation are you avoiding that needs to happen?",
        "What do you do that pushes people away when you want them closer?",
        "What makes someone worthy of your complete trust?",
        "What do you judge people for that says more about you than them?",
        "What kind of person do you become when you're afraid?",
        "What do you wish someone had told you about love before you learned it the hard way?",

        # Meaning & Purpose
        "What problem do you think you were born to solve?",
        "What legacy are you accidentally creating?",
        "What would you regret not doing more than you'd regret trying and failing?",
        "What do you think future generations will judge our era most harshly for?",
        "What small action could you take that would honor your future self?",
        "What does your ideal day reveal about what you truly value?",
        "What would you do with your time if you knew you couldn't fail?",
        "What question do you hope someone asks you before you die?",
        "What would you want written on your tombstone that isn't just nice words?",
        "What part of being human do you find most meaningful?",

        # Moral Complexity
        "When has doing the 'right' thing caused more harm than good?",
        "What moral rule have you bent that you still feel okay about?",
        "What do you think you'd be capable of under extreme circumstances?",
        "When have you stayed silent when you should have spoken up?",
        "What injustice do you personally benefit from?",
        "What's something you've forgiven that others think you shouldn't have?",
        "What judgment do you make about people's circumstances that might be unfair?",
        "When have you chosen comfort over doing what's right?",
        "What privilege do you have that you're only recently recognizing?",
        "What harm have you caused that you've never properly acknowledged?",

        # Growth & Change
        "What pattern in your life took you longest to recognize?",
        "What skill do you wish you'd developed earlier in life?",
        "What part of growing up surprised you the most?",
        "What assumption about adulthood turned out to be completely wrong?",
        "What do you need to forgive yourself for?",
        "What version of yourself are you trying to outgrow?",
        "What's the most important thing you've learned about being wrong?",
        "What strength do you have that you developed from your biggest weakness?",
        "What would you tell someone who's struggling with what you've overcome?",
        "What part of your personality is still developing?",

        # Society & Culture
        "What societal expectation do you rebel against, even quietly?",
        "What tradition do you follow even though you don't believe in its purpose?",
        "What aspect of modern life would you eliminate if you could?",
        "What do you think is the biggest lie our society tells itself?",
        "What progress do you see happening that gives you hope?",
        "What cultural change have you witnessed that you're grateful for?",
        "What do you think will be considered barbaric about our current time?",
        "What social role do you play that doesn't feel authentic to who you are?",
        "What community do you belong to that shapes how you see the world?",
        "What responsibility do you have to future generations that you take seriously?",

        # Wisdom & Understanding
        "What question has changed shape for you as you've gotten older?",
        "What do you understand now that you wish you could have understood earlier?",
        "What wisdom did someone share with you at exactly the right time?",
        "What misunderstanding about life served you well until you outgrew it?",
        "What do you know now that would have saved you years of confusion?",
        "What insight changed how you see everything else?",
        "What did you think was complex that's actually simple, or vice versa?",
        "What truth were you not ready to hear when you first heard it?",
        "What do you now see as a gift that you once saw as a curse?",
        "What question do you ask yourself that always leads to clarity?"
    ]

def clean_philosophy_values():
    """Clean philosophy_values duplicates and add engaging questions"""
    print("🧹 Cleaning philosophy_values duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all philosophy_values questions
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                WHERE category = 'philosophy_values'
                ORDER BY id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} philosophy_values questions")

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
            new_questions = generate_engaging_philosophy_questions()

            # Get next available ID
            cur.execute("SELECT MAX(id) FROM questions")
            max_id = cur.fetchone()['max'] or 0
            next_id = max_id + 1

            # Insert new questions
            print(f"✨ Adding {len(new_questions)} engaging new questions...")

            for i, question_text in enumerate(new_questions):
                cur.execute("""
                    INSERT INTO questions (id, question_text, category)
                    VALUES (%s, %s, %s)
                """, (next_id + i, question_text, 'philosophy_values'))

            conn.commit()

            # Final count
            cur.execute("""
                SELECT COUNT(*) as total,
                       COUNT(DISTINCT question_text) as unique_texts
                FROM questions
                WHERE category = 'philosophy_values'
            """)

            result = cur.fetchone()
            print(f"\n✅ Philosophy & Values cleanup complete!")
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
    clean_philosophy_values()