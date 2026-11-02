import { describe, expect, test } from 'vitest';
import { citedNumbers, splitCitations } from '../citations';

describe('citation markers', () => {
  test('splits prose from the markers in it', () => {
    expect(splitCitations('Keys rotate every 90 days [1] and data stays in the EU [2].')).toEqual([
      { kind: 'text', value: 'Keys rotate every 90 days ' },
      { kind: 'cite', n: 1 },
      { kind: 'text', value: ' and data stays in the EU ' },
      { kind: 'cite', n: 2 },
      { kind: 'text', value: '.' },
    ]);
  });

  test('an answer with no markers is left alone', () => {
    expect(splitCitations('I don\'t know.')).toEqual([{ kind: 'text', value: 'I don\'t know.' }]);
  });

  test('a marker at the very end does not produce an empty tail', () => {
    expect(splitCitations('Billed monthly [3]')).toEqual([
      { kind: 'text', value: 'Billed monthly ' },
      { kind: 'cite', n: 3 },
    ]);
  });

  test('reports which sources the answer leaned on, deduplicated and in order', () => {
    expect(citedNumbers('a [2] b [1] c [2]')).toEqual([1, 2]);
    expect(citedNumbers('nothing here')).toEqual([]);
  });

  test('a bracketed number that is not a citation still reads as one, which is the honest limit', () => {
    // The mock and real models both emit [n] and nothing else, so this is the
    // contract. Worth knowing it is a convention rather than a guarantee.
    expect(citedNumbers('see section [4] of the handbook')).toEqual([4]);
  });
});
