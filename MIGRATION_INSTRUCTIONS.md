# 🚀 Echoes of Me - Supabase Migration Instructions

## Overview

This document provides step-by-step instructions to complete the migration from local PostgreSQL + localStorage authentication to Supabase. All the code has been prepared - you just need to follow these steps to complete the migration.

## 📋 What's Been Done

✅ **Code Preparation Complete:**
- Supabase Python client installed and configured
- Supabase JavaScript client installed and configured
- New `SupabaseAuthContext` created for authentication
- New `supabase_api.py` backend with Supabase integration
- Database schema prepared for Supabase with RLS
- Data migration scripts created
- Verification and export scripts ready
- Environment configuration templates created

## 🎯 Next Steps (Manual Actions Required)

### Step 1: Create Supabase Projects

1. **Go to [supabase.com](https://supabase.com)** and sign up/login
2. **Create Development Project:**
   - Click "New Project"
   - Name: `echosofme-dev`
   - Database Password: Save securely!
   - Region: `us-east-1` (or closest to you)
3. **Create Production Project:**
   - Click "New Project"
   - Name: `echosofme-prod`
   - Database Password: Save securely!
   - Region: `us-east-1`

### Step 2: Set Up Environment Variables

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your Supabase credentials:**
   ```bash
   # From Supabase Dashboard → Settings → API
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_KEY=eyxxxxx_your_service_key_here
   VITE_SUPABASE_URL=https://xxxxx.supabase.co
   VITE_SUPABASE_ANON_KEY=eyxxxxx_your_anon_key_here

   # Keep existing settings
   VITE_ELEANOR_API_URL=http://localhost:8001
   VITE_ELEVENLABS_API_KEY=sk_8d0ee2601bd93668e845171f52b4b0e3e0069fe0cc226bc9
   VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   VITE_ENABLE_PROFILE_SYNC=true
   ```

### Step 3: Set Up Supabase Schema

1. **Go to Supabase Dashboard** → SQL Editor
2. **Run the schema setup script:**
   - Copy contents of `supabase_schema_setup.sql`
   - Paste in SQL Editor and run
   - This creates all tables with proper RLS policies

### Step 4: Verify Current Database

1. **Run verification script:**
   ```bash
   python3 verify_migration.py
   ```
   - This documents current database state
   - Make sure Docker PostgreSQL is running

### Step 5: Export Current Database

1. **Run export script:**
   ```bash
   python3 export_database.py
   ```
   - Creates timestamped backup directory
   - Exports schema, data, and full backup

### Step 6: Migrate Data to Supabase

1. **Run migration script:**
   ```bash
   python3 migrate_data_to_supabase.py
   ```
   - Migrates all data from local PostgreSQL to Supabase
   - Includes verification at the end

### Step 7: Update Frontend to Use Supabase

1. **Update App.tsx to use new AuthContext:**
   ```typescript
   // Replace this line:
   import { AuthProvider } from './contexts/AuthContext';

   // With this:
   import { AuthProvider } from './contexts/SupabaseAuthContext';
   ```

2. **Update components that use API:**
   - Most components should work as-is
   - The new `ApiService` maintains backward compatibility
   - Test dashboard, reflections, and profile pages

### Step 8: Start New Backend

1. **Stop old backend** (if running)
2. **Start Supabase backend:**
   ```bash
   python3 supabase_api.py
   ```
   - Runs on port 8001 (different from old API)

3. **Update frontend API URL:**
   ```bash
   # In .env
   VITE_ELEANOR_API_URL=http://localhost:8001
   ```

### Step 9: Test Authentication

1. **Start frontend:**
   ```bash
   npm run dev
   ```

2. **Test authentication flows:**
   - Sign up with new email/password
   - Sign in with existing credentials (after user migration)
   - Google OAuth (if configured)
   - Password reset flow

### Step 10: Migrate Existing Users

1. **Run user migration script:**
   ```bash
   python3 migrate_users_auth.py
   ```
   - Creates Supabase auth accounts for existing users
   - Sends password reset emails

2. **Manual step: Configure Google OAuth** (if using):
   - Go to Supabase Dashboard → Authentication → Settings
   - Add Google OAuth provider
   - Update `VITE_GOOGLE_CLIENT_ID` in `.env`

### Step 11: Deployment

1. **Deploy to Vercel/Netlify:**
   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Deploy
   vercel
   ```

2. **Set production environment variables** in Vercel dashboard:
   - `VITE_SUPABASE_URL` (production project URL)
   - `VITE_SUPABASE_ANON_KEY` (production anon key)
   - Other environment variables as needed

### Step 12: Final Verification

1. **Run verification script against Supabase:**
   ```bash
   python3 verify_migration_complete.py
   ```

2. **Manual testing checklist:**
   - [ ] User signup works
   - [ ] User login works
   - [ ] Dashboard loads with user data
   - [ ] Can create reflections
   - [ ] Can edit reflections
   - [ ] Can delete reflections
   - [ ] Profile updates work
   - [ ] Eleanor chat works (if configured)
   - [ ] Mobile responsiveness

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check Docker PostgreSQL is running
docker ps | grep postgres

# Test local database connection
python3 verify_migration.py
```

### Supabase Connection Issues
```bash
# Verify environment variables
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_KEY

# Test Supabase connection
python3 -c "from src.services.supabase_service import get_supabase_service; print(get_supabase_service().health_check())"
```

### Frontend Issues
```bash
# Check environment variables in browser console
console.log(import.meta.env.VITE_SUPABASE_URL)

# Clear browser cache and localStorage
localStorage.clear()
```

### Migration Issues
- Check Supabase logs in dashboard
- Verify RLS policies are not blocking data access
- Ensure auth_id is properly linked for existing users

## 📁 File Overview

### New Files Created:
- `verify_migration.py` - Pre-migration verification
- `export_database.py` - Database export utility
- `migrate_data_to_supabase.py` - Data migration script
- `supabase_schema_setup.sql` - Supabase schema with RLS
- `supabase_api.py` - New Supabase-powered backend
- `src/lib/supabase.ts` - Supabase client configuration
- `src/contexts/SupabaseAuthContext.tsx` - New auth context
- `src/services/api.ts` - Backward-compatible API service
- `src/services/supabase_service.py` - Backend Supabase service
- `.env.example` - Environment configuration template

### Modified Files:
- `package.json` - Added Supabase JS client

### Files to Update (Manual):
- `src/App.tsx` - Switch to SupabaseAuthContext
- `.env` - Add Supabase credentials

## 🎉 Benefits After Migration

### Immediate Benefits:
- ✅ **Secure authentication** - Proper password hashing and validation
- ✅ **JWT session management** - Secure, stateless authentication
- ✅ **OAuth integration** - Google login works seamlessly
- ✅ **Row-level security** - Users can only access their own data
- ✅ **Auto-scaling** - Database and APIs scale automatically

### Development Benefits:
- ✅ **Real-time features** - Built-in real-time subscriptions
- ✅ **Automatic APIs** - REST endpoints auto-generated
- ✅ **Type safety** - Generated TypeScript types
- ✅ **Better testing** - Separate dev/prod environments

### Future Capabilities:
- ✅ **iOS app ready** - Same backend for mobile
- ✅ **File storage** - For voice recordings, images
- ✅ **Advanced analytics** - User behavior insights
- ✅ **Email notifications** - Automated reminders

## 🚨 Important Notes

1. **Keep old system running** during migration as backup
2. **Test thoroughly** before switching users over
3. **Have rollback plan** ready (database backups created)
4. **Existing users need to reset passwords** after auth migration
5. **Eleanor LLM integration** may need adjustment for new API

## 🆘 Need Help?

- Check Supabase documentation: https://supabase.com/docs
- Join Supabase Discord: https://discord.supabase.com
- Review migration logs for specific error messages
- Verify environment variables are set correctly

## ✅ Migration Checklist

### Pre-Migration:
- [ ] Supabase projects created (dev & prod)
- [ ] Environment variables configured
- [ ] Current database verified and exported
- [ ] Supabase schema set up with RLS

### Migration:
- [ ] Data migrated to Supabase
- [ ] Migration verified (data counts match)
- [ ] Frontend updated to use Supabase
- [ ] New backend started and tested

### Post-Migration:
- [ ] Authentication flows tested
- [ ] Existing users migrated
- [ ] Production deployment completed
- [ ] All functionality verified working

### Cleanup:
- [ ] Old API server stopped
- [ ] Local PostgreSQL no longer needed
- [ ] Old authentication code removed
- [ ] Documentation updated

---

**Migration Status: Ready to Execute**
All code has been prepared. Follow the steps above to complete the migration to Supabase! 🚀