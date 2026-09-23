# Troubleshooting

🇬🇧 English · [🇭🇺 Magyar](Troubleshooting.hu.md)

## The tool

- **`http://localhost:8000` shows nothing** — build the frontend first: `cd frontend && npm run
  build`, then restart the backend. The backend serves `frontend/dist`.
- **"Build failed: Missing credentials"** — the AI builder needs a provider key. Set one and pick a
  matching model — see [Providers](Providers.md).
- **"Model output invalid"** — the LLM returned something that is not a valid n8n workflow. Try
  again, or use a stronger model.
- **A pasted workflow is rejected** — it must be a JSON object with a non-empty `nodes` array and a
  `connections` object.

## n8n

- **A node is red after import** — usually a missing credential. Open the node, pick the credential
  in its **Credential for …** dropdown; create it first if needed (see [n8n setup](n8n-Setup.md)).
- **"Credential not found"** — the imported workflow references a credential by name that does not
  exist in your n8n yet. Create it and attach it to the node.
- **Gmail/Google won't connect (self-hosted)** — you need Google OAuth client credentials and the
  correct redirect URL; n8n shows the redirect URL to register in Google Cloud Console.
- **Trigger doesn't fire** — make sure the workflow is **Active** (top-right toggle) for
  schedule/webhook/form triggers.
- **Wrong recipient/values** — some fields are not company-data placeholders; open the node and set
  them by hand.

Still stuck? Check the workflow's execution log in n8n (each run shows per-node input/output and the
exact error).
