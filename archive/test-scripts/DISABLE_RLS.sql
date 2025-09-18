-- =============================================
-- TEMPORARILY DISABLE RLS TO FIX AUTHENTICATION
-- This will allow the app to work while we redesign RLS policies
-- Apply this in Supabase Dashboard SQL Editor
-- =============================================

-- Disable RLS on all tables
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE reflections DISABLE ROW LEVEL SECURITY;
ALTER TABLE questions DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE voice_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE training_datasets DISABLE ROW LEVEL SECURITY;

-- Verify RLS is disabled
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('users', 'reflections', 'questions', 'user_profiles', 'ai_conversations', 'voice_profiles', 'training_datasets');

-- Expected result: All tables should show rowsecurity = false
--
-- IMPORTANT: This temporarily removes security restrictions.
-- Only use this for development/testing.
-- Re-enable RLS with proper policies before production!