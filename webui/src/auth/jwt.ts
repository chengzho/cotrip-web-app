export interface JwtPayload {
  sub: string
  email?: string
  name?: string
  preferred_username?: string
  'cognito:username'?: string
  exp?: number
  [key: string]: unknown
}

// Decode only — signature verification is the backend's responsibility.
export function decodeJwtPayload(token: string): JwtPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64)) as JwtPayload
  } catch {
    return null
  }
}

export function isTokenExpired(payload: JwtPayload): boolean {
  if (payload.exp === undefined) return false
  return Date.now() / 1000 >= payload.exp
}

export function getDisplayName(payload: JwtPayload): string {
  if (payload.name) return payload.name
  if (payload.preferred_username) return payload.preferred_username
  if (payload.email) return payload.email
  return 'CoTrip 使用者'
}
