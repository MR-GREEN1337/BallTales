import { useState, useEffect } from 'react';

// Define the type for supported languages
export type SupportedLanguage = 'en' | 'es' | 'ja';

// Hook for managing language state
export const useLanguage = () => {
  const [language, setLanguage] = useState<SupportedLanguage>('en');

  useEffect(() => {
    // Load language from localStorage on mount
    const savedLanguage = localStorage.getItem('preferredLanguage') as SupportedLanguage;
    if (savedLanguage && ['en', 'es', 'ja'].includes(savedLanguage)) {
      setLanguage(savedLanguage);
    }
  }, []);

  const updateLanguage = (newLanguage: SupportedLanguage) => {
    setLanguage(newLanguage);
    localStorage.setItem('preferredLanguage', newLanguage);
  };

  return { language, updateLanguage };
};

// Translations object for reuse across components
export const translations = {
  auth: {
    en: {
      welcomeBack: "Welcome Back",
      welcomeNew: "Welcome",
      signInContinue: "Sign in to continue to BallTales",
      signUpJoin: "Sign up to join BallTales",
      email: "Email",
      password: "Password",
      name: "Your name",
      rememberMe: "Remember me",
      signIn: "Sign In",
      signUp: "Sign Up",
      noAccount: "Don't have an account?",
      haveAccount: "Already have an account?",
      continue: "Continue",
      createAccount: "Create Account",
      selectLanguage: "Select language"
    },
    es: {
      welcomeBack: "Bienvenido de nuevo",
      welcomeNew: "Bienvenido",
      signInContinue: "Inicia sesión para continuar en BallTales",
      signUpJoin: "Regístrate para unirte a BallTales",
      email: "Correo electrónico",
      password: "Contraseña",
      name: "Tu nombre",
      rememberMe: "Recordarme",
      signIn: "Iniciar Sesión",
      signUp: "Registrarse",
      noAccount: "¿No tienes una cuenta?",
      haveAccount: "¿Ya tienes una cuenta?",
      continue: "Continuar",
      createAccount: "Crear Cuenta",
      selectLanguage: "Seleccionar idioma"
    },
    ja: {
      welcomeBack: "おかえりなさい",
      welcomeNew: "ようこそ",
      signInContinue: "BallTalesを続けるにはサインインしてください",
      signUpJoin: "BallTalesに参加するには登録してください",
      email: "メールアドレス",
      password: "パスワード",
      name: "お名前",
      rememberMe: "ログイン情報を保存",
      signIn: "サインイン",
      signUp: "登録",
      noAccount: "アカウントをお持ちでない方",
      haveAccount: "すでにアカウントをお持ちの方",
      continue: "続ける",
      createAccount: "アカウントを作成",
      selectLanguage: "言語を選択"
    }
  }
};