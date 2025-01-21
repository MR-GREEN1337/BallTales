"use client"

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Mail, Lock, User, ChevronRight, Eye, EyeOff, AlertCircle, Chrome, Github } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { signUp } from '@/actions/auth/sign-up'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import Cookies from "js-cookie"

interface SignUpFormData {
  email: string
  password: string
  name: string
  language: string
}

interface FormErrors {
  email?: string
  password?: string
  name?: string
}

const EMAIL_REGEX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/

const SignUpPage = () => {
  // Form state
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState<SignUpFormData>({
    email: '',
    password: '',
    name: '',
    language: 'en'
  })
  
  // UI state
  const [showPassword, setShowPassword] = useState(false)
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [isFormTouched, setIsFormTouched] = useState(false)
  
  const router = useRouter()

  // Password strength indicator
  const getPasswordStrength = (password: string): { strength: number; message: string } => {
    if (password.length === 0) return { strength: 0, message: '' }
    if (password.length < 8) return { strength: 1, message: 'Too short' }
    if (!PASSWORD_REGEX.test(password)) return { strength: 2, message: 'Make it stronger' }
    if (password.length < 12) return { strength: 3, message: 'Getting there' }
    return { strength: 4, message: 'Strong password!' }
  }

  // Form validation
  const validateForm = (step: number): boolean => {
    const errors: FormErrors = {}

    if (step === 1) {
      if (!formData.email) {
        errors.email = 'Email is required'
      } else if (!EMAIL_REGEX.test(formData.email)) {
        errors.email = 'Please enter a valid email'
      }

      if (!formData.password) {
        errors.password = 'Password is required'
      } else if (!PASSWORD_REGEX.test(formData.password)) {
        errors.password = 'Password must contain uppercase, lowercase, number, and special character'
      }
    } else {
      if (!formData.name) {
        errors.name = 'Name is required'
      } else if (formData.name.length < 2) {
        errors.name = 'Name must be at least 2 characters'
      }
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  // Sign up mutation
  const { mutate: handleSignUp, isPending, isError, error } = useMutation({
    mutationFn: async () => {
      const result = await signUp(formData)
      
      if (result.error) {
        throw new Error(result.error)
      }
      if (result.token) {
        // Set the cookie on the client side
        Cookies.set('auth-token', result.token, {
          expires: 7, // 7 days
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          path: '/'
        })
        
        // Add a small delay before redirecting to ensure cookie is set
        setTimeout(() => {
          router.push('/chat')
        }, 100)
      }
      return result.user
    },
    onSuccess: (user) => {
      toast.success('Account created successfully!')
      router.push('/chat')
    },
    onError: (error: Error) => {
      toast.error(error.message)
      if (error.message.includes('email')) {
        setStep(1) // Go back to email step if email error
      }
    },
  })

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
    if (isFormTouched) {
      validateForm(step)
    }
  }

  const passwordStrength = getPasswordStrength(formData.password)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 to-red-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background animations remain the same */}
      
      <Card className="w-full max-w-md relative bg-white/10 backdrop-blur-xl border-white/20">
        <CardContent className="p-6">
          {/* Logo and Title section remains the same */}

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
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>
                    {error?.message || 'An error occurred during sign up'}
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
            <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", duration: 0.5 }}
            >
              {/* Your existing logo */}
            </motion.div>
            
            <motion.h1
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="text-3xl font-bold text-white mb-2"
            >
              Welcome
            </motion.h1>
            
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-gray-300"
            >
              Sign up to join BallTales
            </motion.p>
          </div>
            {step === 1 ? (
              <>
                <div className="space-y-2">
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      type="email"
                      name="email"
                      placeholder="Email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className={`pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400 ${
                        formErrors.email ? 'border-red-500' : ''
                      }`}
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
                      placeholder="Password"
                      value={formData.password}
                      onChange={handleInputChange}
                      className={`pl-10 pr-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400 ${
                        formErrors.password ? 'border-red-500' : ''
                      }`}
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
                      placeholder="Your name"
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
                  name="language"
                  value={formData.language}
                  onValueChange={(value) => handleInputChange({ target: { name: 'language', value } })}
                >
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="ja">日本語</SelectItem>
                    <SelectItem value="fr">Français</SelectItem>
                    <SelectItem value="de">Deutsch</SelectItem>
                  </SelectContent>
                </Select>
              </>
            )}

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-red-500 to-blue-500 text-white hover:opacity-90"
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
                  {step === 1 ? "Continue" : "Create Account"}
                  <ChevronRight className="w-4 h-4" />
                </div>
              )}
            </Button>

            {step === 1 && (
              <>
                <div className="mt-6">
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Sign In Link */}
            <p className="mt-6 text-center text-gray-300">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => router.push('/sign-in')}
                className="text-blue-400 hover:text-blue-300"
              >
                Sign in
              </button>
            </p>
          </motion.form>
        </CardContent>
      </Card>
    </div>
  )
}

export default SignUpPage