import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/SupabaseAuthContext';
import SparkleLoader from './SparkleLoader';
import onboardingBotImage from '../assets/images/onboarding-bot.png';

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
  quickReplies?: string[];
}

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

type ConversationStage =
  | 'personal'
  | 'partner'
  | 'partner_name'
  | 'partner_anniversary'
  | 'children_check'
  | 'children_loop'
  | 'children_dob'
  | 'children_another'
  | 'father'
  | 'father_dob'
  | 'mother'
  | 'mother_dob'
  | 'step_parents'
  | 'mentors'
  | 'profession'
  | 'education'
  | 'spiritual'
  | 'anniversaries'
  | 'important_dates'
  | 'complete';

interface ProfileChatProps {
  onCompletionChange?: (isCompleted: boolean) => void;
}

const ProfileChat: React.FC<ProfileChatProps> = ({ onCompletionChange }) => {
  const { user, updateProfile } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentStage, setCurrentStage] = useState<ConversationStage>('personal');
  const [personalQuestionIndex, setPersonalQuestionIndex] = useState(0);
  const [currentChildIndex, setCurrentChildIndex] = useState(0);
  const [profileData, setProfileData] = useState<ProfileData>({
    full_name: '',
    nickname: '',
    dob: '',
    location: '',
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
    profession: '',
    education: '',
    spiritual_background: '',
    anniversaries: [],
    important_dates: []
  });
  const [isCompleted, setIsCompleted] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasInitialized = useRef(false);
  const hasReset = useRef(false);

  // Reset function to restart the conversation
  const resetConversation = () => {
    console.log('🔄 ProfileChat: Resetting conversation for profile update');
    setMessages([]);
    setCurrentInput('');
    setIsTyping(false);
    setCurrentStage('personal');
    setPersonalQuestionIndex(0);
    setCurrentChildIndex(0);
    setProfileData({
      full_name: '',
      nickname: '',
      dob: '',
      location: '',
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
      profession: '',
      education: '',
      spiritual_background: '',
      anniversaries: [],
      important_dates: []
    });
    setIsCompleted(false);
    setIsSaving(false);
    hasReset.current = true;
    // Keep hasInitialized.current = true to prevent infinite loop

    // Start the conversation with a welcome back message
    setTimeout(() => {
      addBotMessage("Welcome back! Let's update your profile information. I'll go through the questions again so you can review and update your answers.");
      setTimeout(() => {
        addBotMessage("Let's start by confirming your full name - is it still correct or would you like to update it?");
      }, 1500);
    }, 500);
  };

  const personalQuestions = [
    { text: "Hi! I'm here to help you complete your profile. Let's start simple - what's your full name?", field: 'full_name' },
    { text: "Great! Do you go by a nickname or prefer something different than your full name?", field: 'nickname', quickReplies: ['Just use my full name', 'Skip this'] },
    { text: "When's your birthday? You can tell me in any format you like.", field: 'dob', quickReplies: ['Skip this'] },
    { text: "What city or region do you live in?", field: 'location', quickReplies: ['Skip this'] }
  ];

  useEffect(() => {
    // Check if profile is already completed when component mounts
    if (user?.profile?.introduction && !hasInitialized.current && !hasReset.current) {
      try {
        const existingData = JSON.parse(user.profile.introduction);
        // Check if we have a complete profile structure
        if (existingData.personal && existingData.relationships && existingData.life) {
          console.log('✅ ProfileChat: Existing completed profile detected, starting reset conversation');
          hasInitialized.current = true;
          resetConversation();
          return;
        }
      } catch (error) {
        console.warn('ProfileChat: Failed to parse existing profile data:', error);
      }
    }

    // Start normal conversation for new profile
    if (messages.length === 0 && !hasInitialized.current && user && !hasReset.current) {
      hasInitialized.current = true;
      addBotMessage(personalQuestions[0].text);
    }
  }, [user?.profile?.introduction, messages.length, user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (onCompletionChange) {
      onCompletionChange(isCompleted);
    }
  }, [isCompleted, onCompletionChange]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addBotMessage = (text: string, quickReplies: string[] = []) => {
    setIsTyping(true);
    setTimeout(() => {
      const message: Message = {
        id: Date.now().toString(),
        text,
        isBot: true,
        timestamp: new Date(),
        quickReplies
      };
      setMessages(prev => [...prev, message]);
      setIsTyping(false);
    }, 800 + Math.random() * 1200);
  };

  const addUserMessage = (text: string) => {
    const message: Message = {
      id: Date.now().toString(),
      text,
      isBot: false,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;

    addUserMessage(text);
    setCurrentInput('');
    processUserResponse(text);
  };

  const processUserResponse = (response: string) => {
    console.log('🔄 Processing response:', response, 'Stage:', currentStage);

    const isSkip = response.toLowerCase().includes('skip') || response.toLowerCase().includes('just use');

    switch (currentStage) {
      case 'personal':
        handlePersonalQuestions(response, isSkip);
        break;
      case 'partner':
        handlePartnerQuestion(response);
        break;
      case 'partner_name':
        handlePartnerName(response, isSkip);
        break;
      case 'partner_anniversary':
        handlePartnerAnniversary(response, isSkip);
        break;
      case 'children_check':
        handleChildrenCheck(response);
        break;
      case 'children_loop':
        handleChildName(response);
        break;
      case 'children_dob':
        handleChildDob(response, isSkip);
        break;
      case 'children_another':
        handleAnotherChild(response);
        break;
      case 'father':
        handleFatherName(response, isSkip);
        break;
      case 'father_dob':
        handleFatherDob(response, isSkip);
        break;
      case 'mother':
        handleMotherName(response, isSkip);
        break;
      case 'mother_dob':
        handleMotherDob(response, isSkip);
        break;
      case 'step_parents':
        handleStepParents(response);
        break;
      case 'mentors':
        handleMentors(response);
        break;
      case 'profession':
        handleProfession(response, isSkip);
        break;
      case 'education':
        handleEducation(response, isSkip);
        break;
      case 'spiritual':
        handleSpiritual(response, isSkip);
        break;
      case 'anniversaries':
        handleAnniversaries(response);
        break;
      case 'important_dates':
        handleImportantDates(response);
        break;
    }
  };

  const handlePersonalQuestions = (response: string, isSkip: boolean) => {
    const currentQ = personalQuestions[personalQuestionIndex];

    if (!isSkip) {
      if (currentQ.field === 'nickname' && response.toLowerCase().includes('just use')) {
        // Use full name as nickname
        setProfileData(prev => ({
          ...prev,
          nickname: prev.full_name
        }));
      } else {
        setProfileData(prev => ({
          ...prev,
          [currentQ.field]: response
        }));
      }
    }

    if (personalQuestionIndex < personalQuestions.length - 1) {
      const nextIndex = personalQuestionIndex + 1;
      setPersonalQuestionIndex(nextIndex);
      setTimeout(() => {
        addBotMessage(personalQuestions[nextIndex].text, personalQuestions[nextIndex].quickReplies || []);
      }, 1000);
    } else {
      // Move to partner questions
      setCurrentStage('partner');
      setTimeout(() => {
        addBotMessage("Now let's talk about your close relationships. Are you married or in a partnership?", ['Yes', 'No', 'It\'s complicated']);
      }, 1000);
    }
  };

  const handlePartnerQuestion = (response: string) => {
    const hasPartner = response.toLowerCase().includes('yes') || response.toLowerCase().includes('married') || response.toLowerCase().includes('partnership');

    setProfileData(prev => ({
      ...prev,
      has_partner: hasPartner
    }));

    if (hasPartner) {
      setCurrentStage('partner_name');
      setTimeout(() => {
        addBotMessage("What's your spouse or partner's name?", ['Skip this']);
      }, 1000);
    } else {
      moveToChildren();
    }
  };

  const handlePartnerName = (response: string, isSkip: boolean) => {
    if (!isSkip) {
      setProfileData(prev => ({
        ...prev,
        partner_name: response
      }));
    }

    setCurrentStage('partner_anniversary');
    setTimeout(() => {
      addBotMessage("Do you want me to remember your anniversary? If so, what's the date?", ['Skip this', 'We don\'t celebrate it']);
    }, 1000);
  };

  const handlePartnerAnniversary = (response: string, isSkip: boolean) => {
    if (!isSkip && !response.toLowerCase().includes('don\'t')) {
      setProfileData(prev => ({
        ...prev,
        partner_anniversary: response
      }));
    }

    moveToChildren();
  };

  const moveToChildren = () => {
    setCurrentStage('children_check');
    setTimeout(() => {
      addBotMessage("Do you have children?", ['Yes', 'No']);
    }, 1000);
  };

  const handleChildrenCheck = (response: string) => {
    const hasChildren = response.toLowerCase().includes('yes');

    setProfileData(prev => ({
      ...prev,
      has_children: hasChildren
    }));

    if (hasChildren) {
      setCurrentChildIndex(0);
      setCurrentStage('children_loop');
      setTimeout(() => {
        addBotMessage("What's your first child's name?");
      }, 1000);
    } else {
      moveToParents();
    }
  };

  const handleChildName = (response: string) => {
    const newChild: Child = { name: response, dob: '' };

    setProfileData(prev => ({
      ...prev,
      children: [...prev.children, newChild]
    }));

    setCurrentStage('children_dob');
    setTimeout(() => {
      addBotMessage(`When is ${response}'s birthday?`, ['Skip this']);
    }, 1000);
  };

  const handleChildDob = (response: string, isSkip: boolean) => {
    if (!isSkip) {
      setProfileData(prev => {
        const updatedChildren = [...prev.children];
        updatedChildren[currentChildIndex].dob = response;
        return {
          ...prev,
          children: updatedChildren
        };
      });
    }

    setCurrentStage('children_another');
    setTimeout(() => {
      addBotMessage("Do you have another child?", ['Yes', 'No']);
    }, 1000);
  };

  const handleAnotherChild = (response: string) => {
    if (response.toLowerCase().includes('yes')) {
      setCurrentChildIndex(prev => prev + 1);
      setCurrentStage('children_loop');
      setTimeout(() => {
        addBotMessage(`What's your ${currentChildIndex + 2}${getOrdinalSuffix(currentChildIndex + 2)} child's name?`);
      }, 1000);
    } else {
      moveToParents();
    }
  };

  const moveToParents = () => {
    setCurrentStage('father');
    setTimeout(() => {
      addBotMessage("Now let's talk about your parents. What's your father's name?", ['Skip this', 'Prefer not to say']);
    }, 1000);
  };

  const handleFatherName = (response: string, isSkip: boolean) => {
    if (!isSkip) {
      setProfileData(prev => ({
        ...prev,
        father_name: response
      }));
    }

    setCurrentStage('father_dob');
    setTimeout(() => {
      const name = isSkip ? "your father" : response;
      addBotMessage(`When is ${name}'s birthday?`, ['Skip this', 'He has passed away']);
    }, 1000);
  };

  const handleFatherDob = (response: string, isSkip: boolean) => {
    if (!isSkip && !response.toLowerCase().includes('passed')) {
      setProfileData(prev => ({
        ...prev,
        father_dob: response
      }));
    }

    setCurrentStage('mother');
    setTimeout(() => {
      addBotMessage("What's your mother's name?", ['Skip this', 'Prefer not to say']);
    }, 1000);
  };

  const handleMotherName = (response: string, isSkip: boolean) => {
    if (!isSkip) {
      setProfileData(prev => ({
        ...prev,
        mother_name: response
      }));
    }

    setCurrentStage('mother_dob');
    setTimeout(() => {
      const name = isSkip ? "your mother" : response;
      addBotMessage(`When is ${name}'s birthday?`, ['Skip this', 'She has passed away']);
    }, 1000);
  };

  const handleMotherDob = (response: string, isSkip: boolean) => {
    if (!isSkip && !response.toLowerCase().includes('passed')) {
      setProfileData(prev => ({
        ...prev,
        mother_dob: response
      }));
    }

    setCurrentStage('step_parents');
    setTimeout(() => {
      addBotMessage("Do you have step-parents you'd like me to remember?", ['Yes', 'No']);
    }, 1000);
  };

  const handleStepParents = (response: string) => {
    if (response.toLowerCase().includes('yes')) {
      // For now, skip step-parents loop - would need more complex state management
      setTimeout(() => {
        addBotMessage("I'll add step-parent tracking in the next update. For now, let's continue.");
        moveToMentors();
      }, 1000);
    } else {
      moveToMentors();
    }
  };

  const moveToMentors = () => {
    setCurrentStage('mentors');
    setTimeout(() => {
      addBotMessage("Would you like me to remember a close friend or mentor?", ['Yes', 'No']);
    }, 1000);
  };

  const handleMentors = (response: string) => {
    if (response.toLowerCase().includes('yes')) {
      // For now, skip mentors loop - would need more complex state management
      setTimeout(() => {
        addBotMessage("I'll add mentor tracking in the next update. Let's move to your professional life.");
        moveToProfession();
      }, 1000);
    } else {
      moveToProfession();
    }
  };

  const moveToProfession = () => {
    setCurrentStage('profession');
    setTimeout(() => {
      addBotMessage("What's your current profession or career field?", ['Retired', 'Student', 'Between jobs', 'Skip this']);
    }, 1000);
  };

  const handleProfession = (response: string, isSkip: boolean) => {
    if (!isSkip) {
      setProfileData(prev => ({
        ...prev,
        profession: response
      }));
    }

    setCurrentStage('education');
    setTimeout(() => {
      addBotMessage("Where did you go to school, if anywhere you'd like me to remember?", ['Skip this']);
    }, 1000);
  };

  const handleEducation = (response: string, isSkip: boolean) => {
    if (!isSkip) {
      setProfileData(prev => ({
        ...prev,
        education: response
      }));
    }

    setCurrentStage('spiritual');
    setTimeout(() => {
      addBotMessage("Do you follow a religious or spiritual tradition?", ['Skip this', 'Not religious']);
    }, 1000);
  };

  const handleSpiritual = (response: string, isSkip: boolean) => {
    if (!isSkip) {
      setProfileData(prev => ({
        ...prev,
        spiritual_background: response
      }));
    }

    setCurrentStage('anniversaries');
    setTimeout(() => {
      addBotMessage("Do you want me to remember any anniversaries? (wedding, recovery, other milestones)", ['Yes', 'No']);
    }, 1000);
  };

  const handleAnniversaries = (response: string) => {
    if (response.toLowerCase().includes('yes')) {
      setTimeout(() => {
        addBotMessage("I'll add anniversary tracking in the next update. Almost done!");
        moveToImportantDates();
      }, 1000);
    } else {
      moveToImportantDates();
    }
  };

  const moveToImportantDates = () => {
    setCurrentStage('important_dates');
    setTimeout(() => {
      addBotMessage("Are there other important dates you'd like saved?", ['Yes', 'No']);
    }, 1000);
  };

  const handleImportantDates = (response: string) => {
    if (response.toLowerCase().includes('yes')) {
      setTimeout(() => {
        addBotMessage("I'll add important dates tracking in the next update. Let me save your profile now!");
        completeProfile();
      }, 1000);
    } else {
      completeProfile();
    }
  };

  const completeProfile = () => {
    setCurrentStage('complete');
    setTimeout(() => {
      addBotMessage("Perfect! I've collected your information. Let me save your profile...");
      saveProfile();
    }, 1000);
  };

  const saveProfile = async () => {
    setIsSaving(true);

    try {
      console.log('💾 Saving complete profile data:', profileData);

      // Create a structured profile object
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
          mother_dob: profileData.mother_dob
        },
        life: {
          profession: profileData.profession,
          education: profileData.education,
          spiritual_background: profileData.spiritual_background
        },
        collected_at: new Date().toISOString()
      };

      // Create a human-readable summary for the introduction
      const introduction = `${profileData.full_name || 'User'} from ${profileData.location || 'somewhere'}. ${profileData.profession ? `Works as ${profileData.profession}.` : ''}${profileData.has_partner && profileData.partner_name ? ` Married to ${profileData.partner_name}.` : ''}${profileData.has_children ? ` Has ${profileData.children.length} child${profileData.children.length > 1 ? 'ren' : ''}.` : ''}`.trim();

      // Save the complete profile as JSON in introduction field for now
      // Later we can properly structure this in the database
      const saveData = {
        displayName: profileData.nickname || profileData.full_name || '',
        introduction: JSON.stringify(completeProfile)
      };

      console.log('💾 Saving to database:', saveData);

      await updateProfile(saveData);

      setIsCompleted(true);
      addBotMessage("🎉 All done! Your complete profile has been saved. You can always update this information later. The data is safely stored and will help create a more personalized experience for your Echo.");

    } catch (error) {
      console.error('❌ Failed to save profile:', error);
      addBotMessage("Oops! There was an issue saving your profile. Please try again later or contact support if this continues happening.");
    } finally {
      setIsSaving(false);
    }
  };

  const getOrdinalSuffix = (num: number): string => {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return 'st';
    if (j === 2 && k !== 12) return 'nd';
    if (j === 3 && k !== 13) return 'rd';
    return 'th';
  };

  const handleQuickReply = (reply: string) => {
    handleSendMessage(reply);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getProgressPercentage = (): number => {
    const stages = ['personal', 'partner', 'children_check', 'father', 'mother', 'profession', 'education', 'spiritual', 'complete'];
    const currentIndex = stages.indexOf(currentStage);
    return Math.max(0, Math.min(100, (currentIndex / (stages.length - 1)) * 100));
  };

  if (isCompleted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <div className="text-green-600 text-4xl mb-4">✅</div>
        <h3 className="text-lg font-semibold text-green-800 mb-2">Profile Complete!</h3>
        <p className="text-green-700 mb-4">Your comprehensive profile has been saved successfully.</p>
        <div className="text-sm text-green-600">
          Collected: Name, Location, Relationships, Family, Career & Personal Details
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Chat Header */}
      <div className="bg-primary text-white px-4 py-3 flex items-center">
        <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center mr-3">
          <img src={onboardingBotImage} alt="Profile Assistant" className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">Profile Assistant</h3>
          <p className="text-primary-light text-sm">Building your comprehensive profile</p>
        </div>
        <div className="text-right">
          <div className="bg-white/20 rounded-full px-3 py-1 text-xs mb-1">
            {Math.round(getProgressPercentage())}% Complete
          </div>
          <div className="w-16 h-1 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-white transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.isBot
                  ? 'bg-gray-100 text-gray-800'
                  : 'bg-primary text-white'
              }`}
            >
              <p className="text-sm">{message.text}</p>
              <p className={`text-xs mt-1 ${message.isBot ? 'text-gray-500' : 'text-primary-light'}`}>
                {formatTime(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-lg flex items-center">
              <SparkleLoader size="small" />
            </div>
          </div>
        )}

        {/* Quick Replies */}
        {messages.length > 0 && messages[messages.length - 1]?.isBot && messages[messages.length - 1]?.quickReplies && !isTyping && (
          <div className="flex flex-wrap gap-2">
            {messages[messages.length - 1].quickReplies?.map((reply, index) => (
              <button
                key={index}
                onClick={() => handleQuickReply(reply)}
                className="bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-300 transition-colors"
              >
                {reply}
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(currentInput)}
            placeholder="Type your response..."
            disabled={isTyping || isSaving}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
          />
          <button
            onClick={() => handleSendMessage(currentInput)}
            disabled={isTyping || isSaving || !currentInput.trim()}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? '💾' : '📤'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileChat;