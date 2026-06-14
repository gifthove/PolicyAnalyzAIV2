import { useState } from 'react';
import { AskPage } from './features/ask/AskPage';
import { UploadPage } from './features/upload/UploadPage';
import { StatusBadge } from './features/status/StatusBadge';
import styles from './App.module.css';

type Tab = 'ask' | 'upload';

export default function App() {
  const [tab, setTab] = useState<Tab>('ask');

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <h1>PolicyAnalyzAI</h1>
        <StatusBadge />
      </header>

      <nav className={styles.nav}>
        <button
          className={tab === 'ask' ? styles.active : undefined}
          onClick={() => setTab('ask')}
        >
          Ask
        </button>
        <button
          className={tab === 'upload' ? styles.active : undefined}
          onClick={() => setTab('upload')}
        >
          Upload
        </button>
      </nav>

      <main className={styles.main}>{tab === 'ask' ? <AskPage /> : <UploadPage />}</main>
    </div>
  );
}
