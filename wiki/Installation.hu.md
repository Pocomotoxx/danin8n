# Telepítés

[🇬🇧 English](Installation.md) · 🇭🇺 Magyar

## Követelmények

- **Python 3.10+**
- **Node.js 18+** és **npm** (a webes felület felépítéséhez)

## Lépések

1. **Töltsd le a kódot**

   ```bash
   git clone https://github.com/Pocomotoxx/danin8n.git
   cd danin8n
   ```

2. **Backend**

   ```bash
   python -m venv .venv
   . .venv/bin/activate            # Windowson (PowerShell): .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Frontend (egyszer felépíted)**

   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Indítás**

   ```bash
   uvicorn backend.app:app --port 8000
   ```

   Nyisd meg: **http://localhost:8000**.

## Választható: AI-funkciók

A determinisztikus részek (sablonok, cégadat-kitöltés, adatbekérő) kulcs nélkül működnek. A **Build
with AI** módhoz és a `[[ai: …]]` mezőkhöz állíts be egy tetszőleges [LiteLLM](https://docs.litellm.ai/)
provider-kulcsot — lásd a [Providerek](Providers.hu.md) oldalt. Például:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Frontend-fejlesztés (választható)

A felület azonnali újratöltéssel való szerkesztéséhez futtasd a backendet a `:8000` porton, a Vite
fejlesztői szervert pedig külön:

```bash
cd frontend && npm run dev        # http://localhost:5173, a /api hívásokat a :8000-ra irányítja
```
