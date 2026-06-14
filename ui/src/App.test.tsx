import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as healthApi from './api/health';
import App from './App';
import { createTestStore } from './test/test-utils';

describe('App', () => {
  beforeEach(() => {
    vi.spyOn(healthApi, 'getHealth').mockResolvedValue({ status: 'ok' });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows the Ask tab by default and can switch to Upload', async () => {
    render(
      <Provider store={createTestStore()}>
        <App />
      </Provider>,
    );

    expect(screen.getByPlaceholderText(/ask a question/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Upload' }));

    expect(screen.getByLabelText(/document/i)).toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/ask a question/i)).not.toBeInTheDocument();
  });
});
