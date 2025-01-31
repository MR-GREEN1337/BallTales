// GamesDisplay.tsx
"use client"

import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, X, MapPin, CalendarClock } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

interface Game {
  game_id: number;
  date: string;
  opponent: string;
  opponent_image_url: string;
  home_away: string;
  venue?: string;
  time?: string;
  status?: string;
  score?: string;
  result?: string;
}

interface GamesData {
  period?: string;
  games?: Game[];
  upcoming_games?: Game[];
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

const GameCard: React.FC<{ game: Game; type: 'recent' | 'upcoming' }> = ({ game, type }) => {
  const date = new Date(game.date);
  const formattedDate = date.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric' 
  });

  return (
    <motion.div
      variants={itemVariants}
      className="bg-black/20 p-4 rounded-lg hover:bg-black/30 transition-colors"
    >
      <div className="flex justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <img 
            src={game.opponent_image_url} 
            alt={`${game.opponent} logo`}
            className="w-8 h-8"
          />
          <div>
            <div className="text-white/80 font-medium flex items-center gap-2">
              {game.opponent}
              <Badge variant="secondary" className="ml-2 bg-blue-900/60 text-blue-200 hover:bg-blue-800/60">
                {game.home_away.toUpperCase()}
              </Badge>
            </div>
            <div className="text-sm text-white/60 flex items-center gap-2">
              <CalendarClock className="w-4 h-4" />
              {formattedDate}
              {game.time && ` • ${game.time}`}
            </div>
            {game.venue && (
              <div className="text-sm text-white/60 flex items-center gap-2 mt-1">
                <MapPin className="w-4 h-4" />
                {game.venue}
              </div>
            )}
          </div>
        </div>
        <div className="text-right">
          {type === 'recent' ? (
            <>
              <div className="text-lg font-bold text-white">{game.score}</div>
              <div className="text-sm text-white/60">{game.result}</div>
            </>
          ) : (
            <Badge 
              variant="secondary"
              className="text-xs bg-blue-900/60 text-blue-200 hover:bg-blue-800/60"
            >
              {game.status || 'Scheduled'}
            </Badge>
          )}
        </div>
      </div>
    </motion.div>
  );
};

const NoGamesDisplay = ({ type }: { type: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    className="flex flex-col items-center justify-center p-8 bg-black/20 rounded-lg"
  >
    <X className="w-12 h-12 text-purple-500/50 mb-4" />
    <p className="text-lg font-medium text-white/70">No {type} Games Available</p>
    <p className="text-sm text-white/50 mt-2">Check back later for game updates</p>
  </motion.div>
);

export const renderGames = (data: any) => {
  // Split the games into recent and upcoming
  const recentGames = data?.data?.games || [];
  const upcomingGames = data?.data?.upcoming_games || [];

  return (
    <Card className="bg-gradient-to-br from-blue-700/10 to-blue-800/10 border-blue-700/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-500" />
          Games Schedule
        </CardTitle>
      </CardHeader>
      <CardContent>
        {data?.data?.period && (
          <div className="text-sm text-white/60 mb-4">
            Period: {data.data.period}
          </div>
        )}

        <Tabs defaultValue="recent" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="recent">Recent Games</TabsTrigger>
            <TabsTrigger value="upcoming">Upcoming Games</TabsTrigger>
          </TabsList>
          
          <TabsContent value="recent">
            {recentGames.length === 0 ? (
              <NoGamesDisplay type="Recent" />
            ) : (
              <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="space-y-3"
              >
                {recentGames.map((game: Game) => (
                  <GameCard key={game.game_id} game={game} type="recent" />
                ))}
              </motion.div>
            )}
          </TabsContent>

          <TabsContent value="upcoming">
            {upcomingGames.length === 0 ? (
              <NoGamesDisplay type="Upcoming" />
            ) : (
              <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="space-y-3 max-h-[32rem] overflow-y-auto pr-2"
              >
                {upcomingGames.map((game: Game) => (
                  <GameCard key={game.game_id} game={game} type="upcoming" />
                ))}
              </motion.div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default renderGames;