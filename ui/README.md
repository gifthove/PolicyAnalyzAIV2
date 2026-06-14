# PolicyAnalyzAI UI

React SPA frontend for the PolicyAnalyzAI API.

Stack: React 19 + TypeScript + Redux Toolkit + CSS Modules + Parcel,
organised by feature folders. Deployed as its own container into the shared
Container App Environment (see top-level [README](../README.md)).

## Getting Started

```bash
npm install
cp .env.example .env   # set API_BASE_URL if the API isn't on the same origin
npm start               # dev server (Parcel)
npm run check           # type-check
npm run test            # unit/component tests (Vitest)
npm run build           # production build to dist/
```

The API must allow the UI's origin via CORS — set `CORS_ALLOWED_ORIGINS` on
the API (defaults to `*`).

---

## Testing

Tests use [Vitest](https://vitest.dev) with React Testing Library and jsdom.

```bash
npm run test         # run once (used in CI)
npm run test:watch   # watch mode
```

- `src/api/client.test.ts` — shared fetch wrapper's success/error handling
- `src/features/ask/askSlice.test.ts`, `src/features/upload/uploadSlice.test.ts` —
  reducer/thunk state transitions
- `src/features/ask/AskPage.test.tsx`, `src/features/upload/UploadPage.test.tsx`,
  `src/features/status/StatusBadge.test.tsx`, `src/App.test.tsx` — component
  behaviour with the API layer mocked via `vi.spyOn`

`src/test/setup.ts` wires up `@testing-library/jest-dom` matchers, and
`src/test/test-utils.tsx` provides `renderWithStore` for rendering components
with a fresh Redux store.

---

## Features

### Ask (query / chat)

Calls `POST /query` with `{ question, top_k }`.

- A single text input where a user asks a question about the indexed policy
  documents.
- Renders the returned `answer`, which contains inline bracketed citation
  markers (`[1]`, `[2]`, ...).
- A citations panel lists each `QueryCitation`: source document name, policy
  date, chunk text excerpt, and relevance score — clicking a citation marker
  scrolls to / highlights the matching entry.
- If the model has insufficient evidence, the answer text says so plainly
  (no citations are fabricated).

### Upload (document ingestion)

Calls `POST /documents` (multipart form: `file`, optional `source_name`,
optional `policy_date`).

- File picker accepting PDF, DOCX, or TXT (20 MB max, enforced
  server-side).
- Optional fields for source name and policy date, attached to every chunk
  indexed from the document.
- After upload, shows the `DocumentUploadResponse`: filename, file type,
  size, word/char counts, number of chunks indexed, and status.
- Surfaces API errors for unsupported file types, oversized files, or
  indexing failures.

### Status

Calls `GET /health`.

- Small connectivity indicator (e.g. header/footer badge) showing whether
  the API is reachable.

### Users (placeholder)

`GET /users` currently returns a static placeholder record. No UI is planned
for this until the API grows real user/auth functionality.

---

## Known API Gaps for a Full UI

- No endpoint to **list** previously uploaded documents — the Upload screen
  can only show the result of the document just submitted, not a document
  library/history view.
- No authentication — all endpoints are currently open.

---

## Project Layout

```
ui/
├── index.html
├── package.json
├── tsconfig.json
├── Dockerfile / nginx.conf   # production image: build with node, serve with nginx
├── .env.example
└── src/
    ├── index.tsx             # entry point (renders <App> with Redux <Provider>)
    ├── App.tsx               # tab nav between Ask / Upload + status badge
    ├── app/
    │   ├── store.ts          # Redux store
    │   └── hooks.ts          # typed useAppDispatch / useAppSelector
    ├── api/                  # typed fetch client per endpoint
    │   ├── client.ts
    │   ├── query.ts
    │   ├── documents.ts
    │   └── health.ts
    ├── features/
    │   ├── ask/              # query input, answer + citations display
    │   ├── upload/           # document upload form + result
    │   └── status/           # health indicator
    ├── test/                 # Vitest setup + renderWithStore test util
    └── styles/               # shared global CSS
```

`*.test.ts(x)` files live alongside the code they cover (e.g.
`features/ask/askSlice.test.ts`).

A `users` feature is intentionally not scaffolded — see "Users (placeholder)"
above.
