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

      // Add retry logic for race conditions
      let retryCount = 0;
      const maxRetries = 3;

      while (retryCount < maxRetries) {
        try {
          console.log(`🔄 Settings load attempt ${retryCount + 1}/${maxRetries}`);

          // DEBUG: Check what's actually in the database
          await api.debugUserProfile();

          // STEP 1: Try to load from database first (authenticated users)
          const databaseSettings = await api.getUserSettings();

          // Check if we got valid settings (not null and not an error)
          if (databaseSettings !== null) {
            if (Object.keys(databaseSettings).length > 0) {
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
              console.log('📝 Database returned empty settings object (new user)');
              // Empty settings object means new user - use defaults and save them
              setSettings(defaultSettings);

              // Save defaults to database for new user
              try {
                await api.updateUserSettings(defaultSettings);
                console.log('✅ Default settings saved for new user');
              } catch (saveError) {
                console.warn('⚠️ Failed to save default settings:', saveError);
              }

              // Cache in localStorage
              const userSpecificKey = `echos_settings_${targetUserEmail}`;
              localStorage.setItem(userSpecificKey, JSON.stringify(defaultSettings));
              setIsLoading(false);
              return;
            }
          } else {
            console.log('⚠️ Database returned null, checking localStorage for migration...');
          }

          // STEP 2: Database returned null (error or no profile), check localStorage for migration
          const userSpecificKey = `echos_settings_${targetUserEmail}`;
          const savedSettings = localStorage.getItem(userSpecificKey);

          if (savedSettings) {
            const parsedSettings = safeJSONParse(savedSettings, {});
            const mergedSettings = { ...defaultSettings, ...parsedSettings };
            setSettings(mergedSettings);
            console.log('📱 Loaded settings from localStorage:', parsedSettings);

            // Try to migrate localStorage settings to database
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
            console.log('🔄 Migrating old generic settings:', parsedOldSettings);

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
          console.log('🆕 No existing settings found, initializing with defaults');
          setSettings(defaultSettings);

          // Try to save defaults to database for consistency
          try {
            await api.updateUserSettings(defaultSettings);
            console.log('✅ Default settings saved to database');
          } catch (saveError) {
            console.warn('⚠️ Failed to save default settings to database:', saveError);
          }

          setIsLoading(false);
          return;

        } catch (error) {
          retryCount++;
          console.warn(`⚠️ Settings load attempt ${retryCount} failed:`, error);

          if (retryCount >= maxRetries) {
            // All retries exhausted, use localStorage fallback
            console.warn('⚠️ All database attempts failed, using localStorage fallback');

            const userSpecificKey = `echos_settings_${targetUserEmail}`;
            const savedSettings = localStorage.getItem(userSpecificKey);

            if (savedSettings) {
              const parsedSettings = safeJSONParse(savedSettings, {});
              setSettings({ ...defaultSettings, ...parsedSettings });
              console.log('📱 Fallback: Loaded settings from localStorage');
            } else {
              setSettings(defaultSettings);
              console.log('📝 Fallback: No localStorage settings, using defaults');
            }
            setIsLoading(false);
            return;
          } else {
            // Wait a bit before retrying to handle race conditions
            console.log(`⏳ Retrying in ${500 * retryCount}ms...`);
            await new Promise(resolve => setTimeout(resolve, 500 * retryCount));
          }
        }
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
          console.error('❌ Failed to save settings to database:', error);

          // Show specific error message based on error type
          let errorMessage = 'Settings saved locally but failed to sync to cloud.';
          if (error instanceof Error) {
            if (error.message.includes('User not authenticated')) {
              errorMessage = 'Please log in again to sync your settings.';
            } else if (error.message.includes('verification failed')) {
              errorMessage = 'Settings may not have saved correctly. Please refresh and try again.';
            } else if (error.message.includes('Invalid user ID')) {
              errorMessage = 'Account error detected. Please log out and log back in.';
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