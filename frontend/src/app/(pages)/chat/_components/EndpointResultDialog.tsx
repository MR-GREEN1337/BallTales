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
  X,
  MapPin,
  Building2,
  Star
} from 'lucide-react';
import { useState } from "react";
import RosterGallery from "./RosterGallery";
import renderPlayerAwards from "./renderPlayerAwards";
import { motion } from "framer-motion";
import renderHomerunsData from "./renderHomeruns";
import { getEndpointTitle } from "@/lib/constants";
import MLBStatistics from "./MLBStatistics";
import renderGames from "./renderRecentGames";

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
  console.log("EndpointResultDialog", endpoint, data.data.data);
  // Extract endpoint name without path
  const endpointName = endpoint;

  interface TeamData {
    name: string;
    firstYearOfPlay: string;
    locationName: string;
    venue: {
      name: string;
    };
    league: {
      name: string;
    };
    division: {
      name: string;
    };
  }
  

  const ChampionshipHistory = ({ oldData }: any) => {
    const data = oldData.data;
    const startYear = data.first_season;
    const currentYear = new Date().getFullYear();
    const yearsActive = currentYear - startYear;
  
    // Helper function to display years with "more" indicator
    const displayYears = (years: any, limit = 5) => {
      if (!years || years.length === 0) return [];
      const displayedYears = years.slice(0, limit);
      const remaining = years.length - limit;
      return (
        <div className="flex flex-wrap gap-2">
          {displayedYears.map((year: any) => (
            <span key={year} className="px-2 py-1 bg-yellow-900/30 rounded text-xs text-zinc-300">
              {year}
            </span>
          ))}
          {remaining > 0 && (
            <span className="px-2 py-1 bg-yellow-900/30 rounded text-xs text-zinc-300">
              +{remaining} more
            </span>
          )}
        </div>
      );
    };
  
    // Helper function for championship section
    const ChampionshipSection = ({ title, total, lastWon, years }: any) => (
      <div className="bg-zinc-800/80 rounded-lg p-4">
        <div className="border-b border-zinc-700 pb-3 mb-3">
          <h3 className="text-lg font-semibold text-yellow-500 mb-1">{title}</h3>
          <p className="text-4xl font-bold text-zinc-200">{total}</p>
          <p className="text-sm text-zinc-400">
            {lastWon ? `Last won: ${lastWon}` : 'No championships yet'}
          </p>
        </div>
        {displayYears(years)}
      </div>
    );
  
    return (
      <Card className="bg-zinc-900 border-yellow-900/50">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-yellow-500">
            <Trophy className="w-5 h-5" />
            {data.team_name} History
          </CardTitle>
          <div className="flex flex-wrap gap-4 text-sm text-zinc-400">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              Est. {data.first_season}
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              {data.venue.city}
            </div>
            <div className="flex items-center gap-1">
              <Building2 className="w-4 h-4" />
              {data.venue.name}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Team Legacy */}
            <div className="bg-zinc-800/80 rounded-lg p-4 md:col-span-2 lg:col-span-1">
              <h3 className="text-lg font-semibold text-yellow-500 mb-2 flex items-center gap-2">
                <Star className="w-4 h-4" />
                Team Legacy
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Years Active</span>
                  <span className="text-zinc-200 font-semibold">{yearsActive}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">League</span>
                  <span className="text-zinc-200 font-semibold">{data.league}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Division</span>
                  <span className="text-zinc-200 font-semibold">{data.division}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Championship Drought</span>
                  <span className="text-zinc-200 font-semibold">{data.stats.championship_drought} years</span>
                </div>
              </div>
            </div>
  
            {/* World Series Section */}
            <ChampionshipSection 
              title="World Series"
              total={data.stats.total_world_series}
              lastWon={data.stats.last_world_series}
              years={data.championships.world_series}
            />
  
            {/* Division Titles Section */}
            <ChampionshipSection 
              title="Division Titles"
              total={data.stats.total_division_titles}
              lastWon={data.stats.last_division_title}
              years={data.championships.division_titles}
            />
          </div>
  
          {/* Additional Achievements */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* League Pennants */}
            <ChampionshipSection 
              title="League Pennants"
              total={data.stats.total_pennants}
              lastWon={data.stats.last_pennant}
              years={data.championships.league_pennants}
            />
  
            {/* Wild Card Appearances */}
            <ChampionshipSection 
              title="Wild Card Appearances"
              total={data.stats.total_wild_cards}
              lastWon={data.championships.wild_cards?.[0]}
              years={data.championships.wild_cards}
            />
          </div>
        </CardContent>
      </Card>
    );
  };
  
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
  console.log("recent games", data)
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
    console.log("EndpointResultDialog", endpointName, data);
   alert(endpointName)
    switch (endpointName) {
      case '/api/team/games/recent':
      case '/api/player/games/recent':
        return renderGames(data);
      case '/api/player/awards':
        return renderPlayerAwards(data);
      case '/api/team/championships':
        return <ChampionshipHistory oldData={data} />;
      case '/api/team/roster/current':
      case '/api/team/roster/all-time':
        return renderRosterData(data);
      case '/api/player/stats':
        return <MLBStatistics chart={data.data.data} />
      case '/api/team/stats':
        return <MLBStatistics chart={data.data} />
        //return renderStatsData(data);
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
    <Dialog open={isOpen} onOpenChange={onClose} modal={true}>
      <DialogContent 
        className="max-w-4xl max-h-[90vh] overflow-auto bg-black/95 border-white/10 z-[3000]
          fixed left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%]"
        style={{
          position: 'fixed',
          zIndex: 3000,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <DialogHeader>
          <DialogTitle className="text-xl font-bold flex items-center gap-2">
            <ChevronRight className="w-5 h-5" />
            {getEndpointTitle(endpointName)} Results
          </DialogTitle>
        </DialogHeader>
        <div className="relative z-[3001]">
          {renderContent()}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EndpointResultDialog;