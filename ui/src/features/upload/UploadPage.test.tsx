import { fireEvent, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as documentsApi from '../../api/documents';
import { renderWithStore } from '../../test/test-utils';
import { UploadPage } from './UploadPage';

const response = {
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

describe('UploadPage', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('uploads a file and shows the indexing result', async () => {
    vi.spyOn(documentsApi, 'uploadDocument').mockResolvedValue(response);

    renderWithStore(<UploadPage />);

    const file = new File(['hello world'], 'policy.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/document/i) as HTMLInputElement;
    await userEvent.upload(input, file);
    fireEvent.submit(screen.getByRole('button', { name: /^upload$/i }).closest('form')!);

    expect(await screen.findByText('abc-123')).toBeInTheDocument();
    expect(screen.getByText('uploaded')).toBeInTheDocument();
    expect(documentsApi.uploadDocument).toHaveBeenCalledWith(file, undefined, undefined);
  });

  it('shows an error message when the upload fails', async () => {
    vi.spyOn(documentsApi, 'uploadDocument').mockRejectedValue(new Error('File exceeds 20 MB limit'));

    renderWithStore(<UploadPage />);

    const file = new File(['x'], 'big.pdf', { type: 'application/pdf' });
    await userEvent.upload(screen.getByLabelText(/document/i), file);
    fireEvent.submit(screen.getByRole('button', { name: /^upload$/i }).closest('form')!);

    expect(await screen.findByText(/exceeds 20 mb/i)).toBeInTheDocument();
  });

  it('clears the result when "Upload another" is clicked', async () => {
    vi.spyOn(documentsApi, 'uploadDocument').mockResolvedValue(response);

    renderWithStore(<UploadPage />);

    const file = new File(['hello world'], 'policy.pdf', { type: 'application/pdf' });
    await userEvent.upload(screen.getByLabelText(/document/i), file);
    fireEvent.submit(screen.getByRole('button', { name: /^upload$/i }).closest('form')!);
    expect(await screen.findByText('abc-123')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /upload another/i }));

    expect(screen.queryByText('abc-123')).not.toBeInTheDocument();
  });
});
