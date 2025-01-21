'use server'

import prisma from '@/lib/prisma'
import { verify } from 'jsonwebtoken'

export async function getUserProfile(token: string) {
  try {
    // Verify and decode the token
    const decoded = verify(token, process.env.JWT_SECRET!) as {
      id: string
      email: string
      name: string
    }

    console.log("decoded", decoded)

    // Get user with preferences and stats
    const user = await prisma.user.findUnique({
      where: { id: decoded.id },
      include: {
        preferences: true,
        baseballStats: true,
      },
    })

    if (!user) {
      throw new Error('User not found')
    }
    // Format the data to match MLBProfile props
    return {
      user: {
        name: user.name || '',
        email: user.email,
        avatar: user.avatar,
      },
      preferences: {
        favoriteTeam: user.preferences?.favoriteTeam,
        favoritePlayer: user.preferences?.favoritePlayer,
        favoriteHomeRun: user.preferences?.favoriteHomeRun,
        stats: {
          messagesExchanged: user.baseballStats?.messagesExchanged || 0,
          queriesAnswered: user.baseballStats?.queriesAnswered || 0,
          daysActive: user.baseballStats?.daysActive || 0,
        },
        preferences: {
          language: user.preferences?.language || 'English',
          statsPreference: user.preferences?.statsPreference || 'Basic',
          notificationPreference: user.preferences?.notificationPreference || 'Game Time Only',
        },
      },
    }
  } catch (error) {
    console.error('Error fetching user profile:', error)
    throw error
  }
}