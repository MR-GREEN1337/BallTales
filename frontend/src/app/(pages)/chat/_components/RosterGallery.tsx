"use client"

import React, { useState } from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { motion } from 'framer-motion';
import ImageAnalysisDialog from './ImageAnalysisDialog';

interface Player {
  id: string;
  name: string;
  imageUrl?: string;
}

interface RosterGalleryProps {
  players: Player[];
}

const RosterGallery: React.FC<RosterGalleryProps> = ({ players }) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);

  const handleImageClick = (player: Player) => {
    if (player.imageUrl) {
      setSelectedImage(player.imageUrl);
      setShowAnalysis(true);
    }
  };

  const handleCloseAnalysis = () => {
    setShowAnalysis(false);
    setSelectedImage(null);
  };

  return (
    <div className="w-full">
      <ScrollArea className="h-[80vh] w-full rounded-lg border border-white/10 bg-black/20">
        <motion.div 
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ staggerChildren: 0.1 }}
        >
          {players.map((player) => (
            player.imageUrl && (
              <motion.div
                key={player.id}
                layoutId={player.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative aspect-square"
                onClick={() => handleImageClick(player)}
              >
                <motion.div 
                  className="relative w-full h-full rounded-xl overflow-hidden cursor-pointer bg-gradient-to-br from-blue-500/10 to-purple-500/10"
                  whileHover={{ scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                >
                  <motion.img
                    src={player.imageUrl}
                    alt={player.name}
                    className="w-full h-full object-cover"
                    initial={{ scale: 1.2 }}
                    whileHover={{ scale: 1.3 }}
                    transition={{ duration: 0.4 }}
                  />
                  <motion.div 
                    className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"
                    initial={{ opacity: 0 }}
                    whileHover={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  />
                  <motion.div 
                    className="absolute bottom-0 left-0 right-0 p-4"
                    initial={{ y: 20, opacity: 0 }}
                    whileHover={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="text-white">
                      <motion.h3 
                        className="font-semibold text-lg"
                        layoutId={`title-${player.id}`}
                      >
                        {player.name}
                      </motion.h3>
                    </div>
                  </motion.div>
                </motion.div>
              </motion.div>
            )
          ))}
        </motion.div>
      </ScrollArea>

      {showAnalysis && selectedImage && (
        <ImageAnalysisDialog
          isOpen={showAnalysis}
          onClose={handleCloseAnalysis}
          imageUrl={selectedImage}
        />
      )}
    </div>
  );
};

export default RosterGallery;