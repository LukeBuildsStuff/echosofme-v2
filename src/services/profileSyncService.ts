import { getEleanorApiUrl } from '../utils/apiConfig';

export interface UserProfile {
  email: string;
  display_name?: string | null;
  introduction?: string | null;
  relationship?: string | null;
  meeting_status?: string | null;
  avatar_url?: string | null;
  theme_preference?: string | null;
  notification_settings?: Record<string, any>;
  custom_settings?: Record<string, any>;
  voice_id?: string | null;
}

export interface ProfileUpdateRequest {
  display_name?: string | null;
  introduction?: string | null;
  relationship?: string | null;
  meeting_status?: string | null;
  avatar_url?: string | null;
  theme_preference?: string | null;
  notification_settings?: Record<string, any>;
  custom_settings?: Record<string, any>;
  voice_id?: string | null;
}

class ProfileSyncService {
  private readonly STORAGE_KEY = 'echos_user_profile';
  private readonly isProfileSyncEnabled = import.meta.env.VITE_ENABLE_PROFILE_SYNC === 'true';
  
  async getUserProfile(userEmail: string): Promise<UserProfile | null> {
    // Try database first if sync is enabled
    if (this.isProfileSyncEnabled) {
      try {
        const apiUrl = getEleanorApiUrl();
        const response = await fetch(`${apiUrl}/profile/${encodeURIComponent(userEmail)}`);
        
        if (response.ok) {
          const profile = await response.json();
          console.log('✅ Profile loaded from database:', profile);
          
          // Cache to localStorage for offline access
          this.cacheProfile(profile);
          return profile;
        } else if (response.status !== 404) {
          console.warn('⚠️ Database profile fetch failed:', response.status, 'falling back to localStorage');
        }
      } catch (error) {
        console.warn('⚠️ Database profile fetch error, falling back to localStorage:', error);
      }
    }
    
    // Fallback to localStorage
    return this.getLocalProfile(userEmail);
  }

  async updateUserProfile(userEmail: string, updates: ProfileUpdateRequest): Promise<UserProfile | null> {
    let dbProfile: UserProfile | null = null;
    
    // Try to update database first if sync is enabled
    if (this.isProfileSyncEnabled) {
      try {
        const apiUrl = getEleanorApiUrl();
        const response = await fetch(`${apiUrl}/profile/${encodeURIComponent(userEmail)}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updates),
        });
        
        if (response.ok) {
          dbProfile = await response.json();
          console.log('✅ Profile updated in database:', dbProfile);
          
          // Cache to localStorage for consistency
          this.cacheProfile(dbProfile);
          return dbProfile;
        } else {
          console.warn('⚠️ Database profile update failed:', response.status, 'updating localStorage only');
        }
      } catch (error) {
        console.warn('⚠️ Database profile update error, updating localStorage only:', error);
      }
    }
    
    // Fallback: update localStorage
    const localProfile = this.updateLocalProfile(userEmail, updates);
    
    // If database sync is enabled but failed, queue for later sync
    if (this.isProfileSyncEnabled && !dbProfile) {
      this.queueProfileSync(userEmail, updates);
    }
    
    return localProfile;
  }

  private getLocalProfile(userEmail: string): UserProfile | null {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const profile = JSON.parse(stored);
        // Ensure the profile matches the current user
        if (profile.email === userEmail) {
          console.log('📱 Profile loaded from localStorage:', profile);
          return profile;
        }
      }
    } catch (error) {
      console.error('❌ Error reading profile from localStorage:', error);
    }
    
    // Return default profile structure
    return {
      email: userEmail,
      display_name: null,
      introduction: null,
      relationship: null,
      meeting_status: null,
      avatar_url: null,
      theme_preference: 'light',
      notification_settings: {},
      custom_settings: {}
    };
  }

  private updateLocalProfile(userEmail: string, updates: ProfileUpdateRequest): UserProfile {
    const currentProfile = this.getLocalProfile(userEmail) || {
      email: userEmail,
      display_name: null,
      introduction: null,
      relationship: null,
      meeting_status: null,
      avatar_url: null,
      theme_preference: 'light',
      notification_settings: {},
      custom_settings: {}
    };
    
    const updatedProfile = { ...currentProfile, ...updates };
    this.cacheProfile(updatedProfile);
    console.log('📱 Profile updated in localStorage:', updatedProfile);
    return updatedProfile;
  }

  private cacheProfile(profile: UserProfile): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(profile));
    } catch (error) {
      console.error('❌ Error caching profile to localStorage:', error);
    }
  }

  private queueProfileSync(userEmail: string, updates: ProfileUpdateRequest): void {
    // Store pending sync for retry later (e.g., when network is restored)
    const syncQueue = this.getSyncQueue();
    syncQueue.push({
      userEmail,
      updates,
      timestamp: new Date().toISOString()
    });
    
    try {
      localStorage.setItem('echos_profile_sync_queue', JSON.stringify(syncQueue));
      console.log('📋 Profile sync queued for retry:', { userEmail, updates });
    } catch (error) {
      console.error('❌ Error queuing profile sync:', error);
    }
  }

  private getSyncQueue(): Array<{ userEmail: string; updates: ProfileUpdateRequest; timestamp: string }> {
    try {
      const stored = localStorage.getItem('echos_profile_sync_queue');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('❌ Error reading sync queue:', error);
      return [];
    }
  }

  async retryQueuedSyncs(): Promise<void> {
    if (!this.isProfileSyncEnabled) return;
    
    const syncQueue = this.getSyncQueue();
    if (syncQueue.length === 0) return;
    
    console.log(`🔄 Attempting to sync ${syncQueue.length} queued profile updates...`);
    const remainingQueue = [];
    
    for (const queuedSync of syncQueue) {
      try {
        const apiUrl = getEleanorApiUrl();
        const response = await fetch(`${apiUrl}/profile/${encodeURIComponent(queuedSync.userEmail)}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(queuedSync.updates),
        });
        
        if (response.ok) {
          const profile = await response.json();
          this.cacheProfile(profile);
          console.log('✅ Queued profile sync successful:', queuedSync.userEmail);
        } else {
          remainingQueue.push(queuedSync);
          console.warn('⚠️ Queued profile sync still failing:', queuedSync.userEmail, response.status);
        }
      } catch (error) {
        remainingQueue.push(queuedSync);
        console.warn('⚠️ Queued profile sync error:', queuedSync.userEmail, error);
      }
    }
    
    // Update queue with remaining items
    try {
      if (remainingQueue.length > 0) {
        localStorage.setItem('echos_profile_sync_queue', JSON.stringify(remainingQueue));
      } else {
        localStorage.removeItem('echos_profile_sync_queue');
      }
    } catch (error) {
      console.error('❌ Error updating sync queue:', error);
    }
  }

  getFeatureStatus(): { enabled: boolean; source: string } {
    return {
      enabled: this.isProfileSyncEnabled,
      source: this.isProfileSyncEnabled ? 'database' : 'localStorage'
    };
  }
}

export const profileSyncService = new ProfileSyncService();