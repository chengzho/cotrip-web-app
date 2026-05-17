// Trip and member domain types.
// Field names match actual backend API response payloads.

export type TripRole = 'owner' | 'member';

export type TripScope = 'upcoming' | 'past' | 'all';

// Returned by POST /trips
export interface TripCreated {
  trip_id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  description: string | null;
  role: TripRole;
  created_at: string;
  updated_at: string;
}

// Item in the array returned by GET /trips
export interface TripSummary {
  trip_id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  role: TripRole;
  member_count: number;
  candidate_count: number;
  itinerary_item_count: number;
}

// Nested summary counts in GET /trips/{tripId}
export interface TripSummaryCounts {
  member_count: number;
  candidate_count: number;
  vote_count: number;
  itinerary_item_count: number;
}

// Returned by GET /trips/{tripId}
export interface TripDetail {
  trip_id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  description: string | null;
  current_user_role: TripRole;
  summary: TripSummaryCounts;
  created_at: string;
  updated_at: string;
}

// Returned by PATCH /trips/{tripId}
export interface TripUpdated {
  trip_id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  description: string | null;
  updated_at: string;
}

// Item in the array returned by GET /trips/{tripId}/members
export interface TripMember {
  user_id: string;
  display_name: string;
  email: string;
  role: TripRole;
  joined_at: string;
}

// Request body for POST /trips
export interface CreateTripRequest {
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  description?: string;
}

// Request body for PATCH /trips/{tripId}
export interface UpdateTripRequest {
  title?: string;
  destination?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}
