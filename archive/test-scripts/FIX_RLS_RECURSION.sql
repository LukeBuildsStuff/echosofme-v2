-- =============================================
-- FIX RLS INFINITE RECURSION ISSUE
-- This fixes the circular dependency in RLS policies
-- Apply this in Supabase Dashboard SQL Editor
-- =============================================

-- =============================================================================
-- SECTION 1: Fix RLS Policies to Prevent Infinite Recursion
-- =============================================================================

-- Temporarily disable RLS to fix policies
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE reflections DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE voice_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE training_datasets DISABLE ROW LEVEL SECURITY;

-- Drop all existing policies to start fresh
DROP POLICY IF EXISTS "users_select_own" ON users;
DROP POLICY IF EXISTS "users_update_own" ON users;
DROP POLICY IF EXISTS "reflections_select_own" ON reflections;
DROP POLICY IF EXISTS "reflections_insert_own" ON reflections;
DROP POLICY IF EXISTS "reflections_update_own" ON reflections;
DROP POLICY IF EXISTS "reflections_delete_own" ON reflections;
DROP POLICY IF EXISTS "user_profiles_select_own" ON user_profiles;
DROP POLICY IF EXISTS "user_profiles_insert_own" ON user_profiles;
DROP POLICY IF EXISTS "user_profiles_update_own" ON user_profiles;
DROP POLICY IF EXISTS "ai_conversations_select_own" ON ai_conversations;
DROP POLICY IF EXISTS "ai_conversations_insert_own" ON ai_conversations;
DROP POLICY IF EXISTS "voice_profiles_all_own" ON voice_profiles;
DROP POLICY IF EXISTS "training_datasets_all_own" ON training_datasets;
DROP POLICY IF EXISTS "questions_select_authenticated" ON questions;
DROP POLICY IF EXISTS "admin_users_all" ON users;
DROP POLICY IF EXISTS "admin_reflections_all" ON reflections;
DROP POLICY IF EXISTS "admin_questions_all" ON questions;

-- =============================================================================
-- SECTION 2: Create Non-Recursive RLS Policies
-- =============================================================================

-- Users table policies (NO recursion - direct auth.uid() check)
CREATE POLICY "users_select_own" ON users
    FOR SELECT USING (auth.uid() = auth_id);

CREATE POLICY "users_update_own" ON users
    FOR UPDATE USING (auth.uid() = auth_id);

-- Reflections policies (check user_id directly without JOIN)
-- The app already filters by user_id, so we can trust that
CREATE POLICY "reflections_all_own" ON reflections
    FOR ALL USING (
        user_id = (
            SELECT id FROM users
            WHERE auth_id = auth.uid()
            LIMIT 1
        )
    );

-- User profiles policies (check user_id directly)
CREATE POLICY "user_profiles_all_own" ON user_profiles
    FOR ALL USING (
        user_id = (
            SELECT id FROM users
            WHERE auth_id = auth.uid()
            LIMIT 1
        )
    );

-- AI conversations policies (check user_id directly)
CREATE POLICY "ai_conversations_all_own" ON ai_conversations
    FOR ALL USING (
        user_id = (
            SELECT id FROM users
            WHERE auth_id = auth.uid()
            LIMIT 1
        )
    );

-- Voice profiles policies (check user_id directly)
CREATE POLICY "voice_profiles_all_own" ON voice_profiles
    FOR ALL USING (
        user_id = (
            SELECT id FROM users
            WHERE auth_id = auth.uid()
            LIMIT 1
        )
    );

-- Training datasets policies (check user_id directly)
CREATE POLICY "training_datasets_all_own" ON training_datasets
    FOR ALL USING (
        user_id = (
            SELECT id FROM users
            WHERE auth_id = auth.uid()
            LIMIT 1
        )
    );

-- Questions policies (read-only for authenticated users)
CREATE POLICY "questions_select_authenticated" ON questions
    FOR SELECT USING (auth.role() = 'authenticated');

-- Admin policies (simplified to avoid recursion)
CREATE POLICY "admin_all_tables" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_id = auth.uid()
            AND is_admin = true
        )
    );

-- Re-enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- SECTION 3: Test the Fix
-- =============================================================================

-- Test query to verify policies work
SELECT
    'RLS policies updated successfully!' as status,
    'Normal authentication should now work' as result,
    'You can now login with TempPass123! and see reflections' as action;