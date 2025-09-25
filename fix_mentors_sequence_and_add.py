#!/usr/bin/env python3
"""
Fix sequence and add remaining Mentors & Influences questions
"""

from supabase import create_client
import time

SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# The remaining 40 questions that failed to add
remaining_questions = [
    "Tell me about someone outside your family who truly believed in you.",
    "Tell me about someone outside your family who doubted you.",
    "What's a phrase or saying you picked up from a mentor?",
    "What's a habit you learned from a mentor that stuck?",
    "What's a habit from a mentor you've consciously avoided?",
    "Who has been a role model for your character?",
    "Who has been a role model for your career?",
    "Who has been a role model for your creativity or passions?",
    "Tell me about a mentor who taught you through example, not words.",
    "Tell me about a mentor who taught you through tough feedback.",
    "What's the kindest thing a mentor ever did for you?",
    "What's the harshest lesson a mentor ever gave you?",
    "Have you ever had to outgrow a mentor's influence?",
    "Have you ever realized you were modeling yourself after the wrong person?",
    "Who showed you how to lead?",
    "Who showed you how not to lead?",
    "What did you learn from your first boss?",
    "What did you learn from your best boss?",
    "What did you learn from your worst boss?",
    "Who inspired you with their integrity?",
    "Who inspired you with their ambition?",
    "Who inspired you with their resilience?",
    "Tell me about someone you admired but never met in person.",
    "Tell me about someone you admired up close but later saw differently.",
    "What's a moment when you felt guided at the exact right time?",
    "What's a moment when you felt abandoned by someone you looked up to?",
    "Who gave you the confidence to take a big risk?",
    "Who gave you the structure you needed at the right time?",
    "Who taught you a lesson that only made sense years later?",
    "Who taught you a lesson you understood immediately?",
    "Who showed you how to think differently?",
    "Who showed you how to act differently?",
    "Who made you feel like you could be more than you thought?",
    "Who made you feel like you weren't enough?",
    "Who encouraged your talents before anyone else noticed?",
    "Who discouraged your talents when you needed support?",
    "Who do you still quote or reference today?",
    "Who do you still feel grateful for, even if you never told them?",
    "Who do you wish you could thank directly?",
    "Who do you wish you could apologize to for not listening at the time?"
]

print(f"🔧 Fixing sequence and adding {len(remaining_questions)} remaining Mentors & Influences questions...")
print("="*80)

# First, get the current max ID
current_max = supabase.table('questions').select('id').order('id', desc=True).limit(1).execute()
if current_max.data:
    next_id = current_max.data[0]['id'] + 1
    print(f"📊 Current max ID: {current_max.data[0]['id']}, starting from: {next_id}")
else:
    next_id = 1
    print(f"📊 No existing questions found, starting from: {next_id}")

# Add questions with explicit IDs
added_count = 0
failed_count = 0

for i, question_text in enumerate(remaining_questions):
    question_id = next_id + i

    question_data = {
        'id': question_id,
        'question_text': question_text,
        'category': 'relationships',
        'subcategory': 'mentors_influences',
        'difficulty_level': 2,
        'is_active': True
    }

    try:
        result = supabase.table('questions').insert(question_data).execute()
        if result.data:
            added_count += 1
            print(f"✅ Added question {question_id}: {question_text[:60]}...")
        else:
            failed_count += 1
            print(f"❌ Failed to add question {question_id}: {question_text[:60]}...")
    except Exception as e:
        failed_count += 1
        print(f"❌ Error adding question {question_id}: {e}")

    time.sleep(0.1)  # Small delay between questions

print(f"\n📊 RESULTS:")
print(f"   Successfully added: {added_count}")
print(f"   Failed: {failed_count}")

# Update sequence to prevent future conflicts
try:
    final_max = supabase.table('questions').select('id').order('id', desc=True).limit(1).execute()
    if final_max.data:
        max_id = final_max.data[0]['id']
        # Use raw SQL to update the sequence
        result = supabase.rpc('update_sequence', {'sequence_name': 'questions_id_seq', 'new_value': max_id + 1}).execute()
        print(f"✅ Updated sequence to {max_id + 1}")
except Exception as e:
    print(f"⚠️  Could not update sequence: {e}")

# Check final counts
final = supabase.table('questions').select('subcategory').eq('category', 'relationships').eq('is_active', True).execute()
from collections import Counter
subcats = Counter([q.get('subcategory', 'none') for q in final.data])

print(f"\n📊 Final Relationships Category Breakdown:")
print("="*50)
for subcat, count in sorted(subcats.items()):
    print(f"   {subcat}: {count}")

mentors_count = subcats.get('mentors_influences', 0)
print(f"\n🎯 Mentors & Influences subcategory: {mentors_count} questions")
print(f"✅ Total active relationships questions: {len(final.data)}")

if mentors_count >= 50:
    print(f"🎉 Mentors & Influences subcategory complete!")
else:
    print(f"⚠️  Still need {50 - mentors_count} more questions for complete subcategory")