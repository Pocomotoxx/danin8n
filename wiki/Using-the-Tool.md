# Using the tool

🇬🇧 English · [🇭🇺 Magyar](Using-the-Tool.hu.md)

The interface has three columns: **left** (build/import/company data), **center** (the workflow
graph), **right** (data intake and the ready workflow).

## 1. Start a workflow — three ways

- **Build with AI** (top-left): type what the workflow should do, e.g. *"watch a Gmail label,
  summarize new mail, post to Telegram"*, then **Send**. The AI creates it and draws the graph.
  Keep sending instructions to refine it (*"add a filter step first"*). Needs a provider key
  ([Providers](Providers.md)). `Ctrl/⌘+Enter` sends.
- **Templates**: choose one of 10 ready workflows from the **Start from a template** dropdown.
- **Paste**: paste any n8n workflow JSON and press **Inspect**.

## 2. Add company data

After a workflow is loaded, the **Company data** form appears with the fields it detected
(`[[field]]` placeholders — e.g. `company_name`, `website`, `from_email`). Fill them in.

`[[ai: …]]` spots (marketing copy, subjects) are written by the LLM when you tick **Fill with an
LLM** and set a model.

## 3. Generate

Click **Generate workflow**. The tool fills the fields, writes the AI text, keeps n8n's own
`{{ $json… }}` expressions untouched, and shows the finished JSON on the right.

## 4. Data-intake template

Click **📋 Data-intake template**. You get a checklist of everything the workflow needs:

- **Credentials to create in n8n** (API keys, passwords) — with 🔒 marking secrets.
- **Company/config fields** and **AI-written fields**.

Download the **`.env`** template and the **checklist.md**, or copy them. Secrets are never stored
here — they go into n8n (see [n8n setup](n8n-Setup.md)).

## 5. Export

In **3 · Ready workflow**, use **⬇ .json** to download the workflow (or **Copy JSON**). Import it
into n8n — see [n8n setup](n8n-Setup.md).
