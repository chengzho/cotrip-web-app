import { ApiError } from './apiError';
import type { ApiEnvelope } from '../types/api';

// ---------------------------------------------------------------------------
// Access token provider — injected by Phase 7C (Cognito auth).
// In Phase 7A this is a no-op hook; protected requests are sent without a
// token until a real provider is registered.
// ---------------------------------------------------------------------------

type AccessTokenProvider = () => string | null | Promise<string | null>;

let _tokenProvider: AccessTokenProvider | null = null;

export function configureAccessTokenProvider(
  provider: AccessTokenProvider | null,
): void {
  _tokenProvider = provider;
}

// ---------------------------------------------------------------------------
// Base URL resolution — deferred to request time so a missing env var
// surfaces as a clear runtime error rather than a silent build failure.
// ---------------------------------------------------------------------------

function getBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL;
  if (!base || !base.trim()) {
    throw new Error(
      'VITE_API_BASE_URL is not configured. ' +
        'Set this environment variable before making API requests.',
    );
  }
  return base.trimEnd().replace(/\/+$/, '');
}

// ---------------------------------------------------------------------------
// Core request function
// ---------------------------------------------------------------------------

export interface RequestOptions {
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  path: string;
  body?: unknown;
  /** Pass false to skip the Authorization header (public routes). Default: true */
  auth?: boolean;
}

export async function request<TData>(options: RequestOptions): Promise<TData> {
  const { method, path, body, auth = true } = options;
  const url = `${getBaseUrl()}${path}`;

  const headers: Record<string, string> = {};

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  if (auth && _tokenProvider !== null) {
    const token = await _tokenProvider();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let envelope: ApiEnvelope<TData>;
  try {
    envelope = (await response.json()) as ApiEnvelope<TData>;
  } catch {
    throw new ApiError(
      `Non-JSON response from ${method} ${path} (HTTP ${response.status})`,
      response.status,
      'INTERNAL_SERVER_ERROR',
    );
  }

  if (!response.ok || !envelope.success) {
    const err = envelope.success ? null : envelope.error;
    throw new ApiError(
      err?.message ?? `HTTP ${response.status}`,
      response.status,
      err?.code ?? 'INTERNAL_SERVER_ERROR',
      envelope.request_id,
    );
  }

  return envelope.data;
}
