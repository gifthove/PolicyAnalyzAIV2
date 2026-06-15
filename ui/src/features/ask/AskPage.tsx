import type { FormEvent } from 'react';
import { Alert, Button, List, Paper, Stack, TextField, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { setQuestion, submitQuestion } from './askSlice';

const AnswerPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(2),
}));

const CitationItem = styled('li')(({ theme }) => ({
  borderLeft: `3px solid ${theme.palette.primary.main}`,
  paddingLeft: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  '&:last-child': {
    marginBottom: 0,
  },
}));

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
    <Stack spacing={3}>
      <Stack component="form" onSubmit={handleSubmit} spacing={2}>
        <TextField
          value={question}
          onChange={(event) => dispatch(setQuestion(event.target.value))}
          placeholder="Ask a question about the indexed policy documents..."
          multiline
          minRows={3}
          fullWidth
        />
        <Button
          type="submit"
          variant="contained"
          startIcon={<SendIcon />}
          disabled={status === 'loading' || !question.trim()}
          sx={{ alignSelf: 'flex-start' }}
        >
          {status === 'loading' ? 'Asking...' : 'Ask'}
        </Button>
      </Stack>

      {error && <Alert severity="error">{error}</Alert>}

      {result && (
        <AnswerPaper variant="outlined">
          <Typography sx={{ whiteSpace: 'pre-wrap' }}>{result.answer}</Typography>

          {result.citations.length > 0 && (
            <List component="ol" sx={{ pl: 2, listStyleType: 'decimal' }}>
              {result.citations.map((citation) => (
                <CitationItem key={citation.citation_id} id={`citation-${citation.citation_id}`}>
                  <Typography component="span" sx={{ fontWeight: 'bold' }}>
                    {citation.source_name ?? 'Unknown source'}
                  </Typography>
                  {citation.policy_date && (
                    <Typography component="span" color="text.secondary">
                      {' '}
                      ({citation.policy_date})
                    </Typography>
                  )}
                  <Typography sx={{ mt: 0.5 }}>{citation.text}</Typography>
                </CitationItem>
              ))}
            </List>
          )}
        </AnswerPaper>
      )}
    </Stack>
  );
}
