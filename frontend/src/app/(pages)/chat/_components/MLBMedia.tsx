import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

// TypeScript interfaces
interface MediaMetadata {
  exit_velocity?: number;
  launch_angle?: number;
  distance?: number;
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
}

const MLBMedia = ({ media }: MLBMediaProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!media) return null;

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
      
      case 'video':
        return (
          <div className="flex items-start gap-4 group hover:bg-white/5 p-4 rounded-lg transition-all">
            <div className="relative min-w-[200px]">
              <div className="aspect-video w-full">
                <iframe
                  src={mediaItem.url}
                  className="w-full h-full rounded-lg"
                  allowFullScreen
                />
              </div>
            </div>

            <div className="flex-1 space-y-4">
              {mediaItem.title && (
                <h4 className="font-semibold text-white">{mediaItem.title}</h4>
              )}
              
              {mediaItem.description && (
                <p className="text-sm text-gray-300">
                  <span className="float-left text-4xl font-serif font-bold mr-2 mt-1 text-blue-400">
                    {firstLetter}
                  </span>
                  {restOfText}
                </p>
              )}

              {mediaItem.metadata && (
                <div className="flex gap-4">
                  {mediaItem.metadata.exit_velocity && (
                    <div className="bg-blue-500/20 rounded-lg px-3 py-2">
                      <div className="text-xs text-gray-300">Exit Velocity</div>
                      <div className="font-semibold text-white">
                        {mediaItem.metadata.exit_velocity} mph
                      </div>
                    </div>
                  )}
                  {mediaItem.metadata.launch_angle && (
                    <div className="bg-blue-500/20 rounded-lg px-3 py-2">
                      <div className="text-xs text-gray-300">Launch Angle</div>
                      <div className="font-semibold text-white">
                        {mediaItem.metadata.launch_angle}°
                      </div>
                    </div>
                  )}
                  {mediaItem.metadata.distance && (
                    <div className="bg-blue-500/20 rounded-lg px-3 py-2">
                      <div className="text-xs text-gray-300">Distance</div>
                      <div className="font-semibold text-white">
                        {mediaItem.metadata.distance} ft
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  const mediaContent = Array.isArray(media) ? media : [media];
  const previewCount = mediaContent.length;

  return (
    <div className="mt-4 space-y-2">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full p-3 rounded-lg bg-gradient-to-r from-blue-500/20 to-blue-400/5 hover:from-blue-500/30 hover:to-blue-400/10 transition-all group"
      >
        <span className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">
          Baseball Media ({previewCount})
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
        <div className="space-y-2">
          {mediaContent.map((item, index) => (
            <div 
              key={index}
              className="first:rounded-t-lg last:rounded-b-lg border border-white/10 hover:border-white/20 transition-colors overflow-x-auto"
            >
              {renderMediaItem(item)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MLBMedia;