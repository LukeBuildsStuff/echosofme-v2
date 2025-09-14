#!/usr/bin/env python3
"""
Fix dating_experiences category duplicate questions
Removes 94 duplicates of "How do you approach first dates?" and generates unique questions
"""

import json
from collections import Counter

def load_questions():
    with open('src/data/questions.json', 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open('src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2)

def generate_unique_dating_questions():
    """Generate 93 unique dating questions to replace duplicates"""
    return [
        "What's your biggest dating red flag that you've learned to recognize?",
        "How do you handle dating someone with different life goals?",
        "What's been your experience with online dating apps?",
        "How do you navigate dating when you have different religious beliefs?",
        "What's the most important lesson you've learned from a past relationship?",
        "How do you maintain your independence while dating someone?",
        "What's your experience with long-distance relationships?",
        "How do you handle introducing someone you're dating to your family?",
        "What's been your experience dating someone significantly older or younger?",
        "How do you approach dating after a difficult breakup?",
        "What's the most challenging aspect of dating in your current life stage?",
        "How do you balance career ambitions with dating and relationships?",
        "What's your experience with dating someone from a different social class?",
        "How do you handle dating someone who has children?",
        "What's been your experience with casual dating versus serious relationships?",
        "How do you approach dating when you're focused on personal growth?",
        "What's the most important conversation to have early in dating?",
        "How do you handle dating anxiety or nervousness?",
        "What's your experience with dating within your friend group?",
        "How do you navigate dating when you have social anxiety?",
        "What's been your experience with dating apps versus meeting people organically?",
        "How do you handle dating someone who's recently divorced?",
        "What's your approach to dating when you're an introvert?",
        "How do you handle dating someone with different political views?",
        "What's been your experience with dating someone who travels frequently for work?",
        "How do you approach dating when you're dealing with mental health challenges?",
        "What's the most surprising thing you've learned about yourself through dating?",
        "How do you handle dating when you have trust issues from past relationships?",
        "What's your experience with dating someone who has different spending habits?",
        "How do you navigate dating when you're at different life stages?",
        "What's been your experience with dating someone who's very close to their ex?",
        "How do you handle dating when you're focused on building your career?",
        "What's your approach to dating someone who has different communication styles?",
        "How do you navigate dating when you have different views on marriage?",
        "What's been your experience with dating someone who's emotionally unavailable?",
        "How do you handle dating when you're still healing from past trauma?",
        "What's your experience with dating someone who has addiction issues?",
        "How do you approach dating when you have different lifestyle preferences?",
        "What's been your experience with dating someone who's geographically undesirable?",
        "How do you handle dating when you're at different financial stages in life?",
        "What's your experience with dating someone who has different parenting styles?",
        "How do you navigate dating when you have chronic illness or health issues?",
        "What's been your experience with dating someone who's workaholic?",
        "How do you handle dating when you have different social needs?",
        "What's your approach to dating someone with different educational backgrounds?",
        "How do you navigate dating when you have different future timelines?",
        "What's been your experience with dating someone who's commitment-phobic?",
        "How do you handle dating when you're dealing with family pressures?",
        "What's your experience with dating someone who has different cleanliness standards?",
        "How do you approach dating when you're focused on self-improvement?",
        "What's been your experience with dating someone who's recently out of a relationship?",
        "How do you handle dating when you have different conflict resolution styles?",
        "What's your experience with dating someone who has different social circles?",
        "How do you navigate dating when you have different career priorities?",
        "What's been your experience with dating someone who's very private about their life?",
        "How do you handle dating when you're dealing with insecurities?",
        "What's your approach to dating someone who has different relationship experience?",
        "How do you navigate dating when you have different communication needs?",
        "What's been your experience with dating someone who's going through major life changes?",
        "How do you handle dating when you have different attachment styles?",
        "What's your experience with dating someone who has different cultural values?",
        "How do you approach dating when you're rebuilding after a toxic relationship?",
        "What's been your experience with dating someone who's very busy or unavailable?",
        "How do you handle dating when you have different expectations about exclusivity?",
        "What's your experience with dating someone who has different hobbies and interests?",
        "How do you navigate dating when you're dealing with past rejection trauma?",
        "What's been your experience with dating someone who's emotionally expressive?",
        "How do you handle dating when you have different views on personal space?",
        "What's your approach to dating someone who has different friendship dynamics?",
        "How do you navigate dating when you're focused on building financial stability?",
        "What's been your experience with dating someone who has different family dynamics?",
        "How do you handle dating when you have different love languages?",
        "What's your experience with dating someone who's dealing with their own trauma?",
        "How do you approach dating when you're at different maturity levels?",
        "What's been your experience with dating someone who has different life experiences?",
        "How do you handle dating when you have different ideas about personal growth?",
        "What's your experience with dating someone who's very independent?",
        "How do you navigate dating when you have different comfort levels with vulnerability?",
        "What's been your experience with dating someone who has different social media habits?",
        "How do you handle dating when you have different approaches to conflict?",
        "What's your approach to dating someone who has different energy levels?",
        "How do you navigate dating when you're dealing with societal or family expectations?",
        "What's been your experience with dating someone who has different boundaries?",
        "How do you handle dating when you have different ideas about personal time?",
        "What's your experience with dating someone who's going through a career transition?",
        "How do you approach dating when you have different comfort levels with intimacy?",
        "What's been your experience with dating someone who has different coping mechanisms?",
        "How do you handle dating when you're at different points in your healing journey?",
        "What's your experience with dating someone who has different relationship goals?",
        "How do you navigate dating when you have different ideas about personal development?",
        "What's been your experience with dating someone who communicates differently under stress?",
        "How do you handle dating when you have different approaches to problem-solving?",
        "What's your approach to dating someone who has different emotional needs?",
        "How do you navigate dating when you're building your self-confidence?",
        "What's been your experience with dating someone who has different lifestyle rhythms?",
        "How do you handle dating when you have different ideas about work-life balance?"
    ]

def fix_dating_duplicates():
    """Remove dating_experiences duplicates and add unique questions"""
    print("🔧 Loading questions...")
    questions = load_questions()

    # Filter dating questions
    dating_questions = [q for q in questions if q.get('category') == 'dating_experiences']
    other_questions = [q for q in questions if q.get('category') != 'dating_experiences']

    print(f"📊 Found {len(dating_questions)} dating_experiences questions")

    # Analyze duplicates
    question_texts = [q.get('question', q.get('question_text', '')) for q in dating_questions]
    text_counts = Counter(question_texts)

    print("🔍 Duplicates found:")
    for text, count in text_counts.items():
        if count > 1:
            print(f"  '{text[:50]}...': {count} times")

    # Keep only unique questions (first instance of each)
    seen_texts = set()
    unique_dating_questions = []

    for q in dating_questions:
        text = q.get('question', q.get('question_text', ''))
        if text not in seen_texts:
            unique_dating_questions.append(q)
            seen_texts.add(text)

    print(f"✅ Kept {len(unique_dating_questions)} unique questions")

    # Generate new questions to replace duplicates
    new_question_texts = generate_unique_dating_questions()
    next_id = max(q.get('id', 0) for q in questions) + 1

    # Create new question objects
    new_questions = []
    for i, question_text in enumerate(new_question_texts):
        new_questions.append({
            "id": next_id + i,
            "question": question_text,
            "category": "dating_experiences",
            "source": "duplicate_fix_generated"
        })

    print(f"🎯 Generated {len(new_questions)} new unique questions")

    # Combine all questions
    all_dating_questions = unique_dating_questions + new_questions
    all_questions = other_questions + all_dating_questions

    # Sort by ID
    all_questions.sort(key=lambda x: x.get('id', 0))

    print(f"💾 Saving {len(all_questions)} total questions...")
    save_questions(all_questions)

    print("✨ Dating experiences duplicates fixed!")
    print(f"   - Removed {len(dating_questions) - len(unique_dating_questions)} duplicates")
    print(f"   - Added {len(new_questions)} new unique questions")
    print(f"   - Total dating_experiences questions: {len(all_dating_questions)}")

if __name__ == "__main__":
    fix_dating_duplicates()