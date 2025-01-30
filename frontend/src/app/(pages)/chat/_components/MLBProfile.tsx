import React, { useState, useCallback } from 'react';
import { ChevronDown, Volleyball, Heart, LogOut, ExternalLink } from 'lucide-react';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import ProfileSuccessAnimation from './ProfileSuccessAnimation';
import ImageAnalysisDialog from './ImageAnalysisDialog';
import { Image as ImageIcon } from 'lucide-react';
import { languageContent } from '@/lib/constants';
import PreferenceCard from './PreferenceCard';

interface BaseballStats {
  messagesExchanged: number;
  queriesAnswered: number;
  daysActive: number;
}

interface UserPreferences {
  language: string;
  statsPreference: string;
  notificationPreference: string;
}

interface BaseballPreferences {
  favoriteTeam?: string;
  favoriteTeamUrl?: string;
  favoriteTeamDescription?: string;
  favoritePlayer?: string;
  favoritePlayerUrl?: string;
  favoritePlayerDescription?: string;
  favoriteHomeRun?: string;
  favoriteHomeRunUrl?: string;
  favoriteHomeRunDescription?: string;
  stats?: BaseballStats;
  preferences?: UserPreferences;
}

interface MLBProfileProps {
  user: {
    name: string;
    email: string;
    avatar?: string;
  };
  preferences: BaseballPreferences;
  onLogout: () => void;
  showSuccessAnimation?: boolean;
  onAnimationComplete?: () => void;
}

const AvatarComponent = () => (
  <div className="relative inline-block">
    <img
      src={"/user.png"}
      alt="Profile"
      className="w-full h-full object-cover rounded-full"
    />
  </div>
);

const MLBProfile: React.FC<MLBProfileProps> = ({
  user,
  preferences,
  onLogout,
  showSuccessAnimation = false,
  onAnimationComplete
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [imageAnalysis, setImageAnalysis] = useState<{
    isOpen: boolean;
    url: string | null;
    title: string;
  }>({
    isOpen: false,
    url: null,
    title: ''
  });

  const handleImageAnalysis = useCallback((url: string, title: string) => {
    setImageAnalysis({
      isOpen: true,
      url,
      title
    });

    setIsOpen(false);
  }, []);

  const closeImageAnalysis = useCallback(() => {
    setImageAnalysis(prev => ({
      ...prev,
      isOpen: false
    }));
  }, []);

  const userLanguage = preferences?.preferences?.language?.toLowerCase() === 'sp' 
    ? 'es' 
    : preferences?.preferences?.language?.toLowerCase() || 'en';
    
  const content = languageContent[userLanguage as keyof typeof languageContent] || languageContent.en;

  return (
    <>
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <div className="relative">
          <DropdownMenuTrigger asChild>
            <button 
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors duration-200"
              aria-label="Open profile menu"
            >
              <div className="h-8 w-8">
                <AvatarComponent />
              </div>
              <span className="text-white font-medium hidden md:inline">
                {user.name}
              </span>
              <ChevronDown className="w-4 h-4 text-gray-300" />
            </button>
          </DropdownMenuTrigger>

          <ProfileSuccessAnimation
            show={showSuccessAnimation}
            onComplete={onAnimationComplete}
            particleCount={12}
            particleDistance={60}
            animationDuration={2000}
          />
        </div>

        <DropdownMenuContent 
          className="w-96 bg-gray-900/95 backdrop-blur-sm text-white border-gray-800"
          align="end"
        >
          {/* Profile Header */}
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
                    {content.profile.baseballFan}
                  </span>
                  {preferences.favoriteTeam && (
                    <span className="inline-flex items-center gap-1 text-xs bg-green-600/30 text-green-400 px-2 py-1 rounded-full">
                      <Heart className="w-3 h-3" />
                      {`${preferences.favoriteTeam} ${content.profile.teamFanSuffix}`}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <DropdownMenuSeparator className="bg-gray-800" />

          {/* Stats Section */}
          {preferences.stats && (
            <div className="p-4 grid grid-cols-3 gap-3">
              {Object.entries(preferences.stats).map(([key, value]) => (
                <div key={key} className="bg-gray-800/50 p-3 rounded-lg text-center">
                  <p className="text-lg font-semibold">{value}</p>
                  <p className="text-xs text-gray-400">
                    {content.statsSection[key as keyof typeof content.statsSection]}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Preferences Section */}
          <div className="p-4 space-y-3">
            <h4 className="text-sm font-medium text-gray-400">
              {content.preferencesSection.title}
            </h4>
            <div className="grid grid-cols-2 gap-3">
              {preferences.favoriteTeam && (
                <PreferenceCard
                  title={content.preferencesSection.favoriteTeam}
                  value={preferences.favoriteTeam}
                  description={preferences.favoriteTeamDescription}
                  url={preferences.favoriteTeamUrl}
                  onImageAnalysis={
                    preferences.favoriteTeamUrl 
                      ? () => handleImageAnalysis(
                          preferences.favoriteTeamUrl!, 
                          `${preferences.favoriteTeam} Analysis`
                        )
                      : undefined
                  }
                />
              )}
              {preferences.favoritePlayer && (
                <PreferenceCard
                  title={content.preferencesSection.favoritePlayer}
                  value={preferences.favoritePlayer}
                  description={preferences.favoritePlayerDescription}
                  url={preferences.favoritePlayerUrl}
                  onImageAnalysis={
                    preferences.favoritePlayerUrl
                      ? () => handleImageAnalysis(
                          preferences.favoritePlayerUrl!,
                          `${preferences.favoritePlayer} Analysis`
                        )
                      : undefined
                  }
                />
              )}
            </div>
            {preferences.favoriteHomeRun && (
              <PreferenceCard
                title={content.preferencesSection.memorableHomeRun}
                value={preferences.favoriteHomeRun}
                description={preferences.favoriteHomeRunDescription}
                url={preferences.favoriteHomeRunUrl}
                onImageAnalysis={
                  preferences.favoriteHomeRunUrl
                    ? () => handleImageAnalysis(
                        preferences.favoriteHomeRunUrl!,
                        'Home Run Moment Analysis'
                      )
                    : undefined
                }
              />
            )}
          </div>

          {/* Settings Section */}
          {preferences.preferences && (
            <>
              <DropdownMenuSeparator className="bg-gray-800" />
              <div className="p-4 space-y-2">
                <h4 className="text-sm font-medium text-gray-400">
                  {content.settings.title}
                </h4>
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

          {/* Logout Section */}
          <div className="p-2">
            <button
              onClick={onLogout}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-950/30 rounded-lg transition-colors duration-200"
            >
              <LogOut className="w-4 h-4" />
              {content.actions.signOut}
            </button>
          </div>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Image Analysis Dialog */}
      {imageAnalysis.isOpen && imageAnalysis.url && (
        <ImageAnalysisDialog
          isOpen={imageAnalysis.isOpen}
          onClose={closeImageAnalysis}
          imageUrl={imageAnalysis.url}
        />
      )}
    </>
  );
};

export default MLBProfile;