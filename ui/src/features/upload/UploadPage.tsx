import { useRef, useState, type FormEvent } from 'react';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { resetUpload, submitUpload } from './uploadSlice';
import styles from './Upload.module.css';

export function UploadPage() {
  const dispatch = useAppDispatch();
  const { status, result, error } = useAppSelector((state) => state.upload);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [sourceName, setSourceName] = useState('');
  const [policyDate, setPolicyDate] = useState('');

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;

    dispatch(
      submitUpload({
        file,
        sourceName: sourceName || undefined,
        policyDate: policyDate || undefined,
      }),
    );
  };

  const handleReset = () => {
    dispatch(resetUpload());
    setSourceName('');
    setPolicyDate('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <label className={styles.field}>
          Document (PDF, DOCX, or TXT — max 20 MB)
          <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt" required />
        </label>
        <label className={styles.field}>
          Source name (optional)
          <input type="text" value={sourceName} onChange={(event) => setSourceName(event.target.value)} />
        </label>
        <label className={styles.field}>
          Policy date (optional)
          <input type="date" value={policyDate} onChange={(event) => setPolicyDate(event.target.value)} />
        </label>
        <button type="submit" disabled={status === 'loading'}>
          {status === 'loading' ? 'Uploading...' : 'Upload'}
        </button>
      </form>

      {error && <p className={styles.error}>{error}</p>}

      {result && (
        <div className={styles.result}>
          <dl>
            <dt>Document ID</dt>
            <dd>{result.document_id}</dd>
            <dt>Status</dt>
            <dd>{result.status}</dd>
            <dt>Words / characters</dt>
            <dd>
              {result.word_count} / {result.char_count}
            </dd>
            <dt>Chunks indexed</dt>
            <dd>{result.chunk_count}</dd>
          </dl>
          <button type="button" onClick={handleReset}>
            Upload another
          </button>
        </div>
      )}
    </div>
  );
}
