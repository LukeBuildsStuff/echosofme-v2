#!/usr/bin/env python3
"""
Add Mentors & Influences subcategory questions to relationships category
"""

from supabase import create_client
import time

SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

mentors_influences_questions = [
    "Who has been the most influential mentor in your life, and why?",
    "Tell me about a teacher who left a lasting impact on you.",
    "Tell me about a coach who pushed you in ways you needed.",
    "Who was a boss or manager who shaped the way you work?",
    "What's the best advice a mentor ever gave you?",
    "What's the worst advice a mentor ever gave you?",
    "What's something a mentor taught you that you still use today?",
    "What's something a mentor taught you that you later rejected?",
    "Who inspired you when you were a teenager?",
    "Who inspires you most now?",
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

print(f"🎯 Adding {len(mentors_influences_questions)} Mentors & Influences questions...")
print("="*80)

# Check current state
current = supabase.table('questions').select('id').eq('category', 'relationships').eq('is_active', True).execute()
print(f"📊 Current active relationships questions: {len(current.data)}")

# Insert in batches
batch_size = 10
added_count = 0
failed_questions = []

for i in range(0, len(mentors_influences_questions), batch_size):
    batch = mentors_influences_questions[i:i+batch_size]
    batch_data = []

    for q in batch:
        batch_data.append({
            'question_text': q,
            'category': 'relationships',
            'subcategory': 'mentors_influences',
            'difficulty_level': 2,
            'is_active': True
        })

    try:
        result = supabase.table('questions').insert(batch_data).execute()
        if result.data:
            added_count += len(result.data)
            print(f"✅ Added batch {i//batch_size + 1}: {len(result.data)} questions")
        time.sleep(0.5)  # Small delay between batches
    except Exception as e:
        print(f"❌ Batch {i//batch_size + 1} failed: {e}")
        failed_questions.extend(batch)

print(f"\n📊 RESULTS:")
print(f"   Successfully added: {added_count}")
print(f"   Failed: {len(failed_questions)}")

if failed_questions:
    print("\n❌ Failed questions:")
    for q in failed_questions:
        print(f"   - {q}")

# Check final counts by subcategory
final = supabase.table('questions').select('subcategory').eq('category', 'relationships').eq('is_active', True).execute()
from collections import Counter
subcats = Counter([q.get('subcategory', 'none') for q in final.data])

print(f"\n📊 Final Relationships Category Breakdown:")
print("="*50)
for subcat, count in sorted(subcats.items()):
    print(f"   {subcat}: {count}")

print(f"\n✅ Total active relationships questions: {len(final.data)}")
print(f"🎉 Mentors & Influences subcategory complete with {added_count} questions!")
print(f"\n🏆 RELATIONSHIPS CATEGORY NOW COVERS 6 DIMENSIONS:")
print("   🏠 Family & Upbringing - where we came from")
print("   👶 Parenting & Children - families we create")
print("   👥 Friendships - bonds we choose")
print("   💕 Romance & Partnerships - love relationships")
print("   🏘️ Social Bonds & Community - broader connections")
print("   🎯 Mentors & Influences - guidance and inspiration")