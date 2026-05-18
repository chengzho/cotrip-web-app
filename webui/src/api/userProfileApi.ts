import { request } from './httpClient'
import type { UserProfile } from '../types/user'

export async function getMe(): Promise<UserProfile> {
  const result = await request<{ user: UserProfile }>({ method: 'GET', path: '/me' })
  return result.user
}

export async function updateMe(body: { display_name: string }): Promise<UserProfile> {
  const result = await request<{ user: UserProfile }>({ method: 'PATCH', path: '/me', body })
  return result.user
}
