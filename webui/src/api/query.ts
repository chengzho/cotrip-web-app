/**
 * Build a query string from a plain key-value map.
 * Omits keys whose value is undefined, null, or an empty string.
 * Returns the leading "?" only when there is at least one included entry.
 */
export function buildQueryString(
  params: Record<string, string | undefined | null>,
): string {
  const pairs: string[] = [];
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      pairs.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
    }
  }
  return pairs.length > 0 ? `?${pairs.join('&')}` : '';
}
