#!/usr/bin/env python3
"""
Migrate data from local PostgreSQL to Supabase
Handles migration of users, questions, reflections, and related data
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from supabase import create_client
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Local database configuration
LOCAL_DB = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

# Supabase configuration (will be set via environment variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    logger.error("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
    exit(1)

def get_local_connection():
    """Get connection to local PostgreSQL database"""
    try:
        return psycopg2.connect(**LOCAL_DB, cursor_factory=RealDictCursor)
    except Exception as e:
        logger.error(f"Failed to connect to local database: {e}")
        return None

def get_supabase_client():
    """Get Supabase client"""
    try:
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None

def migrate_questions():
    """Migrate questions table (no user dependency)"""
    logger.info("📋 Migrating questions...")

    local_conn = get_local_connection()
    supabase = get_supabase_client()

    if not local_conn or not supabase:
        return False

    try:
        with local_conn.cursor() as cur:
            cur.execute("SELECT * FROM questions ORDER BY id")
            questions = cur.fetchall()

            logger.info(f"Found {len(questions)} questions to migrate")

            # Migrate in batches to avoid timeouts
            batch_size = 100
            successful_migrations = 0

            for i in range(0, len(questions), batch_size):
                batch = questions[i:i+batch_size]
                batch_data = []

                for question in batch:
                    # Convert to dict and prepare for Supabase
                    question_data = dict(question)

                    # Convert datetime objects to strings
                    for key, value in question_data.items():
                        if hasattr(value, 'isoformat'):  # datetime object
                            question_data[key] = value.isoformat()

                    # Map field names if needed
                    if 'question' in question_data:
                        question_data['question_text'] = question_data.pop('question')

                    # Filter out columns that don't exist in Supabase schema
                    allowed_columns = {
                        'id', 'question_text', 'category', 'subcategory', 'difficulty_level',
                        'is_active', 'created_at', 'updated_at', 'tags', 'context_info',
                        'follow_up_prompts', 'estimated_time_minutes', 'requires_preparation',
                        'emotional_intensity', 'age_appropriateness', 'cultural_sensitivity',
                        'therapeutic_value', 'memory_type', 'recommended_frequency'
                    }
                    question_data = {k: v for k, v in question_data.items() if k in allowed_columns}

                    # Ensure required fields
                    if 'category' not in question_data or not question_data['category']:
                        question_data['category'] = 'general'

                    if 'is_active' not in question_data:
                        question_data['is_active'] = True

                    batch_data.append(question_data)

                # Insert batch to Supabase
                try:
                    result = supabase.table('questions').insert(batch_data).execute()
                    successful_migrations += len(batch)
                    logger.info(f"  Migrated batch {i//batch_size + 1}: {len(batch)} questions")
                except Exception as e:
                    logger.error(f"  Failed to migrate questions batch {i//batch_size + 1}: {e}")

            logger.info(f"✅ Migrated {successful_migrations}/{len(questions)} questions")
            return successful_migrations == len(questions)

    except Exception as e:
        logger.error(f"Error migrating questions: {e}")
        return False
    finally:
        local_conn.close()

def migrate_users():
    """Migrate users (will need manual auth account creation later)"""
    logger.info("👥 Migrating users...")
    logger.warning("⚠️  Note: Users will need to set passwords manually after Supabase auth setup")

    local_conn = get_local_connection()
    supabase = get_supabase_client()

    if not local_conn or not supabase:
        return False

    try:
        with local_conn.cursor() as cur:
            cur.execute("SELECT * FROM users ORDER BY id")
            users = cur.fetchall()

            logger.info(f"Found {len(users)} users to migrate")

            successful_migrations = 0

            for user in users:
                try:
                    user_data = dict(user)

                    # Convert datetime objects to strings
                    for key, value in user_data.items():
                        if hasattr(value, 'isoformat'):  # datetime object
                            user_data[key] = value.isoformat()

                    # Remove auth-related fields that Supabase Auth handles
                    user_data.pop('password_hash', None)
                    # Keep auth_id as null for now - will be set during user auth migration

                    # Ensure required fields
                    if not user_data.get('email'):
                        logger.warning(f"Skipping user {user_data.get('id')} - no email")
                        continue

                    if not user_data.get('role'):
                        user_data['role'] = 'user'

                    if 'is_active' not in user_data:
                        user_data['is_active'] = True

                    # Insert to Supabase
                    result = supabase.table('users').insert(user_data).execute()
                    successful_migrations += 1
                    logger.info(f"  Migrated user: {user_data['email']}")

                except Exception as e:
                    logger.error(f"  Failed to migrate user {user.get('email', 'unknown')}: {e}")

            logger.info(f"✅ Migrated {successful_migrations}/{len(users)} users")
            return successful_migrations == len(users)

    except Exception as e:
        logger.error(f"Error migrating users: {e}")
        return False
    finally:
        local_conn.close()

def migrate_reflections():
    """Migrate reflections"""
    logger.info("💭 Migrating reflections...")

    local_conn = get_local_connection()
    supabase = get_supabase_client()

    if not local_conn or not supabase:
        return False

    try:
        with local_conn.cursor() as cur:
            cur.execute("SELECT * FROM reflections ORDER BY id")
            reflections = cur.fetchall()

            logger.info(f"Found {len(reflections)} reflections to migrate")

            # Migrate in batches
            batch_size = 50  # Smaller batches for reflections (larger records)
            successful_migrations = 0

            for i in range(0, len(reflections), batch_size):
                batch = reflections[i:i+batch_size]
                batch_data = []

                for reflection in batch:
                    reflection_data = dict(reflection)

                    # Convert datetime objects to strings
                    for key, value in reflection_data.items():
                        if hasattr(value, 'isoformat'):  # datetime object
                            reflection_data[key] = value.isoformat()

                    # Ensure required fields have defaults
                    if 'word_count' not in reflection_data or not reflection_data['word_count']:
                        response_text = reflection_data.get('response_text', '')
                        reflection_data['word_count'] = len(response_text.split()) if response_text else 0

                    if 'is_draft' not in reflection_data:
                        reflection_data['is_draft'] = False

                    if 'response_type' not in reflection_data:
                        reflection_data['response_type'] = 'reflection'

                    if 'privacy_level' not in reflection_data:
                        reflection_data['privacy_level'] = 'private'

                    batch_data.append(reflection_data)

                # Insert batch to Supabase
                try:
                    result = supabase.table('reflections').insert(batch_data).execute()
                    successful_migrations += len(batch)
                    logger.info(f"  Migrated batch {i//batch_size + 1}: {len(batch)} reflections")
                except Exception as e:
                    logger.error(f"  Failed to migrate reflections batch {i//batch_size + 1}: {e}")

            logger.info(f"✅ Migrated {successful_migrations}/{len(reflections)} reflections")
            return successful_migrations == len(reflections)

    except Exception as e:
        logger.error(f"Error migrating reflections: {e}")
        return False
    finally:
        local_conn.close()

def migrate_user_profiles():
    """Migrate user profiles"""
    logger.info("📝 Migrating user profiles...")

    local_conn = get_local_connection()
    supabase = get_supabase_client()

    if not local_conn or not supabase:
        return False

    try:
        with local_conn.cursor() as cur:
            cur.execute("SELECT * FROM user_profiles ORDER BY id")
            profiles = cur.fetchall()

            logger.info(f"Found {len(profiles)} user profiles to migrate")

            successful_migrations = 0

            for profile in profiles:
                try:
                    profile_data = dict(profile)

                    # Convert datetime objects to strings
                    for key, value in profile_data.items():
                        if hasattr(value, 'isoformat'):  # datetime object
                            profile_data[key] = value.isoformat()

                    # Insert to Supabase
                    result = supabase.table('user_profiles').insert(profile_data).execute()
                    successful_migrations += 1
                    logger.info(f"  Migrated profile for user_id: {profile_data['user_id']}")

                except Exception as e:
                    logger.error(f"  Failed to migrate profile for user_id {profile.get('user_id', 'unknown')}: {e}")

            logger.info(f"✅ Migrated {successful_migrations}/{len(profiles)} user profiles")
            return successful_migrations == len(profiles)

    except Exception as e:
        logger.error(f"Error migrating user profiles: {e}")
        return False
    finally:
        local_conn.close()

def migrate_ai_conversations():
    """Migrate AI conversations"""
    logger.info("🤖 Migrating AI conversations...")

    local_conn = get_local_connection()
    supabase = get_supabase_client()

    if not local_conn or not supabase:
        return False

    try:
        with local_conn.cursor() as cur:
            # Check if ai_conversations table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'ai_conversations'
                )
            """)

            if not cur.fetchone()[0]:
                logger.info("  No ai_conversations table found, skipping...")
                return True

            cur.execute("SELECT * FROM ai_conversations ORDER BY id")
            conversations = cur.fetchall()

            logger.info(f"Found {len(conversations)} AI conversations to migrate")

            # Migrate in batches
            batch_size = 25
            successful_migrations = 0

            for i in range(0, len(conversations), batch_size):
                batch = conversations[i:i+batch_size]
                batch_data = []

                for conv in batch:
                    conv_data = dict(conv)

                    # Convert datetime objects to strings
                    for key, value in conv_data.items():
                        if hasattr(value, 'isoformat'):  # datetime object
                            conv_data[key] = value.isoformat()

                    # Ensure required fields
                    if 'conversation_type' not in conv_data:
                        conv_data['conversation_type'] = 'echo'

                    if 'model_version' not in conv_data:
                        conv_data['model_version'] = 'Eleanor-v1'

                    batch_data.append(conv_data)

                # Insert batch to Supabase
                try:
                    result = supabase.table('ai_conversations').insert(batch_data).execute()
                    successful_migrations += len(batch)
                    logger.info(f"  Migrated batch {i//batch_size + 1}: {len(batch)} conversations")
                except Exception as e:
                    logger.error(f"  Failed to migrate conversations batch {i//batch_size + 1}: {e}")

            logger.info(f"✅ Migrated {successful_migrations}/{len(conversations)} AI conversations")
            return successful_migrations == len(conversations)

    except Exception as e:
        logger.error(f"Error migrating AI conversations: {e}")
        return False
    finally:
        local_conn.close()

