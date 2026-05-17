import { request } from './httpClient';
import type { CreatedInvite, InvitePreview, JoinedTrip, CreateInviteRequest } from '../types/invite';

export async function createInvite(tripId: string, body?: CreateInviteRequest): Promise<CreatedInvite> {
  const result = await request<{ invite: CreatedInvite }>({ method: 'POST', path: `/trips/${tripId}/invites`, body });
  return result.invite;
}

export async function previewInvite(token: string): Promise<InvitePreview> {
  const result = await request<{ invite_preview: InvitePreview }>({
    method: 'GET',
    path: `/invites/${token}`,
    auth: false,
  });
  return result.invite_preview;
}

export async function joinInvite(token: string): Promise<JoinedTrip> {
  const result = await request<{ trip: JoinedTrip }>({ method: 'POST', path: `/invites/${token}/join` });
  return result.trip;
}
