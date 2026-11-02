// The API this panel speaks, mirroring src/ragassistant/api.py one to one.

export interface Health {
  status: string;
  llm: string;
  store: string;
  embedder: string;
  top_k: number;
  min_confidence: number;
  chunk_size: number;
}

export interface SourceSummary {
  source: string;
  chunks: number;
}

export interface Citation {
  n: number;
  source: string;
  chunk_id: string;
  score: number;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  escalated: boolean;
  reason: string | null;
  path: string[];
  confidence: number;
  flagged: string[];
}

export interface Doc {
  source: string;
  text: string;
}

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, init);
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ? String(detail.detail) : `${path} returned ${res.status}`);
  }
  return res.json() as Promise<T>;
}

const post = (body: unknown): RequestInit =>
  ({ method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });

export const api = {
  health: () => json<Health>('/health'),
  samples: () => json<{ documents: Doc[] }>('/samples'),
  sources: (tenant: string) =>
    json<{ sources: SourceSummary[] }>(`/sources?tenant_id=${encodeURIComponent(tenant)}`),
  clear: (tenant: string) =>
    json<{ chunks_removed: number }>(`/sources?tenant_id=${encodeURIComponent(tenant)}`, { method: 'DELETE' }),
  ingest: (tenant: string, documents: Doc[]) =>
    json<{ chunks_indexed: number; sources: SourceSummary[] }>(
      '/ingest', post({ tenant_id: tenant, documents })),
  chat: (tenant: string, question: string) =>
    json<ChatResponse>('/chat', post({ tenant_id: tenant, question })),
};
