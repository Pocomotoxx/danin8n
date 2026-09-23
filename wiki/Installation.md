# Installation

🇬🇧 English · [🇭🇺 Magyar](Installation.hu.md)

## Requirements

- **Python 3.10+**
- **Node.js 18+** and **npm** (to build the web interface)

## Steps

1. **Get the code**

   ```bash
   git clone https://github.com/Pocomotoxx/danin8n.git
   cd danin8n
   ```

2. **Backend**

   ```bash
   python -m venv .venv
   . .venv/bin/activate            # Windows (PowerShell): .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Frontend (build once)**

   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Run**

   ```bash
   uvicorn backend.app:app --port 8000
   ```

   Open **http://localhost:8000**.

## Optional: AI features

The deterministic parts (templates, company-data fill, data-intake) work with no key. For **Build
with AI** and `[[ai: …]]` fields, set any [LiteLLM](https://docs.litellm.ai/) provider key — see
[Providers](Providers.md). Example:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Frontend development (optional)

To edit the interface with hot reload, run the backend on `:8000` and the Vite dev server separately:

```bash
cd frontend && npm run dev        # http://localhost:5173, proxies /api to :8000
```
