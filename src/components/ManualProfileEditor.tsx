import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { useToast } from '../contexts/ToastContext';

interface Child {
  name: string;
  dob: string;
}

interface StepParent {
  name: string;
  dob: string;
}

interface Mentor {
  name: string;
  dob?: string;
}

interface Anniversary {
  name: string;
  date: string;
}

interface ImportantDate {
  name: string;
  date: string;
}

interface ProfileData {
  // Personal Information
  full_name: string;
  nickname: string;
  dob: string;
  location: string;

  // Close Relationships
  has_partner: boolean;
  partner_name: string;
  partner_anniversary: string;
  has_children: boolean;
  children: Child[];
  father_name: string;
  father_dob: string;
  mother_name: string;
  mother_dob: string;
  step_parents: StepParent[];
  mentors: Mentor[];

  // Life Anchors
  profession: string;
  education: string;
  spiritual_background: string;

  // Milestones
  anniversaries: Anniversary[];
  important_dates: ImportantDate[];
}

interface ManualProfileEditorProps {
  className?: string;
  isExpanded?: boolean;
  onExpandChange?: (expanded: boolean) => void;
}

const ManualProfileEditor: React.FC<ManualProfileEditorProps> = ({
  className,
  isExpanded: externalIsExpanded,
  onExpandChange
}) => {
  const { user, updateProfile } = useAuth();
  const { showSuccess, showError } = useToast();
  const [internalIsExpanded, setInternalIsExpanded] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Use external state if provided, otherwise use internal state
  const isExpanded = externalIsExpanded !== undefined ? externalIsExpanded : internalIsExpanded;
  const setIsExpanded = onExpandChange || setInternalIsExpanded;

  const [profileData, setProfileData] = useState<ProfileData>({
    // Personal Information
    full_name: '',
    nickname: '',
    dob: '',
    location: '',

    // Close Relationships
    has_partner: false,
    partner_name: '',
    partner_anniversary: '',
    has_children: false,
    children: [],
    father_name: '',
    father_dob: '',
    mother_name: '',
    mother_dob: '',
    step_parents: [],
    mentors: [],

    // Life Anchors
    profession: '',
    education: '',
    spiritual_background: '',

    // Milestones
    anniversaries: [],
    important_dates: [],
  });

  // Load existing profile data on component mount
  useEffect(() => {
    if (user?.profile?.introduction) {
      try {
        const existingData = JSON.parse(user.profile.introduction);
        if (existingData.personal && existingData.relationships && existingData.life) {
          // Parse the structured format from ProfileChat
          setProfileData({
            // Personal Information
            full_name: existingData.personal.full_name || '',
            nickname: existingData.personal.nickname || '',
            dob: existingData.personal.dob || '',
            location: existingData.personal.location || '',

            // Close Relationships
            has_partner: existingData.relationships.has_partner || false,
            partner_name: existingData.relationships.partner_name || '',
            partner_anniversary: existingData.relationships.partner_anniversary || '',
            has_children: existingData.relationships.has_children || false,
            children: existingData.relationships.children || [],
            father_name: existingData.relationships.father_name || '',
            father_dob: existingData.relationships.father_dob || '',
            mother_name: existingData.relationships.mother_name || '',
            mother_dob: existingData.relationships.mother_dob || '',
            step_parents: existingData.relationships.step_parents || [],
            mentors: existingData.relationships.mentors || [],

            // Life Anchors
            profession: existingData.life.profession || '',
            education: existingData.life.education || '',
            spiritual_background: existingData.life.spiritual_background || '',

            // Milestones
            anniversaries: existingData.anniversaries || [],
            important_dates: existingData.important_dates || [],
          });
        }
      } catch (error) {
        console.error('Failed to parse existing profile data:', error);
      }
    }
  }, [user?.profile?.introduction]);

  const handleInputChange = (field: keyof ProfileData, value: any) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleChildChange = (index: number, field: keyof Child, value: string) => {
    const updatedChildren = [...profileData.children];
    updatedChildren[index] = { ...updatedChildren[index], [field]: value };
    setProfileData(prev => ({ ...prev, children: updatedChildren }));
  };

  const addChild = () => {
    setProfileData(prev => ({
      ...prev,
      children: [...prev.children, { name: '', dob: '' }]
    }));
  };

  const removeChild = (index: number) => {
    setProfileData(prev => ({
      ...prev,
      children: prev.children.filter((_, i) => i !== index)
    }));
  };

  const handleStepParentChange = (index: number, field: keyof StepParent, value: string) => {
    const updatedStepParents = [...profileData.step_parents];
    updatedStepParents[index] = { ...updatedStepParents[index], [field]: value };
    setProfileData(prev => ({ ...prev, step_parents: updatedStepParents }));
  };

  const addStepParent = () => {
    setProfileData(prev => ({
      ...prev,
      step_parents: [...prev.step_parents, { name: '', dob: '' }]
    }));
  };

  const removeStepParent = (index: number) => {
    setProfileData(prev => ({
      ...prev,
      step_parents: prev.step_parents.filter((_, i) => i !== index)
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Create the same structured format as ProfileChat
      const completeProfile = {
        personal: {
          full_name: profileData.full_name,
          nickname: profileData.nickname,
          dob: profileData.dob,
          location: profileData.location
        },
        relationships: {
          has_partner: profileData.has_partner,
          partner_name: profileData.partner_name,
          partner_anniversary: profileData.partner_anniversary,
          has_children: profileData.has_children,
          children: profileData.children,
          father_name: profileData.father_name,
          father_dob: profileData.father_dob,
          mother_name: profileData.mother_name,
          mother_dob: profileData.mother_dob,
          step_parents: profileData.step_parents,
          mentors: profileData.mentors
        },
        life: {
          profession: profileData.profession,
          education: profileData.education,
          spiritual_background: profileData.spiritual_background
        },
        anniversaries: profileData.anniversaries,
        important_dates: profileData.important_dates,
        collected_at: new Date().toISOString(),
        updated_manually: true
      };

      // Save to database
      const saveData = {
        displayName: profileData.nickname || profileData.full_name || '',
        introduction: JSON.stringify(completeProfile)
      };

      await updateProfile(saveData);
      showSuccess('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to save profile:', error);
      showError('Failed to save profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isExpanded) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-4 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Manual Profile Editor</h3>
              <p className="text-sm text-gray-500">Edit your profile information directly</p>
            </div>
          </div>
          <button
            onClick={() => setIsExpanded(true)}
            className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            Edit Profile
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Manual Profile Editor</h3>
        <button
          onClick={() => setIsExpanded(false)}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          title="Collapse"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      <div className="space-y-8">
        {/* Personal Information */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Personal Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={profileData.full_name}
                onChange={(e) => handleInputChange('full_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your full legal name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
              <input
                type="text"
                value={profileData.nickname}
                onChange={(e) => handleInputChange('nickname', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="What people call you"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
              <input
                type="text"
                value={profileData.dob}
                onChange={(e) => handleInputChange('dob', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., March 15, 1985"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                value={profileData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="City, State or general area"
              />
            </div>
          </div>
        </div>

        {/* Partner Information */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Partner & Relationship</h4>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="has_partner"
                checked={profileData.has_partner}
                onChange={(e) => handleInputChange('has_partner', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="has_partner" className="text-sm font-medium text-gray-700">
                I have a spouse or partner
              </label>
            </div>
            {profileData.has_partner && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-7">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Partner's Name</label>
                  <input
                    type="text"
                    value={profileData.partner_name}
                    onChange={(e) => handleInputChange('partner_name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Your partner's name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Anniversary Date</label>
                  <input
                    type="text"
                    value={profileData.partner_anniversary}
                    onChange={(e) => handleInputChange('partner_anniversary', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Wedding or relationship anniversary"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Children Information */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Children</h4>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="has_children"
                checked={profileData.has_children}
                onChange={(e) => handleInputChange('has_children', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="has_children" className="text-sm font-medium text-gray-700">
                I have children
              </label>
            </div>
            {profileData.has_children && (
              <div className="ml-7 space-y-4">
                {profileData.children.map((child, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                      <input
                        type="text"
                        value={child.name}
                        onChange={(e) => handleChildChange(index, 'name', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Child's name"
                      />
                      <input
                        type="text"
                        value={child.dob}
                        onChange={(e) => handleChildChange(index, 'dob', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Date of birth"
                      />
                    </div>
                    <button
                      onClick={() => removeChild(index)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                      title="Remove child"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
                <button
                  onClick={addChild}
                  className="text-sm text-blue-600 hover:text-blue-800 transition-colors flex items-center space-x-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Add another child</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Parents Information */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Parents</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Father</h5>
              <div className="space-y-3">
                <input
                  type="text"
                  value={profileData.father_name}
                  onChange={(e) => handleInputChange('father_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Father's name"
                />
                <input
                  type="text"
                  value={profileData.father_dob}
                  onChange={(e) => handleInputChange('father_dob', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Father's date of birth"
                />
              </div>
            </div>
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Mother</h5>
              <div className="space-y-3">
                <input
                  type="text"
                  value={profileData.mother_name}
                  onChange={(e) => handleInputChange('mother_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Mother's name"
                />
                <input
                  type="text"
                  value={profileData.mother_dob}
                  onChange={(e) => handleInputChange('mother_dob', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Mother's date of birth"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Step-Parents */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Step-Parents</h4>
          <div className="space-y-4">
            {profileData.step_parents.map((stepParent, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    type="text"
                    value={stepParent.name}
                    onChange={(e) => handleStepParentChange(index, 'name', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Step-parent's name"
                  />
                  <input
                    type="text"
                    value={stepParent.dob}
                    onChange={(e) => handleStepParentChange(index, 'dob', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Date of birth"
                  />
                </div>
                <button
                  onClick={() => removeStepParent(index)}
                  className="text-red-500 hover:text-red-700 transition-colors"
                  title="Remove step-parent"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
            <button
              onClick={addStepParent}
              className="text-sm text-blue-600 hover:text-blue-800 transition-colors flex items-center space-x-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Add step-parent</span>
            </button>
          </div>
        </div>

        {/* Life Information */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-4">Life & Background</h4>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Profession</label>
              <input
                type="text"
                value={profileData.profession}
                onChange={(e) => handleInputChange('profession', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your career or occupation"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Education</label>
              <input
                type="text"
                value={profileData.education}
                onChange={(e) => handleInputChange('education', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your educational background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Spiritual Background</label>
              <input
                type="text"
                value={profileData.spiritual_background}
                onChange={(e) => handleInputChange('spiritual_background', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Religious or spiritual beliefs"
              />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-6 border-t border-gray-200">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSaving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ManualProfileEditor;