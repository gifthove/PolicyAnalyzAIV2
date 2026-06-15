import { useState } from 'react';
import { Alert, AppBar, Box, Button, Container, Stack, Toolbar, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import { AskPage } from './features/ask/AskPage';
import { UploadPage } from './features/upload/UploadPage';
import { StatusBadge } from './features/status/StatusBadge';

type Tab = 'ask' | 'upload';

const Root = styled(Box)({
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100vh',
});

const Footer = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
  fontSize: theme.typography.caption.fontSize,
}));

export default function App() {
  const [tab, setTab] = useState<Tab>('ask');

  return (
    <Root>
      <AppBar position="static">
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" component="h1">
            PolicyAnalyzAI
          </Typography>
          <StatusBadge />
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ display: 'flex', flexDirection: 'column', gap: 3, py: 3, flexGrow: 1 }}>
        <Alert severity="info">
          <Typography variant="body2">
            Upload PDF, DOCX, or TXT policy documents to build a searchable corpus — each one is split into
            chunks, embedded, and indexed.
          </Typography>
          <Typography variant="body2">
            Then use Ask to ask questions in plain English; answers are generated from your indexed
            documents with citations back to the source chunks.
          </Typography>
        </Alert>

        <Stack direction="row" spacing={1} sx={{ justifyContent: 'center' }}>
          <Button variant={tab === 'ask' ? 'contained' : 'outlined'} onClick={() => setTab('ask')}>
            Ask
          </Button>
          <Button variant={tab === 'upload' ? 'contained' : 'outlined'} onClick={() => setTab('upload')}>
            Upload
          </Button>
        </Stack>

        <Box sx={{ width: '100%', maxWidth: 640, mx: 'auto' }}>{tab === 'ask' ? <AskPage /> : <UploadPage />}</Box>
      </Container>

      <Footer>Designed by gifthove</Footer>
    </Root>
  );
}
