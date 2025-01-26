"use client"

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Box, Eye, LineChart, Book, Download, Send, X, MessagesSquare } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface ImageAnalysisResponse {
  summary: string;
  details: {
    technical_analysis: string;
    visual_elements: string;
    strategic_insights: string;
    additional_context: string;
  };
  timestamp: string;
  request_id: string;
  generated_image: string | null;
}

interface ImageAnalysisProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  analysis: ImageAnalysisResponse | null;
  onAnalyze: (query: string) => Promise<void>;
  isAnalyzing: boolean;
  error: string | null;
}

const ImageAnalysisComponent: React.FC<ImageAnalysisProps> = ({
  isOpen,
  onClose,
  imageUrl,
  analysis,
  onAnalyze,
  isAnalyzing,
  error
}) => {
  const [query, setQuery] = useState('');
  const [selectedSection, setSelectedSection] = useState<string>('summary');
  
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  const sections = analysis ? [
    {
      id: 'summary',
      title: 'Quick Summary',
      icon: MessagesSquare,
      color: 'from-blue-500/20 to-blue-600/20',
      borderColor: 'border-blue-500/30',
      content: analysis.summary
    },
    {
      id: 'technical',
      title: 'Technical Analysis',
      icon: Box,
      color: 'from-purple-500/20 to-purple-600/20',
      borderColor: 'border-purple-500/30',
      content: analysis.details.technical_analysis
    },
    {
      id: 'visual',
      title: 'Visual Elements',
      icon: Eye,
      color: 'from-green-500/20 to-green-600/20',
      borderColor: 'border-green-500/30',
      content: analysis.details.visual_elements
    },
    {
      id: 'strategic',
      title: 'Strategic Insights',
      icon: LineChart,
      color: 'from-orange-500/20 to-orange-600/20',
      borderColor: 'border-orange-500/30',
      content: analysis.details.strategic_insights
    },
    {
      id: 'context',
      title: 'Additional Context',
      icon: Book,
      color: 'from-pink-500/20 to-pink-600/20',
      borderColor: 'border-pink-500/30',
      content: analysis.details.additional_context
    }
  ] : [];

  const currentSection = sections.find(s => s.id === selectedSection) || sections[0];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/80 backdrop-blur-sm"
        />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-6xl p-6 bg-black/95 border border-white/10 rounded-xl h-[90vh] overflow-hidden z-[999]"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 rounded-full hover:bg-white/10 z-10"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>

          <div className="flex h-full gap-6">
            {/* Left side - Image and Input */}
            <div className="w-1/2 flex flex-col space-y-4">
              <div className="relative group rounded-lg overflow-hidden border border-white/10">
                <img
                  src={imageUrl}
                  alt="Analysis subject"
                  className="w-full object-cover rounded-lg"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent 
                  opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>

              <div className="relative">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask about specific aspects of this image..."
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white 
                    placeholder-gray-500 focus:border-green-500/50 focus:outline-none resize-none h-24"
                />
                <button
                  onClick={() => onAnalyze(query)}
                  disabled={isAnalyzing || !query.trim()}
                  className={`absolute bottom-3 right-3 p-2 rounded-full transition-all duration-200
                    ${query.trim() ? 
                      'bg-green-500 hover:bg-green-600 text-white' : 
                      'bg-white/5 text-gray-500 cursor-not-allowed'
                    }`}
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>

              {error && (
                <div className="text-red-400 bg-red-500/10 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {isAnalyzing && (
                <div className="flex items-center justify-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-green-500"></div>
                </div>
              )}
            </div>

            {/* Right side - Analysis Content */}
            <div className="w-1/2 flex flex-col space-y-4 overflow-hidden">
              {analysis && (
                <motion.div 
                  className="h-full flex flex-col space-y-4 overflow-y-auto pr-4"
                  initial="hidden"
                  animate="visible"
                  variants={containerVariants}
                >
                  {/* Navigation Tabs */}
                  <div className="flex flex-wrap gap-2">
                    {sections.map((section) => {
                      const Icon = section.icon;
                      const isSelected = selectedSection === section.id;
                      
                      return (
                        <motion.button
                          key={section.id}
                          onClick={() => setSelectedSection(section.id)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300
                            ${isSelected 
                              ? `bg-gradient-to-r ${section.color} border ${section.borderColor}` 
                              : 'bg-white/5 hover:bg-white/10 border border-white/10'
                            }`}
                          variants={itemVariants}
                        >
                          <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-gray-400'}`} />
                          <span className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-gray-400'}`}>
                            {section.title}
                          </span>
                        </motion.button>
                      );
                    })}
                  </div>

                  {/* Content Display */}
                  <motion.div
                    key={selectedSection}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      type: "spring",
                      stiffness: 100,
                      damping: 15
                    }}
                    className="flex-grow"
                  >
                    <Card className={`h-full bg-gradient-to-br ${currentSection.color} border ${currentSection.borderColor}`}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-white">
                          <currentSection.icon className="w-5 h-5" />
                          {currentSection.title}
                        </CardTitle>
                        <CardDescription className="text-white/60">
                          Detailed breakdown from {currentSection.title.toLowerCase()} perspective
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <motion.div 
                          className="prose prose-invert max-w-none"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          <p className="leading-relaxed text-white/90">
                            {currentSection.content}
                          </p>
                        </motion.div>
                      </CardContent>
                    </Card>
                  </motion.div>

                  {/* Timestamp */}
                  <motion.div 
                    className="text-xs text-gray-500 text-right"
                    variants={itemVariants}
                  >
                    Analysis generated on {new Date(analysis.timestamp).toLocaleString()}
                  </motion.div>
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ImageAnalysisComponent;