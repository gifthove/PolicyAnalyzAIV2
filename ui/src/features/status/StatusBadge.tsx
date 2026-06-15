import { useEffect, useState } from 'react';
import { Chip, type ChipProps } from '@mui/material';
import { styled } from '@mui/material/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import { getHealth } from '../../api/health';

type Status = 'checking' | 'online' | 'offline';

const STATUS_COLOR: Record<Status, ChipProps['color']> = {
  checking: 'default',
  online: 'success',
  offline: 'error',
};

const STATUS_ICON: Record<Status, ChipProps['icon']> = {
  checking: <HourglassEmptyIcon />,
  online: <CheckCircleIcon />,
  offline: <ErrorIcon />,
};

const StatusChip = styled(Chip)({
  textTransform: 'capitalize',
});

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

  return (
    <StatusChip
      size="small"
      label={`API: ${status}`}
      color={STATUS_COLOR[status]}
      icon={STATUS_ICON[status]}
    />
  );
}