def migrate_additional_tables():
    """Migrate additional tables (voice_profiles, training_datasets)"""
    additional_tables = ['voice_profiles', 'training_datasets']

    for table_name in additional_tables:
        logger.info(f"🔄 Migrating {table_name}...")

        local_conn = get_local_connection()
        supabase = get_supabase_client()

        if not local_conn or not supabase:
            continue

        try:
            with local_conn.cursor() as cur:
                # Check if table exists
                cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = '{table_name}'
                    )
                """)

                if not cur.fetchone()[0]:
                    logger.info(f"  No {table_name} table found, skipping...")
                    continue

                cur.execute(f"SELECT * FROM {table_name} ORDER BY id")
                records = cur.fetchall()

                if not records:
                    logger.info(f"  No records in {table_name}")
                    continue

                logger.info(f"Found {len(records)} records in {table_name}")

                # Migrate in batches
                batch_size = 50
                successful_migrations = 0

                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    batch_data = []

                    for record in batch:
                        record_data = dict(record)
                        # Convert datetime objects to strings
                        for key, value in record_data.items():
                            if hasattr(value, 'isoformat'):  # datetime object
                                record_data[key] = value.isoformat()
                        batch_data.append(record_data)

                    try:
                        result = supabase.table(table_name).insert(batch_data).execute()
                        successful_migrations += len(batch)
                        logger.info(f"  Migrated batch {i//batch_size + 1}: {len(batch)} records")
                    except Exception as e:
                        logger.error(f"  Failed to migrate {table_name} batch {i//batch_size + 1}: {e}")

                logger.info(f"✅ Migrated {successful_migrations}/{len(records)} {table_name}")

        except Exception as e:
            logger.error(f"Error migrating {table_name}: {e}")
        finally:
            local_conn.close()

def verify_migration():
    """Verify migration by comparing record counts"""
    logger.info("🔍 Verifying migration...")

    local_conn = get_local_connection()
    supabase = get_supabase_client()

    if not local_conn or not supabase:
        return False

    tables_to_verify = ['users', 'questions', 'reflections', 'user_profiles']
    verification_passed = True

    try:
        with local_conn.cursor() as cur:
            for table in tables_to_verify:
                try:
                    # Get local count
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    local_count = cur.fetchone()[0]

                    # Get Supabase count
                    result = supabase.table(table).select('id', count='exact').execute()
                    supabase_count = result.count or 0

                    status = "✅" if local_count == supabase_count else "❌"
                    logger.info(f"  {table}: Local={local_count}, Supabase={supabase_count} {status}")

                    if local_count != supabase_count:
                        verification_passed = False

                except Exception as e:
                    logger.error(f"  Error verifying {table}: {e}")
                    verification_passed = False

    except Exception as e:
        logger.error(f"Error during verification: {e}")
        verification_passed = False
    finally:
        local_conn.close()

    if verification_passed:
        logger.info("🎉 Migration verification PASSED!")
    else:
        logger.warning("⚠️  Migration verification FAILED - check logs for details")

    return verification_passed

def migrate_all_tables():
    """Migrate all tables in correct order"""
    logger.info("🚀 Starting full data migration to Supabase...")
    logger.info("=" * 60)

    migration_steps = [
        ("Questions", migrate_questions),
        ("Users", migrate_users),
        ("User Profiles", migrate_user_profiles),
        ("Reflections", migrate_reflections),
        ("AI Conversations", migrate_ai_conversations),
        ("Additional Tables", migrate_additional_tables),
    ]

    successful_steps = 0

    for step_name, migration_func in migration_steps:
        logger.info(f"\n📂 Step: {step_name}")
        try:
            if migration_func():
                successful_steps += 1
                logger.info(f"✅ {step_name} migration completed")
            else:
                logger.error(f"❌ {step_name} migration failed")
        except Exception as e:
            logger.error(f"❌ {step_name} migration error: {e}")

    logger.info(f"\n📊 Migration Summary:")
    logger.info(f"Successful steps: {successful_steps}/{len(migration_steps)}")

    if successful_steps == len(migration_steps):
        logger.info("🎉 All migrations completed successfully!")

        # Run verification
        if verify_migration():
            logger.info("\n✅ DATA MIGRATION COMPLETE AND VERIFIED!")
            logger.info("\n📋 Next steps:")
            logger.info("1. Set up Supabase Row Level Security (RLS)")
            logger.info("2. Create auth accounts for existing users")
            logger.info("3. Update frontend to use Supabase")
            logger.info("4. Test authentication flow")
            return True
        else:
            logger.warning("\n⚠️  Migration completed but verification failed")
            return False
    else:
        logger.error("\n❌ Migration incomplete - check errors above")
        return False

if __name__ == "__main__":
    logger.info("🗄️  Supabase Data Migration Tool")
    logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Check environment variables
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.error("❌ Missing Supabase credentials")
        logger.error("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
        exit(1)

    logger.info(f"📡 Supabase URL: {SUPABASE_URL}")
    logger.info(f"🗄️  Local DB: {LOCAL_DB['host']}:{LOCAL_DB['port']}/{LOCAL_DB['database']}")

    if migrate_all_tables():
        logger.info("\n🎉 Migration completed successfully!")
        exit(0)
    else:
        logger.error("\n❌ Migration failed")
        exit(1)