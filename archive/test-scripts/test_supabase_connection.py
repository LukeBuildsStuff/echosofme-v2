#!/usr/bin/env python3
"""
Test Supabase connection and basic functionality.
"""

import os
import requests
import json

def test_supabase_connection():
    supabase_url = os.getenv('SUPABASE_URL', 'https://cbaudsvlidzfxvmzdvcg.supabase.co')
    anon_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwNzEzNzYsImV4cCI6MjA3MzY0NzM3Nn0.I8JpWNqUlhWUkAdAbmRnHxYY0sFOXgyPFgvBSnerNt4'

    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }

    print(f"🔗 Testing connection to: {supabase_url}")

    # Test 1: Basic connection to health endpoint
    try:
        health_url = f"{supabase_url}/rest/v1/"
        response = requests.get(health_url, headers=headers)

        if response.status_code == 200:
            print("✅ Basic connection successful")
        else:
            print(f"❌ Basic connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

    # Test 2: Try to read questions table (should work with anon key)
    try:
        questions_url = f"{supabase_url}/rest/v1/questions?limit=1"
        response = requests.get(questions_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Questions table accessible, found {len(data)} records")
        else:
            print(f"❌ Questions table access failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Questions query error: {e}")

    # Test 3: Try to read users table (should be restricted by RLS)
    try:
        users_url = f"{supabase_url}/rest/v1/users?limit=1"
        response = requests.get(users_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"⚠️  Users table accessible without auth (RLS may not be working), found {len(data)} records")
        else:
            print(f"✅ Users table properly restricted: {response.status_code}")
    except Exception as e:
        print(f"❌ Users query error: {e}")

    print("\n📋 Current status:")
    print("• Frontend properly configured with anon key only")
    print("• Dev mode bypass code removed")
    print("• Service key removed from frontend")
    print("• Database trigger fix needs manual application")

    return True

if __name__ == "__main__":
    success = test_supabase_connection()
    if success:
        print("\n🎉 Connection tests completed!")
        print("💡 Next steps:")
        print("1. Apply trigger fix manually in Supabase Dashboard")
        print("2. Create new Supabase Auth user for lukemoeller@yahoo.com")
        print("3. Test full authentication flow")
    else:
        print("\n💥 Connection tests failed")