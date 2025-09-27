import React, { createContext, useContext, useState, useEffect, useRef, type ReactNode } from 'react';
import { useAuth } from './SupabaseAuthContext';
import { api } from '../lib/supabase';
import { useToast } from './ToastContext';

export interface SettingsData {
  // Notification settings
  dailyReminders: boolean;
  reminderTime: string;
  streakNotifications: boolean;
  emailUpdates: boolean;
  eleanorInitiates: boolean;

  // General settings
  theme: 'light' | 'dark';
  language: string;
  region: string;
  timezone: string;
  dateFormat: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
  timeFormat: '12h' | '24h';

  updated_at?: number;
}

interface SettingsContextType {
  settings: SettingsData;
  updateSetting: <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => void;
  resetSettings: () => void;
  isLoading: boolean;
}

const defaultSettings: SettingsData = {
  // Notification settings
  dailyReminders: true,
  reminderTime: '20:00',
  streakNotifications: true,
  emailUpdates: true,
  eleanorInitiates: false,

  // General settings
  theme: 'light',
  language: 'en-US',
  region: 'US',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  dateFormat: 'MM/DD/YYYY',
  timeFormat: '12h',

  updated_at: Date.now(),
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
  const syncTimeoutRef = useRef<NodeJS.Timeout>();

  // Get user-specific localStorage key
  const getStorageKey = () => {
    const email = user?.email || localStorage.getItem('last_user_email');
    return email ? `echos_settings_${email.toLowerCase().trim()}` : 'echos_settings_default';
  };

  // Apply settings to UI immediately
  const applySettings = (newSettings: SettingsData) => {
    setSettings(newSettings);

    // Enforce light mode for all users
    const root = document.documentElement;
    root.classList.remove('dark');
  };

  // Debounced sync to Supabase
  const debouncedSync = (settingsToSync: SettingsData) => {
    if (!user?.email) return; // Only sync for authenticated users

    // Clear existing timeout
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current);
    }

    // Set new timeout for background sync
    syncTimeoutRef.current = setTimeout(async () => {
      try {
        await api.updateUserSettings(settingsToSync);
        console.log('✅ Settings synced to cloud');
      } catch (error) {
        console.warn('⚠️ Background sync failed:', error);
        // Silent fail - localStorage is source of truth
      }
    }, 1000);
  };

  // Load settings on app start
  useEffect(() => {
    const loadSettings = async () => {
      setIsLoading(true);

      // 1. Load local settings immediately for instant UI
      const storageKey = getStorageKey();
      const localSettingsStr = localStorage.getItem(storageKey);

      if (localSettingsStr) {
        try {
          const localSettings = JSON.parse(localSettingsStr);
          const mergedLocal = { ...defaultSettings, ...localSettings };
          applySettings(mergedLocal);
          console.log('⚡ Local settings applied instantly');
        } catch (error) {
          console.warn('⚠️ Invalid local settings, using defaults');
          applySettings(defaultSettings);
        }
      } else {
        applySettings(defaultSettings);
      }

      // 2. Sync from cloud in background (non-blocking)
      if (user?.email) {
        try {
          const cloudSettings = await api.getUserSettings();
          if (cloudSettings) {
            const mergedCloud = { ...defaultSettings, ...cloudSettings, updated_at: Date.now() };

            // Only update if cloud settings are newer (simple conflict resolution)
            const localTimestamp = localSettingsStr ?
              JSON.parse(localSettingsStr).updated_at || 0 : 0;
            const cloudTimestamp = cloudSettings.updated_at || 0;

            if (cloudTimestamp > localTimestamp) {
              applySettings(mergedCloud);
              localStorage.setItem(storageKey, JSON.stringify(mergedCloud));
              console.log('☁️ Cloud settings applied (newer than local)');
            } else {
              console.log('📱 Local settings kept (newer than cloud)');
            }
          }
        } catch (error) {
          console.warn('⚠️ Cloud sync failed, using local settings:', error);
          // Silent fail - local settings already loaded
        }
      }

      setIsLoading(false);
    };

    // Remember last user for offline access
    if (user?.email) {
      localStorage.setItem('last_user_email', user.email);
    }

    loadSettings();
  }, [user?.email]);


  // Update setting - instant local, eventual cloud
  const updateSetting = <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => {
    const newSettings = {
      ...settings,
      [key]: value,
      updated_at: Date.now()
    };

    // 1. Instant UI update
    applySettings(newSettings);

    // 2. Save to localStorage immediately
    const storageKey = getStorageKey();
    localStorage.setItem(storageKey, JSON.stringify(newSettings));

    // 3. Background sync to cloud (debounced)
    debouncedSync(newSettings);

    console.log(`⚡ Setting ${String(key)} updated instantly`);
  };

  // Reset settings
  const resetSettings = () => {
    const resetData = { ...defaultSettings, updated_at: Date.now() };

    // 1. Instant UI update
    applySettings(resetData);

    // 2. Clear localStorage
    const storageKey = getStorageKey();
    localStorage.removeItem(storageKey);

    // 3. Background sync to cloud
    if (user?.email) {
      debouncedSync(resetData);
      showSuccess('Settings Reset', 'All settings reset to defaults');
    }

    console.log('🔄 Settings reset to defaults');
  };

  return (
    <SettingsContext.Provider value={{
      settings,
      updateSetting,
      resetSettings,
      isLoading
    }}>
      {children}
    </SettingsContext.Provider>
  );
};