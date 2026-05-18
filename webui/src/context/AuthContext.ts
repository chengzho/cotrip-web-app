import { createContext, useContext } from 'react'
import type { UserProfile } from '../types/user'

export interface AuthUser {
  sub: string
  email?: string
  displayName: string
  initial: string
}

export interface AuthContextValue {
  isAuthenticated: boolean
  isInitializing: boolean
  user: AuthUser | null
  authError: string | null
  /** CoTrip backend profile — available after GET /me resolves post-login. */
  profile: UserProfile | null
  signIn: (returnPath?: string) => Promise<void>
  signOut: () => void
  /** Call PATCH /me and update shared profile state. Throws on API failure. */
  updateProfile: (displayName: string) => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
