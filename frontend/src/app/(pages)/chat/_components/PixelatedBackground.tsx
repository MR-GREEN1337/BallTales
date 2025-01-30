import React, { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  opacity: number;
  pulse: number;
  pulseSpeed: number;
}

interface GridPulse {
  x: number;
  y: number;
  size: number;
  alpha: number;
  direction: 'horizontal' | 'vertical';
  speed: number;
}

const PixelatedBackground: React.FC = () => {
  const particleCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const pulseCanvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const particleCanvas = particleCanvasRef.current;
    const pulseCanvas = pulseCanvasRef.current;
    if (!particleCanvas || !pulseCanvas) return;

    const particleCtx = particleCanvas.getContext('2d');
    const pulseCtx = pulseCanvas.getContext('2d');
    if (!particleCtx || !pulseCtx) return;

    let particleAnimationId: number;
    let pulseAnimationId: number;

    const setCanvasSize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      particleCanvas.width = width;
      particleCanvas.height = height;
      pulseCanvas.width = width;
      pulseCanvas.height = height;
    };

    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    // Initialize particles
    const particles: Particle[] = Array.from({ length: 30 }, () => ({
      x: Math.random() * particleCanvas.width,
      y: Math.random() * particleCanvas.height,
      size: Math.random() * 1.5 + 0.5,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.3 + 0.1,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: Math.random() * 0.01 + 0.005
    }));

    // Initialize grid pulses with more prominent settings
    const gridPulses: GridPulse[] = [];
    const addGridPulse = () => {
      const isHorizontal = Math.random() > 0.5;
      const gridSize = 20; // Match this with the grid size in CSS
      
      gridPulses.push({
        x: isHorizontal ? 0 : Math.floor(Math.random() * pulseCanvas.width / gridSize) * gridSize,
        y: isHorizontal ? Math.floor(Math.random() * pulseCanvas.height / gridSize) * gridSize : 0,
        size: 8, // Increased size
        alpha: 1.0, // Full initial opacity
        direction: isHorizontal ? 'horizontal' : 'vertical',
        speed: 2 // Slightly faster
      });
    };

    // Add new pulse more frequently
    const pulseInterval = setInterval(addGridPulse, 500); // Every 500ms instead of 1000ms

    const animateParticles = () => {
      if (!particleCtx) return;
      particleCtx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);

      particles.forEach(particle => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        if (particle.x < 0) particle.x = particleCanvas.width;
        if (particle.x > particleCanvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = particleCanvas.height;
        if (particle.y > particleCanvas.height) particle.y = 0;

        particle.pulse += particle.pulseSpeed;
        const currentOpacity = particle.opacity + Math.sin(particle.pulse) * 0.1;

        particleCtx.beginPath();
        particleCtx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        particleCtx.fillStyle = `rgba(100, 149, 237, ${currentOpacity})`;
        particleCtx.fill();
      });

      particleAnimationId = requestAnimationFrame(animateParticles);
    };

    const animateGridPulses = () => {
      if (!pulseCtx) return;
      pulseCtx.clearRect(0, 0, pulseCanvas.width, pulseCanvas.height);

      for (let i = gridPulses.length - 1; i >= 0; i--) {
        const pulse = gridPulses[i];
        
        // Enhanced pulse rendering
        pulseCtx.beginPath();
        pulseCtx.fillStyle = `rgba(255, 0, 0, ${pulse.alpha})`; // Bright red
        
        if (pulse.direction === 'horizontal') {
          pulseCtx.fillRect(
            pulse.x - pulse.size,
            pulse.y - 1,
            pulse.size * 2,
            2
          );
          pulse.x += pulse.speed;
        } else {
          pulseCtx.fillRect(
            pulse.x - 1,
            pulse.y - pulse.size,
            2,
            pulse.size * 2
          );
          pulse.y += pulse.speed;
        }

        // Slower fade out
        pulse.alpha *= 0.98;

        // Remove faded pulses
        if (pulse.alpha < 0.05 || 
            pulse.x > pulseCanvas.width || 
            pulse.y > pulseCanvas.height) {
          gridPulses.splice(i, 1);
        }
      }

      pulseAnimationId = requestAnimationFrame(animateGridPulses);
    };

    animateParticles();
    animateGridPulses();

    return () => {
      window.removeEventListener('resize', setCanvasSize);
      cancelAnimationFrame(particleAnimationId);
      cancelAnimationFrame(pulseAnimationId);
      clearInterval(pulseInterval);
    };
  }, []);

  return (
    <div className="fixed inset-0 bg-slate-950 overflow-hidden">
      {/* Background particles */}
      <canvas
        ref={particleCanvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{ opacity: 0.4 }}
      />

      {/* Grid overlay */}
      <div 
        className="absolute inset-0" 
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(100, 149, 237, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(100, 149, 237, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '20px 20px'
        }}
      />

      {/* Pulse effects - increased opacity */}
      <canvas
        ref={pulseCanvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{ opacity: 0.8 }} // Increased from 0.6 to 0.8
      />

      {/* Vignette effect - slightly reduced opacity */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(
              circle at 50% 50%, 
              rgba(0, 0, 0, 0) 0%, 
              rgba(0, 0, 0, 0.3) 100%
            )
          `
        }}
      />

      {/* Ambient glow */}
      <div className="absolute inset-0 opacity-20">
        <div 
          className="absolute inset-0"
          style={{
            animation: 'ambient-shift 10s ease-in-out infinite',
            background: 'linear-gradient(45deg, rgba(100, 149, 237, 0.05), transparent 40%, rgba(100, 149, 237, 0.05) 60%)'
          }}
        />
      </div>

      <style jsx>{`
        @keyframes ambient-shift {
          0%, 100% { transform: scale(1) rotate(0deg); }
          50% { transform: scale(1.1) rotate(1deg); }
        }
      `}</style>
    </div>
  );
};

export default PixelatedBackground;