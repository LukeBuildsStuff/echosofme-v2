#!/usr/bin/env python3
"""
Apply the auth trigger fix via Supabase REST API.
This will allow proper Supabase Auth account creation for existing users.
"""

import os
import requests
import json

def apply_trigger_fix():
    # Get connection details from environment
    supabase_url = os.getenv('SUPABASE_URL', 'https://cbaudsvlidzfxvmzdvcg.supabase.co')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not service_key:
        print("❌ SUPABASE_SERVICE_KEY environment variable not set")
        return False

    # Construct the REST API endpoint for executing raw SQL
    rpc_url = f"{supabase_url}/rest/v1/rpc/exec_sql"

    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }

    # The SQL we want to execute
    sql = """
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

    payload = {
        'sql': sql
    }

    print(f"🔗 Connecting to Supabase API: {supabase_url}")
    print("📝 Executing trigger fix via REST API...")

    try:
        response = requests.post(rpc_url, headers=headers, json=payload)

        if response.status_code == 200:
            print("✅ Auth trigger fix applied successfully!")
            print("📧 You can now create a Supabase Auth account for lukemoeller@yahoo.com")
            return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")

            # Try alternative approach using the supabase Python client
            print("🔄 Trying alternative approach with supabase-py...")
            return try_supabase_client_approach(supabase_url, service_key, sql)

    except Exception as e:
        print(f"❌ Error executing via REST API: {e}")
        print("🔄 Trying alternative approach with supabase-py...")
        return try_supabase_client_approach(supabase_url, service_key, sql)

def try_supabase_client_approach(supabase_url, service_key, sql):
    """Try using the supabase Python client instead"""
    try:
        from supabase import create_client

        supabase = create_client(supabase_url, service_key)

        # Execute the SQL via RPC
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()

        print("✅ Auth trigger fix applied successfully via supabase-py!")
        return True

    except ImportError:
        print("❌ supabase-py not installed, cannot use alternative approach")
        return False
    except Exception as e:
        print(f"❌ Error with supabase-py approach: {e}")
        return False

if __name__ == "__main__":
    success = apply_trigger_fix()
    if success:
        print("\n🎉 Database trigger fix completed!")
        print("💡 Next: Create Supabase Auth account using the signup process")
    else:
        print("\n💥 Failed to apply trigger fix")
        print("📝 You may need to apply this manually in the Supabase Dashboard SQL Editor:")
        print("   1. Go to https://supabase.com/dashboard/project/cbaudsvlidzfxvmzdvcg/sql")
        print("   2. Execute the SQL from fix_auth_trigger_updated.sql")