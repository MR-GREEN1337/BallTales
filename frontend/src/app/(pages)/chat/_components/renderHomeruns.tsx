import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Target } from 'lucide-react';
import { VideoGrid } from './MLBMedia';

// TypeScript Interfaces
interface HomerunMetadata {
  exit_velocity: number;
  launch_angle: number;
  distance: number;
}

interface HomerunVideo {
  type: 'video';
  url: string;
  title?: string;
}

interface Homerun {
  year: number;
  description: string;
  metadata: HomerunMetadata;
  video: HomerunVideo;
}

interface HomerunMetrics {
  avg_distance: number;
  avg_exit_velocity: number;
  avg_launch_angle: number;
  longest_homerun: number;
  highest_exit_velocity: number;
}

interface HomerunData {
  data: {
    player_name: string;
    total_homeruns: number;
    homeruns: Homerun[];
    metrics: HomerunMetrics;
  };
}

interface StatItem {
  label: string;
  value: string;
  bgColor: string;
}

// Format stats with proper typing
const formatStats = (metrics: HomerunMetrics): StatItem[] => {
  return [
    {
      label: "Average Distance",
      value: `${Math.round(metrics.avg_distance)} ft`,
      bgColor: "bg-slate-800/80"
    },
    {
      label: "Average Exit Velocity",
      value: `${Math.round(metrics.avg_exit_velocity)} mph`,
      bgColor: "bg-slate-800/80"
    },
    {
      label: "Average Launch Angle",
      value: `${Math.round(metrics.avg_launch_angle)}°`,
      bgColor: "bg-slate-800/80"
    },
    {
      label: "Longest Home Run",
      value: `${Math.round(metrics.longest_homerun)} ft`,
      bgColor: "bg-slate-800/80"
    },
    {
      label: "Highest Exit Velocity",
      value: `${metrics.highest_exit_velocity} mph`,
      bgColor: "bg-slate-800/80"
    }
  ];
};

const renderHomerunsData = ({ data }: HomerunData) => {
  // Transform homeruns data for VideoGrid
  const videos = data.homeruns.map(hr => ({
    type: 'video' as const,
    url: hr.video.url,
    title: hr.description,
    metadata: {
      exit_velocity: hr.metadata.exit_velocity,
      launch_angle: hr.metadata.launch_angle,
      distance: hr.metadata.distance,
      year: hr.year
    }
  }));

  const stats = formatStats(data.metrics);

  return (
    <div className="space-y-6">
      {/* Player Info & Stats */}
      <Card className="bg-slate-900/90 border-slate-800 shadow-xl">
        <CardHeader className="border-b border-slate-800">
          <CardTitle className="flex items-center gap-2 text-slate-100">
            <Target className="w-5 h-5 text-blue-400" />
            Home Run Statistics
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-slate-100 mb-2">
              {data.player_name}
            </h3>
            <p className="text-slate-400">
              Total Home Runs: {data.total_homeruns}
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {stats.map((stat, index) => (
              <div 
                key={index} 
                className={`${stat.bgColor} rounded-lg p-4 border border-slate-700/50 hover:border-slate-600/50 transition-colors
                  shadow-lg backdrop-blur-sm`}
              >
                <div className="text-xs text-slate-400 font-medium">
                  {stat.label}
                </div>
                <div className="text-lg font-bold text-slate-100 mt-1">
                  {stat.value}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Video Grid */}
      <Card className="bg-slate-900/90 border-slate-800 shadow-xl">
        <CardContent className="p-6">
          <ScrollArea className="h-[calc(100vh-24rem)]">
          <VideoGrid 
  videos={videos} 
  disableDialog={true}
  className="z-[3001]"
/>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default renderHomerunsData;