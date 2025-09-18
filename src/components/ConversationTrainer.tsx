import React, { useState, useEffect } from 'react';
import { useEcho } from '../contexts/EchoContext';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { getEleanorApiUrl } from '../utils/apiConfig';

const CONVERSATION_OPENERS = [
  { id: 4000, text: "Hey, how are you?" },
  { id: 4001, text: "How was your day?" },
  { id: 4002, text: "What's up?" },
  { id: 4003, text: "How's it going?" },
  { id: 4004, text: "What's on your mind?" },
  { id: 4005, text: "Anything interesting happen today?" },
  { id: 4006, text: "What are you working on?" },
  { id: 4007, text: "How are you feeling?" },
  { id: 4008, text: "What's new?" },
  { id: 4009, text: "How's your week going?" }
];

const CATEGORY_KEYWORDS = {
  'career': ['work', 'job', 'meeting', 'boss', 'colleague', 'office', 'project', 'busy', 'deadline', 'client'],
  'family_parenting': ['kids', 'wife', 'husband', 'family', 'parents', 'children', 'son', 'daughter', 'mom', 'dad'],
  'daily_life': ['tired', 'sleep', 'morning', 'evening', 'home', 'today', 'routine', 'busy', 'relaxing', 'weekend'],
  'hobbies': ['gym', 'workout', 'running', 'reading', 'music', 'movie', 'game', 'hobby', 'fun', 'exercise'],
  'personal_history': ['remember', 'past', 'years ago', 'childhood', 'memory', 'used to', 'back then', 'growing up'],
  'philosophy_values': ['think', 'believe', 'important', 'values', 'meaning', 'purpose', 'right', 'wrong', 'philosophy'],
  'relationships': ['friend', 'relationship', 'love', 'dating', 'marriage', 'social', 'people', 'connection'],
  'education': ['school', 'learning', 'study', 'book', 'education', 'knowledge', 'course', 'university', 'college'],
  'life_milestones': ['graduation', 'wedding', 'birthday', 'achievement', 'milestone', 'celebration', 'anniversary'],
  'romantic_love': ['love', 'dating', 'romantic', 'relationship', 'partner', 'boyfriend', 'girlfriend', 'crush'],
  'marriage_partnerships': ['marriage', 'married', 'spouse', 'partner', 'together', 'relationship', 'couple']
};

const ConversationTrainer: React.FC = () => {
  const { user } = useAuth();
  const [currentQuestion, setCurrentQuestion] = useState<{ id: number; text: string } | null>(null);
  const [response, setResponse] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [lastQuestionId, setLastQuestionId] = useState<number | null>(null);

  // Get random opener question (avoid immediate repeats)
  const getRandomOpener = () => {
    let availableQuestions = CONVERSATION_OPENERS;
    
    // If we just answered a question, filter it out temporarily
    if (lastQuestionId !== null) {
      availableQuestions = CONVERSATION_OPENERS.filter(q => q.id !== lastQuestionId);
      
      // If we've run out of unique questions, reset
      if (availableQuestions.length === 0) {
        availableQuestions = CONVERSATION_OPENERS;
      }
    }
    
    const randomIndex = Math.floor(Math.random() * availableQuestions.length);
    return availableQuestions[randomIndex];
  };

  // Auto-categorize based on response content
  const categorizeBylContent = (text: string): string => {
    const lowerText = text.toLowerCase();
    
    for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
      for (const keyword of keywords) {
        if (lowerText.includes(keyword)) {
          return category;
        }
      }
    }
    
    // Default to daily_life if no specific category found
    return 'daily_life';
  };

  // Load initial question
  useEffect(() => {
    setCurrentQuestion(getRandomOpener());
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!response.trim() || !user?.email || !currentQuestion) return;

    setIsSubmitting(true);

    try {
      const wordCount = response.trim().split(/\s+/).length;
      const category = categorizeBylContent(response);

      console.log('🔄 Saving conversation:', {
        question_id: currentQuestion.id,
        response_text: response,
        word_count: wordCount,
        user_email: user.email
      });

      // Save conversation to API
      const apiUrl = getEleanorApiUrl();
      const saveResponse = await fetch(`${apiUrl}/reflections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_email: user.email,
          question_id: currentQuestion.id, // Use the actual question ID from database
          response_text: response,
          word_count: wordCount,
          is_draft: false,
          response_type: 'conversation'
        }),
      });

      console.log('📡 API Response status:', saveResponse.status);
      
      if (saveResponse.ok) {
        const savedData = await saveResponse.json();
        console.log('✅ Conversation saved successfully:', savedData);
        
        setShowSuccess(true);
        setResponse('');
        setLastQuestionId(currentQuestion.id); // Remember this question
        setCurrentQuestion(getRandomOpener()); // Load new question
        
        // Hide success message after 3 seconds
        setTimeout(() => setShowSuccess(false), 3000);
      } else {
        const errorData = await saveResponse.text();
        console.error('❌ API Error Response:', errorData);
        throw new Error(`API Error ${saveResponse.status}: ${errorData}`);
      }
    } catch (error) {
      console.error('💥 Error saving conversation:', error);
      alert(`Failed to save conversation: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNewQuestion = () => {
    setLastQuestionId(currentQuestion?.id || null);
    setCurrentQuestion(getRandomOpener());
    setResponse('');
  };

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      {/* Success Message */}
      {showSuccess && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-green-500 text-xl mr-3">✅</div>
            <div>
              <p className="text-green-800 font-medium">Conversation saved!</p>
              <p className="text-green-600 text-sm">Your Echo is learning natural responses.</p>
            </div>
          </div>
        </div>
      )}

      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Chat Training</h3>
        <p className="text-gray-600 text-sm mb-4">
          Practice natural conversations to teach your Echo how to respond casually. Keep it brief and natural - like texting a friend.
        </p>
      </div>

      {/* Chat Interface */}
      <div className="bg-gray-50 rounded-lg p-4 mb-4 max-h-96 overflow-y-auto">
        <div className="space-y-3">
          {/* Bot Message */}
          <div className="flex items-start">
            <div className="bg-gray-200 text-gray-800 rounded-lg px-3 py-2 max-w-xs">
              {currentQuestion?.text}
            </div>
          </div>

          {/* User Response (if typing) */}
          {response && (
            <div className="flex items-start justify-end">
              <div className="bg-primary text-white rounded-lg px-3 py-2 max-w-xs">
                {response}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Response Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            placeholder="Type your response..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={isSubmitting}
            autoFocus
          />
          <button
            type="submit"
            disabled={!response.trim() || isSubmitting || !currentQuestion}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? 'Saving...' : 'Send'}
          </button>
        </div>

        <div className="flex justify-between items-center text-sm">
          <div className="text-gray-500">
            Words: {response.trim().split(/\s+/).filter(w => w).length}
          </div>
          <button
            type="button"
            onClick={handleNewQuestion}
            className="text-primary hover:text-primary/80"
          >
            New Question
          </button>
        </div>
      </form>

      <div className="mt-4 text-xs text-gray-500">
        💡 Tip: Natural responses like "Good", "Pretty tired", or "Just working" are perfect for training conversational responses.
      </div>
    </div>
  );
};

export default ConversationTrainer;