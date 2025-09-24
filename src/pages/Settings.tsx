import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { useSettings } from '../contexts/SettingsContext';
import { useEcho } from '../contexts/EchoContext';
import { useToast } from '../contexts/ToastContext';
import { validatePassword, getPasswordStrengthColor } from '../utils/passwordValidator';

const Settings: React.FC = () => {
  const { user, logout, updateProfile, updatePassword } = useAuth();
  const { settings, updateSetting } = useSettings();
  const { reflections, stats } = useEcho();
  const { showSuccess, showError, showInfo } = useToast();

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  const [profileSettings, setProfileSettings] = useState({
    displayName: user?.displayName || '',
    bio: user?.profile?.introduction || '',
  });

  // Track if we've initialized the profile settings to prevent premature syncing
  const [profileInitialized, setProfileInitialized] = useState(false);

  // Sync profile data from database when Settings component first mounts
  useEffect(() => {
    const syncProfileData = async () => {
      if (user && user.email && !profileInitialized) {
        try {
          // Always sync from database when Settings page loads to get latest data
          console.log('🔄 Settings: Syncing profile from database...');
          // await syncProfile(); // Function not available
          
          // After sync, the user object should be updated, but we need to wait for the next render
          // So we'll set a small delay to ensure the user object has been updated
          setTimeout(() => {
            const loadedProfile = {
              displayName: user.displayName || '',
              bio: user.profile?.introduction || '',
            };
            setProfileSettings(loadedProfile);
            setProfileInitialized(true);
            console.log('✅ Settings: Profile data loaded:', loadedProfile);
          }, 100);
        } catch (error) {
          console.error('⚠️ Settings: Profile sync failed, using cached data:', error);
          // Fallback to cached user data if sync fails
          const fallbackProfile = {
            displayName: user.displayName || '',
            bio: user.profile?.introduction || '',
          };
          setProfileSettings(fallbackProfile);
          setProfileInitialized(true);
          console.log('📋 Settings: Using fallback profile data:', fallbackProfile);
        }
      }
    };

    // Only run once when component mounts if user is loaded
    if (user?.email) {
      syncProfileData();
    }
  }, [user?.email]); // Only depend on email, not syncProfile to avoid loops
  
  // Update profile settings when user object changes after sync
  useEffect(() => {
    if (user && profileInitialized) {
      const updatedProfile = {
        displayName: user.displayName || '',
        bio: user.profile?.introduction || '',
      };
      setProfileSettings(updatedProfile);
      console.log('📱 Settings: Updated profile settings from user context:', updatedProfile);
    }
  }, [user?.displayName, user?.profile?.introduction, profileInitialized]);

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordErrors, setPasswordErrors] = useState<string[]>([]);

  const handleProfileChange = (key: string, value: any) => {
    setProfileSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveProfile = async () => {
    try {
      console.log('🔄 Settings: Saving profile data:', {
        displayName: profileSettings.displayName,
        introduction: profileSettings.bio
      });

      // Use the updateProfile method with proper field mapping
      await updateProfile({
        displayName: profileSettings.displayName,
        introduction: profileSettings.bio,
      });


      showSuccess('Profile Updated', 'Your profile settings have been saved and synced across devices.');
      console.log('✅ Settings: Profile save successful');
    } catch (error) {
      console.error('❌ Settings: Profile update failed:', error);
      showError('Save Failed', 'There was an error saving your profile. Please try again.');
    }
  };

  const handleExportData = () => {
    try {
      // Create export data structure
      const exportData = {
        exportDate: new Date().toISOString().split('T')[0],
        exportTimestamp: new Date().toISOString(),
        user: {
          email: user?.email || '',
          displayName: user?.displayName || '',
          bio: user?.profile?.introduction || '',
          accountCreated: user?.created_at || ''
        },
        settings: {
          dailyReminders: settings.dailyReminders,
          reminderTime: settings.reminderTime,
          streakNotifications: settings.streakNotifications,
          emailUpdates: settings.emailUpdates,
          eleanorInitiates: settings.eleanorInitiates
        },
        reflections: reflections.map(reflection => ({
          id: reflection.id,
          question: reflection.question,
          response: reflection.response,
          category: reflection.category,
          wordCount: reflection.wordCount,
          qualityScore: reflection.qualityScore,
          tags: reflection.tags,
          createdAt: reflection.createdAt
        })),
        statistics: {
          totalReflections: stats.totalReflections,
          categoriesCovered: stats.categoriesCovered,
          averageWordCount: stats.averageWordCount,
          averageQualityScore: stats.averageQualityScore,
          currentStreak: stats.currentStreak,
          longestStreak: stats.longestStreak,
          echoReadiness: stats.echoReadiness
        }
      };

      // Create filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
      const filename = `echosofme-export-${timestamp}.json`;

      // Create and download file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      showSuccess('Export Complete', `Your data has been exported to ${filename}`);
      console.log('✅ Data exported successfully:', {
        reflections: reflections.length,
        filename
      });

    } catch (error) {
      console.error('❌ Export failed:', error);
      showError('Export Failed', 'There was an error exporting your data. Please try again.');
    }
  };

  const handleClearData = () => {
    if (window.confirm('Are you sure you want to clear all local data? This cannot be undone.')) {
      localStorage.clear();
      showSuccess('Data Cleared', 'All local data has been cleared successfully.');
    }
  };

  const handleClearAllData = () => {
    // const success = clearAllUserData(); // Function not available
    // if (success) {
    //   showSuccess('Data Cleared', 'All your data has been permanently deleted.');
    // }
    showInfo('Feature Unavailable', 'Data clearing is not implemented yet.');
  };

  const handleDeleteAccount = () => {
    if (window.confirm('Are you absolutely sure? This will permanently delete your account and all reflections.')) {
      // TODO: Implement account deletion
      logout();
      showInfo('Feature Coming Soon', 'Account deletion will be available in a future update.');
    }
  };

  const handlePasswordChange = (key: string, value: string) => {
    setPasswordData(prev => ({
      ...prev,
      [key]: value
    }));
    // Clear errors when user starts typing
    if (passwordErrors.length > 0) {
      setPasswordErrors([]);
    }
  };

  const handlePasswordSubmit = async () => {
    try {
      setPasswordLoading(true);
      setPasswordErrors([]);

      // Validate new password
      const validation = validatePassword(passwordData.newPassword);
      if (!validation.isValid) {
        setPasswordErrors(validation.errors);
        return;
      }

      // Check password confirmation
      if (passwordData.newPassword !== passwordData.confirmPassword) {
        setPasswordErrors(['Passwords do not match']);
        return;
      }

      // Update password
      await updatePassword(passwordData.newPassword);

      // Reset form and hide it
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setShowPasswordForm(false);

      showSuccess('Password Updated', 'Your password has been changed successfully.');
    } catch (error: any) {
      console.error('Password update failed:', error);
      setPasswordErrors([error.message || 'Failed to update password. Please try again.']);
    } finally {
      setPasswordLoading(false);
    }
  };

  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: '', color: '' };
    const validation = validatePassword(password);
    return {
      strength: validation.strength.charAt(0).toUpperCase() + validation.strength.slice(1),
      color: getPasswordStrengthColor(validation.strength)
    };
  };

  return (
    <Layout hideFooter={true}>
      <div className="pt-20 min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Settings</h1>
            <p className="text-gray-600">Manage your account and customize your experience.</p>
          </div>

          <div className="space-y-8">
            
            {/* Profile Settings */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Settings</h2>
              
              {!profileInitialized ? (
                <div className="space-y-4">
                  <div className="text-center py-8">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-1/4 mb-4 mx-auto"></div>
                      <div className="h-12 bg-gray-200 rounded mb-4"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/4 mb-2 mx-auto"></div>
                      <div className="h-12 bg-gray-200 rounded mb-4"></div>
                    </div>
                    <p className="text-gray-500 text-sm">Loading profile...</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                <div>
                  <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    id="displayName"
                    value={profileSettings.displayName}
                    onChange={(e) => handleProfileChange('displayName', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="Your name"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Email cannot be changed at this time</p>
                </div>

                <div>
                  <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
                    Bio / Introduction
                  </label>
                  <textarea
                    id="bio"
                    value={profileSettings.bio}
                    onChange={(e) => handleProfileChange('bio', e.target.value)}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="Tell us a bit about yourself..."
                  />
                </div>

                  <div className="flex justify-end">
                    <button
                      onClick={handleSaveProfile}
                      className="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
                    >
                      Save Profile
                    </button>
                  </div>
                </div>
              )}
            </div>


            {/* Notification Settings */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Settings</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Daily Reflection Reminders</p>
                    <p className="text-sm text-gray-500">Get notified to write your daily reflection</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.dailyReminders}
                      onChange={(e) => updateSetting('dailyReminders', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                {settings.dailyReminders && (
                  <div className="ml-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Reminder Time</label>
                    <input
                      type="time"
                      value={settings.reminderTime}
                      onChange={(e) => updateSetting('reminderTime', e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Streak Notifications</p>
                    <p className="text-sm text-gray-500">Celebrate your reflection streaks</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.streakNotifications}
                      onChange={(e) => updateSetting('streakNotifications', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Email Updates</p>
                    <p className="text-sm text-gray-500">Receive product updates and insights</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.emailUpdates}
                      onChange={(e) => updateSetting('emailUpdates', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Echo Conversations</p>
                    <p className="text-sm text-gray-500">Allow Echos to start conversations and check in on you</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.eleanorInitiates}
                      onChange={(e) => updateSetting('eleanorInitiates', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
            </div>

            {/* Security Settings */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Security Settings</h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between py-3">
                  <div>
                    <p className="font-medium text-gray-900">Change Password</p>
                    <p className="text-sm text-gray-500">Update your account password</p>
                  </div>
                  <button
                    onClick={() => setShowPasswordForm(!showPasswordForm)}
                    className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                  >
                    {showPasswordForm ? 'Cancel' : 'Change'}
                  </button>
                </div>

                {showPasswordForm && (
                  <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                    {passwordErrors.length > 0 && (
                      <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <ul className="text-red-700 text-sm">
                          {passwordErrors.map((error, index) => (
                            <li key={index} className="mb-1">{error}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="space-y-4">
                      <div>
                        <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-2">
                          New Password
                        </label>
                        <input
                          type="password"
                          id="newPassword"
                          value={passwordData.newPassword}
                          onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                          disabled={passwordLoading}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
                          placeholder="Enter new password"
                        />
                        {passwordData.newPassword && (
                          <div className="mt-2">
                            <span className={`text-sm ${getPasswordStrength(passwordData.newPassword).color}`}>
                              Password strength: {getPasswordStrength(passwordData.newPassword).strength}
                            </span>
                          </div>
                        )}
                      </div>

                      <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                          Confirm New Password
                        </label>
                        <input
                          type="password"
                          id="confirmPassword"
                          value={passwordData.confirmPassword}
                          onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
                          disabled={passwordLoading}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
                          placeholder="Confirm new password"
                        />
                      </div>

                      <div className="flex space-x-3 pt-4">
                        <button
                          onClick={handlePasswordSubmit}
                          disabled={passwordLoading || !passwordData.newPassword || !passwordData.confirmPassword}
                          className="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {passwordLoading ? (
                            <div className="flex items-center">
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                              Updating...
                            </div>
                          ) : (
                            'Update Password'
                          )}
                        </button>
                        <button
                          onClick={() => {
                            setShowPasswordForm(false);
                            setPasswordData({
                              currentPassword: '',
                              newPassword: '',
                              confirmPassword: '',
                            });
                            setPasswordErrors([]);
                          }}
                          disabled={passwordLoading}
                          className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Privacy & Data */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Privacy & Data</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-gray-100">
                  <div>
                    <p className="font-medium text-gray-900">Export Your Data</p>
                    <p className="text-sm text-gray-500">Download all your reflections and data</p>
                  </div>
                  <button
                    onClick={handleExportData}
                    className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                  >
                    Export
                  </button>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-gray-100">
                  <div>
                    <p className="font-medium text-gray-900">Clear All Data</p>
                    <p className="text-sm text-gray-500">Permanently delete all your data (profile, reflections, settings, etc.)</p>
                  </div>
                  <button
                    onClick={handleClearAllData}
                    className="bg-red-100 text-red-700 px-4 py-2 rounded-lg font-medium hover:bg-red-200 transition-colors"
                  >
                    Clear All
                  </button>
                </div>

                <div className="flex items-center justify-between py-3">
                  <div>
                    <p className="font-medium text-gray-900">Delete Account</p>
                    <p className="text-sm text-gray-500">Permanently delete your account and all data</p>
                  </div>
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="bg-red-100 text-red-700 px-4 py-2 rounded-lg font-medium hover:bg-red-200 transition-colors"
                  >
                    Delete
                  </button>
                </div>

                {showDeleteConfirm && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800 font-medium mb-2">Are you absolutely sure?</p>
                    <p className="text-red-700 text-sm mb-4">This action cannot be undone. All your reflections and data will be permanently deleted.</p>
                    <div className="flex space-x-3">
                      <button
                        onClick={handleDeleteAccount}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors"
                      >
                        Yes, Delete Account
                      </button>
                      <button
                        onClick={() => setShowDeleteConfirm(false)}
                        className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* About */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">About</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">App Version</span>
                  <span className="font-medium">2.0.0</span>
                </div>
                
                <div className="space-y-2">
                  <a href="#" className="block text-primary hover:underline">Terms of Service</a>
                  <a href="#" className="block text-primary hover:underline">Privacy Policy</a>
                  <a href="#" className="block text-primary hover:underline">Support & Help</a>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;