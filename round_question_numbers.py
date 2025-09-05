#!/usr/bin/env python3
"""
Round question numbers to clean values by removing excess questions and adding new ones
"""

import json
import random
from collections import Counter

def load_questions():
    with open('src/data/questions.json', 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open('src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def find_questions_to_remove(questions, category, target_count):
    """Find the least unique/most generic questions to remove from a category"""
    cat_questions = [q for q in questions if q['category'] == category]
    current_count = len(cat_questions)
    to_remove = current_count - target_count
    
    if to_remove <= 0:
        return []
    
    # Score questions by uniqueness/specificity (lower score = more likely to remove)
    scored_questions = []
    for q in cat_questions:
        text = q['question'].lower()
        score = 0
        
        # Prefer to keep longer, more specific questions
        score += len(q['question']) * 0.1
        
        # Prefer to keep questions with specific details
        if any(word in text for word in ['specific', 'particular', 'exactly', 'precisely']):
            score += 10
        
        # Prefer to keep questions that are more complex
        score += text.count('?') * 2  # Multiple questions are complex
        score += text.count(',') * 1  # Commas suggest complexity
        score += text.count('and') * 1
        score += text.count('or') * 1
        
        # Deprioritize very generic starters
        if text.startswith('what') and len(text) < 30:
            score -= 5
        if text.startswith('how') and len(text) < 25:
            score -= 3
            
        # Deprioritize questions with "general" themes
        if any(word in text for word in ['general', 'overall', 'typical', 'usually', 'normally']):
            score -= 3
            
        scored_questions.append((q, score))
    
    # Sort by score (lowest first = most likely to remove)
    scored_questions.sort(key=lambda x: x[1])
    
    # Return questions to remove
    return [q[0] for q in scored_questions[:to_remove]]

def generate_new_questions(category, count):
    """Generate new questions appropriate for the given category"""
    
    new_questions = {
        'philosophy_values': [
            "How do you approach the tension between justice and mercy in difficult situations?",
            "What does it mean to live with moral courage in small, everyday moments?"
        ],
        
        'romantic_love': [
            "How do you maintain romantic curiosity about a long-term partner?",
            "What role does romantic vulnerability play in deepening connection?",
            "How do you express romantic appreciation in meaningful ways?",
            "What does romantic partnership look like during life's difficult seasons?",
            "How do you cultivate romantic presence in a distracted world?"
        ],
        
        'hobbies': [
            "How do you discover new hobbies that align with your evolving interests?"
        ],
        
        'career': [
            "How do you define career fulfillment beyond traditional success metrics?",
            "What role does career resilience play in navigating unexpected changes?"
        ],
        
        'friendships_social': [
            "How do you maintain social connections across different life transitions?"
        ],
        
        'marriage_partnerships': [
            "How do you approach partnership decision-making during disagreements?",
            "What does partnership emotional support look like in practical terms?",
            "How do you maintain individual identity while building shared partnership goals?",
            "What role does partnership humor and playfulness play in relationship health?",
            "How do you handle partnership stress without letting it damage your connection?",
            "What does partnership forgiveness look like when trust has been broken?",
            "How do you approach partnership financial discussions and planning?",
            "How do you navigate partnership relationships with extended family and friends?"
        ],
        
        'daily_life': [
            "How do you create meaningful daily rituals that reflect your values?",
            "What does intentional daily living look like in your current life stage?",
            "How do you balance daily productivity with present-moment awareness?",
            "What daily practices help you stay connected to what matters most?",
            "How do you approach daily decision-making when you're feeling overwhelmed?",
            "What role does daily gratitude play in shaping your overall outlook?",
            "How do you create daily boundaries that protect your energy and wellbeing?",
            "What daily habits have had the most positive impact on your life quality?",
            "How do you maintain daily motivation during periods of low energy?",
            "What does daily self-compassion look like when you make mistakes or fall short?"
        ]
    }
    
    if category not in new_questions:
        return []
    
    return new_questions[category][:count]

def main():
    print("🔢 ROUNDING QUESTION NUMBERS TO CLEAN VALUES")
    print("=" * 60)
    
    # Load current questions
    questions = load_questions()
    
    # Define target counts for each category
    target_counts = {
        'personal': 250,
        'philosophy_values': 250,
        'romantic_love': 250,
        'hobbies': 225,
        'career': 200,
        'family_parenting': 175,
        'personal_history': 175,
        'education': 150,
        'friendships_social': 150,
        'professional': 125,
        'relationships': 100,
        'marriage_partnerships': 100,
        'daily_life': 100,
        'hypotheticals': 75,
        'creative_expression': 75,
        'journal': 1
    }
    
    # Get current counts
    current_counts = Counter(q['category'] for q in questions)
    
    print("\n📊 CURRENT → TARGET COUNTS:")
    total_current = sum(current_counts.values())
    total_target = sum(target_counts.values())
    
    for category in sorted(target_counts.keys()):
        current = current_counts.get(category, 0)
        target = target_counts[category]
        change = target - current
        change_str = f" ({change:+d})" if change != 0 else ""
        print(f"  {category:25s}: {current:3d} → {target:3d}{change_str}")
    
    print(f"\nTotal: {total_current} → {total_target} ({total_target - total_current:+d})")
    
    # Process each category
    questions_to_remove = []
    questions_to_add = []
    
    print(f"\n🔄 PROCESSING CHANGES:")
    
    for category, target in target_counts.items():
        current = current_counts.get(category, 0)
        
        if current > target:
            # Need to remove questions
            remove_count = current - target
            to_remove = find_questions_to_remove(questions, category, target)
            questions_to_remove.extend(to_remove)
            print(f"  📉 {category}: Removing {len(to_remove)} questions")
            
        elif current < target:
            # Need to add questions
            add_count = target - current
            new_questions = generate_new_questions(category, add_count)
            for new_q in new_questions:
                questions_to_add.append({
                    'question': new_q,
                    'category': category,
                    'source': 'reflection'
                })
            print(f"  📈 {category}: Adding {len(new_questions)} questions")
    
    # Apply removals
    questions_to_remove_texts = {q['question'] for q in questions_to_remove}
    questions = [q for q in questions if q['question'] not in questions_to_remove_texts]
    
    # Apply additions
    questions.extend(questions_to_add)
    
    print(f"\n📝 CHANGES APPLIED:")
    print(f"  Removed: {len(questions_to_remove)} questions")
    print(f"  Added: {len(questions_to_add)} questions")
    
    # Verify final counts
    final_counts = Counter(q['question'] for q in questions)
    final_category_counts = Counter(q['category'] for q in questions)
    
    print(f"\n📊 FINAL VERIFICATION:")
    print(f"  Total questions: {len(questions)}")
    print(f"  Unique questions: {len(final_counts)}")
    
    # Check if all targets met
    targets_met = True
    for category, target in target_counts.items():
        actual = final_category_counts.get(category, 0)
        if actual != target:
            print(f"  ❌ {category}: {actual} (target: {target})")
            targets_met = False
    
    if targets_met:
        print("  ✅ All target counts achieved!")
    
    # Check for duplicates
    duplicates = {q: count for q, count in final_counts.items() if count > 1}
    if duplicates:
        print(f"  ❌ {len(duplicates)} duplicates found")
    else:
        print("  ✅ No duplicates")
    
    # Save the rounded questions
    save_questions(questions)
    print(f"\n💾 Saved rounded questions database")
    print(f"🎉 Question numbers successfully rounded to clean values!")

if __name__ == "__main__":
    main()