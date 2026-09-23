# Az eszköz használata

[🇬🇧 English](Using-the-Tool.md) · 🇭🇺 Magyar

A felület három oszlopból áll: **bal** (építés/import/cégadatok), **közép** (a workflow gráfja),
**jobb** (adatbekérő és a kész workflow).

## 1. Workflow indítása — háromféleképp

- **Build with AI** (bal felül): írd le, mit csináljon a workflow, például *„figyeljen egy Gmail-
  címkét, foglalja össze az új leveleket, és küldje Telegramra"*, majd **Send**. Az AI megépíti, és
  kirajzolja a gráfot. Küldj további utasításokat a finomításhoz (*„tegyél elé egy szűrőt"*).
  Provider-kulcs kell hozzá ([Providerek](Providers.hu.md)). Küldés: `Ctrl/⌘+Enter`.
- **Sablonok**: válassz egyet a 10 kész workflow közül a **Start from a template** legördülőben.
- **Beillesztés**: illessz be bármilyen n8n workflow JSON-t, majd nyomd meg az **Inspect** gombot.

## 2. Cégadatok megadása

A workflow betöltése után megjelenik a **Company data** űrlap a felismert mezőkkel (`[[mező]]`
helyek — például `company_name`, `website`, `from_email`). Töltsd ki őket.

A `[[ai: …]]` helyeket (marketingszöveg, tárgysorok) az LLM írja meg, ha bepipálod a **Fill with an
LLM** opciót, és beállítasz egy modellt.

## 3. Generálás

Kattints a **Generate workflow** gombra. Az eszköz kitölti a mezőket, megírja az AI-szöveget, az
n8n saját `{{ $json… }}` kifejezéseit érintetlenül hagyja, és jobbra megjeleníti a kész JSON-t.

## 4. Adatbekérő sablon

Kattints a **📋 Data-intake template** gombra. Kapsz egy checklistet mindenről, amit a workflow
igényel:

- **Az n8n-ben létrehozandó credentialök** (API-kulcsok, jelszavak) — a titkokat 🔒 jelöli.
- **Cég-/config-mezők** és **AI által írt mezők**.

Töltsd le a **`.env`** sablont és a **checklist.md**-t, vagy másold ki őket. A titkok itt sosem
tárolódnak — az n8n-be kerülnek (lásd [n8n beállítás](n8n-Setup.hu.md)).

## 5. Export

A **3 · Ready workflow** résznél a **⬇ .json** gombbal letöltöd a workflow-t (vagy **Copy JSON**).
Importáld az n8n-be — lásd [n8n beállítás](n8n-Setup.hu.md).
