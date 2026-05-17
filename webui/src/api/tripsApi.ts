import { request } from './httpClient';
import { buildQueryString } from './query';
import type { TripCreated, TripSummary, TripDetail, TripUpdated, TripMember, CreateTripRequest, UpdateTripRequest, TripScope } from '../types/trip';

export async function createTrip(body: CreateTripRequest): Promise<TripCreated> {
  return request<TripCreated>({ method: 'POST', path: '/trips', body });
}

export async function listTrips(scope?: TripScope): Promise<TripSummary[]> {
  const qs = buildQueryString({ scope });
  const result = await request<{ trips: TripSummary[] }>({ method: 'GET', path: `/trips${qs}` });
  return result.trips;
}

export async function getTrip(tripId: string): Promise<TripDetail> {
  return request<TripDetail>({ method: 'GET', path: `/trips/${tripId}` });
}

export async function updateTrip(tripId: string, body: UpdateTripRequest): Promise<TripUpdated> {
  return request<TripUpdated>({ method: 'PATCH', path: `/trips/${tripId}`, body });
}

export async function listTripMembers(tripId: string): Promise<TripMember[]> {
  const result = await request<{ members: TripMember[] }>({ method: 'GET', path: `/trips/${tripId}/members` });
  return result.members;
}
