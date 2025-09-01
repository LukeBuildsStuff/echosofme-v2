import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { useAuth } from './AuthContext';

export interface SettingsData {
  theme: 'light' | 'dark' | 'auto';
  dailyReminders: boolean;
  reminderTime: string;
  streakNotifications: boolean;
  emailUpdates: boolean;
  eleanorInitiates: boolean;
}

interface SettingsContextType {
  settings: SettingsData;
  updateSetting: <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => void;
  resetSettings: () => void;
}

const defaultSettings: SettingsData = {
  theme: 'auto',
  dailyReminders: true,
  reminderTime: '20:00',
  streakNotifications: true,
  emailUpdates: true,
  eleanorInitiates: true,
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

interface SettingsProviderProps {
  children: ReactNode;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const [settings, setSettings] = useState<SettingsData>(defaultSettings);

  // Load settings from localStorage when user changes
  useEffect(() => {
    let targetUserEmail = user?.email;
    
    if (!targetUserEmail) {
      // No user logged in, try to get last logged-in user's settings
      const lastUser = localStorage.getItem('echos_last_settings_user');
      if (lastUser) {
        targetUserEmail = lastUser;
      }
    } else {
      // User is logged in, remember them as the last user for settings
      // Normalize email for consistency
      targetUserEmail = targetUserEmail.toLowerCase().trim();
      localStorage.setItem('echos_last_settings_user', targetUserEmail);
    }

    if (!targetUserEmail) {
      // No current user and no last user, use defaults
      setSettings(defaultSettings);
      return;
    }

    const userSpecificKey = `echos_settings_${targetUserEmail}`;
    const savedSettings = localStorage.getItem(userSpecificKey);
    
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings({ ...defaultSettings, ...parsedSettings });
      } catch (error) {
        console.error('Error parsing saved settings:', error);
        setSettings(defaultSettings);
      }
    } else {
      // Check for old generic settings and migrate them
      const oldSettings = localStorage.getItem('echos_settings');
      if (oldSettings) {
        try {
          const parsedOldSettings = JSON.parse(oldSettings);
          const migratedSettings = { ...defaultSettings, ...parsedOldSettings };
          setSettings(migratedSettings);
          // Save migrated settings with user-specific key
          localStorage.setItem(userSpecificKey, JSON.stringify(migratedSettings));
          // Remove old generic settings
          localStorage.removeItem('echos_settings');
        } catch (error) {
          console.error('Error migrating old settings:', error);
          setSettings(defaultSettings);
        }
      } else {
        // No saved settings, use defaults
        setSettings(defaultSettings);
      }
    }
  }, [user?.email]);

  // Apply theme to document
  useEffect(() => {
    const applyTheme = () => {
      const root = document.documentElement;
      
      if (settings.theme === 'dark') {
        root.classList.add('dark');
      } else if (settings.theme === 'light') {
        root.classList.remove('dark');
      } else {
        // Auto mode - follow system preference
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (systemDark) {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      }
    };

    applyTheme();

    // Listen for system theme changes if auto mode is selected
    if (settings.theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => applyTheme();
      mediaQuery.addEventListener('change', handleChange);
      
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [settings.theme]);

  const updateSetting = <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    
    // Save to localStorage with user-specific key
    if (user?.email) {
      // Normalize email for consistent key usage
      const normalizedEmail = user.email.toLowerCase().trim();
      const userSpecificKey = `echos_settings_${normalizedEmail}`;
      localStorage.setItem(userSpecificKey, JSON.stringify(newSettings));
    }
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
    
    // Remove user-specific settings
    if (user?.email) {
      // Normalize email for consistent key usage
      const normalizedEmail = user.email.toLowerCase().trim();
      const userSpecificKey = `echos_settings_${normalizedEmail}`;
      localStorage.removeItem(userSpecificKey);
    }
    
    // Also remove old generic settings if they exist
    localStorage.removeItem('echos_settings');
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSetting, resetSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};