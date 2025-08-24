import { useState, useEffect } from 'react';
import questionsData from '../data/questions.json';
import { useAuth } from '../contexts/AuthContext';

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
  personal_identity: {
    name: 'Personal Identity & Character',
    count: 0,
    color: 'bg-indigo-500',
    icon: '🌟'
  },
  memories_experiences: {
    name: 'Memories & Life Experiences',
    count: 0,
    color: 'bg-orange-500',
    icon: '📖'
  },
  daily_life: {
    name: 'Daily Life & Routines',
    count: 0,
    color: 'bg-cyan-500',
    icon: '🏠'
  },
  relationships_all: {
    name: 'Relationships & Social',
    count: 0,
    color: 'bg-rose-500',
    icon: '❤️'
  },
  values_philosophy: {
    name: 'Values & Philosophy',
    count: 0,
    color: 'bg-violet-500',
    icon: '🤔'
  },
  career_purpose: {
    name: 'Career & Purpose',
    count: 0,
    color: 'bg-green-500',
    icon: '💼'
  },
  interests_passions: {
    name: 'Interests & Passions',
    count: 0,
    color: 'bg-purple-500',
    icon: '🎨'
  },
  education_learning: {
    name: 'Education & Learning',
    count: 0,
    color: 'bg-blue-500',
    icon: '📚'
  },
  dreams_aspirations: {
    name: 'Dreams & Aspirations',
    count: 0,
    color: 'bg-emerald-500',
    icon: '✨'
  },
  fun_hypotheticals: {
    name: 'Fun & Hypotheticals',
    count: 0,
    color: 'bg-amber-500',
    icon: '🎯'
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
    
    // Initialize selected questions tracking
    const initialSelected: Record<string, Set<number>> = {};
    Object.keys(updatedCategories).forEach(cat => {
      initialSelected[cat] = new Set();
    });
    setSelectedQuestionsByCategory(initialSelected);
  }, []);

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

  const getDailyQuestion = (): Question | null => {
    // Simple algorithm: use date to determine which question to show
    const today = new Date();
    const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
    const questionIndex = dayOfYear % questions.length;
    
    return questions[questionIndex] || null;
  };

  const getMorningQuestion = (): Question | null => {
    // Use date + "morning" seed for consistent morning questions
    const today = new Date();
    const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
    const morningIndex = (dayOfYear * 2) % questions.length; // Different from afternoon
    
    return questions[morningIndex] || null;
  };

  const getAfternoonQuestion = (): Question | null => {
    // Use date + "afternoon" seed for different afternoon questions
    const today = new Date();
    const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
    const afternoonIndex = (dayOfYear * 2 + 1) % questions.length; // Different from morning
    
    return questions[afternoonIndex] || null;
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
    const categoryQuestions = getQuestionsByCategory(category);
    if (categoryQuestions.length === 0) return null;
    
    const randomIndex = Math.floor(Math.random() * categoryQuestions.length);
    return categoryQuestions[randomIndex];
  };

  const markQuestionAsAnswered = (questionId: number, category: string) => {
    setSelectedQuestionsByCategory(prev => ({
      ...prev,
      [category]: new Set([...prev[category], questionId])
    }));
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
    getCategoryProgress,
    getTotalProgress,
    getAnsweredCount,
    getRemainingCount,
    totalQuestions: questions.length
  };
};

export default useQuestionLoader;