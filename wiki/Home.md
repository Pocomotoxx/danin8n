# Wiki — n8n Workflow Factory

🇬🇧 English · [🇭🇺 Magyar](Home.hu.md)

Step-by-step guides for building an n8n workflow with this tool and setting it up in n8n.

## The big picture

```
[ This tool ]                         [ n8n ]
 pick/build a workflow      →  import the workflow JSON
 add company data           →  create the credentials from the checklist
 download .json + intake     →  activate and run
```

This tool prepares a workflow and a **data-intake checklist**; **n8n runs it**. Secrets (API keys,
passwords) live only in n8n, never in this tool.

## Pages

1. **[Installation](Installation.md)** — get the tool running.
2. **[Using the tool](Using-the-Tool.md)** — templates, Build with AI, customize, data intake.
3. **[n8n setup, step by step](n8n-Setup.md)** — import the workflow and create the credentials.
4. **[Providers](Providers.md)** — set an LLM key for the AI features (any provider).
5. **[AG2 Studio](AG2-Studio.md)** — design agent teams and export them to app.ag2.ai (free path).
6. **[Troubleshooting](Troubleshooting.md)** — common problems.

## Typical flow

1. Open the tool (`http://localhost:8000`).
2. Pick a template or describe a workflow with **Build with AI**.
3. Add your **company data** and generate the workflow.
4. Click **📋 Data-intake template** and download the checklist + `.env`.
5. Download the workflow **`.json`**.
6. Follow **[n8n setup](n8n-Setup.md)**: import the JSON, create the credentials from the checklist,
   activate.
