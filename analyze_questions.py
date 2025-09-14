#!/usr/bin/env python3
"""
Analyze the questions.json file to understand data integrity issues
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor

def analyze_json_file():
    """Analyze the questions.json file structure and content"""
    print("=== QUESTIONS.JSON ANALYSIS ===")
    
    with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
        data = json.load(f)
    
    print(f"Total questions in JSON: {len(data)}")
    
    # Analyze IDs - some items don't have IDs
    ids = [q['id'] for q in data if 'id' in q]
    items_without_id = [q for q in data if 'id' not in q]
    print(f"Items with ID: {len(ids)}")
    print(f"Items without ID: {len(items_without_id)}")
    
    if ids:
        print(f"ID range: {min(ids)} - {max(ids)}")
        print(f"Unique IDs: {len(set(ids))}")
        duplicates = len(ids) - len(set(ids))
        print(f"Duplicate IDs: {duplicates}")
    else:
        print("No items with IDs found!")
    
    if ids and duplicates > 0:
        # Find duplicate IDs
        seen = set()
        dups = []
        for qid in ids:
            if qid in seen:
                dups.append(qid)
            seen.add(qid)
        print(f"Duplicate ID values: {sorted(set(dups))}")
    
    # Analyze categories
    categories = {}
    for q in data:
        cat = q['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print("\nCategories and counts:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Find gaps in ID sequence
    all_ids = set(ids)
    gaps = []
    for i in range(1, max(ids) + 1):
        if i not in all_ids:
            gaps.append(i)
    
    print(f"\nMissing IDs in sequence (first 20): {gaps[:20]}")
    print(f"Total missing IDs in sequence: {len(gaps)}")
    
    return data, set(ids), categories

def analyze_database():
    """Analyze the database questions table"""
    print("\n=== DATABASE ANALYSIS ===")
    
    DATABASE_CONFIG = {
        'host': 'host.docker.internal',
        'database': 'echosofme_dev', 
        'user': 'echosofme',
        'password': 'secure_dev_password',
        'port': 5432
    }
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        with conn.cursor() as cur:
            # Get all questions from database
            cur.execute("SELECT id, question_text, category, subcategory, difficulty_level, question_type, is_active FROM questions ORDER BY id")
            db_questions = cur.fetchall()
            
            print(f"Total questions in database: {len(db_questions)}")
            
            if db_questions:
                db_ids = [q['id'] for q in db_questions]
                print(f"Database ID range: {min(db_ids)} - {max(db_ids)}")
                print(f"Unique database IDs: {len(set(db_ids))}")
                
                # Check categories
                db_categories = {}
                for q in db_questions:
                    cat = q['category']
                    if cat:
                        if cat not in db_categories:
                            db_categories[cat] = 0
                        db_categories[cat] += 1
                
                print("\nDatabase categories and counts:")
                for cat, count in sorted(db_categories.items()):
                    print(f"  {cat}: {count}")
                
                # Check for inactive questions
                inactive_count = sum(1 for q in db_questions if not q['is_active'])
                print(f"\nInactive questions: {inactive_count}")
                
            # Get all responses to check orphaned records
            cur.execute("SELECT DISTINCT question_id FROM responses ORDER BY question_id")
            response_qids = [r['question_id'] for r in cur.fetchall()]
            print(f"\nUnique question IDs referenced in responses: {len(response_qids)}")
            
            if response_qids:
                print(f"Response question ID range: {min(response_qids)} - {max(response_qids)}")
            
            return set(db_ids) if db_questions else set(), set(response_qids), db_questions
            
    except Exception as e:
        print(f"Database connection error: {e}")
        return set(), set(), []
    finally:
        if 'conn' in locals():
            conn.close()

def find_sync_issues(json_ids, db_ids, response_qids, json_data, db_questions):
    """Find synchronization issues between JSON and database"""
    print("\n=== SYNCHRONIZATION ISSUES ===")
    
    # IDs in JSON but not in database
    json_only = json_ids - db_ids
    print(f"IDs in JSON but NOT in database: {len(json_only)}")
    if json_only:
        print(f"Sample JSON-only IDs: {sorted(list(json_only))[:20]}")
    
    # IDs in database but not in JSON
    db_only = db_ids - json_ids
    print(f"IDs in database but NOT in JSON: {len(db_only)}")
    if db_only:
        print(f"Sample DB-only IDs: {sorted(list(db_only))[:20]}")
    
    # Orphaned responses (responses referencing non-existent questions)
    orphaned_responses = response_qids - db_ids
    print(f"Orphaned response question IDs (not in database): {len(orphaned_responses)}")
    if orphaned_responses:
        print(f"Orphaned question IDs: {sorted(list(orphaned_responses))[:20]}")
    
    # Responses referencing questions that exist in JSON but not DB
    json_referenced_missing = response_qids & json_only
    print(f"Responses referencing JSON questions missing from DB: {len(json_referenced_missing)}")
    if json_referenced_missing:
        print(f"JSON-referenced missing IDs: {sorted(list(json_referenced_missing))[:20]}")
    
    return {
        'json_only': json_only,
        'db_only': db_only, 
        'orphaned_responses': orphaned_responses,
        'json_referenced_missing': json_referenced_missing
    }

def risk_assessment(issues, json_data, db_questions):
    """Assess risks of synchronization"""
    print("\n=== RISK ASSESSMENT ===")
    
    total_responses_at_risk = len(issues['orphaned_responses']) + len(issues['json_referenced_missing'])
    
    print(f"🔥 HIGH RISK: {total_responses_at_risk} responses reference non-existent questions")
    print(f"⚠️  MEDIUM RISK: {len(issues['json_only'])} questions in JSON missing from database")
    print(f"ℹ️  LOW RISK: {len(issues['db_only'])} questions in database not in JSON")
    
    if issues['orphaned_responses']:
        print(f"\n⚠️ CRITICAL: {len(issues['orphaned_responses'])} responses are completely orphaned")
        print("   These responses will cause errors when loading reflections")
    
    if issues['json_referenced_missing']:
        print(f"\n⚠️ BLOCKING: {len(issues['json_referenced_missing'])} responses reference JSON questions not in DB")
        print("   These prevent the website from loading properly")
    
    return total_responses_at_risk

def suggest_migration_strategy(issues, json_data):
    """Suggest safe migration strategy"""
    print("\n=== SAFE MIGRATION STRATEGY ===")
    
    print("Phase 1: Backup and Safety")
    print("1. Create full database backup")
    print("2. Export all responses with question_id references") 
    print("3. Create backup copies of questions.json")
    
    print("\nPhase 2: Fix Orphaned Responses")
    if issues['orphaned_responses']:
        print(f"4. Handle {len(issues['orphaned_responses'])} orphaned responses:")
        print("   Option A: Create placeholder questions for orphaned IDs")
        print("   Option B: Move orphaned responses to 'recovered_reflections' table")
        print("   Option C: Associate with closest matching questions")
    
    print("\nPhase 3: Sync Missing Questions")  
    if issues['json_only']:
        print(f"5. Import {len(issues['json_only'])} missing questions from JSON to database")
        print("   - Use INSERT INTO questions (id, question_text, category) SELECT ...")
        print("   - Set is_active=true, created_at=now()")
        print("   - Map JSON 'question' field to 'question_text'")
    
    print("\nPhase 4: Validation")
    print("6. Verify all response.question_id references exist in questions table")
    print("7. Run website smoke tests")  
    print("8. Check reflection loading for all users")
    
    print("\nPhase 5: Cleanup (Optional)")
    if issues['db_only']:
        print(f"9. Review {len(issues['db_only'])} database-only questions")
        print("   - Check if they have responses")
        print("   - Consider soft-deleting unused ones (is_active=false)")

def main():
    """Main analysis function"""
    print("Starting comprehensive database integrity analysis...")
    
    # Analyze JSON file
    json_data, json_ids, json_categories = analyze_json_file()
    
    # Analyze database
    db_ids, response_qids, db_questions = analyze_database()
    
    # Find sync issues
    issues = find_sync_issues(json_ids, db_ids, response_qids, json_data, db_questions)
    
    # Assess risks
    risk_level = risk_assessment(issues, json_data, db_questions)
    
    # Suggest migration strategy
    suggest_migration_strategy(issues, json_data)
    
    print(f"\n=== SUMMARY ===")
    print(f"JSON questions: {len(json_data)}")
    print(f"Database questions: {len(db_questions)}")
    print(f"Response question references: {len(response_qids)}")
    print(f"Critical issues: {risk_level} responses at risk")
    
    if risk_level == 0:
        print("✅ No critical data integrity issues found")
    elif risk_level < 10:
        print("⚠️ Minor integrity issues - safe to proceed with caution")
    else:
        print("🔥 Major integrity issues - backup required before any changes")

if __name__ == "__main__":
    main()