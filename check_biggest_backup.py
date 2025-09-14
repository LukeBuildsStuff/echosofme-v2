#!/usr/bin/env python3
"""
Check the biggest backup to see original duplicate state
"""

import json
from collections import Counter

# Try the biggest backup file
backup_file = "/home/luke/echosofme-v2/src/data/questions_backup_before_rebalance_20250831_134316.json"

print(f"🔍 CHECKING LARGEST BACKUP: {backup_file}")
print("="*60)

with open(backup_file, 'r') as f:
    backup_data = json.load(f)

# Handle different formats
if isinstance(backup_data, dict) and 'categories' in backup_data:
    backup_questions = []
    for cat, questions in backup_data['categories'].items():
        backup_questions.extend([q.lower().strip() for q in questions if isinstance(q, str)])
    backup_categories = len(backup_data['categories'])
    print(f"Format: Categorized structure")
    print(f"Categories: {backup_categories}")
    for cat, questions in backup_data['categories'].items():
        print(f"  {cat}: {len(questions)} questions")
else:
    backup_questions = [item['question'].lower().strip() for item in backup_data]
    backup_categories = len(set(item['category'] for item in backup_data))
    print(f"Format: Array structure")

backup_unique = len(set(backup_questions))
backup_duplicates = len(backup_questions) - backup_unique

print(f"\nBACKUP STATISTICS:")
print(f"  Total questions: {len(backup_questions)}")
print(f"  Unique questions: {backup_unique}")
print(f"  Total duplicates: {backup_duplicates}")

# Show sample duplicates
if backup_duplicates > 0:
    question_counts = Counter(backup_questions)
    dupes = [(q, count) for q, count in question_counts.items() if count > 1]
    print(f"\nSAMPLE DUPLICATES FROM BACKUP:")
    for question, count in dupes[:5]:
        print(f"  '{question[:60]}...' appears {count} times")

# Load current for comparison
with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
    current_data = json.load(f)

current_questions = [item['question'].lower().strip() for item in current_data]
current_unique = len(set(current_questions))
current_duplicates = len(current_questions) - current_unique

print(f"\nCOMPARISON:")
print(f"Backup -> Current")
print(f"Total: {len(backup_questions)} -> {len(current_questions)} (diff: {len(current_questions) - len(backup_questions)})")
print(f"Duplicates: {backup_duplicates} -> {current_duplicates} (reduction: {backup_duplicates - current_duplicates})")

print(f"\nFINAL ASSESSMENT:")
if backup_duplicates > 1000 and current_duplicates > 0:
    print(f"❌ CLAIM PARTIALLY FALSE: Agent reduced duplicates from {backup_duplicates} to {current_duplicates}, but did NOT achieve zero duplicates as claimed")
elif backup_duplicates > current_duplicates:
    print(f"✅ PROGRESS MADE: Duplicates reduced from {backup_duplicates} to {current_duplicates}")
else:
    print(f"⚠️  UNCLEAR: Cannot determine original duplicate state")