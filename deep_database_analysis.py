#!/usr/bin/env python3
"""
Deep Database Analysis Script
Comprehensive analysis of the Echosofme database for integrity and consistency
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from collections import defaultdict, Counter
import logging

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

def analyze_schema():
    """Analyze database schema structure"""
    logger.info("=" * 80)
    logger.info("📊 ANALYZING DATABASE SCHEMA")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cur.fetchall()]
            
            logger.info(f"\n📋 Found {len(tables)} tables:")
            for table in tables:
                logger.info(f"  • {table}")
            
            # Analyze each table
            for table in tables:
                logger.info(f"\n📊 Table: {table}")
                
                # Get row count
                cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cur.fetchone()['count']
                logger.info(f"  Rows: {count:,}")
                
                # Get columns
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                columns = cur.fetchall()
                
                logger.info(f"  Columns ({len(columns)}):")
                for col in columns[:10]:  # Show first 10 columns
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    logger.info(f"    - {col['column_name']}: {col['data_type']} {nullable}{default}")
                if len(columns) > 10:
                    logger.info(f"    ... and {len(columns) - 10} more columns")
                
                # Get indexes
                cur.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = %s
                """, (table,))
                indexes = cur.fetchall()
                
                if indexes:
                    logger.info(f"  Indexes ({len(indexes)}):")
                    for idx in indexes[:5]:
                        logger.info(f"    - {idx['indexname']}")
                    if len(indexes) > 5:
                        logger.info(f"    ... and {len(indexes) - 5} more indexes")
                
                # Get constraints
                cur.execute("""
                    SELECT conname, contype
                    FROM pg_constraint
                    WHERE conrelid = %s::regclass
                """, (table,))
                constraints = cur.fetchall()
                
                if constraints:
                    constraint_types = Counter(c['contype'] for c in constraints)
                    logger.info(f"  Constraints:")
                    type_map = {'p': 'PRIMARY KEY', 'f': 'FOREIGN KEY', 'u': 'UNIQUE', 'c': 'CHECK'}
                    for ctype, count in constraint_types.items():
                        logger.info(f"    - {type_map.get(ctype, ctype)}: {count}")
    
    finally:
        conn.close()

