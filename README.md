# n8n Workflow Factory

🇬🇧 English · [🇭🇺 Magyar](README.hu.md)

A lean, single-user tool: **import an n8n workflow template, add your company data, and copy or
download a ready-to-import workflow for n8n.** No OpenAI SDK — the runtime is n8n; the optional AI
steps go through LiteLLM (any provider).

## What it does

1. **Build with AI** — describe a workflow in plain language and refine it over several turns; an
   LLM returns an updated, validated n8n workflow each time.
2. **Templates** — start from one of 10 curated n8n workflows.
3. **Customize** — fill company data into `[[field]]` placeholders; let an LLM write `[[ai: …]]`
   text; n8n's own `{{ $json… }}` expressions are preserved.
4. **Data intake** — generate a checklist and `.env` template of everything the workflow needs
   (API keys, e-mails, passwords, credentials), with secrets clearly flagged.
5. **Export** — copy or download the finished workflow as `.json` and import it into n8n.
6. **AG2 Studio** — also design agent teams and export a workflow to paste into
   [AG2 Studio](https://app.ag2.ai/) (a free, open-source path for learning multi-agent design).

## Documentation (bilingual)

Full step-by-step guides live in the [`wiki/`](wiki/) folder, in English and Hungarian:

- **[Home](wiki/Home.md)** · [Kezdőlap](wiki/Home.hu.md)
- **[Installation](wiki/Installation.md)** · [Telepítés](wiki/Installation.hu.md)
- **[Using the tool](wiki/Using-the-Tool.md)** · [Az eszköz használata](wiki/Using-the-Tool.hu.md)
- **[n8n setup, step by step](wiki/n8n-Setup.md)** · [n8n beállítás lépésről lépésre](wiki/n8n-Setup.hu.md)
- **[Providers (LLM keys)](wiki/Providers.md)** · [Providerek (LLM-kulcsok)](wiki/Providers.hu.md)
- **[Troubleshooting](wiki/Troubleshooting.md)** · [Hibaelhárítás](wiki/Troubleshooting.hu.md)

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
uvicorn backend.app:app --port 8000                    # open http://localhost:8000
```

For AI features, set any LiteLLM provider key (no OpenAI required), e.g.
`export ANTHROPIC_API_KEY=sk-ant-...` and use a model like `anthropic/claude-sonnet-4-20250514`.

## Security

Secrets are never stored: the tool deals in credential *names* and field names only. Real API keys
and passwords go into n8n's own credential store — never into this tool. See
[n8n setup](wiki/n8n-Setup.md).

## Test

```bash
pytest -q        # 21 offline tests, no provider calls
```
