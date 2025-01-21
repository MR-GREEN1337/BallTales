import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verify } from 'jsonwebtoken'

// Configure which paths require authentication
const protectedPaths = [
  '/chat',
]

// Configure public paths that should bypass authentication
const publicPaths = [
  '/sign-up',
  '/sign-in',
  '/'
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get('auth-token')?.value

  // If user is authenticated and tries to access sign-in, redirect to dashboard
  if (pathname === '/sign-in' && token) {
    return NextResponse.redirect(new URL('/chat', request.url))
  }
  
  // Check if the path is public
  if (publicPaths.some(path => pathname.startsWith(path))) {
    return NextResponse.next()
  }
  
  // Check if path requires authentication
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path))
  
  if (!isProtectedPath) {
    return NextResponse.next()
  }
  
  // If no token is present, redirect to login
  if (!token) {
    const loginUrl = new URL('/sign-in', request.url)
    loginUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(loginUrl)
  }
  
  try {
    // Verify the JWT token
    verify(token, process.env.JWT_SECRET || 'fallback-secret')
    return NextResponse.next()
  } catch (error) {
    // If token is invalid, clear it and redirect to login
    const response = NextResponse.redirect(new URL('/sign-in', request.url))
    response.cookies.delete('auth-token')  // Use auth-token instead of token
    return response
  }
}

// Configure middleware to match specific paths
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public directory)
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
}