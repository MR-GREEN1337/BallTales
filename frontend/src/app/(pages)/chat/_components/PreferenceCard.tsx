import React from 'react';
import { ImageIcon } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface PreferenceCardProps {
  title: string;
  value: string;
  description?: string;
  url?: string;
  onImageAnalysis?: () => void;
}

const PreferenceCard: React.FC<PreferenceCardProps> = ({
  title,
  value,
  description,
  url,
  onImageAnalysis
}) => {
  const handleAnalyzeClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onImageAnalysis?.();
  };

  return (
    <div 
      className="bg-gray-800/50 p-3 rounded-lg space-y-2 hover:bg-gray-800/70 transition-colors duration-200"
      role="article"
      aria-labelledby={`preference-title-${title}`}
    >
      <p 
        id={`preference-title-${title}`}
        className="text-xs text-gray-400"
      >
        {title}
      </p>
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium truncate flex-1 mr-2">{value}</p>
          {url && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={handleAnalyzeClick}
                    className="relative group w-8 h-8 rounded-full overflow-hidden hover:ring-2 hover:ring-blue-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    aria-label={`Analyze ${value} image`}
                  >
                    <img 
                      src={url}
                      alt={value}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = "/placeholder.png";
                        e.currentTarget.className = "w-full h-full object-cover opacity-50";
                      }}
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors duration-200" />
                  </button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Analyze {value} image</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
        {description && (
          <p 
            className="text-xs text-gray-400 line-clamp-2 transition-all duration-200 hover:line-clamp-none"
            title={description}
          >
            {description}
          </p>
        )}
      </div>
    </div>
  );
};

export default PreferenceCard;