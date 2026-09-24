# AG2 Studio (ingyenes tanulópálya)

[🇬🇧 English](AG2-Studio.md) · 🇭🇺 Magyar

Az n8n mellett az eszköz **AG2 agent-csapatokat** is tervez, és olyan workflow-t exportál, amit az
**[AG2 Studióba](https://app.ag2.ai/)** illesztesz be. Az AG2 ingyenes, nyílt forrású multi-agent
keretrendszer — jó hely megtanulni, hogyan működnek az AI-agentek, mielőtt átlépnél n8n-re (ami két
felhasználó fölött fizetős).

## Tervezés → beillesztés, ugyanúgy, mint az n8n-nél

1. Az eszközben nyisd meg a **🤖 AG2 Studio agentek** panelt (a bal oszlop alján).
2. Adj meg egy **workflow-nevet** és egy **modellt** (pl. `gpt-4o`, vagy egy ingyenes/helyi).
3. Vedd fel az agenteket — mindegyiknek van **neve** és **system message-e** (mit csinál). További
   agenthez a **+ agent** gomb.
4. Kattints az **AG2 workflow generálása** gombra. A JSON jobbra megjelenik.
5. **Másold** vagy **⬇ töltsd le** a JSON-t.

## Importálás az AG2 Studióba

1. Jelentkezz be a **https://app.ag2.ai/** oldalon.
2. A workflow/build részben **importáld** a JSON-t (vagy illeszd be).
3. Állítsd be a modell **API-kulcsát** az AG2 Studióban (az eszköz sosem tárol kulcsot). Az AG2-höz
   kell egy LLM a futtatáshoz; ez lehet ingyenes/helyi modell is.
4. Futtasd és finomítsd.

## Mit kapsz

- **Egy agent** → `twoagents` workflow (egy user proxy beszélget egy assistanttal).
- **Két vagy több agent** → `groupchat` workflow (egy manager koordinálja az assistanteket).

Minden agent **system message-e** lesz az utasítása; a **modell** minden agent `llm_config`-jába
bekerül. Ez az AG2 Studio / ag2studio workflow-sémájához illeszkedik.

## Miért érdemes itt kezdeni

Az AG2 ingyenes és nyílt forrású, így ideális a multi-agent tervezés ingyenes tanulására. Ha
belejöttél, ugyanez az elv (tervezés → export → import) érvényes az n8n-re is az éles
automatizálásokhoz.
