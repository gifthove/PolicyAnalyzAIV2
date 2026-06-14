import { useEffect, useState } from 'react';
import { getHealth } from '../../api/health';
import styles from './Status.module.css';

type Status = 'checking' | 'online' | 'offline';

export function StatusBadge() {
  const [status, setStatus] = useState<Status>('checking');

  useEffect(() => {
    let cancelled = false;

    getHealth()
      .then(() => {
        if (!cancelled) setStatus('online');
      })
      .catch(() => {
        if (!cancelled) setStatus('offline');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return <span className={`${styles.badge} ${styles[status]}`}>API: {status}</span>;
}
