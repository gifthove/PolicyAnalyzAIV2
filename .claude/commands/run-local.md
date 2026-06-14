# Run Local (API + UI)

Start the FastAPI backend and the React UI dev servers for local development.

## Usage
`/run-local`

## Steps

1. **API setup** (skip any step already satisfied):
   - If `.venv/` doesn't exist at the repo root, create it: `python -m venv .venv`.
   - Install dependencies: `.venv/Scripts/pip install -r api/requirements.txt`.
   - If `api/.env` doesn't exist, copy `api/.env.example` to `api/.env` and
     warn the user that the Ask/Upload features need Azure OpenAI/Search/
     Storage credentials filled in before they'll work — `/health` works
     regardless.

2. **Start the API** in the background (`run_in_background: true`):
   ```
   cd api && ../.venv/Scripts/uvicorn app.main:app --reload --port 8000
   ```

3. **UI setup** (skip any step already satisfied):
   - If `ui/node_modules/` doesn't exist, run `npm install` in `ui/`.
   - If `ui/.env` doesn't exist, copy `ui/.env.example` to `ui/.env`.

4. **Start the UI** in the background (`run_in_background: true`):
   ```
   cd ui && npm start
   ```

5. Report both URLs to the user:
   - API: `http://localhost:8000` (Swagger UI at `/docs`)
   - UI: whatever URL Parcel prints (typically `http://localhost:1234`)

## Notes
- Both processes run in the background — use TaskOutput/TaskStop (or ask the
  user) to check logs or stop them.
- If the API was just started with a fresh `.env` (no Azure credentials),
  the UI's "API: online" badge will still show online since `/health` has no
  external dependencies, but Ask/Upload calls will fail until credentials
  are set.
