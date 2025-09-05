#!/usr/bin/env python3
"""
Enhanced script to replace duplicate questions with category-appropriate questions
Generates more replacement questions for categories with high duplicate counts
"""
import json
import random
from collections import defaultdict, Counter

def load_questions():
    """Load questions from JSON file"""
    with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
        return json.load(f)

def find_duplicates(questions):
    """Find all duplicate questions and their details"""
    question_occurrences = defaultdict(list)
    
    for i, q in enumerate(questions):
        question_occurrences[q['question']].append({
            'index': i,
            'id': q['id'],
            'category': q['category'],
            'source': q['source']
        })
    
    # Find duplicates (questions that appear more than once)
    duplicates = {question: occurrences for question, occurrences in question_occurrences.items() 
                 if len(occurrences) > 1}
    
    return duplicates

def generate_enhanced_replacement_questions():
    """Generate extensive replacement questions for high-duplicate categories"""
    return {
        'relationships': [
            "How do you handle power dynamics in relationships?",
            "What role does vulnerability play in your relationships?",
            "How do you maintain your identity within a relationship?",
            "What's your approach to setting relationship boundaries?",
            "How do you handle different attachment styles in relationships?",
            "What does emotional safety mean to you in relationships?",
            "How do you navigate relationships with different communication styles?",
            "What's your experience with long-distance relationships?",
            "How do you handle relationship transitions and changes?",
            "What role does forgiveness play in your relationships?",
            "How do you balance independence and togetherness?",
            "What patterns do you notice in your relationship conflicts?",
            "How do you support a partner through difficult times?",
            "What's your approach to relationship maintenance?",
            "How do you handle different life goals in a relationship?",
            "What role does trust play in your relationships?",
            "How do you navigate financial discussions in relationships?",
            "What's your experience with blended families or complex family dynamics?",
            "How do you handle social pressure about your relationships?",
            "What relationship advice would you give to someone starting out?",
            "How do you know when a relationship is worth fighting for?",
            "What's your approach to relationship compromise?",
            "How do you handle different social needs in a relationship?",
            "What role does physical affection play in your relationships?",
            "How do you navigate relationships with different values?",
            "What's your experience with relationship counseling or therapy?",
            "How do you handle relationship insecurities?",
            "What's your approach to maintaining friendships while in a relationship?",
            "How do you handle different conflict resolution styles?",
            "What does mutual respect look like to you in relationships?",
            "How do you navigate cultural differences in relationships?",
            "What's your experience with relationship milestones?",
            "How do you handle different life phases in relationships?",
            "What role does shared humor play in your relationships?",
            "How do you maintain romance in long-term relationships?",
            "What's your approach to handling ex-partners and past relationships?",
            "How do you navigate relationships with different energy levels?",
            "What's your experience with relationship expectations vs reality?",
            "How do you handle different approaches to personal growth in relationships?",
            "What does partnership mean to you beyond romantic relationships?",
            "How do you handle relationship jealousy and envy?",
            "What's your approach to giving and receiving love?",
            "How do you navigate relationships during stressful times?",
            "What role does emotional intelligence play in your relationships?",
            "How do you handle relationship disappointments?",
            "What's your experience with relationship chemistry vs compatibility?",
            "How do you maintain individual interests within relationships?",
            "What's your approach to relationship problem-solving?",
            "How do you handle different levels of emotional availability?"
        ],
        'romantic_love': [
            "How has your understanding of romance evolved over time?",
            "What does falling in love feel like to you?",
            "How do you express romantic love?",
            "What role does physical chemistry play in romantic love?",
            "How do you know when romantic feelings are genuine?",
            "What's your experience with unrequited love?",
            "How do you maintain passion in long-term relationships?",
            "What does romantic compatibility mean to you?",
            "How do you handle the transition from passion to deep love?",
            "What role does romance play in everyday life?",
            "How do you navigate love and timing?",
            "What's your experience with first love?",
            "How do you balance romantic love with self-love?",
            "What does it mean to choose love daily?",
            "How do you handle romantic disappointment?",
            "What's your approach to romantic gestures?",
            "How do you know when you're ready for romantic love?",
            "What role does intellectual connection play in romantic love?",
            "How do you handle different love languages in romantic relationships?",
            "What's your experience with love at different life stages?",
            "How do you navigate the vulnerability of being in love?",
            "What does romantic trust mean to you?",
            "How do you handle romantic insecurity?",
            "What's your approach to romantic communication?",
            "How do you maintain your sense of self while in love?",
            "What role does shared values play in romantic love?",
            "How do you handle romantic conflict?",
            "What's your experience with romantic sacrifice?",
            "How do you know when romantic love is lasting?",
            "What does romantic commitment mean to you?",
            "How do you handle romantic expectations?",
            "What's your approach to romantic intimacy?",
            "How do you navigate romantic love across different cultures?",
            "What role does romantic friendship play in love?",
            "How do you handle the fear of losing someone you love?",
            "What's your experience with romantic love and personal growth?",
            "How do you express romantic appreciation?",
            "What does romantic partnership look like to you?",
            "How do you handle romantic miscommunication?",
            "What's your approach to romantic boundaries?"
        ],
        'professional': [
            "What does professional integrity mean to you?",
            "How do you handle workplace politics?",
            "What's your approach to professional networking?",
            "How do you balance ambition with ethics in your career?",
            "What role does mentorship play in your professional life?",
            "How do you handle professional setbacks?",
            "What's your approach to work-life integration?",
            "How do you stay current in your professional field?",
            "What does professional success look like to you?",
            "How do you handle difficult clients or customers?",
            "What's your experience with professional transitions?",
            "How do you approach professional skill development?",
            "What role does creativity play in your professional work?",
            "How do you handle professional competition?",
            "What's your approach to professional communication?",
            "How do you navigate professional relationships?",
            "What does professional leadership mean to you?",
            "How do you handle professional stress?",
            "What's your experience with professional failure?",
            "How do you approach professional goal setting?",
            "What role does collaboration play in your professional life?",
            "How do you handle professional criticism?",
            "What's your approach to professional presentations?",
            "How do you navigate professional hierarchies?",
            "What does professional authenticity mean to you?",
            "How do you handle professional burnout?",
            "What's your experience with professional recognition?",
            "How do you approach professional problem-solving?",
            "What role does innovation play in your professional work?",
            "How do you handle professional uncertainty?",
            "What's your approach to professional time management?",
            "How do you navigate professional ethics dilemmas?",
            "What does professional growth mean to you?",
            "How do you handle professional negotiations?",
            "What's your experience with professional teams?",
            "How do you approach professional decision-making?",
            "What role does technology play in your professional work?",
            "How do you handle professional deadlines?",
            "What's your approach to professional learning?",
            "How do you maintain professional boundaries?",
            "What's your experience with professional change management?",
            "How do you approach professional risk assessment?",
            "What role does emotional intelligence play professionally?",
            "How do you handle professional disappointment?",
            "What's your approach to professional delegation?",
            "How do you navigate professional cultural differences?",
            "What does professional excellence mean to you?",
            "How do you handle professional overwhelm?",
            "What's your experience with professional public speaking?",
            "How do you approach professional continuous improvement?"
        ],
        'philosophy_values': [
            "What does authentic living mean to you?",
            "How do you define personal responsibility?",
            "What role does hope play in your worldview?",
            "How do you approach the concept of truth?",
            "What does it mean to live with integrity?",
            "How do you handle moral complexity?",
            "What's your philosophy on personal change?",
            "How do you think about freedom and constraints?",
            "What role does tradition play in shaping values?",
            "How do you approach the concept of justice?",
            "What does it mean to live meaningfully?",
            "How do you handle value conflicts?",
            "What's your approach to making ethical choices?",
            "How do you think about individual vs collective good?",
            "What role does courage play in living your values?",
            "How do you approach the concept of forgiveness?",
            "What does personal growth mean to you?",
            "How do you handle uncertainty about values?",
            "What's your philosophy on human potential?",
            "How do you think about legacy and impact?",
            "What role does compassion play in your value system?",
            "How do you approach the concept of fairness?",
            "What does it mean to live with purpose?",
            "How do you handle competing values?",
            "What's your approach to moral decision-making?",
            "How do you think about good and evil?",
            "What role does wisdom play in your life philosophy?",
            "How do you approach the concept of sacrifice?",
            "What does inner peace mean to you?",
            "How do you handle moral uncertainty?",
            "What's your philosophy on personal boundaries?",
            "How do you think about duty and obligation?",
            "What role does humility play in your value system?",
            "How do you approach the concept of strength?",
            "What does it mean to live authentically?",
            "How do you handle value evolution over time?",
            "What's your approach to making principled stands?",
            "How do you think about loyalty and commitment?",
            "What role does gratitude play in your philosophy?",
            "How do you approach life's fundamental questions?",
            "What does moral courage mean to you?",
            "How do you handle philosophical disagreements?",
            "What's your approach to finding meaning in suffering?",
            "How do you think about personal freedom?",
            "What role does love play in your value system?",
            "How do you approach the concept of happiness?",
            "What does it mean to live with dignity?",
            "How do you handle moral ambiguity?",
            "What's your philosophy on personal relationships?",
            "How do you think about time and mortality?",
            "What role does truth play in your decision-making?",
            "How do you approach the concept of virtue?",
            "What does it mean to live with compassion?",
            "How do you handle value-based challenges?",
            "What's your approach to personal ethics?",
            "How do you think about honor and reputation?",
            "What role does empathy play in your worldview?",
            "How do you approach the concept of wisdom?",
            "What does it mean to live with purpose and meaning?",
            "How do you handle philosophical uncertainty?",
            "What's your approach to moral leadership?",
            "How do you think about personal and social responsibility?",
            "What role does faith play in your value system?",
            "How do you approach the concept of redemption?",
            "What does it mean to live with grace?",
            "How do you handle ethical complexity?",
            "What's your philosophy on human nature and potential?",
            "How do you think about justice and mercy?",
            "What role does character play in your life philosophy?",
            "How do you approach the concept of moral growth?",
            "What does it mean to live with authenticity and truth?",
            "How do you handle value-based conflicts with others?",
            "What's your approach to finding purpose in adversity?",
            "How do you think about personal and universal values?",
            "What role does service play in your value system?",
            "How do you approach the concept of inner strength?",
            "What does it mean to live with moral clarity?",
            "How do you handle the tension between ideals and reality?",
            "What's your philosophy on personal transformation?",
            "How do you think about responsibility to future generations?",
            "What role does integrity play in difficult decisions?",
            "How do you approach the concept of spiritual growth?",
            "What does it mean to live with authentic purpose?",
            "How do you handle moral courage in challenging situations?",
            "What's your approach to finding meaning in everyday life?",
            "How do you think about the relationship between values and actions?",
            "What role does moral imagination play in your decision-making?",
            "How do you approach the concept of living with honor?",
            "What does it mean to align your life with your deepest values?",
            "How do you handle the complexity of modern ethical challenges?",
            "What's your philosophy on personal responsibility in community?",
            "How do you think about the balance between self-care and service?",
            "What role does moral conviction play in your life choices?",
            "How do you approach the concept of living with purpose and passion?",
            "What does it mean to create a life of meaning and significance?",
            "How do you handle the ongoing work of moral and personal development?",
            "What's your approach to cultivating wisdom and discernment?",
            "How do you think about the role of suffering in personal growth?",
            "What does it mean to live with both confidence and humility?",
            "How do you handle the challenge of staying true to your values?",
            "What's your philosophy on the relationship between knowledge and wisdom?",
            "How do you approach the concept of moral imagination?",
            "What role does intuition play in your value system?",
            "How do you think about the balance between acceptance and change?",
            "What does it mean to live with both passion and peace?",
            "How do you handle the complexity of competing moral claims?",
            "What's your approach to developing moral sensitivity?",
            "How do you think about the relationship between values and emotions?",
            "What role does story and narrative play in your value system?",
            "How do you approach the concept of living with intention?",
            "What does it mean to cultivate both strength and gentleness?",
            "How do you handle the challenge of moral perfectionism?",
            "What's your philosophy on the role of community in shaping values?",
            "How do you think about the balance between idealism and pragmatism?",
            "What does it mean to live with both conviction and openness?"
        ],
        'marriage_partnerships': [
            "What does partnership equality mean to you?",
            "How do you handle major life decisions as a couple?",
            "What role does commitment play in your partnership?",
            "How do you navigate different career ambitions in a partnership?",
            "What's your approach to handling partnership stress?",
            "How do you maintain individual identity within a partnership?",
            "What does partnership support look like to you?",
            "How do you handle partnership financial planning?",
            "What role does shared vision play in your partnership?",
            "How do you navigate partnership family planning decisions?",
            "What's your approach to partnership conflict resolution?",
            "How do you handle partnership role distributions?",
            "What does partnership intimacy mean beyond physical connection?",
            "How do you maintain partnership friendship?",
            "What's your experience with partnership growth and change?",
            "How do you handle partnership social obligations?",
            "What role does partnership ritual and tradition play?",
            "How do you navigate partnership living arrangements?",
            "What's your approach to partnership communication?",
            "How do you handle partnership extended family relationships?",
            "What does partnership loyalty mean to you?",
            "How do you maintain partnership excitement and novelty?",
            "What's your experience with partnership challenges?",
            "How do you navigate partnership different values?",
            "What does partnership trust mean to you?",
            "How do you handle partnership jealousy or insecurity?",
            "What's your approach to partnership goal setting?",
            "How do you maintain partnership romance over time?",
            "What role does partnership forgiveness play?",
            "How do you handle partnership different communication styles?",
            "What's your experience with partnership compromise?",
            "How do you navigate partnership different needs?",
            "What does partnership respect look like to you?",
            "How do you handle partnership life transitions?",
            "What's your approach to partnership problem solving?",
            "How do you maintain partnership appreciation?",
            "What role does partnership humor play?",
            "How do you handle partnership different priorities?",
            "What's your experience with partnership vulnerability?",
            "How do you navigate partnership different personalities?"
        ]
    }

