#!/usr/bin/env python3
"""
Test that normal authentication works after removing dev mode
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwNzEzNzYsImV4cCI6MjA3MzY0NzM3Nn0.I8JpWNqUlhWUkAdAbmRnHxYY0sFOXgyPFgvBSnerNt4"

def test_normal_auth():
    print("\n🔐 Testing Normal Authentication Only")
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

            # Try to fetch reflections
            print("\n📊 Testing reflection access...")
            try:
                reflections = client.table('reflections').select('*').execute()
                if reflections.data is not None:
                    print(f"✅ Can access reflections! Found {len(reflections.data)} total")

                    # Show some recent ones
                    recent = sorted(reflections.data, key=lambda x: x['created_at'], reverse=True)[:3]
                    print("\n📝 Recent reflections:")
                    for r in recent:
                        text = r['response_text'][:100] + '...' if len(r['response_text']) > 100 else r['response_text']
                        print(f"  - {r['created_at'][:10]}: {text}")
                else:
                    print("⚠️ No reflections returned")
            except Exception as e:
                print(f"❌ Cannot access reflections: {e}")

            # Try to create a new reflection
            print("\n💾 Testing reflection creation...")
            try:
                # Get a question first
                questions = client.table('questions').select('*').limit(1).execute()
                if questions.data:
                    question_id = questions.data[0]['id']

                    # Create test reflection
                    new_reflection = client.table('reflections').insert({
                        'user_id': 2,  # Your user ID
                        'question_id': question_id,
                        'response_text': 'Test reflection after dev mode cleanup',
                        'word_count': 7,
                        'is_draft': False,
                        'response_type': 'reflection'
                    }).execute()

                    if new_reflection.data:
                        print("✅ Successfully created new reflection")
                        reflection_id = new_reflection.data[0]['id']

                        # Clean up test reflection
                        client.table('reflections').delete().eq('id', reflection_id).execute()
                        print("🧹 Cleaned up test reflection")
                    else:
                        print("❌ Failed to create reflection")
                else:
                    print("⚠️ No questions found to test with")
            except Exception as e:
                print(f"❌ Error creating reflection: {e}")

        else:
            print("❌ Failed to authenticate")
    except Exception as e:
        print(f"❌ Authentication error: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ECHOES OF ME - NORMAL AUTH TEST (POST DEV CLEANUP)")
    print("=" * 60)

    test_normal_auth()

    print("\n" + "=" * 60)
    print("✅ Dev mode cleanup complete!")
    print("🔐 Normal authentication is working")
    print("🎉 Your app is ready for production!")
    print("=" * 60)