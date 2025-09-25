#!/usr/bin/env python3
"""
Add Social Bonds & Community subcategory questions to relationships category
"""

from supabase import create_client
import time

SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

social_community_questions = [
    "What role has community played in your life?",
    "Tell me about a neighbor who shaped your childhood.",
    "What's a neighborhood memory that stands out to you?",
    "What's a workplace relationship that mattered to you?",
    "What's a workplace friendship that surprised you?",
    "Tell me about a mentor or colleague who influenced your career.",
    "What's the best team you've ever been part of?",
    "What made that team work well together?",
    "What's a time when community support lifted you up?",
    "What's a time when community failed you?",
    "What role has religion, church, or spiritual community played in your life?",
    "What role has school community played in your life?",
    "What role has sports or clubs played in your life?",
    "Tell me about a volunteer experience that mattered to you.",
    "What's a cause or community project you cared about deeply?",
    "What makes you feel connected to a community?",
    "What makes you feel disconnected from a community?",
    "What's a time you felt like an outsider?",
    "What's a time you felt fully included?",
    "Tell me about a group identity you've been proud to belong to.",
    "Tell me about a group identity you struggled with.",
    "Who was the best neighbor you've ever had?",
    "Who was the worst neighbor you've ever had?",
    "How did your community celebrate big events (holidays, milestones)?",
    "How did your community respond to crises or hardships?",
    "What's a gathering or festival you'll always remember?",
    "What's a tradition in your community that shaped you?",
    "What's a stereotype about your community that isn't true?",
    "What's a stereotype about your community that does fit?",
    "What makes you proud of where you're from?",
    "What makes you critical of where you're from?",
    "Tell me about a boss, teacher, or coach who changed how you see things.",
    "Tell me about a boss, teacher, or coach who challenged you.",
    "What's the best group activity you've ever been part of?",
    "What's the most difficult group activity you've been part of?",
    "How do you usually contribute to a group setting?",
    "How do you usually behave in crowds or large gatherings?",
    "What's a time you felt responsible for your community?",
    "What's a time you felt let down by your community?",
    "How do you usually meet new people in a community?",
    "How do you usually keep in touch with community groups?",
    "What makes you trust a group of people?",
    "What makes you skeptical of a group of people?",
    "What's a time you took leadership in a community?",
    "What's a time you stayed quiet in a community?",
    "Who in your community do you admire most?",
    "Who in your community frustrated you most?",
    "What makes a community healthy in your eyes?",
    "What makes a community toxic in your eyes?",
    "How do you hope people in your community remember you?"
]

print(f"🏘️ Adding {len(social_community_questions)} Social Bonds & Community questions...")
print("="*80)

# Check current state
current = supabase.table('questions').select('id').eq('category', 'relationships').eq('is_active', True).execute()
print(f"📊 Current active relationships questions: {len(current.data)}")

# Insert in batches
batch_size = 10
added_count = 0
failed_questions = []

for i in range(0, len(social_community_questions), batch_size):
    batch = social_community_questions[i:i+batch_size]
    batch_data = []

    for q in batch:
        batch_data.append({
            'question_text': q,
            'category': 'relationships',
            'subcategory': 'social_bonds_community',
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
print(f"🎉 Social Bonds & Community subcategory complete with {added_count} questions!")
print(f"\n🏆 RELATIONSHIPS CATEGORY NOW COVERS:")
print("   🏠 Family & Upbringing - where we came from")
print("   👶 Parenting & Children - families we create")
print("   👥 Friendships - bonds we choose")
print("   💕 Romance & Partnerships - love relationships")
print("   🏘️ Social Bonds & Community - broader connections")