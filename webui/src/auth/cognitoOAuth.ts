import { getCognitoConfig } from './cognitoConfig'
import { generateState, generateCodeVerifier, generateCodeChallenge } from './pkce'

const VERIFIER_KEY = 'cotrip_pkce_verifier'
const STATE_KEY = 'cotrip_oauth_state'
const RETURN_PATH_KEY = 'cotrip_oauth_return_path'

export interface OAuthTokenResponse {
  id_token: string
  access_token: string
  refresh_token?: string
  expires_in: number
  token_type: string
}

export type CallbackParams =
  | { code: string; state: string }
  | { error: string; errorDescription?: string }

export function detectCallback(): CallbackParams | null {
  const params = new URLSearchParams(window.location.search)
  const error = params.get('error')
  if (error) {
    return {
      error,
      errorDescription: params.get('error_description') ?? undefined,
    }
  }
  const code = params.get('code')
  const state = params.get('state')
  if (code && state) return { code, state }
  return null
}

export async function buildAuthorizeUrl(returnPath: string): Promise<string> {
  const config = getCognitoConfig()
  const state = generateState()
  const verifier = generateCodeVerifier()
  const challenge = await generateCodeChallenge(verifier)

  sessionStorage.setItem(STATE_KEY, state)
  sessionStorage.setItem(VERIFIER_KEY, verifier)
  sessionStorage.setItem(RETURN_PATH_KEY, returnPath)

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    scope: 'openid email profile',
    state,
    code_challenge_method: 'S256',
    code_challenge: challenge,
  })

  return `${config.authorizeUrl}?${params.toString()}`
}

export async function exchangeCode(
  code: string,
  state: string,
): Promise<{ tokens: OAuthTokenResponse; returnPath: string }> {
  const storedState = sessionStorage.getItem(STATE_KEY)
  const verifier = sessionStorage.getItem(VERIFIER_KEY)
  const returnPath = sessionStorage.getItem(RETURN_PATH_KEY) ?? '/trips'

  if (!storedState || state !== storedState) {
    clearOAuthTransaction()
    throw new Error('OAuth 狀態驗證失敗，請重新嘗試登入。')
  }
  if (!verifier) {
    clearOAuthTransaction()
    throw new Error('缺少 PKCE 驗證資訊，請重新嘗試登入。')
  }

  const config = getCognitoConfig()
  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: config.clientId,
    code,
    redirect_uri: config.redirectUri,
    code_verifier: verifier,
  })

  // Always clear transaction data after the exchange attempt
  clearOAuthTransaction()

  const response = await fetch(config.tokenUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  })

  if (!response.ok) {
    let msg = `Token 交換失敗 (HTTP ${response.status})，請重新登入。`
    try {
      const data = (await response.json()) as {
        error?: string
        error_description?: string
      }
      if (data.error_description) msg = data.error_description
      else if (data.error) msg = data.error
    } catch { /* ignore */ }
    throw new Error(msg)
  }

  const tokens = (await response.json()) as OAuthTokenResponse
  return { tokens, returnPath }
}

export function buildLogoutUrl(): string {
  const config = getCognitoConfig()
  const params = new URLSearchParams({
    client_id: config.clientId,
    logout_uri: config.logoutUri,
  })
  return `${config.logoutUrl}?${params.toString()}`
}

export function clearOAuthTransaction(): void {
  sessionStorage.removeItem(VERIFIER_KEY)
  sessionStorage.removeItem(STATE_KEY)
  sessionStorage.removeItem(RETURN_PATH_KEY)
}
