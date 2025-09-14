#!/usr/bin/env python3
"""
Database Question Sync Script
Safely syncs questions table with JSON file for orphaned reflections.
"""

import json
import psycopg2
import os
from datetime import datetime

# Question IDs that are used in reflections but missing from database
NEEDED_QUESTION_IDS = [6, 62, 63, 76, 96, 98, 107, 139, 148, 156, 157, 158, 174, 183, 188, 199, 210, 228, 240, 272, 286, 327, 361, 411, 440, 581, 605, 649, 700, 719, 732, 750, 802, 813, 820, 841, 842, 1109, 1419, 1510, 1517, 1520, 1568, 1999, 2168, 2262, 2341, 2346, 2358, 2373, 2442, 2593, 2615, 2757, 2802, 2840, 2874, 3077, 3119, 3170, 3171, 3172, 3218, 3238, 3241, 3314, 3359, 3375, 3394, 3398, 3473, 3482, 3507, 3512, 4000, 4001, 4002, 4003, 4004, 4005, 4006, 4007, 4009, 5000, 5077, 5407, 5489, 5512]

MISSING_IDS = [2593, 5407]  # These don't exist in JSON and need manual creation

def get_db_connection():
    """Get database connection using same method as API"""
    DATABASE_CONFIG = {
        'host': 'host.docker.internal',
        'database': 'echosofme_dev',
        'user': 'echosofme',
        'password': 'secure_dev_password',
        'port': 5432
    }
    return psycopg2.connect(**DATABASE_CONFIG)

def load_questions_json():
    """Load questions from JSON file"""
    with open('src/data/questions.json', 'r') as f:
        return json.load(f)

def create_missing_questions():
    """Create placeholder questions for missing IDs"""
    missing_questions = [
        {
            "id": 2593,
            "question": "What are your thoughts on personal growth and self-improvement?",
            "category": "personal_growth",
            "source": "manual_recovery"
        },
        {
            "id": 5407,
            "question": "How do you approach making difficult life decisions?",
            "category": "decision_making", 
            "source": "manual_recovery"
        }
    ]
    return {q["id"]: q for q in missing_questions}

def sync_questions(dry_run=True):
    """Sync questions table with JSON file for needed questions only"""
    print(f"🔄 Starting question sync ({'DRY RUN' if dry_run else 'LIVE RUN'})")
    
    # Load data
    questions_data = load_questions_json()
    questions_by_id = {q["id"]: q for q in questions_data if "id" in q and q.get("id") is not None}
    missing_questions = create_missing_questions()
    
    print(f"📊 Loaded {len(questions_by_id)} valid questions from JSON")
    
    # Combine questions
    all_questions = {**questions_by_id, **missing_questions}
    
    if dry_run:
        print("📊 DRY RUN ANALYSIS:")
        found = [id for id in NEEDED_QUESTION_IDS if id in all_questions]
        not_found = [id for id in NEEDED_QUESTION_IDS if id not in all_questions]
        
        print(f"✅ Questions found: {len(found)}")
        print(f"❌ Questions still missing: {len(not_found)}")
        if not_found:
            print(f"Missing: {not_found}")
        
        print(f"\n📝 Would insert {len(found)} questions")
        return
    
    # Connect to database
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check existing questions
            cur.execute("SELECT id FROM questions WHERE id = ANY(%s)", (NEEDED_QUESTION_IDS,))
            existing_ids = set(row[0] for row in cur.fetchall())
            
            to_insert = [id for id in NEEDED_QUESTION_IDS if id not in existing_ids and id in all_questions]
            
            print(f"📝 Inserting {len(to_insert)} questions...")
            
            inserted_count = 0
            for question_id in to_insert:
                question = all_questions[question_id]
                
                # Insert question
                cur.execute("""
                    INSERT INTO questions (id, question_text, category)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (question_id, question["question"], question["category"]))
                
                inserted_count += cur.rowcount
                
            conn.commit()
            print(f"✅ Successfully inserted {inserted_count} questions")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_sync():
    """Verify that all needed questions now exist"""
    print("🔍 Verifying sync...")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM questions WHERE id = ANY(%s)", (NEEDED_QUESTION_IDS,))
            found_ids = set(row[0] for row in cur.fetchall())
            
            missing = [id for id in NEEDED_QUESTION_IDS if id not in found_ids]
            
            print(f"✅ Questions in database: {len(found_ids)}")
            print(f"❌ Still missing: {len(missing)}")
            if missing:
                print(f"Missing IDs: {missing}")
            else:
                print("🎉 All needed questions are now in the database!")
                
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    print("🔧 Database Question Sync Tool")
    print("="*50)
    
    if "--dry-run" in sys.argv or len(sys.argv) == 1:
        sync_questions(dry_run=True)
    elif "--sync" in sys.argv:
        print("⚠️  LIVE RUN: This will modify the database!")
        if "--force" not in sys.argv:
            input("Press Enter to continue or Ctrl+C to abort...")
        sync_questions(dry_run=False)
        verify_sync()
    elif "--verify" in sys.argv:
        verify_sync()
    else:
        print("Usage:")
        print("  python3 sync_questions.py --dry-run   # Show what would be done")
        print("  python3 sync_questions.py --sync      # Actually sync the database")
        print("  python3 sync_questions.py --verify    # Verify current state")