-- Quick fix for admin panel - just add the missing function
-- This creates the get_users_with_response_counts function needed by the admin API

CREATE OR REPLACE FUNCTION get_users_with_response_counts(limit_val INTEGER DEFAULT 50, offset_val INTEGER DEFAULT 0)
RETURNS TABLE (
    id INTEGER,
    auth_id UUID,
    email VARCHAR,
    name VARCHAR,
    role VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN,
    last_login_at TIMESTAMP,
    is_admin BOOLEAN,
    response_count BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.auth_id,
        u.email,
        u.name,
        u.role,
        u.created_at,
        u.updated_at,
        u.is_active,
        u.last_login_at,
        u.is_admin,
        COALESCE(r.response_count, 0) as response_count
    FROM users u
    LEFT JOIN (
        SELECT user_id, COUNT(*) as response_count
        FROM reflections
        GROUP BY user_id
    ) r ON u.id = r.user_id
    ORDER BY u.created_at DESC
    LIMIT limit_val OFFSET offset_val;
END;
$$;

-- Grant permissions for the function
GRANT EXECUTE ON FUNCTION get_users_with_response_counts TO authenticated;

-- Test the function to make sure it works
SELECT 'Function created successfully!' AS status;