def analyze_data_integrity():
    """Check for data integrity issues"""
    logger.info("\n" + "=" * 80)
    logger.info("🔍 ANALYZING DATA INTEGRITY")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    issues = []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Check for orphaned responses (responses without valid questions)
            logger.info("\n🔍 Checking for orphaned responses...")
            cur.execute("""
                SELECT COUNT(*) as count
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                WHERE q.id IS NULL
            """)
            orphaned_responses = cur.fetchone()['count']
            
            if orphaned_responses > 0:
                issues.append(f"Found {orphaned_responses} orphaned responses without valid questions")
                cur.execute("""
                    SELECT r.id, r.question_id, r.user_id, r.created_at
                    FROM responses r
                    LEFT JOIN questions q ON r.question_id = q.id
                    WHERE q.id IS NULL
                    LIMIT 5
                """)
                samples = cur.fetchall()
                logger.warning(f"  ⚠️ Found {orphaned_responses} orphaned responses!")
                for sample in samples:
                    logger.warning(f"    Response ID {sample['id']}: Question {sample['question_id']} missing")
            else:
                logger.info("  ✅ No orphaned responses found")
            
            # 2. Check for duplicate questions with same ID
            logger.info("\n🔍 Checking for duplicate question IDs...")
            cur.execute("""
                SELECT id, COUNT(*) as count
                FROM questions
                GROUP BY id
                HAVING COUNT(*) > 1
            """)
            duplicate_questions = cur.fetchall()
            
            if duplicate_questions:
                issues.append(f"Found {len(duplicate_questions)} duplicate question IDs")
                logger.warning(f"  ⚠️ Found {len(duplicate_questions)} duplicate question IDs!")
                for dup in duplicate_questions[:5]:
                    logger.warning(f"    Question ID {dup['id']}: {dup['count']} duplicates")
            else:
                logger.info("  ✅ No duplicate question IDs found")
            
            # 3. Check for responses without users
            logger.info("\n🔍 Checking for responses without valid users...")
            cur.execute("""
                SELECT COUNT(*) as count
                FROM responses r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE u.id IS NULL
            """)
            orphaned_user_responses = cur.fetchone()['count']
            
            if orphaned_user_responses > 0:
                issues.append(f"Found {orphaned_user_responses} responses without valid users")
                logger.warning(f"  ⚠️ Found {orphaned_user_responses} responses without valid users!")
            else:
                logger.info("  ✅ All responses have valid users")
            
            # 4. Check for duplicate responses (same user, same question)
            logger.info("\n🔍 Checking for duplicate responses...")
            cur.execute("""
                SELECT user_id, question_id, COUNT(*) as count
                FROM responses
                GROUP BY user_id, question_id
                HAVING COUNT(*) > 1
            """)
            duplicate_responses = cur.fetchall()
            
            if duplicate_responses:
                issues.append(f"Found {len(duplicate_responses)} duplicate user-question combinations")
                logger.warning(f"  ⚠️ Found {len(duplicate_responses)} duplicate responses!")
                for dup in duplicate_responses[:5]:
                    logger.warning(f"    User {dup['user_id']}, Question {dup['question_id']}: {dup['count']} responses")
            else:
                logger.info("  ✅ No duplicate responses found")
            
            # 5. Check for missing question snapshots
            logger.info("\n🔍 Checking question snapshot completeness...")
            cur.execute("""
                SELECT COUNT(*) as total,
                       COUNT(question_text_snapshot) as with_snapshot,
                       COUNT(*) - COUNT(question_text_snapshot) as without_snapshot
                FROM responses
            """)
            snapshot_stats = cur.fetchone()
            
            logger.info(f"  Total responses: {snapshot_stats['total']:,}")
            logger.info(f"  With snapshots: {snapshot_stats['with_snapshot']:,}")
            logger.info(f"  Without snapshots: {snapshot_stats['without_snapshot']:,}")
            
            if snapshot_stats['without_snapshot'] > 0:
                issues.append(f"Found {snapshot_stats['without_snapshot']} responses without question snapshots")
                logger.warning(f"  ⚠️ {snapshot_stats['without_snapshot']} responses missing snapshots!")
            else:
                logger.info("  ✅ All responses have question snapshots")
            
            # 6. Check for snapshot mismatches
            logger.info("\n🔍 Checking for snapshot mismatches...")
            cur.execute("""
                SELECT COUNT(*) as count
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.question_text_snapshot IS NOT NULL
                  AND r.question_text_snapshot != q.question_text
                  AND r.question_text_snapshot NOT LIKE '⚠️%'
            """)
            mismatches = cur.fetchone()['count']
            
            if mismatches > 0:
                logger.info(f"  ℹ️ {mismatches} responses have different snapshot text than current question")
                logger.info("    (This is expected and shows the snapshot system is working)")
                
                # Show some examples
                cur.execute("""
                    SELECT r.id, r.question_id, 
                           LEFT(r.question_text_snapshot, 50) as snapshot,
                           LEFT(q.question_text, 50) as current
                    FROM responses r
                    JOIN questions q ON r.question_id = q.id
                    WHERE r.question_text_snapshot IS NOT NULL
                      AND r.question_text_snapshot != q.question_text
                      AND r.question_text_snapshot NOT LIKE '⚠️%'
                    LIMIT 3
                """)
                examples = cur.fetchall()
                for ex in examples:
                    logger.info(f"    Example - Response {ex['id']}:")
                    logger.info(f"      Snapshot: {ex['snapshot']}...")
                    logger.info(f"      Current:  {ex['current']}...")
            else:
                logger.info("  ✅ All snapshots match current questions (no changes detected)")
    
    finally:
        conn.close()
    
    return issues

