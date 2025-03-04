"use client"

import { useState } from "react";
import axios from "axios";
import ImageAnalysisComponent from './ImageAnalysisDialogComponent';
import EndpointResultDialog from './EndpointResultDialog';
import { NEXT_PUBLIC_API_URL } from "@/lib/constants";
import { api } from "@/lib/utils";

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
  const [activeEndpoint, setActiveEndpoint] = useState<string>('');
  const [showEndpointDialog, setShowEndpointDialog] = useState(false);

  const handleAnalyze = async (query: string) => {
    if (!query.trim()) return;
    
    setError(null);
    setIsAnalyzing(true);
    setSuggestionData(null);
    //alert(localStorage.getItem('userLang'))
    try {
      const response = await api.post<ImageAnalysisResponse>(
        `${NEXT_PUBLIC_API_URL}/chat/analyze-image`,
        {
          imageUrl,
          userLang: localStorage.getItem('userLang'),
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
    setActiveEndpoint(endpoint);

    try {
      const response = await api.post(
        `${NEXT_PUBLIC_API_URL}/chat/${endpoint.replaceAll('/', '_')}`,
        null,
        {
          params: {
            userLang: localStorage.getItem('userLang'),
            mediaUrl: imageUrl
          }
        }
      );
      
      if (!response.data) {
        throw new Error('No data received from suggestion endpoint');
      }

      setSuggestionData(response.data);
      setShowEndpointDialog(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load suggestion data');
      setSuggestionData(null);
    } finally {
      setIsLoadingSuggestion(false);
    }
  };

  const handleEndpointDialogClose = () => {
    setShowEndpointDialog(false);
    setSuggestionData(null);
    setActiveEndpoint('');
  };

  return (
    <>
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
      
      {suggestionData && showEndpointDialog && (
        <EndpointResultDialog
          isOpen={showEndpointDialog}
          onClose={handleEndpointDialogClose}
          endpoint={activeEndpoint}
          data={suggestionData}
          onImageAnalysis={handleAnalyze}
        />
      )}
    </>
  );
};

export default ImageAnalysisDialog;