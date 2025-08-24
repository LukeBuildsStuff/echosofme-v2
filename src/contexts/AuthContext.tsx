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
          
          // Also check for user-specific profile for better persistence
          const userSpecificKey = `echos_user_profile_${userData.email}`;
          const savedProfile = localStorage.getItem(userSpecificKey);
          
          if (savedProfile) {
            try {
              const parsedSavedProfile = JSON.parse(savedProfile);
              // Deep merge with user-specific saved data
              const mergedData = {
                ...userData,
                ...parsedSavedProfile,
                profile: {
                  ...userData.profile,
                  ...parsedSavedProfile.profile,
                },
                email: userData.email, // Keep original email
                id: userData.id, // Keep original id
              };
              setUser(mergedData);
            } catch (error) {
              console.error('Error loading saved user-specific profile:', error);
              setUser(userData);
            }
          } else {
            setUser(userData);
          }
          
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
      // Check for existing user profile for this email
      const userSpecificKey = `echos_user_profile_${userData.email}`;
      const existingProfile = localStorage.getItem(userSpecificKey);
      
      let finalUserData = userData;
      if (existingProfile) {
        try {
          const savedProfile = JSON.parse(existingProfile);
          // Deep merge saved profile with login data, prioritizing saved profile for customizations
          finalUserData = {
            ...userData,
            ...savedProfile,
            profile: {
              ...userData.profile,
              ...savedProfile.profile,
            },
            email: userData.email, // Always use login email
            id: userData.id, // Use current session ID
          };
        } catch (error) {
          console.error('Error loading saved profile:', error);
        }
      }
      
      localStorage.setItem('echos_authenticated', 'true');
      localStorage.setItem('echos_user_profile', JSON.stringify(finalUserData)); // Current user (for checkAuth)
      localStorage.setItem(userSpecificKey, JSON.stringify(finalUserData)); // User-specific backup
      localStorage.setItem('echos_current_user', finalUserData.id);
      
      setUser(finalUserData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Error during login:', error);
      throw new Error('Failed to save authentication data');
    }
  };

  const logout = () => {
    try {
      // Clear all authentication and user data
      localStorage.removeItem('echos_authenticated');
      localStorage.removeItem('echos_user_profile');
      localStorage.removeItem('echos_user_settings');
      localStorage.removeItem('echos_current_user');
      
      // Optionally clear user-specific data
      const clearUserData = window.confirm('Do you want to clear all your saved data (reflections, chat history, etc.)?');
      if (clearUserData && user?.email) {
        localStorage.removeItem('echos_reflections');
        localStorage.removeItem('echos_chat_sessions');
        localStorage.removeItem('echos_chat_messages');
        localStorage.removeItem('echos_memories');
        localStorage.removeItem('echos_insights');
        
        // Also remove user-specific profile
        const userSpecificKey = `echos_user_profile_${user.email}`;
        localStorage.removeItem(userSpecificKey);
      }
      
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  const updateUser = (userData: Partial<User>) => {
    if (!user) return;
    
    try {
      const updatedUser = { ...user, ...userData };
      
      // Save to both global key (for checkAuth) and user-specific key (for persistence)
      localStorage.setItem('echos_user_profile', JSON.stringify(updatedUser));
      if (updatedUser.email) {
        const userSpecificKey = `echos_user_profile_${updatedUser.email}`;
        localStorage.setItem(userSpecificKey, JSON.stringify(updatedUser));
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