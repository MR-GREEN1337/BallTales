"use client"

import React, { useEffect, useRef, useState } from 'react';
import { BarChart3, ChevronDown, ChevronUp, Grid2X2, Play, Search, Send, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import MLBStatistics from './MLBStatistics';
import { AnimatePresence, motion } from 'framer-motion';
import axios from 'axios';
import ImageAnalysisDialog from './ImageAnalysisDialog';
import VideoAnalysis, { AnalysisResponse } from './VideoAnalysis';

// TypeScript interfaces remain the same
interface MediaMetadata {
  exit_velocity?: number;
  launch_angle?: number;
  distance?: number;
  year?: number;
}

interface MediaItem {
  type: 'image' | 'video';
  url: string;
  description?: string;
  title?: string;
  metadata?: MediaMetadata;
}

interface MLBMediaProps {
  media: MediaItem | MediaItem[];
  chart: any;
}

interface MediaStatsProps {
  metadata: MediaMetadata;
}

const VIDEO_GALLERY_THRESHOLD = 3;

// MediaStats component remains the same
const MediaStats: React.FC<MediaStatsProps> = ({ metadata }) => (
  <div className="flex flex-wrap gap-2">
    {metadata.exit_velocity && (
      <div className="bg-blue-500/20 rounded-lg px-3 py-2">
        <div className="text-xs text-gray-300">Exit Velocity</div>
        <div className="font-semibold text-white">
          {metadata.exit_velocity} mph
        </div>
      </div>
    )}
    {metadata.launch_angle && (
      <div className="bg-blue-500/20 rounded-lg px-3 py-2">
        <div className="text-xs text-gray-300">Launch Angle</div>
        <div className="font-semibold text-white">
          {metadata.launch_angle}°
        </div>
      </div>
    )}
    {metadata.distance && (
      <div className="bg-blue-500/20 rounded-lg px-3 py-2">
        <div className="text-xs text-gray-300">Distance</div>
        <div className="font-semibold text-white">
          {metadata.distance} ft
        </div>
      </div>
    )}
    {metadata.year && (
      <div className="bg-blue-500/20 rounded-lg px-3 py-2">
        <div className="text-xs text-gray-300">Season</div>
        <div className="font-semibold text-white">
          {metadata.year}
        </div>
      </div>
    )}
  </div>
);

interface AnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  videoUrl: string;
}
const AnalysisDialog: React.FC<AnalysisDialogProps> = ({ 
  isOpen, 
  onClose,
  videoUrl
}) => {
  const [message, setMessage] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const handleAnalyze = async () => {
    setError(null);
    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      const response = await axios.post<AnalysisResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/analyze-video`,
        {
          videoUrl,
          message: message.trim()
        }
      );
      
      // response.data is already parsed by axios
      setAnalysisResult(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze video');
    } finally {
      setIsAnalyzing(false);
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
        
        <div className="relative w-full max-w-4xl px-4">
          <span className="inline-block h-screen align-middle" aria-hidden="true">
            &#8203;
          </span>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", duration: 0.5 }}
            className="inline-block w-full max-w-4xl p-6 my-8 text-left align-middle bg-black/95 
              border border-white/10 rounded-xl shadow-2xl transform transition-all relative"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-1 rounded-full hover:bg-white/10 
                transition-colors duration-200"
            >
              <X className="w-5 h-5 text-gray-400 hover:text-white" />
            </button>

            <div className="mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-green-500" />
                Video Analysis
              </h3>
            </div>

            <div className="mb-6">
              <VideoPlayer video={{ type: 'video', url: videoUrl }} />
            </div>
    
            <div className="space-y-6">
              {/* Message Input Section */}
              <div className="space-y-2">
                <div className="relative">
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Ask about specific aspects of this play..."
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white 
                      placeholder-gray-500 focus:border-green-500/50 focus:ring-0 focus:outline-none
                      transition-colors resize-none h-24"
                  />
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || !message.trim()}
                    className={`absolute bottom-3 right-3 p-2 rounded-full transition-all duration-200
                      ${message.trim() ? 
                        'bg-green-500 hover:bg-green-600 text-white' : 
                        'bg-white/5 text-gray-500 cursor-not-allowed'
                      }`}
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="text-red-400 bg-red-500/10 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {/* Loading State */}
              {isAnalyzing && (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-green-500"></div>
                </div>
              )}

              {/* Analysis Result */}
              {analysisResult && (
                <VideoAnalysis analysis={analysisResult} />
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </AnimatePresence>
  );
};

// Enhanced VideoPlayer component with mobile-friendly analysis button
const VideoPlayer: React.FC<{ video: MediaItem, onAnalyze?: () => void }> = ({ video, onAnalyze }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);

  // Handle analysis button click with smooth scrolling
  const handleAnalysisClick = () => {
    const element = containerRef.current;
    if (!element) {
      // If we can't get the element, still show the dialog
      setShowAnalysis(true);
      if (onAnalyze) onAnalyze();
      return;
    }

    const rect = element.getBoundingClientRect();
    const isOffscreen = rect.top < 0 || rect.bottom > window.innerHeight;

    if (isOffscreen) {
      const targetPosition = window.scrollY + rect.top - 20;
      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
      });
      // Wait for scroll to complete before showing dialog
      setTimeout(() => {
        setShowAnalysis(true);
        if (onAnalyze) onAnalyze();
      }, 300);
    } else {
      // If not offscreen, show dialog immediately
      setShowAnalysis(true);
      if (onAnalyze) onAnalyze();
    }
  };

  // Detect touch device on mount
  useEffect(() => {
    setIsTouchDevice('ontouchstart' in window);
  }, []);

  const handlePlayClick = () => {
    setIsPlaying(true);
  };

  const getRandomImageNum = () => {
    return Math.floor(Math.random() * 30) + 1;
  };
  
  const formatImageNum = (num: number) => {
    return num.toString().padStart(6, '0');
  };
  
  const thumbnailUrl = `/homeruns/${formatImageNum(getRandomImageNum())}.jpg`;

  return (
    <>
      <div 
        className="relative aspect-video w-full bg-black/30 rounded-lg overflow-hidden group"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {!isPlaying ? (
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent 
              opacity-0 group-hover:opacity-100 md:transition-opacity md:duration-500 md:ease-in-out" 
            />
            
            <img
              src={thumbnailUrl}
              alt={video.title || "Video thumbnail"}
              className={`absolute inset-0 w-full h-full object-cover md:transition-all md:duration-700 md:ease-in-out
                ${isHovered ? 'scale-110 blur-sm brightness-75' : 'scale-100 blur-none brightness-100'}
              `}
            />
            
            <div className="relative z-2 transform md:transition-all md:duration-500 md:ease-in-out">
              <button
                onClick={handlePlayClick}
                className="relative p-4 rounded-full bg-blue-500/90 hover:bg-blue-500 
                  transition-all duration-500 ease-in-out group/button"
                aria-label="Play video"
              >
                <div className="absolute inset-0 rounded-full bg-blue-400/20 animate-ping" />
                <Play className="w-8 h-8 text-white" />
              </button>
            </div>

            <motion.button
              onClick={handleAnalysisClick}
              className={`absolute bottom-4 right-4 flex items-center gap-0 overflow-hidden
                bg-green-700/90 hover:bg-green-800 rounded-full text-sm font-medium text-white
                transform transition-all duration-500 ease-out group/analyze
                ${isTouchDevice ? 'opacity-100 px-3' : 'opacity-0 group-hover:opacity-100 group-hover:px-3 px-2'}
                hover:shadow-lg hover:shadow-green-500/20 py-2
                ${isTouchDevice ? 'gap-2' : 'group-hover:gap-2'}`}
            >
              <BarChart3 className={`w-4 h-4 transition-transform duration-500 ease-out
                ${isTouchDevice ? 'rotate-0' : 'group-hover:rotate-0 rotate-12'}`} 
              />
              <span className={`overflow-hidden transition-all duration-500 ease-out
                ${isTouchDevice ? 
                  'w-auto opacity-100' : 
                  'w-0 group-hover:w-14 opacity-0 group-hover:opacity-100'
                }`}>
                Analyze
              </span>
              
              {/* Subtle background pulse effect */}
              <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100">
                <div className="absolute inset-0 bg-white/20 rounded-full animate-ping-slow" />
              </div>
              
              {/* Elegant border animation */}
              <div className={`absolute inset-0 rounded-full border border-white/20
                transition-all duration-500 ease-out scale-50 opacity-0
                group-hover:scale-100 group-hover:opacity-100`} 
              />
            </motion.button>

            {video.title && (
              <div className={`absolute bottom-0 left-0 right-16 p-4 transform transition-all duration-500 ease-in-out
                ${isHovered ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}
              `}>
                <h4 className="text-white font-medium text-shadow-lg line-clamp-2">
                  {video.title}
                </h4>
              </div>
            )}
          </div>
        ) : (
          <iframe
            src={`${video.url}?autoplay=1`}
            className="w-full h-full"
            allow="autoplay; encrypted-media"
            allowFullScreen
          />
        )}
      </div>

      <AnalysisDialog
        isOpen={showAnalysis}
        onClose={() => setShowAnalysis(false)}
        videoUrl={video.url}
      />
    </>
  );
};

// SingleVideo component remains the same
const SingleVideo: React.FC<{ video: MediaItem }> = ({ video }) => (
  <div className="border border-white/10 hover:border-white/20 transition-colors rounded-lg overflow-hidden">
    <div className="p-4 space-y-4">
      {video.title && (
        <h4 className="font-semibold text-white">{video.title}</h4>
      )}
      <VideoPlayer video={video} />
      {video.metadata && <MediaStats metadata={video.metadata} />}
    </div>
  </div>
);

// Updated VideoGrid component with search functionality
const VideoGrid: React.FC<{ videos: MediaItem[] }> = ({ videos }) => {
  const [searchQuery, setSearchQuery] = useState('');
  
  const filteredVideos = videos.filter(video => 
    video.title?.toLowerCase().includes(searchQuery.toLowerCase()) || !searchQuery
  );

  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="w-full flex items-center justify-center gap-2 p-1 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg transition-all">
          <Grid2X2 className="w-5 h-5" />
          <span className='text-muted-foreground text-sm'>View All Videos ({videos.length})</span>
        </button>
      </DialogTrigger>
      <DialogContent className="fixed inset-0 z-[100] flex items-center justify-center">
        <div className="bg-black/90 border border-white/10 w-full max-w-6xl h-[90vh] rounded-lg overflow-hidden flex flex-col">
          <DialogHeader className="p-4 border-b border-white/10">
            <DialogTitle className="text-white">Home Run Gallery</DialogTitle>
          </DialogHeader>
          
          <div className="flex-1 overflow-y-auto">
            <div className="sticky top-0 z-10 bg-black/95 px-4 pt-2 pb-2 border-b border-white/10">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search home runs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-black/20 border-white/10 focus:border-blue-500/50 transition-colors text-white"
                />
              </div>
              <div className="mt-2 text-sm text-gray-400">
                Showing {filteredVideos.length} of {videos.length} videos
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
              {filteredVideos.map((video, index) => (
                <Card 
                  key={index} 
                  className="overflow-hidden bg-black/50 hover:bg-black/60 transition-colors border-white/10 hover:border-white/20"
                >
                  <CardHeader className="space-y-2">
                    <CardTitle className="text-sm font-medium line-clamp-2 text-white">
                      {video.title}
                    </CardTitle>
                    {video.metadata && (
                      <CardDescription>
                        <MediaStats metadata={video.metadata} />
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent className="p-0">
                    <VideoPlayer video={video} />
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// MLBMedia component remains largely the same
const MLBMedia: React.FC<MLBMediaProps> = ({ media, chart }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  // Track both whether dialog is open and which image is selected
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  if (!media) return null;

  const mediaContent = Array.isArray(media) ? media : [media];
  const videos = mediaContent.filter(item => item.type === 'video');
  const images = mediaContent.filter(item => item.type === 'image');

  const renderMediaItem = (mediaItem: MediaItem) => {
    switch (mediaItem.type) {
      case 'image':
        return (
          <div className="flex items-start gap-4 group hover:bg-white/5 p-4 rounded-lg transition-all">
            <div className="relative min-w-[100px]">
              <img
                src={mediaItem.url}
                alt={mediaItem.description || "MLB Media"}
                className="w-24 h-24 rounded-lg object-contain bg-white/5 p-2 cursor-pointer"
                onClick={() => setSelectedImage(mediaItem.url)}
              />
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent rounded-lg -z-10" />
            </div>

            {mediaItem.description && (
              <div className="flex-1 prose prose-invert">
                <p className="leading-relaxed">{mediaItem.description}</p>
              </div>
            )}
          </div>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <div className="mt-4 space-y-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full p-3 rounded-lg bg-gradient-to-r from-blue-500/20 to-blue-400/5 hover:from-blue-500/30 hover:to-blue-400/10 transition-all group"
      >
        <span className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">
          Baseball Media ({mediaContent.length})
        </span>
        <div className="flex items-center gap-2">
          <div className="text-xs text-gray-400">
            {isExpanded ? 'Click to collapse' : 'Click to expand'}
          </div>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-300" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-300" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="space-y-4">
          {videos.length > 0 && (
            <div className="space-y-4">
              {videos.length >= VIDEO_GALLERY_THRESHOLD ? (
                <VideoGrid videos={videos} />
              ) : (
                videos.map((video, index) => (
                  <SingleVideo key={index} video={video} />
                ))
              )}
            </div>
          )}
          
          {images.length > 0 && (
            <div className="space-y-2">
              {images.map((item, index) => (
                <div 
                  key={index}
                  className="first:rounded-t-lg last:rounded-b-lg border border-white/10 hover:border-white/20 transition-colors"
                >
                  {renderMediaItem(item)}
                </div>
              ))}
            </div>
          )}
          
          {/* Image Analysis Dialog */}
          {selectedImage && (
            <ImageAnalysisDialog
              isOpen={!!selectedImage}
              onClose={() => setSelectedImage(null)}
              imageUrl={selectedImage}
            />
          )}
          
          {chart && chart.requires_chart && (
            <div className="mt-8">
              <MLBStatistics chart={chart} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MLBMedia;