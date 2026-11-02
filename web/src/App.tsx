import { useCallback, useEffect, useState } from 'react';
import { api, type ChatResponse, type Health, type SourceSummary } from './api';
import { Answer } from './components/Answer';
import { Ask } from './components/Ask';
import { Documents } from './components/Documents';
import { Route } from './components/Route';
import { Chip } from './components/ui';

// Two tenants, because isolation is the kind of claim nobody should take on
// trust: index documents under one, then ask the other the same question.
const TENANTS = ['acme', 'globex'];

export function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [tenant, setTenant] = useState(TENANTS[0]);
  const [sources, setSources] = useState<SourceSummary[]>([]);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSources = useCallback(async (which: string) => {
    try {
      setSources((await api.sources(which)).sources);
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  useEffect(() => {
    api.health().then(setHealth).catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    setResult(null);
    void refreshSources(tenant);
  }, [tenant, refreshSources]);

  const run = async (work: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await work();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-edge/70 bg-ink-800/90 backdrop-blur sticky top-0 z-10">
        <div className="mx-auto max-w-5xl px-5 py-4 flex flex-wrap items-center gap-x-4 gap-y-2">
          <h1 className="text-xl font-bold tracking-tight text-slate-50">
            RAG Assistant<span className="text-good">.</span>
          </h1>
          <p className="text-xs text-slate-500">
            answers only from your documents, cites them, escalates the rest
            <a className="ml-2 font-mono text-slate-600 hover:text-slate-400"
               href="https://github.com/charlie-hk/rag-assistant">A.Amini</a>
          </p>
          <div className="ml-auto flex flex-wrap items-center gap-2">
            {health ? (
              <>
                <Chip tone="info">model: {health.llm}</Chip>
                <Chip>store: {health.store}</Chip>
                <Chip>embedder: {health.embedder}</Chip>
                <Chip>top {health.top_k}</Chip>
              </>
            ) : (
              <Chip tone="warn">connecting</Chip>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-5 py-6 space-y-6">
        {error ? (
          <p className="text-xs text-bad border border-bad/40 bg-bad/10 rounded-lg px-4 py-3">
            {error} — is the API running? <span className="font-mono">uvicorn ragassistant.api:app --app-dir src</span>
          </p>
        ) : null}

        <div className="flex flex-wrap items-center gap-2">
          <span className="label">tenant</span>
          {TENANTS.map((name) => (
            <button
              key={name}
              onClick={() => setTenant(name)}
              className={`btn ${tenant === name
                ? 'bg-info/15 border border-info/60 text-[#58a6ff]'
                : 'border border-edge text-slate-400 hover:border-slate-500'}`}
            >
              {name}
            </button>
          ))}
          <p className="text-xs text-slate-500 ml-2">
            A query is scoped to its tenant in the store, so one tenant's documents cannot be retrieved for another.
          </p>
        </div>

        <Documents
          tenant={tenant}
          sources={sources}
          chunkSize={health?.chunk_size ?? 500}
          busy={busy}
          onLoadSamples={() => run(async () => {
            const { documents } = await api.samples();
            await api.ingest(tenant, documents);
            await refreshSources(tenant);
          })}
          onIngest={(source, text) => run(async () => {
            await api.ingest(tenant, [{ source, text }]);
            await refreshSources(tenant);
          })}
          onClear={() => run(async () => {
            await api.clear(tenant);
            setResult(null);
            await refreshSources(tenant);
          })}
        />

        <Ask busy={busy} onAsk={(question) => run(async () => setResult(await api.chat(tenant, question)))} />

        {result ? (
          <>
            <Answer result={result} minConfidence={health?.min_confidence ?? 0.34} />
            <Route path={result.path} />
          </>
        ) : null}

        <footer className="pt-2 pb-10 text-xs text-slate-600">
          <a className="hover:text-slate-400" href="https://github.com/charlie-hk/rag-assistant">
            github.com/charlie-hk/rag-assistant
          </a>
        </footer>
      </main>
    </div>
  );
}
