# n8n setup, step by step

🇬🇧 English · [🇭🇺 Magyar](n8n-Setup.hu.md)

You have a workflow `.json` and a data-intake checklist from the tool. Here is exactly what to do in
n8n.

## 0. Get an n8n instance

Use **any** of these:

- **n8n Cloud** — sign up at [n8n.io](https://n8n.io) (easiest, nothing to install).
- **Desktop / self-hosted** — run locally:
  ```bash
  npx n8n
  ```
  then open `http://localhost:5678`.

## 1. Import the workflow

1. In n8n, open the **Workflows** list.
2. Click the **⋮ (three dots) → Import from File** (top-right of a new workflow canvas), or
   **Import from URL**.
3. Choose the `.json` you downloaded from the tool.
4. The workflow appears on the canvas with all its nodes.

> Tip: you can also open a blank workflow, press the **⋮** menu → **Import from File**.

## 2. Create the credentials

Open the **checklist** you downloaded. Each item under *"Credentials to create in n8n"* is one
credential to add. For every item:

1. Go to **Credentials** (left sidebar) → **Add credential** (or **New**).
2. Search for the credential **type** from the checklist, e.g.:
   - `gmailOAuth2` → **Gmail OAuth2 API**
   - `openAiApi` → **OpenAI API** (or the provider you use)
   - `anthropicApi` → **Anthropic API**
   - `openWeatherMapApi` → **OpenWeatherMap API**
   - `smtp` → **SMTP**
   - `telegramApi` → **Telegram API**
   - `googleSheetsOAuth2Api` / `googleCalendarOAuth2Api` → the matching Google credential
3. Fill the fields the checklist lists. **🔒 fields are secret** (API keys, passwords, client
   secrets) — paste your real values here, in n8n. OAuth credentials (Gmail, Google) walk you
   through a **Connect / Sign in** button.
4. Save the credential.

## 3. Attach credentials to nodes

1. Double-click a node that needs a credential (the checklist names the node).
2. In the node's **Credential for …** dropdown, select the credential you just created.
3. Repeat for each node listed in the checklist.

## 4. Fill in the remaining values

If your workflow still has non-secret values to set (recipient e-mail, a spreadsheet id, a
schedule), open each node and set them. The company-data fields you filled in the tool are already
substituted; anything left is highlighted in the checklist under *"Company / config data"*.

## 5. Test

1. Click **Execute Workflow** (or **Test step** on a single node) to run it once.
2. Check each node turns green. Red nodes show an error — usually a missing credential or an empty
   required field. Fix and re-run.

## 6. Activate

For workflows with a trigger (schedule, webhook, form), toggle **Active** (top-right) so n8n runs it
automatically. Manual workflows are run with **Execute Workflow**.

## Common credential notes

- **Gmail / Google** — need OAuth: click **Connect my account** and sign in; for self-hosted n8n you
  may need to set up Google OAuth client credentials first (n8n shows the redirect URL to use).
- **SMTP** — host, port, user, and password of your mail provider.
- **OpenAI / Anthropic / OpenWeatherMap / Telegram** — a single API key/token from that service.

See [Troubleshooting](Troubleshooting.md) if a node stays red.
