"use client"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Trophy,
  Users,
  UserCheck,
  BarChart,
  Calendar,
  LineChart,
  Video,
  Target,
  Award,
  ChevronRight,
  X
} from 'lucide-react';
import { useState } from "react";
import RosterGallery from "./RosterGallery";
import renderPlayerAwards from "./renderPlayerAwards";
import { motion } from "framer-motion";
import renderHomerunsData from "./renderHomeruns";

interface EndpointResultDialogProps {
  isOpen: boolean;
  onClose: () => void;
  endpoint: string;
  data: any;
  onImageAnalysis: (query: string) => Promise<void>;
}

// Helper to format numbers with commas
const formatNumber = (num: number): string => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

const EndpointResultDialog = ({ isOpen, onClose, endpoint, data, onImageAnalysis }: EndpointResultDialogProps) => {
  // Extract endpoint name without path
  const endpointName = endpoint;

  const renderChampionshipData = (data: any) => (
    <Card className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 border-yellow-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="w-5 h-5 text-yellow-500" />
          Championship History
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-black/20 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-yellow-400 mb-2">World Series</h3>
            <p className="text-3xl font-bold text-white mb-2">{data.world_series.total}</p>
            <p className="text-sm text-white/60">Last won: {data.world_series.last_won || 'Never'}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {data.world_series.titles.map((year: number) => (
                <span key={year} className="px-2 py-1 bg-yellow-500/20 rounded text-xs">
                  {year}
                </span>
              ))}
            </div>
          </div>
          <div className="bg-black/20 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-yellow-400 mb-2">League Pennants</h3>
            <p className="text-3xl font-bold text-white mb-2">{data.pennants.total}</p>
            <p className="text-sm text-white/60">Last won: {data.pennants.last_won || 'Never'}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {data.pennants.titles.map((year: number) => (
                <span key={year} className="px-2 py-1 bg-yellow-500/20 rounded text-xs">
                  {year}
                </span>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderRosterData = (data: any) => {
    const [searchTerm, setSearchTerm] = useState('');
    console.log('roster data:', data);
    
    const filteredPlayers = data.data.players.filter((player: any) => 
      player.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  
    return (
      <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border-blue-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-500" />
            Team Roster
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Simple Search */}
            <input
              type="text"
              placeholder="Search players..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white/10 rounded-md px-4 py-2 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
  
            {/* Player Image Gallery */}
            <RosterGallery
              players={filteredPlayers.map((player: any) => ({
                id: player.id || Math.random().toString(),
                name: player.name,
                imageUrl: player.imageUrl
              }))}
            />
          </div>
        </CardContent>
      </Card>
    );
  };
  const renderStatsData = (data: any) => (
    console.log('stats data:', data),
    <Card className="bg-gradient-to-br from-green-500/10 to-green-600/10 border-green-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart className="w-5 h-5 text-green-500" />
          Team Statistics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="batting" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="batting">Batting</TabsTrigger>
            <TabsTrigger value="pitching">Pitching</TabsTrigger>
            <TabsTrigger value="fielding">Fielding</TabsTrigger>
          </TabsList>
          <TabsContent value="batting" className="p-4">
            <div className="space-y-4">
              {Object.entries(data.stats.batting).map(([key, value]: [string, any]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="capitalize text-white/80">{key.replace('_', ' ')}</span>
                  <span className="font-mono text-white">{value}</span>
                </div>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="pitching" className="p-4">
            <div className="space-y-4">
              {Object.entries(data.stats.pitching).map(([key, value]: [string, any]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="capitalize text-white/80">{key.replace('_', ' ')}</span>
                  <span className="font-mono text-white">{value}</span>
                </div>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="fielding" className="p-4">
            <div className="space-y-4">
              {Object.entries(data.stats.fielding).map(([key, value]: [string, any]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="capitalize text-white/80">{key.replace('_', ' ')}</span>
                  <span className="font-mono text-white">{value}</span>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );

const renderRecentGames = (oldData: any) => {
  const data = oldData.data;
  const hasGames = data?.games && data.games.length > 0;

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
  };

  return (
    <Card className="bg-gradient-to-br from-blue-700/10 to-blue-800/10 border-blue-700/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-500" />
          Recent Games
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-white/60 mb-4">
          Period: {data?.period}
        </div>

        {!hasGames ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center justify-center p-8 bg-black/20 rounded-lg"
          >
            <X className="w-12 h-12 text-purple-500/50 mb-4" />
            <p className="text-lg font-medium text-white/70">No Recent Games Available</p>
            <p className="text-sm text-white/50 mt-2">Check back later for game updates</p>
          </motion.div>
        ) : (
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-3"
          >
            {data.games.map((game: any, index: number) => (
              <motion.div
                key={game.game_id || index}
                variants={item}
                className="bg-black/20 p-4 rounded-lg"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-white/80 font-medium">{game.opponent}</div>
                    <div className="text-sm text-white/60">{game.date} • {game.home_away.toUpperCase()}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">{game.score}</div>
                    <div className="text-sm text-white/60">{game.result}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
};

  const renderContent = () => {
   alert(endpointName)
    switch (endpointName) {
      case '/api/team/games/recent':
      case '/api/player/games/recent':
        return renderRecentGames(data);
      case '/api/player/awards':
        return renderPlayerAwards(data);
      case 'championships':
        return renderChampionshipData(data);
      case '/api/team/roster/current':
      case '/api/team/roster/all-time':
        return renderRosterData(data);
      case '/api/player/stats':
        return renderStatsData(data);
      case '/api/player/homeruns':
        return renderHomerunsData(data);
      default:
        return (
          <Card className="bg-gradient-to-br from-gray-500/10 to-gray-600/10 border-gray-500/20">
            <CardHeader>
              <CardTitle>Raw Data</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-black/30 p-4 rounded-lg overflow-x-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            </CardContent>
          </Card>
        );
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto bg-black/95 border-white/10">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold flex items-center gap-2">
            <ChevronRight className="w-5 h-5" />
            {endpointName.charAt(0).toUpperCase() + endpointName.slice(1)} Results
          </DialogTitle>
        </DialogHeader>
        {renderContent()}
      </DialogContent>
    </Dialog>
  );
};

export default EndpointResultDialog;