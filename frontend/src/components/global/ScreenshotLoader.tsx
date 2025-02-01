import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronRight, Database, Video, LineChart } from 'lucide-react';

const showcaseContent = {
  en: {
    title: "Elevate Your Game Experience",
    features: [
      {
        title: "Smart Analytics",
        description: "Dive deep into player statistics and game analysis powered by cutting-edge AI technology.",
        icon: LineChart,
        badge: "AI-Powered"
      },
      {
        title: "Video Highlights",
        description: "Watch personalized game highlights curated just for you, with real-time statistical overlays.",
        icon: Video,
        badge: "Real-time"
      },
      {
        title: "Rich Statistics",
        description: "Access comprehensive MLB statistics with intuitive visualizations and insights.",
        icon: Database,
        badge: "Live Data"
      }
    ]
  },
  es: {
    title: "Eleva tu Experiencia de Juego",
    features: [
      {
        title: "Análisis Inteligente",
        description: "Profundiza en las estadísticas de jugadores y análisis de juegos impulsados por IA de vanguardia.",
        icon: LineChart,
        badge: "IA Avanzada"
      },
      {
        title: "Momentos Destacados",
        description: "Mira los momentos destacados personalizados del juego, con estadísticas en tiempo real.",
        icon: Video,
        badge: "Tiempo Real"
      },
      {
        title: "Estadísticas Detalladas",
        description: "Accede a estadísticas completas de la MLB con visualizaciones intuitivas.",
        icon: Database,
        badge: "Datos en Vivo"
      }
    ]
  },
  ja: {
    title: "ゲーム体験を極める",
    features: [
      {
        title: "スマート分析",
        description: "最先端のAI技術を活用した選手統計とゲーム分析を詳しく見ることができます。",
        icon: LineChart,
        badge: "AI搭載"
      },
      {
        title: "ビデオハイライト",
        description: "リアルタイムの統計情報と共に、あなただけのパーソナライズされたゲームハイライトをご覧ください。",
        icon: Video,
        badge: "リアルタイム"
      },
      {
        title: "詳細な統計",
        description: "直感的な可視化と洞察を備えた包括的なMLB統計にアクセスできます。",
        icon: Database,
        badge: "ライブデータ"
      }
    ]
  }
};

interface ScreenshotShowcaseProps {
  language: 'en' | 'es' | 'ja';
}

const ScreenshotShowcase: React.FC<ScreenshotShowcaseProps> = ({ language }) => {
  const content = showcaseContent[language];

  return (
    <section className="py-24 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden">
      <div className="container mx-auto px-4">
        {/* Title */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-5xl font-bold text-center text-white mb-16"
        >
          {content.title}
        </motion.h2>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {content.features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
            >
              <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm hover:bg-gray-800/70 transition-all duration-300">
                <CardContent className="p-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="p-2 bg-red-500/10 rounded-lg">
                      <feature.icon className="w-6 h-6 text-red-500" />
                    </div>
                    <Badge variant="secondary" className="bg-red-500/10 text-red-500">
                      {feature.badge}
                    </Badge>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Screenshots */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative"
        >
          <div className="grid md:grid-cols-2 gap-8">
            <div className="relative group">
              <img
                src="/api/placeholder/600/400"
                alt="App Screenshot 1"
                className="rounded-lg shadow-2xl w-full"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
            <div className="relative group mt-12 md:mt-24">
              <img
                src="/api/placeholder/600/400"
                alt="App Screenshot 2"
                className="rounded-lg shadow-2xl w-full"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
          </div>
          
          {/* Decorative elements */}
          <div className="absolute -top-16 -left-16 w-32 h-32 bg-red-500/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-16 -right-16 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl" />
        </motion.div>
      </div>
    </section>
  );
};

export default ScreenshotShowcase;