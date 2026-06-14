import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiFetch, ApiError } from './client';

describe('apiFetch', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns parsed JSON on success', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'ok' }),
      }),
    );

    const result = await apiFetch<{ status: string }>('/health');

    expect(result).toEqual({ status: 'ok' });
  });

  it('throws an ApiError with the response detail on failure', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        json: async () => ({ detail: 'Question must not be blank' }),
      }),
    );

    const error = await apiFetch('/query').catch((err) => err);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 422, message: 'Question must not be blank' });
  });

  it('falls back to statusText when the error body has no detail', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('not json');
        },
      }),
    );

    const error = await apiFetch('/query').catch((err) => err);

    expect(error).toMatchObject({ status: 500, message: 'Internal Server Error' });
  });
});
