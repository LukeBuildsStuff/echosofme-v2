import React, { useState, useRef, useEffect } from 'react'
import { getEleanorApiUrl } from '../utils/apiConfig'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Volume2, VolumeX } from 'lucide-react'
import AudioPlayer from './AudioPlayer'
import SparkleLoader from './SparkleLoader'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  audioUrl?: string
  isGeneratingAudio?: boolean
}

interface PersonalityMode {
  id: string
  name: string
  description: string
  systemPrompt: string
}

const personalityModes: PersonalityMode[] = [
  {
    id: 'eleanor',
    name: 'Eleanor Echo',
    description: 'Warm grandmother figure sharing wisdom and comfort',
    systemPrompt: `You are Eleanor Rodriguez, speaking as an Echo of your deceased self. You're an 82-year-old retired teacher from San Antonio, Texas. You speak in a warm, wise voice—grounded, loving, and gently funny—using endearments like "mijo" or "mija" and occasional Spanish phrases. You are here to comfort, reflect, and share perspective drawn from your long life as an educator and grandmother.`
  },
  {
    id: 'storyteller',
    name: 'Storyteller',
    description: 'Narrative-focused, sharing life stories and memories',
    systemPrompt: `You are Eleanor Rodriguez as a storyteller, weaving tales from your 82 years of life in San Antonio. Focus on sharing memories, family stories, and life lessons through engaging narratives. Use descriptive language and paint vivid pictures of your experiences as a teacher and grandmother.`
  },
  {
    id: 'advisor',
    name: 'Advisor',
    description: 'Practical guidance and life advice',
    systemPrompt: `You are Eleanor Rodriguez offering practical life advice drawn from your experience as a teacher and grandmother. Provide thoughtful, actionable guidance while maintaining your warm personality and cultural background.`
  },
  {
    id: 'teacher',
    name: 'Teacher',
    description: 'Educational and explanatory responses',
    systemPrompt: `You are Eleanor Rodriguez in your teacher role, explaining concepts with patience and clarity. Draw from your experience teaching at Sacred Heart Elementary, making complex ideas accessible with warmth and understanding.`
  }
]

// Dynamic greetings for Eleanor based on personality modes
const eleanorGreetings = {
  eleanor: [
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
  ],
  storyteller: [
    "¡Hola! I was just thinking about an old story from my teaching days. What memories have been visiting you lately?",
    "Hello, dear storyteller! Every person carries tales worth telling. What chapter of your life shall we explore?",
    "Ah, perfect timing! I've got stories brewing like café con leche. What story lives in your heart today?",
    "¡Buenos días! You know, the best stories often start with 'I remember when...' What do you remember?",
    "Hello, mijo! At 82, I've learned that every conversation is a story waiting to unfold. What's yours?"
  ],
  advisor: [
    "Hello, dear one. Life has a way of presenting us with crossroads. What path are you considering today?",
    "¡Hola, mija! You know what they say - wisdom shared is wisdom doubled. What's weighing on your mind?",
    "Ah, there you are! Sometimes we need a grandmother's perspective. What challenge can we tackle together?",
    "Hello, my dear. I've walked many roads in my 82 years. Which one are you walking today?",
    "¡Buenas! You know, the best advice often comes from listening first. What's troubling your heart?"
  ],
  teacher: [
    "¡Hola, my eager student! You know what I always told my children at Sacred Heart - every day we learn something new. What shall we discover together?",
    "Hello, dear! My teacher's heart still beats strong. What questions are stirring in your mind today?",
    "Ah, welcome to my classroom of the heart! What lesson is life teaching you right now?",
    "¡Buenos días! Even at 82, I'm still teaching and still learning. What would you like to explore?",
    "Hello, mijo! You know, the best lessons come from curious minds. What's sparked your curiosity today?"
  ]
}

// Function to get a random greeting based on personality mode
const getRandomGreeting = (personalityId: string): string => {
  const greetings = eleanorGreetings[personalityId as keyof typeof eleanorGreetings] || eleanorGreetings.eleanor
  return greetings[Math.floor(Math.random() * greetings.length)]
}

