# n8n Workflow Factory

[🇬🇧 English](README.md) · 🇭🇺 Magyar

Karcsú, egyszemélyes eszköz: **behúzol egy n8n workflow-sablont, megadod a cégadatokat, majd
kimásolod vagy letöltöd a kész, n8n-be importálható workflow-t.** OpenAI SDK nélkül — a futtatómotor
az n8n; a választható AI-lépések a LiteLLM-en át bármely providert elérnek.

## Mit tud

1. **Build with AI** — hétköznapi nyelven leírod a workflow-t, és több körben finomítod; az LLM
   minden körben egy frissített, ellenőrzött n8n-workflow-t ad vissza.
2. **Sablonok** — 10 kész n8n-workflow közül indulhatsz.
3. **Testreszabás** — a cégadatokat a `[[mező]]` helyekre tölti; a `[[ai: …]]` szövegeket egy LLM
   írja meg; az n8n saját `{{ $json… }}` kifejezései érintetlenek maradnak.
4. **Adatbekérő** — checklistet és `.env` sablont készít mindenről, amit a workflow igényel
   (API-kulcsok, e-mailek, jelszavak, credentialök), a titkokat jól láthatóan megjelölve.
5. **Export** — a kész workflow-t `.json`-ként kimásolod vagy letöltöd, és importálod az n8n-be.

## Dokumentáció (kétnyelvű)

A részletes, lépésről lépésre útmutatók a [`wiki/`](wiki/) mappában vannak, angolul és magyarul:

- **[Kezdőlap](wiki/Home.hu.md)** · [Home](wiki/Home.md)
- **[Telepítés](wiki/Installation.hu.md)** · [Installation](wiki/Installation.md)
- **[Az eszköz használata](wiki/Using-the-Tool.hu.md)** · [Using the tool](wiki/Using-the-Tool.md)
- **[n8n beállítás lépésről lépésre](wiki/n8n-Setup.hu.md)** · [n8n setup](wiki/n8n-Setup.md)
- **[Providerek (LLM-kulcsok)](wiki/Providers.hu.md)** · [Providers](wiki/Providers.md)
- **[Hibaelhárítás](wiki/Troubleshooting.hu.md)** · [Troubleshooting](wiki/Troubleshooting.md)

## Gyors kezdés

```bash
python -m venv .venv && . .venv/bin/activate          # Windowson: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
uvicorn backend.app:app --port 8000                    # nyisd meg: http://localhost:8000
```

Az AI-funkciókhoz állíts be egy tetszőleges LiteLLM-provider kulcsot (OpenAI nem kell), például
`export ANTHROPIC_API_KEY=sk-ant-...`, és használj egy modellt, mint az
`anthropic/claude-sonnet-4-20250514`.

## Biztonság

A titkok sosem tárolódnak: az eszköz csak a credential- és mezőneveket kezeli. A valódi API-kulcsok
és jelszavak az n8n saját credential-tárába kerülnek — sosem ebbe az eszközbe. Lásd az
[n8n beállítás](wiki/n8n-Setup.hu.md) oldalt.

## Teszt

```bash
pytest -q        # 21 offline teszt, provider-hívás nélkül
```
