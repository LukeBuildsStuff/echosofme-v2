import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import useQuestionLoader, { type Question } from '../components/QuestionLoader';
import { useEcho } from '../contexts/EchoContext';
import { useToast } from '../contexts/ToastContext';

const Reflections: React.FC = () => {
  const location = useLocation();
  const { getDailyQuestion, getRandomQuestionFromCategory } = useQuestionLoader();
  const { addReflection } = useEcho();
  const { showSuccess, showError } = useToast();
  
  const [reflection, setReflection] = useState({
    title: '',
    content: '',
    mood: '',
    tags: '',
  });
  
  const [currentQuestions, setCurrentQuestions] = useState<Question[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  const refreshQuestions = useCallback(() => {
    setIsLoadingQuestions(true);
    try {
      const dailyQ = getDailyQuestion();
      const randomQuestions: Question[] = [];
      const usedIds = new Set<number>();
      
      // Add daily question first if it exists
      if (dailyQ) {
        usedIds.add(dailyQ.id);
      }
      
      // Get 4 random questions from different categories, avoiding duplicates
      const categories = ['personal', 'family_parenting', 'philosophy_values', 'daily_life'];
      categories.forEach(category => {
        let attempts = 0;
        while (attempts < 10) { // Prevent infinite loop
          const randomQ = getRandomQuestionFromCategory(category);
          if (randomQ && !usedIds.has(randomQ.id)) {
            randomQuestions.push(randomQ);
            usedIds.add(randomQ.id);
            break;
          }
          attempts++;
        }
      });
      
      const allQuestions = dailyQ ? [dailyQ, ...randomQuestions] : randomQuestions;
      setCurrentQuestions(allQuestions.slice(0, 5)); // Limit to 5 questions
    } catch (error) {
      console.error('Error loading questions:', error);
      setCurrentQuestions([]);
    } finally {
      setIsLoadingQuestions(false);
    }
  }, [getDailyQuestion, getRandomQuestionFromCategory]);

  useEffect(() => {
    // Check if we got a selected question from navigation (e.g., from Dashboard)
    const questionFromNav = location.state?.selectedQuestion;
    if (questionFromNav) {
      setSelectedQuestion(questionFromNav);
    }
    
    // Initialize with some random questions
    refreshQuestions();
  }, [location.state, refreshQuestions]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setReflection({
      ...reflection,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isSaving) return; // Prevent multiple submissions

    setIsSaving(true);

    try {
      // Add timeout wrapper for the save operation
      const saveWithTimeout = Promise.race([
        (async () => {
          // Calculate word count and quality score
          const wordCount = reflection.content.trim().split(/\s+/).length;

          // Create reflection data in the format expected by EchoContext
          const reflectionData = {
            questionId: selectedQuestion?.id || 0,
            question: selectedQuestion?.question || 'Free reflection',
            category: selectedQuestion?.category || 'general',
            response: reflection.content,
            wordCount,
            qualityScore: 0.8, // Will be calculated by EchoContext
            tags: reflection.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          };

          // Save using EchoContext which handles API and localStorage fallback
          await addReflection(reflectionData);
        })(),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Save operation timed out')), 30000)
        )
      ]);

      await saveWithTimeout;

      // Reset form on successful save
      setReflection({
        title: '',
        content: '',
        mood: '',
        tags: '',
      });

      // Clear selected question
      setSelectedQuestion(null);

      showSuccess('Reflection saved!', 'Your reflection has been saved successfully.');
    } catch (error) {
      console.error('Failed to save reflection:', error);
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      showError('Save failed', `Failed to save reflection: ${errorMessage}. Please try again.`);
    } finally {
      setIsSaving(false);
    }
  };

  const rollForNewQuestions = useCallback(() => {
    refreshQuestions();
  }, [refreshQuestions]);

  return (
    <Layout hideFooter={true}>
      <div className="pt-20 min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Daily Reflections</h1>
            <p className="text-gray-600">Take a moment to reflect on your day and capture your thoughts.</p>
          </div>

          <div className="flex flex-col lg:grid lg:grid-cols-3 gap-8">
            {/* Reflection Form - Order 2 on mobile (appears after sidebar), Order 1 on desktop */}
            <div className="order-2 lg:order-1 lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Today's Reflection</h2>
                
                {/* Selected Question Display - Always visible at top */}
                {selectedQuestion && (
                  <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-purple-900 mb-2">Reflecting on:</p>
                        <p className="text-lg font-medium text-purple-800 leading-relaxed">{selectedQuestion.question}</p>
                        <span className="inline-block text-xs bg-purple-200 text-purple-800 px-2 py-1 rounded mt-3">
                          {selectedQuestion.category.replace('_', ' ')}
                        </span>
                      </div>
                      <button
                        onClick={() => setSelectedQuestion(null)}
                        className="text-purple-400 hover:text-purple-600 p-2 ml-4 hover:bg-purple-100 rounded-lg transition-colors"
                        title="Clear question"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                )}
                
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                      Title (Optional)
                    </label>
                    <input
                      type="text"
                      id="title"
                      name="title"
                      value={reflection.title}
                      onChange={handleChange}
                      placeholder="Give your reflection a title..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label htmlFor="mood" className="block text-sm font-medium text-gray-700 mb-2">
                      How are you feeling?
                    </label>
                    <select
                      id="mood"
                      name="mood"
                      value={reflection.mood}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    >
                      <option value="">Select your mood...</option>
                      <option value="great">Great 😊</option>
                      <option value="good">Good 🙂</option>
                      <option value="okay">Okay 😐</option>
                      <option value="difficult">Difficult 😔</option>
                      <option value="challenging">Challenging 😤</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                      Your Reflection *
                    </label>
                    <textarea
                      id="content"
                      name="content"
                      value={reflection.content}
                      onChange={handleChange}
                      required
                      rows={8}
                      placeholder="Share your thoughts, feelings, experiences, or anything that's on your mind..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                    />
                  </div>

                  <div>
                    <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
                      Tags (Optional)
                    </label>
                    <input
                      type="text"
                      id="tags"
                      name="tags"
                      value={reflection.tags}
                      onChange={handleChange}
                      placeholder="e.g. gratitude, family, work, growth (separate with commas)"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={!reflection.content.trim() || isSaving}
                      className="bg-primary text-white px-8 py-3 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                      {isSaving && (
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      )}
                      {isSaving ? 'Saving...' : 'Save Reflection'}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Sidebar - Order 1 on mobile (appears first), Order 2 on desktop */}
            <div className="order-1 lg:order-2 space-y-6">
              {/* Reflection Prompts */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">Reflection Prompts</h3>
                    <p className="text-xs text-gray-500 mt-1">Click questions to add them to your reflection</p>
                  </div>
                  <button
                    onClick={rollForNewQuestions}
                    disabled={isLoadingQuestions}
                    className="bg-primary text-white px-4 py-2 rounded-lg transition-all duration-300 hover:scale-105 active:scale-95 hover:bg-primary/90 min-h-[44px] min-w-[44px] flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shrink-0 ml-4 border border-primary-dark shadow-md"
                    style={{backgroundColor: '#6366F1'}}
                    title="Roll for new random questions!"
                  >
                    <svg 
                      className={`w-5 h-5 ${isLoadingQuestions ? 'animate-spin' : ''}`} 
                      fill="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      {isLoadingQuestions ? (
                        <path d="M12 2v4m0 12v4m8.485-15.485l-2.829 2.829M5.344 18.656l-2.829 2.829M20 12h-4M8 12H4m13.314-5.314l-2.829-2.829m-8.485 8.485l-2.829 2.829" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none"/>
                      ) : (
                        <path d="M5 3a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2H5zm0 2h14v14H5V5zm2 2a1 1 0 100 2 1 1 0 000-2zm6 0a1 1 0 100 2 1 1 0 000-2zm-6 6a1 1 0 100 2 1 1 0 000-2zm6 0a1 1 0 100 2 1 1 0 000-2zm-6 6a1 1 0 100 2 1 1 0 000-2zm6 0a1 1 0 100 2 1 1 0 000-2z"/>
                      )}
                    </svg>
                    <span className="text-sm font-medium">Roll</span>
                  </button>
                </div>
                
                <div className="space-y-3">
                  {isLoadingQuestions ? (
                    <div className="text-center py-8">
                      <div className="inline-flex items-center gap-2 text-gray-500">
                        <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span className="text-sm">Loading new questions...</span>
                      </div>
                    </div>
                  ) : (
                    <>
                      {currentQuestions.map((question) => (
                        <div 
                          key={question.id}
                          className="p-3 bg-blue-50 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors group"
                          onClick={() => {
                            setReflection(prev => ({
                              ...prev,
                              content: prev.content + (prev.content ? '\n\n' : '') + `Question: ${question.question}\n\nAnswer: `
                            }));
                            setSelectedQuestion(question);
                          }}
                        >
                          <p className="text-sm text-blue-900">{question.question}</p>
                          <span className="inline-block text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            {question.category.replace('_', ' ')}
                          </span>
                        </div>
                      ))}
                      
                      {currentQuestions.length === 0 && (
                        <div className="text-center py-4 text-gray-500">
                          <p className="text-sm">No questions available. Try clicking the Roll button!</p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Quick Stats */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Your Progress</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">This Week</span>
                    <span className="font-semibold text-primary">3 reflections</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">This Month</span>
                    <span className="font-semibold text-primary">12 reflections</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total</span>
                    <span className="font-semibold text-primary">89 reflections</span>
                  </div>
                  <div className="pt-2 border-t">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">5-day streak!</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Reflections */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Recent Reflections</h3>
                <div className="space-y-3">
                  <div className="pb-3 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">Gratitude Practice</p>
                    <p className="text-xs text-gray-500">Yesterday • Good mood</p>
                  </div>
                  <div className="pb-3 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">Weekend Adventures</p>
                    <p className="text-xs text-gray-500">2 days ago • Great mood</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Learning From Challenges</p>
                    <p className="text-xs text-gray-500">3 days ago • Difficult mood</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Reflections;