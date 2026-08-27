/** Empty = same origin (Vite proxy / Render one-URL). Set on Vercel to the Render API. */
export const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return API_BASE ? `${API_BASE}${normalized}` : normalized;
}

/** Make /chat (and other API paths) work when the landing is on Vercel. */
export function resolveHref(href: string | null | undefined): string | null | undefined {
  if (!href || href.startsWith("http") || !API_BASE) {
    return href;
  }
  return href.startsWith("/") ? `${API_BASE}${href}` : href;
}
