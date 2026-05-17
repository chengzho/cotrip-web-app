import { request } from './httpClient';
import type { Itinerary, ItineraryItemDetail, GenerateItineraryRequest, UpdateItineraryItemRequest } from '../types/itinerary';

export async function generateItinerary(tripId: string, body?: GenerateItineraryRequest): Promise<Itinerary> {
  const result = await request<{ itinerary: Itinerary }>({
    method: 'POST',
    path: `/trips/${tripId}/itinerary/generate`,
    body,
  });
  return result.itinerary;
}

export async function getItinerary(tripId: string): Promise<Itinerary> {
  const result = await request<{ itinerary: Itinerary }>({ method: 'GET', path: `/trips/${tripId}/itinerary` });
  return result.itinerary;
}

export async function updateItineraryItem(
  tripId: string,
  itemId: string,
  body: UpdateItineraryItemRequest,
): Promise<ItineraryItemDetail> {
  const result = await request<{ item: ItineraryItemDetail }>({
    method: 'PATCH',
    path: `/trips/${tripId}/itinerary/items/${itemId}`,
    body,
  });
  return result.item;
}

export async function deleteItineraryItem(tripId: string, itemId: string): Promise<string> {
  const result = await request<{ deleted_item_id: string }>({
    method: 'DELETE',
    path: `/trips/${tripId}/itinerary/items/${itemId}`,
  });
  return result.deleted_item_id;
}
