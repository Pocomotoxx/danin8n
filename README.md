# n8n Workflow Factory

A lean tool for marketers: **import an n8n workflow template, add your company data, and copy a
ready-to-import workflow into n8n.** No OpenAI SDK — the runtime is n8n; the optional AI step goes
through LiteLLM (any provider).

## How it works

1. **Import** — paste an n8n workflow JSON (a template). Templates mark fillable spots with
   `[[field]]` (from company data) and `[[ai: instruction]]` (written by an LLM). These use double
   square brackets, so they never collide with n8n's own `{{ $json… }}` expressions.
2. **Add company data** — the tool auto-detects the `[[field]]` placeholders and shows a form.
3. **Generate** — field placeholders are filled deterministically; `[[ai:…]]` placeholders are
   written by an LLM using the company as context (optional — needs a provider key). n8n expressions
   are preserved untouched.
4. **Copy** — copy the finished workflow JSON and paste it into n8n. The tool lists which
   **credentials** to set up there.

Secrets are never stored: real API keys live in n8n's own credential store. This tool only
references credential slots by name.

## Run it

```bash
# Backend
python -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Frontend (build once; the backend then serves it from the same origin)
cd frontend && npm install && npm run build && cd ..

uvicorn backend.app:app --port 8000                 # open http://localhost:8000
```

For AI-written fields, configure any LiteLLM provider (no OpenAI required), e.g.:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# then in the UI: tick "Fill with an LLM" and set the model, e.g. anthropic/claude-sonnet-4-20250514
```

Frontend dev with hot reload: `uvicorn ... --port 8000` in one terminal, `cd frontend && npm run dev`
in another (Vite proxies `/api` to the backend).

## Architecture

- `backend/n8n.py` — parse/validate an n8n workflow; find and substitute `[[…]]` placeholders.
- `backend/customize.py` — fill fields from the company profile; fill `[[ai:…]]` via an LLM; report
  what was filled, what is unresolved, and which credentials to set up.
- `backend/llm.py` — provider-agnostic LLM via LiteLLM (injectable; offline `EchoCompleter` for tests).
- `backend/app.py` — FastAPI: `/api/inspect`, `/api/customize`; serves the built SPA.
- `frontend/` — Vite + React + React Flow: import, company form, workflow graph, ready JSON.
- `samples/welcome_email.json` — an example template with both placeholder kinds.

## Test

```bash
pytest -q        # fully offline (no provider calls)
```
