#!/usr/bin/env python3
"""
Simple audit to verify key claims
"""

import json
from collections import Counter

# Load current file
with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
    current_data = json.load(f)

# Load backup file
with open('/home/luke/echosofme-v2/questions_backup_20250905_102723.json', 'r') as f:
    backup_data = json.load(f)

print("🔍 SIMPLE AUDIT VERIFICATION")
print("="*60)

# Current analysis
current_questions = [item['question'].lower().strip() for item in current_data]
current_categories = set(item['category'] for item in current_data)
current_unique = len(set(current_questions))
current_duplicates = len(current_questions) - current_unique

print(f"CURRENT STATE:")
print(f"  Total questions: {len(current_questions)}")
print(f"  Unique questions: {current_unique}")
print(f"  Duplicates: {current_duplicates}")
print(f"  Categories: {len(current_categories)}")
print(f"  Category list: {sorted(current_categories)}")

# Backup analysis (assuming it's in old format)
if isinstance(backup_data, dict) and 'categories' in backup_data:
    backup_questions = []
    for cat, questions in backup_data['categories'].items():
        backup_questions.extend([q.lower().strip() for q in questions if isinstance(q, str)])
    backup_categories = len(backup_data['categories'])
else:
    # Handle if backup is also in new format
    backup_questions = [item['question'].lower().strip() for item in backup_data]
    backup_categories = len(set(item['category'] for item in backup_data))

backup_unique = len(set(backup_questions))
backup_duplicates = len(backup_questions) - backup_unique

print(f"\nBACKUP STATE:")
print(f"  Total questions: {len(backup_questions)}")
print(f"  Unique questions: {backup_unique}")
print(f"  Duplicates: {backup_duplicates}")
print(f"  Categories: {backup_categories}")

print(f"\nCHANGES:")
print(f"  Question difference: {len(current_questions) - len(backup_questions)}")
print(f"  Duplicate reduction: {backup_duplicates - current_duplicates}")

print(f"\nCLAIM VERIFICATION:")
print(f"✅ 17 categories: {len(current_categories) == 17} (Found: {len(current_categories)})")
print(f"❌ 3,590 total questions: {len(current_questions) == 3590} (Found: {len(current_questions)})")
print(f"❌ Zero duplicates: {current_duplicates == 0} (Found: {current_duplicates})")
print(f"❌ All unique: {current_unique == len(current_questions)} (Found: {current_unique}/{len(current_questions)})")

# Show some duplicates as evidence
if current_duplicates > 0:
    print(f"\nEXAMPLE DUPLICATES:")
    question_counts = Counter(current_questions)
    dupes = [(q, count) for q, count in question_counts.items() if count > 1]
    for question, count in dupes[:5]:  # Show first 5
        print(f"  '{question[:60]}...' appears {count} times")

print(f"\n🚨 AGENT CLAIMS ASSESSMENT:")
if len(current_categories) == 17:
    print(f"✅ CORRECT: 17 categories exist")
else:
    print(f"❌ FALSE: Claimed 17 categories, found {len(current_categories)}")

if len(current_questions) == 3590:
    print(f"✅ CORRECT: 3,590 total questions")
else:
    print(f"❌ FALSE: Claimed 3,590 questions, found {len(current_questions)}")

if current_duplicates == 0:
    print(f"✅ CORRECT: Zero duplicates")
else:
    print(f"❌ FALSE: Claimed zero duplicates, found {current_duplicates}")

if backup_duplicates > 1000:
    reduction = backup_duplicates - current_duplicates
    print(f"✅ PARTIAL: Duplicates reduced from {backup_duplicates} to {current_duplicates} (reduction: {reduction})")
else:
    print(f"⚠️  UNKNOWN: Cannot verify original duplicate count from backup")