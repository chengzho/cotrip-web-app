// Invite domain types.
// Field names match actual backend API response payloads.

// Returned inside data.invite from POST /trips/{tripId}/invites
export interface CreatedInvite {
  id: string;
  trip_id: string;
  invite_url: string;
  expires_at: string;
  max_uses: number;
}

// Returned inside data.invite_preview from GET /invites/{inviteToken}
export interface InvitePreview {
  trip_title: string;
  destination: string;
  start_date: string;
  end_date: string;
  invited_by_display_name: string;
}

// Returned inside data.trip from POST /invites/{inviteToken}/join
export interface JoinedTrip {
  id: string;
  title: string;
  destination: string;
  current_user_role: 'member';
}

// Request body for POST /trips/{tripId}/invites
export interface CreateInviteRequest {
  expires_in_days?: number;
  max_uses?: number;
}
