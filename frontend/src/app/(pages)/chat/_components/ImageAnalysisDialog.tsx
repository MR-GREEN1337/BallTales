"use client"

import { Button } from "@/components/ui/button";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import { Download, Send, X } from "lucide-react";
import { useState } from "react";

const ImageAnalysisDialog: React.FC<{ 
    isOpen: boolean;
    onClose: () => void;
    imageUrl: string;
  }> = ({ isOpen, onClose, imageUrl }) => {
    const [query, setQuery] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analyzedImageUrl, setAnalyzedImageUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
  
    const handleAnalyze = async () => {
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
  
        setAnalyzedImageUrl(response.data.resultImageUrl);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to analyze image');
      } finally {
        setIsAnalyzing(false);
      }
    };
  
    const handleDownload = async () => {
      if (!analyzedImageUrl) return;
      
      try {
        const response = await fetch(analyzedImageUrl);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'analyzed-image.png';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (err) {
        console.error('Download failed:', err);
      }
    };
  
    if (!isOpen) return null;
  
    return (
      <AnimatePresence>
        <div className="fixed inset-0 z-50 flex items-center justify-center">
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
            className="relative w-full max-w-2xl p-6 bg-black/95 border border-white/10 rounded-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-1 rounded-full hover:bg-white/10"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
  
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <img
                  src={analyzedImageUrl || imageUrl}
                  alt="Analysis"
                  className="w-full rounded-lg"
                />
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
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || !query.trim()}
                  className={`absolute bottom-3 right-3 p-2 rounded-full
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
  
              {analyzedImageUrl && (
                <Button
                  onClick={handleDownload}
                  className="w-full flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600"
                >
                  <Download className="w-4 h-4" />
                  Download Analyzed Image
                </Button>
              )}
            </div>
          </motion.div>
        </div>
      </AnimatePresence>
    );
  };

  export default ImageAnalysisDialog;