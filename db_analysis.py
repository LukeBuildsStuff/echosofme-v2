#!/usr/bin/env python3
"""
Simple database integrity analysis for Echoes of Me
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev', 
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

def main():
    print("=== ECHOES OF ME DATABASE INTEGRITY ANALYSIS ===\n")
    
    # 1. Analyze JSON file
    print("1. QUESTIONS.JSON ANALYSIS")
    print("-" * 40)
    
    with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
        json_data = json.load(f)
    
    print(f"Total items in JSON: {len(json_data)}")
    
    json_ids = []
    items_without_id = []
    json_categories = {}
    
    for item in json_data:
        if 'id' in item:
            json_ids.append(item['id'])
        else:
            items_without_id.append(item)
        
        cat = item.get('category', 'unknown')
        json_categories[cat] = json_categories.get(cat, 0) + 1
    
    print(f"Items with IDs: {len(json_ids)}")
    print(f"Items without IDs: {len(items_without_id)}")
    
    if json_ids:
        print(f"JSON ID range: {min(json_ids)} - {max(json_ids)}")
        print(f"Unique JSON IDs: {len(set(json_ids))}")
        if len(json_ids) != len(set(json_ids)):
            print(f"Duplicate JSON IDs: {len(json_ids) - len(set(json_ids))}")
    
    print(f"JSON Categories: {list(json_categories.keys())}")
    
    # 2. Analyze Database
    print(f"\n2. DATABASE ANALYSIS")
    print("-" * 40)
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        with conn.cursor() as cur:
            # Get questions from database
            cur.execute("SELECT COUNT(*) as count FROM questions")
            db_question_count = cur.fetchone()['count']
            print(f"Total questions in database: {db_question_count}")
            
            cur.execute("SELECT id, question_text, category FROM questions ORDER BY id")
            db_questions = cur.fetchall()
            
            db_ids = [q['id'] for q in db_questions]
            db_categories = {}
            for q in db_questions:
                cat = q['category'] or 'unknown'
                db_categories[cat] = db_categories.get(cat, 0) + 1
            
            if db_ids:
                print(f"Database ID range: {min(db_ids)} - {max(db_ids)}")
                print(f"Database categories: {list(db_categories.keys())}")
            
            # Get responses
            cur.execute("SELECT DISTINCT question_id FROM responses ORDER BY question_id")
            response_question_ids = [r['question_id'] for r in cur.fetchall()]
            print(f"Question IDs referenced in responses: {len(response_question_ids)}")
            
            if response_question_ids:
                print(f"Response question ID range: {min(response_question_ids)} - {max(response_question_ids)}")
    
    except Exception as e:
        print(f"Database error: {e}")
        db_ids = []
        response_question_ids = []
    finally:
        if 'conn' in locals():
            conn.close()
    
    # 3. Find Issues
    print(f"\n3. INTEGRITY ISSUES")
    print("-" * 40)
    
    json_id_set = set(json_ids)
    db_id_set = set(db_ids)
    response_id_set = set(response_question_ids)
    
    # Missing from database
    missing_from_db = json_id_set - db_id_set
    print(f"Question IDs in JSON but missing from database: {len(missing_from_db)}")
    if missing_from_db and len(missing_from_db) <= 20:
        print(f"  Missing IDs: {sorted(list(missing_from_db))}")
    elif missing_from_db:
        print(f"  Sample missing IDs: {sorted(list(missing_from_db))[:20]}")
    
    # Extra in database  
    extra_in_db = db_id_set - json_id_set
    print(f"Question IDs in database but not in JSON: {len(extra_in_db)}")
    if extra_in_db and len(extra_in_db) <= 20:
        print(f"  Extra IDs: {sorted(list(extra_in_db))}")
    elif extra_in_db:
        print(f"  Sample extra IDs: {sorted(list(extra_in_db))[:20]}")
    
    # Orphaned responses
    orphaned = response_id_set - db_id_set  
    print(f"Response question IDs with no matching database question: {len(orphaned)}")
    if orphaned:
        print(f"  Orphaned response IDs: {sorted(list(orphaned))}")
    
    # Responses to JSON-only questions
    json_only_responses = response_id_set & missing_from_db
    print(f"Responses to questions that exist in JSON but not database: {len(json_only_responses)}")
    if json_only_responses:
        print(f"  JSON-only response IDs: {sorted(list(json_only_responses))}")
    
    # 4. Risk Assessment
    print(f"\n4. RISK ASSESSMENT")
    print("-" * 40)
    
    critical_issues = len(orphaned) + len(json_only_responses)
    
    if critical_issues == 0:
        print("✅ NO CRITICAL ISSUES - Database sync is safe")
    elif critical_issues < 5:
        print(f"⚠️  MINOR ISSUES - {critical_issues} responses may be affected")
        print("   Proceed with caution and backup first")
    else:
        print(f"🔥 MAJOR ISSUES - {critical_issues} responses at risk")
        print("   BACKUP REQUIRED before any sync operations")
    
    print(f"\nIssue summary:")
    print(f"  Items without IDs in JSON: {len(items_without_id)}")  
    print(f"  Missing questions in database: {len(missing_from_db)}")
    print(f"  Orphaned responses: {len(orphaned)}")
    print(f"  JSON-only responses: {len(json_only_responses)}")
    
    # 5. Migration Plan
    print(f"\n5. SAFE MIGRATION PLAN")
    print("-" * 40)
    
    print("Phase 1: Backup")
    print("  1. pg_dump echosofme_dev > backup_$(date +%Y%m%d_%H%M%S).sql")
    print("  2. cp questions.json questions_backup_$(date +%Y%m%d_%H%M%S).json")
    
    if items_without_id:
        print(f"\nPhase 2: Fix JSON Items Without IDs ({len(items_without_id)} items)")
        print("  3. Assign sequential IDs starting from max(existing_ids) + 1") 
        print("  4. Update questions.json with new IDs")
    
    if orphaned:
        print(f"\nPhase 3: Handle Orphaned Responses ({len(orphaned)} responses)")
        print("  5. Option A: Create placeholder questions for orphaned IDs")
        print("  6. Option B: Move to recovery table for manual review")
    
    if missing_from_db:
        print(f"\nPhase 4: Sync Missing Questions ({len(missing_from_db)} questions)")
        print("  7. INSERT missing questions from JSON into database")
        print("  8. Map JSON 'question' -> 'question_text' field")
        print("  9. Set is_active=true, created_at=NOW()")
    
    print(f"\nPhase 5: Validation")
    print("  10. Verify all response.question_id exist in questions table")
    print("  11. Test website question loading")
    print("  12. Test user reflection display")

if __name__ == "__main__":
    main()