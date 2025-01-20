import React from 'react';
import { Bot } from 'lucide-react';
import { motion } from 'framer-motion';

const AnimatedThinking = () => {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start gap-3"
      >
        <Bot className="w-8 h-8 text-blue-400 mt-1" />
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl px-4 py-2">
          <motion.p 
            className="text-white/70 font-serif italic text-sm tracking-wide"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ 
              duration: 1.8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            cogitating...
          </motion.p>
        </div>
      </motion.div>
    )
  }

export default AnimatedThinking