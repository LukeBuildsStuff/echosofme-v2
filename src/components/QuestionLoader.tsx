import { useState, useEffect } from 'react';
import questionsData from '../data/questions.json';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { getEleanorApiUrl } from '../utils/apiConfig';

export interface Question {
  id: number;
  question: string;
  category: string;
  source: string;
}

export interface QuestionCategory {
  name: string;
  count: number;
  color: string;
  icon: string;
}

const CATEGORIES: Record<string, QuestionCategory> = {
  hobbies: {
    name: 'Hobbies & Interests',
    count: 0,
    color: 'bg-purple-500',
    icon: '🎨'
  },
  education: {
    name: 'Education & Learning',
    count: 0,
    color: 'bg-blue-500',
    icon: '📚'
  },
  personal: {
    name: 'Personal Identity',
    count: 0,
    color: 'bg-indigo-500',
    icon: '🌟'
  },
  career: {
    name: 'Career & Work',
    count: 0,
    color: 'bg-green-500',
    icon: '💼'
  },
  personal_history: {
    name: 'Life History & Memories',
    count: 0,
    color: 'bg-orange-500',
    icon: '📖'
  },
  relationships: {
    name: 'Relationships',
    count: 0,
    color: 'bg-rose-500',
    icon: '❤️'
  },
  daily_life: {
    name: 'Daily Life & Routines',
    count: 0,
    color: 'bg-cyan-500',
    icon: '🏠'
  },
  philosophy_values: {
    name: 'Values & Philosophy',
    count: 0,
    color: 'bg-violet-500',
    icon: '🤔'
  },
  hypotheticals: {
    name: 'Fun & Hypotheticals',
    count: 0,
    color: 'bg-amber-500',
    icon: '🎯'
  },
  romantic_love: {
    name: 'Romance & Love',
    count: 0,
    color: 'bg-pink-500',
    icon: '💕'
  },
  marriage_partnerships: {
    name: 'Marriage & Partnerships',
    count: 0,
    color: 'bg-red-500',
    icon: '💑'
  },
  friendships_social: {
    name: 'Friendships & Social',
    count: 0,
    color: 'bg-teal-500',
    icon: '👥'
  },
  family_parenting: {
    name: 'Family & Parenting',
    count: 0,
    color: 'bg-lime-500',
    icon: '👨‍👩‍👧‍👦'
  },
  professional: {
    name: 'Professional Development',
    count: 0,
    color: 'bg-gray-500',
    icon: '🎯'
  },
  creative_expression: {
    name: 'Creative Expression',
    count: 0,
    color: 'bg-fuchsia-500',
    icon: '🎭'
  },
  journal: {
    name: 'Journal',
    count: 1,
    color: 'bg-yellow-500',
    icon: '📝'
  }
};

