import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as healthApi from '../../api/health';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows online when the health check succeeds', async () => {
    vi.spyOn(healthApi, 'getHealth').mockResolvedValue({ status: 'ok' });

    render(<StatusBadge />);

    expect(await screen.findByText(/online/i)).toBeInTheDocument();
  });

  it('shows offline when the health check fails', async () => {
    vi.spyOn(healthApi, 'getHealth').mockRejectedValue(new Error('network error'));

    render(<StatusBadge />);

    expect(await screen.findByText(/offline/i)).toBeInTheDocument();
  });
});