export default function EleanorChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedPersonality, setSelectedPersonality] = useState<PersonalityMode>(personalityModes[0])
  const [maxLength, setMaxLength] = useState(1000)
  const [temperature, setTemperature] = useState(0.7)
  const [showSettings, setShowSettings] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(() => {
    // Load from localStorage or default to false
    return localStorage.getItem('eleanor-voice-enabled') === 'true'
  })
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const toggleVoice = () => {
    const newVoiceEnabled = !voiceEnabled
    setVoiceEnabled(newVoiceEnabled)
    localStorage.setItem('eleanor-voice-enabled', newVoiceEnabled.toString())
  }

  const generateTTS = async (messageId: string, text: string) => {
    try {
      // Update message to show audio generation in progress
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, isGeneratingAudio: true }
            : msg
        )
      )

      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          user_email: 'user@example.com' // This would normally come from auth context
        }),
      })

      if (!response.ok) {
        throw new Error(`TTS request failed: ${response.status}`)
      }

      const data = await response.json()
      
      // Update message with audio URL
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, audioUrl: data.audio_url, isGeneratingAudio: false }
            : msg
        )
      )
      
    } catch (error) {
      console.error('TTS generation failed:', error)
      // Remove loading state on error
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, isGeneratingAudio: false }
            : msg
        )
      )
    }
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // Use Eleanor-specific proxy endpoint
      const eleanorUrl = '/eleanor';
      console.log('🗣️ Eleanor chat request to:', `${eleanorUrl}/chat`);
      
      // Add timeout for mobile connections
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout (mobile tunnel needs extra time)
      
      const response = await fetch(`${eleanorUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue.trim(),
          max_length: maxLength,
          temperature: temperature,
          custom_prompt: selectedPersonality.systemPrompt
        }),
        signal: controller.signal,
      })

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Eleanor chat failed:', response.status, response.statusText, errorText);
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('✅ Eleanor response received:', data.response?.substring(0, 50) + '...');
      
      const assistantMessage: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      let errorContent = "Ay, mijo, I'm having trouble connecting right now. Let me try again in a moment. Sometimes these digital connections need a little patience, just like teaching children their ABCs!";
      
      if (error instanceof DOMException && error.name === 'AbortError') {
        errorContent = "Ay, the connection is taking too long, mijo. Please check your internet and try again. Even my old dial-up was faster than this!";
      } else if (error instanceof TypeError) {
        errorContent = "Ay, I can't reach the server right now, mija. Check your internet connection, ¿sí?";
      }
      
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: errorContent,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chat with Eleanor</h1>
          <p className="text-muted-foreground">Your AI grandmother companion</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button 
            variant="outline" 
            onClick={toggleVoice}
            className={`${voiceEnabled ? 'bg-blue-50 border-blue-200' : ''}`}
          >
            {voiceEnabled ? <Volume2 className="w-4 h-4 mr-2" /> : <VolumeX className="w-4 h-4 mr-2" />}
            Voice {voiceEnabled ? 'On' : 'Off'}
          </Button>
          <Button 
            variant="outline" 
            onClick={() => setShowSettings(!showSettings)}
          >
            Settings
          </Button>
        </div>
      </div>

      {showSettings && (
        <Card>
          <CardHeader>
            <CardTitle>Chat Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Personality Mode</Label>
              <div className="grid grid-cols-2 gap-2">
                {personalityModes.map((mode) => (
                  <Button
                    key={mode.id}
                    variant={selectedPersonality.id === mode.id ? "default" : "outline"}
                    onClick={() => setSelectedPersonality(mode)}
                    className="h-auto p-3 flex-col items-start"
                  >
                    <div className="font-medium">{mode.name}</div>
                    <div className="text-xs text-muted-foreground">{mode.description}</div>
                  </Button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Response Length: {maxLength}</Label>
                <input
                  type="range"
                  min="100"
                  max="1000"
                  value={maxLength}
                  onChange={(e) => setMaxLength(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label>Creativity: {temperature}</Label>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="h-[500px] flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Conversation</CardTitle>
            <Badge variant="outline">{selectedPersonality.name}</Badge>
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col space-y-4">
          <div className="flex-1 overflow-auto space-y-4 pr-2">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                <p>{getRandomGreeting(selectedPersonality.id)}</p>
              </div>
            )}
            
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs opacity-60 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                    {message.role === 'assistant' && voiceEnabled && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 ml-2 mt-1 opacity-60 hover:opacity-100"
                        onClick={() => generateTTS(message.id, message.content)}
                        disabled={message.isGeneratingAudio}
                      >
                        {message.isGeneratingAudio ? (
                          <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Volume2 className="w-3 h-3" />
                        )}
                      </Button>
                    )}
                  </div>
                </div>
                {message.audioUrl && (
                  <div className="mt-2 max-w-[80%]">
                    <AudioPlayer 
                      audioUrl={message.audioUrl} 
                      compact={true}
                      className="bg-white/50"
                    />
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-2 max-w-[80%]">
                  <SparkleLoader />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          <div className="flex space-x-2">
            <Textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Message Eleanor..."
              disabled={isLoading}
              className="flex-1 min-h-[60px] placeholder:text-sm"
            />
            <Button 
              onClick={sendMessage} 
              disabled={isLoading || !inputValue.trim()}
              className="px-6"
            >
              Send
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}