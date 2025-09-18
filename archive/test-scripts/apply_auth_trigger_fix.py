#!/usr/bin/env python3
"""
Apply the auth trigger fix to Supabase database.
This will allow proper Supabase Auth account creation for existing users.
"""

import os
import psycopg2
from urllib.parse import urlparse

def apply_trigger_fix():
    # Get database connection details from environment
    supabase_url = os.getenv('SUPABASE_URL', 'https://cbaudsvlidzfxvmzdvcg.supabase.co')

    # Parse the database URL (remove /rest/v1 and replace with direct DB port)
    parsed = urlparse(supabase_url)
    host = parsed.hostname  # This will be something like 'cbaudsvlidzfxvmzdvcg.supabase.co'

    # Extract project ID from hostname
    project_id = host.split('.')[0]  # Extract 'cbaudsvlidzfxvmzdvcg'

    # Supabase direct database connection details
    db_host = f"db.{project_id}.supabase.co"
    db_port = 5432
    db_name = "postgres"
    db_user = "postgres"
    db_password = "Luke19841984!"  # Your database password

    print(f"🔗 Connecting to database: {db_host}")

    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )

        cursor = conn.cursor()

        # Read and execute the trigger fix
        trigger_fix_sql = """
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY DEFINER SET search_path = public
        AS $$
        BEGIN
            INSERT INTO public.users (auth_id, email, name)
            VALUES (
                NEW.id,
                NEW.email,
                COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
            )
            ON CONFLICT (email) DO UPDATE SET
                auth_id = NEW.id,
                name = COALESCE(NEW.raw_user_meta_data->>'full_name', users.name),
                updated_at = NOW();
            RETURN NEW;
        END;
        $$;
        """

        print("📝 Executing trigger fix...")
        cursor.execute(trigger_fix_sql)
        conn.commit()

        print("✅ Auth trigger fix applied successfully!")
        print("📧 You can now create a Supabase Auth account for lukemoeller@yahoo.com")

    except Exception as e:
        print(f"❌ Error applying trigger fix: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()

    return True

if __name__ == "__main__":
    success = apply_trigger_fix()
    if success:
        print("\n🎉 Database trigger fix completed!")
        print("💡 Next: Create Supabase Auth account using the signup process")
    else:
        print("\n💥 Failed to apply trigger fix")