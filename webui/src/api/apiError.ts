import type { ApiErrorCode } from '../types/api';

/**
 * Thrown by the HTTP client for any non-successful API response.
 * Preserves HTTP status, backend error code, backend message, and request ID
 * so page-level code can branch on specific failure cases without parsing
 * raw response objects.
 */
export class ApiError extends Error {
  readonly statusCode: number;
  readonly errorCode: ApiErrorCode;
  readonly requestId: string;

  constructor(
    message: string,
    statusCode: number,
    errorCode: ApiErrorCode,
    requestId: string = '',
  ) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.requestId = requestId;
    // Restore prototype chain for instanceof checks across transpilation targets.
    Object.setPrototypeOf(this, new.target.prototype);
  }

  get isNotFound(): boolean {
    return this.statusCode === 404;
  }

  get isForbidden(): boolean {
    return this.statusCode === 403;
  }

  get isUnauthorized(): boolean {
    return this.statusCode === 401;
  }

  get isConflict(): boolean {
    return this.statusCode === 409;
  }

  get isValidationError(): boolean {
    return this.statusCode === 400;
  }
}
