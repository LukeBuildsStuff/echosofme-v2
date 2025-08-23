import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import TrainingProgress from '../components/TrainingProgress';
import useQuestionLoader, { type Question } from '../components/QuestionLoader';
import { useEcho } from '../contexts/EchoContext';

const EnhancedReflections: React.FC = () => {
  const { categories, getDailyQuestion, getQuestionsByCategory } = useQuestionLoader();
  const { addReflection, stats } = useEcho();
  
  const [selectedCategory, setSelectedCategory] = useState<string>('daily');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [response, setResponse] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [viewMode, setViewMode] = useState<'daily' | 'category' | 'all'>('daily');

  useEffect(() => {
    if (viewMode === 'daily') {
      const dailyQ = getDailyQuestion();
      setCurrentQuestion(dailyQ);
    }
  }, [viewMode, getDailyQuestion]);

  const calculateQualityScore = (text: string): number => {
    const wordCount = text.trim().split(/\s+/).length;
    const minWords = 50;
    const targetWords = 200;
    
    // Base score from word count
    let score = Math.min(wordCount / targetWords, 1.0);
    
    // Penalty for very short responses
    if (wordCount < minWords) {
      score *= (wordCount / minWords);
    }
    
    // Bonus for depth indicators
    const depthIndicators = ['because', 'however', 'although', 'therefore', 'for example', 'specifically', 'particularly'];
    const depthCount = depthIndicators.filter(word => text.toLowerCase().includes(word)).length;
    score += Math.min(depthCount * 0.05, 0.2);
    
    // Bonus for personal pronouns (indicates personal reflection)
    const personalPronouns = text.match(/\b(i|my|me|myself|mine)\b/gi) || [];
    score += Math.min(personalPronouns.length * 0.01, 0.1);
    
    return Math.min(Math.max(score, 0.1), 1.0); // Ensure score is between 0.1 and 1.0
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentQuestion || !response.trim()) return;

    setIsSubmitting(true);
    
    try {
      const wordCount = response.trim().split(/\s+/).length;
      const qualityScore = calculateQualityScore(response);
      
      addReflection({
        questionId: currentQuestion.id,
        question: currentQuestion.question,
        category: currentQuestion.category,
        response: response.trim(),
        wordCount,
        qualityScore,
        tags: [] // Could add tag extraction later
      });

      // Show success message
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
      
      // Clear form
      setResponse('');
      
      // Load next question if in category mode
      if (viewMode === 'category') {
        const categoryQuestions = getQuestionsByCategory(selectedCategory);
        const randomQ = categoryQuestions[Math.floor(Math.random() * categoryQuestions.length)];
        setCurrentQuestion(randomQ);
      }
      
    } catch (error) {
      console.error('Error saving reflection:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    setViewMode('category');
    const categoryQuestions = getQuestionsByCategory(category);
    if (categoryQuestions.length > 0) {
      const randomQ = categoryQuestions[Math.floor(Math.random() * categoryQuestions.length)];
      setCurrentQuestion(randomQ);
    }
  };

  const getCategoryIcon = (category: string): string => {
    return categories[category]?.icon || '❓';
  };

  const getCategoryColor = (category: string): string => {
    return categories[category]?.color || 'bg-gray-500';
  };

  return (
    <Layout hideFooter={true}>
      <div className="min-h-screen bg-gray-50 pt-20">
        <div className="max-w-6xl mx-auto px-4 py-8">
          
          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Echo Training Center</h1>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Share your thoughts, experiences, and memories to train your personal Echo. 
              Each reflection makes your digital self more authentic and complete.
            </p>
          </div>

          <div className="flex flex-col lg:grid lg:grid-cols-3 gap-8">
            
            {/* Training Progress Sidebar - Order 2 on mobile (appears after main content) */}
            <div className="order-2 lg:order-1 lg:col-span-1">
              <TrainingProgress compact={false} />
              
              {/* Quick Stats */}
              <div className="mt-6 bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-3">Overall Progress</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Reflections completed:</span>
                    <span className="font-medium">{stats.totalReflections}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Average length:</span>
                    <span className="font-medium">{Math.round(stats.averageWordCount)} words</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Quality score:</span>
                    <span className="font-medium">{Math.round(stats.averageQualityScore * 100)}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content - Order 1 on mobile (appears first) */}
            <div className="order-1 lg:order-2 lg:col-span-2">
              
              {/* Success Message */}
              {showSuccess && (
                <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="text-green-500 text-xl mr-3">✅</div>
                    <div>
                      <p className="text-green-800 font-medium">Reflection saved successfully!</p>
                      <p className="text-green-600 text-sm">Your Echo is learning from your response.</p>
                    </div>
                  </div>
                </div>
              )}

              {/* View Mode Selector */}
              <div className="mb-6 bg-white rounded-lg p-4 shadow-sm">
                <div className="flex space-x-1">
                  <button
                    onClick={() => setViewMode('daily')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      viewMode === 'daily'
                        ? 'bg-primary text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    📅 Today's Question
                  </button>
                  <button
                    onClick={() => setViewMode('category')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      viewMode === 'category'
                        ? 'bg-primary text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    🗂️ By Category
                  </button>
                </div>
              </div>

              {/* Category Selection */}
              {viewMode === 'category' && (
                <div className="mb-6 bg-white rounded-lg p-6 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose a Category</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {Object.entries(categories)
                      .filter(([_, cat]) => cat.count > 0)
                      .sort(([,a], [,b]) => b.count - a.count)
                      .map(([key, category]) => (
                        <button
                          key={key}
                          onClick={() => handleCategorySelect(key)}
                          className={`p-3 rounded-lg border-2 transition-all ${
                            selectedCategory === key
                              ? 'border-primary bg-primary/10'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          <div className="text-2xl mb-1">{category.icon}</div>
                          <div className="text-sm font-medium text-gray-900">{category.name}</div>
                          <div className="text-xs text-gray-500">{category.count} questions</div>
                        </button>
                      ))}
                  </div>
                </div>
              )}

              {/* Question & Response Form */}
              {currentQuestion && (
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  
                  {/* Question Header */}
                  <div className="mb-6">
                    <div className="flex items-center mb-2">
                      <span className="text-2xl mr-2">{getCategoryIcon(currentQuestion.category)}</span>
                      <span className={`px-2 py-1 text-xs font-medium text-white rounded-full ${getCategoryColor(currentQuestion.category)}`}>
                        {categories[currentQuestion.category]?.name || currentQuestion.category}
                      </span>
                    </div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {currentQuestion.question}
                    </h2>
                  </div>

                  {/* Response Form */}
                  <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                      <label htmlFor="response" className="block text-sm font-medium text-gray-700 mb-2">
                        Your Reflection
                      </label>
                      <textarea
                        id="response"
                        value={response}
                        onChange={(e) => setResponse(e.target.value)}
                        placeholder="Take your time to reflect deeply. Share your thoughts, experiences, and emotions. The more authentic and detailed your response, the better your Echo will understand you."
                        rows={8}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                        required
                      />
                      
                      {/* Word Counter */}
                      <div className="flex justify-between mt-2 text-sm text-gray-500">
                        <span>{response.trim().split(/\s+/).filter(word => word).length} words</span>
                        <span className={`${
                          response.trim().split(/\s+/).filter(word => word).length >= 50 
                            ? 'text-green-600' 
                            : 'text-amber-600'
                        }`}>
                          {response.trim().split(/\s+/).filter(word => word).length >= 50 
                            ? 'Good length ✓' 
                            : 'Try for at least 50 words'}
                        </span>
                      </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-between items-center">
                      <button
                        type="button"
                        onClick={() => setResponse('')}
                        disabled={isSubmitting}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
                      >
                        Clear
                      </button>
                      
                      <button
                        type="submit"
                        disabled={isSubmitting || !response.trim()}
                        className="px-6 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {isSubmitting ? 'Saving...' : 'Save Reflection'}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {!currentQuestion && (
                <div className="bg-white rounded-lg p-6 shadow-sm text-center">
                  <div className="text-4xl mb-4">🤔</div>
                  <p className="text-gray-600">Select a category to start reflecting, or try today's question!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default EnhancedReflections;