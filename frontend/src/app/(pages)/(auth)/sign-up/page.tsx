"use client"

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Mail, Lock, User, ChevronRight, Eye, EyeOff, AlertCircle, ArrowLeft } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { signUp } from '@/actions/auth/sign-up';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import Cookies from "js-cookie";
import BackgroundSlideshow from '../_components/BackgroundSlideShow';
import { translations, useLanguage, SupportedLanguage } from '@/hooks/use-language-auth';

interface SignUpFormData {
  email: string;
  password: string;
  name: string;
  language: SupportedLanguage;
}

interface FormErrors {
  email?: string;
  password?: string;
  name?: string;
}

const EMAIL_REGEX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/;

// Import languageContent for comprehensive error messages
import { languageContent } from '@/lib/constants';

const SignUpPage = () => {
  const { language, updateLanguage } = useLanguage();
  const t = translations.auth[language];
  const validationMessages = languageContent[language].validation;
  const errorMessages = languageContent[language].errors;
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<SignUpFormData>({
    email: '',
    password: '',
    name: '',
    language: language
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [isFormTouched, setIsFormTouched] = useState(false);

  // Debounced validation
  useEffect(() => {
    const timer = setTimeout(() => {
      if (isFormTouched) validateForm(step);
    }, 300);
    return () => clearTimeout(timer);
  }, [formData, step, isFormTouched]);

  // Password strength calculation with memoization
  const getPasswordStrength = React.useMemo(() => (password: string): { strength: number; message: string } => {
    if (password.length === 0) return { strength: 0, message: '' };
    if (password.length < 8) return { strength: 1, message: languageContent[language].validation.password.tooShort };
    
    let score = 0;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    if (score < 3) return { strength: 2, message: languageContent[language].validation.password.makeStronger };
    if (score === 3) return { strength: 3, message: languageContent[language].validation.password.gettingThere };
    return { strength: 4, message: languageContent[language].validation.password.strong };
  }, [language]);

  const validateForm = (currentStep: number): boolean => {
    const errors: FormErrors = {};

    if (currentStep === 1) {
      if (!formData.email.trim()) {
        errors.email = validationMessages.required.email;
      } else if (!EMAIL_REGEX.test(formData.email)) {
        errors.email = validationMessages.invalid.email;
      }

      if (!formData.password) {
        errors.password = validationMessages.required.password;
      } else if (formData.password.length < 8) {
        errors.password = validationMessages.password.minLength;
      } else {
        const strength = getPasswordStrength(formData.password);
        if (strength.strength < 3) {
          errors.password = validationMessages.password.requirements;
        }
      }
    } else if (currentStep === 2) {
      if (!formData.name.trim()) {
        errors.name = validationMessages.required.name;
      } else if (formData.name.length < 2) {
        errors.name = validationMessages.name.minLength;
      } else if (formData.name.length > 50) {
        errors.name = validationMessages.name.maxLength;
      } else if (!/^[A-Za-z\s]+$/.test(formData.name)) {
        errors.name = validationMessages.name.invalid;
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const { mutate: handleSignUp, isPending, isError, error } = useMutation({
    mutationFn: async () => {
      const result = await signUp(formData);
      if (result.error) throw new Error(result.error);
      if (result.token) {
        Cookies.set('auth-token', result.token, {
          expires: 7,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          path: '/'
        });
      }
      return result.user;
    },
          onSuccess: () => {
      toast.success(languageContent[language].auth.accountCreated);
      router.push('/chat');
    },
    onError: (error: Error) => {
      let errorMessage = error.message;
      
      // Map common error messages to translated versions
      if (error.message.toLowerCase().includes('email') && error.message.toLowerCase().includes('use')) {
        errorMessage = errorMessages.emailTaken;
      } else if (error.message.toLowerCase().includes('password') && error.message.toLowerCase().includes('weak')) {
        errorMessage = errorMessages.weakPassword;
      } else if (error.message.toLowerCase().includes('network')) {
        errorMessage = errorMessages.networkError;
      } else if (error.message.toLowerCase().includes('unauthorized')) {
        errorMessage = errorMessages.unauthorized;
      } else {
        errorMessage = errorMessages.default;
      }
      
      toast.error(errorMessage);
      if (errorMessage === errorMessages.emailTaken) {
        setStep(1);
      }
    },
  });

  const handleLanguageChange = (newLanguage: SupportedLanguage) => {
    updateLanguage(newLanguage);
    setFormData(prev => ({ ...prev, language: newLanguage }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsFormTouched(true);
    
    if (validateForm(step)) {
      if (step === 1) {
        setStep(2);
      } else {
        handleSignUp();
      }
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement> | { target: { name: string; value: string } }
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const goBack = () => {
    setStep(1);
  };

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 to-red-950 flex items-center justify-center p-4 relative overflow-hidden">
      <BackgroundSlideshow />
      
      <Card className="w-full max-w-md relative bg-black/80 backdrop-blur-xl border-white/10">
        <CardContent className="p-6">
          {step === 2 && (
            <button
              onClick={goBack}
              className="absolute top-4 left-4 text-gray-400 hover:text-white transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
          )}

          <div className="text-center mb-8">
            <motion.h1
              key={`title-${step}`}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="text-3xl font-bold text-white mb-2"
            >
              {step === 1 ? t.welcomeNew : t.createAccount}
            </motion.h1>
            
            <motion.p
              key={`subtitle-${step}`}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-gray-300"
            >
              {t.signUpJoin}
            </motion.p>
          </div>

          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              {[1, 2].map((i) => (
                <div key={i} className="flex items-center">
                  <motion.div
                    animate={{
                      scale: i === step ? 1.1 : 1,
                      backgroundColor: i === step ? 'rgb(59, 130, 246)' : i < step ? 'rgb(34, 197, 94)' : 'rgba(255, 255, 255, 0.1)'
                    }}
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-white transition-colors duration-300`}
                  >
                    {i < step ? '✓' : i}
                  </motion.div>
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

          <AnimatePresence mode="wait">
            {isError && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mb-4"
              >
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>{languageContent[language].form.error}</AlertTitle>
                  <AlertDescription>
                    {error?.message || languageContent[language].form.errorOccurred}
                  </AlertDescription>
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.form
            key={`form-step-${step}`}
            initial={{ opacity: 0, x: step === 1 ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: step === 1 ? 20 : -20 }}
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
                      aria-invalid={!!formErrors.email}
                      aria-describedby={formErrors.email ? "email-error" : undefined}
                      required
                    />
                  </div>
                  {formErrors.email && (
                    <p id="email-error" className="text-red-500 text-sm">{formErrors.email}</p>
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
                      aria-invalid={!!formErrors.password}
                      aria-describedby={formErrors.password ? "password-error" : undefined}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-gray-400 hover:text-gray-300"
                      aria-label={showPassword ? "Hide password" : "Show password"}
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
                          <motion.div
                            key={level}
                            className="h-1 flex-1 rounded-full"
                            animate={{
                              backgroundColor: level <= passwordStrength.strength
                                ? level === 4
                                  ? 'rgb(34, 197, 94)'
                                  : level === 3
                                  ? 'rgb(234, 179, 8)'
                                  : 'rgb(239, 68, 68)'
                                : 'rgb(209, 213, 219)'
                            }}
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
                    <p id="password-error" className="text-red-500 text-sm">{formErrors.password}</p>
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
                      aria-invalid={!!formErrors.name}
                      aria-describedby={formErrors.name ? "name-error" : undefined}
                      required
                    />
                  </div>
                  {formErrors.name && (
                    <p id="name-error" className="text-red-500 text-sm">{formErrors.name}</p>
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
              className="w-full bg-gradient-to-r from-blue-600 to-blue-800 text-white hover:from-blue-700 hover:to-blue-900 relative overflow-hidden"
              disabled={isPending}
            >
              <AnimatePresence mode="wait">
                {isPending ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 flex items-center justify-center"
                  >
                    <svg className="w-5 h-5 animate-spin text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </motion.div>
                ) : (
                  <motion.div
                    key="text"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center justify-center gap-2"
                  >
                    {step === 1 ? t.continue : t.createAccount}
                    <ChevronRight className="w-4 h-4" />
                  </motion.div>
                )}
              </AnimatePresence>
            </Button>

            <p className="mt-6 text-center text-gray-300">
              {t.haveAccount}{' '}
              <button
                type="button"
                onClick={() => router.push('/sign-in')}
                className="text-blue-400 hover:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-black rounded-sm"
              >
                {t.signIn}
              </button>
            </p>
          </motion.form>
        </CardContent>
      </Card>
    </div>
  );
};

export default SignUpPage;