import React, { useState } from 'react'
import { ChevronDown, User, Volleyball, Heart, LogOut } from 'lucide-react'
import { DropdownMenu, DropdownMenuContent, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'

interface UserPreference {
  favoriteTeam?: string
  favoritePlayer?: string
  favoriteHomeRun?: string
  stats?: {
    messagesExchanged: number
    queriesAnswered: number
    daysActive: number
  }
  preferences?: {
    language: string
    statsPreference: string
    notificationPreference: string
  }
}

interface MLBProfileProps {
  user: {
    name: string
    email: string
    avatar?: string
  }
  preferences: UserPreference
  onLogout: () => void
}

// Language-specific content configuration for all UI text
const languageContent = {
  en: {
    baseballFan: "Baseball Fan",
    teamFanSuffix: "Fan",
    statsSection: {
      title: "Baseball Stats",
      messagesExchanged: "Messages Exchanged",
      queriesAnswered: "Queries Answered",
      daysActive: "Days Active"
    },
    preferencesSection: {
      title: "Baseball Preferences",
      favoriteTeam: "Favorite Team",
      favoritePlayer: "Favorite Player",
      memorableHomeRun: "Most Memorable Home Run"
    },
    settings: {
      title: "Settings",
      language: "Language",
      statsPreference: "Stats Preference",
      notificationPreference: "Notification Preference"
    },
    signOut: "Sign Out"
  },
  es: {
    baseballFan: "Aficionado al Béisbol",
    teamFanSuffix: "Aficionado",
    statsSection: {
      title: "Estadísticas de Béisbol",
      messagesExchanged: "Mensajes Intercambiados",
      queriesAnswered: "Consultas Respondidas",
      daysActive: "Días Activos"
    },
    preferencesSection: {
      title: "Preferencias de Béisbol",
      favoriteTeam: "Equipo Favorito",
      favoritePlayer: "Jugador Favorito",
      memorableHomeRun: "Home Run Más Memorable"
    },
    settings: {
      title: "Configuración",
      language: "Idioma",
      statsPreference: "Preferencia de Estadísticas",
      notificationPreference: "Preferencia de Notificaciones"
    },
    signOut: "Cerrar Sesión"
  },
  ja: {
    baseballFan: "野球ファン",
    teamFanSuffix: "ファン",
    statsSection: {
      title: "野球統計",
      messagesExchanged: "交換メッセージ",
      queriesAnswered: "回答済みクエリ",
      daysActive: "アクティブ日数"
    },
    preferencesSection: {
      title: "野球設定",
      favoriteTeam: "お気に入りチーム",
      favoritePlayer: "お気に入り選手",
      memorableHomeRun: "最も印象的なホームラン"
    },
    settings: {
      title: "設定",
      language: "言語",
      statsPreference: "統計設定",
      notificationPreference: "通知設定"
    },
    signOut: "サインアウト"
  }
};

const AvatarComponent = () => (
  <div className="relative inline-block">
    <img 
      src={"/user.png"} 
      alt="Profile" 
      className="w-full h-full object-cover rounded-full"
    />
  </div>
);

const MLBProfile = ({ user, preferences, onLogout }: MLBProfileProps) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Get user language from preferences, default to English if not set
  // Map 'sp' to 'es' for Spanish
  const userLanguage = (preferences?.preferences?.language?.toLowerCase() === 'sp' ? 
    'es' : preferences?.preferences?.language?.toLowerCase()) || 'en';
  
  // Get language-specific content, fallback to English if translation not found
  const content = languageContent[userLanguage as keyof typeof languageContent] || languageContent.en;

  const formatStatKey = (key: string): string => {
    // Map the stat keys to their translated versions
    const statTranslations = content.statsSection;
    const mappings: { [key: string]: string } = {
      messagesExchanged: statTranslations.messagesExchanged,
      queriesAnswered: statTranslations.queriesAnswered,
      daysActive: statTranslations.daysActive
    };
    return mappings[key] || key;
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors duration-200">
          <div className="h-8 w-8">
            <AvatarComponent />
          </div>
          <span className="text-white font-medium hidden md:inline">{user.name}</span>
          <ChevronDown className="w-4 h-4 text-gray-300" />
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent className="w-96 bg-gray-900/95 backdrop-blur-sm text-white border-gray-800">
        {/* User Header */}
        <div className="p-4">
          <div className="flex items-start gap-3">
            <div className="h-16 w-16">
              <AvatarComponent />
            </div>
            <div>
              <h3 className="text-lg font-semibold">{user.name}</h3>
              <p className="text-sm text-gray-400">{user.email}</p>
              <div className="flex gap-2 mt-2">
                <span className="inline-flex items-center gap-1 text-xs bg-blue-600/30 text-blue-400 px-2 py-1 rounded-full">
                  <Volleyball className="w-3 h-3" />
                  {content.baseballFan}
                </span>
                {preferences.favoriteTeam && (
                  <span className="inline-flex items-center gap-1 text-xs bg-green-600/30 text-green-400 px-2 py-1 rounded-full">
                    <Heart className="w-3 h-3" />
                    {`${preferences.favoriteTeam} ${content.teamFanSuffix}`}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
        
        <DropdownMenuSeparator className="bg-gray-800" />
        
        {/* Baseball Stats Boxes */}
        <div className="p-4 grid grid-cols-3 gap-3">
          {preferences.stats && Object.entries(preferences.stats).map(([key, value]) => (
            <div key={key} className="bg-gray-800/50 p-3 rounded-lg text-center">
              <p className="text-lg font-semibold">{value}</p>
              <p className="text-xs text-gray-400">{formatStatKey(key)}</p>
            </div>
          ))}
        </div>

        {/* Favorite Baseball Info */}
        <div className="p-4 space-y-3">
          <h4 className="text-sm font-medium text-gray-400">{content.preferencesSection.title}</h4>
          <div className="grid grid-cols-2 gap-3">
            {preferences.favoriteTeam && (
              <div className="bg-gray-800/50 p-3 rounded-lg">
                <p className="text-xs text-gray-400">{content.preferencesSection.favoriteTeam}</p>
                <p className="text-sm font-medium">{preferences.favoriteTeam}</p>
              </div>
            )}
            {preferences.favoritePlayer && (
              <div className="bg-gray-800/50 p-3 rounded-lg">
                <p className="text-xs text-gray-400">{content.preferencesSection.favoritePlayer}</p>
                <p className="text-sm font-medium">{preferences.favoritePlayer}</p>
              </div>
            )}
          </div>
          {preferences.favoriteHomeRun && (
            <div className="bg-gray-800/50 p-3 rounded-lg">
              <p className="text-xs text-gray-400">{content.preferencesSection.memorableHomeRun}</p>
              <p className="text-sm font-medium">{preferences.favoriteHomeRun}</p>
            </div>
          )}
        </div>

        {/* Settings */}
        {preferences.preferences && (
          <>
            <DropdownMenuSeparator className="bg-gray-800" />
            <div className="p-4 space-y-2">
              <h4 className="text-sm font-medium text-gray-400">{content.settings.title}</h4>
              <div className="space-y-2">
                {Object.entries(preferences.preferences).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-400">
                      {content.settings[key as keyof typeof content.settings] || key}
                    </span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        <DropdownMenuSeparator className="bg-gray-800" />
        
        {/* Logout Button */}
        <div className="p-2">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-950/30 rounded-lg transition-colors duration-200"
          >
            <LogOut className="w-4 h-4" />
            {content.signOut}
          </button>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default MLBProfile;