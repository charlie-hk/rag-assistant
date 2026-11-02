import { Card, Chip } from './ui';
import { citedNumbers, splitCitations } from '../citations';
import type { ChatResponse } from '../api';

export function Answer({ result, minConfidence }: { result: ChatResponse; minConfidence: number }) {
  const cited = new Set(citedNumbers(result.answer));
  const pct = Math.round(result.confidence * 100);
  const threshold = Math.round(minConfidence * 100);

  return (
    <Card
      title={result.escalated ? 'Sent to a human' : 'Answer'}
      subtitle={result.escalated
        ? 'Nothing was answered from guesswork. The reason is recorded below.'
        : 'Built only from the retrieved context, and citing it.'}
      action={<Chip tone={result.escalated ? 'warn' : 'good'}>{result.escalated ? 'escalated' : 'answered'}</Chip>}
    >
      {result.escalated ? (
        <div className="border border-warn/40 bg-warn/10 rounded-lg px-4 py-3 mb-4">
          <p className="text-sm text-warn">{result.reason}</p>
          {result.flagged.length ? (
            <div className="mt-2 flex flex-wrap gap-2">
              {result.flagged.map((pattern) => (
                <Chip key={pattern} tone="bad">matched: {pattern}</Chip>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}

      <p className="text-[15px] leading-relaxed text-slate-100 whitespace-pre-wrap">
        {splitCitations(result.answer).map((part, i) =>
          part.kind === 'text' ? (
            <span key={i}>{part.value}</span>
          ) : (
            <a key={i} href={`#citation-${part.n}`} className="mx-0.5 align-super text-[11px]
                 font-mono text-[#58a6ff] hover:underline">[{part.n}]</a>
          ),
        )}
      </p>

      <div className="mt-5">
        <div className="flex items-baseline gap-2">
          <span className="label">grounding confidence</span>
          <span className="font-mono text-xs text-slate-400">
            {pct}% of the question's content words appear in the retrieved text
          </span>
        </div>
        <div className="mt-2 h-1.5 rounded-full bg-ink-900 border border-edge/60 relative overflow-hidden">
          <div
            className={`h-full ${result.confidence >= minConfidence ? 'bg-good' : 'bg-warn'}`}
            style={{ width: `${Math.min(100, pct)}%` }}
          />
          <div className="absolute inset-y-0 w-px bg-slate-500" style={{ left: `${threshold}%` }} />
        </div>
        <p className="text-[11px] text-slate-600 mt-1 font-mono">
          the line is the {threshold}% threshold: below it, the graph escalates instead of answering
        </p>
      </div>

      {result.citations.length ? (
        <ol className="mt-5 space-y-2">
          {result.citations.map((c) => (
            <li
              key={c.chunk_id}
              id={`citation-${c.n}`}
              className={`bg-ink-900/60 border rounded-lg px-4 py-3 ${
                cited.has(c.n) ? 'border-info/50' : 'border-edge/60'}`}
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs text-[#58a6ff]">[{c.n}]</span>
                <span className="font-mono text-xs text-slate-200">{c.source}</span>
                <Chip>cosine {c.score.toFixed(4)}</Chip>
                {cited.has(c.n) ? <Chip tone="info">used in the answer</Chip> : <Chip>retrieved only</Chip>}
                <span className="ml-auto font-mono text-[11px] text-slate-600">{c.chunk_id}</span>
              </div>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">{c.snippet}</p>
            </li>
          ))}
        </ol>
      ) : (
        <p className="text-sm text-slate-500 mt-5">
          Nothing was retrieved for this tenant, so there is nothing to cite.
        </p>
      )}
    </Card>
  );
}
