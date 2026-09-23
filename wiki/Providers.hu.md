# Providerek (LLM-kulcsok)

[🇬🇧 English](Providers.md) · 🇭🇺 Magyar

Az AI-funkciók — a **Build with AI** és a `[[ai: …]]` mezők — a [LiteLLM](https://docs.litellm.ai/)
réteget használják, így **bármely** providert használhatsz. OpenAI-fiók nem kell.

## Kulcs beállítása

A backend indítása előtt állítsd be a provider szokásos környezeti változóját, majd a felületen
válassz hozzá illő modellnevet.

| Provider | Környezeti változó | Példamodell |
| --- | --- | --- |
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4-20250514` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4.1` |
| Google | `GEMINI_API_KEY` | `gemini/gemini-2.0-flash` |
| Groq | `GROQ_API_KEY` | `groq/llama-3.3-70b-versatile` |
| Helyi (Ollama) | — | `ollama/llama3` |

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn backend.app:app --port 8000
```

Ezután az eszközben állítsd be a **model** mezőt (például `anthropic/claude-sonnet-4-20250514`), és
használd a **Build with AI**-t, vagy pipáld be a **Fill with an LLM** opciót.

## Nincs kulcsod?

Minden más kulcs nélkül működik: a sablonok, a cégadatok betöltése a `[[mező]]` helyekre, az
adatbekérő checklist és az export. Csak a `[[ai: …]]` szöveg és az AI-builder igényel providert.

A teljes modell-listát a [LiteLLM providers dokumentáció](https://docs.litellm.ai/docs/providers)
tartalmazza.
