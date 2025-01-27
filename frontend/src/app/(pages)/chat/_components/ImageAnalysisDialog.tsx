"use client"

import { useState } from "react";
import axios from "axios";
import ImageAnalysisComponent from './ImageAnalysisDialogComponent';

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
  suggestions: Array<{
    text: string;
    endpoint: string;
    icon: string;
  }>;
}

const ImageAnalysisDialog: React.FC<{ 
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
}> = ({ isOpen, onClose, imageUrl }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ImageAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [suggestionData, setSuggestionData] = useState<any | null>(null);
  const [isLoadingSuggestion, setIsLoadingSuggestion] = useState(false);

  const handleAnalyze = async (query: string) => {
    setError(null);
    setIsAnalyzing(true);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/analyze-image`,
        {
          imageUrl,
          message: query.trim()
        }
      );
      console.log('Analysis response:', response.data);
      setAnalysis(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze image');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSuggestionClick = async (endpoint: string) => {
    setIsLoadingSuggestion(true);
    setSuggestionData(null);
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/${endpoint}`,
        {
          params: { mediaUrl: imageUrl }
        }
      );
      setSuggestionData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load suggestion data');
    } finally {
      setIsLoadingSuggestion(false);
    }
  };

  return (
    <div className="relative">
      <ImageAnalysisComponent
        isOpen={isOpen}
        onClose={onClose}
        imageUrl={imageUrl}
        analysis={analysis as any}
        onAnalyze={handleAnalyze}
        isAnalyzing={isAnalyzing}
        error={error}
        suggestionData={suggestionData}
        isLoadingSuggestion={isLoadingSuggestion}
        onSuggestionClick={handleSuggestionClick}
      />
    </div>
  );
};

export default ImageAnalysisDialog;