#!/usr/bin/env python3
"""
Database export script for Supabase migration
Exports schema and data from current PostgreSQL database
"""
import subprocess
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

def run_command(command, description):
    """Run a shell command and capture output"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr.strip()}")
        return False

def create_export_directory():
    """Create timestamped export directory"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = f"database_export_{timestamp}"
    os.makedirs(export_dir, exist_ok=True)
    print(f"📁 Created export directory: {export_dir}")
    return export_dir

def export_database():
    """Export PostgreSQL database for Supabase migration"""
    print("🚀 Starting database export for Supabase migration")
    print("=" * 60)

    export_dir = create_export_directory()

    # Set environment variable for password
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_CONFIG['password']

    # Base pg_dump command
    base_cmd = f"pg_dump -h {DB_CONFIG['host']} -U {DB_CONFIG['user']} -d {DB_CONFIG['database']} -p {DB_CONFIG['port']}"

    exports = [
        {
            'file': f"{export_dir}/echosofme_full_backup.sql",
            'cmd': f"{base_cmd} -f {export_dir}/echosofme_full_backup.sql",
            'desc': "Full database backup (schema + data)"
        },
        {
            'file': f"{export_dir}/echosofme_schema.sql",
            'cmd': f"{base_cmd} --schema-only -f {export_dir}/echosofme_schema.sql",
            'desc': "Schema-only backup"
        },
        {
            'file': f"{export_dir}/echosofme_data.sql",
            'cmd': f"{base_cmd} --data-only -f {export_dir}/echosofme_data.sql",
            'desc': "Data-only backup"
        }
    ]

    success_count = 0
    for export in exports:
        cmd_with_env = f"PGPASSWORD={DB_CONFIG['password']} {export['cmd']}"
        if run_command(cmd_with_env, export['desc']):
            success_count += 1
            # Check file size
            if os.path.exists(export['file']):
                size = os.path.getsize(export['file']) / 1024 / 1024  # MB
                print(f"   File size: {size:.2f} MB")

    print(f"\n📊 Export Summary:")
    print(f"   Successful exports: {success_count}/{len(exports)}")
    print(f"   Export directory: {export_dir}")

    if success_count == len(exports):
        print("✅ All exports completed successfully!")

        # Create migration notes
        create_migration_notes(export_dir)

        print(f"\n📋 Next steps:")
        print(f"1. Create Supabase projects")
        print(f"2. Review exported files in {export_dir}/")
        print(f"3. Follow SUPABASE_MIGRATION.md Phase 2")

        return True
    else:
        print("⚠️  Some exports failed. Check Docker PostgreSQL is running.")
        return False

def create_migration_notes(export_dir):
    """Create migration notes file"""
    notes_file = f"{export_dir}/migration_notes.md"

    # Get current database stats
    stats = get_database_stats()

    content = f"""# Migration Export Notes

## Export Details
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source Database**: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}
- **Export Directory**: {export_dir}

## Database Statistics
{stats}

## Files Created
- `echosofme_full_backup.sql` - Complete database backup
- `echosofme_schema.sql` - Schema only (for Supabase import)
- `echosofme_data.sql` - Data only (for verification)

## Migration Steps
1. ✅ Database exported
2. ⏳ Create Supabase projects
3. ⏳ Import schema to Supabase
4. ⏳ Configure Row Level Security
5. ⏳ Migrate data
6. ⏳ Update application code

## Important Notes
- Review schema modifications needed for Supabase Auth
- Users table needs auth_id column instead of password_hash
- Configure RLS policies before data migration
- Test authentication flow thoroughly

## Rollback Plan
If migration fails, restore with:
```bash
psql -h {DB_CONFIG['host']} -U {DB_CONFIG['user']} -d {DB_CONFIG['database']} < echosofme_full_backup.sql
```
"""

    with open(notes_file, 'w') as f:
        f.write(content)

    print(f"📝 Created migration notes: {notes_file}")

def get_database_stats():
    """Get current database statistics"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

        with conn.cursor() as cur:
            # Table counts
            tables = ['users', 'reflections', 'questions', 'user_profiles', 'ai_conversations', 'voice_profiles']
            stats = []

            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    stats.append(f"- {table}: {count:,} records")
                except:
                    stats.append(f"- {table}: Error getting count")

            # Database size
            cur.execute("SELECT pg_database_size(current_database())/1024/1024 as size_mb")
            size = cur.fetchone()['size_mb']
            stats.append(f"- Total size: {size:.2f} MB")

            return "\n".join(stats)

    except Exception as e:
        return f"Error getting stats: {e}"
    finally:
        if 'conn' in locals():
            conn.close()

def test_pg_dump_availability():
    """Test if pg_dump is available"""
    try:
        result = subprocess.run(['pg_dump', '--version'], capture_output=True, text=True)
        print(f"✅ pg_dump available: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ pg_dump not found. Please install PostgreSQL client tools.")
        print("   Ubuntu/Debian: sudo apt-get install postgresql-client")
        print("   macOS: brew install postgresql")
        return False

if __name__ == "__main__":
    print("🗄️  PostgreSQL Database Export for Supabase Migration")
    print("=" * 60)

    if not test_pg_dump_availability():
        exit(1)

    if export_database():
        print("\n🎉 Database export completed successfully!")
        print("Ready for Supabase migration Phase 2")
    else:
        print("\n❌ Database export failed")
        print("Check database connection and try again")
        exit(1)