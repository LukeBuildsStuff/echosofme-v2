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
      localStorage.setItem('echos_authenticated', 'true');
      localStorage.setItem('echos_user_profile', JSON.stringify(userData));
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
      // Clear all authentication and user data
      localStorage.removeItem('echos_authenticated');
      localStorage.removeItem('echos_user_profile');
      localStorage.removeItem('echos_user_settings');
      localStorage.removeItem('echos_current_user');
      
      // Optionally clear user-specific data
      const clearUserData = window.confirm('Do you want to clear all your saved data (reflections, chat history, etc.)?');
      if (clearUserData) {
        localStorage.removeItem('echos_reflections');
        localStorage.removeItem('echos_chat_sessions');
        localStorage.removeItem('echos_chat_messages');
        localStorage.removeItem('echos_memories');
        localStorage.removeItem('echos_insights');
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
      localStorage.setItem('echos_user_profile', JSON.stringify(updatedUser));
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