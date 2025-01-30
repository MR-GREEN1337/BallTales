"use client"

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UserCircle2, Bot, Send, ChevronRight, Save, Loader2Icon } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from 'sonner'
import axios from 'axios'
import MLBProfile from './_components/MLBProfile'
import MLBMedia from './_components/MLBMedia'
import { getUserProfile } from '@/actions/user/get-user'
import Cookies from "js-cookie"
import { redirect, useRouter } from 'next/navigation'
import { ClearButton, MessageDust } from './_components/ResetButton'
import { languageContent, typingPhrases } from '@/lib/constants'
import AnimatedBotIcon from './_components/AnimatedBotIcon'
import { updateUserPreferences } from '@/actions/user/update-preferences'
import ContextViewer from './_components/ContextViewer'
import PixelatedBackground from './_components/PixelatedBackground'


interface PreferencesState {
  botMessageCount: number;
  lastPreferencesUpdate: number;
}

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
  media?: any
  chart: any
  context: any
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
  chart: any
}

interface ChatRequestData {
  message: string;
  history: {
    id: string;
    content: string;
    sender: 'bot' | 'user';
    type: 'text' | 'options' | 'selection';
    options?: string[];
    suggestions?: string[];
    media?: any;
    chart?: any;
  }[];
  user_data: {
    id: string;
    name: string;
    email: string;
    language: string;
    preferences: {
      favorite_teams: string[];
      favorite_players: string[];
      interests: string[];
    }
  }
}

