#!/usr/bin/env python3
"""
Fix the remaining 44 category misalignment issues identified in the review
"""

import json

def load_questions():
    with open('src/data/questions.json', 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open('src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def main():
    print("🔧 FIXING REMAINING CATEGORY MISALIGNMENTS")
    print("=" * 50)
    
    questions = load_questions()
    fixes_made = 0
    
    # Define specific fixes based on the review
    fixes = [
        # Creative Expression → Philosophy Values (moral imagination questions)
        {"from_cat": "creative_expression", "to_cat": "philosophy_values", "keywords": ["moral imagination"]},
        
        # Creative Expression → Hobbies (hobby questions)
        {"from_cat": "creative_expression", "to_cat": "hobbies", "keywords": ["creative hobby"]},
        
        # Daily Life → Family Parenting (family questions)
        {"from_cat": "daily_life", "to_cat": "family_parenting", "keywords": ["family teamwork", "family ritual"]},
        
        # Daily Life → Philosophy Values (principled questions)
        {"from_cat": "daily_life", "to_cat": "philosophy_values", "keywords": ["principled stands"]},
        
        # Education → Philosophy Values (moral choice questions)
        {"from_cat": "education", "to_cat": "philosophy_values", "keywords": ["available choices are ethically"]},
        
        # Family Parenting → Philosophy Values (spiritual/philosophical questions)
        {"from_cat": "family_parenting", "to_cat": "philosophy_values", "keywords": ["spiritual or philosophical", "profit and principles"]},
        
        # Family Parenting → Hobbies (hobby time questions)
        {"from_cat": "family_parenting", "to_cat": "hobbies", "keywords": ["hobby time with family"]},
        
        # Friendships Social → Hobbies (hobby friendship questions)
        {"from_cat": "friendships_social", "to_cat": "hobbies", "keywords": ["friendship within hobby", "competitive elements in social hobby", "hobby social ritual"]},
        
        # Hobbies → Philosophy Values (moral questions)
        {"from_cat": "hobbies", "to_cat": "philosophy_values", "keywords": ["moral conviction", "empathy play in your moral", "forgiveness play in your approach to moral"]},
        
        # Marriage Partnerships → Family Parenting (family planning questions)
        {"from_cat": "marriage_partnerships", "to_cat": "family_parenting", "keywords": ["family planning", "extended family relationships"]},
        
        # Marriage Partnerships → Philosophy Values (spiritual questions)
        {"from_cat": "marriage_partnerships", "to_cat": "philosophy_values", "keywords": ["spiritual or philosophical development"]},
        
        # Personal → Philosophy Values (ethics questions)
        {"from_cat": "personal", "to_cat": "philosophy_values", "keywords": ["personal ethics", "moral dilemma"]},
        
        # Personal → Family Parenting (family development questions)
        {"from_cat": "personal", "to_cat": "family_parenting", "keywords": ["family play in individual personal development"]},
        
        # Philosophy Values → Family Parenting (family shaping values questions)
        {"from_cat": "philosophy_values", "to_cat": "family_parenting", "keywords": ["family helped shape your values", "family influenced your spiritual"]},
        
        # Relationships → Professional (workplace relationship questions)
        {"from_cat": "relationships", "to_cat": "professional", "keywords": ["workplace relationship"]},
        
        # Relationships → Philosophy Values (law and morality questions)
        {"from_cat": "relationships", "to_cat": "philosophy_values", "keywords": ["relationship between law and moral"]},
        
        # Romantic Love → Family Parenting (family love questions)
        {"from_cat": "romantic_love", "to_cat": "family_parenting", "keywords": ["love to family members", "family discipline with love", "family background influenced your approach to l"]}
    ]
    
    for question in questions:
        original_category = question['category']
        question_text = question['question'].lower()
        
        # Check each fix pattern
        for fix in fixes:
            if (question['category'] == fix['from_cat'] and 
                any(keyword.lower() in question_text for keyword in fix['keywords'])):
                
                question['category'] = fix['to_cat']
                print(f"✓ Moved: \"{question['question'][:60]}...\"")
                print(f"  {fix['from_cat']} → {fix['to_cat']}")
                fixes_made += 1
                break
    
    print(f"\n📊 FIXES APPLIED: {fixes_made}")
    
    # Show final distribution
    from collections import Counter
    final_counts = Counter(q['category'] for q in questions)
    
    print(f"\n📂 FINAL CATEGORY DISTRIBUTION:")
    for cat in sorted(final_counts.keys()):
        print(f"  {cat}: {final_counts[cat]} questions")
    
    # Save the corrected questions
    save_questions(questions)
    print(f"\n💾 Saved corrected questions to src/data/questions.json")
    print(f"✅ Category misalignment fixes complete!")

if __name__ == "__main__":
    main()