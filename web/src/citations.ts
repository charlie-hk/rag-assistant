// Splits an answer into text and its [n] markers, so a citation in the prose can
// be a chip that points at the source it came from. The marker is the whole
// contract between the answer and its evidence, so it is worth a unit test.

export type Part = { kind: 'text'; value: string } | { kind: 'cite'; n: number };

const MARKER = /\[(\d{1,2})\]/g;

export function splitCitations(answer: string): Part[] {
  const parts: Part[] = [];
  let last = 0;
  for (const match of answer.matchAll(MARKER)) {
    const at = match.index ?? 0;
    if (at > last) parts.push({ kind: 'text', value: answer.slice(last, at) });
    parts.push({ kind: 'cite', n: Number(match[1]) });
    last = at + match[0].length;
  }
  if (last < answer.length) parts.push({ kind: 'text', value: answer.slice(last) });
  return parts;
}

// Which sources the answer actually leaned on, as opposed to everything that
// came back from retrieval. The difference matters when judging an answer.
export function citedNumbers(answer: string): number[] {
  return [...new Set([...answer.matchAll(MARKER)].map((m) => Number(m[1])))].sort((a, b) => a - b);
}
