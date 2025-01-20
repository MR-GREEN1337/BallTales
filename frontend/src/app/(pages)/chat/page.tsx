"use client"

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UserCircle2, Bot, Send, ChevronRight, Save } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from 'sonner'
import axios from 'axios'
import MLBProfile from './_components/MLBProfile'

interface Message {
  id: string
  content: string
  sender: 'bot' | 'user'
  type: 'text' | 'options' | 'selection'
  options?: string[]
  selection?: {
    type: 'teams' | 'players' | 'preferences'
    items: { id: string; name: string; image?: string }[]
  }
  suggestions?: string[]
  media?: {
    type: string
    url: string
    thumbnail: string
    description: string
  }
}

interface MLBResponse {
  message: string
  conversation: string
  data_type: string
  data: any
  context: any
  suggestions: string[]
  media?: {
    type: string
    url: string
    thumbnail: string
    description: string
  }
}

const TypingText = ({ text }: { text: string }) => {
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const phrases = ["Thinking...", "Mulling it over...", "Processing..."];
  const [phraseIndex, setPhraseIndex] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      const currentPhrase = phrases[phraseIndex];
      
      if (!isDeleting) {
        if (displayText !== currentPhrase) {
          setDisplayText(currentPhrase.slice(0, displayText.length + 1));
        } else {
          setTimeout(() => setIsDeleting(true), 1000);
        }
      } else {
        if (displayText === "") {
          setIsDeleting(false);
          setPhraseIndex((prev) => (prev + 1) % phrases.length);
        } else {
          setDisplayText(currentPhrase.slice(0, displayText.length - 1));
        }
      }
    }, 100);

    return () => clearInterval(interval);
  }, [displayText, isDeleting, phraseIndex]);

  return (
    <motion.span
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="inline-block"
    >
      {displayText}
      <motion.span
        animate={{ opacity: [0, 1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity }}
        className="ml-1"
      >
        |
      </motion.span>
    </motion.span>
  );
};

const OnboardingChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showThinking, setShowThinking] = useState(false)
  const [preferences, setPreferences] = useState<any>({})
  const [hasInitialized, setHasInitialized] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const thinkingTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

  const user = {
    name: "Jane Smith",
    email: "jane@mlb.fan",
    avatar: "/user.png" // Using placeholder for demo
  }

  // Example preferences collected during chat
  const user_preferences = {
    favoriteTeam: "New York Yankees",
    favoritePlayer: "Aaron Judge",
    favoriteHomeRun: "Judge's 62nd HR of 2022 Season",
    stats: {
      messagesExchanged: 145,
      queriesAnswered: 72,
      daysActive: 30
    },
    preferences: {
      language: "English",
      statsPreference: "Advanced",
      notificationPreference: "Game Time Only"
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion)
    handleSend()
  }

  const handleLogout = () => {
    toast.success("Successfully logged out")
    // Add your logout logic here
  }

  useEffect(() => {
    setIsLoaded(true)
    setMessages([{
      id: 'welcome-message',
      content: "Hey there! I'm your baseball buddy, here to chat about the game we love! 💫⚾️ Tell me, what got you into baseball?",
      sender: 'bot',
      type: 'text'
    }])
  }, [])

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message])
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Clear thinking timeout when component unmounts
  useEffect(() => {
    return () => {
      if (thinkingTimeoutRef.current) {
        clearTimeout(thinkingTimeoutRef.current)
      }
    }
  }, [])

  const handleSend = async () => {
    if (!inputText.trim()) return

    // Add user message
    const userMessage = {
      id: `user-${Date.now()}`,
      content: inputText,
      sender: 'user',
      type: 'text' as const
    }
    addMessage(userMessage as any)
    setInputText('')
    setIsTyping(true)
    
    // Set thinking indicator after 3 seconds if no response
    thinkingTimeoutRef.current = setTimeout(() => {
      setShowThinking(true)
    }, 1500)

    try {
      const response = await axios.post<MLBResponse>(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat`, {
        message: inputText
      })

      // Clear thinking timeout and hide indicator
      if (thinkingTimeoutRef.current) {
        clearTimeout(thinkingTimeoutRef.current)
      }
      setShowThinking(false)

      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        content: response.data.conversation || response.data.message,
        sender: 'bot',
        type: 'text',
        suggestions: response.data.suggestions,
        media: response.data.media
      }

      setIsTyping(false)
      addMessage(botMessage)

      if (response.data.suggestions?.length) {
        addMessage({
          id: `suggestions-${Date.now()}`,
          content: "You might also be interested in:",
          sender: 'bot',
          type: 'options',
          options: response.data.suggestions
        })
      }

      if (response.data.data_type === 'error') {
        toast.error(response.data.message)
      }

    } catch (error) {
      console.error('Chat API error:', error)
      setIsTyping(false)
      setShowThinking(false)
      
      if (thinkingTimeoutRef.current) {
        clearTimeout(thinkingTimeoutRef.current)
      }
      
      addMessage({
        id: `error-${Date.now()}`,
        content: "I'm having trouble connecting to the baseball data. Can you try asking that again?",
        sender: 'bot',
        type: 'text'
      })
      
      toast.error('Failed to get response from MLB chat')
    }
  }

  return (
    <div 
      className="min-h-screen relative overflow-hidden"
      style={{
        backgroundImage: 'url(/chat.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
        backgroundColor: 'rgba(17, 24, 39, 0.85)',
        backgroundBlendMode: 'multiply'
      }}
    >
      <div className="fixed top-4 right-4 z-50">
        <MLBProfile 
          user={user}
          preferences={user_preferences}
          onLogout={handleLogout}
        />
      </div>
      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-8 pb-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold text-white mb-2">Welcome to BallTales</h1>
            <p className="text-gray-300">Let's chat about baseball and get to know your interests</p>
          </motion.div>

          {/* Messages */}
          <div className="space-y-6">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start gap-3 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                    {message.sender === 'bot' ? (
                      <Bot className="w-8 h-8 text-blue-400 mt-1" />
                    ) : (
                      <UserCircle2 className="w-8 h-8 text-gray-400 mt-1" />
                    )}
                    
                    <div className={`rounded-2xl p-4 backdrop-blur-sm ${
                      message.sender === 'user' 
                        ? 'bg-blue-600/90 text-white'
                        : 'bg-white/10 text-white'
                    }`}>
                      <div className="prose prose-invert">
                        {message.content}
                      </div>
                      
                      {message.media && (
                        <div className="mt-4">
                          {message.media.type === 'image' && (
                            <img 
                              src={message.media.url} 
                              alt={message.media.description}
                              className="rounded-lg max-w-full h-auto transform-none"
                            />
                          )}
                        </div>
                      )}
                      
                      {message.options && (
                        <div className="mt-4 flex flex-wrap gap-2">
                          {message.options.map((option) => (
                            <Button
                              key={`${message.id}-${option}`}
                              variant="outline"
                              className="bg-white/10 hover:bg-white/20 border-white/20 text-white"
                              onClick={() => handleSuggestionClick(option)}
                            >
                              {option}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {/* Thinking indicator with animated text */}
              {showThinking && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="flex items-start gap-3"
                >
                  <Bot className="w-8 h-8 text-blue-400 mt-1" />
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4">
                    <div className="text-white">
                      <TypingText text="Thinking..." />
                    </div>
                  </div>
                </motion.div>
              )}
              
              {/* Typing indicator */}
              {isTyping && !showThinking && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start gap-3"
                >
                  <Bot className="w-8 h-8 text-blue-400 mt-1" />
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-gray-900 to-transparent p-4">
          <div className="max-w-4xl mx-auto flex gap-2">
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type anything about baseball..."
              className="bg-white/5 border-white/20 text-white placeholder:text-gray-400 backdrop-blur-sm"
            />
            <Button
              onClick={handleSend}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OnboardingChat