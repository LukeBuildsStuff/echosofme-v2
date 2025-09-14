#!/usr/bin/env python3
"""
Clean creative_expression category duplicates and add engaging creative questions
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

def generate_engaging_creative_expression_questions():
    """Generate 85 thought-provoking questions about creative expression, blocks, identity, and the messy realities of artistic life"""
    return [
        # Creative Blocks & Frustrations
        "What creative dream did you abandon that still haunts you?",
        "What creative project failed so badly it made you question your abilities?",
        "What creative work are you most ashamed of ever creating?",
        "What creative jealousy do you struggle with but won't admit?",
        "What creative block has lasted longer than you care to admit?",
        "What creative excuse do you keep making to avoid starting?",
        "What creative failure taught you the most about yourself?",
        "What creative criticism destroyed your confidence for years?",
        "What creative project do you keep starting but never finish?",
        "What creative skill do you wish you had but gave up pursuing?",

        # Artistic Identity Crisis
        "What creative identity do you cling to that no longer serves you?",
        "What artistic skill do you pretend to have but don't really possess?",
        "What creative community do you feel excluded from despite trying to fit in?",
        "What creative persona do you put on that doesn't feel authentic?",
        "What artistic movement do you claim to understand but actually find confusing?",
        "What creative achievement do you inflate to seem more accomplished?",
        "What artistic tradition do you rebel against but secretly admire?",
        "What creative role do you play that exhausts your authentic self?",
        "What artistic style do you force yourself into that doesn't feel natural?",
        "What creative validation do you desperately seek but won't ask for directly?",

        # Creative Fears & Vulnerabilities
        "What creative risk are you too scared to take despite knowing you should?",
        "What artistic vulnerability do you hide behind technical skill?",
        "What creative truth about yourself are you afraid to express?",
        "What artistic rejection still stings when you think about it?",
        "What creative work would expose too much of your inner world?",
        "What artistic failure are you afraid to repeat?",
        "What creative judgment from others paralyzes your self-expression?",
        "What artistic insecurity do you cover up with bravado?",
        "What creative perfectionism prevents you from sharing your work?",
        "What artistic exposure feels too risky for your current life?",

        # The Dark Side of Creating
        "What destructive habit fuels your creativity but damages other areas of life?",
        "What toxic creative pattern do you repeat despite knowing it's unhealthy?",
        "What unhealthy comparison kills your creative joy but you can't stop making?",
        "What creative obsession has negatively impacted your relationships?",
        "What artistic pursuit consumes time you should spend on responsibilities?",
        "What creative mood swing do others have to endure when you're working?",
        "What artistic sacrifice was too high a price for the creative outcome?",
        "What creative addiction do you rationalize as necessary for your art?",
        "What toxic creative environment do you stay in because you fear change?",
        "What artistic ego problem do you struggle to keep in check?",

        # Creative Authenticity vs. Commercial Success
        "What creative work feels most like selling out but pays the bills?",
        "What artistic compromise do you regret most in hindsight?",
        "What creative voice are you suppressing to be more marketable?",
        "What artistic integrity have you sacrificed for financial stability?",
        "What creative project would you do if money wasn't a factor?",
        "What artistic direction do you avoid because it won't appeal to others?",
        "What creative authenticity do you sacrifice to fit current trends?",
        "What artistic vision do you water down to make it more palatable?",
        "What creative expression do you censor to avoid controversy?",
        "What artistic truth do you avoid because it might alienate your audience?",

        # Creative Process Struggles
        "What creative ritual have you developed that borders on superstition?",
        "What artistic workflow do you know is inefficient but can't change?",
        "What creative environment requirement limits where you can work?",
        "What artistic tool or medium do you depend on too heavily?",
        "What creative schedule works against your natural rhythms?",
        "What artistic collaboration style consistently creates conflict?",
        "What creative decision-making pattern leads to regret?",
        "What artistic feedback do you ignore that you should probably listen to?",
        "What creative inspiration source has become a crutch?",
        "What artistic deadline pressure brings out your worst creative habits?",

        # Creative Legacy and Mortality
        "What creative work do you want to complete before you die?",
        "What artistic impact do you hope to have that currently feels impossible?",
        "What creative legacy would disappoint you if it's all you're remembered for?",
        "What artistic contribution do you wish you could make to future generations?",
        "What creative work would you be devastated to see unfinished at your death?",
        "What artistic influence on others do you hope you're having but can't measure?",
        "What creative achievement would finally make you feel you've 'made it'?",
        "What artistic recognition do you crave that may never come?",
        "What creative regret would haunt you if you never addressed it?",
        "What artistic courage do you need to develop before it's too late?",

        # Hidden Creative Shame
        "What creative genre do you secretly love but publicly dismiss?",
        "What artistic skill are you embarrassed about being good at?",
        "What creative work of yours do you hide from certain people?",
        "What artistic interest do you downplay because it doesn't fit your image?",
        "What creative achievement are you proud of but feel you can't share?",
        "What artistic inspiration source would surprise people who know you?",
        "What creative dream do you keep private because others might laugh?",
        "What artistic talent do you possess but feel guilty about having?",
        "What creative activity brings you joy but seems 'beneath' your artistic level?",
        "What artistic appreciation do you hide because it conflicts with your stated values?",

        # Creative Relationships and Isolation
        "What creative solitude do you need that others interpret as rejection?",
        "What artistic community support do you want but don't know how to ask for?",
        "What creative collaboration consistently brings out your worst instincts?",
        "What artistic mentor relationship ended badly and still affects your work?",
        "What creative friend do you compete with in unhealthy ways?",
        "What artistic isolation do you choose that might be limiting your growth?",
        "What creative relationship boundary do you struggle to maintain?",
        "What artistic networking feels so inauthentic it makes you uncomfortable?",
        "What creative support do you give others while neglecting your own needs?",
        "What artistic connection are you afraid to pursue because of vulnerability?"
    ]

def clean_creative_expression():
    """Clean creative_expression category duplicates and add engaging questions"""
    print("🧹 Cleaning creative_expression category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all creative_expression questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'creative_expression'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} creative_expression questions")

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

            # Add new engaging creative expression questions
            print(f"\n🌟 Adding engaging creative expression questions...")
            new_questions = generate_engaging_creative_expression_questions()

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
                        VALUES (%s, %s, 'creative_expression')
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
                WHERE category = 'creative_expression'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 CREATIVE EXPRESSION CLEANUP COMPLETE!")
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
    clean_creative_expression()