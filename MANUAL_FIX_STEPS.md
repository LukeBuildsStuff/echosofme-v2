# Manual Steps to Complete Authentication Fix

## Current Status: ✅ Dev Mode Working
You can now log in with:
- **Email**: lukemoeller@yahoo.com
- **Password**: Luke19841984!
- **Dev mode expires**: 2025-09-18

## Step 1: Apply Database Fixes in Supabase Dashboard

### 1.1 Open Supabase SQL Editor
- Go to: https://supabase.com/dashboard/project/cbaudsvlidzfxvmzdvcg/sql
- Click "SQL Editor" in left sidebar
- Click "New query"

### 1.2 Execute the Fix Script
- Open file: `COMPREHENSIVE_DATABASE_FIX.sql`
- Copy entire contents
- Paste into SQL Editor
- Click "Run" to execute

### 1.3 Verify Success
Look for these messages in the output:
```
✅ Database fixes applied successfully!
Next steps: 1. Create Supabase Auth account via dashboard or API
```

## Step 2: Create Proper Supabase Auth Account

### Option A: Via Supabase Dashboard
1. Go to: https://supabase.com/dashboard/project/cbaudsvlidzfxvmzdvcg/auth/users
2. Click "Invite user" or "Add user"
3. Enter:
   - Email: lukemoeller@yahoo.com
   - Password: [choose new secure password]
4. The trigger will automatically link to existing user record

### Option B: Via Application (Recommended)
1. Go to your app signup page
2. Register with lukemoeller@yahoo.com
3. The improved trigger will handle the email conflict gracefully

## Step 3: Test Normal Authentication

### 3.1 Test Login Flow
1. Clear browser cache/localStorage
2. Try logging in with lukemoeller@yahoo.com and new password
3. Should work without dev mode bypass

### 3.2 Verify Database Connection
- Check that user data loads correctly
- Verify reflections and questions display
- Test creating new reflections

## Step 4: Remove Dev Mode (After Testing)

### 4.1 Update Environment Variables
In `.env` file, change:
```env
VITE_DEV_MODE_ENABLED=false
# or remove these lines entirely:
# VITE_DEV_MODE_PASSWORD=Luke19841984!
# VITE_DEV_MODE_EXPIRES=2025-09-18
# VITE_SUPABASE_SERVICE_KEY_DEV=[service_key]
```

### 4.2 Test Final State
- Restart the application
- Verify normal login still works
- Confirm dev mode bypass is disabled

## Troubleshooting

### If Database Fixes Fail:
1. Check for syntax errors in SQL output
2. Ensure you have admin privileges
3. Try running sections individually if needed

### If Auth Account Creation Fails:
1. Check the trigger was created successfully
2. Verify RLS policies are not blocking
3. Check auth.users table for existing records

### If Normal Login Still Fails:
1. Check browser console for errors
2. Verify auth_id was properly set in users table
3. Test with a completely new user account first

## Files Modified in This Fix:
- `.env` - Added dev mode configuration
- `src/lib/supabase.ts` - Added conditional admin client
- `src/contexts/SupabaseAuthContext.tsx` - Added dev mode bypass
- `src/contexts/EchoContext.tsx` - Added admin client usage
- `COMPREHENSIVE_DATABASE_FIX.sql` - Database fix script

## Security Notes:
- Dev mode is time-limited (expires 2025-09-18)
- Service key only used in secure dev context
- Remove dev mode after permanent fix is applied
- Never commit service keys to version control

## Support:
If you encounter issues, the dev mode bypass will continue working until 2025-09-18, giving you time to troubleshoot the permanent fix.