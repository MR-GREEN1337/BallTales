import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence, Transition, Variants } from 'framer-motion';

// Define interfaces for our component props
interface ParticleProps {
  delay: number;
  x: number;
  y: number;
}

interface RippleProps {
  delay: number;
}

interface ProfileSuccessAnimationProps {
  show: boolean;
  onComplete?: () => void;
  particleCount?: number;
  particleDistance?: number;
  animationDuration?: number;
}

// Define interface for particle data structure
interface ParticleData {
  id: number;
  x: number;
  y: number;
  delay: number;
}

// Animation variants for reusable animations
const particleVariants: Variants = {
  initial: { scale: 0, x: 0, y: 0, opacity: 0 },
  animate: {
    scale: [1, 1.5, 0],
    opacity: [0.8, 0.8, 0],
  },
};

const checkmarkVariants: Variants = {
  initial: { scale: 0, opacity: 0 },
  animate: {
    scale: [0, 1.2, 1],
    opacity: [0, 1, 0],
  },
};

// Define common transition configurations
const easeOutTransition: Transition = {
  duration: 1,
  ease: "easeOut",
};

// Success particle component with proper typing
const SuccessParticle: React.FC<ParticleProps> = ({ delay, x, y }) => (
  <motion.div
    className="absolute w-2 h-2 rounded-full bg-green-400"
    variants={particleVariants}
    initial="initial"
    animate="animate"
    style={{ transformOrigin: 'center' }}
    transition={{
      duration: 1.2,
      delay,
      ease: [0.32, 0, 0.67, 0],
    }}
    custom={{ x, y }}
  />
);

// Ripple effect component with proper typing
const SuccessRipple: React.FC<RippleProps> = ({ delay }) => (
  <motion.div
    className="absolute inset-0 border-4 border-green-400 rounded-full"
    initial={{ scale: 0.2, opacity: 0 }}
    animate={{
      scale: 2,
      opacity: [0, 0.5, 0],
    }}
    transition={{
      ...easeOutTransition,
      delay,
    }}
  />
);

// Main success animation component
const ProfileSuccessAnimation: React.FC<ProfileSuccessAnimationProps> = ({
  show,
  onComplete,
  particleCount = 12,
  particleDistance = 60,
  animationDuration = 2000,
}) => {
  const [particles, setParticles] = useState<ParticleData[]>([]);

  // Memoize particle creation to prevent unnecessary recalculations
  const createParticles = useCallback(() => {
    return Array.from({ length: particleCount }, (_, i) => {
      const angle = (i * Math.PI * 2) / particleCount;
      return {
        id: i,
        x: Math.cos(angle) * particleDistance,
        y: Math.sin(angle) * particleDistance,
        delay: i * 0.05,
      };
    });
  }, [particleCount, particleDistance]);

  useEffect(() => {
    if (show) {
      console.log('Animation triggered:', { show, particleCount, particleDistance });
    }
  }, [show, particleCount, particleDistance]);

  useEffect(() => {
    let cleanupTimer: NodeJS.Timeout;

    if (show) {
      setParticles(createParticles());
      
      cleanupTimer = setTimeout(() => {
        onComplete?.();
        setParticles([]); // Clean up particles after animation
      }, animationDuration);
    }

    return () => {
      if (cleanupTimer) {
        clearTimeout(cleanupTimer);
      }
    };
  }, [show, createParticles, onComplete, animationDuration]);

  // Early return if not showing
  if (!show) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="absolute inset-0 pointer-events-none"
        initial={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        aria-hidden="true" // This is a decorative animation
      >
        {/* Central glow effect */}
        <motion.div
          className="absolute inset-0 bg-green-400"
          initial={{ opacity: 0 }}
          animate={{
            opacity: [0, 0.15, 0],
          }}
          transition={easeOutTransition}
        />
        
        {/* Ripple effects */}
        <SuccessRipple delay={0} />
        <SuccessRipple delay={0.2} />
        
        {/* Particles */}
        {particles.map((particle) => (
          <SuccessParticle
            key={particle.id}
            delay={particle.delay}
            x={particle.x}
            y={particle.y}
          />
        ))}
        
        {/* Success checkmark */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          variants={checkmarkVariants}
          initial="initial"
          animate="animate"
          transition={easeOutTransition}
        >
          <div className="text-green-400 text-2xl" aria-label="success">✓</div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ProfileSuccessAnimation;