# Hibaelhárítás

[🇬🇧 English](Troubleshooting.md) · 🇭🇺 Magyar

## Az eszköz

- **A `http://localhost:8000` üres** — előbb építsd fel a frontendet: `cd frontend && npm run
  build`, majd indítsd újra a backendet. A backend a `frontend/dist` mappát szolgálja ki.
- **„Build failed: Missing credentials"** — az AI-buildernek provider-kulcs kell. Állíts be egyet,
  és válassz hozzá illő modellt — lásd [Providerek](Providers.hu.md).
- **„Model output invalid"** — az LLM nem érvényes n8n-workflow-t adott vissza. Próbáld újra, vagy
  használj erősebb modellt.
- **A beillesztett workflow-t elutasítja** — JSON-objektum kell, nem üres `nodes` tömbbel és egy
  `connections` objektummal.

## n8n

- **Egy node piros az import után** — általában hiányzó credential. Nyisd meg a node-ot, válaszd ki
  a credentialt a **Credential for …** legördülőben; ha kell, előbb hozd létre (lásd
  [n8n beállítás](n8n-Setup.hu.md)).
- **„Credential not found"** — az importált workflow egy név szerinti credentialra hivatkozik, ami
  még nincs meg az n8n-edben. Hozd létre, és rendeld a node-hoz.
- **A Gmail/Google nem kapcsolódik (saját szerver)** — Google OAuth-client credential kell és a
  helyes redirect URL; az n8n megmutatja a Google Cloud Console-ban regisztrálandó redirect URL-t.
- **A trigger nem indul** — az ütemezés/webhook/űrlap triggerekhez a workflow legyen **Active** (a
  jobb felső kapcsoló).
- **Rossz címzett/értékek** — néhány mező nem cégadat-placeholder; nyisd meg a node-ot, és állítsd be
  kézzel.

Még mindig elakadtál? Nézd meg a workflow futási naplóját az n8n-ben (minden futás node-onként
mutatja a be- és kimenetet, és a pontos hibát).
