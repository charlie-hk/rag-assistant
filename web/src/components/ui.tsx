import type { ReactNode } from 'react';

const tones = {
  good: 'text-good border-good/40 bg-good/10',
  warn: 'text-warn border-warn/40 bg-warn/10',
  bad: 'text-bad border-bad/40 bg-bad/10',
  info: 'text-[#58a6ff] border-info/40 bg-info/10',
  mute: 'text-slate-400 border-edge bg-white/5',
} as const;

export type Tone = keyof typeof tones;

export function Chip({ tone = 'mute', children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`chip ${tones[tone]}`}>{children}</span>;
}

export function Card({ title, subtitle, action, children }: {
  title: string; subtitle?: string; action?: ReactNode; children: ReactNode;
}) {
  return (
    <section className="card overflow-hidden">
      <header className="flex items-start gap-4 px-5 py-4 border-b border-edge/70">
        <div className="min-w-0">
          <h2 className="text-sm font-semibold text-slate-100">{title}</h2>
          {subtitle ? <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p> : null}
        </div>
        {action ? <div className="ml-auto shrink-0">{action}</div> : null}
      </header>
      <div className="p-5">{children}</div>
    </section>
  );
}
