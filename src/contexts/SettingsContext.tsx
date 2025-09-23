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
      if (isLoading) {
        console.log('⏳ Settings already loading, skipping duplicate request');
        return; // Prevent concurrent executions
      }

      setIsLoading(true);
      console.log('🔄 Starting settings load process...');

      let targetUserEmail = user?.email;

      if (!targetUserEmail) {
        // No user logged in, try to get last logged-in user's settings from localStorage
        const lastUser = localStorage.getItem('last_user_email');
        if (lastUser) {
          targetUserEmail = lastUser;
          console.log('📱 Loading offline settings for:', targetUserEmail);

          // For non-authenticated users, only use localStorage
          const userSpecificKey = `echos_settings_${targetUserEmail}`;
          const savedSettings = localStorage.getItem(userSpecificKey);

          if (savedSettings) {
            const parsedSettings = safeJSONParse(savedSettings, {});
            setSettings({ ...defaultSettings, ...parsedSettings });
            console.log('✅ Loaded offline settings:', parsedSettings);
          } else {
            setSettings(defaultSettings);
            console.log('📝 No offline settings found, using defaults');
          }
        } else {
          setSettings(defaultSettings);
          console.log('🆕 No previous user found, using defaults');
        }
        setIsLoading(false);
        return;
      }

      // User is logged in, normalize email and remember them
      targetUserEmail = targetUserEmail.toLowerCase().trim();
      localStorage.setItem('last_user_email', targetUserEmail);
      console.log('👤 Authenticated user detected:', targetUserEmail);

      // Try to load settings from database (simplified - no retries)
      try {
        console.log('🔄 Loading settings from database...');

        const databaseSettings = await api.getUserSettings();

        if (databaseSettings !== null) {
          // Database returned settings (could be empty object for new user)
          console.log('✅ Loaded settings from database:', databaseSettings);
          const mergedSettings = { ...defaultSettings, ...databaseSettings };
          setSettings(mergedSettings);

          // Cache in localStorage for offline access
          const userSpecificKey = `echos_settings_${targetUserEmail}`;
          localStorage.setItem(userSpecificKey, JSON.stringify(mergedSettings));
          setIsLoading(false);
          return;
        } else {
          console.log('⚠️ Database returned null, using localStorage fallback...');
        }

        // Database error - check localStorage for fallback
        const userSpecificKey = `echos_settings_${targetUserEmail}`;
        const savedSettings = localStorage.getItem(userSpecificKey);

        if (savedSettings) {
          const parsedSettings = safeJSONParse(savedSettings, {});
          const mergedSettings = { ...defaultSettings, ...parsedSettings };
          setSettings(mergedSettings);
          console.log('📱 Loaded settings from localStorage fallback');
          setIsLoading(false);
          return;
        }

        // No localStorage either - use defaults
        console.log('🆕 No existing settings found, using defaults');
        setSettings(defaultSettings);
        setIsLoading(false);
        return;

      } catch (error) {
        console.warn('⚠️ Database settings load failed:', error);

        // Error loading from database - use localStorage fallback
        const userSpecificKey = `echos_settings_${targetUserEmail}`;
        const savedSettings = localStorage.getItem(userSpecificKey);

        if (savedSettings) {
          const parsedSettings = safeJSONParse(savedSettings, {});
          setSettings({ ...defaultSettings, ...parsedSettings });
          console.log('📱 Error fallback: Loaded settings from localStorage');
        } else {
          setSettings(defaultSettings);
          console.log('📝 Error fallback: No localStorage settings, using defaults');
        }
        setIsLoading(false);
      }
    };

    // Add a small delay to ensure auth context has stabilized
    const timeoutId = setTimeout(loadSettings, 100);
    return () => clearTimeout(timeoutId);
  }, [user?.email, isLoading]);

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

    console.log(`🔄 Updating setting: ${String(key)} = ${value}`);

    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    // Get fresh user data to ensure we have a valid user record
    let currentUser;
    try {
      currentUser = await api.getCurrentUser();
    } catch (userError) {
      console.warn('⚠️ Could not get current user, falling back to cached user:', userError);
      currentUser = user;
    }

    // Save to localStorage with user-specific key (immediate backup)
    let emailToUse = currentUser?.email || user?.email;
    if (!emailToUse) {
      emailToUse = localStorage.getItem('last_user_email') || undefined;
    }

    if (emailToUse) {
      // Normalize email for consistent key usage
      const normalizedEmail = emailToUse.toLowerCase().trim();
      const userSpecificKey = `echos_settings_${normalizedEmail}`;
      localStorage.setItem(userSpecificKey, JSON.stringify(newSettings));
      console.log('💾 Settings backed up to localStorage');

      // If user is authenticated, also save to database
      if (currentUser?.email) {
        try {
          console.log('💾 Saving settings to database...');
          await api.updateUserSettings(newSettings);
          console.log('✅ Settings saved to database successfully');

          // Immediate verification - don't use setTimeout
          try {
            console.log('🔍 VERIFICATION: Checking what was saved...');
            const verificationData = await api.getUserSettings();
            console.log('🔍 VERIFICATION: Retrieved settings:', verificationData);

            // Check if the key we just saved is actually there
            if (verificationData && verificationData[key] === value) {
              console.log(`✅ VERIFICATION: Setting ${String(key)} correctly saved as ${value}`);
            } else {
              console.error(`❌ VERIFICATION: Setting ${String(key)} not found or incorrect:`, {
                expected: value,
                actual: verificationData?.[key],
                allSettings: verificationData
              });
              throw new Error(`Settings verification failed for ${String(key)}`);
            }
          } catch (verificationError) {
            console.error('❌ Settings verification failed:', verificationError);
            // Don't show error to user for verification failures - the save might have worked
          }

          showSuccess('Settings Saved', 'Your preferences have been saved and will sync across devices.');
        } catch (error) {
          console.error('❌ DETAILED ERROR - Failed to save settings to database:');
          console.error('❌ Error object:', error);
          console.error('❌ Error type:', typeof error);
          console.error('❌ Error constructor:', error?.constructor?.name);
          if (error instanceof Error) {
            console.error('❌ Error message:', error.message);
            console.error('❌ Error stack:', error.stack);
          }
          console.error('❌ Full error details:', JSON.stringify(error, null, 2));

          // Show specific error message based on error type
          let errorMessage = `Settings save failed: ${error instanceof Error ? error.message : 'Unknown error'}`;
          if (error instanceof Error) {
            if (error.message.includes('User not authenticated')) {
              errorMessage = 'Please log in again to sync your settings.';
            } else if (error.message.includes('verification failed')) {
              errorMessage = 'Settings may not have saved correctly. Please refresh and try again.';
            } else if (error.message.includes('Invalid user ID')) {
              errorMessage = 'Account error detected. Please log out and log back in.';
            } else if (error.message.includes('upsert failed')) {
              errorMessage = `Database error: ${error.message}`;
            }
          }

          showError('Settings Save Failed', errorMessage);
          // Settings still saved to localStorage, so functionality continues
        }
      } else {
        console.log('📋 User not authenticated, settings only saved locally');
      }
    } else {
      console.warn('⚠️ No email found for settings key - settings may not persist');
    }
  };

  const resetSettings = async () => {
    console.log('🔄 Resetting all settings to defaults');
    setSettings(defaultSettings);

    // Get fresh user data
    let currentUser;
    try {
      currentUser = await api.getCurrentUser();
    } catch (userError) {
      console.warn('⚠️ Could not get current user for reset, using cached user:', userError);
      currentUser = user;
    }

    // Remove user-specific settings from localStorage
    let emailToUse = currentUser?.email || user?.email;
    if (!emailToUse) {
      emailToUse = localStorage.getItem('last_user_email') || undefined;
    }

    if (emailToUse) {
      // Normalize email for consistent key usage
      const normalizedEmail = emailToUse.toLowerCase().trim();
      const userSpecificKey = `echos_settings_${normalizedEmail}`;
      localStorage.removeItem(userSpecificKey);
      console.log('📱 Removed settings from localStorage');

      // If user is authenticated, also reset database settings
      if (currentUser?.email) {
        try {
          await api.updateUserSettings(defaultSettings);
          console.log('✅ Settings reset in database');
          showSuccess('Settings Reset', 'All settings have been reset to their default values.');
        } catch (error) {
          console.warn('⚠️ Failed to reset settings in database:', error);
          showError('Reset Incomplete', 'Settings reset locally but may not have synced to cloud.');
        }
      }
    }

    // Also remove old generic settings if they exist
    localStorage.removeItem('echos_settings');
    console.log('📝 Cleanup: Removed old generic settings');
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSetting, resetSettings, isLoading }}>
      {children}
    </SettingsContext.Provider>
  );
};