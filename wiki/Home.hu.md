# Wiki — n8n Workflow Factory

[🇬🇧 English](Home.md) · 🇭🇺 Magyar

Lépésről lépésre útmutatók: hogyan építs n8n-workflow-t ezzel az eszközzel, és hogyan állítsd be az
n8n-ben.

## A nagy kép

```
[ Ez az eszköz ]                       [ n8n ]
 workflow választása/építése   →  a workflow JSON importálása
 cégadatok megadása            →  a credentialök létrehozása a checklist alapján
 .json + adatbekérő letöltése   →  aktiválás és futtatás
```

Az eszköz előkészíti a workflow-t és egy **adatbekérő checklistet**; **az n8n futtatja**. A titkok
(API-kulcsok, jelszavak) csak az n8n-ben élnek, sosem ebben az eszközben.

## Oldalak

1. **[Telepítés](Installation.hu.md)** — az eszköz elindítása.
2. **[Az eszköz használata](Using-the-Tool.hu.md)** — sablonok, Build with AI, testreszabás, adatbekérő.
3. **[n8n beállítás lépésről lépésre](n8n-Setup.hu.md)** — a workflow importálása és a credentialök létrehozása.
4. **[Providerek](Providers.hu.md)** — LLM-kulcs beállítása az AI-funkciókhoz (bármely provider).
5. **[AG2 Studio](AG2-Studio.hu.md)** — agent-csapatok tervezése és exportja az app.ag2.ai-ra (ingyenes út).
6. **[Hibaelhárítás](Troubleshooting.hu.md)** — gyakori problémák.

## Tipikus folyamat

1. Nyisd meg az eszközt (`http://localhost:8000`).
2. Válassz sablont, vagy írd le a workflow-t a **Build with AI** mezőben.
3. Add meg a **cégadatokat**, és generáld a workflow-t.
4. Kattints a **📋 Data-intake template** gombra, és töltsd le a checklistet + a `.env`-et.
5. Töltsd le a workflow **`.json`**-t.
6. Kövesd az **[n8n beállítás](n8n-Setup.hu.md)** oldalt: importáld a JSON-t, hozd létre a
   credentialöket a checklist alapján, aktiváld.
