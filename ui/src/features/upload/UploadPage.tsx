import { useRef, useState, type FormEvent } from 'react';
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { resetUpload, submitUpload } from './uploadSlice';

const FileField = styled('label')(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1),
  padding: theme.spacing(1.5),
  border: `1px dashed ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  cursor: 'pointer',
  fontSize: theme.typography.body2.fontSize,
}));

const ResultRow = styled(Box)({
  display: 'flex',
  flexDirection: 'column',
});

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
    <Stack spacing={3}>
      <Stack component="form" onSubmit={handleSubmit} spacing={2} sx={{ maxWidth: 24 * 16 }}>
        <FileField>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <UploadFileIcon fontSize="small" color="action" />
            Document (PDF, DOCX, or TXT — max 20 MB)
          </Box>
          <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt" required />
        </FileField>
        <TextField
          label="Source name (optional)"
          value={sourceName}
          onChange={(event) => setSourceName(event.target.value)}
        />
        <TextField
          label="Policy date (optional)"
          type="date"
          value={policyDate}
          onChange={(event) => setPolicyDate(event.target.value)}
          slotProps={{ inputLabel: { shrink: true } }}
        />
        <Button
          type="submit"
          variant="contained"
          startIcon={<CloudUploadIcon />}
          disabled={status === 'loading'}
          sx={{ alignSelf: 'flex-start' }}
        >
          {status === 'loading' ? 'Uploading...' : 'Upload'}
        </Button>
      </Stack>

      {error && <Alert severity="error">{error}</Alert>}

      {result && (
        <Card variant="outlined">
          <CardContent>
            <Stack spacing={1.5}>
              <ResultRow>
                <Typography variant="caption" color="text.secondary">
                  Document ID
                </Typography>
                <Typography>{result.document_id}</Typography>
              </ResultRow>
              <ResultRow>
                <Typography variant="caption" color="text.secondary">
                  Status
                </Typography>
                <Typography>{result.status}</Typography>
              </ResultRow>
              <ResultRow>
                <Typography variant="caption" color="text.secondary">
                  Words / characters
                </Typography>
                <Typography>
                  {result.word_count} / {result.char_count}
                </Typography>
              </ResultRow>
              <ResultRow>
                <Typography variant="caption" color="text.secondary">
                  Chunks indexed
                </Typography>
                <Typography>{result.chunk_count}</Typography>
              </ResultRow>
              <Button
                type="button"
                variant="outlined"
                startIcon={<RestartAltIcon />}
                onClick={handleReset}
                sx={{ alignSelf: 'flex-start' }}
              >
                Upload another
              </Button>
            </Stack>
          </CardContent>
        </Card>
      )}
    </Stack>
  );
}
