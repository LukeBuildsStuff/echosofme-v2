import React, { useState, useRef, useEffect } from 'react'
import { getEleanorApiUrl } from '../utils/apiConfig'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
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

export default function EleanorChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedPersonality, setSelectedPersonality] = useState<PersonalityMode>(personalityModes[0])
  const [maxLength, setMaxLength] = useState(1000)
  const [temperature, setTemperature] = useState(0.7)
  const [showSettings, setShowSettings] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
        <Button 
          variant="outline" 
          onClick={() => setShowSettings(!showSettings)}
        >
          Settings
        </Button>
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
                <p>¡Hola! I'm Eleanor. What would you like to talk about today?</p>
              </div>
            )}
            
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs opacity-60 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-3 max-w-[80%]">
                  <p className="text-sm">Eleanor is thinking...</p>
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