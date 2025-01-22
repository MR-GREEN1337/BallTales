"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

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

const WindEffect = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: [0.1, 0.3, 0.1] }}
      transition={{
        duration: 5,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      className="absolute inset-0 z-10 mix-blend-overlay"
    >
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute h-full w-1 bg-gradient-to-b from-transparent via-white to-transparent"
          style={{
            left: `${i * 20}%`,
          }}
          animate={{
            y: ["0%", "100%"],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.2,
            ease: "easeInOut",
          }}
        />
      ))}
    </motion.div>
  );
};

const Home = () => {
  const [language, setLanguage] = useState<'en' | 'es' | 'ja'>('en');
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

      {/* Wind effect overlay */}
      <WindEffect />

      {/* Main content */}
      <div className="container mx-auto px-4 py-12 relative z-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="flex flex-col items-center justify-center min-h-[80vh] gap-8"
        >
          {/* 
          3D Baseball Bat
          <motion.div
            whileHover={{ scale: 1.1 }}
            transition={{ duration: 0.3 }}
          >
            <BaseballBat />
          </motion.div> */}

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

        {/* Language Selection */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-4"
        >
          <Button 
            variant={language === 'en' ? 'default' : 'ghost'} 
            onClick={() => setLanguage('en')}
            className={cn(
              "text-white",
              language === 'en' ? "bg-red-600 hover:bg-red-700" : "hover:text-red-500"
            )}
          >
            English
          </Button>
          <Button 
            variant={language === 'es' ? 'default' : 'ghost'}
            onClick={() => setLanguage('es')}
            className={cn(
              "text-white",
              language === 'es' ? "bg-red-600 hover:bg-red-700" : "hover:text-red-500"
            )}
          >
            Español
          </Button>
          <Button 
            variant={language === 'ja' ? 'default' : 'ghost'}
            onClick={() => setLanguage('ja')}
            className={cn(
              "text-white",
              language === 'ja' ? "bg-red-600 hover:bg-red-700" : "hover:text-red-500"
            )}
          >
            日本語
          </Button>
        </motion.div>
      </div>
    </div>
  );
};

export default Home;