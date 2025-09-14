#!/usr/bin/env python3
"""
Fix Question Text Issue Script
Adds question_text_snapshot and category_snapshot columns to responses table
to preserve the exact question text when users submit their reflections.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    DATABASE_CONFIG = {
        'host': 'host.docker.internal',
        'database': 'echosofme_dev',
        'user': 'echosofme',
        'password': 'secure_dev_password',
        'port': 5432
    }
    return psycopg2.connect(**DATABASE_CONFIG)

def check_columns_exist():
    """Check if the new columns already exist"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'responses' 
                AND column_name IN ('question_text_snapshot', 'category_snapshot')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
            return existing_columns
    finally:
        conn.close()

def add_snapshot_columns(dry_run=True):
    """Add question_text_snapshot and category_snapshot columns to responses table"""
    logger.info(f"🔧 Adding snapshot columns to responses table ({'DRY RUN' if dry_run else 'LIVE RUN'})")
    
    # Check if columns already exist
    existing_columns = check_columns_exist()
    
    if 'question_text_snapshot' in existing_columns and 'category_snapshot' in existing_columns:
        logger.info("✅ Both snapshot columns already exist!")
        return True
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Add question_text_snapshot column if it doesn't exist
            if 'question_text_snapshot' not in existing_columns:
                alter_sql = """
                    ALTER TABLE responses 
                    ADD COLUMN question_text_snapshot TEXT;
                """
                if dry_run:
                    logger.info("📝 Would execute: ALTER TABLE responses ADD COLUMN question_text_snapshot TEXT;")
                else:
                    logger.info("📝 Adding question_text_snapshot column...")
                    cur.execute(alter_sql)
                    logger.info("✅ Added question_text_snapshot column")
            else:
                logger.info("✅ question_text_snapshot column already exists")
            
            # Add category_snapshot column if it doesn't exist
            if 'category_snapshot' not in existing_columns:
                alter_sql = """
                    ALTER TABLE responses 
                    ADD COLUMN category_snapshot VARCHAR(100);
                """
                if dry_run:
                    logger.info("📝 Would execute: ALTER TABLE responses ADD COLUMN category_snapshot VARCHAR(100);")
                else:
                    logger.info("📝 Adding category_snapshot column...")
                    cur.execute(alter_sql)
                    logger.info("✅ Added category_snapshot column")
            else:
                logger.info("✅ category_snapshot column already exists")
            
            if not dry_run:
                conn.commit()
                logger.info("✅ Database schema updated successfully!")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error updating schema: {e}")
        if not dry_run:
            conn.rollback()
        return False
    finally:
        conn.close()

