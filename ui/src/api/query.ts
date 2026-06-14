import { apiFetch } from './client';

export interface QueryCitation {
  citation_id: number;
  chunk_id: string;
  document_id: string;
  source_name: string | null;
  policy_date: string | null;
  chunk_index: number;
  score: number | null;
  text: string;
}

export interface QueryResponse {
  answer: string;
  citations: QueryCitation[];
}

export function askQuestion(question: string, topK = 5): Promise<QueryResponse> {
  return apiFetch<QueryResponse>('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
  });
}
