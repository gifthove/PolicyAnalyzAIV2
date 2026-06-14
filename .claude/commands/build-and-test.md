# Build and Test (API + UI)

Type-check, build, and run the test suites for the API and UI to verify the
repo is in a good state.

## Usage
`/build-and-test`

## Steps

1. **API setup** (skip any step already satisfied):
   - If `.venv/` doesn't exist at the repo root, create it: `python -m venv .venv`.
   - Install dependencies: `.venv/Scripts/pip install -r api/requirements.txt`.

2. **Run API tests**:
   ```
   cd api && ../.venv/Scripts/python.exe -m pytest
   ```

3. **UI setup** (skip if already satisfied):
   - If `ui/node_modules/` doesn't exist, run `npm install` in `ui/`.

4. **Type-check the UI**:
   ```
   cd ui && npm run check
   ```

5. **Run UI tests**:
   ```
   cd ui && npm run test
   ```

6. **Build the UI** (production bundle):
   ```
   cd ui && npm run build
   ```

7. Report results:
   - Summarize pass/fail for each step (pytest, `npm run check`, `npm run test`, `npm run build`).
   - If anything fails, show the relevant error output and stop — do not
     proceed to later steps if an earlier one fails, unless the user asks
     otherwise.

## Notes
- This is the same set of checks expected in [CLAUDE.md](../../CLAUDE.md)
  before any change is considered done; use this command to run them all in
  one pass.
- The API test suite doesn't require real Azure credentials — `api/.env` can
  be absent or use placeholder values for the tests that are mocked.
