interface CognitoConfig {
  domain: string
  clientId: string
  redirectUri: string
  logoutUri: string
  authorizeUrl: string
  tokenUrl: string
  logoutUrl: string
}

function requireEnv(key: keyof ImportMetaEnv): string {
  const val = import.meta.env[key] as string | undefined
  if (!val || !val.trim()) {
    throw new Error(
      `Missing required environment variable: ${key}. ` +
        'Ensure .env.local is configured with Cognito values.',
    )
  }
  return val.trim()
}

export function getCognitoConfig(): CognitoConfig {
  const domain = requireEnv('VITE_COGNITO_DOMAIN').replace(/\/+$/, '')
  return {
    domain,
    clientId: requireEnv('VITE_COGNITO_CLIENT_ID'),
    redirectUri: requireEnv('VITE_COGNITO_REDIRECT_URI'),
    logoutUri: requireEnv('VITE_COGNITO_LOGOUT_URI'),
    authorizeUrl: `${domain}/oauth2/authorize`,
    tokenUrl: `${domain}/oauth2/token`,
    logoutUrl: `${domain}/logout`,
  }
}
