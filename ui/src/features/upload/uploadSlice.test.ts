import { describe, expect, it } from 'vitest';
import type { DocumentUploadResponse } from '../../api/documents';
import uploadReducer, { resetUpload, submitUpload } from './uploadSlice';

const initialState = uploadReducer(undefined, { type: '@@init' });

const response: DocumentUploadResponse = {
  document_id: 'abc-123',
  filename: 'policy.pdf',
  file_type: 'pdf',
  size_bytes: 1024,
  upload_timestamp: '2026-01-01T00:00:00Z',
  source_name: null,
  policy_date: null,
  blob_path: 'abc-123/policy.pdf',
  word_count: 100,
  char_count: 600,
  chunk_count: 3,
  status: 'uploaded',
};

describe('uploadSlice', () => {
  it('sets a loading status and clears the previous result when an upload starts', () => {
    const previous = { ...initialState, result: response };

    const state = uploadReducer(previous, { type: submitUpload.pending.type });

    expect(state.status).toBe('loading');
    expect(state.error).toBeNull();
    expect(state.result).toBeNull();
  });

  it('stores the result and returns to idle on success', () => {
    const state = uploadReducer(initialState, {
      type: submitUpload.fulfilled.type,
      payload: response,
    });

    expect(state.status).toBe('idle');
    expect(state.result).toEqual(response);
  });

  it('stores an error message and sets status to error on failure', () => {
    const state = uploadReducer(initialState, {
      type: submitUpload.rejected.type,
      error: { message: 'File exceeds 20 MB limit' },
    });

    expect(state.status).toBe('error');
    expect(state.error).toBe('File exceeds 20 MB limit');
  });

  it('resets to the initial state', () => {
    const populated = uploadReducer(initialState, {
      type: submitUpload.fulfilled.type,
      payload: response,
    });

    const state = uploadReducer(populated, resetUpload());

    expect(state).toEqual(initialState);
  });
});