def analyze_questions():
    """Analyze questions table in detail"""
    logger.info("\n" + "=" * 80)
    logger.info("📚 ANALYZING QUESTIONS")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Total questions
            cur.execute("SELECT COUNT(*) as count FROM questions")
            total_questions = cur.fetchone()['count']
            logger.info(f"\n📊 Total questions: {total_questions:,}")
            
            # Questions by category
            cur.execute("""
                SELECT category, COUNT(*) as count
                FROM questions
                GROUP BY category
                ORDER BY count DESC
            """)
            categories = cur.fetchall()
            
            logger.info("\n📊 Questions by category:")
            for cat in categories:
                percentage = (cat['count'] / total_questions) * 100
                logger.info(f"  • {cat['category'] or 'NULL'}: {cat['count']:,} ({percentage:.1f}%)")
            
            # Check for missing question IDs in sequence
            cur.execute("""
                SELECT MIN(id) as min_id, MAX(id) as max_id
                FROM questions
            """)
            id_range = cur.fetchone()
            
            if id_range['min_id'] and id_range['max_id']:
                expected_count = id_range['max_id'] - id_range['min_id'] + 1
                missing_count = expected_count - total_questions
                
                logger.info(f"\n📊 Question ID analysis:")
                logger.info(f"  ID range: {id_range['min_id']:,} to {id_range['max_id']:,}")
                logger.info(f"  Expected questions: {expected_count:,}")
                logger.info(f"  Actual questions: {total_questions:,}")
                logger.info(f"  Missing IDs: {missing_count:,}")
                
                if missing_count > 0:
                    # Find some missing IDs
                    cur.execute("""
                        SELECT generate_series(%s, %s) as id
                        EXCEPT
                        SELECT id FROM questions
                        ORDER BY id
                        LIMIT 10
                    """, (id_range['min_id'], id_range['max_id']))
                    missing_ids = [row['id'] for row in cur.fetchall()]
                    logger.info(f"  Sample missing IDs: {missing_ids}")
            
            # Questions with most responses
            cur.execute("""
                SELECT q.id, q.question_text, q.category, COUNT(r.id) as response_count
                FROM questions q
                LEFT JOIN responses r ON q.id = r.question_id
                GROUP BY q.id, q.question_text, q.category
                ORDER BY response_count DESC
                LIMIT 10
            """)
            popular_questions = cur.fetchall()
            
            logger.info("\n📊 Most answered questions:")
            for q in popular_questions[:5]:
                logger.info(f"  • Q{q['id']}: {q['response_count']} responses")
                logger.info(f"    '{q['question_text'][:60]}...'")
            
            # Questions with no responses
            cur.execute("""
                SELECT COUNT(*) as count
                FROM questions q
                LEFT JOIN responses r ON q.id = r.question_id
                WHERE r.id IS NULL
            """)
            unanswered_count = cur.fetchone()['count']
            logger.info(f"\n📊 Unanswered questions: {unanswered_count:,}")
    
    finally:
        conn.close()

def analyze_responses():
    """Analyze responses table in detail"""
    logger.info("\n" + "=" * 80)
    logger.info("💬 ANALYZING RESPONSES")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Response statistics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_responses,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT question_id) as unique_questions,
                    AVG(word_count) as avg_word_count,
                    MIN(word_count) as min_word_count,
                    MAX(word_count) as max_word_count,
                    MIN(created_at) as earliest_response,
                    MAX(created_at) as latest_response
                FROM responses
            """)
            stats = cur.fetchone()
            
            logger.info("\n📊 Response statistics:")
            logger.info(f"  Total responses: {stats['total_responses']:,}")
            logger.info(f"  Unique users: {stats['unique_users']:,}")
            logger.info(f"  Unique questions answered: {stats['unique_questions']:,}")
            logger.info(f"  Average word count: {stats['avg_word_count']:.1f}")
            logger.info(f"  Word count range: {stats['min_word_count']} - {stats['max_word_count']}")
            logger.info(f"  Date range: {stats['earliest_response']} to {stats['latest_response']}")
            
            # Responses by user
            cur.execute("""
                SELECT u.email, COUNT(r.id) as response_count,
                       AVG(r.word_count) as avg_words,
                       COUNT(DISTINCT r.question_id) as unique_questions
                FROM responses r
                JOIN users u ON r.user_id = u.id
                GROUP BY u.id, u.email
                ORDER BY response_count DESC
            """)
            user_stats = cur.fetchall()
            
            logger.info("\n📊 Responses by user:")
            for user in user_stats[:5]:
                logger.info(f"  • {user['email']}: {user['response_count']:,} responses")
                logger.info(f"    Unique questions: {user['unique_questions']:,}, Avg words: {user['avg_words']:.1f}")
            
            # Response distribution over time
            cur.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM responses
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 10
            """)
            recent_activity = cur.fetchall()
            
            logger.info("\n📊 Recent activity (last 10 days with responses):")
            for day in recent_activity:
                logger.info(f"  {day['date']}: {day['count']} responses")
            
            # Check for data anomalies
            logger.info("\n🔍 Checking for anomalies...")
            
            # Responses with zero or null word count
            cur.execute("""
                SELECT COUNT(*) as count
                FROM responses
                WHERE word_count IS NULL OR word_count = 0
            """)
            zero_word_count = cur.fetchone()['count']
            
            if zero_word_count > 0:
                logger.warning(f"  ⚠️ {zero_word_count} responses with zero/null word count")
            else:
                logger.info("  ✅ All responses have valid word counts")
            
            # Very short responses
            cur.execute("""
                SELECT COUNT(*) as count
                FROM responses
                WHERE word_count < 10
            """)
            short_responses = cur.fetchone()['count']
            
            if short_responses > 0:
                logger.info(f"  ℹ️ {short_responses} responses with less than 10 words")
            
            # Check response_type distribution
            cur.execute("""
                SELECT response_type, COUNT(*) as count
                FROM responses
                GROUP BY response_type
            """)
            response_types = cur.fetchall()
            
            logger.info("\n📊 Response types:")
            for rtype in response_types:
                logger.info(f"  • {rtype['response_type'] or 'NULL'}: {rtype['count']:,}")
    
    finally:
        conn.close()

