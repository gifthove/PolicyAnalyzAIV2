import { useState, type FormEvent } from 'react';
import { Alert, Button, Collapse, List, Paper, Stack, TextField, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import ClearIcon from '@mui/icons-material/Clear';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import type { QueryCitation } from '../../api/query';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { resetAsk, setQuestion, submitQuestion } from './askSlice';

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

function CitationEntry({ citation }: { citation: QueryCitation }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <CitationItem id={`citation-${citation.citation_id}`}>
      <Typography component="span" sx={{ fontWeight: 'bold' }}>
        {citation.source_name ?? 'Unknown source'}
      </Typography>
      {citation.policy_date && (
        <Typography component="span" color="text.secondary">
          {' '}
          ({citation.policy_date})
        </Typography>
      )}
      <Stack direction="row">
        <Button
          size="small"
          onClick={() => setExpanded((prev) => !prev)}
          endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          sx={{ mt: 0.5 }}
        >
          {expanded ? 'Hide source text' : 'Show source text'}
        </Button>
      </Stack>
      <Collapse in={expanded}>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          {citation.text}
        </Typography>
      </Collapse>
    </CitationItem>
  );
}

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

  const handleClear = () => {
    dispatch(resetAsk());
  };

  const canClear = Boolean(question || result || error);

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
        <Stack direction="row" spacing={1}>
          <Button
            type="submit"
            variant="contained"
            startIcon={<SendIcon />}
            disabled={status === 'loading' || !question.trim()}
          >
            {status === 'loading' ? 'Asking...' : 'Ask'}
          </Button>
          <Button type="button" variant="outlined" startIcon={<ClearIcon />} onClick={handleClear} disabled={!canClear}>
            Clear
          </Button>
        </Stack>
      </Stack>

      {error && <Alert severity="error">{error}</Alert>}

      {result && (
        <AnswerPaper variant="outlined">
          <Typography sx={{ whiteSpace: 'pre-wrap' }}>{result.answer}</Typography>

          {result.citations.length > 0 && (
            <List component="ol" sx={{ pl: 2, listStyleType: 'decimal' }}>
              {result.citations.map((citation) => (
                <CitationEntry key={citation.citation_id} citation={citation} />
              ))}
            </List>
          )}
        </AnswerPaper>
      )}
    </Stack>
  );
}