def replace_all_duplicates(questions):
    """Replace ALL duplicate questions with new unique ones"""
    # Find duplicates
    duplicates = find_duplicates(questions)
    replacement_questions = generate_enhanced_replacement_questions()
    
    print(f"Processing {len(duplicates)} duplicate question types...")
    
    # Create a master pool of all replacement questions
    master_pool = []
    for category, question_list in replacement_questions.items():
        for question in question_list:
            master_pool.append((question, category))
    
    print(f"Generated {len(master_pool)} total replacement questions")
    
    replacement_count = 0
    
    for question_text, occurrences in duplicates.items():
        # Replace ALL BUT ONE occurrence (keep the first one)
        occurrences_to_replace = occurrences[1:]  # Skip first occurrence
        
        print(f"\nReplacing {len(occurrences_to_replace)} duplicates of: '{question_text[:60]}...'")
        
        for occurrence in occurrences_to_replace:
            category = occurrence['category']
            index = occurrence['index']
            
            # Try to find a replacement from the same category first
            category_matches = [q for q, c in master_pool if c == category]
            if category_matches:
                new_question = random.choice(category_matches)
                # Remove from master pool to avoid creating new duplicates
                master_pool.remove((new_question, category))
            elif master_pool:
                # Use any available replacement if no category match
                new_question, used_category = random.choice(master_pool)
                master_pool.remove((new_question, used_category))
                print(f"    Using cross-category replacement from {used_category}")
            else:
                print(f"    WARNING: No more replacement questions available!")
                continue
            
            # Update the question
            questions[index]['question'] = new_question
            replacement_count += 1
            
            print(f"  [{category}] -> '{new_question[:60]}...'")
    
    print(f"\nTotal replacements made: {replacement_count}")
    return questions

