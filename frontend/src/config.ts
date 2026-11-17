/**
 * Application Configuration
 *
 * In development, defaults to 'http://localhost:8000' unless VITE_API_URL is set.
 * In production, uses VITE_API_URL if configured, or falls back to '' (same-origin relative URL)
 * for seamless hosting with backend or reverse proxy.
 */
export const API_BASE_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ||
  (import.meta.env.DEV ? 'http://localhost:8000' : '');
