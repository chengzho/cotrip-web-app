import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { configureAccessTokenProvider } from '../api/httpClient'
import {
  buildAuthorizeUrl,
  buildLogoutUrl,
  clearOAuthTransaction,
  detectCallback,
  exchangeCode,
} from '../auth/cognitoOAuth'
import {
  clearSession,
  isSessionExpired,
  loadSession,
  saveSession,
} from '../auth/tokenStorage'
import { decodeJwtPayload, getDisplayName, isTokenExpired } from '../auth/jwt'
import { AuthContext } from './AuthContext'
import type { AuthUser } from './AuthContext'
import type { JwtPayload } from '../auth/jwt'

function buildUser(payload: JwtPayload): AuthUser {
  const displayName = getDisplayName(payload)
  return {
    sub: payload.sub,
    email: payload.email,
    displayName,
    initial: displayName.charAt(0).toUpperCase(),
  }
}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isInitializing, setIsInitializing] = useState(true)
  const [user, setUser] = useState<AuthUser | null>(null)
  const [authError, setAuthError] = useState<string | null>(null)
  const navigate = useNavigate()
  const didInit = useRef(false)

  const applyIdToken = useCallback((idToken: string) => {
    const payload = decodeJwtPayload(idToken)
    if (!payload) return
    setUser(buildUser(payload))
    configureAccessTokenProvider(() => {
      const session = loadSession()
      return session ? session.id_token : null
    })
  }, [])

  useEffect(() => {
    // Guard against React StrictMode double-invocation
    if (didInit.current) return
    didInit.current = true

    async function init() {
      const callback = detectCallback()

      if (callback) {
        // Remove OAuth query params from the address bar immediately
        window.history.replaceState({}, '', window.location.pathname)

        if ('error' in callback) {
          setAuthError(callback.errorDescription ?? callback.error)
          setIsInitializing(false)
          return
        }

        try {
          const { tokens, returnPath } = await exchangeCode(
            callback.code,
            callback.state,
          )
          saveSession({
            id_token: tokens.id_token,
            access_token: tokens.access_token,
            refresh_token: tokens.refresh_token,
            expires_in: tokens.expires_in,
            token_type: tokens.token_type,
            received_at: Math.floor(Date.now() / 1000),
          })
          applyIdToken(tokens.id_token)
          navigate(returnPath, { replace: true })
        } catch (err: unknown) {
          clearOAuthTransaction()
          setAuthError(
            err instanceof Error ? err.message : '登入失敗，請稍後再試。',
          )
        }
        setIsInitializing(false)
        return
      }

      // Restore session from sessionStorage
      const session = loadSession()
      if (session) {
        const payload = decodeJwtPayload(session.id_token)
        if (payload && !isTokenExpired(payload) && !isSessionExpired(session)) {
          applyIdToken(session.id_token)
        } else {
          clearSession()
        }
      }

      setIsInitializing(false)
    }

    init().catch(() => {
      setIsInitializing(false)
    })
  }, [applyIdToken, navigate])

  const signIn = useCallback(async (returnPath?: string) => {
    try {
      const url = await buildAuthorizeUrl(
        returnPath ?? window.location.pathname,
      )
      window.location.href = url
    } catch (err: unknown) {
      setAuthError(
        err instanceof Error
          ? err.message
          : '無法建立登入連結，請確認環境設定。',
      )
    }
  }, [])

  const signOut = useCallback(() => {
    clearSession()
    setUser(null)
    configureAccessTokenProvider(null)
    try {
      window.location.href = buildLogoutUrl()
    } catch {
      window.location.href = '/'
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: user !== null,
        isInitializing,
        user,
        authError,
        signIn,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
