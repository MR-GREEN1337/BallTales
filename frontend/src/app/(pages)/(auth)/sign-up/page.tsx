"use client"

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Mail, Lock, User, ChevronRight, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { signUp } from '@/actions/auth/sign-up'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import Cookies from "js-cookie"
import BackgroundSlideshow from '../_components/BackgroundSlideShow'
import { translations, useLanguage, SupportedLanguage } from '@/hooks/use-language-auth'

interface SignUpFormData {
  email: string
  password: string
  name: string
  language: SupportedLanguage
}

interface FormErrors {
  email?: string
  password?: string
  name?: string
}

const EMAIL_REGEX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/

const SignUpPage = () => {
  const { language, updateLanguage } = useLanguage()
  const t = translations.auth[language]
  const router = useRouter()

  // Form state
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState<SignUpFormData>({
    email: '',
    password: '',
    name: '',
    language: language
  })
  
  // UI state
  const [showPassword, setShowPassword] = useState(false)
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [isFormTouched, setIsFormTouched] = useState(false)

  // Password strength indicator
  const getPasswordStrength = (password: string): { strength: number; message: string } => {
    if (password.length === 0) return { strength: 0, message: '' }
    if (password.length < 8) return { strength: 1, message: t.passwordTooShort || 'Too short' }
    if (!PASSWORD_REGEX.test(password)) return { strength: 2, message: t.passwordMakeStronger || 'Make it stronger' }
    if (password.length < 12) return { strength: 3, message: t.passwordGettingThere || 'Getting there' }
    return { strength: 4, message: t.passwordStrong || 'Strong password!' }
  }

  // Form validation
  const validateForm = (step: number): boolean => {
    const errors: FormErrors = {}

    if (step === 1) {
      if (!formData.email) {
        errors.email = t.emailRequired || 'Email is required'
      } else if (!EMAIL_REGEX.test(formData.email)) {
        errors.email = t.emailInvalid || 'Please enter a valid email'
      }

      if (!formData.password) {
        errors.password = t.passwordRequired || 'Password is required'
      } else if (!PASSWORD_REGEX.test(formData.password)) {
        errors.password = t.passwordRequirements || 'Password must contain uppercase, lowercase, number, and special character'
      }
    } else {
      if (!formData.name) {
        errors.name = t.nameRequired || 'Name is required'
      } else if (formData.name.length < 2) {
        errors.name = t.nameMinLength || 'Name must be at least 2 characters'
      }
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  // Sign up mutation
  const { mutate: handleSignUp, isPending, isError, error } = useMutation({
    mutationFn: async () => {
      const result = await signUp(formData)
      if (result.error) throw new Error(result.error)
      if (result.token) {
        Cookies.set('auth-token', result.token, {
          expires: 7,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          path: '/'
        })
        setTimeout(() => router.push('/chat'), 100)
      }
      return result.user
    },
    onSuccess: () => {
      toast.success(t.accountCreated || 'Account created successfully!')
      router.push('/chat')
    },
    onError: (error: Error) => {
      toast.error(error.message)
      if (error.message.includes('email')) setStep(1)
    },
  })

  // Handle language change
  const handleLanguageChange = (newLanguage: SupportedLanguage) => {
    updateLanguage(newLanguage)
    setFormData(prev => ({ ...prev, language: newLanguage }))
  }

  // Form submission handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsFormTouched(true)
    
    if (validateForm(step)) {
      if (step === 1) {
        setStep(2)
      } else {
        handleSignUp()
      }
    }
  }

  // Input change handler
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement> | { target: { name: string; value: string } }
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (isFormTouched) validateForm(step)
  }

  const passwordStrength = getPasswordStrength(formData.password)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 to-red-950 flex items-center justify-center p-4 relative overflow-hidden">
      <BackgroundSlideshow />
      
      <Card className="w-full max-w-md relative bg-black/80 backdrop-blur-xl border-white/10">
        <CardContent className="p-6">
          <div className="text-center mb-8">
            <motion.h1
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="text-3xl font-bold text-white mb-2"
            >
              {t.welcomeNew}
            </motion.h1>
            
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-gray-300"
            >
              {t.signUpJoin}
            </motion.p>
          </div>

          {/* Progress Steps */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              {[1, 2].map((i) => (
                <div key={i} className="flex items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors duration-300 ${
                      i === step
                        ? 'bg-blue-500 text-white'
                        : i < step
                        ? 'bg-green-500 text-white'
                        : 'bg-white/10 text-gray-400'
                    }`}
                  >
                    {i < step ? '✓' : i}
                  </div>
                  {i !== 2 && (
                    <div
                      className={`w-16 h-0.5 ml-4 transition-colors duration-300 ${
                        step > i ? 'bg-green-500' : 'bg-white/10'
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Error Alert */}
          <AnimatePresence>
            {isError && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mb-4"
              >
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>{t.error || 'Error'}</AlertTitle>
                  <AlertDescription>
                    {error?.message || t.  || 'An error occurred during sign up'}
                  </AlertDescription>
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Sign Up Form */}
          <motion.form
            initial={{ opacity: 0, x: step === 1 ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            {step === 1 ? (
              <>
                <div className="space-y-2">
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      type="email"
                      name="email"
                      placeholder={t.email}
                      value={formData.email}
                      onChange={handleInputChange}
                      className={`pl-10 bg-black/50 border-white/20 text-white placeholder:text-gray-400
                        ${formErrors.email ? 'border-red-500' : 'focus:border-blue-400'}
                      `}
                      required
                    />
                  </div>
                  {formErrors.email && (
                    <p className="text-red-500 text-sm">{formErrors.email}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      placeholder={t.password}
                      value={formData.password}
                      onChange={handleInputChange}
                      className={`pl-10 bg-black/50 border-white/20 text-white placeholder:text-gray-400
                        ${formErrors.password ? 'border-red-500' : 'focus:border-blue-400'}
                      `}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-gray-400 hover:text-gray-300"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {formData.password && (
                    <div className="space-y-1">
                      <div className="flex gap-1">
                        {[1, 2, 3, 4].map((level) => (
                          <div
                            key={level}
                            className={`h-1 flex-1 rounded-full transition-colors duration-300 ${
                              level <= passwordStrength.strength
                                ? level === 4
                                  ? 'bg-green-500'
                                  : level === 3
                                  ? 'bg-yellow-500'
                                  : 'bg-red-500'
                                : 'bg-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                      <p className={`text-sm ${
                        passwordStrength.strength === 4
                          ? 'text-green-500'
                          : 'text-gray-400'
                      }`}>
                        {passwordStrength.message}
                      </p>
                    </div>
                  )}
                  {formErrors.password && (
                    <p className="text-red-500 text-sm">{formErrors.password}</p>
                  )}
                </div>
              </>
            ) : (
              <>
                <div className="space-y-2">
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      type="text"
                      name="name"
                      placeholder={t.name}
                      value={formData.name}
                      onChange={handleInputChange}
                      className={`pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400 ${
                        formErrors.name ? 'border-red-500' : ''
                      }`}
                      required
                    />
                  </div>
                  {formErrors.name && (
                    <p className="text-red-500 text-sm">{formErrors.name}</p>
                  )}
                </div>

                <Select
                  value={formData.language}
                  onValueChange={handleLanguageChange}
                >
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder={t.selectLanguage} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="ja">日本語</SelectItem>
                  </SelectContent>
                </Select>
              </>
            )}

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-blue-800 text-white hover:from-blue-700 hover:to-blue-900"
              disabled={isPending}
            >
              {isPending ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <svg className="w-5 h-5 animate-spin text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </motion.div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  {step === 1 ? t.continue : t.createAccount}
                  <ChevronRight className="w-4 h-4" />
                </div>
              )}
            </Button>

            {/* Sign In Link */}
            <p className="mt-6 text-center text-gray-300">
              {t.haveAccount}{' '}
              <button
                type="button"
                onClick={() => router.push('/sign-in')}
                className="text-blue-400 hover:text-blue-300"
              >
                {t.signIn}
              </button>
            </p>
          </motion.form>
        </CardContent>
      </Card>
    </div>
  )
}

export default SignUpPage