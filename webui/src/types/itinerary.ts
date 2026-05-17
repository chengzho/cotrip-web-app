// Itinerary domain types.
// Field names match actual backend API response payloads.

export type ItinerarySlot = 'morning' | 'lunch' | 'afternoon' | 'dinner' | 'evening';

// One item within a day in the itinerary response
export interface ItineraryItem {
  item_id: string;
  slot: ItinerarySlot;
  title: string;
  candidate_id: string | null;
  category: string;
  note: string | null;
  sort_order: number;
}

// One day group in the itinerary response
export interface ItineraryDay {
  day_number: number;
  date: string;
  items: ItineraryItem[];
}

// Full itinerary returned by generate and get endpoints
export interface Itinerary {
  trip_id: string;
  days: ItineraryDay[];
}

// Full itinerary item returned by PATCH /trips/{tripId}/itinerary/items/{itemId}
export interface ItineraryItemDetail extends ItineraryItem {
  trip_id: string;
  day_number: number;
}

// Request body for POST /trips/{tripId}/itinerary/generate
export interface GenerateItineraryRequest {
  overwrite_existing?: boolean;
}

// Request body for PATCH /trips/{tripId}/itinerary/items/{itemId}
export interface UpdateItineraryItemRequest {
  day_number?: number;
  slot?: ItinerarySlot;
  title?: string;
  note?: string | null;
  sort_order?: number;
}
