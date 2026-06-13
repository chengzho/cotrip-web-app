// Candidate place domain types.
// Field names match actual backend API response payloads.

import type { CandidateCategory, RestaurantMealTime } from '../constants/candidateCategories';
export type { CandidateCategory, RestaurantMealTime };

export interface CandidateCreatedBy {
  user_id: string;
  display_name: string;
}

// Candidate place model returned by list/create/update endpoints
export interface Candidate {
  candidate_id: string;
  trip_id: string;
  category: CandidateCategory;
  name: string;
  address: string | null;
  note: string | null;
  source_url: string | null;
  created_by: CandidateCreatedBy;
  vote_count: number;
  current_user_voted: boolean;
  created_at: string;
  updated_at: string;
  restaurant_meal_times: RestaurantMealTime[] | null;
}

// Request body for POST /trips/{tripId}/candidates
export interface CreateCandidateRequest {
  category: CandidateCategory;
  name: string;
  address?: string;
  note?: string;
  source_url?: string;
  restaurant_meal_times?: RestaurantMealTime[];
}

// Request body for PATCH /trips/{tripId}/candidates/{candidateId}
export interface UpdateCandidateRequest {
  category?: CandidateCategory;
  name?: string;
  address?: string;
  note?: string;
  source_url?: string;
  restaurant_meal_times?: RestaurantMealTime[] | null;
}
