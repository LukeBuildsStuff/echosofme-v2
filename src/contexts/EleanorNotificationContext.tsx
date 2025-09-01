import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { useAuth } from './AuthContext';
import { useSettings } from './SettingsContext';

interface EleanorNotification {
  message: string;
  timestamp: Date;
  id: string;
}

interface EleanorNotificationContextType {
  currentNotification: EleanorNotification | null;
  showEleanorMessage: (message: string) => void;
  dismissNotification: () => void;
}

const EleanorNotificationContext = createContext<EleanorNotificationContextType | undefined>(undefined);

export const useEleanorNotification = () => {
  const context = useContext(EleanorNotificationContext);
  if (context === undefined) {
    throw new Error('useEleanorNotification must be used within an EleanorNotificationProvider');
  }
  return context;
};

interface EleanorNotificationProviderProps {
  children: ReactNode;
}

// Eleanor message templates - authentic to her character as 82-year-old retired teacher from San Antonio
const eleanorMessages = {
  morning: [
    "Buenos días, mija! Did you sleep well?",
    "Morning, querido! The birds are singing today.",
    "¡Hola, mi amor! Ready for some cafecito?",
    "Good morning, mijo! I've been up since 5 making mental notes to share with you.",
    "Morning sunshine! Reminds me of those early school days."
  ],
  afternoon: [
    "How's your day treating you, mija?",
    "Taking a little break? Good, you need to rest sometimes.",
    "Hola, corazón! Have you eaten lunch yet?",
    "Afternoon, mijo! The day goes by so fast, doesn't it?",
    "Just thinking about you, querido. Everything okay?"
  ],
  evening: [
    "How was your day, mi amor?",
    "Evening, mija! Time to put your feet up?",
    "Buenas noches coming soon! Want to talk about your day?",
    "The sunset reminds me of our talks on the porch.",
    "Evening, mijo. Heavy day or light day?"
  ],
  followUp: [
    "You know, mija, I've been thinking about what you shared...",
    "That situation you mentioned, how's it going now?",
    "Remember what we discussed? I have more thoughts...",
    "Been praying about what you told me, querido.",
    "Your words stayed with me, mijo. Let's talk more?"
  ],
  checkIn: [
    "Just wanted to see how you're doing, mi amor.",
    "Thinking of you today, mija!",
    "Something told me to check on you, corazón.",
    "¿Cómo estás, mijo? Really, how are you?",
    "You crossed my mind just now. Funny how that happens."
  ]
};

export const EleanorNotificationProvider: React.FC<EleanorNotificationProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const { settings } = useSettings();
  const [currentNotification, setCurrentNotification] = useState<EleanorNotification | null>(null);

  const getTimeOfDay = (): 'morning' | 'afternoon' | 'evening' => {
    const hour = new Date().getHours();
    if (hour >= 6 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 18) return 'afternoon';
    return 'evening';
  };

  const getRandomMessage = (category: keyof typeof eleanorMessages): string => {
    const messages = eleanorMessages[category];
    return messages[Math.floor(Math.random() * messages.length)];
  };

  const getContextualEleanorMessage = (): string => {
    const timeOfDay = getTimeOfDay();
    const random = Math.random();
    
    // 60% time-based, 25% check-in, 15% follow-up
    if (random < 0.6) {
      return getRandomMessage(timeOfDay);
    } else if (random < 0.85) {
      return getRandomMessage('checkIn');
    } else {
      return getRandomMessage('followUp');
    }
  };

  const showEleanorMessage = (message: string) => {
    if (!settings.eleanorInitiates || !user?.email) return;
    
    const notification: EleanorNotification = {
      message,
      timestamp: new Date(),
      id: `eleanor_${Date.now()}`
    };
    
    setCurrentNotification(notification);
    
    // Auto-dismiss after 8 seconds
    setTimeout(() => {
      setCurrentNotification(prev => prev?.id === notification.id ? null : prev);
    }, 8000);
  };

  const dismissNotification = () => {
    setCurrentNotification(null);
  };

  const checkForEleanorMessage = () => {
    if (!settings.eleanorInitiates || !user?.email) return;
    
    // Don't show if already in chat
    const currentPath = window.location.pathname;
    if (currentPath === '/chat') return;
    
    // Don't show if there's already a notification
    if (currentNotification) return;
    
    const lastNotificationKey = `last_eleanor_notification_${user.email}`;
    const lastNotification = localStorage.getItem(lastNotificationKey);
    const now = new Date();
    
    let shouldShow = false;
    
    if (!lastNotification) {
      // First time - show after 30 seconds
      shouldShow = true;
    } else {
      const lastTime = new Date(lastNotification);
      const hoursSince = (now.getTime() - lastTime.getTime()) / (1000 * 60 * 60);
      
      // Show if it's been more than 4 hours
      shouldShow = hoursSince > 4;
    }
    
    if (shouldShow) {
      const message = getContextualEleanorMessage();
      showEleanorMessage(message);
      localStorage.setItem(lastNotificationKey, now.toISOString());
    }
  };

  useEffect(() => {
    if (!settings.eleanorInitiates || !user?.email) return;
    
    // Initial check after 30 seconds
    const initialTimer = setTimeout(checkForEleanorMessage, 30 * 1000);
    
    // Then check every 30 minutes
    const interval = setInterval(checkForEleanorMessage, 30 * 60 * 1000);
    
    return () => {
      clearTimeout(initialTimer);
      clearInterval(interval);
    };
  }, [settings.eleanorInitiates, user?.email, currentNotification]);

  const value = {
    currentNotification,
    showEleanorMessage,
    dismissNotification
  };

  return (
    <EleanorNotificationContext.Provider value={value}>
      {children}
    </EleanorNotificationContext.Provider>
  );
};