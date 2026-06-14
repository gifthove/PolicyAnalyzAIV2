import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { uploadDocument, type DocumentUploadResponse } from '../../api/documents';

interface UploadArgs {
  file: File;
  sourceName?: string;
  policyDate?: string;
}

interface UploadState {
  status: 'idle' | 'loading' | 'error';
  result: DocumentUploadResponse | null;
  error: string | null;
}

const initialState: UploadState = {
  status: 'idle',
  result: null,
  error: null,
};

export const submitUpload = createAsyncThunk('upload/submit', async (args: UploadArgs) => {
  return uploadDocument(args.file, args.sourceName, args.policyDate);
});

const uploadSlice = createSlice({
  name: 'upload',
  initialState,
  reducers: {
    resetUpload(state) {
      state.status = 'idle';
      state.result = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitUpload.pending, (state) => {
        state.status = 'loading';
        state.error = null;
        state.result = null;
      })
      .addCase(submitUpload.fulfilled, (state, action) => {
        state.status = 'idle';
        state.result = action.payload;
      })
      .addCase(submitUpload.rejected, (state, action) => {
        state.status = 'error';
        state.error = action.error.message ?? 'Failed to upload document';
      });
  },
});

export const { resetUpload } = uploadSlice.actions;
export default uploadSlice.reducer;
