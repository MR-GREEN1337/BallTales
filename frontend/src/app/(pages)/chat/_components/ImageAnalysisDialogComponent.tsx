"use client"

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessagesSquare, 
  Box, 
  Eye, 
  LineChart, 
  Book, 
  Send, 
  X,
  Award,
  Calendar,
  Target,
  Trophy,
  Users,
  UserCheck,
  Video,
  BarChart
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface SuggestionItem {
  text: string;
  endpoint: string;
  icon: string;
}

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
  suggestions: SuggestionItem[];
}

interface ImageAnalysisProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  analysis: ImageAnalysisResponse | null;
  onAnalyze: (query: string) => Promise<void>;
  onSuggestionClick: (endpoint: string) => Promise<void>;
  isAnalyzing: boolean;
  isLoadingSuggestion: boolean;
  error: string | null;
  suggestionData: any | null;
}

interface Section {
  id: string;
  title: string;
  icon: React.ElementType;
  color: string;
  borderColor: string;
  content: string;
}

const SuggestionsSection: React.FC<{
  suggestions: SuggestionItem[];
  onSuggestionClick: (endpoint: string) => Promise<void>;
  isLoading: boolean;
}> = ({ suggestions, onSuggestionClick, isLoading }) => {
  const [selectedSuggestion, setSelectedSuggestion] = useState<string | null>(null);

  const getIconComponent = (iconName: string) => {
    const icons: { [key: string]: React.ElementType } = {
      Trophy, Users, UserCheck, BarChart, Calendar,
      LineChart, Video, Target, Award
    };
    return icons[iconName] || Box;
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, index) => {
          const Icon = getIconComponent(suggestion.icon);
          const isSelected = selectedSuggestion === suggestion.endpoint;
          
          return (
            <button
              key={index}
              onClick={() => {
                setSelectedSuggestion(suggestion.endpoint);
                onSuggestionClick(suggestion.endpoint);
              }}
              disabled={isLoading}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all
                ${isSelected 
                  ? 'bg-blue-500/20 border-blue-500/30' 
                  : 'bg-white/5 hover:bg-white/10 border-white/10'} 
                border text-sm font-medium text-white/90
                disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <Icon className="w-4 h-4" />
              <span>{suggestion.text}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

const ImageAnalysisComponent: React.FC<ImageAnalysisProps> = ({
  isOpen,
  onClose,
  imageUrl,
  analysis,
  onAnalyze,
  onSuggestionClick,
  isAnalyzing,
  isLoadingSuggestion,
  error,
  suggestionData
}) => {
  const [query, setQuery] = useState('');
  const [selectedSection, setSelectedSection] = useState<string>('summary');
  
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
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

  const sections: Section[] = analysis ? [
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
      <div className="fixed inset-0 z-[1500] flex items-center justify-center px-2 md:px-6"> {/* Increased z-index */}
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
          className="relative w-[95vw] md:w-full max-w-6xl p-4 md:p-6 bg-black/95 border border-white/10 rounded-xl h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 rounded-full hover:bg-white/10"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>

          <div className="flex flex-col md:flex-row h-full gap-4 md:gap-6 overflow-hidden">
            {/* Left side with image and input */}
            <div className="w-full md:w-1/2 flex flex-col space-y-4 min-h-[40vh] md:min-h-0 overflow-y-auto">
              <div className="relative group rounded-lg overflow-hidden border border-white/10 h-48 md:h-auto flex-shrink-0">
                <img
                  src={imageUrl}
                  alt="Analysis subject"
                  className="w-full h-full object-cover rounded-lg"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent 
                  opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>

              {/* Suggestions Section */}
              {analysis?.suggestions && (
                <div className="bg-black/30 rounded-lg p-4 border border-white/10 flex-shrink-0">
                  <h4 className="text-sm font-medium text-white/80 mb-3">Quick Actions</h4>
                  <SuggestionsSection
                    suggestions={analysis.suggestions}
                    onSuggestionClick={onSuggestionClick}
                    isLoading={isLoadingSuggestion}
                  />
                  
                  {/* Suggestion Data Display */}
                  {isLoadingSuggestion && (
                    <div className="mt-4 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
                    </div>
                  )}
                  {suggestionData && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-4 bg-white/5 rounded-lg p-4 overflow-x-auto"
                    >
                      <pre className="text-sm text-white/80 whitespace-pre-wrap">
                        {JSON.stringify(suggestionData, null, 2)}
                      </pre>
                    </motion.div>
                  )}
                </div>
              )}

              <div className="relative flex-shrink-0">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask about specific aspects..."
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
                <div className="text-red-400 bg-red-500/10 px-4 py-3 rounded-lg text-sm flex-shrink-0">
                  {error}
                </div>
              )}

              {isAnalyzing && (
                <div className="flex items-center justify-center py-4 flex-shrink-0">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-green-500"></div>
                </div>
              )}
            </div>

            {/* Right side with analysis content */}
            <div className="w-full md:w-1/2 flex flex-col space-y-4 overflow-hidden">
              {analysis && (
                <motion.div 
                  className="h-full flex flex-col space-y-4 overflow-y-auto pr-2 md:pr-4"
                  initial="hidden"
                  animate="visible"
                  variants={containerVariants}
                >
                  {/* Navigation Tabs */}
                  <div className="flex flex-nowrap md:flex-wrap gap-2 overflow-x-auto pb-2 md:pb-0 scrollbar-hide">
                    {sections.map((section) => {
                      const Icon = section.icon;
                      const isSelected = selectedSection === section.id;
                      
                      return (
                        <motion.button
                          key={section.id}
                          onClick={() => setSelectedSection(section.id)}
                          className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300
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
                    className="flex-grow min-h-[30vh] md:min-h-0 overflow-hidden"
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
                          className="prose prose-invert max-w-none overflow-y-auto max-h-[40vh] md:max-h-[50vh]"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          <p className="leading-relaxed text-white/90 whitespace-pre-wrap">
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

// Type guard for suggestion data
function isSuggestionDataValid(data: any): data is any {
  return data && typeof data === 'object';
}

export default ImageAnalysisComponent;