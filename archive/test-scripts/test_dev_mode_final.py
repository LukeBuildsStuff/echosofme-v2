#!/usr/bin/env python3
"""
Test dev mode login functionality after fixes
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwNzEzNzYsImV4cCI6MjA3MzY0NzM3Nn0.I8JpWNqUlhWUkAdAbmRnHxYY0sFOXgyPFgvBSnerNt4"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8"

def test_dev_mode():
    print("\n🔧 Testing Dev Mode Login")
    print("=" * 50)

    # Create admin client (bypasses RLS)
    admin_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Test fetching user data
    print("\n📊 Fetching user data with service key...")
    try:
        user_result = admin_client.table('users').select('*').eq('email', 'lukemoeller@yahoo.com').execute()
        if user_result.data:
            user = user_result.data[0]
            print(f"✅ User found: {user['name']} (ID: {user['id']})")
            user_id = user['id']

            # Test fetching reflections
            print(f"\n📊 Fetching reflections for user {user_id}...")
            reflections_result = admin_client.table('reflections').select('*').eq('user_id', user_id).execute()

            if reflections_result.data:
                print(f"✅ Found {len(reflections_result.data)} reflections")

                # Show recent reflections
                recent = sorted(reflections_result.data, key=lambda x: x['created_at'], reverse=True)[:3]
                print("\n📝 Recent reflections:")
                for r in recent:
                    text = r['response_text'][:100] + '...' if len(r['response_text']) > 100 else r['response_text']
                    print(f"  - {r['created_at'][:10]}: {text}")
            else:
                print("❌ No reflections found")

            # Test saving a new reflection
            print("\n💾 Testing save functionality...")
            test_reflection = {
                'user_id': user_id,
                'question_id': 1,
                'response_text': 'Test reflection from dev mode - after fixes',
                'word_count': 8,
                'is_draft': False,
                'response_type': 'reflection'
            }

            save_result = admin_client.table('reflections').insert(test_reflection).execute()
            if save_result.data:
                print("✅ Successfully saved test reflection")
                reflection_id = save_result.data[0]['id']

                # Clean up
                admin_client.table('reflections').delete().eq('id', reflection_id).execute()
                print("🧹 Cleaned up test reflection")
            else:
                print("❌ Failed to save reflection")

        else:
            print("❌ User not found")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_normal_auth():
    print("\n🔐 Testing Normal Authentication")
    print("=" * 50)

    # Create regular client
    client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Try to sign in with normal auth
        print("\n🔑 Attempting normal login...")
        auth_result = client.auth.sign_in_with_password({
            "email": "lukemoeller@yahoo.com",
            "password": "TempPass123!"
        })

        if auth_result.user:
            print(f"✅ Successfully logged in as: {auth_result.user.email}")
            print(f"   Auth ID: {auth_result.user.id}")

            # Try to fetch reflections (this will fail if RLS is still enabled)
            print("\n📊 Testing reflection access with normal auth...")
            try:
                reflections = client.table('reflections').select('*').execute()
                if reflections.data is not None:
                    print(f"✅ Can access reflections! Found {len(reflections.data)} total")
                else:
                    print("⚠️ No reflections returned (might be RLS issue)")
            except Exception as e:
                print(f"❌ Cannot access reflections: {e}")
                print("   This indicates RLS is still blocking access")

        else:
            print("❌ Failed to authenticate")
    except Exception as e:
        print(f"❌ Authentication error: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ECHOES OF ME - AUTHENTICATION TEST (POST-FIX)")
    print("=" * 60)

    test_dev_mode()
    test_normal_auth()

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Run the DISABLE_RLS.sql script in Supabase Dashboard")
    print("2. Test the app at http://localhost:5173")
    print("3. Try both dev mode (Luke19841984!) and normal auth (TempPass123!)")
    print("=" * 60)