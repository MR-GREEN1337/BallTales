'use server'

import prisma from '@/lib/prisma'
import { verify } from 'jsonwebtoken'

// Type definitions to ensure type safety throughout the function
interface UserStats {
  daysActive: number
  messagesExchanged: number
  queriesAnswered: number
}

interface UserPreferences {
  language: string
  notificationPreference: string
  statsPreference: string
}

interface BaseballPreferences {
  favoriteHomeRun: string | null
  favoritePlayer: string | null
  favoriteTeam: string | null
  preferences: UserPreferences
  stats: UserStats
}

interface Message {
  content: string
  sender: 'bot' | 'user'
  type: 'text' | 'options' | 'selection'
  suggestions?: string[]
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
  try {
    // Verify and decode the JWT token
    const decoded = verify(token, process.env.JWT_SECRET!) as {
      id: string
      email: string
      name: string
    }

    // Verify the user exists and matches the token
    if (decoded.email !== payload.user.email) {
      throw new Error('User email does not match token')
    }

    // Start a transaction to update both preferences and stats
    const updatedUser = await prisma.$transaction(async (tx) => {
      // Update user preferences
      const preferences = await tx.userPreferences.upsert({
        where: {
          userId: decoded.id,
        },
        create: {
          userId: decoded.id,
          language: payload.preferences.preferences.language,
          favoriteTeam: payload.preferences.favoriteTeam,
          favoritePlayer: payload.preferences.favoritePlayer,
          favoriteHomeRun: payload.preferences.favoriteHomeRun,
          statsPreference: payload.preferences.preferences.statsPreference,
          notificationPreference: payload.preferences.preferences.notificationPreference,
        },
        update: {
          language: payload.preferences.preferences.language,
          favoriteTeam: payload.preferences.favoriteTeam,
          favoritePlayer: payload.preferences.favoritePlayer,
          favoriteHomeRun: payload.preferences.favoriteHomeRun,
          statsPreference: payload.preferences.preferences.statsPreference,
          notificationPreference: payload.preferences.preferences.notificationPreference,
        },
      })

      // Update baseball stats
      const stats = await tx.baseballStats.upsert({
        where: {
          userId: decoded.id,
        },
        create: {
          userId: decoded.id,
          messagesExchanged: payload.preferences.stats.messagesExchanged,
          queriesAnswered: payload.preferences.stats.queriesAnswered,
          daysActive: payload.preferences.stats.daysActive,
          lastActive: new Date(),
        },
        update: {
          messagesExchanged: payload.preferences.stats.messagesExchanged,
          queriesAnswered: payload.preferences.stats.queriesAnswered,
          daysActive: payload.preferences.stats.daysActive,
          lastActive: new Date(),
        },
      })

      return {
        preferences,
        stats,
      }
    })

    // Format the response to match the expected BaseballPreferences structure
    return {
      favoriteTeam: updatedUser.preferences.favoriteTeam,
      favoritePlayer: updatedUser.preferences.favoritePlayer,
      favoriteHomeRun: updatedUser.preferences.favoriteHomeRun,
      preferences: {
        language: updatedUser.preferences.language,
        statsPreference: updatedUser.preferences.statsPreference,
        notificationPreference: updatedUser.preferences.notificationPreference,
      },
      stats: {
        messagesExchanged: updatedUser.stats.messagesExchanged,
        queriesAnswered: updatedUser.stats.queriesAnswered,
        daysActive: updatedUser.stats.daysActive,
      },
    }
  } catch (error) {
    console.error('Error updating user preferences:', error)
    throw error
  }
}