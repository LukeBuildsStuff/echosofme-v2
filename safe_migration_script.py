#!/usr/bin/env python3
"""
Safe Database Migration Script for Echoes of Me
Addresses data integrity issues with rollback capabilities
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import shutil
import os
import sys

DATABASE_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev', 
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

class SafeMigration:
    def __init__(self):
        self.backup_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.json_file = '/home/luke/echosofme-v2/src/data/questions.json'
        self.backup_dir = '/home/luke/echosofme-v2/backups'
        self.rollback_info = {}
        
    def create_backup_directory(self):
        """Create backup directory if it doesn't exist"""
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def backup_json_file(self):
        """Create backup of questions.json file"""
        backup_file = f"{self.backup_dir}/questions_backup_{self.backup_timestamp}.json"
        shutil.copy2(self.json_file, backup_file)
        print(f"✅ JSON backup created: {backup_file}")
        return backup_file
        
    def backup_database(self):
        """Create database backup using pg_dump"""
        backup_file = f"{self.backup_dir}/database_backup_{self.backup_timestamp}.sql"
        cmd = f"PGPASSWORD='{DATABASE_CONFIG['password']}' pg_dump -h {DATABASE_CONFIG['host']} -p {DATABASE_CONFIG['port']} -U {DATABASE_CONFIG['user']} {DATABASE_CONFIG['database']} > {backup_file}"
        
        result = os.system(cmd)
        if result == 0:
            print(f"✅ Database backup created: {backup_file}")
            return backup_file
        else:
            print(f"❌ Database backup failed")
            return None
    
    def fix_json_missing_ids(self, dry_run=True):
        """Fix items in JSON that don't have IDs"""
        print(f"\n{'DRY RUN: ' if dry_run else ''}Fixing JSON items without IDs...")
        
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        
        # Find max existing ID
        existing_ids = [q['id'] for q in data if 'id' in q]
        max_id = max(existing_ids) if existing_ids else 0
        
        next_id = max_id + 1
        fixed_count = 0
        
        for item in data:
            if 'id' not in item:
                if not dry_run:
                    item['id'] = next_id
                print(f"  {'Would assign' if dry_run else 'Assigned'} ID {next_id} to: \"{item['question'][:50]}...\"")
                next_id += 1
                fixed_count += 1
        
        if not dry_run and fixed_count > 0:
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Fixed {fixed_count} items in JSON file")
        elif dry_run:
            print(f"📋 Would fix {fixed_count} items")
            
        return fixed_count
    
    def deduplicate_questions(self, dry_run=True):
        """Remove duplicate questions from database (keep newest)"""
        print(f"\n{'DRY RUN: ' if dry_run else ''}Deduplicating questions...")
        
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
            with conn.cursor() as cur:
                # Find duplicates
                cur.execute("""
                    SELECT question_text, array_agg(id ORDER BY created_at DESC) as ids, COUNT(*) as count
                    FROM questions 
                    WHERE question_text IS NOT NULL AND question_text != ''
                    GROUP BY question_text 
                    HAVING COUNT(*) > 1
                    ORDER BY COUNT(*) DESC
                """)
                
                duplicates = cur.fetchall()
                total_to_remove = 0
                
                for dup in duplicates:
                    ids_to_keep = dup['ids'][0]  # Keep first (newest)
                    ids_to_remove = dup['ids'][1:]  # Remove rest
                    total_to_remove += len(ids_to_remove)
                    
                    print(f"  Question: \"{dup['question_text'][:50]}...\"")
                    print(f"    {'Would keep' if dry_run else 'Keeping'} ID {ids_to_keep}, {'would remove' if dry_run else 'removing'} {ids_to_remove}")
                    
                    if not dry_run:
                        # Check if any responses reference the IDs we want to remove
                        cur.execute("SELECT COUNT(*) FROM responses WHERE question_id = ANY(%s)", (ids_to_remove,))
                        response_count = cur.fetchone()['count']
                        
                        if response_count > 0:
                            print(f"    ⚠️ {response_count} responses reference these duplicate IDs - updating to use {ids_to_keep}")
                            cur.execute("UPDATE responses SET question_id = %s WHERE question_id = ANY(%s)", (ids_to_keep, ids_to_remove))
                        
                        # Now safe to delete the duplicate questions
                        cur.execute("DELETE FROM questions WHERE id = ANY(%s)", (ids_to_remove,))
                
                if not dry_run and total_to_remove > 0:
                    conn.commit()
                    print(f"✅ Removed {total_to_remove} duplicate questions")
                elif dry_run:
                    print(f"📋 Would remove {total_to_remove} duplicate questions")
                
        except Exception as e:
            print(f"❌ Error deduplicating: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()
                
        return total_to_remove
    
    def fix_duplicate_responses(self, dry_run=True):
        """Remove duplicate responses (same user, question, text)"""
        print(f"\n{'DRY RUN: ' if dry_run else ''}Fixing duplicate responses...")
        
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
            with conn.cursor() as cur:
                # Find duplicates
                cur.execute("""
                    SELECT user_id, question_id, response_text, array_agg(id ORDER BY created_at DESC) as ids, COUNT(*) as count
                    FROM responses
                    GROUP BY user_id, question_id, response_text
                    HAVING COUNT(*) > 1
                """)
                
                duplicates = cur.fetchall()
                total_removed = 0
                
                for dup in duplicates:
                    ids_to_keep = dup['ids'][0]  # Keep newest
                    ids_to_remove = dup['ids'][1:]  # Remove older ones
                    total_removed += len(ids_to_remove)
                    
                    print(f"  User {dup['user_id']}, Question {dup['question_id']}: {'would keep' if dry_run else 'keeping'} ID {ids_to_keep}, {'would remove' if dry_run else 'removing'} {ids_to_remove}")
                    
                    if not dry_run:
                        cur.execute("DELETE FROM responses WHERE id = ANY(%s)", (ids_to_remove,))
                
                if not dry_run and total_removed > 0:
                    conn.commit()
                    print(f"✅ Removed {total_removed} duplicate responses")
                elif dry_run:
                    print(f"📋 Would remove {total_removed} duplicate responses")
                    
        except Exception as e:
            print(f"❌ Error fixing duplicate responses: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()
                
        return total_removed
    
    def validate_data_integrity(self):
        """Final validation that all data integrity is maintained"""
        print(f"\n🔍 Validating data integrity...")
        
        issues = []
        
        try:
            conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
            with conn.cursor() as cur:
                # Check for orphaned responses
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM responses r 
                    LEFT JOIN questions q ON r.question_id = q.id 
                    WHERE q.id IS NULL
                """)
                orphaned = cur.fetchone()['count']
                if orphaned > 0:
                    issues.append(f"❌ {orphaned} orphaned responses found")
                else:
                    print("✅ No orphaned responses")
                
                # Check for NULL critical fields
                cur.execute("SELECT COUNT(*) FROM questions WHERE question_text IS NULL OR question_text = ''")
                null_questions = cur.fetchone()['count']
                if null_questions > 0:
                    issues.append(f"❌ {null_questions} questions with empty text")
                else:
                    print("✅ All questions have text")
                
                cur.execute("SELECT COUNT(*) FROM responses WHERE response_text IS NULL OR response_text = ''")
                null_responses = cur.fetchone()['count']
                if null_responses > 0:
                    issues.append(f"❌ {null_responses} responses with empty text")
                else:
                    print("✅ All responses have text")
                
                # Check JSON sync status
                with open(self.json_file, 'r') as f:
                    json_data = json.load(f)
                
                items_without_id = [q for q in json_data if 'id' not in q]
                if items_without_id:
                    issues.append(f"❌ {len(items_without_id)} JSON items still missing IDs")
                else:
                    print("✅ All JSON items have IDs")
                    
        except Exception as e:
            issues.append(f"❌ Validation error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
        
        if issues:
            print("\n⚠️ VALIDATION FAILED:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("\n🎉 ALL VALIDATION CHECKS PASSED")
            return True
    
    def run_migration(self, dry_run=True):
        """Run the complete migration process"""
        print(f"🚀 Starting {'DRY RUN' if dry_run else 'LIVE'} migration at {datetime.datetime.now()}")
        print("=" * 60)
        
        # 1. Create backups
        if not dry_run:
            self.create_backup_directory()
            json_backup = self.backup_json_file()
            db_backup = self.backup_database()
            
            if not db_backup:
                print("❌ Migration aborted - database backup failed")
                return False
        
        # 2. Fix JSON missing IDs
        self.fix_json_missing_ids(dry_run)
        
        # 3. Deduplicate questions
        self.deduplicate_questions(dry_run)
        
        # 4. Fix duplicate responses
        self.fix_duplicate_responses(dry_run)
        
        # 5. Validate
        if not dry_run:
            success = self.validate_data_integrity()
            if not success:
                print("❌ Migration completed but validation failed - check issues above")
                return False
        
        print("\n" + "=" * 60)
        print(f"✅ {'DRY RUN' if dry_run else 'MIGRATION'} COMPLETED SUCCESSFULLY")
        
        if dry_run:
            print("\nTo run the actual migration:")
            print("python3 safe_migration_script.py --live")
            
        return True
    
    def create_rollback_script(self):
        """Create a rollback script for emergency recovery"""
        rollback_script = f"""#!/bin/bash
# Emergency rollback script generated {self.backup_timestamp}

echo "🚨 EMERGENCY ROLLBACK - This will restore the database to pre-migration state"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Restore database
echo "Restoring database..."
PGPASSWORD='{DATABASE_CONFIG['password']}' psql -h {DATABASE_CONFIG['host']} -p {DATABASE_CONFIG['port']} -U {DATABASE_CONFIG['user']} -d {DATABASE_CONFIG['database']} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
PGPASSWORD='{DATABASE_CONFIG['password']}' psql -h {DATABASE_CONFIG['host']} -p {DATABASE_CONFIG['port']} -U {DATABASE_CONFIG['user']} -d {DATABASE_CONFIG['database']} < {self.backup_dir}/database_backup_{self.backup_timestamp}.sql

# Restore JSON file
echo "Restoring JSON file..."
cp {self.backup_dir}/questions_backup_{self.backup_timestamp}.json {self.json_file}

echo "✅ Rollback completed"
"""
        
        rollback_file = f"{self.backup_dir}/rollback_{self.backup_timestamp}.sh"
        with open(rollback_file, 'w') as f:
            f.write(rollback_script)
        os.chmod(rollback_file, 0o755)
        
        print(f"📝 Rollback script created: {rollback_file}")

def main():
    migration = SafeMigration()
    
    # Check command line arguments
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        print("⚠️ LIVE MIGRATION MODE ENABLED")
        print("This will make actual changes to your database and files!")
        response = input("Are you sure you want to continue? (yes/NO): ")
        if response.lower() != 'yes':
            print("Migration cancelled")
            return
        dry_run = False
    
    # Run migration
    success = migration.run_migration(dry_run)
    
    # Create rollback script if live migration
    if not dry_run and success:
        migration.create_rollback_script()

if __name__ == "__main__":
    main()