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
  notificationPreference: string
  statsPreference: string
  theme?: string
  notifications?: boolean
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
  preferences: UserPreferences
  stats: UserStats
}

interface Message {
  content: string
  sender: 'bot' | 'user'
  type: 'text' | 'options' | 'selection'
  timestamp?: number
}

interface UpdateUserDataPayload {
  messages: Message[]
  preferences: BaseballPreferences
  user: {
    avatar?: string
    email: string
    name: string
  }
}

export async function updateUserPreferences(
  token: string,
  payload: UpdateUserDataPayload
): Promise<BaseballPreferences> {
  if (!token || !payload) {
    throw new Error('Missing required parameters')
  }

  try {
    const decoded = verify(token, process.env.JWT_SECRET!) as {
      id: string
      email: string
      name: string
    }

    if (decoded.email !== payload.user.email) {
      throw new Error('User email does not match token')
    }

    // Extract the core fields we need to update
    const preferenceData = {
      userId: decoded.id,
      language: payload.preferences.preferences.language || 'en',
      theme: payload.preferences.preferences.theme || 'system',
      notifications: payload.preferences.preferences.notifications ?? true,
      favoriteTeam: payload.preferences.favoriteTeam || null,
      favoriteTeamUrl: payload.preferences.favoriteTeamUrl || null,
      favoriteTeamDescription: payload.preferences.favoriteTeamDescription || null,
      favoritePlayer: payload.preferences.favoritePlayer || null,
      favoritePlayerUrl: payload.preferences.favoritePlayerUrl || null,
      favoritePlayerDescription: payload.preferences.favoritePlayerDescription || null,
      favoriteHomeRun: payload.preferences.favoriteHomeRun || null,
      favoriteHomeRunUrl: payload.preferences.favoriteHomeRunUrl || null,
      favoriteHomeRunDescription: payload.preferences.favoriteHomeRunDescription || null,
      statsPreference: payload.preferences.preferences.statsPreference || 'Basic',
      notificationPreference: payload.preferences.preferences.notificationPreference || 'Game Time Only'
    }

    const updatedUser = await prisma.$transaction(async (tx) => {
      // Update user profile
      await tx.user.update({
        where: { id: decoded.id },
        data: {
          name: payload.user.name,
          avatar: payload.user.avatar,
          updatedAt: new Date()
        }
      })

      // Update preferences using the extracted data
      const preferences = await tx.userPreferences.upsert({
        where: { userId: decoded.id },
        create: preferenceData,
        update: preferenceData
      })

      // Count new messages
      const newMessages = payload.messages.filter(msg => 
        msg.timestamp && msg.timestamp > Date.now() - 5 * 60 * 1000
      ).length

      // Update stats
      const stats = await tx.baseballStats.upsert({
        where: { userId: decoded.id },
        create: {
          userId: decoded.id,
          messagesExchanged: newMessages,
          queriesAnswered: payload.preferences.stats.queriesAnswered || 0,
          daysActive: payload.preferences.stats.daysActive || 1,
          lastActive: new Date()
        },
        update: {
          messagesExchanged: {
            increment: newMessages
          },
          queriesAnswered: payload.preferences.stats.queriesAnswered || 0,
          daysActive: payload.preferences.stats.daysActive || 1,
          lastActive: new Date()
        }
      })

      return { preferences, stats }
    })

    return {
      favoriteTeam: updatedUser.preferences.favoriteTeam,
      favoriteTeamUrl: updatedUser.preferences.favoriteTeamUrl,
      favoriteTeamDescription: updatedUser.preferences.favoriteTeamDescription,
      favoritePlayer: updatedUser.preferences.favoritePlayer,
      favoritePlayerUrl: updatedUser.preferences.favoritePlayerUrl,
      favoritePlayerDescription: updatedUser.preferences.favoritePlayerDescription,
      favoriteHomeRun: updatedUser.preferences.favoriteHomeRun,
      favoriteHomeRunUrl: updatedUser.preferences.favoriteHomeRunUrl,
      favoriteHomeRunDescription: updatedUser.preferences.favoriteHomeRunDescription,
      preferences: {
        language: updatedUser.preferences.language,
        theme: updatedUser.preferences.theme,
        notifications: updatedUser.preferences.notifications,
        statsPreference: updatedUser.preferences.statsPreference,
        notificationPreference: updatedUser.preferences.notificationPreference
      },
      stats: {
        messagesExchanged: updatedUser.stats.messagesExchanged,
        queriesAnswered: updatedUser.stats.queriesAnswered,
        daysActive: updatedUser.stats.daysActive
      }
    }
  } catch (error) {
    console.error('Error updating user preferences:', error)
    throw error
  }
}