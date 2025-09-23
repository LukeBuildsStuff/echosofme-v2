import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { supabase, api } from '../lib/supabase';
import type { User as SupabaseUser, Session } from '@supabase/supabase-js';

interface User {
  id: string;
  email: string;
  displayName: string; // Keep at root level for backward compatibility
  provider?: 'email' | 'google';
  isAdmin?: boolean;
  profile: {
    displayName: string; // Also in profile for database sync
    relationship: string;
    meetingStatus: string;
    purpose: string;
    knowledgeLevel: string;
    introduction: string;
    voiceId?: string;
  };
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  session: Session | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, displayName: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (profileData: Partial<User['profile']>) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updatePassword: (newPassword: string) => Promise<void>;
  verifyPasswordReset: (accessToken: string, refreshToken: string) => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);


export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!session;

  // Admin email constant
  const ADMIN_EMAIL = 'lukemoeller@yahoo.com';

  // Helper function to check if user is admin
  const checkIsAdmin = (email: string): boolean => {
    return email.toLowerCase().trim() === ADMIN_EMAIL.toLowerCase();
  };

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        loadUserProfile(session.user);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔐 Auth state change:', event, session?.user?.email);

      setSession(session);

      if (session) {
        await loadUserProfile(session.user);
      } else {
        setUser(null);
      }

      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const loadUserProfile = async (authUser: SupabaseUser) => {
    try {
      // Get user record from our users table
      const userData = await api.getCurrentUser();

      if (!userData) {
        console.warn('No user record found for authenticated user');
        // Create user record if it doesn't exist
        console.log('🔄 Creating new user record for:', authUser.email);
        const newUser = await api.createUserRecord(
          authUser.id,
          authUser.email!,
          authUser.user_metadata?.full_name || authUser.email!.split('@')[0]
        );

        if (newUser.error) {
          console.error('❌ Failed to create user record:', newUser.error);
          throw new Error('Failed to create user record: ' + newUser.error.message);
        }

        if (newUser.data) {
          console.log('✅ Created user record with ID:', newUser.data.id);
          await loadUserWithProfile(newUser.data);
        } else {
          throw new Error('User record creation returned no data');
        }
        return;
      }

      await loadUserWithProfile(userData);
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
  };

  const loadUserWithProfile = async (userData: any) => {
    try {
      // Get additional profile data from user_profiles table
      let profileData = null;
      try {
        // Use api helper to get profile data
        const result = await api.getUserProfile();
        profileData = result?.data;
      } catch (profileError) {
        console.warn('Profile data not found, using defaults:', profileError);
      }

      // Ensure we have a valid user ID before creating the user object
      if (!userData.id) {
        console.error('❌ User data missing ID, cannot create user object');
        throw new Error('User data is incomplete - missing ID');
      }

      const user: User = {
        id: userData.id.toString(),
        email: userData.email,
        displayName: userData.name || userData.email.split('@')[0],
        provider: 'email', // TODO: Detect provider from auth metadata
        isAdmin: checkIsAdmin(userData.email),
        profile: {
          displayName: profileData?.display_name || userData.name || '',
          relationship: profileData?.relationship || 'Friendly',
          meetingStatus: profileData?.meeting_status || 'First time meeting',
          purpose: 'Personal growth and reflection',
          knowledgeLevel: 'Learning together',
          introduction: profileData?.introduction || '',
          voiceId: profileData?.voice_id,
        }
      };

      setUser(user);
      console.log('✅ User profile loaded:', {
        displayName: user.displayName,
        introduction: user.profile.introduction,
        id: user.id
      });
    } catch (error) {
      console.error('Error loading user with profile:', error);
    }
  };

  const login = async (email: string, password: string) => {
    const { error } = await api.signIn(email, password);

    if (error) {
      throw new Error(error.message);
    }
    // User state will be updated via onAuthStateChange
  };

  const signup = async (email: string, password: string, displayName: string) => {
    const { data, error } = await api.signUp(email, password);

    if (error) {
      throw new Error(error.message);
    }

    if (data.user) {
      // Create user record in our users table
      try {
        await api.createUserRecord(data.user.id, data.user.email!, displayName);
      } catch (userError) {
        console.error('Error creating user record:', userError);
        // Auth user is created but user record failed - they can still log in later
      }
    }
  };

  const loginWithGoogle = async () => {
    const { error } = await api.signInWithGoogle();

    if (error) {
      throw new Error(error.message);
    }
    // Redirect will happen automatically
  };

  const logout = async () => {
    const { error } = await api.signOut();
    if (error) {
      console.error('Error logging out:', error);
    }
    // User state will be cleared via onAuthStateChange
  };

  const updateProfile = async (profileData: Partial<User['profile']>) => {
    if (!user) {
      throw new Error('No user logged in');
    }

    try {
      console.log('🔄 Updating profile with data:', profileData);

      // Transform field names for database (camelCase to snake_case)
      const dbProfileData: any = {};

      // Handle displayName mapping
      if (profileData.displayName !== undefined) {
        dbProfileData.display_name = profileData.displayName;
      }

      // Handle introduction field
      if (profileData.introduction !== undefined) {
        dbProfileData.introduction = profileData.introduction;
      }

      // Handle other profile fields
      if (profileData.relationship !== undefined) {
        dbProfileData.relationship = profileData.relationship;
      }
      if (profileData.meetingStatus !== undefined) {
        dbProfileData.meeting_status = profileData.meetingStatus;
      }
      if (profileData.voiceId !== undefined) {
        dbProfileData.voice_id = profileData.voiceId;
      }

      console.log('🔧 Transformed data for database:', dbProfileData);

      // Update user_profiles table
      const { data } = await api.updateUserProfile(dbProfileData);

      if (data) {
        console.log('📦 Database save response:', data);

        // CRITICAL: Reload the complete profile from database to verify what was actually saved
        console.log('🔄 Reloading profile from database to verify save...');

        // Get fresh user data and reload profile
        const freshUserData = await api.getCurrentUser();
        if (freshUserData) {
          await loadUserWithProfile(freshUserData);
          console.log('✅ Profile updated and reloaded from database');
        } else {
          console.error('❌ Failed to reload user data after profile update');
        }
      }
    } catch (error) {
      console.error('❌ Profile update failed:', error);
      throw error;
    }
  };

  const resetPassword = async (email: string) => {
    const { error } = await api.resetPasswordForEmail(email);

    if (error) {
      throw new Error(error.message);
    }
    // Email sent successfully
  };

  const updatePassword = async (newPassword: string) => {
    const { error } = await api.updatePassword(newPassword);

    if (error) {
      throw new Error(error.message);
    }
    // Password updated successfully
  };

  const verifyPasswordReset = async (accessToken: string, refreshToken: string) => {
    const { error } = await api.verifyPasswordResetToken(accessToken, refreshToken);

    if (error) {
      throw new Error(error.message);
    }
    // Session updated - user is now logged in and can update password
  };

  const value = {
    isAuthenticated,
    user,
    session,
    login,
    signup,
    loginWithGoogle,
    logout,
    updateProfile,
    resetPassword,
    updatePassword,
    verifyPasswordReset,
    loading,
  };

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;