def analyze_users():
    """Analyze users and their data"""
    logger.info("\n" + "=" * 80)
    logger.info("👥 ANALYZING USERS")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # User statistics
            cur.execute("SELECT COUNT(*) as count FROM users")
            total_users = cur.fetchone()['count']
            logger.info(f"\n📊 Total users: {total_users}")
            
            # User profiles
            cur.execute("SELECT COUNT(*) as count FROM user_profiles")
            total_profiles = cur.fetchone()['count']
            logger.info(f"📊 User profiles: {total_profiles}")
            
            # Users with/without profiles
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT u.id) as users_with_profiles
                FROM users u
                JOIN user_profiles p ON u.email = p.email
            """)
            users_with_profiles = cur.fetchone()['users_with_profiles']
            logger.info(f"  Users with profiles: {users_with_profiles}")
            logger.info(f"  Users without profiles: {total_users - users_with_profiles}")
            
            # Profile completeness
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(display_name) as has_display_name,
                    COUNT(introduction) as has_introduction,
                    COUNT(relationship) as has_relationship,
                    COUNT(meeting_status) as has_meeting_status
                FROM user_profiles
            """)
            profile_stats = cur.fetchone()
            
            if profile_stats['total'] > 0:
                logger.info("\n📊 Profile completeness:")
                for field in ['display_name', 'introduction', 'relationship', 'meeting_status']:
                    count = profile_stats[f'has_{field}']
                    percentage = (count / profile_stats['total']) * 100
                    logger.info(f"  {field}: {count}/{profile_stats['total']} ({percentage:.1f}%)")
    
    finally:
        conn.close()

def generate_summary(issues):
    """Generate summary report"""
    logger.info("\n" + "=" * 80)
    logger.info("📋 SUMMARY REPORT")
    logger.info("=" * 80)
    
    if issues:
        logger.warning(f"\n⚠️ Found {len(issues)} potential issues:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"  {i}. {issue}")
    else:
        logger.info("\n✅ No critical issues found!")
    
    logger.info("\n📊 Database Health Score: ")
    if not issues:
        logger.info("  🟢 EXCELLENT - Database is in perfect condition!")
    elif len(issues) <= 2:
        logger.info("  🟡 GOOD - Minor issues that should be addressed")
    else:
        logger.info("  🔴 NEEDS ATTENTION - Multiple issues require fixing")
    
    logger.info("\n💡 Recommendations:")
    logger.info("  1. Regular backups are essential")
    logger.info("  2. Monitor response growth rate")
    logger.info("  3. Consider archiving old data if database grows large")
    logger.info("  4. Keep question snapshots feature enabled for data integrity")

def main():
    """Main analysis function"""
    logger.info("🔍 DEEP DATABASE ANALYSIS")
    logger.info("Starting comprehensive database analysis...")
    logger.info(f"Timestamp: {datetime.now()}")
    
    try:
        # Run all analyses
        analyze_schema()
        issues = analyze_data_integrity()
        analyze_questions()
        analyze_responses()
        analyze_users()
        generate_summary(issues)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Analysis complete!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()