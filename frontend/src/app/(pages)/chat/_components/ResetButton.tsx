import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2 } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface Particle {
  id: number;
  x: number;
  y: number;
  initialX: number;
  initialY: number;
}

interface Message {
  id: string;
  content: string;
  sender: 'bot' | 'user';
  type: 'text' | 'options' | 'selection';
  options?: string[];
  selection?: {
    type: 'teams' | 'players' | 'preferences';
    items: { id: string; name: string; image?: string; }[];
  };
  suggestions?: string[];
  media?: any;
}

interface DustMessageProps {
  message: Message;
  onComplete: () => void;
}

export const MessageDust: React.FC<DustMessageProps> = ({ message, onComplete }) => {
  const [particles, setParticles] = useState<Particle[]>([]);
  
  useEffect(() => {
    // Get element position for accurate particle origin
    const messageEl = document.getElementById(`message-${message.id}`);
    const rect = messageEl?.getBoundingClientRect();
    
    if (!rect) return;
    
    const text = message.content;
    const particlesCount = Math.min(text.length * 2, 50); // 2 particles per character, max 50
    
    const newParticles: Particle[] = Array.from({ length: particlesCount }, (_, i) => ({
      id: i,
      x: rect.x + rect.width / 2,
      y: rect.y + rect.height / 2,
      initialX: (Math.random() - 0.5) * 200, // Wider spread
      initialY: (Math.random() - 0.5) * 200,
    }));
    
    setParticles(newParticles);
    
    const timeout = setTimeout(() => {
      onComplete();
    }, 1000);
    
    return () => clearTimeout(timeout);
  }, [message.id, onComplete]);

  return (
    <AnimatePresence>
      {particles.map((particle) => (
        <motion.div
          key={`${message.id}-particle-${particle.id}`}
          className="fixed w-1.5 h-1.5 rounded-full shadow-glow"
          style={{
            background: message.sender === 'user' ? '#3B82F6' : '#FFFFFF',
            opacity: 0.8,
            boxShadow: `0 0 10px ${message.sender === 'user' ? '#3B82F6' : '#FFFFFF'}`,
            left: particle.x,
            top: particle.y,
          }}
          initial={{ 
            scale: 1,
            x: 0,
            y: 0,
            opacity: 1 
          }}
          animate={{ 
            scale: 0,
            x: particle.initialX,
            y: particle.initialY,
            opacity: 0
          }}
          transition={{
            duration: 0.8,
            ease: "easeOut",
            delay: Math.random() * 0.3
          }}
        />
      ))}
    </AnimatePresence>
  );
};

interface ClearButtonProps {
  onClear: () => void;
  disabled: boolean
}

export const ClearButton: React.FC<ClearButtonProps> = ({ onClear, disabled }) => {
    const [isHovered, setIsHovered] = useState(false);
  
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={onClear}
              disabled={disabled}
              variant="ghost"
              size="icon"
              className="relative bg-white/5 hover:bg-white/10 text-white border border-white/10 transition-all duration-200"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              <Trash2 className="w-4 h-4" />
              {isHovered && (
                <div className="absolute inset-0 overflow-hidden">
                  {Array.from({ length: 6 }).map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-0.5 h-0.5 bg-white/40 rounded-full"
                      initial={{ x: '50%', y: '50%' }}
                      animate={{
                        y: ['50%', '120%'],
                        x: ['50%', `${50 + (Math.random() * 20 - 10)}%`],
                        opacity: [1, 0]
                      }}
                      transition={{
                        duration: 0.6,
                        delay: i * 0.1,
                        repeat: Infinity,
                        repeatDelay: 0.2
                      }}
                    />
                  ))}
                </div>
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="bg-white/10 text-white border-white/20 backdrop-blur-sm">
            <p>Clear messages</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  };