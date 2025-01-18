"use client"

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UserCircle2, Bot, Send, ChevronRight, Save } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from 'sonner'

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
}

const OnboardingChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [preferences, setPreferences] = useState<any>({})
  const [hasInitialized, setHasInitialized] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize with welcome message
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

  const handleSend = () => {
    if (!inputText.trim()) return

    addMessage({
      id: `user-${Date.now()}`,
      content: inputText,
      sender: 'user',
      type: 'text'
    })
    setInputText('')
    setIsTyping(true)

    // Simulate bot thinking and response
    setTimeout(() => {
      setIsTyping(false)
      processUserInput(inputText)
    }, 1500)
  }

  const processUserInput = (text: string) => {
    // Simple keyword-based responses for demo
    const lowerText = text.toLowerCase()
    
    if (lowerText.includes('yankees') || lowerText.includes('red sox') || lowerText.includes('team')) {
      addMessage({
        id: `bot-team-${Date.now()}`,
        content: "That's a great team! Who's your favorite player from the roster?",
        sender: 'bot',
        type: 'text'
      })
    } else if (lowerText.includes('player') || lowerText.includes('favorite')) {
      setPreferences((prev: any) => ({...prev, mentionedPlayer: true}))
      addMessage({
        id: `bot-player-${Date.now()}`,
        content: "Amazing choice! Would you like to hear about some iconic moments from their career? Or maybe learn about similar players you might enjoy watching?",
        sender: 'bot',
        type: 'options',
        options: ['Iconic Moments', 'Similar Players']
      })
    } else {
      addMessage({
        id: `bot-default-${Date.now()}`,
        content: "Tell me more! What aspects of baseball interest you the most? The strategy, the statistics, the history, or the live action?",
        sender: 'bot',
        type: 'text'
      })
    }
  }

  const handleSaveProgress = () => {
    // Save preferences logic here
    toast.success("Progress saved! You can continue chatting or proceed to the dashboard.")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-blue-900 relative">
      {/* Fixed Save & Proceed Button */}
      <div className="fixed top-4 right-4 z-50">
        <Button
          onClick={handleSaveProgress}
          className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-8 pb-24">
          {/* Welcome Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
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
                    
                    <div className={`rounded-2xl p-4 ${
                      message.sender === 'user' 
                        ? 'bg-blue-600 text-white'
                        : 'bg-white/10 text-white'
                    }`}>
                      <div className="prose prose-invert">
                        {message.content}
                      </div>
                      
                      {message.options && (
                        <div className="mt-4 flex flex-wrap gap-2">
                          {message.options.map((option) => (
                            <Button
                              key={`${message.id}-${option}`}
                              variant="outline"
                              className="bg-white/10 hover:bg-white/20 border-white/20 text-white"
                              onClick={() => processUserInput(option)}
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
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start gap-3"
                >
                  <Bot className="w-8 h-8 text-blue-400 mt-1" />
                  <div className="bg-white/10 rounded-2xl p-4">
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

        {/* Fixed Input at Bottom */}
        <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-gray-900 to-transparent p-4">
          <div className="max-w-4xl mx-auto flex gap-2">
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type anything about baseball..."
              className="bg-white/5 border-white/20 text-white placeholder:text-gray-400"
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