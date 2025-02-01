"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import ScreenshotLoader from '@/components/global/ScreenshotLoader';
import { useLanguage } from '@/hooks/use-language-auth';

const translations = {
  en: {
    title: "Your Game,",
    titleSpan: "Your Highlights",
    subtitle: "Personalized MLB highlights in English, Spanish, and Japanese. Stay connected to every moment that matters.",
    cta: "Experience the App"
  },
  es: {
    title: "Tu Juego,",
    titleSpan: "Tus Momentos",
    subtitle: "Momentos destacados personalizados de la MLB en inglés, español y japonés. Mantente conectado a cada momento importante.",
    cta: "Prueba la Aplicación"
  },
  ja: {
    title: "あなたの試合、",
    titleSpan: "あなたのハイライト",
    subtitle: "英語、スペイン語、日本語で楽しめるパーソナライズされたMLBハイライト。大切な瞬間をお見逃しなく。",
    cta: "アプリを体験"
  }
};

const Home = () => {
  const { language, updateLanguage } = useLanguage();
  const t = translations[language];

  return (
    <div className="min-h-screen text-white overflow-hidden relative">
      {/* Background image with overlay */}
      <motion.div 
        initial={{ scale: 1.1, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1.5 }}
        className="absolute inset-0 z-0"
      >
        <div className="absolute inset-0 bg-gradient-to-b from-blue-950/70 to-red-950/70 z-10" />
        <div className="absolute inset-0 bg-black/30 z-10" />
        <motion.img
          src="/field.jpg"
          alt="Baseball Field"
          className="object-cover w-full h-full"
          animate={{
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </motion.div>

      {/* Main content wrapper - encompasses all content including language selection */}
      <div className="relative z-20 min-h-screen">
        {/* Content container */}
        <div className="container mx-auto px-4 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="flex flex-col items-center justify-center min-h-[80vh] gap-8"
          >
            {/* Title */}
            <AnimatePresence mode="wait">
              <motion.h1
                key={language}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="text-5xl md:text-7xl font-bold text-center mb-4"
              >
                {t.title}
                <span className="text-red-500"> {t.titleSpan}</span>
              </motion.h1>
            </AnimatePresence>

            {/* Subtitle */}
            <AnimatePresence mode="wait">
              <motion.p
                key={language}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
                className="text-xl md:text-2xl text-gray-300 text-center max-w-2xl mb-8"
              >
                {t.subtitle}
              </motion.p>
            </AnimatePresence>

            {/* CTA Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <Button 
                size="lg"
                className={cn(
                  "bg-red-600 hover:bg-red-700 text-white",
                  "px-8 py-6 text-xl rounded-full",
                  "transition-transform hover:scale-105 shadow-lg"
                )}
                onClick={() => window.location.href = '/chat'}
              >
                {t.cta}
              </Button>
            </motion.div>
          </motion.div>

          {/* Language Selection - now properly nested within the main content structure */}
          <div className="absolute bottom-8 left-0 right-0 flex flex-col items-center">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
              className="flex gap-4"
            >
              <Button 
                variant={language === 'en' ? 'default' : 'ghost'} 
                onClick={() => updateLanguage('en')}
                className={cn(
                  "text-white",
                  language === 'en' ? "bg-red-600 hover:bg-red-700" : "hover:text-red-500"
                )}
              >
                English
              </Button>
              <Button 
                variant={language === 'es' ? 'default' : 'ghost'}
                onClick={() => updateLanguage('es')}
                className={cn(
                  "text-white",
                  language === 'es' ? "bg-red-600 hover:bg-red-700" : "hover:text-red-500"
                )}
              >
                Español
              </Button>
              <Button 
                variant={language === 'ja' ? 'default' : 'ghost'}
                onClick={() => updateLanguage('ja')}
                className={cn(
                  "text-white",
                  language === 'ja' ? "bg-red-600 hover:bg-red-700" : "hover:text-red-500"
                )}
              >
                日本語
              </Button>
            </motion.div>
            
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.4 }}
              className="text-sm text-gray-400 mt-4 tracking-wide"
            >
              A Google Cloud × MLB™ Hackathon App Submission
            </motion.p>
          </div>
        </div>
      </div>
    </div>
);
};

export default Home;