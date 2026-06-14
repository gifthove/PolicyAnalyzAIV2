import { configureStore } from '@reduxjs/toolkit';
import { render, type RenderResult } from '@testing-library/react';
import type { ReactElement } from 'react';
import { Provider } from 'react-redux';
import askReducer from '../features/ask/askSlice';
import uploadReducer from '../features/upload/uploadSlice';

export function createTestStore() {
  return configureStore({
    reducer: {
      ask: askReducer,
      upload: uploadReducer,
    },
  });
}

export type TestStore = ReturnType<typeof createTestStore>;

export function renderWithStore(
  ui: ReactElement,
  store: TestStore = createTestStore(),
): RenderResult & { store: TestStore } {
  return { store, ...render(<Provider store={store}>{ui}</Provider>) };
}
