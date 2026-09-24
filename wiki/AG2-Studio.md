# AG2 Studio (free learning path)

🇬🇧 English · [🇭🇺 Magyar](AG2-Studio.hu.md)

Besides n8n, the tool can design **AG2 agent teams** and export a workflow you paste into the
**[AG2 Studio](https://app.ag2.ai/)**. AG2 is a free, open-source multi-agent framework — a good place
to learn how AI agents work before moving to n8n (which is paid beyond two users).

## Design → paste, just like n8n

1. In the tool, open the **🤖 AG2 Studio agents** panel (bottom of the left column).
2. Set a **workflow name** and a **model** (e.g. `gpt-4o`, or a free/local one).
3. Add your agents — each has a **name** and a **system message** (what that agent does). Use
   **+ add agent** for more.
4. Click **Generate AG2 workflow**. The JSON appears on the right.
5. **Copy** or **⬇ download** the JSON.

## Import into AG2 Studio

1. Sign in at **https://app.ag2.ai/**.
2. Go to the workflows/build area and **import** the JSON (or paste it).
3. Set your model's **API key** in AG2 Studio (the tool never stores keys). AG2 needs an LLM to run;
   it can use a free/local model.
4. Run and iterate.

## What you get

- **One agent** → a `twoagents` workflow (a user proxy talks to one assistant).
- **Two or more agents** → a `groupchat` workflow (a manager coordinates the assistants).

Each agent's **system message** becomes its instructions; the **model** is set in every agent's
`llm_config`. This matches the AG2 Studio / ag2studio workflow schema.

## Why start here

AG2 is free and open-source, so it is ideal for learning multi-agent design at no cost. Once you are
comfortable, the same idea (design → export → import) applies to n8n for production automations.
