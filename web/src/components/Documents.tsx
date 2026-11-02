import { useState } from 'react';
import { Card, Chip } from './ui';
import type { SourceSummary } from '../api';

export function Documents({ tenant, sources, chunkSize, busy, onLoadSamples, onIngest, onClear }: {
  tenant: string;
  sources: SourceSummary[];
  chunkSize: number;
  busy: boolean;
  onLoadSamples: () => Promise<void>;
  onIngest: (source: string, text: string) => Promise<void>;
  onClear: () => Promise<void>;
}) {
  const [source, setSource] = useState('');
  const [text, setText] = useState('');
  const total = sources.reduce((sum, s) => sum + s.chunks, 0);

  const add = async () => {
    const name = source.trim() || 'pasted.txt';
    if (!text.trim()) return;
    await onIngest(name, text);
    setSource('');
    setText('');
  };

  return (
    <Card
      title={`Documents for ${tenant}`}
      subtitle={`Split into overlapping chunks of about ${chunkSize} characters, embedded, and indexed under this tenant only.`}
      action={
        <div className="flex gap-2">
          <button className="btn-ghost" disabled={busy} onClick={() => void onLoadSamples()}>
            Load the sample docs
          </button>
          <button className="btn-ghost" disabled={busy || total === 0} onClick={() => void onClear()}>
            Clear
          </button>
        </div>
      }
    >
      {sources.length === 0 ? (
        <p className="text-sm text-slate-500">
          Nothing indexed for this tenant. Load the samples, or paste a document below.
        </p>
      ) : (
        <ul className="flex flex-wrap gap-2">
          {sources.map((s) => (
            <li key={s.source}>
              <Chip tone="info">{s.source} · {s.chunks} chunks</Chip>
            </li>
          ))}
          <li><Chip>{total} chunks in total</Chip></li>
        </ul>
      )}

      <div className="mt-5 grid gap-2">
        <input
          className="field text-xs font-mono"
          placeholder="file name, for the citation (e.g. handbook.txt)"
          value={source}
          onChange={(e) => setSource(e.target.value)}
          aria-label="Document name"
        />
        <textarea
          className="field text-xs h-28"
          placeholder="Paste a document for this tenant. Answers will be built only from what is indexed here."
          value={text}
          onChange={(e) => setText(e.target.value)}
          aria-label="Document text"
        />
        <div className="flex justify-end">
          <button className="btn-primary" disabled={busy || !text.trim()} onClick={() => void add()}>
            Index it
          </button>
        </div>
      </div>
    </Card>
  );
}
