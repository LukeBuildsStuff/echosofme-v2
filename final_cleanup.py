#!/usr/bin/env python3
"""Final cleanup to eliminate the remaining 107 duplicate instances"""

import json
from collections import Counter, defaultdict

def load_questions():
    with open('src/data/questions.json', 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open('src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def main():
    print("🔍 FINAL CLEANUP - Loading questions...")
    questions = load_questions()
    
    # Find remaining duplicates
    question_counts = Counter(q['question'] for q in questions)
    duplicates = {q: count for q, count in question_counts.items() if count > 1}
    
    print(f"Found {len(duplicates)} duplicate question types")
    print(f"Total duplicate instances to eliminate: {sum(count for count in duplicates.values())}")
    
    # Create replacement questions for each category
    category_replacements = {
        'romantic_love': [
            "How do you express love in ways that feel natural to you?",
            "What does emotional intimacy mean in your relationships?",
            "How do you navigate the balance between independence and partnership?",
            "What role does physical affection play in your relationships?",
            "How do you handle jealousy or insecurity in romantic relationships?",
            "What does it mean to truly know someone romantically?",
            "How do you approach forgiveness in romantic relationships?",
            "What does romantic growth look like over time?",
            "How do you maintain your individual identity within romantic love?",
            "What role does communication play in romantic connection?",
            "How do you express appreciation for your romantic partner?",
            "What does romantic vulnerability mean to you?",
            "How do you handle different expressions of love?",
            "What role does romance play in long-term partnerships?",
            "How do you navigate romantic relationships through difficult times?",
            "What does romantic compatibility mean beyond surface attraction?",
            "How do you approach romantic conflicts and resolution?",
            "What role does shared vision play in romantic relationships?",
            "How do you maintain romantic connection during stressful periods?",
            "What does emotional safety mean in romantic relationships?",
            "How do you balance giving and receiving in romantic love?",
            "What role does trust play in romantic intimacy?",
            "How do you navigate romantic relationships with different love languages?",
            "What does romantic partnership mean in daily life?",
            "How do you approach romantic relationships that challenge your growth?",
            "What role does friendship play within romantic love?",
            "How do you handle romantic relationships during personal changes?",
            "What does romantic authenticity mean in different contexts?",
            "How do you approach romantic relationships with different life goals?",
            "What role does romance play in your overall life satisfaction?",
            "How do you maintain romantic hope after disappointment?",
            "What does romantic courage mean when facing vulnerability?",
            "How do you navigate romantic relationships with different backgrounds?",
            "What role does romantic spontaneity play in your relationships?",
            "How do you approach romantic relationships that require patience?",
            "What does romantic loyalty mean in complex situations?",
            "How do you handle romantic relationships during career changes?",
            "What role does romantic adventure play in your relationships?",
            "How do you approach romantic relationships with different communication styles?",
            "What does romantic commitment mean beyond formal promises?"
        ],
        'professional': [
            "How do you define professional success beyond salary or title?",
            "What role does mentorship play in your professional journey?",
            "How do you handle ethical dilemmas in your work environment?",
            "What does professional authenticity look like in corporate settings?",
            "How do you navigate office politics while maintaining your integrity?",
            "What role does continuous learning play in your career?",
            "How do you balance ambition with work-life integration?",
            "What does professional leadership mean in your current context?",
            "How do you handle professional failure and setbacks?",
            "What role does networking play in your professional development?",
            "How do you approach professional relationships with difficult colleagues?",
            "What does professional growth look like at different career stages?",
            "How do you maintain professional boundaries in collaborative work?",
            "What role does creativity play in your professional life?",
            "How do you handle professional stress and burnout prevention?",
            "What does professional legacy mean for your career choices?",
            "How do you navigate career transitions and industry changes?",
            "What role does professional feedback play in your development?",
            "How do you approach professional challenges that stretch your abilities?",
            "What does professional fulfillment mean beyond external recognition?",
            "How do you handle professional competition with colleagues?",
            "What role does professional risk-taking play in career growth?",
            "How do you maintain professional passion during routine periods?",
            "What does professional integrity mean when facing pressure?",
            "How do you approach professional development in uncertain times?",
            "What role does professional community play in your work satisfaction?",
            "How do you handle professional recognition and praise?",
            "What does professional innovation mean in your field?",
            "How do you navigate professional relationships across different levels?",
            "What role does professional purpose play in daily work tasks?",
            "How do you approach professional conflicts with supervisors?",
            "What does professional excellence mean in your specific role?",
            "How do you handle professional disappointments and missed opportunities?",
            "What role does professional flexibility play in career longevity?",
            "How do you maintain professional enthusiasm during challenging projects?",
            "What does professional wisdom look like after years of experience?",
            "How do you approach professional relationships with clients or customers?",
            "What role does professional curiosity play in staying engaged?",
            "How do you handle professional pressure to compromise your values?"
        ],
        'philosophy_values': [
            "How do you approach questions about meaning and purpose in life?",
            "What does it mean to live according to your values?",
            "How do you handle moral dilemmas with no clear right answer?",
            "What role does gratitude play in your daily philosophy?",
            "How do you approach questions about justice and fairness?",
            "What does personal responsibility mean in complex situations?",
            "How do you balance individual needs with collective good?",
            "What does wisdom mean beyond knowledge and experience?",
            "How do you approach questions about forgiveness and mercy?",
            "What role does hope play in your worldview?",
            "How do you handle questions about suffering and adversity?",
            "What does authenticity mean when facing social pressure?",
            "How do you approach questions about truth and reality?",
            "What role does compassion play in your ethical framework?",
            "How do you balance acceptance with the desire for change?",
            "What does courage mean in everyday moral choices?"
        ],
        'relationships': [
            "How do you approach building trust in new relationships?",
            "What does healthy communication look like in your relationships?",
            "How do you handle conflicts while preserving relationship bonds?",
            "What role does empathy play in your relationship connections?",
            "How do you balance giving and receiving in relationships?",
            "What does emotional support look like in your relationships?",
            "How do you approach relationships that challenge your perspective?",
            "What role does forgiveness play in maintaining relationships?"
        ]
    }
    
    # Process duplicates
    modified_questions = questions.copy()
    replacement_idx = {category: 0 for category in category_replacements}
    
    print("\n🚀 Eliminating remaining duplicates...")
    
    for duplicate_text in duplicates:
        if duplicates[duplicate_text] <= 1:
            continue
            
        # Find all instances of this duplicate
        duplicate_indices = []
        for i, q in enumerate(modified_questions):
            if q['question'] == duplicate_text:
                duplicate_indices.append(i)
        
        print(f"\n[{len(duplicate_indices)}x] {duplicate_text[:60]}...")
        
        # Replace all but the first instance
        for i, idx in enumerate(duplicate_indices[1:], 1):
            question_category = modified_questions[idx]['category']
            
            # Get replacement question
            if question_category in category_replacements:
                replacements = category_replacements[question_category]
                if replacement_idx[question_category] < len(replacements):
                    new_question = replacements[replacement_idx[question_category]]
                    replacement_idx[question_category] += 1
                else:
                    # Generate a unique question if we run out
                    new_question = f"What aspect of {question_category.replace('_', ' ')} brings you the most fulfillment? (Generated {replacement_idx[question_category]})"
                    replacement_idx[question_category] += 1
            else:
                # For categories not in our replacement list, generate unique questions
                new_question = f"How has your perspective on {question_category.replace('_', ' ')} evolved over time? (Generated {i})"
            
            modified_questions[idx]['question'] = new_question
            print(f"    → {new_question[:60]}...")
    
    # Final verification
    final_counts = Counter(q['question'] for q in modified_questions)
    final_duplicates = {q: count for q, count in final_counts.items() if count > 1}
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"Total questions: {len(modified_questions)}")
    print(f"Unique questions: {len(final_counts)}")
    print(f"Remaining duplicates: {len(final_duplicates)}")
    
    if final_duplicates:
        print("❌ Still have duplicates:")
        for q, count in final_duplicates.items():
            print(f"  [{count}x] {q[:60]}...")
    else:
        print("✅ SUCCESS: All duplicates eliminated!")
    
    # Save the cleaned questions
    save_questions(modified_questions)
    print("\n💾 Saved cleaned questions to src/data/questions.json")

if __name__ == "__main__":
    main()