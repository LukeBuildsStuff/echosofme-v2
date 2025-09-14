#!/usr/bin/env python3
"""
Clean family_parenting category duplicates and add engaging family & parenting questions
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

def generate_engaging_family_parenting_questions():
    """Generate 70 thought-provoking questions about family dynamics and parenting realities"""
    return [
        # Family Dysfunction & Unspoken Tensions
        "What family dynamic do you participate in despite knowing it's unhealthy?",
        "What truth about your family does everyone avoid talking about?",
        "What family pattern do you see repeating that you can't seem to break?",
        "What family member do you love but struggle to like?",
        "What family gathering always creates tension for predictable reasons?",
        "What unspoken family rule governs how you all interact?",
        "What family role were you assigned that you never chose?",
        "What family secret weighs on you that others don't know you know?",
        "What family relationship feels more like an obligation than love?",
        "What family expectation do you fulfill to avoid conflict?",

        # Parenting Regrets & Guilt
        "What parenting mistake do you replay in your mind?",
        "What did you swear you'd never do as a parent but ended up doing anyway?",
        "What aspect of parenting makes you feel like you're failing daily?",
        "What parenting decision do you regret but can't undo?",
        "What childhood experience of yours do you worry you've passed on?",
        "What parenting standard do you have that's impossible to meet?",
        "What kind of parent did you think you'd be versus who you actually are?",
        "What parenting moment still makes you cringe?",
        "What do you hide from other parents about your struggles?",
        "What parenting advice do you give but don't follow yourself?",

        # Generational Patterns & Trauma
        "What family pattern from your childhood are you determined to break?",
        "What generational trauma shows up in your daily life?",
        "What family dysfunction did you think was normal until you got older?",
        "What family communication style did you inherit that doesn't serve you?",
        "What childhood coping mechanism do you still use as an adult?",
        "What family story gets told that isn't actually true?",
        "What family behavior did you normalize that you now recognize as harmful?",
        "What generational expectation weighs on you that you want to reject?",
        "What family healing needs to happen but no one wants to address it?",
        "What family legacy do you want to change for future generations?",

        # Sibling Dynamics & Rivalry
        "What sibling wound from childhood still affects you?",
        "What sibling dynamic exists now that mirrors your childhood roles?",
        "What do you envy about your sibling that you've never admitted?",
        "What sibling rivalry still plays out in subtle ways as adults?",
        "What sibling relationship do you wish you could repair but don't know how?",
        "What family favoritism did you experience that shaped your self-worth?",
        "What sibling comparison still triggers insecurity in you?",
        "What did your parents do differently with your siblings that hurt you?",
        "What sibling resentment do you carry that feels petty but persists?",
        "What sibling bond was damaged by family circumstances beyond your control?",

        # Parent-Child Relationship Evolution
        "What did you think about your parents as a child versus now?",
        "What parent relationship boundary do you struggle to maintain?",
        "What childhood need from your parents do you still crave?",
        "What do you wish you could tell your parents but never will?",
        "What parental expectation do you still try to meet despite being an adult?",
        "What aspect of your relationship with your parents embarrasses you?",
        "What do you appreciate about your parents now that you couldn't see before?",
        "What parent wound affects your other relationships?",
        "What do you wish your parents understood about you that they don't?",
        "What family conversation needs to happen but feels too risky?",

        # Family Roles & Expectations
        "What family role exhausts you but everyone expects you to play?",
        "What family responsibility fell to you that wasn't fair?",
        "What family function would fall apart if you stopped managing it?",
        "What family member do you always have to take care of?",
        "What family expectation do you meet to keep the peace?",
        "What family tradition do you participate in but don't enjoy?",
        "What family decision do you always have to make for everyone?",
        "What family crisis always becomes your problem to solve?",
        "What family boundary do you struggle to enforce?",
        "What family loyalty conflicts with your personal values?",

        # Family Secrets & Difficult Truths
        "What family truth would change how others see your family?",
        "What family member are you protecting by keeping their secret?",
        "What family shame gets passed down without being discussed?",
        "What family story gets sanitized when told to outsiders?",
        "What family reality do you all pretend is different than it is?",
        "What family member's struggles does everyone ignore?",
        "What family behavior gets excused because 'that's just how they are'?",
        "What family elephant in the room affects everyone but no one mentions?",
        "What family denial keeps everyone from healing?",
        "What family truth are you afraid to acknowledge even to yourself?",

        # Balancing Family vs Personal Needs
        "What personal dream have you sacrificed for family obligations?",
        "What family demand consistently conflicts with your well-being?",
        "What family boundary would improve your life but hurt their feelings?",
        "What family time commitment drains you but you can't say no?",
        "What family need always takes priority over your own?",
        "What family guilt trip works on you every time?",
        "What family relationship costs you more energy than it gives?",
        "What family approval do you seek at the expense of being yourself?",
        "What family peace do you maintain by suppressing your own needs?",
        "What family harmony would be disrupted if you were completely honest?"
    ]

def clean_family_parenting():
    """Clean family_parenting category duplicates and add engaging questions"""
    print("🧹 Cleaning family_parenting category duplicates...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all family_parenting questions
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE category = 'family_parenting'
                ORDER BY question_text, id ASC
            """)

            questions = cur.fetchall()
            print(f"📊 Found {len(questions)} family_parenting questions")

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

            # Add new engaging family & parenting questions
            print(f"\n🌟 Adding engaging family and parenting questions...")
            new_questions = generate_engaging_family_parenting_questions()

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
                        VALUES (%s, %s, 'family_parenting')
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
                WHERE category = 'family_parenting'
            """)

            final_stats = cur.fetchone()

            print(f"\n🎉 FAMILY & PARENTING CLEANUP COMPLETE!")
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
    clean_family_parenting()