import { request } from './httpClient';
import { buildQueryString } from './query';
import type { VoteResult, RankingRow } from '../types/vote';

export async function voteCandidate(candidateId: string): Promise<VoteResult> {
  return request<VoteResult>({ method: 'POST', path: `/candidates/${candidateId}/votes` });
}

export async function unvoteCandidate(candidateId: string): Promise<VoteResult> {
  return request<VoteResult>({ method: 'DELETE', path: `/candidates/${candidateId}/votes` });
}

export async function getRankings(tripId: string, category?: string): Promise<RankingRow[]> {
  const qs = buildQueryString({ category });
  const result = await request<{ rankings: RankingRow[] }>({ method: 'GET', path: `/trips/${tripId}/rankings${qs}` });
  return result.rankings;
}
