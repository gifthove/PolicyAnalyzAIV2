import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as queryApi from '../../api/query';
import { renderWithStore } from '../../test/test-utils';
import { AskPage } from './AskPage';

describe('AskPage', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('disables the submit button until a question is entered', () => {
    renderWithStore(<AskPage />);

    expect(screen.getByRole('button', { name: /ask/i })).toBeDisabled();
  });

  it('submits the question and renders the answer with citations', async () => {
    vi.spyOn(queryApi, 'askQuestion').mockResolvedValue({
      answer: 'Employees get 20 days of annual leave [1].',
      citations: [
        {
          citation_id: 1,
          chunk_id: 'doc1_0',
          document_id: 'doc1',
          source_name: 'Leave Policy 2024',
          policy_date: '2024-01-01',
          chunk_index: 0,
          score: 0.9,
          text: 'Annual leave entitlement is 20 days per year.',
        },
      ],
    });

    renderWithStore(<AskPage />);

    await userEvent.type(
      screen.getByPlaceholderText(/ask a question/i),
      'How much annual leave do I get?',
    );
    await userEvent.click(screen.getByRole('button', { name: /ask/i }));

    expect(await screen.findByText(/20 days of annual leave/i)).toBeInTheDocument();
    expect(screen.getByText('Leave Policy 2024')).toBeInTheDocument();
    expect(queryApi.askQuestion).toHaveBeenCalledWith('How much annual leave do I get?');
  });

  it('shows an error message when the request fails', async () => {
    vi.spyOn(queryApi, 'askQuestion').mockRejectedValue(new Error('Failed to answer query'));

    renderWithStore(<AskPage />);

    await userEvent.type(screen.getByPlaceholderText(/ask a question/i), 'Will this fail?');
    await userEvent.click(screen.getByRole('button', { name: /ask/i }));

    expect(await screen.findByText(/failed to answer query/i)).toBeInTheDocument();
  });
});
