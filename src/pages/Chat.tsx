import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import { useEcho } from '../contexts/EchoContext';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { isEleanorEnabled } from '../utils/apiConfig';
import AudioPlayer from '../components/AudioPlayer';
import { Volume2, VolumeX, AlertCircle } from 'lucide-react';
import SparkleLoader from '../components/SparkleLoader';

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
  const { user } = useAuth();
  const [selectedEcho, setSelectedEcho] = useState<Echo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [eleanorAvailable, setEleanorAvailable] = useState<boolean>(true);

  // Dynamic Echo description based on readiness
  const getEchoDescription = () => {
    if (isEchoReady()) {
      return 'Your complete digital reflection, trained from all your memories';
    } else {
      return `Your future digital self (${2500 - stats.totalReflections} more reflections to unlock)`;
    }
  };

  // All available Echos (base array)
  const allEchos: Echo[] = [
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
      description: getEchoDescription(),
      avatar: '🪞',
      isOwn: true
    }
  ];

  // Filter Echos based on admin status - only admins can see Eleanor
  const availableEchos: Echo[] = allEchos.filter(echo => {
    if (echo.id === 'eleanor' && !user?.isAdmin) {
      return false; // Hide Eleanor from non-admin users
    }
    return true; // Show all other Echos
  });

  // Dynamic greetings for Eleanor
  const eleanorGreetings = [
    "¡Hola, mijo! I was just thinking about you. How has your day been treating you?",
    "Ah, there you are! Come, sit with me. What's on your heart today?",
    "Hello, dear one. The house always feels warmer when we talk. What brings you to visit?",
    "¡Buenas! I was just remembering something that might make you smile. But first, how are you?",
    "My dear, perfect timing! I've been hoping we could chat. How are things going?",
    "Ah, mijo, you know what I always say - the best conversations happen over imaginary coffee. What shall we talk about?",
    "Hello, sweetheart. Sometimes the heart needs to speak. What's weighing on your mind?",
    "¡Qué bueno verte! You know, at my age, every conversation is a gift. What would you like to share?",
    "Hello, dear. I've lived long enough to know when someone needs to talk. I'm here to listen.",
    "Mija, come close. Tell me - what stories are you carrying today?"
  ];

  const getRandomEleanorGreeting = (): string => {
    return eleanorGreetings[Math.floor(Math.random() * eleanorGreetings.length)];
  };
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Voice features state
  const [voiceEnabled, setVoiceEnabled] = useState(() => {
    return localStorage.getItem('eleanor-voice-enabled') === 'true';
  });
  const [audioUrls, setAudioUrls] = useState<Map<string, string>>(new Map());
  const [generatingAudio, setGeneratingAudio] = useState<Set<string>>(new Set());

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check Eleanor availability on component mount
  useEffect(() => {
    try {
      const available = isEleanorEnabled();
      setEleanorAvailable(available);
    } catch (error) {
      setEleanorAvailable(false);
    }
  }, []);

  // Handle navigation state to auto-select Echo
  useEffect(() => {
    const state = location.state as { eleanorMessage?: string; selectedEchoId?: string };
    
    if (state?.eleanorMessage || state?.selectedEchoId === 'eleanor') {
      // Auto-select Eleanor if coming from popup or dashboard
      const eleanorEcho = availableEchos.find(echo => echo.id === 'eleanor');
      if (eleanorEcho) {
        setSelectedEcho(eleanorEcho);
        
        // Set initial message
        const initialMessage: Message = {
          id: '1',
          sender: 'echo',
          content: state.eleanorMessage || getRandomEleanorGreeting(),
          timestamp: new Date().toISOString(),
        };
        
        setMessages([initialMessage]);
      }
    }
  }, [location.state]);

  const selectEcho = (echo: Echo) => {
    // Don't allow selection if it's user's own Echo and it's not ready
    if (echo.isOwn && !isEchoReady()) {
      return;
    }

    setSelectedEcho(echo);

    // Set initial message based on selected Echo
    let echoMessage;
    if (echo.isOwn) {
      echoMessage = "Hello! I'm your Echo - your complete digital reflection. I've learned from all your reflections and I'm ready for deep conversations. What would you like to explore together?";
    } else {
      echoMessage = getRandomEleanorGreeting();
    }

    const initialMessage: Message = {
      id: '1',
      sender: 'echo',
      content: echoMessage,
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
      let response;
      let apiEndpoint;

      if (selectedEcho?.isOwn) {
        // Route to full Echo endpoint (only available when Echo is ready at 2500+ reflections)
        const userProfile = JSON.parse(localStorage.getItem('echos_user_profile') || '{}');
        const userEmail = userProfile.email || 'user@example.com';

        // For now, show placeholder message since full Echo isn't implemented yet
        throw new Error('Full Echo functionality coming soon! Complete 2500 reflections to unlock.');
      } else {
        // Check if Eleanor is available before attempting connection
        if (!eleanorAvailable) {
          throw new Error('Eleanor is only available when running the application locally with your RTX 5090 GPU.');
        }

        // Route to Eleanor endpoint
        const userProfile = JSON.parse(localStorage.getItem('echos_user_profile') || '{}');
        const contextualMessage = `${userProfile.displayName || 'User'} (${userProfile.profile?.relationship || 'Friend'}): ${inputMessage}`;

        // Detect question complexity for appropriate response length
        const isSimpleGreeting = /^(hi|hello|hey|good morning|buenos dias)[\s!?]*$/i.test(inputMessage);
        const isYesNoQuestion = /^(is |are |do |does |can |will |should |would |could ).*\?$/i.test(inputMessage);

        let maxResponseLength = 500; // default for complex questions
        if (isSimpleGreeting) maxResponseLength = 200;  // short for greetings
        else if (isYesNoQuestion) maxResponseLength = 300; // medium for yes/no

        apiEndpoint = '/eleanor/chat';
        console.log('💬 Sending chat message to Eleanor:', apiEndpoint);

        // Add timeout for mobile connections
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout for chat (mobile tunnel needs extra time)

        response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            message: contextualMessage,
            max_length: maxResponseLength,
            temperature: 0.7,
          }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
      }

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

  const toggleVoice = () => {
    const newVoiceEnabled = !voiceEnabled;
    setVoiceEnabled(newVoiceEnabled);
    localStorage.setItem('eleanor-voice-enabled', newVoiceEnabled.toString());
  };

  const generateTTS = async (messageId: string, text: string) => {
    // Only generate if not already generating or already has audio
    if (generatingAudio.has(messageId) || audioUrls.has(messageId)) return;
    
    try {
      setGeneratingAudio(prev => new Set(prev).add(messageId));
      
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          user_email: 'user@example.com'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAudioUrls(prev => new Map(prev).set(messageId, data.audio_url));
      } else {
        console.error('TTS request failed:', response.status);
      }
    } catch (error) {
      console.error('TTS generation failed:', error);
    } finally {
      setGeneratingAudio(prev => {
        const newSet = new Set(prev);
        newSet.delete(messageId);
        return newSet;
      });
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
            
            {/* Enhanced Progress Display for Non-Admin Users */}
            {!user?.isAdmin && availableEchos.length === 1 && (
              <div className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Reflection Journey</h2>
                  <p className="text-gray-600">Track your progress as you build your digital Echo</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-white rounded-lg p-4 shadow-sm border">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">{stats.totalReflections}</div>
                      <div className="text-sm text-gray-600">Total Reflections</div>
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm border">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">{Math.round((stats.totalReflections / 2500) * 100)}%</div>
                      <div className="text-sm text-gray-600">Echo Progress</div>
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm border">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-indigo-600">{2500 - stats.totalReflections}</div>
                      <div className="text-sm text-gray-600">Reflections Remaining</div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg p-4 border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Echo Training Progress</span>
                    <span className="text-sm text-gray-500">{stats.totalReflections} / 2500</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min((stats.totalReflections / 2500) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-600 mt-2">
                    {isEchoReady()
                      ? "🎉 Congratulations! Your Echo is fully trained and ready for conversations!"
                      : `Keep reflecting to unlock your personalized Echo! You're ${Math.round((stats.totalReflections / 2500) * 100)}% of the way there.`
                    }
                  </p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {availableEchos.map((echo) => {
                const isEchoDisabled = echo.isOwn && !isEchoReady();
                const isEleanorUnavailable = echo.id === 'eleanor' && !eleanorAvailable;
                const isDisabled = isEchoDisabled || isEleanorUnavailable;

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

                  {/* Eleanor unavailable message */}
                  {echo.id === 'eleanor' && !eleanorAvailable && (
                    <div className="rounded-lg p-3 bg-blue-50 border border-blue-200 mb-4">
                      <div className="flex items-start">
                        <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
                        <div>
                          <p className="text-blue-800 text-sm font-medium mb-1">
                            💻 Local Access Required
                          </p>
                          <p className="text-blue-700 text-xs">
                            Eleanor requires your RTX 5090 GPU and runs locally. To chat with Eleanor, please run the application on your local machine.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {echo.isOwn && (
                    <div className={`rounded-lg p-3 ${
                      isEchoReady()
                        ? 'bg-green-50 border border-green-200'
                        : 'bg-amber-50 border border-amber-200'
                    }`}>
                      {isEchoReady() ? (
                        <p className="text-green-800 text-sm">
                          <span className="font-medium">✨ Fully Trained:</span> Your Echo is complete with {stats.totalReflections} reflections!
                        </p>
                      ) : (
                        <div>
                          <p className="text-amber-800 text-sm mb-2">
                            <span className="font-medium">🔒 Not Ready Yet:</span> {2500 - stats.totalReflections} more reflections needed
                          </p>
                          <div className="w-full bg-amber-200 rounded-full h-2 mb-2">
                            <div
                              className="bg-amber-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${(stats.totalReflections / 2500) * 100}%` }}
                            ></div>
                          </div>
                          <p className="text-amber-700 text-xs">
                            Add {2500 - stats.totalReflections} more reflections to unlock your Echo!
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
            {/* Voice toggle button - only for Eleanor */}
            {selectedEcho.id === 'eleanor' && (
              <button
                onClick={toggleVoice}
                className="ml-4 p-2 rounded-lg border hover:bg-gray-50 transition-colors flex items-center space-x-2"
              >
                {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                <span className="text-sm">Voice {voiceEnabled ? 'On' : 'Off'}</span>
              </button>
            )}
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
                  {/* Speaker icon for Eleanor messages when voice is enabled */}
                  {message.sender === 'echo' && selectedEcho.id === 'eleanor' && voiceEnabled && (
                    <button
                      onClick={() => generateTTS(message.id, message.content)}
                      disabled={generatingAudio.has(message.id)}
                      className="mt-2 p-1 hover:bg-gray-100 rounded transition-colors inline-flex items-center"
                    >
                      {generatingAudio.has(message.id) ? (
                        <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Volume2 className="w-4 h-4 text-gray-500" />
                      )}
                    </button>
                  )}
                  <p className={`text-xs mt-2 ${
                    message.sender === 'user' ? 'text-white/70' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                {/* Audio player for generated TTS */}
                {audioUrls.has(message.id) && (
                  <div className="mt-2 max-w-xs lg:max-w-md">
                    <AudioPlayer audioUrl={audioUrls.get(message.id)!} compact={true} />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border rounded-lg p-2 shadow-sm">
                  <div className="flex items-center justify-center">
                    <SparkleLoader />
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