import { describe, expect, it } from 'vitest';
import type { QueryResponse } from '../../api/query';
import askReducer, { resetAsk, setQuestion, submitQuestion } from './askSlice';

const initialState = askReducer(undefined, { type: '@@init' });

describe('askSlice', () => {
  it('updates the question text', () => {
    const state = askReducer(initialState, setQuestion('What is the leave policy?'));

    expect(state.question).toBe('What is the leave policy?');
  });

  it('sets a loading status and clears errors when a question is submitted', () => {
    const errored = { ...initialState, status: 'error' as const, error: 'previous failure' };

    const state = askReducer(errored, { type: submitQuestion.pending.type });

    expect(state.status).toBe('loading');
    expect(state.error).toBeNull();
  });

  it('stores the result and returns to idle on success', () => {
    const response: QueryResponse = { answer: 'Yes [1].', citations: [] };

    const state = askReducer(initialState, {
      type: submitQuestion.fulfilled.type,
      payload: response,
    });

    expect(state.status).toBe('idle');
    expect(state.result).toEqual(response);
  });

  it('stores an error message and sets status to error on failure', () => {
    const state = askReducer(initialState, {
      type: submitQuestion.rejected.type,
      error: { message: 'Failed to answer query' },
    });

    expect(state.status).toBe('error');
    expect(state.error).toBe('Failed to answer query');
  });

  it('clears the question, result, and error on reset', () => {
    const response: QueryResponse = { answer: 'Yes [1].', citations: [] };
    const populated = {
      question: 'What is the leave policy?',
      result: response,
      status: 'error' as const,
      error: 'previous failure',
    };

    const state = askReducer(populated, resetAsk());

    expect(state.question).toBe('');
    expect(state.result).toBeNull();
    expect(state.status).toBe('idle');
    expect(state.error).toBeNull();
  });
});
