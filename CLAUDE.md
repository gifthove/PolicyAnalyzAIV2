# Project Instructions

## Run tests before finishing any change

After making any code change in this repo, run the relevant test suite(s) and
make sure they pass before considering the work done.

### API (`api/`)

```bash
cd api
../.venv/Scripts/python.exe -m pytest
```

### UI (`ui/`)

```bash
cd ui
npm run check   # type-check
npm run test    # Vitest unit/component tests
```

If a change touches both `api/` and `ui/` (e.g. API response shapes, CORS,
env vars), run both suites. Fix any failures introduced by the change before
reporting it as complete.
