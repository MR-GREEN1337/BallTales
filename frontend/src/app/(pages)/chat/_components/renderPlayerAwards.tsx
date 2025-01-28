"use client"

import { motion } from 'framer-motion';
import { Award, Trophy, Calendar, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const renderPlayerAwards = (oldData: any) => {
    const data = oldData.data
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 15
      }
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 200,
        damping: 20
      }
    }
  };

  const glowVariants = {
    hover: {
      boxShadow: "0 0 20px rgba(42, 42, 42, 0.5)",
      scale: 1.02,
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 25
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Card className="bg-gradient-to-br from-[#1a1a1a] via-[#0f0f0f] to-[#0a0a0a] border-[#2a2a2a] overflow-hidden">
        <CardHeader>
          <motion.div variants={itemVariants}>
            <CardTitle className="flex items-center gap-2">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              >
                <Award className="w-6 h-6 text-purple-500" />
              </motion.div>
              <span className="text-white font-semibold">
                {data.player_info.name} - Career Achievements
              </span>
            </CardTitle>
          </motion.div>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {/* Player Info Section */}
            <motion.div 
              variants={itemVariants} 
              className="flex flex-wrap gap-4"
            >
              <motion.div
                whileHover="hover"
                variants={glowVariants}
                className="bg-[#1a1a1a] rounded-lg px-4 py-3 backdrop-blur-sm border border-[#2a2a2a]"
              >
                <div className="text-sm text-gray-400">Position</div>
                <div className="text-lg font-bold text-white">{data.player_info.position}</div>
              </motion.div>
              <motion.div
                whileHover="hover"
                variants={glowVariants}
                className="bg-black/20 rounded-lg px-4 py-3 backdrop-blur-sm"
              >
                <div className="text-sm text-purple-300">MLB Debut</div>
                <div className="text-lg font-bold text-white">{data.player_info.mlb_debut}</div>
              </motion.div>
            </motion.div>

            {/* Career Achievements Section */}
            <motion.div variants={itemVariants} className="space-y-4">
              <motion.h3 
                className="text-lg font-semibold text-white/90 flex items-center gap-2"
                variants={itemVariants}
              >
                <motion.div
                  animate={{ scale: [1, 1.2, 1], rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  <Trophy className="w-5 h-5 text-yellow-500" />
                </motion.div>
                Career Milestones
              </motion.h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.career_achievements.map((achievement: any, index: number) => (
                  <motion.div
                    key={index}
                    variants={{
                      ...cardVariants,
                      ...glowVariants
                    }}
                    whileHover="hover"
                    className="bg-[#161616] backdrop-blur-sm
                             rounded-lg p-4 border border-[#2a2a2a] relative overflow-hidden"
                  >
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 opacity-0"
                      whileHover={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    />
                    <div className="relative z-10">
                      <div className="text-sm text-purple-300">{achievement.type}</div>
                      <div className="text-2xl font-bold text-white mb-2">
                        {achievement.value}
                      </div>
                      <div className="text-sm text-white/60">{achievement.description}</div>
                      {achievement.year && (
                        <div className="mt-2 text-xs text-white/40">
                          Achieved in {achievement.year}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Notable Seasons Section */}
            <motion.div variants={itemVariants} className="space-y-4">
              <motion.h3 
                className="text-lg font-semibold text-white/90 flex items-center gap-2"
                variants={itemVariants}
              >
                <motion.div
                  animate={{ 
                    rotate: [0, 360],
                    scale: [1, 1.1, 1]
                  }}
                  transition={{ 
                    rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                    scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                  }}
                >
                  <Calendar className="w-5 h-5 text-blue-500" />
                </motion.div>
                Notable Seasons
              </motion.h3>
              <div className="space-y-4">
                {data.notable_seasons.map((season: any, index: number) => (
                  <motion.div
                    key={index}
                    variants={{
                      ...cardVariants,
                      ...glowVariants
                    }}
                    whileHover="hover"
                    className="bg-[#161616] backdrop-blur-sm
                             rounded-lg p-4 border border-[#2a2a2a] relative overflow-hidden"
                  >
                    <div className="text-lg font-semibold text-white mb-3">{season.year} Season</div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                      {season.achievements.map((achievement: any, achieveIndex: number) => (
                        <motion.div
                          key={achieveIndex}
                          variants={cardVariants}
                          whileHover={{ scale: 1.05 }}
                          className="bg-black/20 rounded-lg p-3 backdrop-blur-sm"
                        >
                          <div className="text-sm text-blue-300">{achievement.type}</div>
                          <div className="text-lg font-bold text-white">{achievement.value}</div>
                          <div className="text-xs text-white/60">{achievement.description}</div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Records Section */}
            {data.records && data.records.length > 0 && (
              <motion.div variants={itemVariants} className="space-y-4">
                <motion.h3 
                  className="text-lg font-semibold text-white/90 flex items-center gap-2"
                  variants={itemVariants}
                >
                  <motion.div
                    animate={{ 
                      scale: [1, 1.2, 1],
                      rotate: [0, 360]
                    }}
                    transition={{ 
                      duration: 4,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    <Target className="w-5 h-5 text-red-500" />
                  </motion.div>
                  Records
                </motion.h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.records.map((record: any, index: number) => (
                    <motion.div
                      key={index}
                      variants={{
                        ...cardVariants,
                        ...glowVariants
                      }}
                      whileHover="hover"
                      className="bg-gradient-to-r from-red-500/10 to-orange-500/10 backdrop-blur-sm
                               rounded-lg p-4 border border-red-500/20"
                    >
                      <div className="text-sm text-red-300">{record.type}</div>
                      <div className="text-xl font-bold text-white">{record.value}</div>
                      <div className="text-sm text-white/60">{record.description}</div>
                      {record.year && (
                        <div className="mt-2 text-xs text-white/40">Set in {record.year}</div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default renderPlayerAwards;