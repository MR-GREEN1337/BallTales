"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { useRouter } from 'next/navigation';
import { cn } from "@/lib/utils";

const NotFound = () => {
  const router = useRouter();

  const ballVariants = {
    initial: { y: -100, x: -100, rotate: 0, scale: 0.8 },
    animate: {
      y: [0, -30, 0],
      x: [0, 15, 0],
      rotate: [0, 180, 360],
      scale: [1, 0.95, 1],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: [0.45, 0, 0.55, 1],
        times: [0, 0.5, 1],
        rotate: {
          duration: 3,
          repeat: Infinity,
          ease: "linear"
        }
      }
    },
    hover: {
      scale: 1.1,
      transition: {
        duration: 0.3
      }
    }
  };

  return (
    <div className="min-h-screen text-white overflow-hidden relative">
      {/* Background with overlay */}
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

      {/* Main content */}
      <div className="relative z-20 min-h-screen flex flex-col items-center justify-center px-4">
        <div className="text-center">
          {/* Animated baseball */}
          <motion.div
            variants={ballVariants}
            initial="initial"
            animate="animate"
            className="mb-8 inline-block"
          >
            <svg width="80" height="80" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* Main ball */}
              <circle cx="50" cy="50" r="45" fill="white" filter="drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))"/>
              
              {/* Ball texture gradient */}
              <circle cx="50" cy="50" r="44" fill="url(#ballGradient)" fillOpacity="0.1"/>
              
              {/* Stitching patterns */}
              <path d="M30 30C40 35 45 45 45 50C45 55 40 65 30 70" 
                    stroke="#D63031" 
                    strokeWidth="3" 
                    fill="none" 
                    strokeLinecap="round"/>
              <path d="M70 30C60 35 55 45 55 50C55 55 60 65 70 70" 
                    stroke="#D63031" 
                    strokeWidth="3" 
                    fill="none" 
                    strokeLinecap="round"/>
              
              {/* Secondary stitching details */}
              <path d="M35 25C45 32 42 42 42 45" 
                    stroke="#D63031" 
                    strokeWidth="2" 
                    fill="none" 
                    strokeLinecap="round"/>
              <path d="M65 25C55 32 58 42 58 45" 
                    stroke="#D63031" 
                    strokeWidth="2" 
                    fill="none" 
                    strokeLinecap="round"/>
              <path d="M35 75C45 68 42 58 42 55" 
                    stroke="#D63031" 
                    strokeWidth="2" 
                    fill="none" 
                    strokeLinecap="round"/>
              <path d="M65 75C55 68 58 58 58 55" 
                    stroke="#D63031" 
                    strokeWidth="2" 
                    fill="none" 
                    strokeLinecap="round"/>
              
              {/* Subtle surface details */}
              <circle cx="50" cy="50" r="44" 
                      stroke="#E0E0E0" 
                      strokeWidth="0.5" 
                      strokeDasharray="1 3"/>
              
              {/* Definitions for gradients and filters */}
              <defs>
                <radialGradient id="ballGradient" cx="35" cy="35" r="50" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FFFFFF"/>
                  <stop offset="100%" stopColor="#E0E0E0"/>
                </radialGradient>
              </defs>
            </svg>
          </motion.div>

          {/* Error message */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h1 className="text-7xl md:text-9xl font-bold mb-4">404</h1>
            <h2 className="text-2xl md:text-4xl font-semibold mb-4">
              Strike <span className="text-red-500">Out!</span>
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-md mx-auto">
              Looks like this page got caught in a pickle. Let's head back to home plate.
            </p>
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Button 
              size="lg"
              onClick={() => router.push('/')}
              className={cn(
                "bg-red-600 hover:bg-red-700 text-white",
                "px-8 py-6 text-xl rounded-full",
                "transition-transform hover:scale-105 shadow-lg"
              )}
            >
              Return Home
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;