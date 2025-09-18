#!/usr/bin/env python3
"""
Test RLS issue - why reflections aren't showing for authenticated user
"""

import requests
import json

SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwNzEzNzYsImV4cCI6MjA3MzY0NzM3Nn0.I8JpWNqUlhWUkAdAbmRnHxYY0sFOXgyPFgvBSnerNt4"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8"

def test_auth_login():
    """Get auth token for testing RLS"""

    print("🔐 GETTING AUTH TOKEN")
    print("=" * 60)

    auth_headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Content-Type': 'application/json'
    }

    login_data = {
        'email': 'lukemoeller@yahoo.com',
        'password': 'TempPass123!'
    }

    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers=auth_headers,
        json=login_data
    )

    if response.status_code == 200:
        login_result = response.json()
        access_token = login_result.get('access_token')
        user = login_result.get('user', {})

        print(f"✅ Auth successful")
        print(f"🎫 Token: {access_token[:20]}..." if access_token else "❌ No token")
        print(f"👤 User ID: {user.get('id')}")
        print(f"📧 Email: {user.get('email')}")

        return access_token, user.get('id')
    else:
        print(f"❌ Auth failed: {response.status_code}")
        try:
            error = response.json()
            print(f"Error: {error}")
        except:
            pass
        return None, None

def test_reflections_with_auth(access_token, auth_user_id):
    """Test reflections access with auth token"""

    print(f"\n📊 TESTING REFLECTIONS WITH AUTH TOKEN")
    print("=" * 60)

    auth_headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Test direct reflections query (what RLS sees)
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/reflections?select=id,user_id&limit=5",
        headers=auth_headers
    )

    print(f"Direct reflections query: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {len(data)} reflections through RLS")
        for r in data[:3]:
            print(f"   Reflection {r['id']}: user_id={r['user_id']}")
    else:
        print(f"❌ RLS blocking reflections access")
        try:
            error = response.json()
            print(f"Error: {error}")
        except:
            pass

    # Test user lookup with auth token
    print(f"\n👤 Testing user lookup with auth token...")
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?select=id,auth_id,email",
        headers=auth_headers
    )

    print(f"User lookup: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {len(data)} users through RLS")
        for u in data:
            print(f"   User {u['id']}: auth_id={u['auth_id']}, email={u['email']}")
    else:
        print(f"❌ RLS blocking user access")

def test_with_service_key():
    """Test with service key to see actual data"""

    print(f"\n🔑 TESTING WITH SERVICE KEY (BYPASS RLS)")
    print("=" * 60)

    service_headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json'
    }

    # Count reflections for user_id 2
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/reflections?user_id=eq.2&select=count",
        headers=service_headers
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Service key shows {len(data)} reflections for user_id 2")
    else:
        print(f"❌ Service key query failed: {response.status_code}")

def main():
    """Main test"""

    print("🧪 RLS TROUBLESHOOTING TEST")
    print("=" * 60)
    print("Testing why reflections aren't showing with normal auth")
    print()

    # Get auth token
    access_token, auth_user_id = test_auth_login()

    if not access_token:
        print("❌ Cannot get auth token - stopping test")
        return

    # Test reflections with auth
    test_reflections_with_auth(access_token, auth_user_id)

    # Test with service key for comparison
    test_with_service_key()

    print(f"\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print("If reflections aren't showing through RLS but exist with service key,")
    print("then the RLS policies are incorrectly blocking access.")
    print()
    print("🔄 WORKAROUND: Use dev mode login (Luke19841984!) until RLS is fixed")
    print("🔧 SOLUTION: Fix the RLS policies to properly recognize authenticated users")

if __name__ == "__main__":
    main()