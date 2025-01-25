"use client"

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Book, Eye, LineChart, MessagesSquare } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

// Define our interfaces for type safety
export interface AnalysisResponse {
  summary: string;
  details: {
    technical_analysis: string;
    visual_elements: string;
    strategic_insights: string;
    additional_context: string;
  };
  timestamp: string;
  request_id: string;
}

const VideoAnalysis = ({ analysis }: { analysis: AnalysisResponse | null }) => {
  if (!analysis) {
    return null;
  }
  const [selectedSection, setSelectedSection] = useState<string>('summary');
  
  // Animation variants for our content sections
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

  // Section configuration with icons and colors
  const sections = [
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
      icon: Activity,
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
  ];

  const currentSection = sections.find(s => s.id === selectedSection) || sections[0];

  return (
    <motion.div 
      className="space-y-6"
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
      >
        <Card className={`bg-gradient-to-br ${currentSection.color} border ${currentSection.borderColor}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <currentSection.icon className="w-5 h-5" />
              {currentSection.title}
            </CardTitle>
            <CardDescription className="text-white/60">
              Detailed breakdown of the play from {currentSection.title.toLowerCase()} perspective
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

      {/* Timestamp Footer */}
      <motion.div 
        className="text-xs text-gray-500 text-right"
        variants={itemVariants}
      >
        Analysis generated on {new Date(analysis.timestamp).toLocaleString()}
      </motion.div>
    </motion.div>
  );
};

export default VideoAnalysis;