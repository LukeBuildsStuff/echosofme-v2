-- Fix the auth trigger to handle existing users properly
-- This will allow proper Supabase Auth account creation for existing users

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