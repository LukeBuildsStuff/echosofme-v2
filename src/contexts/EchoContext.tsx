import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from './SupabaseAuthContext';

// Safe JSON parser to prevent crashes on invalid data
const safeJSONParse = <T,>(str: string | null, defaultValue: T): T => {
  if (!str) return defaultValue;
  try {
    return JSON.parse(str);
  } catch {
    return defaultValue;
  }
};

export interface Reflection {
  id: string;
  questionId: number;
  question: string;
  category: string;
  response: string;
  wordCount: number;
  qualityScore: number;
  createdAt: string;
  tags: string[];
}

export interface EchoStats {
  totalReflections: number;
  categoriesCovered: string[];
  averageWordCount: number;
  averageQualityScore: number;
  currentStreak: number;
  longestStreak: number;
  echoReadiness: number; // 0-100 percentage
}

export interface HistoricalStats {
  stats: EchoStats;
  timestamp: string;
}

export interface StatsChanges {
  totalReflectionsChange: number;
  categoriesCoveredChange: number;
  averageQualityScoreChange: number;
  currentStreakChange: number;
}

export interface EchoPersonality {
  name: string;
  description: string;
  dominantTraits: string[];
  communicationStyle: string;
  emotionalTone: string;
}

interface EchoContextType {
  // Reflections
  reflections: Reflection[];
  addReflection: (reflection: Omit<Reflection, 'id' | 'createdAt'>) => void;
  updateReflection: (id: string, updatedReflection: Partial<Reflection>) => Promise<void>;
  deleteReflection: (id: string, onSuccess?: (questionId: number, category: string) => void) => Promise<void>;
  getReflectionsByCategory: (category: string) => Reflection[];
  
  // Statistics
  stats: EchoStats;
  updateStats: () => void;
  getStatsChanges: () => StatsChanges;
  
  // Personality
  personality: EchoPersonality;
  updatePersonality: (traits: Partial<EchoPersonality>) => void;
  
  // Training
  isEchoReady: () => boolean;
  getNextMilestone: () => { target: number; description: string } | null;
  
  // Progress
  getCompletionPercentage: () => number;
  getDailyStreak: () => number;
}

const ECHO_TARGET = 2500; // Target number of reflections
const QUALITY_THRESHOLD = 0.6; // Minimum quality score for echo readiness
const READINESS_THRESHOLD = 0.8; // Minimum completion percentage for echo readiness

const MILESTONES = [
  { target: 50, description: "First steps taken! Your Echo is beginning to learn your voice." },
  { target: 100, description: "Foundation built! Your Echo understands your basic perspective." },
  { target: 250, description: "Personality emerging! Your Echo is developing your unique traits." },
  { target: 500, description: "Half-way there! Your Echo can now engage in meaningful conversations." },
  { target: 1000, description: "Major milestone! Your Echo has deep insight into your thoughts." },
  { target: 1500, description: "Advanced training! Your Echo captures your nuanced perspectives." },
  { target: 2000, description: "Nearly complete! Your Echo embodies your wisdom and experiences." },
  { target: 2500, description: "Echo complete! Your digital legacy is ready to share with loved ones." }
];

const EchoContext = createContext<EchoContextType | undefined>(undefined);

export const useEcho = () => {
  const context = useContext(EchoContext);
  if (context === undefined) {
    throw new Error('useEcho must be used within an EchoProvider');
  }
  return context;
};

interface EchoProviderProps {
  children: ReactNode;
}

// Helper function to get the Eleanor API URL
const getEleanorApiUrl = (): string => {
  // Check if we're running the Supabase API locally
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8001';
  }
  // For production, use your deployed Supabase API URL
  return 'https://your-api-domain.com'; // TODO: Replace with actual production URL
};

