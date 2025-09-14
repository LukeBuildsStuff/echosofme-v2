#!/usr/bin/env python3
"""
Database Integrity Fix Script for Echoes of Me
Fixes identified sync and integrity issues
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import sys
from collections import defaultdict

# Database configuration
DATABASE_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

class DatabaseIntegrityFixer:
    def __init__(self, dry_run=True):
        self.conn = None
        self.dry_run = dry_run
        self.fixes_applied = []
        self.fixes_failed = []
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
            print("✅ Database connection established")
            if self.dry_run:
                print("🔍 DRY RUN MODE - No changes will be made")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def add_fix(self, category, action, details, success=True):
        """Record a fix attempt"""
        fix_record = {
            'category': category,
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run
        }
        
        if success:
            self.fixes_applied.append(fix_record)
        else:
            self.fixes_failed.append(fix_record)
    
    def execute_sql(self, query, params=None, description="SQL operation"):
        """Execute SQL with proper error handling and dry-run support"""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Would execute: {description}")
                print(f"[DRY RUN] SQL: {query}")
                if params:
                    print(f"[DRY RUN] Params: {params}")
                return True
            else:
                with self.conn.cursor() as cur:
                    cur.execute(query, params)
                    if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                        self.conn.commit()
                    return cur.fetchall() if query.strip().upper().startswith('SELECT') else True
        except Exception as e:
            print(f"❌ Failed to execute {description}: {e}")
            if not self.dry_run:
                self.conn.rollback()
            return False
    
    def add_missing_foreign_keys(self):
        """Add missing foreign key constraints"""
        print("\n🔧 ADDING MISSING FOREIGN KEY CONSTRAINTS...")
        
        constraints_to_add = [
            {
                'name': 'fk_responses_user_id',
                'table': 'responses',
                'column': 'user_id',
                'ref_table': 'users',
                'ref_column': 'id',
                'description': 'Foreign key for responses.user_id -> users.id'
            },
            {
                'name': 'fk_responses_question_id',
                'table': 'responses',
                'column': 'question_id',
                'ref_table': 'questions',
                'ref_column': 'id',
                'description': 'Foreign key for responses.question_id -> questions.id'
            }
        ]
        
        for constraint in constraints_to_add:
            # Check if constraint already exists
            check_query = """
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = %s AND constraint_name = %s
            """
            
            if not self.dry_run:
                with self.conn.cursor() as cur:
                    cur.execute(check_query, (constraint['table'], constraint['name']))
                    if cur.fetchone():
                        print(f"✅ Constraint {constraint['name']} already exists")
                        continue
            
            # Add foreign key constraint
            add_fk_query = f"""
                ALTER TABLE {constraint['table']} 
                ADD CONSTRAINT {constraint['name']} 
                FOREIGN KEY ({constraint['column']}) 
                REFERENCES {constraint['ref_table']}({constraint['ref_column']})
            """
            
            if self.execute_sql(add_fk_query, description=constraint['description']):
                self.add_fix('foreign_keys', f"Added constraint {constraint['name']}", constraint)
                print(f"✅ Added foreign key constraint: {constraint['name']}")
            else:
                self.add_fix('foreign_keys', f"Failed to add constraint {constraint['name']}", constraint, False)
    
    def fix_orphaned_responses(self):
        """Fix orphaned responses by either linking to correct questions or creating missing questions"""
        print("\n🔧 FIXING ORPHANED RESPONSES...")
        
        # First, identify orphaned responses
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.user_id, r.question_id, r.response_text, r.created_at,
                       u.email
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                JOIN users u ON r.user_id = u.id
                WHERE q.id IS NULL
                ORDER BY r.created_at DESC
            """)
            
            orphaned = cur.fetchall()
        
        if not orphaned:
            print("✅ No orphaned responses found")
            return
        
        print(f"Found {len(orphaned)} orphaned responses")
        
        # Load questions.json to see if we can find the missing questions
        try:
            with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
                json_questions = json.load(f)
            json_by_id = {q['id']: q for q in json_questions}
        except Exception as e:
            print(f"❌ Cannot load questions.json: {e}")
            return
        
        for orphan in orphaned:
            question_id = orphan['question_id']
            response_id = orphan['id']
            
            if question_id in json_by_id:
                # Question exists in JSON, add it to database
                json_q = json_by_id[question_id]
                insert_question_query = """
                    INSERT INTO questions (id, question_text, category, subcategory, difficulty_level, question_type, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        question_text = EXCLUDED.question_text,
                        category = EXCLUDED.category
                """
                
                params = (
                    question_id,
                    json_q.get('question', 'Missing question text'),
                    json_q.get('category', 'general'),
                    json_q.get('subcategory'),
                    json_q.get('difficulty_level', 'medium'),
                    json_q.get('question_type', 'reflection'),
                    True
                )
                
                if self.execute_sql(insert_question_query, params, f"Insert question {question_id}"):
                    self.add_fix('orphaned_responses', f"Added missing question {question_id}", {
                        'question_id': question_id,
                        'response_id': response_id,
                        'user_email': orphan['email']
                    })
                    print(f"✅ Added missing question {question_id} for response {response_id}")
                else:
                    self.add_fix('orphaned_responses', f"Failed to add question {question_id}", {
                        'question_id': question_id,
                        'response_id': response_id
                    }, False)
            else:
                # Question doesn't exist in JSON either - create a generic question
                generic_question_query = """
                    INSERT INTO questions (id, question_text, category, is_active)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """
                
                generic_text = f"[RECOVERED] Question {question_id} - content needs review"
                
                if self.execute_sql(generic_question_query, (question_id, generic_text, 'general', True), 
                                  f"Create generic question {question_id}"):
                    self.add_fix('orphaned_responses', f"Created generic question {question_id}", {
                        'question_id': question_id,
                        'response_id': response_id,
                        'user_email': orphan['email'],
                        'generic': True
                    })
                    print(f"⚠️ Created generic question {question_id} for response {response_id}")
                else:
                    self.add_fix('orphaned_responses', f"Failed to create question {question_id}", {
                        'question_id': question_id,
                        'response_id': response_id
                    }, False)
    
    def sync_questions_from_json(self):
        """Sync questions from JSON to database"""
        print("\n🔧 SYNCING QUESTIONS FROM JSON TO DATABASE...")
        
        try:
            with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
                json_questions = json.load(f)
        except Exception as e:
            print(f"❌ Cannot load questions.json: {e}")
            return
        
        # Get existing questions from database
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM questions")
            existing_ids = set(row['id'] for row in cur.fetchall())
        
        # Insert missing questions
        missing_count = 0
        updated_count = 0
        
        for q in json_questions:
            question_id = q['id']
            
            upsert_query = """
                INSERT INTO questions (id, question_text, category, subcategory, difficulty_level, question_type, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    question_text = EXCLUDED.question_text,
                    category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    difficulty_level = EXCLUDED.difficulty_level,
                    question_type = EXCLUDED.question_type,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            params = (
                question_id,
                q.get('question', f'Question {question_id}'),
                q.get('category', 'general'),
                q.get('subcategory'),
                q.get('difficulty_level', 'medium'),
                q.get('question_type', 'reflection'),
                True
            )
            
            if self.execute_sql(upsert_query, params, f"Upsert question {question_id}"):
                if question_id in existing_ids:
                    updated_count += 1
                else:
                    missing_count += 1
            else:
                print(f"❌ Failed to sync question {question_id}")
        
        self.add_fix('json_sync', f"Synced {missing_count + updated_count} questions from JSON", {
            'new_questions': missing_count,
            'updated_questions': updated_count,
            'total_json_questions': len(json_questions)
        })
        
        print(f"✅ Synced questions: {missing_count} new, {updated_count} updated")
    
    def add_missing_indexes(self):
        """Add recommended database indexes for performance"""
        print("\n🔧 ADDING PERFORMANCE INDEXES...")
        
        indexes_to_add = [
            {
                'name': 'idx_responses_user_id',
                'table': 'responses',
                'columns': 'user_id',
                'description': 'Index for responses by user'
            },
            {
                'name': 'idx_responses_question_id',
                'table': 'responses',
                'columns': 'question_id',
                'description': 'Index for responses by question'
            },
            {
                'name': 'idx_responses_created_at',
                'table': 'responses',
                'columns': 'created_at DESC',
                'description': 'Index for responses by creation date'
            },
            {
                'name': 'idx_questions_category',
                'table': 'questions',
                'columns': 'category',
                'description': 'Index for questions by category'
            },
            {
                'name': 'idx_questions_is_active',
                'table': 'questions',
                'columns': 'is_active',
                'description': 'Index for active questions'
            },
            {
                'name': 'idx_users_email',
                'table': 'users',
                'columns': 'email',
                'description': 'Unique index for user emails'
            }
        ]
        
        for index in indexes_to_add:
            # Check if index already exists
            check_query = """
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = %s AND indexname = %s
            """
            
            if not self.dry_run:
                with self.conn.cursor() as cur:
                    cur.execute(check_query, (index['table'], index['name']))
                    if cur.fetchone():
                        print(f"✅ Index {index['name']} already exists")
                        continue
            
            # Create index
            unique_clause = "UNIQUE " if "email" in index['name'] else ""
            create_index_query = f"CREATE {unique_clause}INDEX IF NOT EXISTS {index['name']} ON {index['table']} ({index['columns']})"
            
            if self.execute_sql(create_index_query, description=index['description']):
                self.add_fix('indexes', f"Added index {index['name']}", index)
                print(f"✅ Added index: {index['name']}")
            else:
                self.add_fix('indexes', f"Failed to add index {index['name']}", index, False)
    
    def fix_word_count_inconsistencies(self):
        """Fix word count inconsistencies in responses"""
        print("\n🔧 FIXING WORD COUNT INCONSISTENCIES...")
        
        # Find responses with incorrect word counts
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, response_text, word_count,
                       array_length(string_to_array(trim(response_text), ' '), 1) as actual_count
                FROM responses 
                WHERE response_text IS NOT NULL 
                AND response_text != ''
                AND word_count != array_length(string_to_array(trim(response_text), ' '), 1)
                LIMIT 1000
            """)
            
            inconsistent = cur.fetchall()
        
        if not inconsistent:
            print("✅ No word count inconsistencies found")
            return
        
        print(f"Found {len(inconsistent)} responses with incorrect word counts")
        
        # Fix word counts
        fixed_count = 0
        for response in inconsistent:
            update_query = """
                UPDATE responses 
                SET word_count = array_length(string_to_array(trim(response_text), ' '), 1),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            if self.execute_sql(update_query, (response['id'],), f"Fix word count for response {response['id']}"):
                fixed_count += 1
        
        self.add_fix('word_counts', f"Fixed {fixed_count} word count inconsistencies", {
            'total_inconsistent': len(inconsistent),
            'fixed_count': fixed_count
        })
        
        print(f"✅ Fixed {fixed_count} word count inconsistencies")
    
    def create_backup_tables(self):
        """Create backup tables before making changes"""
        print("\n💾 CREATING BACKUP TABLES...")
        
        backup_queries = [
            "CREATE TABLE responses_backup AS SELECT * FROM responses",
            "CREATE TABLE questions_backup AS SELECT * FROM questions",
            "CREATE TABLE users_backup AS SELECT * FROM users"
        ]
        
        for query in backup_queries:
            table_name = query.split()[2]  # Extract table name
            
            # Check if backup already exists
            check_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = %s
            """
            
            if not self.dry_run:
                with self.conn.cursor() as cur:
                    cur.execute(check_query, (table_name,))
                    if cur.fetchone():
                        print(f"✅ Backup table {table_name} already exists")
                        continue
            
            if self.execute_sql(query, description=f"Create backup table {table_name}"):
                self.add_fix('backup', f"Created backup table {table_name}", {'table': table_name})
                print(f"✅ Created backup table: {table_name}")
            else:
                self.add_fix('backup', f"Failed to create backup table {table_name}", {'table': table_name}, False)
    
    def run_fixes(self, skip_backup=False):
        """Run all integrity fixes"""
        print("🚀 STARTING DATABASE INTEGRITY FIXES")
        print("=" * 60)
        
        self.connect()
        
        try:
            # Create backups first (unless skipped)
            if not skip_backup and not self.dry_run:
                self.create_backup_tables()
            
            # Apply fixes in order of importance
            self.sync_questions_from_json()
            self.fix_orphaned_responses()
            self.add_missing_foreign_keys()
            self.add_missing_indexes()
            self.fix_word_count_inconsistencies()
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 FIX SUMMARY")
            print("=" * 60)
            
            print(f"\n✅ SUCCESSFUL FIXES: {len(self.fixes_applied)}")
            for fix in self.fixes_applied:
                print(f"  - {fix['category']}: {fix['action']}")
            
            if self.fixes_failed:
                print(f"\n❌ FAILED FIXES: {len(self.fixes_failed)}")
                for fix in self.fixes_failed:
                    print(f"  - {fix['category']}: {fix['action']}")
            
            # Save fix report
            fix_report = {
                'fix_timestamp': datetime.now().isoformat(),
                'dry_run': self.dry_run,
                'successful_fixes': self.fixes_applied,
                'failed_fixes': self.fixes_failed,
                'summary': {
                    'total_fixes_attempted': len(self.fixes_applied) + len(self.fixes_failed),
                    'successful': len(self.fixes_applied),
                    'failed': len(self.fixes_failed)
                }
            }
            
            report_filename = f"database_fixes_{'dry_run_' if self.dry_run else ''}{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(f'/home/luke/echosofme-v2/{report_filename}', 'w') as f:
                json.dump(fix_report, f, indent=2, default=str)
            
            print(f"\n💾 Fix report saved to: {report_filename}")
            
            if self.dry_run:
                print("\n🔍 This was a DRY RUN - no actual changes were made")
                print("Run with --execute to apply the fixes")
            
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix database integrity issues')
    parser.add_argument('--execute', action='store_true', help='Actually execute the fixes (default is dry run)')
    parser.add_argument('--skip-backup', action='store_true', help='Skip creating backup tables')
    args = parser.parse_args()
    
    fixer = DatabaseIntegrityFixer(dry_run=not args.execute)
    fixer.run_fixes(skip_backup=args.skip_backup)