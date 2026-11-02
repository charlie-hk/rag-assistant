import { describe, expect, test, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Answer } from '../components/Answer';
import { Route } from '../components/Route';
import { Documents } from '../components/Documents';
import type { ChatResponse } from '../api';

const answered: ChatResponse = {
  answer: 'Based on the documents: encryption keys are rotated every 90 days. [1]',
  citations: [
    { n: 1, source: 'security.txt', chunk_id: 'acme:security.txt:0', score: 0.1862, snippet: 'Encryption keys are rotated every 90 days.' },
    { n: 2, source: 'billing.txt', chunk_id: 'acme:billing.txt:0', score: 0.0741, snippet: 'Plans. ACME Cloud has three plans...' },
  ],
  escalated: false,
  reason: null,
  path: ['guard', 'retrieve', 'answer'],
  confidence: 0.75,
  flagged: [],
};

const escalated: ChatResponse = {
  answer: "I can't answer this reliably from your documents, so I'm routing it to a human.",
  citations: [],
  escalated: true,
  reason: 'Flagged possible prompt injection in the question.',
  path: ['guard', 'retrieve (skipped)', 'escalate'],
  confidence: 0,
  flagged: ['ignore (all|any|the) (previous|above|prior) (instructions|prompts)'],
};

describe('the answer', () => {
  test('separates the sources the answer used from the ones only retrieved', () => {
    render(<Answer result={answered} minConfidence={0.34} />);
    expect(screen.getByText('used in the answer')).toBeInTheDocument();
    expect(screen.getByText('retrieved only')).toBeInTheDocument();
    expect(screen.getByText('security.txt')).toBeInTheDocument();
    expect(screen.getByText('cosine 0.1862')).toBeInTheDocument();
  });

  test('shows the reason and the pattern that fired when it escalated', () => {
    render(<Answer result={escalated} minConfidence={0.34} />);
    expect(screen.getByText('escalated')).toBeInTheDocument();
    expect(screen.getByText(/possible prompt injection/)).toBeInTheDocument();
    expect(screen.getByText(/matched: ignore/)).toBeInTheDocument();
    expect(screen.getByText(/nothing to cite/)).toBeInTheDocument();
  });

  test('states the confidence against the threshold it was graded on', () => {
    render(<Answer result={answered} minConfidence={0.34} />);
    expect(screen.getByText(/75% of the question's content words/)).toBeInTheDocument();
    expect(screen.getByText(/34% threshold/)).toBeInTheDocument();
  });
});

describe('the route', () => {
  test('marks retrieval as skipped when the guard stopped the question', () => {
    render(<Route path={escalated.path} />);
    expect(screen.getByText('skipped')).toBeInTheDocument();
    expect(screen.getByText('guard → retrieve (skipped) → escalate')).toBeInTheDocument();
  });

  test('shows the answering route when the question was grounded', () => {
    render(<Route path={answered.path} />);
    expect(screen.getByText('guard → retrieve → answer')).toBeInTheDocument();
    expect(screen.queryByText('skipped')).not.toBeInTheDocument();
  });
});

describe('the documents panel', () => {
  test('indexes pasted text under the name given for the citation', async () => {
    const onIngest = vi.fn().mockResolvedValue(undefined);
    render(<Documents tenant="acme" sources={[]} chunkSize={500} busy={false}
      onLoadSamples={vi.fn()} onIngest={onIngest} onClear={vi.fn()} />);

    await userEvent.type(screen.getByLabelText('Document name'), 'handbook.txt');
    await userEvent.type(screen.getByLabelText('Document text'), 'Holiday is 25 days.');
    await userEvent.click(screen.getByRole('button', { name: 'Index it' }));

    expect(onIngest).toHaveBeenCalledWith('handbook.txt', 'Holiday is 25 days.');
  });

  test('falls back to a placeholder name rather than refusing the paste', async () => {
    const onIngest = vi.fn().mockResolvedValue(undefined);
    render(<Documents tenant="acme" sources={[]} chunkSize={500} busy={false}
      onLoadSamples={vi.fn()} onIngest={onIngest} onClear={vi.fn()} />);

    await userEvent.type(screen.getByLabelText('Document text'), 'Some policy.');
    await userEvent.click(screen.getByRole('button', { name: 'Index it' }));

    expect(onIngest).toHaveBeenCalledWith('pasted.txt', 'Some policy.');
  });

  test('says what is indexed, per source', () => {
    render(<Documents tenant="acme" chunkSize={500} busy={false}
      sources={[{ source: 'billing.txt', chunks: 2 }, { source: 'security.txt', chunks: 2 }]}
      onLoadSamples={vi.fn()} onIngest={vi.fn()} onClear={vi.fn()} />);
    expect(screen.getByText('billing.txt · 2 chunks')).toBeInTheDocument();
    expect(screen.getByText('4 chunks in total')).toBeInTheDocument();
  });
});