const useQuestionLoader = () => {
  const { user } = useAuth();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [categories, setCategories] = useState<Record<string, QuestionCategory>>(CATEGORIES);
  const [selectedQuestionsByCategory, setSelectedQuestionsByCategory] = useState<Record<string, Set<number>>>({});

  useEffect(() => {
    // Load questions and update category counts
    const loadedQuestions = questionsData as Question[];
    setQuestions(loadedQuestions);
    
    // Reset and update category counts
    const updatedCategories = { ...CATEGORIES };
    // Reset all counts to 0 first
    Object.keys(updatedCategories).forEach(cat => {
      updatedCategories[cat].count = 0;
    });
    
    // Count questions in each category
    loadedQuestions.forEach(q => {
      if (updatedCategories[q.category]) {
        updatedCategories[q.category].count++;
      }
    });
    
    setCategories(updatedCategories);
    
    // Initialize selected questions tracking with persistence
    const initialSelected: Record<string, Set<number>> = {};
    Object.keys(updatedCategories).forEach(cat => {
      initialSelected[cat] = new Set();
    });

    // Load answered questions from localStorage if user is available
    if (user?.email) {
      const userSpecificKey = `echos_answered_questions_${user.email.toLowerCase()}`;
      try {
        const savedAnswers = localStorage.getItem(userSpecificKey);
        if (savedAnswers) {
          const parsed = JSON.parse(savedAnswers);
          // Convert arrays back to Sets
          Object.keys(parsed).forEach(cat => {
            if (initialSelected[cat] && Array.isArray(parsed[cat])) {
              initialSelected[cat] = new Set(parsed[cat]);
            }
          });
        }
      } catch (error) {
        console.warn('Failed to load answered questions from localStorage:', error);
      }
    }
    
    setSelectedQuestionsByCategory(initialSelected);
    
    // Trigger sync if user is logged in
    if (user?.email) {
      // Sync after a short delay to let the component render first
      setTimeout(() => {
        syncAnsweredQuestions();
      }, 1000);
    }
  }, [user?.email]);

  // Sync answered questions from database to localStorage
  const syncAnsweredQuestions = async () => {
    if (!user?.email) return;
    
    try {
      console.log('🔄 Syncing answered questions from database...');
      const apiUrl = getEleanorApiUrl();
      const response = await fetch(`${apiUrl}/user/${encodeURIComponent(user.email)}/answered-questions`);
      
      if (response.ok) {
        const answeredByCategory = await response.json();
        
        // Convert arrays to Sets and update state
        const updated: Record<string, Set<number>> = {};
        Object.keys(CATEGORIES).forEach(cat => {
          updated[cat] = new Set(answeredByCategory[cat] || []);
        });
        
        // Update localStorage
        const userSpecificKey = `echos_answered_questions_${user.email.toLowerCase()}`;
        const toSave: Record<string, number[]> = {};
        Object.keys(updated).forEach(cat => {
          toSave[cat] = Array.from(updated[cat]);
        });
        localStorage.setItem(userSpecificKey, JSON.stringify(toSave));
        
        // Update state to trigger re-render
        setSelectedQuestionsByCategory(updated);
        
        const totalSynced = Object.values(updated).reduce((sum, set) => sum + set.size, 0);
        console.log(`✅ Synced ${totalSynced} answered questions across ${Object.keys(answeredByCategory).length} categories`);
      } else {
        console.warn('Failed to fetch answered questions:', response.status);
      }
    } catch (error) {
      console.error('Error syncing answered questions:', error);
    }
  };

  const getQuestionsByCategory = (category: string): Question[] => {
    return questions.filter(q => q.category === category);
  };

  // Helper functions for daily reflection scheduling
  const getCurrentReflectionPeriod = (): 'morning' | 'afternoon' | 'none' => {
    const now = new Date();
    const hour = now.getHours();
    
    if (hour >= 6 && hour < 15) return 'morning'; // 6 AM - 3 PM
    if (hour >= 15 && hour < 21) return 'afternoon'; // 3 PM - 9 PM
    return 'none';
  };

  const hasCompletedMorningReflection = (): boolean => {
    if (!user?.email) return false;
    
    const today = new Date().toDateString();
    const userSpecificKey = `echos_last_morning_reflection_${user.email}`;
    const lastMorning = localStorage.getItem(userSpecificKey);
    if (!lastMorning) return false;
    
    try {
      const data = JSON.parse(lastMorning);
      return data.date === today;
    } catch {
      return false;
    }
  };

  const hasCompletedAfternoonReflection = (): boolean => {
    if (!user?.email) return false;
    
    const today = new Date().toDateString();
    const userSpecificKey = `echos_last_afternoon_reflection_${user.email}`;
    const lastAfternoon = localStorage.getItem(userSpecificKey);
    if (!lastAfternoon) return false;
    
    try {
      const data = JSON.parse(lastAfternoon);
      return data.date === today;
    } catch {
      return false;
    }
  };

  // Hash function for consistent daily randomization
  const hashStringToNumber = (str: string): number => {
    let hash = 0;
    if (str.length === 0) return hash;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  };

  const getRecentlyAnsweredQuestionIds = (daysBack: number = 14): number[] => {
    // Get all answered question IDs from the last N days
    const recentIds: number[] = [];
    Object.values(selectedQuestionsByCategory).forEach(categorySet => {
      categorySet.forEach(id => recentIds.push(id));
    });
    return recentIds;
  };

  const getRandomizedQuestionIndex = (seed: string, excludeRecentIds: number[] = []): number => {
    // Filter out recently answered questions
    const recentlyAnswered = getRecentlyAnsweredQuestionIds();
    const allExcludedIds = [...excludeRecentIds, ...recentlyAnswered];
    
    const availableQuestions = questions.filter(q => !allExcludedIds.includes(q.id));
    
    if (availableQuestions.length === 0) {
      // If all questions are recent, fall back to all questions (but still avoid today's other period)
      const fallbackQuestions = questions.filter(q => !excludeRecentIds.includes(q.id));
      if (fallbackQuestions.length === 0) {
        return hashStringToNumber(seed) % questions.length;
      }
      const randomIndex = hashStringToNumber(seed) % fallbackQuestions.length;
      const selectedQuestion = fallbackQuestions[randomIndex];
      return questions.findIndex(q => q.id === selectedQuestion.id);
    }
    
    const randomIndex = hashStringToNumber(seed) % availableQuestions.length;
    const selectedQuestion = availableQuestions[randomIndex];
    return questions.findIndex(q => q.id === selectedQuestion.id);
  };

  const getDailyQuestion = (): Question | null => {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
    const seed = `${user?.email || 'anonymous'}-daily-${today}`;
    const questionIndex = getRandomizedQuestionIndex(seed);
    
    return questions[questionIndex] || null;
  };

  const getMorningQuestion = (): Question | null => {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format

    // CHECK LOCALSTORAGE FIRST - prevent question from changing mid-day
    if (user?.email) {
      const storageKey = `morning_question_${today}_${user.email}`;
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          // Find the stored question by ID
          const storedQuestion = questions.find(q => q.id === parsed.questionId);
          if (storedQuestion) {
            console.log('🔒 Using stored morning question:', storedQuestion.question.substring(0, 50) + '...');
            return storedQuestion;
          }
        } catch (e) {
          console.warn('Failed to parse stored morning question:', e);
        }
      }
    }

    // Check if we should prioritize a skipped question
    const skippedIds = getSkippedQuestions();
    let selectedQuestion: Question | null = null;

    if (shouldPrioritizeSkipped() && skippedIds.length > 0) {
      // Sort skipped questions by last skipped time (oldest first)
      const skippedData = getSkippedQuestionsData();
      const sortedSkippedIds = skippedIds.sort((a, b) => {
        const timeA = skippedData.lastSkipped[a] || '';
        const timeB = skippedData.lastSkipped[b] || '';
        return timeA.localeCompare(timeB);
      });

      // Try to find the oldest skipped question that's not the afternoon question
      const afternoonSeed = `${user?.email || 'anonymous'}-afternoon-${today}`;
      const afternoonIndex = getRandomizedQuestionIndex(afternoonSeed);
      const afternoonQuestionId = questions[afternoonIndex]?.id;

      for (const skippedId of sortedSkippedIds) {
        if (skippedId !== afternoonQuestionId) {
          selectedQuestion = questions.find(q => q.id === skippedId) || null;
          if (selectedQuestion) {
            console.log('📌 Prioritizing previously skipped question:', selectedQuestion.question.substring(0, 50) + '...');
            break;
          }
        }
      }
    }

    // If no skipped question was selected, use normal selection
    if (!selectedQuestion) {
      const seed = `${user?.email || 'anonymous'}-morning-${today}`;

      // Get afternoon question to avoid duplicating it
      const afternoonSeed = `${user?.email || 'anonymous'}-afternoon-${today}`;
      const afternoonIndex = getRandomizedQuestionIndex(afternoonSeed);
      const afternoonQuestionId = questions[afternoonIndex]?.id;

      const excludeIds = afternoonQuestionId ? [afternoonQuestionId] : [];
      const questionIndex = getRandomizedQuestionIndex(seed, excludeIds);

      selectedQuestion = questions[questionIndex] || null;
    }

    // STORE THE SELECTED QUESTION - lock it for the day
    if (selectedQuestion && user?.email) {
      const storageKey = `morning_question_${today}_${user.email}`;
      const toStore = {
        questionId: selectedQuestion.id,
        questionText: selectedQuestion.question,
        selectedAt: new Date().toISOString(),
        seed: `${user?.email || 'anonymous'}-morning-${today}`,
        previouslySkipped: skippedIds.includes(selectedQuestion.id)
      };
      localStorage.setItem(storageKey, JSON.stringify(toStore));
      console.log('💾 Stored morning question for', today, ':', selectedQuestion.question.substring(0, 50) + '...');
    }

    return selectedQuestion;
  };

  const getAfternoonQuestion = (): Question | null => {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format

    // CHECK LOCALSTORAGE FIRST - prevent question from changing mid-day
    if (user?.email) {
      const storageKey = `afternoon_question_${today}_${user.email}`;
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          // Find the stored question by ID
          const storedQuestion = questions.find(q => q.id === parsed.questionId);
          if (storedQuestion) {
            console.log('🔒 Using stored afternoon question:', storedQuestion.question.substring(0, 50) + '...');
            return storedQuestion;
          }
        } catch (e) {
          console.warn('Failed to parse stored afternoon question:', e);
        }
      }
    }

    // Check if we should prioritize a skipped question
    const skippedIds = getSkippedQuestions();
    let selectedQuestion: Question | null = null;

    if (shouldPrioritizeSkipped() && skippedIds.length > 0) {
      // Sort skipped questions by last skipped time (oldest first)
      const skippedData = getSkippedQuestionsData();
      const sortedSkippedIds = skippedIds.sort((a, b) => {
        const timeA = skippedData.lastSkipped[a] || '';
        const timeB = skippedData.lastSkipped[b] || '';
        return timeA.localeCompare(timeB);
      });

      // Try to find the oldest skipped question that's not the morning question
      const morningSeed = `${user?.email || 'anonymous'}-morning-${today}`;
      const morningIndex = getRandomizedQuestionIndex(morningSeed);
      const morningQuestionId = questions[morningIndex]?.id;

      for (const skippedId of sortedSkippedIds) {
        if (skippedId !== morningQuestionId) {
          selectedQuestion = questions.find(q => q.id === skippedId) || null;
          if (selectedQuestion) {
            console.log('📌 Prioritizing previously skipped question:', selectedQuestion.question.substring(0, 50) + '...');
            break;
          }
        }
      }
    }

    // If no skipped question was selected, use normal selection
    if (!selectedQuestion) {
      const seed = `${user?.email || 'anonymous'}-afternoon-${today}`;

      // Get morning question to avoid duplicating it
      const morningSeed = `${user?.email || 'anonymous'}-morning-${today}`;
      const morningIndex = getRandomizedQuestionIndex(morningSeed);
      const morningQuestionId = questions[morningIndex]?.id;

      const excludeIds = morningQuestionId ? [morningQuestionId] : [];
      const questionIndex = getRandomizedQuestionIndex(seed, excludeIds);

      selectedQuestion = questions[questionIndex] || null;
    }

    // STORE THE SELECTED QUESTION - lock it for the day
    if (selectedQuestion && user?.email) {
      const storageKey = `afternoon_question_${today}_${user.email}`;
      const toStore = {
        questionId: selectedQuestion.id,
        questionText: selectedQuestion.question,
        selectedAt: new Date().toISOString(),
        seed: `${user?.email || 'anonymous'}-afternoon-${today}`,
        previouslySkipped: skippedIds.includes(selectedQuestion.id)
      };
      localStorage.setItem(storageKey, JSON.stringify(toStore));
      console.log('💾 Stored afternoon question for', today, ':', selectedQuestion.question.substring(0, 50) + '...');
    }

    return selectedQuestion;
  };

  const getNextReflectionTime = (): { time: string; period: string } | null => {
    const now = new Date();
    const hour = now.getHours();
    
    if (hour < 6) {
      return { time: '6:00 AM', period: 'morning' };
    } else if (hour < 15) {
      if (!hasCompletedMorningReflection()) return null; // Morning is available now
      return { time: '3:00 PM', period: 'afternoon' };
    } else if (hour < 21) {
      if (!hasCompletedAfternoonReflection()) return null; // Afternoon is available now
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      return { time: '6:00 AM', period: 'morning' };
    } else {
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      return { time: '6:00 AM', period: 'morning' };
    }
  };

  const getRandomQuestionFromCategory = (category: string): Question | null => {
    // Special handling for journal category
    if (category === 'journal') {
      return {
        id: 5000,
        question: "What's on your mind today?",
        category: 'journal',
        source: 'journal'
      };
    }

    const categoryQuestions = getQuestionsByCategory(category);
    if (categoryQuestions.length === 0) return null;
    
    const randomIndex = Math.floor(Math.random() * categoryQuestions.length);
    return categoryQuestions[randomIndex];
  };

  const markQuestionAsAnswered = (questionId: number, category: string) => {
    setSelectedQuestionsByCategory(prev => {
      const updated = {
        ...prev,
        [category]: new Set([...(prev[category] || new Set()), questionId])
      };

      // Save to localStorage if user is available
      if (user?.email) {
        try {
          const userSpecificKey = `echos_answered_questions_${user.email.toLowerCase()}`;
          // Convert Sets to arrays for JSON storage
          const toSave: Record<string, number[]> = {};
          Object.keys(updated).forEach(cat => {
            toSave[cat] = Array.from(updated[cat]);
          });
          localStorage.setItem(userSpecificKey, JSON.stringify(toSave));
        } catch (error) {
          console.warn('Failed to save answered questions to localStorage:', error);
        }
      }

      return updated;
    });
  };

  const unmarkQuestionAsAnswered = (questionId: number, category: string) => {
    setSelectedQuestionsByCategory(prev => {
      const updated = {
        ...prev,
        [category]: new Set([...(prev[category] || new Set())].filter(id => id !== questionId))
      };

      // Save to localStorage if user is available
      if (user?.email) {
        try {
          const userSpecificKey = `echos_answered_questions_${user.email.toLowerCase()}`;
          // Convert Sets to arrays for JSON storage
          const toSave: Record<string, number[]> = {};
          Object.keys(updated).forEach(cat => {
            toSave[cat] = Array.from(updated[cat]);
          });
          localStorage.setItem(userSpecificKey, JSON.stringify(toSave));
        } catch (error) {
          console.warn('Failed to save answered questions to localStorage:', error);
        }
      }

      return updated;
    });
  };

  const getCategoryProgress = (category: string): number => {
    const totalQuestions = categories[category]?.count || 0;
    const answeredQuestions = selectedQuestionsByCategory[category]?.size || 0;
    return totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
  };

  const getTotalProgress = (): number => {
    const totalQuestions = questions.length;
    let answeredQuestions = 0;
    Object.values(selectedQuestionsByCategory).forEach(categorySet => {
      answeredQuestions += categorySet.size;
    });
    return totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
  };

  const getAnsweredCount = (): number => {
    let total = 0;
    Object.values(selectedQuestionsByCategory).forEach(categorySet => {
      total += categorySet.size;
    });
    return total;
  };

  const getRemainingCount = (category: string): number => {
    const totalQuestions = categories[category]?.count || 0;
    const answeredQuestions = selectedQuestionsByCategory[category]?.size || 0;
    return totalQuestions - answeredQuestions;
  };

  // Skipped questions management
  const getSkippedQuestionsData = (): { questionIds: number[], skipCounts: Record<number, number>, lastSkipped: Record<number, string> } => {
    if (!user?.email) return { questionIds: [], skipCounts: {}, lastSkipped: {} };

    const storageKey = `echos_skipped_questions_${user.email}`;
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.warn('Failed to load skipped questions:', e);
    }
    return { questionIds: [], skipCounts: {}, lastSkipped: {} };
  };

  const addToSkippedPool = (questionId: number) => {
    if (!user?.email) return;

    const storageKey = `echos_skipped_questions_${user.email}`;
    const data = getSkippedQuestionsData();

    // Add to pool if not already there
    if (!data.questionIds.includes(questionId)) {
      data.questionIds.push(questionId);
    }

    // Increment skip count
    data.skipCounts[questionId] = (data.skipCounts[questionId] || 0) + 1;

    // Update last skipped timestamp
    data.lastSkipped[questionId] = new Date().toISOString();

    localStorage.setItem(storageKey, JSON.stringify(data));
    console.log(`📋 Added question ${questionId} to skip pool. Total skipped: ${data.questionIds.length}`);
  };

  const removeFromSkippedPool = (questionId: number) => {
    if (!user?.email) return;

    const storageKey = `echos_skipped_questions_${user.email}`;
    const data = getSkippedQuestionsData();

    // Remove from pool
    data.questionIds = data.questionIds.filter(id => id !== questionId);

    // Clean up related data
    delete data.skipCounts[questionId];
    delete data.lastSkipped[questionId];

    localStorage.setItem(storageKey, JSON.stringify(data));
    console.log(`✅ Removed question ${questionId} from skip pool. Remaining: ${data.questionIds.length}`);
  };

  const getSkippedQuestions = (): number[] => {
    return getSkippedQuestionsData().questionIds;
  };

  const getSkippedQuestionsCount = (): number => {
    return getSkippedQuestionsData().questionIds.length;
  };

  const shouldPrioritizeSkipped = (): boolean => {
    // 30% chance to show a skipped question if any exist
    const skippedCount = getSkippedQuestionsCount();
    if (skippedCount === 0) return false;
    return Math.random() < 0.3;
  };

  const rerollMorningQuestion = (): Question | null => {
    const today = new Date().toISOString().split('T')[0];

    // Add current question to skip pool if it exists
    if (user?.email) {
      const storageKey = `morning_question_${today}_${user.email}`;
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed.questionId) {
            addToSkippedPool(parsed.questionId);
          }
        } catch (e) {
          console.warn('Failed to parse stored morning question:', e);
        }
      }
    }

    // Generate new seed with reroll counter
    const rerollCount = Math.random() * 1000000; // Random component for new selection
    const seed = `${user?.email || 'anonymous'}-morning-${today}-reroll-${rerollCount}`;

    // Get afternoon question to avoid duplicating it
    const afternoonSeed = `${user?.email || 'anonymous'}-afternoon-${today}`;
    const afternoonIndex = getRandomizedQuestionIndex(afternoonSeed);
    const afternoonQuestionId = questions[afternoonIndex]?.id;

    // Get all skipped questions
    const skippedIds = getSkippedQuestions();

    // Build exclude list (afternoon question + already skipped ones for this session)
    const excludeIds = [...skippedIds];
    if (afternoonQuestionId) excludeIds.push(afternoonQuestionId);

    const questionIndex = getRandomizedQuestionIndex(seed, excludeIds);
    const selectedQuestion = questions[questionIndex] || null;

    // Store the new question
    if (selectedQuestion && user?.email) {
      const storageKey = `morning_question_${today}_${user.email}`;
      const toStore = {
        questionId: selectedQuestion.id,
        questionText: selectedQuestion.question,
        selectedAt: new Date().toISOString(),
        seed: seed,
        isReroll: true,
        previouslySkipped: skippedIds.includes(selectedQuestion.id)
      };
      localStorage.setItem(storageKey, JSON.stringify(toStore));
      console.log('🔄 Rerolled morning question:', selectedQuestion.question.substring(0, 50) + '...');
    }

    return selectedQuestion;
  };

  const rerollAfternoonQuestion = (): Question | null => {
    const today = new Date().toISOString().split('T')[0];

    // Add current question to skip pool if it exists
    if (user?.email) {
      const storageKey = `afternoon_question_${today}_${user.email}`;
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed.questionId) {
            addToSkippedPool(parsed.questionId);
          }
        } catch (e) {
          console.warn('Failed to parse stored afternoon question:', e);
        }
      }
    }

    // Generate new seed with reroll counter
    const rerollCount = Math.random() * 1000000; // Random component for new selection
    const seed = `${user?.email || 'anonymous'}-afternoon-${today}-reroll-${rerollCount}`;

    // Get morning question to avoid duplicating it
    const morningSeed = `${user?.email || 'anonymous'}-morning-${today}`;
    const morningIndex = getRandomizedQuestionIndex(morningSeed);
    const morningQuestionId = questions[morningIndex]?.id;

    // Get all skipped questions
    const skippedIds = getSkippedQuestions();

    // Build exclude list (morning question + already skipped ones for this session)
    const excludeIds = [...skippedIds];
    if (morningQuestionId) excludeIds.push(morningQuestionId);

    const questionIndex = getRandomizedQuestionIndex(seed, excludeIds);
    const selectedQuestion = questions[questionIndex] || null;

    // Store the new question
    if (selectedQuestion && user?.email) {
      const storageKey = `afternoon_question_${today}_${user.email}`;
      const toStore = {
        questionId: selectedQuestion.id,
        questionText: selectedQuestion.question,
        selectedAt: new Date().toISOString(),
        seed: seed,
        isReroll: true,
        previouslySkipped: skippedIds.includes(selectedQuestion.id)
      };
      localStorage.setItem(storageKey, JSON.stringify(toStore));
      console.log('🔄 Rerolled afternoon question:', selectedQuestion.question.substring(0, 50) + '...');
    }

    return selectedQuestion;
  };

  // Check if current question was previously skipped
  const isQuestionPreviouslySkipped = (questionId: number): boolean => {
    const skippedIds = getSkippedQuestions();
    return skippedIds.includes(questionId);
  };

  return {
    questions,
    categories,
    getDailyQuestion,
    getMorningQuestion,
    getAfternoonQuestion,
    getQuestionsByCategory,
    getCurrentReflectionPeriod,
    hasCompletedMorningReflection,
    hasCompletedAfternoonReflection,
    getNextReflectionTime,
    getRandomQuestionFromCategory,
    markQuestionAsAnswered,
    unmarkQuestionAsAnswered,
    getCategoryProgress,
    getTotalProgress,
    getAnsweredCount,
    getRemainingCount,
    syncAnsweredQuestions,
    totalQuestions: questions.length,
    // New reroll functions
    rerollMorningQuestion,
    rerollAfternoonQuestion,
    getSkippedQuestionsCount,
    isQuestionPreviouslySkipped,
    removeFromSkippedPool
  };
};

export default useQuestionLoader;