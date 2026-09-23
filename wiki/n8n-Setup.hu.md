# n8n beállítás lépésről lépésre

[🇬🇧 English](n8n-Setup.md) · 🇭🇺 Magyar

Van egy workflow `.json`-od és egy adatbekérő checklisted az eszközből. Íme pontosan, mit tegyél az
n8n-ben.

## 0. Legyen egy n8n példányod

Bármelyik jó:

- **n8n Cloud** — regisztrálj az [n8n.io](https://n8n.io) oldalon (a legegyszerűbb, semmit nem kell
  telepíteni).
- **Desktop / saját szerver** — helyben futtatod:
  ```bash
  npx n8n
  ```
  majd nyisd meg: `http://localhost:5678`.

## 1. A workflow importálása

1. Az n8n-ben nyisd meg a **Workflows** listát.
2. Kattints a **⋮ (három pont) → Import from File** menüre (egy új workflow-vászon jobb felső
   sarkában), vagy az **Import from URL** opcióra.
3. Válaszd ki az eszközből letöltött `.json`-t.
4. A workflow megjelenik a vásznon az összes node-jával.

> Tipp: nyithatsz egy üres workflow-t is, majd a **⋮** menü → **Import from File**.

## 2. A credentialök létrehozása

Nyisd meg a letöltött **checklistet**. A *„Credentials to create in n8n"* alatti minden tétel egy
hozzáadandó credential. Minden tételnél:

1. Menj a **Credentials** menübe (bal oldalsáv) → **Add credential** (vagy **New**).
2. Keresd meg a credential **típusát** a checklistből, például:
   - `gmailOAuth2` → **Gmail OAuth2 API**
   - `openAiApi` → **OpenAI API** (vagy amelyik providert használod)
   - `anthropicApi` → **Anthropic API**
   - `openWeatherMapApi` → **OpenWeatherMap API**
   - `smtp` → **SMTP**
   - `telegramApi` → **Telegram API**
   - `googleSheetsOAuth2Api` / `googleCalendarOAuth2Api` → a megfelelő Google-credential
3. Töltsd ki a checklistben felsorolt mezőket. **A 🔒 mezők titkosak** (API-kulcsok, jelszavak,
   client secretek) — a valódi értékeidet ide, az n8n-be írd be. Az OAuth-credentialök (Gmail,
   Google) egy **Connect / Sign in** gombbal végigvezetnek a bejelentkezésen.
4. Mentsd el a credentialt.

## 3. A credentialök hozzárendelése a node-okhoz

1. Kattints duplán egy credentialt igénylő node-ra (a checklist megnevezi a node-ot).
2. A node **Credential for …** legördülőjében válaszd ki az imént létrehozott credentialt.
3. Ismételd meg a checklistben felsorolt minden node-nál.

## 4. A maradék értékek kitöltése

Ha a workflow-ban maradt nem-titkos beállítás (címzett e-mail, egy táblázat azonosítója, ütemezés),
nyisd meg az adott node-ot, és állítsd be. Az eszközben megadott cégadatok már be vannak
helyettesítve; ami maradt, azt a checklist a *„Company / config data"* alatt kiemeli.

## 5. Tesztelés

1. Kattints az **Execute Workflow** gombra (vagy a **Test step**-re egyetlen node-nál), hogy egyszer
   lefusson.
2. Nézd meg, hogy minden node zöldre vált. A piros node hibát jelez — általában hiányzó credential
   vagy üres kötelező mező. Javítsd, és futtasd újra.

## 6. Aktiválás

A triggeres workflow-knál (ütemezés, webhook, űrlap) kapcsold be az **Active** kapcsolót (jobb
felül), így az n8n automatikusan futtatja. A kézi workflow-kat az **Execute Workflow** gombbal
indítod.

## Gyakori credential-tudnivalók

- **Gmail / Google** — OAuth kell: kattints a **Connect my account** gombra, és jelentkezz be; saját
  szerveres n8n-nél előbb be kell állítanod egy Google OAuth-client credentialt (az n8n megmutatja a
  használandó redirect URL-t).
- **SMTP** — a levelező szolgáltatód host, port, felhasználó és jelszó adatai.
- **OpenAI / Anthropic / OpenWeatherMap / Telegram** — egyetlen API-kulcs/token az adott
  szolgáltatástól.

Ha egy node piros marad, lásd a [Hibaelhárítás](Troubleshooting.hu.md) oldalt.
