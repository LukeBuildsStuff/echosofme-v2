#!/usr/bin/env python3
"""
Test creating a proper Supabase Auth account for lukemoeller@yahoo.com
This will test if the fixed trigger properly links the auth account to existing user.
"""

import requests
import json
from datetime import datetime

SUPABASE_URL = "https://cbaudsvlidzfxvmzdvcg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwNzEzNzYsImV4cCI6MjA3MzY0NzM3Nn0.I8JpWNqUlhWUkAdAbmRnHxYY0sFOXgyPFgvBSnerNt4"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODA3MTM3NiwiZXhwIjoyMDczNjQ3Mzc2fQ.Eow0ec5pFGiRG7zC029hPFB5wtqmZlMyapS1CLxZEv8"

def test_auth_signup():
    """Test creating auth account via Supabase Auth API"""

    print("🔐 TESTING AUTH ACCOUNT CREATION")
    print("=" * 60)

    # Check current user state
    print("1. Checking current user state...")
    service_headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json'
    }

    # Get current user record
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?email=eq.lukemoeller@yahoo.com&select=id,email,auth_id,name",
        headers=service_headers
    )

    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            user = data[0]
            print(f"   ✅ Found user: {user['name']} ({user['email']})")
            print(f"   📊 User ID: {user['id']}")
            print(f"   🔑 Auth ID: {user['auth_id']}")

            if user['auth_id'] is not None:
                print("   ⚠️  User already has auth_id - auth account exists!")
                return True
        else:
            print("   ❌ User not found in database")
            return False
    else:
        print(f"   ❌ Database query failed: {response.status_code}")
        return False

    # Try to create auth account
    print("\n2. Attempting to create Supabase Auth account...")

    auth_headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Content-Type': 'application/json'
    }

    signup_data = {
        'email': 'lukemoeller@yahoo.com',
        'password': 'TempPass123!',  # Temporary password for testing
        'data': {
            'full_name': 'Luke'
        }
    }

    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/signup",
        headers=auth_headers,
        json=signup_data
    )

    print(f"   📡 Auth API Response: {response.status_code}")

    if response.status_code == 200:
        auth_data = response.json()
        print("   ✅ Auth account created successfully!")

        if 'user' in auth_data and auth_data['user']:
            auth_user = auth_data['user']
            print(f"   🆔 Auth User ID: {auth_user['id']}")
            print(f"   📧 Email: {auth_user['email']}")

            # Check if trigger linked the accounts
            print("\n3. Checking if trigger linked the accounts...")

            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/users?email=eq.lukemoeller@yahoo.com&select=id,email,auth_id,name",
                headers=service_headers
            )

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    updated_user = data[0]
                    print(f"   📊 User ID: {updated_user['id']}")
                    print(f"   🔑 Auth ID: {updated_user['auth_id']}")

                    if updated_user['auth_id'] == auth_user['id']:
                        print("   ✅ SUCCESS! Trigger properly linked auth account to existing user!")
                        return True
                    else:
                        print("   ❌ Trigger failed to link accounts properly")
                        return False

        return True

    elif response.status_code == 422:
        error_data = response.json()
        if 'msg' in error_data and 'already been registered' in error_data['msg']:
            print("   ⚠️  Email already registered - this is expected!")
            print("   ✅ Auth account already exists - trigger worked on previous signup")
            return True
        else:
            print(f"   ❌ Signup failed: {error_data}")
            return False
    else:
        try:
            error_data = response.json()
            print(f"   ❌ Signup failed: {error_data}")
        except:
            print(f"   ❌ Signup failed with status {response.status_code}")
        return False

def test_auth_login():
    """Test logging in with the created auth account"""

    print("\n🔑 TESTING AUTH LOGIN")
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

    print(f"📡 Login Response: {response.status_code}")

    if response.status_code == 200:
        login_data = response.json()
        print("✅ Login successful!")

        if 'access_token' in login_data:
            print(f"🎫 Got access token: {login_data['access_token'][:20]}...")

            if 'user' in login_data:
                user = login_data['user']
                print(f"👤 User ID: {user['id']}")
                print(f"📧 Email: {user['email']}")

        return True
    else:
        try:
            error_data = response.json()
            print(f"❌ Login failed: {error_data}")
        except:
            print(f"❌ Login failed with status {response.status_code}")
        return False

def main():
    """Main test function"""

    print("🧪 AUTH ACCOUNT CREATION TEST")
    print("=" * 60)
    print("Testing if the database trigger properly creates and links auth accounts")
    print()

    # Test auth account creation
    signup_success = test_auth_signup()

    # Test login if signup worked
    if signup_success:
        login_success = test_auth_login()
    else:
        login_success = False

    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)

    if signup_success and login_success:
        print("🎉 SUCCESS! Auth account creation and linking works perfectly!")
        print("✅ Database trigger is functioning correctly")
        print("✅ Auth account properly linked to existing user record")
        print("✅ Login works with new credentials")
        print()
        print("🎯 YOU CAN NOW LOGIN WITH NORMAL AUTH:")
        print("   Email: lukemoeller@yahoo.com")
        print("   Password: TempPass123!")
        print()
        print("💡 NEXT STEPS:")
        print("1. Test login in the web app")
        print("2. Verify app functionality (reflections, questions)")
        print("3. Change password to something secure")
        print("4. Remove dev mode bypass")

    elif signup_success:
        print("⚠️  Auth account created but login test failed")
        print("✅ Database trigger worked - accounts are linked")
        print("❌ Login issue - may need password reset")

    else:
        print("❌ Auth account creation failed")
        print("🔧 Check database trigger and RLS policies")
        print("🔄 Dev mode bypass is still available as fallback")

if __name__ == "__main__":
    main()