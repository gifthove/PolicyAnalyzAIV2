import { apiFetch } from './client';

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  upload_timestamp: string;
  source_name: string | null;
  policy_date: string | null;
  blob_path: string;
  word_count: number;
  char_count: number;
  chunk_count: number;
  status: string;
}

export function uploadDocument(
  file: File,
  sourceName?: string,
  policyDate?: string,
): Promise<DocumentUploadResponse> {
  const form = new FormData();
  form.append('file', file);
  if (sourceName) form.append('source_name', sourceName);
  if (policyDate) form.append('policy_date', policyDate);

  return apiFetch<DocumentUploadResponse>('/documents', {
    method: 'POST',
    body: form,
  });
}
