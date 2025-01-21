"use client"

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { 
  ChevronRight, 
  Mail, 
  Lock,
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
  Github,
  Chrome
} from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { signIn } from '@/actions/auth/sign-in'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";
import Cookies from 'js-cookie';

interface SignInFormData {
  email: string;
  password: string;
  rememberMe: boolean
}

const EMAIL_REGEX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i

const SignInPage = () => {
  // Form state
  const [formData, setFormData] = useState<SignInFormData>({
    email: '',
    password: '',
    rememberMe: false
  })
  
  // UI state
  const [showPassword, setShowPassword] = useState(false)
  const [formErrors, setFormErrors] = useState<Partial<SignInFormData>>({})
  const [isFormTouched, setIsFormTouched] = useState(false)
  
  const router = useRouter()

  // Load saved email if it exists
  useEffect(() => {
    const savedEmail = localStorage.getItem('rememberedEmail')
    if (savedEmail) {
      setFormData(prev => ({ ...prev, email: savedEmail, rememberMe: true }))
    }
  }, [])

  // Form validation
  const validateForm = (): boolean => {
    const errors: Partial<SignInFormData> = {}

    if (!formData.email) {
      errors.email = 'Email is required'
    } else if (!EMAIL_REGEX.test(formData.email)) {
      errors.email = 'Please enter a valid email'
    }

    if (!formData.password) {
      errors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  // Sign in mutation
  const { mutate: handleSignIn, isPending, isError, error } = useMutation({
    mutationFn: async () => {
      const result = await signIn({ 
        email: formData.email, 
        password: formData.password 
      })
      
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
        }
      )
    }
      
    router.push('/chat')
    },
    onSuccess: (user) => {
      // Handle "Remember me"
      if (formData.rememberMe) {
        localStorage.setItem('rememberedEmail', formData.email)
      } else {
        localStorage.removeItem('rememberedEmail')
      }

      toast.success('Welcome back!')
      router.push('/chat')
    },
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })

  // Form submission handler
  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsFormTouched(true)
    
    if (validateForm()) {
      handleSignIn()
    }
  }

  // Input change handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (isFormTouched) {
      validateForm()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 to-red-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background animation */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute"
          initial={{
            x: Math.random() * window.innerWidth,
            y: -100,
            opacity: 0.3,
          }}
          animate={{
            y: window.innerHeight + 100,
            opacity: [0.3, 0.5, 0.3],
            rotate: 360,
          }}
          transition={{
            duration: 15 + Math.random() * 10,
            repeat: Infinity,
            ease: "linear",
            delay: i * 0.5,
          }}
        >
          {/* Your existing baseball SVG */}
        </motion.div>
      ))}

      <Card className="w-full max-w-md relative bg-white/10 backdrop-blur-xl border-white/20">
        <CardContent className="p-6">
          {/* Logo and Title */}
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
              Welcome Back
            </motion.h1>
            
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-gray-300"
            >
              Sign in to continue to BallTales
            </motion.p>
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
                    {error?.message || 'An error occurred during sign in'}
                  </AlertDescription>
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Sign In Form */}
          <motion.form
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            onSubmit={onSubmit}
            className="space-y-4"
          >
            {/* Email Field */}
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

            {/* Password Field */}
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
              {formErrors.password && (
                <p className="text-red-500 text-sm">{formErrors.password}</p>
              )}
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="rememberMe"
                  checked={formData.rememberMe}
                  onCheckedChange={(checked) => 
                    setFormData(prev => ({ ...prev, rememberMe: checked === true }))
                  }
                  className="border-white/20 data-[state=checked]:bg-blue-500"
                />
                <label 
                  htmlFor="rememberMe" 
                  className="text-sm text-gray-300 cursor-pointer"
                >
                  Remember me
                </label>
              </div>
              <button
                type="button"
                className="text-sm text-blue-400 hover:text-blue-300"
                onClick={() => router.push('/forgot-password')}
              >
                Forgot password?
              </button>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-red-500 to-blue-500 text-white hover:opacity-90"
              disabled={isPending}
            >
              {isPending ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <div className="flex items-center justify-center gap-2">
                  Sign In
                  <ChevronRight className="w-4 h-4" />
                </div>
              )}
            </Button>
          </motion.form>

          {/* Sign Up Link */}
          <p className="mt-6 text-center text-gray-300">
            Don't have an account?{' '}
            <button
              type="button" 
              onClick={() => router.push('/sign-up')}
              className="text-blue-400 hover:text-blue-300"
            >
              Sign up
            </button>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default SignInPage