'use server'

import prisma from '@/lib/prisma'
import { compare } from 'bcryptjs'
import { sign } from 'jsonwebtoken'

interface SignInInput {
  email: string
  password: string
}

export async function signIn({ email, password }: SignInInput) {
  try {
    // Find user by email
    const user = await prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        email: true,
        password: true,
        name: true,
      },
    })

    if (!user) {
      return {
        error: 'Invalid credentials',
      }
    }

    // Verify password
    const isPasswordValid = await compare(password, user.password)

    if (!isPasswordValid) {
      return {
        error: 'Invalid credentials',
      }
    }

    // Create session token
    const token: string = sign(
      {
        id: user.id,
        email: user.email,
        name: user.name,
      },
      process.env.JWT_SECRET || 'fallback-secret',
      { expiresIn: '7d' }
    )

    // Return token and user data
    return {
      token, // Send token back to client
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    }
  } catch (error) {
    console.error('Sign in error:', error)
    return {
      error: 'An error occurred during sign in',
    }
  }
}