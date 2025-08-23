import { useState, useEffect } from 'react';
import questionsData from '../data/questions.json';

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
  career: {
    name: 'Career & Work',
    count: 0,
    color: 'bg-green-500',
    icon: '💼'
  },
  personal: {
    name: 'Personal Growth',
    count: 0,
    color: 'bg-indigo-500',
    icon: '🌱'
  },
  family_parenting: {
    name: 'Family & Parenting',
    count: 0,
    color: 'bg-rose-500',
    icon: '👨‍👩‍👧‍👦'
  },
  friendships_social: {
    name: 'Friendships & Social',
    count: 0,
    color: 'bg-amber-500',
    icon: '👥'
  },
  romantic_love: {
    name: 'Love & Romance',
    count: 0,
    color: 'bg-pink-500',
    icon: '💕'
  },
  daily_life: {
    name: 'Daily Life',
    count: 0,
    color: 'bg-cyan-500',
    icon: '🏠'
  },
  personal_history: {
    name: 'Personal History',
    count: 0,
    color: 'bg-orange-500',
    icon: '📖'
  },
  philosophy_values: {
    name: 'Values & Philosophy',
    count: 0,
    color: 'bg-violet-500',
    icon: '🤔'
  },
  life_milestones: {
    name: 'Life Milestones',
    count: 0,
    color: 'bg-emerald-500',
    icon: '🏆'
  }
};

const useQuestionLoader = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [categories, setCategories] = useState<Record<string, QuestionCategory>>(CATEGORIES);
  const [selectedQuestionsByCategory, setSelectedQuestionsByCategory] = useState<Record<string, Set<number>>>({});

  useEffect(() => {
    // Load questions and update category counts
    const loadedQuestions = questionsData as Question[];
    setQuestions(loadedQuestions);
    
    // Update category counts
    const updatedCategories = { ...CATEGORIES };
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

  const getDailyQuestion = (): Question | null => {
    // Simple algorithm: use date to determine which question to show
    const today = new Date();
    const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
    const questionIndex = dayOfYear % questions.length;
    
    return questions[questionIndex] || null;
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

  return {
    questions,
    categories,
    getDailyQuestion,
    getQuestionsByCategory,
    getRandomQuestionFromCategory,
    markQuestionAsAnswered,
    getCategoryProgress,
    getTotalProgress,
    getAnsweredCount,
    totalQuestions: questions.length
  };
};

export default useQuestionLoader;