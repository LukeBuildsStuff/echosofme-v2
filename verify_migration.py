#!/usr/bin/env python3
"""
Pre-migration data verification
Analyzes current database state before Supabase migration
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# Local database config - matches existing connection pattern
LOCAL_DB = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

def get_db_connection():
    """Get database connection using existing pattern"""
    try:
        return psycopg2.connect(**LOCAL_DB, cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure Docker PostgreSQL is running on host.docker.internal:5432")
        return None

def verify_current_data():
    """Verify current database state"""
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Count all important tables
            tables_to_check = [
                'users', 'reflections', 'questions', 'user_profiles',
                'ai_conversations', 'voice_profiles', 'training_datasets'
            ]

            print("📊 CURRENT DATABASE STATE:")
            print("=" * 50)

            total_records = 0
            for table in tables_to_check:
                try:
                    cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = cur.fetchone()['count']
                    total_records += count
                    print(f"{table:20}: {count:,} records")
                except Exception as e:
                    print(f"{table:20}: Error - {e}")

            print(f"\nTotal records: {total_records:,}")

            # Check database size
            try:
                cur.execute("SELECT pg_database_size('echosofme_dev')/1024/1024 as size_mb")
                size = cur.fetchone()['size_mb']
                print(f"Database size: {size:.2f} MB")
            except Exception as e:
                print(f"Database size: Error - {e}")

            # Check for users without passwords (critical security issue)
            try:
                cur.execute("SELECT COUNT(*) FROM users WHERE password_hash IS NULL OR password_hash = ''")
                no_password = cur.fetchone()[0]
                print(f"\n🚨 SECURITY ISSUE:")
                print(f"Users without passwords: {no_password}")
                if no_password > 0:
                    print("⚠️  THIS IS WHY WE'RE MIGRATING TO SUPABASE!")
            except Exception as e:
                print(f"Password check error: {e}")

            # Get sample user data
            try:
                cur.execute("SELECT id, email, name, created_at FROM users LIMIT 5")
                users = cur.fetchall()
                print(f"\n👥 SAMPLE USERS:")
                for user in users:
                    print(f"  {user['id']:3}: {user['email']:30} {user['name'] or 'No name'}")
            except Exception as e:
                print(f"Users sample error: {e}")

            # Get reflection statistics
            try:
                cur.execute("""
                    SELECT
                        COUNT(*) as total_reflections,
                        COUNT(DISTINCT user_id) as users_with_reflections,
                        AVG(word_count) as avg_word_count,
                        MAX(created_at) as latest_reflection,
                        MIN(created_at) as earliest_reflection
                    FROM reflections
                """)
                stats = cur.fetchone()
                print(f"\n💭 REFLECTION STATISTICS:")
                print(f"  Total reflections: {stats['total_reflections']:,}")
                print(f"  Active users: {stats['users_with_reflections']}")
                print(f"  Average words: {stats['avg_word_count']:.1f}")
                print(f"  Date range: {stats['earliest_reflection']} to {stats['latest_reflection']}")
            except Exception as e:
                print(f"Reflection stats error: {e}")

            # Get question categories
            try:
                cur.execute("""
                    SELECT category, COUNT(*) as count
                    FROM questions
                    GROUP BY category
                    ORDER BY count DESC
                """)
                categories = cur.fetchall()
                print(f"\n❓ QUESTION CATEGORIES:")
                for cat in categories:
                    print(f"  {cat['category']:25}: {cat['count']:,} questions")
            except Exception as e:
                print(f"Categories error: {e}")

    finally:
        conn.close()

    print("\n✅ Verification complete")
    print("\n📋 NEXT STEPS:")
    print("1. Create Supabase projects (dev & prod)")
    print("2. Export database with: python3 export_database.py")
    print("3. Follow SUPABASE_MIGRATION.md guide")

def check_database_connectivity():
    """Test database connection and provide helpful error messages"""
    print("🔍 Testing database connectivity...")

    conn = get_db_connection()
    if conn:
        print("✅ Database connection successful!")
        conn.close()
        return True
    else:
        print("\n💡 Troubleshooting tips:")
        print("- Ensure Docker PostgreSQL container is running")
        print("- Check if host.docker.internal resolves")
        print("- Verify database credentials match Docker setup")
        print("- Try: docker ps | grep postgres")
        return False

if __name__ == "__main__":
    print(f"🚀 Echoes of Me - Migration Verification")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    if check_database_connectivity():
        verify_current_data()
    else:
        print("❌ Cannot proceed without database connection")
        exit(1)