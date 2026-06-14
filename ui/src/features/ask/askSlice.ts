import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit';
import { askQuestion, type QueryResponse } from '../../api/query';

interface AskState {
  question: string;
  result: QueryResponse | null;
  status: 'idle' | 'loading' | 'error';
  error: string | null;
}

const initialState: AskState = {
  question: '',
  result: null,
  status: 'idle',
  error: null,
};

export const submitQuestion = createAsyncThunk('ask/submit', async (question: string) => {
  return askQuestion(question);
});

const askSlice = createSlice({
  name: 'ask',
  initialState,
  reducers: {
    setQuestion(state, action: PayloadAction<string>) {
      state.question = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitQuestion.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(submitQuestion.fulfilled, (state, action) => {
        state.status = 'idle';
        state.result = action.payload;
      })
      .addCase(submitQuestion.rejected, (state, action) => {
        state.status = 'error';
        state.error = action.error.message ?? 'Failed to get an answer';
      });
  },
});

export const { setQuestion } = askSlice.actions;
export default askSlice.reducer;
