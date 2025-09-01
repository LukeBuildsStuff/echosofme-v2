import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  displayName: string;
  profile: {
    displayName: string;
    relationship: string;
    meetingStatus: string;
    purpose: string;
    knowledgeLevel: string;
    introduction: string;
  };
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  clearAllUserData: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication on app load
    const checkAuth = () => {
      try {
        const auth = localStorage.getItem('echos_authenticated');
        const userProfile = localStorage.getItem('echos_user_profile');
        
        if (auth === 'true' && userProfile) {
          const userData = JSON.parse(userProfile);
          setUser(userData);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        // Clear corrupted auth data
        localStorage.removeItem('echos_authenticated');
        localStorage.removeItem('echos_user_profile');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = (userData: User) => {
    try {
      console.log('🔍 AUTH - Login called with displayName:', userData.displayName);
      
      // Login.tsx now provides the correct user data, so we can use it directly
      localStorage.setItem('echos_authenticated', 'true');
      localStorage.setItem('echos_user_profile', JSON.stringify(userData)); // Current user (for checkAuth)
      
      // Save to user-specific key for persistence across sessions
      // Normalize email to ensure consistent key usage
      const normalizedEmail = userData.email.toLowerCase().trim();
      const userSpecificKey = `echos_user_profile_${normalizedEmail}`;
      
      // Trust Login.tsx - it already loaded the correct saved profile
      localStorage.setItem(userSpecificKey, JSON.stringify(userData));
      console.log('🔍 AUTH - Saved to key:', userSpecificKey, 'displayName:', userData.displayName);
      
      localStorage.setItem('echos_current_user', userData.id);
      
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Error during login:', error);
      throw new Error('Failed to save authentication data');
    }
  };

  const logout = () => {
    try {
      // Clear ONLY session data on logout (preserve user preferences/profile)
      localStorage.removeItem('echos_authenticated');
      localStorage.removeItem('echos_user_profile'); // Current session profile
      localStorage.removeItem('echos_current_user');
      
      // User-specific data remains for next login: echos_user_profile_${email}
      console.log('🔍 LOGOUT - Session cleared, user data preserved for next login');
      
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  const clearAllUserData = () => {
    if (!user?.email) return;
    
    const confirmClear = window.confirm(
      'Are you sure you want to permanently delete ALL your data? This includes:\n' +
      '• Your profile and settings\n' +
      '• All reflections and memories\n' +
      '• Chat history\n' +
      '• All other saved data\n\n' +
      'This action cannot be undone!'
    );
    
    if (confirmClear) {
      try {
        // Clear ALL user data
        localStorage.removeItem('echos_user_profile');
        localStorage.removeItem('echos_user_settings');
        localStorage.removeItem('echos_reflections');
        localStorage.removeItem('echos_chat_sessions');
        localStorage.removeItem('echos_chat_messages');
        localStorage.removeItem('echos_memories');
        localStorage.removeItem('echos_insights');
        
        // Remove user-specific profile
        const normalizedEmail = user.email.toLowerCase().trim();
        const userSpecificKey = `echos_user_profile_${normalizedEmail}`;
        localStorage.removeItem(userSpecificKey);
        
        console.log('🔍 CLEAR DATA - All user data deleted');
        
        // Also log them out since their profile is gone
        logout();
        
        return true; // Success
      } catch (error) {
        console.error('Error clearing user data:', error);
        return false;
      }
    }
    
    return false; // User cancelled
  };

  const updateUser = (userData: Partial<User>) => {
    if (!user) return;
    
    try {
      // Deep merge for profile to prevent losing nested fields
      const updatedUser = {
        ...user,
        ...userData,
        profile: userData.profile ? {
          ...user.profile,      // Keep existing profile fields
          ...userData.profile   // Merge new profile fields
        } : user.profile       // Keep existing if no profile update
      };
      
      console.log('🔍 UPDATE - Saving user with displayName:', updatedUser.displayName);
      
      // Save to both global key (for checkAuth) and user-specific key (for persistence)
      localStorage.setItem('echos_user_profile', JSON.stringify(updatedUser));
      if (updatedUser.email) {
        // Normalize email for consistent key usage
        const normalizedEmail = updatedUser.email.toLowerCase().trim();
        const userSpecificKey = `echos_user_profile_${normalizedEmail}`;
        localStorage.setItem(userSpecificKey, JSON.stringify(updatedUser));
        console.log('🔍 UPDATE - Saved to key:', userSpecificKey);
      }
      
      setUser(updatedUser);
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const value = {
    isAuthenticated,
    user,
    login,
    logout,
    updateUser,
    clearAllUserData,
  };

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
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