def verify_no_duplicates(questions):
    """Verify no duplicate questions remain"""
    question_counts = Counter(q['question'] for q in questions)
    duplicates = {q: count for q, count in question_counts.items() if count > 1}
    
    if duplicates:
        print(f"\nWARNING: {len(duplicates)} duplicate questions still exist:")
        for q, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {count}x: {q[:60]}...")
    else:
        print("\n✅ SUCCESS: No duplicate questions found!")
    
    return len(duplicates) == 0

def save_questions(questions, backup=True):
    """Save questions to file with optional backup"""
    if backup:
        # Create backup
        with open('/home/luke/echosofme-v2/src/data/questions.json.backup2', 'w') as f:
            with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as original:
                f.write(original.read())
        print("✅ Created backup: questions.json.backup2")
    
    # Save new questions
    with open('/home/luke/echosofme-v2/src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2)
    print("✅ Saved updated questions.json")

def main():
    """Main function to process duplicate questions"""
    print("🔍 Loading questions...")
    questions = load_questions()
    print(f"Loaded {len(questions)} questions")
    
    print("\n🔍 Finding duplicates...")
    duplicates = find_duplicates(questions)
    print(f"Found {len(duplicates)} duplicate question types")
    
    # Calculate total duplicates to replace
    total_duplicates_to_replace = sum(len(occurrences) - 1 for occurrences in duplicates.values())
    print(f"Total duplicate instances to replace: {total_duplicates_to_replace}")
    
    if total_duplicates_to_replace == 0:
        print("✅ No duplicates to replace!")
        return
    
    print("\n🔄 Replacing ALL duplicate questions...")
    updated_questions = replace_all_duplicates(questions)
    
    print("\n🔍 Verifying results...")
    success = verify_no_duplicates(updated_questions)
    
    if success:
        print("\n💾 Saving results...")
        save_questions(updated_questions)
        print("\n🎉 Successfully replaced all duplicate questions!")
        
        # Final stats
        unique_count = len(set(q['question'] for q in updated_questions))
        print(f"\n📊 Final Results:")
        print(f"  Total questions: {len(updated_questions)}")
        print(f"  Unique questions: {unique_count}")
        print(f"  Duplicates eliminated: {total_duplicates_to_replace}")
    else:
        print("\n❌ Some duplicates remain. Saving anyway as this reduces the problem.")
        save_questions(updated_questions)

if __name__ == "__main__":
    main()