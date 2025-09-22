import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { useAuth } from './SupabaseAuthContext';
import { api } from '../lib/supabase';
import { useToast } from './ToastContext';

// Safe JSON parser to prevent crashes on invalid data
const safeJSONParse = <T,>(str: string | null, defaultValue: T): T => {
  if (!str) return defaultValue;
  try {
    return JSON.parse(str);
  } catch {
    return defaultValue;
  }
};

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
  updateSetting: <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => Promise<void>;
  resetSettings: () => Promise<void>;
  isLoading: boolean;
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
  const { showSuccess, showError } = useToast();
  const [settings, setSettings] = useState<SettingsData>(defaultSettings);
  const [isLoading, setIsLoading] = useState(false);

  // Load settings when user changes - try database first, then localStorage
  useEffect(() => {
    const loadSettings = async () => {
      if (isLoading) return; // Prevent concurrent executions
      setIsLoading(true);

      let targetUserEmail = user?.email;

      if (!targetUserEmail) {
        // No user logged in, try to get last logged-in user's settings from localStorage
        const lastUser = localStorage.getItem('last_user_email'); // Standardized key
        if (lastUser) {
          targetUserEmail = lastUser;

          // For non-authenticated users, only use localStorage
          const userSpecificKey = `echos_settings_${targetUserEmail}`;
          const savedSettings = localStorage.getItem(userSpecificKey);

          if (savedSettings) {
            const parsedSettings = safeJSONParse(savedSettings, {});
            setSettings({ ...defaultSettings, ...parsedSettings });
          } else {
            setSettings(defaultSettings);
          }
        } else {
          setSettings(defaultSettings);
        }
        setIsLoading(false);
        return;
      }

      // User is logged in, normalize email and remember them
      targetUserEmail = targetUserEmail.toLowerCase().trim();
      localStorage.setItem('last_user_email', targetUserEmail);

      try {
        // DEBUG: Check what's actually in the database
        await api.debugUserProfile();

        // STEP 1: Try to load from database first (authenticated users)
        const databaseSettings = await api.getUserSettings();

        if (databaseSettings && Object.keys(databaseSettings).length > 0) {
          // Database has settings, use them
          console.log('✅ Loaded settings from database:', databaseSettings);
          const mergedSettings = { ...defaultSettings, ...databaseSettings };
          setSettings(mergedSettings);

          // Cache in localStorage for offline access
          const userSpecificKey = `echos_settings_${targetUserEmail}`;
          localStorage.setItem(userSpecificKey, JSON.stringify(mergedSettings));
          setIsLoading(false);
          return;
        } else {
          console.log('⚠️ No settings found in database, checking localStorage...');
        }

        // STEP 2: Database empty, check localStorage for migration
        const userSpecificKey = `echos_settings_${targetUserEmail}`;
        const savedSettings = localStorage.getItem(userSpecificKey);

        if (savedSettings) {
          const parsedSettings = safeJSONParse(savedSettings, {});
          const mergedSettings = { ...defaultSettings, ...parsedSettings };
          setSettings(mergedSettings);

          // Migrate localStorage settings to database
          console.log('🔄 Migrating settings from localStorage to database');
          try {
            await api.updateUserSettings(mergedSettings);
            console.log('✅ Settings migrated to database successfully');
          } catch (migrationError) {
            console.warn('⚠️ Settings migration to database failed:', migrationError);
            // Continue with localStorage settings - no error thrown
          }
          setIsLoading(false);
          return;
        }

        // STEP 3: Check for old generic settings and migrate them
        const oldSettings = localStorage.getItem('echos_settings');
        if (oldSettings) {
          const parsedOldSettings = safeJSONParse(oldSettings, {});
          const migratedSettings = { ...defaultSettings, ...parsedOldSettings };
          setSettings(migratedSettings);

          // Save migrated settings with user-specific key
          localStorage.setItem(userSpecificKey, JSON.stringify(migratedSettings));

          // Try to save to database too
          try {
            await api.updateUserSettings(migratedSettings);
            console.log('✅ Old settings migrated to database');
          } catch (migrationError) {
            console.warn('⚠️ Old settings migration to database failed:', migrationError);
          }

          // Remove old generic settings
          localStorage.removeItem('echos_settings');
          setIsLoading(false);
          return;
        }

        // STEP 4: No settings found anywhere, use defaults
        setSettings(defaultSettings);
        setIsLoading(false);

      } catch (error) {
        console.warn('⚠️ Error loading settings from database, using localStorage fallback:', error);

        // Fallback to localStorage only
        const userSpecificKey = `echos_settings_${targetUserEmail}`;
        const savedSettings = localStorage.getItem(userSpecificKey);

        if (savedSettings) {
          const parsedSettings = safeJSONParse(savedSettings, {});
          setSettings({ ...defaultSettings, ...parsedSettings });
        } else {
          setSettings(defaultSettings);
        }
        setIsLoading(false);
      }
    };

    loadSettings();
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

  const updateSetting = async <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => {
    if (isLoading) {
      console.warn('⚠️ Settings update skipped - still loading');
      return;
    }

    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    // Save to localStorage with user-specific key (immediate backup)
    let emailToUse = user?.email;
    if (!emailToUse) {
      emailToUse = localStorage.getItem('last_user_email') || undefined;
    }

    if (emailToUse) {
      // Normalize email for consistent key usage
      const normalizedEmail = emailToUse.toLowerCase().trim();
      const userSpecificKey = `echos_settings_${normalizedEmail}`;
      localStorage.setItem(userSpecificKey, JSON.stringify(newSettings));

      // If user is authenticated, also save to database
      if (user?.email) {
        try {
          await api.updateUserSettings(newSettings);
          console.log('✅ Settings saved to database');

          // DEBUG: Verify what was actually saved
          setTimeout(async () => {
            console.log('🔍 VERIFICATION: Checking what was saved...');
            await api.debugUserProfile();
          }, 500);

          showSuccess('Settings Saved', 'Your preferences have been saved and will sync across devices.');
        } catch (error) {
          console.error('❌ Failed to save settings to database:', error);
          showError('Settings Save Failed', 'Settings saved locally but failed to sync to cloud. Please check your connection.');
          // Settings still saved to localStorage, so functionality continues
        }
      }
    }
  };

  const resetSettings = async () => {
    setSettings(defaultSettings);

    // Remove user-specific settings from localStorage
    let emailToUse = user?.email;
    if (!emailToUse) {
      emailToUse = localStorage.getItem('last_user_email') || undefined;
    }

    if (emailToUse) {
      // Normalize email for consistent key usage
      const normalizedEmail = emailToUse.toLowerCase().trim();
      const userSpecificKey = `echos_settings_${normalizedEmail}`;
      localStorage.removeItem(userSpecificKey);

      // If user is authenticated, also reset database settings
      if (user?.email) {
        try {
          await api.updateUserSettings(defaultSettings);
          console.log('✅ Settings reset in database');
        } catch (error) {
          console.warn('⚠️ Failed to reset settings in database:', error);
          // localStorage was still cleared, so reset partially works
        }
      }
    }

    // Also remove old generic settings if they exist
    localStorage.removeItem('echos_settings');
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSetting, resetSettings, isLoading }}>
      {children}
    </SettingsContext.Provider>
  );
};