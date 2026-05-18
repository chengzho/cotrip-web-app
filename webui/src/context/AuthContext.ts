import { createContext, useContext } from 'react'

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
  signIn: (returnPath?: string) => Promise<void>
  signOut: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