def populate_existing_data(dry_run=True):
    """Populate snapshot columns for existing responses"""
    logger.info(f"🔄 Populating existing responses with question snapshots ({'DRY RUN' if dry_run else 'LIVE RUN'})")
    
    # In dry run mode, check if columns exist first
    if dry_run:
        existing_columns = check_columns_exist()
        if 'question_text_snapshot' not in existing_columns:
            logger.info("📝 Would populate existing responses after columns are created")
            logger.info("📊 Sample of what would be populated:")
            
            conn = get_db_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT COUNT(*) as total_responses
                        FROM responses
                    """)
                    total_count = cur.fetchone()['total_responses']
                    
                    cur.execute("""
                        SELECT r.id, r.question_id, q.question_text, q.category
                        FROM responses r
                        LEFT JOIN questions q ON r.question_id = q.id
                        ORDER BY r.created_at DESC
                        LIMIT 5
                    """)
                    sample_rows = cur.fetchall()
                    
                    logger.info(f"📊 Would populate {total_count} responses")
                    logger.info("📝 Sample updates that would be performed:")
                    for row in sample_rows:
                        question_text = row['question_text'] or "⚠️  MISSING QUESTION"
                        category = row['category'] or "unknown"
                        logger.info(f"  Response {row['id']}: Question {row['question_id']} -> '{question_text}' ({category})")
                    
                    return True
            finally:
                conn.close()
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get count of responses without snapshots
            cur.execute("""
                SELECT COUNT(*) as count
                FROM responses 
                WHERE question_text_snapshot IS NULL
            """)
            total_count = cur.fetchone()['count']
            
            if total_count == 0:
                logger.info("✅ All responses already have question snapshots!")
                return True
            
            logger.info(f"📊 Found {total_count} responses to populate")
            
            if dry_run:
                # Show what would be updated
                cur.execute("""
                    SELECT r.id, r.question_id, q.question_text, q.category
                    FROM responses r
                    LEFT JOIN questions q ON r.question_id = q.id
                    WHERE r.question_text_snapshot IS NULL
                    LIMIT 5
                """)
                sample_rows = cur.fetchall()
                
                logger.info("📝 Sample updates that would be performed:")
                for row in sample_rows:
                    question_text = row['question_text'] or "⚠️  MISSING QUESTION"
                    category = row['category'] or "unknown"
                    logger.info(f"  Response {row['id']}: Question {row['question_id']} -> '{question_text}' ({category})")
                
                return True
            
            # Actually populate the data
            logger.info("📝 Updating responses with question snapshots...")
            cur.execute("""
                UPDATE responses 
                SET question_text_snapshot = q.question_text,
                    category_snapshot = q.category
                FROM questions q
                WHERE responses.question_id = q.id
                AND responses.question_text_snapshot IS NULL
            """)
            
            updated_count = cur.rowcount
            logger.info(f"✅ Updated {updated_count} responses with question snapshots")
            
            # Handle missing questions
            cur.execute("""
                UPDATE responses 
                SET question_text_snapshot = '⚠️ Question text not available (ID: ' || question_id || ')',
                    category_snapshot = 'unknown'
                WHERE question_text_snapshot IS NULL
            """)
            
            missing_count = cur.rowcount
            if missing_count > 0:
                logger.warning(f"⚠️  Set placeholder text for {missing_count} responses with missing questions")
            
            conn.commit()
            logger.info("✅ Successfully populated all existing responses!")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error populating data: {e}")
        if not dry_run:
            conn.rollback()
        return False
    finally:
        conn.close()

def verify_fix():
    """Verify that the fix is working correctly"""
    logger.info("🔍 Verifying the fix...")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check column existence
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'responses' 
                AND column_name IN ('question_text_snapshot', 'category_snapshot')
                ORDER BY column_name
            """)
            columns = cur.fetchall()
            
            logger.info("📊 Schema verification:")
            for col in columns:
                logger.info(f"  ✅ {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check data population
            cur.execute("""
                SELECT 
                    COUNT(*) as total_responses,
                    COUNT(question_text_snapshot) as with_snapshots,
                    COUNT(*) - COUNT(question_text_snapshot) as without_snapshots
                FROM responses
            """)
            stats = cur.fetchone()
            
            logger.info("📊 Data verification:")
            logger.info(f"  Total responses: {stats['total_responses']}")
            logger.info(f"  With snapshots: {stats['with_snapshots']}")
            logger.info(f"  Without snapshots: {stats['without_snapshots']}")
            
            if stats['without_snapshots'] == 0:
                logger.info("✅ All responses have question snapshots!")
            else:
                logger.warning(f"⚠️  {stats['without_snapshots']} responses still missing snapshots")
            
            # Show a sample of the data
            cur.execute("""
                SELECT id, question_id, question_text_snapshot, category_snapshot
                FROM responses 
                WHERE question_text_snapshot IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 3
            """)
            samples = cur.fetchall()
            
            logger.info("📊 Sample snapshot data:")
            for sample in samples:
                logger.info(f"  Response {sample['id']}: Q{sample['question_id']} -> '{sample['question_text_snapshot'][:50]}...' ({sample['category_snapshot']})")
            
            return stats['without_snapshots'] == 0
            
    except Exception as e:
        logger.error(f"❌ Error verifying fix: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function"""
    logger.info("🔧 Question Text Issue Fix Tool")
    logger.info("=" * 50)
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
Usage:
  python3 fix_question_text_issue.py --dry-run     # Show what would be done
  python3 fix_question_text_issue.py --apply       # Actually apply the changes
  python3 fix_question_text_issue.py --verify      # Verify current state
        """)
        return
    
    if "--verify" in sys.argv:
        verify_fix()
        return
    
    dry_run = "--dry-run" in sys.argv or len(sys.argv) == 1
    
    if not dry_run and "--apply" not in sys.argv:
        logger.error("❌ For live changes, use --apply flag")
        return
    
    # Step 1: Add columns
    if not add_snapshot_columns(dry_run):
        logger.error("❌ Failed to add columns")
        return
    
    # Step 2: Populate existing data
    if not populate_existing_data(dry_run):
        logger.error("❌ Failed to populate data")
        return
    
    if not dry_run:
        logger.info("🎉 Database migration completed successfully!")
        logger.info("🔄 Next steps: Update the API code to use snapshot columns")
    else:
        logger.info("📝 Dry run completed. Use --apply to execute changes.")

if __name__ == "__main__":
    main()