"use client"

import { useState } from "react";
import axios from "axios";
import ImageAnalysisComponent from './ImageAnalysisDialogComponent';

const ImageAnalysisDialog: React.FC<{ 
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
}> = ({ isOpen, onClose, imageUrl }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (query: string) => {
    setError(null);
    setIsAnalyzing(true);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/analyze-image`,
        {
          imageUrl,
          query: query.trim()
        }
      );

      setAnalysis(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze image');
    } finally {
      setIsAnalyzing(false);
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
    />
  );
};

export default ImageAnalysisDialog;