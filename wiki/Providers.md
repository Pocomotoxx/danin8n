# Providers (LLM keys)

🇬🇧 English · [🇭🇺 Magyar](Providers.hu.md)

The AI features — **Build with AI** and `[[ai: …]]` fields — use [LiteLLM](https://docs.litellm.ai/),
so you can use **any** provider. No OpenAI account is required.

## Set a key

Set the provider's usual environment variable before starting the backend, then pick a matching
model name in the interface.

| Provider | Env var | Example model |
| --- | --- | --- |
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4-20250514` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4.1` |
| Google | `GEMINI_API_KEY` | `gemini/gemini-2.0-flash` |
| Groq | `GROQ_API_KEY` | `groq/llama-3.3-70b-versatile` |
| Local (Ollama) | — | `ollama/llama3` |

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn backend.app:app --port 8000
```

Then in the tool, set the **model** field (e.g. `anthropic/claude-sonnet-4-20250514`) and use
**Build with AI** or tick **Fill with an LLM**.

## No key?

Everything else works without a key: templates, filling company data into `[[field]]` placeholders,
the data-intake checklist, and export. Only `[[ai: …]]` text and the AI builder need a provider.

See the full model list at the [LiteLLM providers docs](https://docs.litellm.ai/docs/providers).