export const EchoProvider: React.FC<EchoProviderProps> = ({ children }) => {
  const { user, session } = useAuth();
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [stats, setStats] = useState<EchoStats>({
    totalReflections: 0,
    categoriesCovered: [],
    averageWordCount: 0,
    averageQualityScore: 0,
    currentStreak: 0,
    longestStreak: 0,
    echoReadiness: 0
  });
  const [previousStats, setPreviousStats] = useState<EchoStats | null>(null);
  const [personality, setPersonality] = useState<EchoPersonality>({
    name: 'Your Echo',
    description: 'Still learning your unique voice...',
    dominantTraits: [],
    communicationStyle: 'Developing',
    emotionalTone: 'Learning'
  });

  useEffect(() => {
    if (user?.email) {
      // Clear existing reflections when user changes
      setReflections([]);
      loadReflections();
    }
  }, [user?.email]);

  useEffect(() => {
    if (reflections.length > 0) {
      updateStats();
      updatePersonalityFromReflections();
    }
  }, [reflections]);

  useEffect(() => {
    if (user?.email) {
      loadPreviousStats();
    }
  }, [user?.email]);

  const loadReflections = async () => {
    try {
      if (!user?.id) {
        console.log('⚠️ No user ID available, skipping reflection loading');
        return;
      }

      // Clear old localStorage cache if it exists (one-time cleanup)
      const userSpecificKey = `echos_reflections_${user.email}`;
      const cacheVersionKey = `echos_cache_version_${user.email}`;
      const currentCacheVersion = '2024-09-17'; // Update when structure changes

      const storedVersion = localStorage.getItem(cacheVersionKey);
      if (storedVersion !== currentCacheVersion) {
        console.log('🧹 Clearing old cache version:', storedVersion, '-> updating to:', currentCacheVersion);
        localStorage.removeItem(userSpecificKey);
        localStorage.setItem(cacheVersionKey, currentCacheVersion);
      }

      const userId = parseInt(user.id);
      console.log('📊 Loading reflections from Supabase for user ID:', userId);

      if (isNaN(userId)) {
        console.error('❌ Invalid user ID - cannot convert to integer:', user.id);
        return;
      }

      // Use standard supabase client for all operations
      const client = supabase;

      console.log('🔧 Using standard client for reflections query');

      const { data: reflectionsData, error } = await client
        .from('reflections')
        .select(`
          *,
          questions (
            id,
            question_text,
            category
          )
        `)
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('❌ Error loading reflections from Supabase:', error);
        throw error;
      }

      if (reflectionsData) {
        console.log('✅ Successfully loaded reflections:', reflectionsData.length, 'items');

        // Convert database format to our interface format
        const convertedReflections: Reflection[] = reflectionsData.map((r: any) => ({
          id: r.id.toString(),
          questionId: r.question_id,
          question: r.questions?.question_text || '',
          category: r.questions?.category || 'general',
          response: r.response_text,
          wordCount: r.word_count || 0,
          qualityScore: calculateQualityScore(r.response_text, r.word_count || 0),
          createdAt: r.created_at,
          tags: []
        }));

        setReflections(convertedReflections);
      }
    } catch (error) {
      console.error('❌ Error loading reflections from database:', error);
      console.warn('⚠️  Database query failed - this may indicate a JavaScript error or network issue');

      // Only fall back to localStorage as a last resort
      console.log('🔄 Attempting fallback to localStorage...');
      try {
        const userSpecificKey = `echos_reflections_${user?.email}`;
        const saved = localStorage.getItem(userSpecificKey);
        if (saved) {
          const loadedReflections = safeJSONParse(saved, []);
          console.warn('⚠️  Using cached data from localStorage:', loadedReflections.length, 'items');
          console.warn('⚠️  This may not reflect your latest reflections. Check browser console for errors.');
          setReflections(loadedReflections);
        } else {
          console.error('❌ No cached data available - user will see 0 reflections');
          console.error('❌ This indicates a serious issue. Please check your internet connection and refresh the page.');
        }
      } catch (localError) {
        console.error('❌ Error loading from localStorage:', localError);
      }
    }
  };


  const calculateQualityScore = (text: string, wordCount: number): number => {
    // Simple quality scoring algorithm
    let score = 0.5; // Base score
    
    // Word count factor (longer responses generally better)
    if (wordCount > 50) score += 0.1;
    if (wordCount > 100) score += 0.1;
    if (wordCount > 200) score += 0.1;
    
    // Content indicators
    const depthIndicators = ['because', 'however', 'although', 'therefore', 'moreover', 'furthermore'];
    const personalIndicators = ['I feel', 'I believe', 'I think', 'my experience', 'in my opinion'];
    
    depthIndicators.forEach(indicator => {
      if (text.toLowerCase().includes(indicator)) score += 0.05;
    });
    
    personalIndicators.forEach(indicator => {
      if (text.toLowerCase().includes(indicator)) score += 0.05;
    });
    
    return Math.min(score, 1.0);
  };

  const addReflection = async (reflectionData: Omit<Reflection, 'id' | 'createdAt'>) => {
    try {
      if (!user?.id) {
        throw new Error('User ID not available');
      }

      const userId = parseInt(user.id);

      // Use standard supabase client for all operations
      const client = supabase;

      const { data: savedReflection, error } = await client
        .from('reflections')
        .insert({
          user_id: userId,
          question_id: reflectionData.questionId,
          response_text: reflectionData.response,
          word_count: reflectionData.wordCount,
          is_draft: false,
          response_type: reflectionData.category === 'journal' ? 'journal' : 'reflection'
        })
        .select()
        .single();

      if (error) {
        throw error;
      }

      if (savedReflection) {
        // Convert back to our format and add to local state
        const newReflection: Reflection = {
          id: savedReflection.id.toString(),
          questionId: savedReflection.question_id,
          question: reflectionData.question,
          category: reflectionData.category,
          response: savedReflection.response_text,
          wordCount: savedReflection.word_count,
          qualityScore: reflectionData.qualityScore,
          createdAt: savedReflection.created_at,
          tags: reflectionData.tags
        };

        setReflections(prev => [...prev, newReflection]);
      }
    } catch (error) {
      console.error('Error saving reflection to Supabase:', error);

      // Fallback to localStorage
      const newReflection: Reflection = {
        ...reflectionData,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
      };

      const updatedReflections = [...reflections, newReflection];
      try {
        const userSpecificKey = `echos_reflections_${user?.email}`;
        localStorage.setItem(userSpecificKey, JSON.stringify(updatedReflections));
        setReflections(updatedReflections);
      } catch (localError) {
        console.error('Error saving to localStorage:', localError);
      }
    }
  };

  const updateReflection = async (id: string, updatedReflection: Partial<Reflection>) => {
    try {
      if (!user?.email) {
        throw new Error('User email not available');
      }

      if (!session?.access_token) {
        throw new Error('Authentication session not available');
      }

      const userEmail = user.email;

      // Find the reflection to update
      const existingReflection = reflections.find(r => r.id === id);
      if (!existingReflection) {
        throw new Error('Reflection not found');
      }

      const apiUrl = getEleanorApiUrl();
      const response = await fetch(`${apiUrl}/reflections/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          user_email: userEmail,
          question_id: existingReflection.questionId,
          response_text: updatedReflection.response || existingReflection.response,
          word_count: updatedReflection.wordCount || existingReflection.wordCount,
          is_draft: false
        }),
      });

      if (response.ok) {
        const updatedData = await response.json();
        
        // Update the reflection in local state
        setReflections(prev => prev.map(r => 
          r.id === id 
            ? {
                ...r,
                response: updatedData.response_text,
                wordCount: updatedData.word_count,
                qualityScore: calculateQualityScore(updatedData.response_text, updatedData.word_count),
                ...updatedReflection
              }
            : r
        ));
      } else {
        throw new Error('Failed to update reflection');
      }
    } catch (error) {
      console.error('Error updating reflection:', error);
      throw error;
    }
  };

  const deleteReflection = async (id: string, onSuccess?: (questionId: number, category: string) => void) => {
    try {
      if (!user?.email) {
        throw new Error('User email not available');
      }
      
      // Find the reflection to get its questionId and category before deleting
      const reflectionToDelete = reflections.find(r => r.id === id);
      if (!reflectionToDelete) {
        throw new Error('Reflection not found');
      }
      
      // Check if this is a localStorage-only reflection (timestamp-based ID)
      const isLocalStorageOnly = /^\d{13}$/.test(id); // 13-digit timestamp
      
      if (isLocalStorageOnly) {
        console.log('🗑️ Deleting localStorage-only reflection:', id);
        
        // For localStorage-only reflections, skip API call
        // Call the success callback to unmark the question
        if (onSuccess) {
          onSuccess(reflectionToDelete.questionId, reflectionToDelete.category);
        }
        
        // Remove from local state
        setReflections(prev => prev.filter(r => r.id !== id));
        
        // Also update localStorage
        try {
          const userSpecificKey = `echos_reflections_${user.email}`;
          const updatedReflections = reflections.filter(r => r.id !== id);
          localStorage.setItem(userSpecificKey, JSON.stringify(updatedReflections));
        } catch (localError) {
          console.warn('Failed to update localStorage:', localError);
        }
      } else {
        // For API-saved reflections, use the API
        const userEmail = user.email;

        if (!session?.access_token) {
          throw new Error('Authentication session not available');
        }

        const apiUrl = getEleanorApiUrl();
        const response = await fetch(`${apiUrl}/reflections/${id}?user_email=${encodeURIComponent(userEmail)}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        });

        if (response.ok) {
          // Call the success callback to unmark the question
          if (onSuccess) {
            onSuccess(reflectionToDelete.questionId, reflectionToDelete.category);
          }
          
          // Remove the reflection from local state
          setReflections(prev => prev.filter(r => r.id !== id));
        } else if (response.status === 404) {
          // Reflection already deleted or doesn't exist - remove from local state anyway
          console.log('🗑️ Reflection not found in database (already deleted), removing from local state');
          
          // Call the success callback to unmark the question
          if (onSuccess) {
            onSuccess(reflectionToDelete.questionId, reflectionToDelete.category);
          }
          
          // Remove from local state since it's not in the database
          setReflections(prev => prev.filter(r => r.id !== id));
        } else {
          throw new Error('Failed to delete reflection from API');
        }
      }
    } catch (error) {
      console.error('Error deleting reflection:', error);
      throw error;
    }
  };

  const getReflectionsByCategory = (category: string): Reflection[] => {
    return reflections.filter(r => r.category === category);
  };

  const loadPreviousStats = () => {
    if (!user?.email) return;
    
    const userSpecificKey = `echos_stats_history_${user.email}`;
    const saved = localStorage.getItem(userSpecificKey);
    
    if (saved) {
      const history: HistoricalStats[] = safeJSONParse(saved, []);
      if (history.length > 0) {
        setPreviousStats(history[history.length - 1].stats);
      }
    }
  };

  const saveStatsHistory = (newStats: EchoStats) => {
    if (!user?.email) return;
    
    const userSpecificKey = `echos_stats_history_${user.email}`;
    const saved = localStorage.getItem(userSpecificKey);
    
    let history: HistoricalStats[] = [];
    if (saved) {
      history = safeJSONParse(saved, []);
    }
    
    // Save current stats as historical data
    const now = new Date().toISOString();
    const newHistoryEntry: HistoricalStats = {
      stats: newStats,
      timestamp: now
    };
    
    // Keep only last 30 entries to prevent localStorage bloat
    history.push(newHistoryEntry);
    if (history.length > 30) {
      history = history.slice(-30);
    }
    
    localStorage.setItem(userSpecificKey, JSON.stringify(history));
  };

  const updateStats = () => {
    const totalReflections = reflections.length;
    const categoriesCovered = [...new Set(reflections.map(r => r.category))];
    
    const averageWordCount = reflections.length > 0 
      ? reflections.reduce((sum, r) => sum + r.wordCount, 0) / reflections.length 
      : 0;
    
    const averageQualityScore = reflections.length > 0
      ? reflections.reduce((sum, r) => sum + r.qualityScore, 0) / reflections.length
      : 0;

    const echoReadiness = Math.min(
      (totalReflections / ECHO_TARGET) * 100,
      100
    );

    // Calculate streaks
    const { currentStreak, longestStreak } = calculateStreaks();

    const newStats = {
      totalReflections,
      categoriesCovered,
      averageWordCount,
      averageQualityScore,
      currentStreak,
      longestStreak,
      echoReadiness
    };

    // Save previous stats before updating
    if (stats.totalReflections > 0) {
      setPreviousStats(stats);
      saveStatsHistory(stats);
    }

    setStats(newStats);
  };

  const calculateStreaks = (): { currentStreak: number; longestStreak: number } => {
    if (reflections.length === 0) return { currentStreak: 0, longestStreak: 0 };

    // Group reflections by date
    const reflectionsByDate = reflections.reduce((acc, reflection) => {
      // Safety check: skip reflections without valid createdAt
      if (!reflection.createdAt || typeof reflection.createdAt !== 'string') {
        console.warn('Reflection missing createdAt:', reflection.id);
        return acc;
      }
      
      const date = reflection.createdAt.split('T')[0];
      if (!acc[date]) acc[date] = [];
      acc[date].push(reflection);
      return acc;
    }, {} as Record<string, Reflection[]>);

    const dates = Object.keys(reflectionsByDate).sort();
    
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 0;

    // Calculate current streak (from today backwards)
    const today = new Date().toISOString().split('T')[0];
    let checkDate = new Date();
    
    while (checkDate >= new Date(dates[0])) {
      const dateStr = checkDate.toISOString().split('T')[0];
      if (reflectionsByDate[dateStr]) {
        currentStreak++;
        tempStreak++;
      } else if (dateStr !== today) {
        break;
      }
      checkDate.setDate(checkDate.getDate() - 1);
    }

    // Calculate longest streak
    tempStreak = 0;
    for (let i = 0; i < dates.length; i++) {
      if (reflectionsByDate[dates[i]]) {
        tempStreak++;
        longestStreak = Math.max(longestStreak, tempStreak);
      } else {
        tempStreak = 0;
      }
    }

    return { currentStreak, longestStreak };
  };

  const updatePersonalityFromReflections = () => {
    if (reflections.length < 10) return; // Need minimum reflections to analyze personality

    // Analyze reflections to determine personality traits
    const traits: string[] = [];
    const categories = stats.categoriesCovered;

    if (categories.includes('philosophy_values')) {
      traits.push('Thoughtful');
    }
    if (categories.includes('family_parenting')) {
      traits.push('Family-oriented');
    }
    if (categories.includes('career')) {
      traits.push('Ambitious');
    }
    if (categories.includes('hobbies')) {
      traits.push('Creative');
    }
    if (stats.averageWordCount > 150) {
      traits.push('Expressive');
    }
    if (stats.currentStreak > 7) {
      traits.push('Dedicated');
    }

    let communicationStyle = 'Developing';
    if (stats.averageWordCount > 200) {
      communicationStyle = 'Detailed and thoughtful';
    } else if (stats.averageWordCount > 100) {
      communicationStyle = 'Clear and concise';
    }

    let description = 'Still learning your unique voice...';
    if (reflections.length > 100) {
      description = 'Beginning to capture your perspective and wisdom.';
    }
    if (reflections.length > 500) {
      description = 'Developing a strong understanding of your thoughts and values.';
    }
    if (reflections.length > 1000) {
      description = 'Well-trained in your communication style and perspectives.';
    }
    if (reflections.length >= ECHO_TARGET) {
      description = 'Complete digital representation of your voice and wisdom.';
    }

    setPersonality({
      name: reflections.length >= ECHO_TARGET ? 'Your Echo (Complete)' : 'Your Echo (Training)',
      description,
      dominantTraits: traits.slice(0, 4), // Top 4 traits
      communicationStyle,
      emotionalTone: stats.averageQualityScore > 0.8 ? 'Warm and genuine' : 'Learning to express'
    });
  };

  const updatePersonality = (traits: Partial<EchoPersonality>) => {
    setPersonality(prev => ({ ...prev, ...traits }));
  };

  const isEchoReady = (): boolean => {
    return stats.totalReflections >= ECHO_TARGET * READINESS_THRESHOLD &&
           stats.averageQualityScore >= QUALITY_THRESHOLD;
  };


  const getNextMilestone = (): { target: number; description: string } | null => {
    const nextMilestone = MILESTONES.find(m => m.target > stats.totalReflections);
    return nextMilestone || null;
  };

  const getCompletionPercentage = (): number => {
    return Math.min((stats.totalReflections / ECHO_TARGET) * 100, 100);
  };

  const getDailyStreak = (): number => {
    return stats.currentStreak;
  };

  const getStatsChanges = (): StatsChanges => {
    if (!previousStats) {
      return {
        totalReflectionsChange: 0,
        categoriesCoveredChange: 0,
        averageQualityScoreChange: 0,
        currentStreakChange: 0
      };
    }

    const totalReflectionsChange = previousStats.totalReflections > 0 
      ? ((stats.totalReflections - previousStats.totalReflections) / previousStats.totalReflections) * 100
      : 0;
      
    const categoriesCoveredChange = previousStats.categoriesCovered.length > 0
      ? ((stats.categoriesCovered.length - previousStats.categoriesCovered.length) / previousStats.categoriesCovered.length) * 100
      : 0;
      
    const averageQualityScoreChange = previousStats.averageQualityScore > 0
      ? ((stats.averageQualityScore - previousStats.averageQualityScore) / previousStats.averageQualityScore) * 100
      : 0;
      
    const currentStreakChange = previousStats.currentStreak > 0
      ? ((stats.currentStreak - previousStats.currentStreak) / previousStats.currentStreak) * 100
      : stats.currentStreak > 0 ? 100 : 0; // If streak went from 0 to something, that's 100% increase

    return {
      totalReflectionsChange: Math.round(totalReflectionsChange),
      categoriesCoveredChange: Math.round(categoriesCoveredChange),
      averageQualityScoreChange: Math.round(averageQualityScoreChange),
      currentStreakChange: Math.round(currentStreakChange)
    };
  };

  const value = {
    reflections,
    addReflection,
    updateReflection,
    deleteReflection,
    getReflectionsByCategory,
    stats,
    updateStats,
    getStatsChanges,
    personality,
    updatePersonality,
    isEchoReady,
    getNextMilestone,
    getCompletionPercentage,
    getDailyStreak,
  };

  return <EchoContext.Provider value={value}>{children}</EchoContext.Provider>;
};

export default EchoContext;