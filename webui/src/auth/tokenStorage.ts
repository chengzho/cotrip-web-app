const STORAGE_KEY = 'cotrip_auth_session'

export interface AuthSession {
  id_token: string
  access_token: string
  refresh_token?: string
  expires_in: number
  token_type: string
  received_at: number // Unix seconds at time of token receipt
}

export function saveSession(session: AuthSession): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session))
}

export function loadSession(): AuthSession | null {
  const raw = sessionStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthSession
  } catch {
    return null
  }
}

export function clearSession(): void {
  sessionStorage.removeItem(STORAGE_KEY)
}

export function isSessionExpired(session: AuthSession): boolean {
  const expiresAt = session.received_at + session.expires_in
  return Date.now() / 1000 >= expiresAt
}
