import { Card } from './ui';

// The nodes of the LangGraph workflow, in order, with the ones this question
// actually went through lit up. "It escalated" is a claim; this is the evidence.
const NODES = [
  { key: 'guard', label: 'guard', hint: 'injection patterns' },
  { key: 'retrieve', label: 'retrieve', hint: 'hybrid search, scoped to the tenant' },
  { key: 'grade', label: 'grade', hint: 'confident enough to answer?' },
  { key: 'answer', label: 'answer', hint: 'only from the context' },
  { key: 'escalate', label: 'escalate', hint: 'hand it to a person' },
];

export function Route({ path }: { path: string[] }) {
  // The graph has no explicit grade node to record: it is the conditional edge
  // out of retrieve, so it counts as visited whenever retrieve ran.
  const visited = new Set(path.map((p) => p.split(' ')[0]));
  if (visited.has('retrieve') && !path.includes('retrieve (skipped)')) visited.add('grade');
  const skipped = path.includes('retrieve (skipped)');

  return (
    <Card title="The route this question took" subtitle="guard, retrieve, grade, then either answer or escalate.">
      <div className="flex flex-wrap items-stretch gap-2">
        {NODES.map((node, i) => {
          const on = visited.has(node.key) && !(node.key === 'retrieve' && skipped);
          const isSkipped = node.key === 'retrieve' && skipped;
          const tone = on
            ? node.key === 'escalate' ? 'border-warn text-warn bg-warn/10'
              : node.key === 'answer' ? 'border-good text-good bg-good/10'
              : 'border-info text-[#58a6ff] bg-info/10'
            : 'border-edge/70 text-slate-600';
          return (
            <div key={node.key} className="flex items-center gap-2">
              <div className={`rounded-lg border px-3 py-2 min-w-[132px] ${tone}`}>
                <div className="font-mono text-xs">{node.label}</div>
                <div className="text-[10.5px] text-slate-500 mt-0.5 leading-tight">
                  {isSkipped ? 'skipped' : node.hint}
                </div>
              </div>
              {i < NODES.length - 1 ? <span className="text-slate-700">&rarr;</span> : null}
            </div>
          );
        })}
      </div>
      <p className="font-mono text-[11px] text-slate-600 mt-3">{path.join(' → ') || 'nothing yet'}</p>
    </Card>
  );
}
