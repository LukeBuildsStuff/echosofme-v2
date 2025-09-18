#!/usr/bin/env python3
"""
Create Supabase Auth account for existing user
"""
import os
from src.services.supabase_service import get_supabase_service
from dotenv import load_dotenv

load_dotenv()

def create_auth_for_user(email: str, password: str):
    """Create Supabase Auth account for existing user"""
    service = get_supabase_service()

    try:
        # Use regular signup method instead of admin
        result = service.client.auth.sign_up({
            "email": email,
            "password": password
        })

        if result.user:
            auth_id = result.user.id
            print(f"✅ Created auth account for {email}")
            print(f"   Auth ID: {auth_id}")

            # Update user record with auth_id
            update_result = service.client.table('users').update({
                'auth_id': auth_id
            }).eq('email', email).execute()

            if update_result.data:
                print(f"✅ Updated user record with auth_id")
                return auth_id
            else:
                print(f"❌ Failed to update user record")
                return None
        else:
            print(f"❌ Failed to create auth account")
            print(f"   Error: {result.error if hasattr(result, 'error') else 'Unknown error'}")
            return None

    except Exception as e:
        print(f"❌ Error creating auth account: {e}")
        return None

if __name__ == "__main__":
    email = "lukemoeller@yahoo.com"
    password = "TempPassword123!"  # Temporary password

    print(f"Creating Supabase Auth account for {email}...")
    auth_id = create_auth_for_user(email, password)

    if auth_id:
        print(f"\n🎉 Success!")
        print(f"You can now log in with:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  URL: http://localhost:5173")
        print(f"\nPlease change your password after logging in!")
    else:
        print(f"\n❌ Failed to set up authentication")