'use server'

import prisma from '@/lib/prisma'
import { hash } from 'bcryptjs'
import { sign } from 'jsonwebtoken'
import { cookies } from 'next/headers'

const SALT_ROUNDS = 12

interface SignUpInput {
  email: string
  password: string
  name: string
  language: string
}

export async function signUp({ email, password, name, language }: SignUpInput) {
  try {
    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email },
    })

    if (existingUser) {
      return {
        error: 'Email already registered',
      }
    }

    // Validate password strength
    if (password.length < 8) {
      return {
        error: 'Password must be at least 8 characters long',
      }
    }

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/
    if (!passwordRegex.test(password)) {
      return {
        error: 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character',
      }
    }

    // Hash password
    const hashedPassword = await hash(password, SALT_ROUNDS)

    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
        preferences: {
          create: {
            language,
            theme: 'system',
            notifications: true,
          },
        },
      },
      select: {
        id: true,
        email: true,
        name: true,
        preferences: {
          select: {
            language: true
          }
        }
      },
    })

    // Create auth token
    const authToken = sign(
      {
        id: user.id,
        email: user.email,
        name: user.name,
      },
      process.env.JWT_SECRET || 'fallback-secret',
      { expiresIn: '7d' }
    )

    // Set auth cookie
    const cookieStore = await cookies()
    cookieStore.set('auth-token', authToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      expires: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    })

    return {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        language: user.preferences?.language,
      },
    }
  } catch (error) {
    console.error('Sign up error:', error)
    return {
      error: 'An error occurred during sign up',
    }
  }
}