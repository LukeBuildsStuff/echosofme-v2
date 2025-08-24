import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { getEleanorApiUrl } from '../utils/apiConfig';
import Layout from '../components/Layout/Layout';
import { useEcho } from '../contexts/EchoContext';

interface Echo {
  id: string;
  name: string;
  relationship: string;
  description: string;
  avatar: string;
  isOwn?: boolean;
}

interface Message {
  id: string;
  sender: 'user' | 'echo';
  content: string;
  timestamp: string;
}

const Chat: React.FC = () => {
  const location = useLocation();
  const { isEchoReady, stats } = useEcho();
  const [selectedEcho, setSelectedEcho] = useState<Echo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  // Mock data for available Echos
  const availableEchos: Echo[] = [
    {
      id: 'eleanor',
      name: 'Eleanor Rodriguez',
      relationship: 'Grandmother',
      description: 'Warm, caring grandmother with decades of life wisdom',
      avatar: '👵',
      isOwn: false
    },
    {
      id: 'my-echo',
      name: 'Your Echo',
      relationship: 'Self',
      description: 'Your personal digital reflection (in training)',
      avatar: '🪞',
      isOwn: true
    }
  ];
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const selectEcho = (echo: Echo) => {
    // Don't allow selection if it's user's own Echo and it's not ready
    if (echo.isOwn && !isEchoReady()) {
      return;
    }
    
    setSelectedEcho(echo);
    
    // Set initial message based on selected Echo
    const initialMessage: Message = {
      id: '1',
      sender: 'echo',
      content: echo.isOwn 
        ? "Hello! I'm your Echo - a digital reflection of yourself. I'm still learning from your reflections, but I'm here to help you explore your thoughts and memories. What would you like to talk about?"
        : `Hello! I'm ${echo.name}. I'm here to listen, chat, and help you reflect on your experiences. How are you feeling today?`,
      timestamp: new Date().toISOString(),
    };
    
    setMessages([initialMessage]);
  };

  const goBackToSelector = () => {
    setSelectedEcho(null);
    setMessages([]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Get user profile for context
      const userProfile = JSON.parse(localStorage.getItem('echos_user_profile') || '{}');
      const contextualMessage = `[User: ${userProfile.displayName || 'User'}, Relationship: ${userProfile.profile?.relationship || 'Friendly'}] ${inputMessage}`;

      const apiUrl = getEleanorApiUrl();
      console.log('💬 Sending chat message to:', `${apiUrl}/chat`);
      
      // Add timeout for mobile connections
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout for chat (mobile tunnel needs extra time)
      
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          message: contextualMessage,
          max_length: 350,
          temperature: 0.7,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Chat response received:', data.response?.substring(0, 50) + '...');
        const echoMessage: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'echo',
          content: data.response || "I'm sorry, I couldn't process that message.",
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, echoMessage]);
      } else {
        console.error('❌ Chat request failed. Status:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('❌ Error details:', errorText);
        throw new Error(`Failed to get response: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      let errorContent = "I'm having trouble connecting right now. Please try again in a moment.";
      
      if (error instanceof DOMException && error.name === 'AbortError') {
        errorContent = "The connection is taking too long. Please check your network and try again.";
      } else if (error instanceof TypeError) {
        errorContent = "Unable to reach the server. Please check your internet connection.";
      }
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'echo',
        content: errorContent,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Show Echo selector if no Echo is selected
  if (!selectedEcho) {
    return (
      <Layout hideFooter={true}>
        <div className="pt-20 min-h-screen bg-gray-50">
          <div className="max-w-4xl mx-auto px-6 py-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">Select which Echo to speak with</h1>
              <p className="text-gray-600">Choose an Echo to start your conversation</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {availableEchos.map((echo) => {
                const isDisabled = echo.isOwn && !isEchoReady();
                return (
                  <div
                    key={echo.id}
                    onClick={() => !isDisabled && selectEcho(echo)}
                    className={`bg-white rounded-lg p-6 shadow-sm border transition-all ${
                      isDisabled 
                        ? 'opacity-60 cursor-not-allowed' 
                        : 'hover:shadow-md hover:border-primary/20 cursor-pointer'
                    }`}
                  >
                  <div className="flex items-center mb-4">
                    <div className="text-4xl mr-4">{echo.avatar}</div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">{echo.name}</h3>
                      <p className="text-sm text-gray-500">{echo.relationship}</p>
                    </div>
                  </div>
                  <p className="text-gray-600 mb-4">{echo.description}</p>
                  {echo.isOwn && (
                    <div className={`rounded-lg p-3 ${
                      isEchoReady() 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-blue-50 border border-blue-200'
                    }`}>
                      {isEchoReady() ? (
                        <p className="text-green-800 text-sm">
                          <span className="font-medium">Ready:</span> Your Echo is fully trained and ready for conversations!
                        </p>
                      ) : (
                        <div>
                          <p className="text-blue-800 text-sm mb-2">
                            <span className="font-medium">Training Progress:</span> {Math.round(stats.echoReadiness)}% complete
                          </p>
                          <div className="w-full bg-blue-200 rounded-full h-2 mb-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                              style={{ width: `${stats.echoReadiness}%` }}
                            ></div>
                          </div>
                          <p className="text-blue-700 text-xs">
                            Continue adding reflections to train your Echo. Need {2500 - stats.totalReflections} more reflections.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                )
              })}
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout hideFooter={true}>
      <div className="pt-20 h-[100dvh] flex flex-col bg-gray-50">
        {/* Chat Header */}
        <div className="bg-white shadow-sm border-b px-4 py-3 sm:px-6 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button 
                onClick={goBackToSelector}
                className="mr-4 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
                </svg>
              </button>
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-2xl">
                  {selectedEcho.avatar}
                </div>
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">{selectedEcho.name}</h1>
                <p className="text-sm text-gray-500">{selectedEcho.relationship}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-3 sm:px-6 sm:py-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${
                  message.sender === 'user' 
                    ? 'bg-primary text-white' 
                    : 'bg-white border'
                } rounded-lg p-4 shadow-sm`}>
                  <p className="text-sm">{message.content}</p>
                  <p className={`text-xs mt-2 ${
                    message.sender === 'user' ? 'text-white/70' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border rounded-lg p-4 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Message Input */}
        <div className="bg-white border-t px-6 py-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex space-x-4">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Message ${selectedEcho.name}...`}
                className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent resize-none placeholder:text-sm"
                rows={1}
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Send
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Press Enter to send, Shift+Enter for a new line
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Chat;