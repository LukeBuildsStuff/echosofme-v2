#!/usr/bin/env python3
"""
Add Romance & Partnerships subcategory questions to relationships category
"""

from supabase import create_client
import time

SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

romance_partnership_questions = [
    "What's the story of your first crush?",
    "What's the story of your first love?",
    "What's the story of your first heartbreak?",
    "How did you meet your first serious partner?",
    "How did you meet your longest-lasting partner?",
    "What first attracted you to them?",
    "What do you remember about your first date?",
    "What's the best date you've ever had?",
    "What's the worst date you've ever had?",
    "What's a funny memory you share with a partner?",
    "What's a romantic gesture you'll never forget?",
    "What's a romantic gesture you're proud of making?",
    "What's a song that reminds you of love?",
    "What's a place that reminds you of love?",
    "How do you usually show affection?",
    "How do you usually receive affection?",
    "What's a phrase or nickname you've used for a partner?",
    "What's a phrase or nickname a partner used for you?",
    "What's a love letter, text, or note you'll always remember?",
    "What's the most surprising thing a partner ever did for you?",
    "What's the most surprising thing you ever did for a partner?",
    "What role does humor play in your relationships?",
    "What role does passion play in your relationships?",
    "What role does comfort play in your relationships?",
    "What role does loyalty play in your relationships?",
    "What role does forgiveness play in your relationships?",
    "What's a fight or disagreement you'll never forget?",
    "How do you usually argue with a partner?",
    "How do you usually make up with a partner?",
    "What's the biggest lesson you've learned from a relationship?",
    "What's the hardest lesson you've learned from a relationship?",
    "What makes you fall in love?",
    "What makes you fall out of love?",
    "What's the difference between love and infatuation to you?",
    "How do you know when you're truly in love?",
    "How do you know when it's time to let go?",
    "What's a heartbreak that shaped you?",
    "What's a love that shaped you?",
    "What's a relationship you regret losing?",
    "What's a relationship you're glad ended?",
    "Who taught you the most about love?",
    "Who taught you the most about heartbreak?",
    "What advice about love do you live by?",
    "What advice about love do you ignore?",
    "What's a movie or book that reflects your view of love?",
    "What's a song lyric that reflects your view of love?",
    "How did you know you wanted to commit to someone?",
    "How did you know someone was not right for you?",
    "What makes a relationship strong?",
    "What makes a relationship fragile?",
    "How do you balance independence and closeness?",
    "How do you balance passion and stability?",
    "How do you balance friendship and romance in a partnership?",
    "What's a small ritual you've shared with a partner?",
    "What's a big milestone you've shared with a partner?",
    "What's a holiday memory you shared with a partner?",
    "What's a travel memory you shared with a partner?",
    "What's a quiet everyday memory you shared with a partner?",
    "What's a sacrifice you made for love?",
    "What's a sacrifice someone made for you out of love?",
    "What's something you learned about yourself through love?",
    "What's something you learned about others through love?",
    "What's a way you express romance that feels unique to you?",
    "What's a way you've been loved that felt unforgettable?",
    "What's a relationship milestone that felt especially meaningful?",
    "What's a relationship milestone that felt overrated?",
    "What makes you jealous in love?",
    "What makes you secure in love?",
    "What's a way you've handled betrayal or dishonesty?",
    "What's a way you've handled forgiveness in love?",
    "What's a relationship that others didn't understand but mattered to you?",
    "What's a relationship that others admired?",
    "What do you hope your partner(s) would say about you?",
    "What do you hope your partner(s) remember about you?",
    "What do you hope your partner(s) forgive you for?",
    "What do you hope your partner(s) thank you for?",
    "What's your love language?",
    "What's your partner's love language?",
    "What's a mismatch you've had in relationships?",
    "What's a perfect match you've had in relationships?",
    "What's a funny pet peeve you've had with a partner?",
    "What's a serious pet peeve you've had with a partner?",
    "What's a habit of yours that partners have had to adjust to?",
    "What's a habit of a partner you had to adjust to?",
    "What's something you've only ever told a partner?",
    "What's something a partner told you that you'll never forget?",
    "What's a romantic surprise you've planned?",
    "What's a romantic surprise you've received?",
    "What's a way your view of romance has changed over time?",
    "What's a way your view of commitment has changed over time?",
    "What's a way your view of heartbreak has changed over time?",
    "What makes you excited about love?",
    "What makes you scared about love?",
    "What makes you hopeful about love?",
    "What makes you doubtful about love?",
    "What do you think is the most romantic thing about you?",
    "What do you think is the least romantic thing about you?",
    "What's a phrase, gesture, or look that always meant love to you?",
    "What do you think love means at its core?",
    "If you could tell your younger self one thing about love, what would it be?"
]

print(f"🌹 Adding {len(romance_partnership_questions)} Romance & Partnerships questions...")
print("="*80)

# Check current state
current = supabase.table('questions').select('id').eq('category', 'relationships').eq('is_active', True).execute()
print(f"📊 Current active relationships questions: {len(current.data)}")

# Insert in batches
batch_size = 10
added_count = 0
failed_questions = []

for i in range(0, len(romance_partnership_questions), batch_size):
    batch = romance_partnership_questions[i:i+batch_size]
    batch_data = []

    for q in batch:
        batch_data.append({
            'question_text': q,
            'category': 'relationships',
            'subcategory': 'romance_partnerships',
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
    if 'eleanor' not in subcat:  # Skip Eleanor batch subcategories in display
        print(f"   {subcat}: {count}")

print(f"\n✅ Total active relationships questions: {len(final.data)}")
print(f"🎉 Romance & Partnerships subcategory complete with {added_count} questions!")