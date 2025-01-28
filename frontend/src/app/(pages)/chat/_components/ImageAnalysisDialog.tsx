"use client"

import { useState } from "react";
import axios from "axios";
import ImageAnalysisComponent from './ImageAnalysisDialogComponent';

// Shared interfaces to ensure type consistency
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

interface ImageAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
}

const ImageAnalysisDialog: React.FC<ImageAnalysisDialogProps> = ({ 
  isOpen, 
  onClose, 
  imageUrl 
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ImageAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [suggestionData, setSuggestionData] = useState<any | null>(null);
  const [isLoadingSuggestion, setIsLoadingSuggestion] = useState(false);

  const handleAnalyze = async (query: string) => {
    if (!query.trim()) return;
    
    setError(null);
    setIsAnalyzing(true);
    setSuggestionData(null);

    try {
      const response = await axios.post<ImageAnalysisResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/analyze-image`,
        {
          imageUrl,
          message: query.trim()
        }
      );

      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid response format');
      }

      setAnalysis(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze image');
      setAnalysis(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSuggestionClick = async (endpoint: string) => {
    if (!endpoint) return;
    
    setIsLoadingSuggestion(true);
    setSuggestionData(null);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/${endpoint.replaceAll('/', '_')}`,
        null,  // empty body since we're using query params
        {
          params: {
            mediaUrl: imageUrl
          }
        }
      );
      if (!response.data) {
        throw new Error('No data received from suggestion endpoint');
      }

      setSuggestionData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load suggestion data');
      setSuggestionData(null);
    } finally {
      setIsLoadingSuggestion(false);
    }
  };

  return (
    <ImageAnalysisComponent
      isOpen={isOpen}
      onClose={onClose}
      imageUrl={imageUrl}
      analysis={analysis}
      onAnalyze={handleAnalyze}
      isAnalyzing={isAnalyzing}
      error={error}
      suggestionData={suggestionData}
      isLoadingSuggestion={isLoadingSuggestion}
      onSuggestionClick={handleSuggestionClick}
    />
  );
};

export default ImageAnalysisDialog;