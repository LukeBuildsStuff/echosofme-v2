#!/usr/bin/env python3
"""
Agent Verification Audit Script
Thoroughly verifies claims about Echos of Me database cleanup
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

def load_json_file(filepath):
    """Load and parse JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading {filepath}: {e}")
        return None

def analyze_questions_file(filepath, label=""):
    """Comprehensive analysis of questions file"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {label} ({filepath})")
    print(f"{'='*60}")

    data = load_json_file(filepath)
    if not data:
        return None

    # Handle different file formats
    if isinstance(data, list):
        # New format: array of question objects
        return analyze_array_format(data, label)
    elif isinstance(data, dict) and 'categories' in data:
        # Old format: categorized structure
        return analyze_categorized_format(data, label)
    else:
        print("ERROR: Unknown file format")
        return None

def analyze_array_format(data, label=""):
    """Analyze array format questions file"""
    print(f"Format: Array of question objects")
    print(f"Total questions found: {len(data)}")

    # Group by category
    categories = defaultdict(list)
    all_questions = []
    category_stats = {}
    duplicates_by_category = {}

    for item in data:
        if not isinstance(item, dict) or 'question' not in item or 'category' not in item:
            print(f"WARNING: Invalid question object: {item}")
            continue

        question_text = item['question'].strip().lower()
        category = item['category']
        categories[category].append(question_text)
        all_questions.append(question_text)

    print(f"Categories found: {len(categories)}")

    # Analyze each category
    for cat_name, questions in categories.items():
        cat_questions = [q for q in questions if q.strip()]
        category_stats[cat_name] = {
            'total': len(questions),
            'valid': len(cat_questions),
            'duplicates_in_category': len(cat_questions) - len(set(cat_questions))
        }

        # Find duplicates within category
        question_counts = Counter(cat_questions)
        category_duplicates = {q: count for q, count in question_counts.items() if count > 1}
        duplicates_by_category[cat_name] = category_duplicates

    return analyze_questions_common(all_questions, category_stats, duplicates_by_category, len(categories))

def analyze_categorized_format(data, label=""):
    """Analyze old categorized format"""
    categories = data['categories']
    print(f"Format: Categorized structure")
    print(f"Total categories found: {len(categories)}")

    total_questions = 0
    category_stats = {}
    all_questions = []
    duplicates_by_category = {}

    # Analyze each category
    for cat_name, questions in categories.items():
        if not isinstance(questions, list):
            print(f"WARNING: Category '{cat_name}' is not a list")
            continue

        cat_questions = [q.strip().lower() for q in questions if isinstance(q, str) and q.strip()]
        category_stats[cat_name] = {
            'total': len(questions),
            'valid': len(cat_questions),
            'duplicates_in_category': len(cat_questions) - len(set(cat_questions))
        }

        # Find duplicates within category
        question_counts = Counter(cat_questions)
        category_duplicates = {q: count for q, count in question_counts.items() if count > 1}
        duplicates_by_category[cat_name] = category_duplicates

        total_questions += len(cat_questions)
        all_questions.extend(cat_questions)

    return analyze_questions_common(all_questions, category_stats, duplicates_by_category, len(categories))

def analyze_questions_common(all_questions, category_stats, duplicates_by_category, categories_count):
    """Common analysis logic for both formats"""

    # Cross-category duplicate analysis
    all_question_counts = Counter(all_questions)
    cross_category_duplicates = {q: count for q, count in all_question_counts.items() if count > 1}

    # Summary statistics
    unique_questions = len(set(all_questions))
    total_duplicates = len(all_questions) - unique_questions

    print(f"\nQUESTION COUNT ANALYSIS:")
    print(f"Total questions (all categories): {len(all_questions)}")
    print(f"Unique questions: {unique_questions}")
    print(f"Total duplicates: {total_duplicates}")

    print(f"\nCATEGORY BREAKDOWN:")
    for cat_name, stats in category_stats.items():
        dupes = stats['duplicates_in_category']
        print(f"  {cat_name}: {stats['valid']} questions ({dupes} internal duplicates)")

    # Report duplicates if any exist
    if total_duplicates > 0:
        print(f"\n🚨 DUPLICATE DETECTION RESULTS:")
        print(f"Found {total_duplicates} total duplicates!")

        # Within-category duplicates
        within_cat_dupes = 0
        for cat_name, dupes in duplicates_by_category.items():
            if dupes:
                within_cat_dupes += sum(count - 1 for count in dupes.values())
                print(f"\n  Category '{cat_name}' internal duplicates:")
                for question, count in dupes.items():
                    print(f"    '{question[:80]}...' appears {count} times")

        # Cross-category duplicates
        cross_cat_dupes = len([q for q, count in cross_category_duplicates.items() if count > 1])
        if cross_cat_dupes > 0:
            print(f"\n  Cross-category duplicates ({cross_cat_dupes} unique questions):")
            for question, count in list(cross_category_duplicates.items())[:10]:  # Show first 10
                print(f"    '{question[:80]}...' appears in {count} categories")
            if cross_cat_dupes > 10:
                print(f"    ... and {cross_cat_dupes - 10} more")
    else:
        print(f"\n✅ NO DUPLICATES FOUND - Database is clean!")

    return {
        'total_questions': len(all_questions),
        'unique_questions': unique_questions,
        'total_duplicates': total_duplicates,
        'categories_count': categories_count,
        'category_stats': category_stats,
        'duplicates_by_category': duplicates_by_category,
        'cross_category_duplicates': cross_category_duplicates
    }

def compare_files(current_file, backup_file):
    """Compare current state with backup to verify cleanup claims"""
    print(f"\n{'='*60}")
    print(f"COMPARISON ANALYSIS")
    print(f"{'='*60}")

    current_analysis = analyze_questions_file(current_file, "CURRENT STATE")
    backup_analysis = analyze_questions_file(backup_file, "BACKUP STATE")

    if not current_analysis or not backup_analysis:
        print("ERROR: Could not compare files")
        return

    print(f"\n📊 BEFORE vs AFTER COMPARISON:")
    print(f"Backup total questions: {backup_analysis['total_questions']}")
    print(f"Backup duplicates: {backup_analysis['total_duplicates']}")
    print(f"Current total questions: {current_analysis['total_questions']}")
    print(f"Current duplicates: {current_analysis['total_duplicates']}")

    duplicate_reduction = backup_analysis['total_duplicates'] - current_analysis['total_duplicates']
    print(f"Duplicate reduction: {duplicate_reduction}")

    return current_analysis, backup_analysis

def main():
    """Main audit function"""
    print("🔍 AGENT VERIFICATION AUDIT")
    print("Investigating claims about Echos of Me database cleanup")

    # Define file paths
    current_file = "/home/luke/echosofme-v2/src/data/questions.json"
    backup_file = "/home/luke/echosofme-v2/questions_backup_20250905_102723.json"

    # Verify current state
    current_analysis = analyze_questions_file(current_file, "CURRENT DATABASE STATE")

    if not current_analysis:
        print("CRITICAL ERROR: Cannot analyze current database")
        return

    # Verify backup for comparison
    if Path(backup_file).exists():
        print(f"\nFound backup file for comparison: {backup_file}")
        compare_files(current_file, backup_file)
    else:
        print(f"WARNING: Backup file not found: {backup_file}")

    # Final verdict
    print(f"\n{'='*60}")
    print(f"FINAL AUDIT VERDICT")
    print(f"{'='*60}")

    claims = {
        "17_categories_clean": current_analysis['categories_count'] == 17 and current_analysis['total_duplicates'] == 0,
        "3590_total_questions": current_analysis['total_questions'] == 3590,
        "zero_duplicates": current_analysis['total_duplicates'] == 0,
        "all_unique": current_analysis['unique_questions'] == current_analysis['total_questions']
    }

    print(f"CLAIM VERIFICATION:")
    print(f"✅ 17 categories exist: {current_analysis['categories_count'] == 17}")
    print(f"✅ All categories clean (0 duplicates): {current_analysis['total_duplicates'] == 0}")
    print(f"✅ Total questions = 3,590: {current_analysis['total_questions'] == 3590}")
    print(f"✅ All questions unique: {current_analysis['unique_questions'] == current_analysis['total_questions']}")

    if all(claims.values()):
        print(f"\n🎉 ALL CLAIMS VERIFIED - Agent was truthful!")
    else:
        print(f"\n🚨 FALSE CLAIMS DETECTED!")
        for claim, verified in claims.items():
            if not verified:
                print(f"   ❌ {claim}: FAILED")

if __name__ == "__main__":
    main()