import { configureStore } from '@reduxjs/toolkit';
import askReducer from '../features/ask/askSlice';
import uploadReducer from '../features/upload/uploadSlice';

export const store = configureStore({
  reducer: {
    ask: askReducer,
    upload: uploadReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
