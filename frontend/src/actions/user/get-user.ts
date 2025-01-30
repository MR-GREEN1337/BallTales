'use server'

import prisma from '@/lib/prisma'
import { verify } from 'jsonwebtoken'

interface UserStats {
  messagesExchanged: number
  queriesAnswered: number
  daysActive: number
}

interface UserPreferences {
  language: string
  theme: string
  notifications: boolean
  statsPreference: string
  notificationPreference: string
}

interface BaseballPreferences {
  favoriteTeam?: string | null
  favoriteTeamUrl?: string | null
  favoriteTeamDescription?: string | null
  favoritePlayer?: string | null
  favoritePlayerUrl?: string | null
  favoritePlayerDescription?: string | null
  favoriteHomeRun?: string | null
  favoriteHomeRunUrl?: string | null
  favoriteHomeRunDescription?: string | null
  stats: UserStats
  preferences: UserPreferences
}

interface UserProfile {
  user: {
    name: string
    email: string
    avatar?: string | null
  }
  preferences: BaseballPreferences
}

export async function getUserProfile(token: string): Promise<UserProfile> {
  if (!token) {
    throw new Error('Authentication token is required')
  }

  try {
    // Verify and decode the token
    const decoded = verify(token, process.env.JWT_SECRET!) as {
      id: string
      email: string
      name: string
    }

    // Get user with preferences and stats
    const user = await prisma.user.findUnique({
      where: { 
        id: decoded.id 
      },
      include: {
        preferences: true,
        baseballStats: true,
      },
    })

    if (!user) {
      throw new Error('User not found')
    }

    // Calculate days active if lastActive exists
    const daysActive = user.baseballStats?.lastActive 
      ? Math.ceil((Date.now() - user.baseballStats.lastActive.getTime()) / (1000 * 60 * 60 * 24))
      : 0

    // Format the data to match MLBProfile props with all fields
    return {
      user: {
        name: user.name || '',
        email: user.email,
        avatar: user.avatar,
      },
      preferences: {
        // Favorite team details
        favoriteTeam: user.preferences?.favoriteTeam || null,
        favoriteTeamUrl: user.preferences?.favoriteTeamUrl || null,
        favoriteTeamDescription: user.preferences?.favoriteTeamDescription || null,
        
        // Favorite player details
        favoritePlayer: user.preferences?.favoritePlayer || null,
        favoritePlayerUrl: user.preferences?.favoritePlayerUrl || null,
        favoritePlayerDescription: user.preferences?.favoritePlayerDescription || null,
        
        // Favorite home run details
        favoriteHomeRun: user.preferences?.favoriteHomeRun || null,
        favoriteHomeRunUrl: user.preferences?.favoriteHomeRunUrl || null,
        favoriteHomeRunDescription: user.preferences?.favoriteHomeRunDescription || null,
        
        // Stats with proper defaults
        stats: {
          messagesExchanged: user.baseballStats?.messagesExchanged || 0,
          queriesAnswered: user.baseballStats?.queriesAnswered || 0,
          daysActive: user.baseballStats?.daysActive || daysActive || 0,
        },
        
        // User preferences with schema defaults
        preferences: {
          language: user.preferences?.language || 'en',
          theme: user.preferences?.theme || 'system',
          notifications: user.preferences?.notifications ?? true,
          statsPreference: user.preferences?.statsPreference || 'Basic',
          notificationPreference: user.preferences?.notificationPreference || 'Game Time Only',
        },
      },
    }
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('jwt')) {
        throw new Error('Invalid or expired authentication token')
      }
      throw new Error(`Error fetching user profile: ${error.message}`)
    }
    throw new Error('An unexpected error occurred')
  }
}