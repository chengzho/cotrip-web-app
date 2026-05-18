function base64urlEncode(bytes: Uint8Array): string {
  let str = ''
  for (const byte of bytes) {
    str += String.fromCharCode(byte)
  }
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

export function generateState(): string {
  return base64urlEncode(crypto.getRandomValues(new Uint8Array(32)))
}

export function generateCodeVerifier(): string {
  return base64urlEncode(crypto.getRandomValues(new Uint8Array(32)))
}

export async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoded = new TextEncoder().encode(verifier)
  const digest = await crypto.subtle.digest('SHA-256', encoded)
  return base64urlEncode(new Uint8Array(digest))
}
