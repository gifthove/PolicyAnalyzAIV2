import type { FormEvent } from 'react';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { setQuestion, submitQuestion } from './askSlice';
import styles from './Ask.module.css';

export function AskPage() {
  const dispatch = useAppDispatch();
  const { question, result, status, error } = useAppSelector((state) => state.ask);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (trimmed) {
      dispatch(submitQuestion(trimmed));
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <textarea
          className={styles.input}
          value={question}
          onChange={(event) => dispatch(setQuestion(event.target.value))}
          placeholder="Ask a question about the indexed policy documents..."
          rows={3}
        />
        <button type="submit" disabled={status === 'loading' || !question.trim()}>
          {status === 'loading' ? 'Asking...' : 'Ask'}
        </button>
      </form>

      {error && <p className={styles.error}>{error}</p>}

      {result && (
        <div className={styles.result}>
          <p className={styles.answer}>{result.answer}</p>

          {result.citations.length > 0 && (
            <ol className={styles.citations}>
              {result.citations.map((citation) => (
                <li key={citation.citation_id} id={`citation-${citation.citation_id}`}>
                  <strong>{citation.source_name ?? 'Unknown source'}</strong>
                  {citation.policy_date && <span> ({citation.policy_date})</span>}
                  <p>{citation.text}</p>
                </li>
              ))}
            </ol>
          )}
        </div>
      )}
    </div>
  );
}
