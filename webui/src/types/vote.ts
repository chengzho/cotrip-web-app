// Vote and ranking domain types.
// Field names match actual backend API response payloads.

import type { CandidateCreatedBy } from './candidate';

// Response data from POST/DELETE /candidates/{candidateId}/votes
export interface VoteResult {
  candidate_id: string;
  voted: boolean;
  vote_count: number;
}

// One row in the rankings array from GET /trips/{tripId}/rankings
export interface RankingRow {
  rank: number;
  candidate_id: string;
  trip_id: string;
  category: string;
  name: string;
  note: string | null;
  created_by: CandidateCreatedBy;
  vote_count: number;
  current_user_voted: boolean;
  created_at: string;
}
