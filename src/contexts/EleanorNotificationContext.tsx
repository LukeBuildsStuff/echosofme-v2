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

// Eleanor message templates
const eleanorMessages = {
  morning: [
    "Good morning! How did you sleep?",
    "Morning! Ready to start the day?",
    "Hey there! Coffee time?",
    "Good morning! I was just thinking about you.",
    "Morning! Hope you're having a wonderful start to your day."
  ],
  afternoon: [
    "How's your day going so far?",
    "Taking a break? Want to chat?",
    "Just checking in on you!",
    "Afternoon! How are things?",
    "Hey! Perfect time for a quick chat."
  ],
  evening: [
    "How was your day?",
    "Evening! Time to unwind?",
    "Hey, want to reflect on today?",
    "Good evening! Ready to wind down?",
    "Evening check-in - how are you feeling?"
  ],
  followUp: [
    "I've been thinking about what you said yesterday...",
    "Remember what we talked about last time?",
    "Following up on our last conversation...",
    "That thing you mentioned has been on my mind...",
    "Hope that situation you told me about is going better."
  ],
  checkIn: [
    "Just wanted to see how you're doing.",
    "Thinking of you today!",
    "Hey there! What's on your mind?",
    "Quick check-in - how are you really doing?",
    "Something reminded me of you today."
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