const TypingText = ({ text, language }: { text: string, language: string }) => {
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const phrases = typingPhrases[language as keyof typeof typingPhrases] || typingPhrases.en;
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
  const [userLanguage, setUserLanguage] = useState('en');
  const [inputText, setInputText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showThinking, setShowThinking] = useState(false)
  const [userData, setUserData] = useState<any>(null)
  const router = useRouter()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const thinkingTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)
  const [clearingMessages, setClearingMessages] = useState(false);
  const [messagesToClear, setMessagesToClear] = useState<Message[]>([]);
  const [initialMessageSet, setInitialMessageSet] = useState(false);
  const [showProfileAnimation, setShowProfileAnimation] = useState(false);
  const [preferencesState, setPreferencesState] = useState<PreferencesState>({
    botMessageCount: 0,
    lastPreferencesUpdate: Date.now()
  });
  const updateRef = useRef(false);

  useEffect(() => {
    const authToken = Cookies.get('auth-token')
    //alert(authToken)
    if (!authToken) {
      router.push('/sign-in')
      return
    }

    const fetchUserData = async () => {
      try {
        const data = await getUserProfile(authToken)
        setUserData(data)
        //alert(JSON.stringify(data, null, 2))
      } catch (error) {
        console.error('Error fetching user data:', error)
        toast.error('Failed to load user profile')
        router.push('/sign-in')
      }
    }

    fetchUserData()
  }, [])

  //console.log("samaykom", userData)

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion)
    handleSend()
  }

  const handlePreferencesUpdate = async () => {
    try {
      const authToken = Cookies.get('auth-token');
      if (!authToken) {
        console.error('No auth token found');
        return;
      }

      const recentMessages = messages.slice(-5);

      const payload = {
        messages: recentMessages.map(msg => ({
          content: msg.content,
          sender: msg.sender,
          type: msg.type,
          timestamp: Date.now()
        })),
        preferences: userData.preferences,
        user: {
          email: userData.user.email,
          name: userData.user.name,
          avatar: userData.user.avatar
        }
      };

      const backendResponse = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/user/update-preferences`,
        payload,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!backendResponse.data || !backendResponse.data.preferences) {
        throw new Error('Invalid response from preferences update API');
      }

      const dd = await updateUserPreferences(authToken, backendResponse.data);

      // Update user data without triggering a full re-render
      setUserData((prev: any) => ({
        ...prev,
        preferences: {
          ...prev.preferences,
          ...backendResponse.data.preferences
        }
      }));

      // Trigger the success animation in the profile component
      const profileElement = document.querySelector('.mlb-profile-trigger');
      if (profileElement) {
        setShowProfileAnimation(true);

        // Reset the animation state after it completes
        setTimeout(() => {
          setShowProfileAnimation(false);
        }, 2000);
      }

    } catch (error) {
      console.error('Failed to update preferences:', error);
      toast.error('Failed to update preferences');

      // Reset counter to 2 so next bot message will trigger update
      setPreferencesState(prev => ({
        ...prev,
        botMessageCount: 2
      }));
    }
  };

  const handleLogout = () => {
    Cookies.remove('auth-token')
    router.push('/sign-in')
    toast.success('Successfully logged out')
  }

  useEffect(() => {
    // Only set initial message if it hasn't been set and we have user data
    if (!initialMessageSet && userData?.preferences?.preferences?.language) {
      const lang = userData.preferences.preferences.language.toLowerCase();
      setUserLanguage(lang);

      setMessages([{
        id: 'welcome-message',
        content: languageContent[lang as keyof typeof languageContent]?.welcomeMessage || languageContent.en.welcomeMessage,
        sender: 'bot',
        type: 'text',
        chart: undefined,
        context: undefined
      }]);

      setInitialMessageSet(true);
    }
  }, [userData, initialMessageSet]);

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message]);
    if (message.sender === 'bot' && !message.id.startsWith('suggestions-')) {
      setPreferencesState(prev => {
        const newCount = prev.botMessageCount + 1;

        //console.log('Bot message counter:', newCount);

        // Only trigger update exactly every 3 messages
        if (newCount === 3) {
          // Schedule the update asynchronously to avoid state conflicts
          setTimeout(() => {
            handlePreferencesUpdate();
          }, 0);

          return {
            botMessageCount: 0,
            lastPreferencesUpdate: Date.now()
          };
        }

        return {
          ...prev,
          botMessageCount: newCount
        };
      });
    }
  };

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

  interface MessageHistory {
    content: string
    sender: 'bot' | 'user'
    timestamp?: number
  }

  interface UserPreferences {
    favorite_teams?: string[]
    favorite_players?: string[]
    interests?: string[]
  }

  // Update the handleSend function in your OnboardingChat component
  const handleSend = async () => {
    if (!inputText.trim()) return

    const timestamp = Date.now()

    // Add user message
    const userMessage = {
      id: `user-${timestamp}`,
      content: inputText,
      sender: 'user' as const,
      type: 'text' as const,
      timestamp
    }
    addMessage(userMessage as any)
    setInputText('')
    setIsTyping(true)

    // Set thinking indicator after 3 seconds if no response
    thinkingTimeoutRef.current = setTimeout(() => {
      setShowThinking(true)
    }, 2000)

    try {
      // Convert messages to the format expected by the backend
      const messageHistory = messages.map(msg => ({
        content: msg.content,
        sender: msg.sender,
        type: msg.type || 'text',
        suggestions: msg.suggestions || undefined,
      }))
      //console.log("userData", userData)
      // Prepare user data
      const userDataForRequest = {
        id: userData.user.id,
        name: userData.user.name,
        email: userData.user.email,
        language: userData.preferences.preferences.language,
        preferences: {
          favorite_teams: userData.preferences?.favorite_teams || [],
          favorite_players: userData.preferences?.favorite_players || [],
          interests: userData.preferences?.interests || []
        }
      }
      const backData = {
        message: inputText,
        history: messageHistory,
        user_data: userDataForRequest
      }
      //console.log("Back Data", backData)
      const response = await axios.post<MLBResponse>(`${process.env.NEXT_PUBLIC_API_URL}/chat`, backData as ChatRequestData)
      console.log(response)
      // Clear thinking timeout and hide indicator
      if (thinkingTimeoutRef.current) {
        clearTimeout(thinkingTimeoutRef.current)
      }
      setShowThinking(false)

      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        content: response.data.conversation || response.data.message,
        context: response.data.context,
        sender: 'bot',
        type: 'text',
        suggestions: response.data.suggestions,
        media: response.data.media,
        chart: response.data.chart
      }

      setIsTyping(false)
      addMessage(botMessage)

      if (response.data.suggestions?.length) {
        addMessage({
          id: `suggestions-${Date.now()}`,
          content: "You might also be interested in:",
          sender: 'bot',
          type: 'options',
          options: response.data.suggestions,
          chart: undefined,
          context: undefined
        })
      }

      if (response.data.data_type === 'error') {
        toast.error(response.data.message)
      }

    } catch (error) {
      console.error('Chat API error:', error)
      handleChatError()
    }
  }

  // Separate error handling function for cleaner code
  const handleChatError = () => {
    setIsTyping(false)
    setShowThinking(false)

    if (thinkingTimeoutRef.current) {
      clearTimeout(thinkingTimeoutRef.current)
    }

    addMessage({
      id: `error-${Date.now()}`,
      content: "I'm having trouble connecting to the baseball data. Can you try asking that again?",
      sender: 'bot',
      type: 'text',
      chart: undefined,
      context: undefined
    })

    toast.error('Failed to get response from MLB chat')
  }

  if (!userData?.user) {
    return null
  }

  const handleReset = () => {
    setClearingMessages(true);
    // Store current messages except welcome message
    setMessagesToClear(messages.filter(m => m.id !== 'welcome-message'));
    // Reset to only welcome message
    setMessages([{
      id: 'welcome-message',
      content: languageContent[userLanguage as keyof typeof languageContent]?.welcomeMessage || languageContent.en.welcomeMessage,
      sender: 'bot',
      type: 'text',
      chart: undefined,
      context: undefined
    }]);

    // Clean up after animation
    setTimeout(() => {
      setClearingMessages(false);
      setMessagesToClear([]);
    }, 1000);
  };


  return (
<div className="relative h-full w-full bg-slate-950">
<PixelatedBackground />
      <div className="min-h-screen relative overflow-x-hidden">
        {/* Header */}
        <motion.div
          className="fixed top-0 left-0 right-0 bg-gradient-to-b from-gray-900 to-transparent p-4 z-30"
          initial={{ opacity: 1, y: 0 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="max-w-4xl mx-auto flex justify-end px-4">
            <div className="flex items-center gap-2">
              <ClearButton onClear={handleReset} disabled={messages.length === 1} />
              <MLBProfile
                user={userData.user}
                preferences={userData.preferences}
                onLogout={handleLogout}
                showSuccessAnimation={showProfileAnimation}
                onAnimationComplete={() => setShowProfileAnimation(false)}
              />
            </div>
          </div>
        </motion.div>
  
        {/* Chat Container */}
        <div className="max-w-4xl mx-auto px-4">
          <div className="pt-24 pb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="text-center"
            >
              <motion.h1
                className="text-4xl font-bold text-white mb-2 px-4 break-words"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
              >
                {languageContent[userLanguage as keyof typeof languageContent]?.pageTitle || languageContent.en.pageTitle}
              </motion.h1>
              <motion.p
                className="text-gray-300 mb-3 px-4"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.4 }}
              >
                {languageContent[userLanguage as keyof typeof languageContent]?.pageSubtitle || languageContent.en.pageSubtitle}
              </motion.p>
            </motion.div>
  
            {/* Messages */}
            <div className="space-y-8 pb-24">
              <div className="space-y-6">
                <AnimatePresence>
                  {clearingMessages && (
                    <div className="fixed inset-0 pointer-events-none">
                      {messagesToClear.map((message) => (
                        <MessageDust
                          key={`dust-${message.id}`}
                          message={message}
                          onComplete={() => {
                            setMessagesToClear(prev =>
                              prev.filter(m => m.id !== message.id)
                            );
                          }}
                        />
                      ))}
                    </div>
                  )}
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      id={`message-${message.id}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex items-start gap-3 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className="flex-shrink-0 w-8 h-8">
                          {message.sender === 'bot' ? (
                            <AnimatedBotIcon uniqueId={`bot-${message.id}`} state="default" />
                          ) : (
                            <UserCircle2 className="w-8 h-8 text-gray-400 mt-1" />
                          )}
                        </div>
  
                        <div className={`rounded-2xl p-4 backdrop-blur-lg break-words ${
                          message.sender === 'user'
                            ? 'bg-blue-600/90 text-white'
                            : 'bg-white/10 text-white'
                        }`}>
                          <div className="prose prose-invert max-w-full">
                            {message.content}
                          </div>
  
                          {message.media && (
                            <div className="max-w-full overflow-hidden">
                              <MLBMedia media={message.media} chart={message.chart} />
                            </div>
                          )}
  
                          {message.context && (
                            <div className="max-w-full overflow-hidden">
                              <ContextViewer context={message.context} />
                            </div>
                          )}
  
                          {message.options && (
                            <div className="relative mt-4 flex flex-wrap gap-2">
                              {message.options.map((option) => (
                                <Button
                                  key={`${message.id}-${option}`}
                                  variant="outline"
                                  className="bg-white/10 hover:bg-white/20 border-white/20 text-white text-sm break-words"
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
                      <AnimatedBotIcon uniqueId="thinking" state="thinking" />
                      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4">
                        <div className="text-white">
                          <TypingText text="Thinking..." language={userLanguage} />
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
                      <AnimatedBotIcon uniqueId="processing" state="processing" />
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
          </div>
  
          {/* Input */}
          <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-gray-900 to-transparent p-4">
            <div className="max-w-4xl mx-auto flex gap-2 px-4">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder={languageContent[userLanguage as keyof typeof languageContent]?.inputPlaceholder || languageContent.en.inputPlaceholder}
                className="bg-white/5 border-white/20 text-white placeholder:text-gray-400 backdrop-blur-sm flex-1 min-w-0"
              />
              <Button
                onClick={handleSend}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-lg flex-shrink-0"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OnboardingChat