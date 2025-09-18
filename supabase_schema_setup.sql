-- Supabase Schema Setup for Echoes of Me
-- This script creates the modified schema for Supabase with Row Level Security

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the modified users table
-- Note: Supabase handles auth.users separately, this is our application users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    role VARCHAR DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    secondary_roles TEXT[],
    image TEXT,
    reset_token VARCHAR,
    cultural_background TEXT[],
    primary_role VARCHAR,
    email_verified TIMESTAMP,
    crisis_contact_info JSONB,
    grief_support_opt_in BOOLEAN DEFAULT false,
    memorial_account BOOLEAN DEFAULT false,
    memorial_contact_id INTEGER,
    is_admin BOOLEAN DEFAULT false,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    reset_token_expires TIMESTAMP,
    important_people JSONB,
    birthday DATE,
    significant_events JSONB,
    admin_role_id UUID,
    last_shadow_session TIMESTAMP,
    privacy_preferences JSONB
);

-- Create questions table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    category VARCHAR NOT NULL DEFAULT 'general',
    subcategory VARCHAR,
    difficulty_level INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    tags TEXT[],
    context_info JSONB,
    follow_up_prompts TEXT[],
    estimated_time_minutes INTEGER,
    requires_preparation BOOLEAN DEFAULT false,
    emotional_intensity INTEGER DEFAULT 1,
    age_appropriateness VARCHAR,
    cultural_sensitivity TEXT[],
    therapeutic_value INTEGER DEFAULT 1,
    memory_type VARCHAR,
    recommended_frequency VARCHAR
);

-- Create reflections table
CREATE TABLE IF NOT EXISTS reflections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    response_text TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    is_draft BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    response_type VARCHAR DEFAULT 'reflection',
    emotional_tags TEXT[],
    privacy_level VARCHAR DEFAULT 'private',
    voice_notes JSONB,
    shared_with INTEGER[],
    revision_count INTEGER DEFAULT 0,
    original_response_id INTEGER REFERENCES reflections(id),
    ai_analysis JSONB,
    sentiment_score NUMERIC(3,2),
    themes TEXT[],
    follow_up_questions TEXT[],
    memory_strength INTEGER DEFAULT 1,
    context_tags TEXT[]
);

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    display_name VARCHAR,
    relationship VARCHAR,
    meeting_status VARCHAR,
    introduction TEXT,
    voice_id VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    avatar_url TEXT,
    bio TEXT,
    interests TEXT[],
    goals TEXT[],
    reflection_preferences JSONB,
    notification_settings JSONB,
    privacy_settings JSONB,
    cultural_preferences JSONB,
    accessibility_settings JSONB,
    time_zone VARCHAR,
    preferred_language VARCHAR DEFAULT 'en'
);

-- Create ai_conversations table
CREATE TABLE IF NOT EXISTS ai_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    conversation_type VARCHAR DEFAULT 'echo',
    model_version VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    response_time_ms INTEGER,
    tokens_used INTEGER,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    context_data JSONB,
    follow_up_suggestions TEXT[],
    emotional_tone VARCHAR,
    conversation_thread_id UUID DEFAULT uuid_generate_v4()
);

-- Create voice_profiles table
CREATE TABLE IF NOT EXISTS voice_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    voice_id VARCHAR NOT NULL,
    voice_name VARCHAR,
    provider VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    voice_settings JSONB,
    sample_audio_url TEXT,
    clone_quality_score NUMERIC(3,2),
    training_status VARCHAR DEFAULT 'pending',
    training_data_url TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP
);

