-- Settings Database Diagnostic Queries
-- Use these in your Supabase SQL editor or psql to debug settings issues

-- 1. Check if user exists and has profile
-- Replace 'user@example.com' with actual email
SELECT
    u.id as user_id,
    u.email,
    u.auth_id,
    up.id as profile_id,
    up.reflection_preferences,
    up.notification_settings,
    up.created_at as profile_created,
    up.updated_at as profile_updated
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.email = 'user@example.com';

-- 2. Check all users with their settings (for debugging)
SELECT
    u.id,
    u.email,
    up.reflection_preferences,
    up.notification_settings
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
ORDER BY u.created_at DESC
LIMIT 10;

-- 3. Check for users without profiles (should be none after our fix)
SELECT u.id, u.email, u.created_at
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE up.id IS NULL;

-- 4. Check for profiles with empty/null settings
SELECT
    up.id,
    up.user_id,
    u.email,
    up.reflection_preferences,
    up.notification_settings,
    CASE
        WHEN up.reflection_preferences = '{}' THEN 'EMPTY'
        WHEN up.reflection_preferences IS NULL THEN 'NULL'
        ELSE 'HAS_DATA'
    END as reflection_status,
    CASE
        WHEN up.notification_settings = '{}' THEN 'EMPTY'
        WHEN up.notification_settings IS NULL THEN 'NULL'
        ELSE 'HAS_DATA'
    END as notification_status
FROM user_profiles up
JOIN users u ON up.user_id = u.id
ORDER BY up.updated_at DESC;

-- 5. Migration check: Find profiles that still use old split format
SELECT
    up.id,
    up.user_id,
    u.email,
    jsonb_object_keys(up.reflection_preferences) as reflection_keys,
    jsonb_object_keys(up.notification_settings) as notification_keys
FROM user_profiles up
JOIN users u ON up.user_id = u.id
WHERE up.notification_settings != '{}'
   OR (up.reflection_preferences != '{}' AND up.notification_settings != '{}');

-- 6. Check for specific user settings (replace user_id with actual ID)
SELECT
    reflection_preferences,
    notification_settings,
    reflection_preferences->'theme' as theme_setting,
    reflection_preferences->'dailyReminders' as daily_reminders,
    updated_at
FROM user_profiles
WHERE user_id = 1; -- Replace with actual user ID

-- 7. Check data types and constraints
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
  AND column_name IN ('reflection_preferences', 'notification_settings', 'user_id');

-- 8. Check foreign key relationships
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'user_profiles';

-- 9. Recent settings updates (last 24 hours)
SELECT
    up.user_id,
    u.email,
    up.reflection_preferences,
    up.updated_at
FROM user_profiles up
JOIN users u ON up.user_id = u.id
WHERE up.updated_at > NOW() - INTERVAL '24 hours'
ORDER BY up.updated_at DESC;

-- 10. Test query: Create sample settings to test format
-- (Uncomment and modify as needed for testing)
/*
UPDATE user_profiles
SET reflection_preferences = '{
    "theme": "dark",
    "dailyReminders": true,
    "reminderTime": "20:00",
    "streakNotifications": true,
    "emailUpdates": true,
    "eleanorInitiates": true
}'::jsonb,
notification_settings = '{}'::jsonb
WHERE user_id = 1; -- Replace with your user ID
*/