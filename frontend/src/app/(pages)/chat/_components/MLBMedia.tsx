import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Grid2X2, Play, Search } from 'lucide-react';
import {
  Dialog,
  DialogContent,
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

// VideoPlayer component remains the same
const VideoPlayer: React.FC<{ video: MediaItem }> = ({ video }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

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
    <div 
      className="relative aspect-video w-full bg-black/30 rounded-lg overflow-hidden group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {!isPlaying ? (
        <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 ease-in-out" />
          
          <img
            src={thumbnailUrl}
            alt={video.title || "Video thumbnail"}
            className={`absolute inset-0 w-full h-full object-cover transition-all duration-700 ease-in-out
              ${isHovered ? 'scale-110 blur-sm brightness-75' : 'scale-100 blur-none brightness-100'}
            `}
          />
          
          <div className="relative z-10 transform transition-all duration-500 ease-in-out">
            <button
              onClick={handlePlayClick}
              className={`relative p-4 rounded-full bg-blue-500/90 hover:bg-blue-500 
                transition-all duration-500 ease-in-out group/button
                ${isHovered ? 'scale-110 shadow-lg shadow-blue-500/20' : 'scale-100'}
              `}
              aria-label="Play video"
            >
              <div className="absolute inset-0 rounded-full bg-blue-400/20 animate-ping" />
              <Play className={`w-8 h-8 text-white transition-all duration-500 ease-in-out
                ${isHovered ? 'scale-110' : 'scale-100'}
              `} />
              
              <div className={`absolute inset-0 rounded-full border-2 border-white/30
                transition-all duration-500 ease-in-out
                ${isHovered ? 'scale-110 opacity-100' : 'scale-90 opacity-0'}
              `} />
            </button>
          </div>
          
          {video.title && (
            <div className={`absolute bottom-0 left-0 right-0 p-4 transform transition-all duration-500 ease-in-out
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
  
  // Filter videos based on search query
  const filteredVideos = videos.filter(video => 
    video.title?.toLowerCase().includes(searchQuery.toLowerCase()) || !searchQuery
  );

  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="w-full flex items-center justify-center gap-2 p-4 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg transition-all">
          <Grid2X2 className="w-5 h-5" />
          <span>View All Videos ({videos.length})</span>
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-6xl w-full h-full max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Home Run Gallery</DialogTitle>
        </DialogHeader>
        
        {/* Search Bar */}
        <div className="px-4 pt-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search home runs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-black/20 border-white/10 focus:border-blue-500/50 transition-colors"
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
                <CardTitle className="text-sm font-medium line-clamp-2">
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
      </DialogContent>
    </Dialog>
  );
};

// MLBMedia component remains largely the same
const MLBMedia: React.FC<MLBMediaProps> = ({ media, chart }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  if (!media) return null;

  const mediaContent = Array.isArray(media) ? media : [media];
  const videos = mediaContent.filter(item => item.type === 'video');
  const images = mediaContent.filter(item => item.type === 'image');

  const renderMediaItem = (mediaItem: MediaItem) => {
    const firstLetter = mediaItem.description?.charAt(0) || '';
    const restOfText = mediaItem.description?.slice(1) || '';

    switch (mediaItem.type) {
      case 'image':
        return (
          <div className="flex items-start gap-4 group hover:bg-white/5 p-4 rounded-lg transition-all">
            <div className="relative min-w-[100px]">
              <img
                src={mediaItem.url}
                alt={mediaItem.description || "MLB Media"}
                className="w-24 h-24 rounded-lg object-contain bg-white/5 p-2"
              />
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent rounded-lg -z-10" />
            </div>

            {mediaItem.description && (
              <div className="flex-1 prose prose-invert">
                <p className="leading-relaxed">
                  <span className="float-left text-4xl font-serif font-bold mr-2 mt-1 text-blue-400">
                    {firstLetter}
                  </span>
                  {restOfText}
                </p>
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