-- Create training_datasets table
CREATE TABLE IF NOT EXISTS training_datasets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dataset_name VARCHAR NOT NULL,
    dataset_type VARCHAR NOT NULL,
    file_path TEXT,
    file_size_mb NUMERIC(10,2),
    record_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    processing_status VARCHAR DEFAULT 'pending',
    quality_score NUMERIC(3,2),
    metadata JSONB,
    is_active BOOLEAN DEFAULT true,
    export_format VARCHAR,
    compression_ratio NUMERIC(4,2),
    validation_results JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_auth_id ON users(auth_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_reflections_user_id ON reflections(user_id);
CREATE INDEX IF NOT EXISTS idx_reflections_question_id ON reflections(question_id);
CREATE INDEX IF NOT EXISTS idx_reflections_created_at ON reflections(created_at);
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_is_active ON questions(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_thread ON ai_conversations(conversation_thread_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reflections_updated_at BEFORE UPDATE ON reflections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voice_profiles_updated_at BEFORE UPDATE ON voice_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_training_datasets_updated_at BEFORE UPDATE ON training_datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_datasets ENABLE ROW LEVEL SECURITY;

-- Questions table can be read by all authenticated users (no RLS needed for reads)
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies

-- Users table policies
CREATE POLICY "Users can view own record" ON users
    FOR SELECT USING (auth.uid() = auth_id);

CREATE POLICY "Users can update own record" ON users
    FOR UPDATE USING (auth.uid() = auth_id);

-- Reflections policies
CREATE POLICY "Users can view own reflections" ON reflections
    FOR SELECT USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can insert own reflections" ON reflections
    FOR INSERT WITH CHECK (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can update own reflections" ON reflections
    FOR UPDATE USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can delete own reflections" ON reflections
    FOR DELETE USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

-- User profiles policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

-- AI conversations policies
CREATE POLICY "Users can view own conversations" ON ai_conversations
    FOR SELECT USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can insert own conversations" ON ai_conversations
    FOR INSERT WITH CHECK (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

-- Voice profiles policies
CREATE POLICY "Users can view own voice profiles" ON voice_profiles
    FOR SELECT USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can manage own voice profiles" ON voice_profiles
    FOR ALL USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

-- Training datasets policies
CREATE POLICY "Users can view own training datasets" ON training_datasets
    FOR SELECT USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

CREATE POLICY "Users can manage own training datasets" ON training_datasets
    FOR ALL USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));

-- Questions policies (read-only for authenticated users)
CREATE POLICY "Authenticated users can read questions" ON questions
    FOR SELECT USING (auth.role() = 'authenticated');

-- Admin policies (users with is_admin = true can access everything)
CREATE POLICY "Admins can do everything on users" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_id = auth.uid() AND is_admin = true
        )
    );

CREATE POLICY "Admins can do everything on reflections" ON reflections
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_id = auth.uid() AND is_admin = true
        )
    );

CREATE POLICY "Admins can manage questions" ON questions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_id = auth.uid() AND is_admin = true
        )
    );

-- Create a function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    INSERT INTO public.users (auth_id, email, name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
    )
    ON CONFLICT (email) DO UPDATE SET
        auth_id = NEW.id,
        name = COALESCE(NEW.raw_user_meta_data->>'full_name', users.name),
        updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Create trigger for new user creation
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create a function to get user stats (for dashboard)
CREATE OR REPLACE FUNCTION get_user_stats(user_auth_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result JSON;
    user_internal_id INTEGER;
BEGIN
    -- Get internal user ID
    SELECT id INTO user_internal_id FROM users WHERE auth_id = user_auth_id;

    IF user_internal_id IS NULL THEN
        RETURN '{"error": "User not found"}'::json;
    END IF;

    -- Calculate stats
    SELECT json_build_object(
        'total_reflections', (SELECT COUNT(*) FROM reflections WHERE user_id = user_internal_id),
        'total_words', (SELECT COALESCE(SUM(word_count), 0) FROM reflections WHERE user_id = user_internal_id),
        'categories_covered', (
            SELECT COUNT(DISTINCT q.category)
            FROM reflections r
            JOIN questions q ON r.question_id = q.id
            WHERE r.user_id = user_internal_id
        ),
        'weekly_reflections', (
            SELECT COUNT(*)
            FROM reflections
            WHERE user_id = user_internal_id
            AND created_at >= NOW() - INTERVAL '7 days'
        ),
        'last_reflection', (
            SELECT MAX(created_at)
            FROM reflections
            WHERE user_id = user_internal_id
        )
    ) INTO result;

    RETURN result;
END;
$$;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Comments for documentation
COMMENT ON TABLE users IS 'Application users linked to Supabase auth.users';
COMMENT ON TABLE reflections IS 'User responses to questions with metadata';
COMMENT ON TABLE questions IS 'Question bank for reflections';
COMMENT ON TABLE user_profiles IS 'Extended user profile information';
COMMENT ON TABLE ai_conversations IS 'Chat history with AI assistants';
COMMENT ON TABLE voice_profiles IS 'Voice cloning profiles for users';
COMMENT ON TABLE training_datasets IS 'AI training datasets generated from user data';

COMMENT ON COLUMN users.auth_id IS 'References auth.users(id) for Supabase authentication';
COMMENT ON COLUMN reflections.privacy_level IS 'private, shared, or public';
COMMENT ON COLUMN questions.difficulty_level IS '1=easy, 2=medium, 3=hard, 4=expert';
COMMENT ON COLUMN questions.emotional_intensity IS '1=light, 2=medium, 3=deep, 4=intense';

-- Completion message
SELECT 'Supabase schema setup completed successfully! 🎉' AS status;