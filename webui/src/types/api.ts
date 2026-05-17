// Shared API envelope types aligned to the backend response format.

export type ApiErrorCode =
  | 'VALIDATION_ERROR'
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'ALREADY_EXISTS'
  | 'CONFLICT'
  | 'INVITE_EXPIRED'
  | 'INVITE_REVOKED'
  | 'INVITE_USAGE_LIMIT_REACHED'
  | 'ITINERARY_ALREADY_EXISTS'
  | 'INTERNAL_SERVER_ERROR'
  | (string & {}); // preserve autocomplete while allowing unknown codes

export interface ApiErrorPayload {
  code: ApiErrorCode;
  message: string;
}

export interface ApiSuccessEnvelope<T> {
  success: true;
  data: T;
  error: null;
  request_id: string;
}

export interface ApiErrorEnvelope {
  success: false;
  data: null;
  error: ApiErrorPayload;
  request_id: string;
}

export type ApiEnvelope<T> = ApiSuccessEnvelope<T> | ApiErrorEnvelope;
