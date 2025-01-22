import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const BackgroundSlideshow = () => {
    // State to track current and next image indices
    const [currentImageIndex, setCurrentImageIndex] = useState(1);
  
    // Format the image number with leading zeros
    const formatImageNumber = (num: number) => {
      return num.toString().padStart(6, '0');
    };
  
    // Effect to handle image transitions
    useEffect(() => {
        const timer = setInterval(() => {
          setCurrentImageIndex((prev) => (prev === 30 ? 1 : prev + 1));
        }, 6000);
    
        return () => clearInterval(timer);
      }, []);
  
    return (
        <div className="fixed inset-0 w-full h-full overflow-hidden bg-black">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentImageIndex}
            className="absolute inset-0 w-full h-full"
            initial={{ opacity: 0, scale: 1.1 }}
            animate={{ 
              opacity: 1,
              scale: 1,
            }}
            exit={{ opacity: 0 }}
            transition={{
              opacity: { duration: 1.5, ease: "easeInOut" },
              scale: { duration: 6, ease: "easeInOut" }
            }}
          >
            <img
              src={`/homeruns/${formatImageNumber(currentImageIndex)}.jpg`}
              alt={`Baseball Moment ${currentImageIndex}`}
              className="object-cover w-full h-full"
            />
          </motion.div>
        </AnimatePresence>
      </div>
    );
  };

export default BackgroundSlideshow;