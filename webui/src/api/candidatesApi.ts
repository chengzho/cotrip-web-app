import { request } from './httpClient';
import { buildQueryString } from './query';
import type { Candidate, CreateCandidateRequest, UpdateCandidateRequest } from '../types/candidate';

export async function createCandidate(tripId: string, body: CreateCandidateRequest): Promise<Candidate> {
  const result = await request<{ candidate: Candidate }>({ method: 'POST', path: `/trips/${tripId}/candidates`, body });
  return result.candidate;
}

export async function listCandidates(tripId: string, category?: string): Promise<Candidate[]> {
  const qs = buildQueryString({ category });
  const result = await request<{ candidates: Candidate[] }>({ method: 'GET', path: `/trips/${tripId}/candidates${qs}` });
  return result.candidates;
}

export async function updateCandidate(tripId: string, candidateId: string, body: UpdateCandidateRequest): Promise<Candidate> {
  const result = await request<{ candidate: Candidate }>({
    method: 'PATCH',
    path: `/trips/${tripId}/candidates/${candidateId}`,
    body,
  });
  return result.candidate;
}

export async function deleteCandidate(tripId: string, candidateId: string): Promise<string> {
  const result = await request<{ deleted_candidate_id: string }>({
    method: 'DELETE',
    path: `/trips/${tripId}/candidates/${candidateId}`,
  });
  return result.deleted_candidate_id;
}
