#!/usr/bin/env python3
"""
Comprehensive recategorization script to fix category misalignments in questions database
"""

import json
import re
from collections import defaultdict, Counter

def load_questions():
    with open('src/data/questions.json', 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open('src/data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def analyze_question_category(question_text):
    """Analyze question text to determine the most appropriate category"""
    text = question_text.lower()
    
    # Define comprehensive keyword patterns for each category
    category_patterns = {
        'romantic_love': [
            r'\bromantic\b', r'\bromance\b', r'\blove\b', r'\blover\b', r'\bdating\b', r'\bdate\b',
            r'\battraction\b', r'\bintimacy\b', r'\bintimate\b', r'\bpassion\b', r'\baffection\b',
            r'\brelationship.*romantic\b', r'\bpartner.*romantic\b', r'\bheart\b.*\blove\b',
            r'\bfalling in love\b', r'\bfell in love\b', r'\bin love\b', r'\blove language\b'
        ],
        
        'marriage_partnerships': [
            r'\bmarriage\b', r'\bmarried\b', r'\bspouse\b', r'\bhusband\b', r'\bwife\b',
            r'\bpartnership\b', r'\bpartner\b(?!.*business)', r'\bwedding\b', r'\bengagement\b',
            r'\blong[- ]?term relationship\b', r'\bcommitted relationship\b', r'\blife partner\b'
        ],
        
        'family_parenting': [
            r'\bfamily\b', r'\bparent\b', r'\bparenting\b', r'\bmother\b', r'\bfather\b', r'\bmom\b', r'\bdad\b',
            r'\bchild\b', r'\bchildren\b', r'\bkids?\b', r'\bson\b', r'\bdaughter\b', r'\bsibling\b',
            r'\bbrother\b', r'\bsister\b', r'\bgrandparent\b', r'\bgrandchild\b', r'\bgeneration\b'
        ],
        
        'friendships_social': [
            r'\bfriend\b', r'\bfriendship\b', r'\bbuddy\b', r'\bcompanion\b', r'\bpeer\b',
            r'\bsocial\b', r'\bsocializing\b', r'\bsocial.*group\b', r'\bcommunity.*social\b'
        ],
        
        'relationships': [
            r'\brelationship\b(?!.*romantic)', r'\bconnection\b', r'\bbond\b', r'\brelate to\b',
            r'\brelating\b', r'\binterpersonal\b', r'\bhuman connection\b'
        ],
        
        'career': [
            r'\bcareer\b', r'\bjob\b', r'\bwork\b(?!.*home)', r'\bemployment\b', r'\bprofession\b',
            r'\boccupation\b', r'\bindustry\b', r'\bbusiness\b', r'\bcompany\b', r'\borganization\b',
            r'\bmanagement\b', r'\bleadership\b', r'\bteam\b', r'\bcolleague\b', r'\bboss\b', r'\bsupervisor\b'
        ],
        
        'professional': [
            r'\bprofessional\b', r'\bworkplace\b', r'\bcorporate\b', r'\boffice\b',
            r'\bprofessional development\b', r'\bprofessional growth\b', r'\bnetworking\b'
        ],
        
        'creative_expression': [
            r'\bcreative\b', r'\bcreativity\b', r'\bart\b', r'\bartist\b', r'\bartistic\b',
            r'\bmusic\b', r'\bpainting\b', r'\bdrawing\b', r'\bwriting\b', r'\bdesign\b',
            r'\bcraft\b', r'\bperform\b', r'\bperformance\b', r'\bexpress\b.*creativ',
            r'\bimagination\b', r'\bimagine\b.*creat', r'\bcreate\b', r'\bcreating\b'
        ],
        
        'hobbies': [
            r'\bhobby\b', r'\bhobbies\b', r'\bleisure\b', r'\bfun\b', r'\bpastime\b',
            r'\brecreation\b', r'\bentertainment\b', r'\bplay\b', r'\benjoying\b',
            r'\bfree time\b', r'\bspare time\b', r'\brelaxation\b'
        ],
        
        'education': [
            r'\beducation\b', r'\bschool\b', r'\bcollege\b', r'\buniversity\b', r'\bstudent\b',
            r'\bteacher\b', r'\bteaching\b', r'\blearn\b', r'\blearning\b', r'\bstudy\b',
            r'\bstudying\b', r'\bacademic\b', r'\bclass\b', r'\bcourse\b', r'\bknowledge\b'
        ],
        
        'personal': [
            r'\byourself\b', r'\byou feel\b', r'\bpersonal\b(?!.*history)', r'\bidentity\b',
            r'\bpersonality\b', r'\bself\b', r'\bindividual\b', r'\bwho you are\b',
            r'\byour.*nature\b', r'\byour.*character\b', r'\byour.*traits\b'
        ],
        
        'personal_history': [
            r'\bchildhood\b', r'\bgrew up\b', r'\bgrowing up\b', r'\bwhen you were\b',
            r'\bpast\b', r'\bmemory\b', r'\bmemories\b', r'\bremember\b', r'\bhistory\b',
            r'\bexperience\b.*past', r'\bfirst time\b', r'\byounger\b', r'\byears ago\b',
            r'\bback then\b', r'\bused to\b', r'\bonce\b.*time'
        ],
        
        'philosophy_values': [
            r'\bphilosophy\b', r'\bphilosophical\b', r'\bvalues?\b', r'\bethics?\b', r'\bethical\b',
            r'\bmoral\b', r'\bmorality\b', r'\bbelief\b', r'\bbeliefs\b', r'\bmeaning\b',
            r'\bpurpose\b', r'\bprinciple\b', r'\bvirtue\b', r'\bwisdom\b', r'\bmeaningful\b'
        ],
        
        'daily_life': [
            r'\bdaily\b', r'\beveryday\b', r'\broutine\b', r'\bregular\b', r'\bhabit\b',
            r'\bmorning\b', r'\bevening\b', r'\bhome\b', r'\bhousehold\b', r'\bchore\b',
            r'\bliving space\b', r'\bdaily life\b'
        ],
        
        'hypotheticals': [
            r'\bif you could\b', r'\bwould you rather\b', r'\bwhat if\b', r'\bimagine if\b',
            r'\bsuppose\b', r'\bhypothetical\b', r'\bwould you\b.*choose'
        ]
    }
    
    # Score each category
    category_scores = defaultdict(int)
    
    for category, patterns in category_patterns.items():
        for pattern in patterns:
            matches = len(re.findall(pattern, text))
            if matches > 0:
                category_scores[category] += matches * 10  # Weight pattern matches heavily
    
    # Additional context scoring
    if 'work' in text and ('professional' in text or 'career' in text or 'job' in text):
        category_scores['career'] += 5
        category_scores['professional'] += 5
        
    if 'relationship' in text and ('romantic' in text or 'love' in text or 'partner' in text):
        category_scores['romantic_love'] += 8
        
    if 'family' in text and ('parent' in text or 'child' in text):
        category_scores['family_parenting'] += 8
        
    # Return the highest scoring category, or None if no clear match
    if category_scores:
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    return None

def main():
    print("🔍 COMPREHENSIVE QUESTION RECATEGORIZATION")
    print("=" * 50)
    
    # Load questions
    questions = load_questions()
    print(f"Loaded {len(questions)} questions")
    
    # Track changes
    changes = []
    category_counts_before = Counter(q['category'] for q in questions)
    
    print("\n📊 BEFORE RECATEGORIZATION:")
    for cat in sorted(category_counts_before.keys()):
        print(f"  {cat}: {category_counts_before[cat]} questions")
    
    print("\n🔄 ANALYZING AND RECATEGORIZING...")
    
    # Process each question
    for i, question in enumerate(questions):
        current_category = question['category']
        suggested_category = analyze_question_category(question['question'])
        
        # Skip if no suggestion or same as current
        if not suggested_category or suggested_category == current_category:
            continue
            
        # Skip journal category (special case)
        if current_category == 'journal':
            continue
            
        # Record the change
        changes.append({
            'question': question['question'][:100],
            'from': current_category,
            'to': suggested_category,
            'index': i
        })
        
        # Apply the change
        questions[i]['category'] = suggested_category
    
    print(f"\n📝 CHANGES MADE: {len(changes)}")
    if changes:
        print("\nFirst 20 changes:")
        for change in changes[:20]:
            print(f"  '{change['question']}...'")
            print(f"    {change['from']} → {change['to']}")
            print()
    
    # Show final distribution
    category_counts_after = Counter(q['category'] for q in questions)
    
    print("\n📊 AFTER RECATEGORIZATION:")
    for cat in sorted(category_counts_after.keys()):
        change = category_counts_after[cat] - category_counts_before.get(cat, 0)
        change_str = f" ({change:+d})" if change != 0 else ""
        print(f"  {cat}: {category_counts_after[cat]} questions{change_str}")
    
    # Save the recategorized questions
    save_questions(questions)
    print(f"\n💾 Saved recategorized questions to src/data/questions.json")
    
    print(f"\n✅ RECATEGORIZATION COMPLETE")
    print(f"Total questions processed: {len(questions)}")
    print(f"Questions recategorized: {len(changes)}")

if __name__ == "__main__":
    main()