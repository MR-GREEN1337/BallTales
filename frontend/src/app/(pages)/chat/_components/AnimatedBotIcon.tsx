import React from 'react';

const AnimatedBotIcon = ({ uniqueId = "bot", state = "default" }) => {
  const gradientIds = {
    glow: `glow-gradient-${uniqueId}`,
    center: `center-gradient-${uniqueId}`
  };

  return (
    <div className="w-8 h-8 relative">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" className="w-full h-full">
        {/* Base circle */}
        <circle cx="32" cy="32" r="30" fill={`url(#${gradientIds.glow})`} />
        
        {/* Face container */}
        <g transform="translate(32 32)">
          {/* Main face circle */}
          <circle cx="0" cy="0" r="16" fill={`url(#${gradientIds.center})`} />
          
          {/* Animated eyes */}
          <g className="eyes">
            {/* Left eye with blinking and thinking movement */}
            <circle cx="-6" cy="-2" r="2.5" fill="#E4F1FF">
              {/* Blinking animation */}
              <animate
                attributeName="ry"
                values="2.5;0.2;2.5"
                dur="3s"
                repeatCount="indefinite"
              />
              {/* Thinking movement */}
              {state === 'thinking' && (
                <animateTransform
                  attributeName="transform"
                  type="translate"
                  values="0 0; 0 2; 0 0"
                  dur="2s"
                  repeatCount="indefinite"
                />
              )}
            </circle>
            
            {/* Right eye with blinking and thinking movement */}
            <circle cx="6" cy="-2" r="2.5" fill="#E4F1FF">
              <animate
                attributeName="ry"
                values="2.5;0.2;2.5"
                dur="3s"
                repeatCount="indefinite"
              />
              {state === 'thinking' && (
                <animateTransform
                  attributeName="transform"
                  type="translate"
                  values="0 0; 0 2; 0 0"
                  dur="2s"
                  repeatCount="indefinite"
                />
              )}
            </circle>

            {/* Eyebrows for thinking state */}
            {state === 'thinking' && (
              <>
                <path 
                  d="M-8 -6 L-4 -4" 
                  stroke="#E4F1FF" 
                  strokeWidth="1.5"
                  strokeLinecap="round"
                >
                  <animateTransform
                    attributeName="transform"
                    type="rotate"
                    values="0 -6 -5; 10 -6 -5; 0 -6 -5"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </path>
                <path 
                  d="M4 -4 L8 -6" 
                  stroke="#E4F1FF" 
                  strokeWidth="1.5"
                  strokeLinecap="round"
                >
                  <animateTransform
                    attributeName="transform"
                    type="rotate"
                    values="0 6 -5; -10 6 -5; 0 6 -5"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </path>
              </>
            )}
          </g>
          
          {/* Animated mouth/expression */}
          {state === 'default' && (
            <path
              d="M-6 4 Q0 8 6 4"
              fill="none"
              stroke="#E4F1FF"
              strokeWidth="1.5"
              strokeLinecap="round"
            >
              <animate
                attributeName="d"
                values="M-6 4 Q0 8 6 4; M-6 5 Q0 9 6 5; M-6 4 Q0 8 6 4"
                dur="4s"
                repeatCount="indefinite"
              />
            </path>
          )}
          
          {state === 'thinking' && (
            <path
              d="M-4 4 Q0 4 4 4"
              fill="none"
              stroke="#E4F1FF"
              strokeWidth="1.5"
              strokeLinecap="round"
            >
              <animate
                attributeName="d"
                values="M-4 4 Q0 4 4 4; M-4 6 Q0 6 4 6; M-4 4 Q0 4 4 4"
                dur="2s"
                repeatCount="indefinite"
              />
              <animateTransform
                attributeName="transform"
                type="translate"
                values="0 0; -2 0; 0 0"
                dur="2s"
                repeatCount="indefinite"
              />
            </path>
          )}
          
          {/* Processing/speaking animation */}
          {state === 'processing' && (
            <path
              d="M-6 4 Q0 6 6 4"
              fill="none"
              stroke="#E4F1FF"
              strokeWidth="1.5"
              strokeLinecap="round"
            >
              <animate
                attributeName="d"
                values="M-6 4 Q0 6 6 4; M-6 5 Q0 3 6 5; M-6 4 Q0 6 6 4"
                dur="0.8s"
                repeatCount="indefinite"
              />
            </path>
          )}
        </g>

        {/* Gradients */}
        <defs>
          <radialGradient id={gradientIds.glow}>
            <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#2563EB" stopOpacity="0" />
          </radialGradient>
          
          <radialGradient id={gradientIds.center}>
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#1D4ED8" />
          </radialGradient>
        </defs>
      </svg>
    </div>
  );
};

export default AnimatedBotIcon;