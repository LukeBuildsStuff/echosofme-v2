#!/usr/bin/env python3
"""
Add Question Management Features Script
Adds is_active column and related fields to questions table for enhanced management
"""

import os
import sys
import logging
from supabase import create_client, Client

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_supabase_client():
    """Get Supabase client using environment variables"""
    try:
        url = os.getenv('SUPABASE_URL', 'https://cbaudsvlidzfxvmzdvcg.supabase.co')
        key = os.getenv('SUPABASE_SERVICE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8')

        if not url or not key:
            raise ValueError("Missing Supabase configuration")

        supabase = create_client(url, key)
        return supabase
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        raise

def check_columns_exist():
    """Check if the new columns already exist"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'questions'
                AND column_name IN ('is_active', 'difficulty_level', 'deactivated_at', 'deactivated_reason')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
            return existing_columns
    finally:
        conn.close()

def add_question_management_columns(dry_run=True):
    """Add question management columns to questions table"""
    logger.info(f"🔧 Adding question management columns ({'DRY RUN' if dry_run else 'LIVE RUN'})")

    # Check if columns already exist
    existing_columns = check_columns_exist()

    columns_to_add = {
        'is_active': 'BOOLEAN DEFAULT true',
        'difficulty_level': 'INTEGER DEFAULT 2',
        'deactivated_at': 'TIMESTAMP',
        'deactivated_reason': 'TEXT'
    }

    new_columns = {col: def_val for col, def_val in columns_to_add.items() if col not in existing_columns}

    if not new_columns:
        logger.info("✅ All question management columns already exist!")
        return True

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for column_name, column_definition in new_columns.items():
                alter_sql = f"""
                    ALTER TABLE questions
                    ADD COLUMN {column_name} {column_definition};
                """
                if dry_run:
                    logger.info(f"📝 Would execute: ALTER TABLE questions ADD COLUMN {column_name} {column_definition};")
                else:
                    logger.info(f"📝 Adding {column_name} column...")
                    cur.execute(alter_sql)
                    logger.info(f"✅ Added {column_name} column")

            if not dry_run:
                conn.commit()
                logger.info("✅ All columns added successfully")

    except Exception as e:
        logger.error(f"❌ Failed to add columns: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

    return True

def create_indexes(dry_run=True):
    """Create indexes for better performance"""
    logger.info(f"🔧 Creating indexes ({'DRY RUN' if dry_run else 'LIVE RUN'})")

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_questions_is_active ON questions(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty_level);",
        "CREATE INDEX IF NOT EXISTS idx_questions_category_active ON questions(category, is_active);"
    ]

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for index_sql in indexes:
                if dry_run:
                    logger.info(f"📝 Would execute: {index_sql}")
                else:
                    logger.info(f"📝 Creating index...")
                    cur.execute(index_sql)
                    logger.info(f"✅ Index created")

            if not dry_run:
                conn.commit()
                logger.info("✅ All indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

    return True

def verify_changes():
    """Verify that changes were applied correctly"""
    logger.info("🔍 Verifying table structure...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'questions'
                AND column_name IN ('is_active', 'difficulty_level', 'deactivated_at', 'deactivated_reason')
                ORDER BY column_name
            """)
            columns = cur.fetchall()

            logger.info("📊 New columns in questions table:")
            for col in columns:
                logger.info(f"  {col['column_name']}: {col['data_type']} (default: {col['column_default']})")

            # Check sample data
            cur.execute("""
                SELECT
                    COUNT(*) as total_questions,
                    COUNT(*) FILTER (WHERE is_active = true) as active_questions,
                    COUNT(*) FILTER (WHERE is_active = false) as inactive_questions,
                    AVG(difficulty_level) as avg_difficulty
                FROM questions
            """)
            stats = cur.fetchone()

            logger.info("📊 Question statistics:")
            logger.info(f"  Total questions: {stats['total_questions']}")
            logger.info(f"  Active questions: {stats['active_questions']}")
            logger.info(f"  Inactive questions: {stats['inactive_questions']}")
            logger.info(f"  Average difficulty: {stats['avg_difficulty']:.1f}")

            # Show sample questions
            cur.execute("""
                SELECT id, question_text[:50] as question_preview, category, is_active, difficulty_level
                FROM questions
                ORDER BY id
                LIMIT 3
            """)
            samples = cur.fetchall()

            logger.info("📊 Sample questions with new fields:")
            for sample in samples:
                logger.info(f"  Q{sample['id']}: '{sample['question_preview']}...' | {sample['category']} | Active: {sample['is_active']} | Difficulty: {sample['difficulty_level']}")

            return len(columns) == 4

    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function"""
    logger.info("🚀 Starting Question Management Enhancement")

    # Parse command line arguments
    dry_run = '--live' not in sys.argv

    if dry_run:
        logger.info("📋 Running in DRY RUN mode. Use --live to execute changes.")
    else:
        logger.warning("⚠️  Running in LIVE mode. Changes will be applied to database.")

    try:
        # Step 1: Add columns
        if not add_question_management_columns(dry_run):
            logger.error("Failed to add columns")
            return False

        # Step 2: Create indexes
        if not create_indexes(dry_run):
            logger.error("Failed to create indexes")
            return False

        # Step 3: Verify changes (only in live mode)
        if not dry_run:
            if not verify_changes():
                logger.error("Verification failed")
                return False

        logger.info("✅ Question management enhancement completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Enhancement failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)