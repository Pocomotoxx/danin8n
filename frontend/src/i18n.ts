// Minimal i18n: a string table + a t() helper with {var} interpolation. No dependencies.

export type Lang = "en" | "hu";

type Entry = { en: string; hu: string };

export const STRINGS: Record<string, Entry> = {
  subtitle: {
    en: "import a template → add company data → copy a ready workflow",
    hu: "sablon behúzása → cégadatok megadása → kész workflow kimásolása",
  },
  buildTitle: { en: "🛠 Build with AI", hu: "🛠 Építés AI-val" },
  buildPh: {
    en: "Describe or change the workflow, e.g. 'watch a Gmail label, summarize new mail, post to Telegram'",
    hu: "Írd le vagy módosítsd a workflow-t, pl. „figyeljen egy Gmail-címkét, foglalja össze az új leveleket, küldje Telegramra”",
  },
  model: { en: "model", hu: "modell" },
  sendUpdate: { en: "Send (update workflow)", hu: "Küldés (workflow frissítése)" },
  sendCreate: { en: "Send (create workflow)", hu: "Küldés (workflow létrehozása)" },
  sendHint: {
    en: "Ctrl/⌘+Enter to send. Needs a provider key (any LiteLLM model).",
    hu: "Küldés: Ctrl/⌘+Enter. Provider-kulcs kell hozzá (bármely LiteLLM-modell).",
  },
  importTitle: { en: "1 · Import n8n workflow", hu: "1 · n8n workflow behúzása" },
  tplLabel: { en: "Start from a template", hu: "Indulj egy sablonból" },
  tplChoose: { en: "— choose a template ({n}) —", hu: "— válassz sablont ({n}) —" },
  pastePh: { en: "…or paste an n8n workflow JSON here", hu: "…vagy illessz be ide egy n8n workflow JSON-t" },
  loadSample: { en: "Load sample", hu: "Minta betöltése" },
  inspect: { en: "Inspect", hu: "Vizsgálat" },
  companyTitle: { en: "2 · Company data", hu: "2 · Cégadatok" },
  aiTitle: { en: "AI-written fields", hu: "AI által írt mezők" },
  fillLlm: { en: "Fill with an LLM", hu: "Kitöltés LLM-mel" },
  credsSetup: { en: "Credentials to set up in n8n: {list}", hu: "Az n8n-ben beállítandó credentialök: {list}" },
  generate: { en: "Generate workflow", hu: "Workflow generálása" },
  intakeBtn: { en: "📋 Data-intake template", hu: "📋 Adatbekérő sablon" },
  intakeTitle: { en: "📋 Data intake", hu: "📋 Adatbekérő" },
  intakeHint: {
    en: "Fill these before running. 🔒 secrets go into n8n's credential store — never here.",
    hu: "Ezeket töltsd ki futtatás előtt. 🔒 a titkok az n8n credential-tárába mennek — sosem ide.",
  },
  dlEnv: { en: "⬇ .env", hu: "⬇ .env" },
  dlChecklist: { en: "⬇ checklist.md", hu: "⬇ checklist.md" },
  copyEnv: { en: "Copy .env", hu: ".env másolása" },
  copyChecklist: { en: "Copy checklist", hu: "Checklist másolása" },
  readyTitle: { en: "3 · Ready workflow", hu: "3 · Kész workflow" },
  dlJson: { en: "⬇ .json", hu: "⬇ .json" },
  copyJson: { en: "Copy JSON", hu: "JSON másolása" },
  unresolved: { en: "Unresolved: {list}", hu: "Kitöltetlen: {list}" },
  setupN8n: { en: "Set up in n8n: {list}", hu: "Állítsd be az n8n-ben: {list}" },
  rightPlaceholder: {
    en: "Inspect a workflow, add company data, then Generate to get a workflow you can paste into n8n.",
    hu: "Vizsgálj meg egy workflow-t, add meg a cégadatokat, majd a Generálással kész workflow-t kapsz, amit az n8n-be illeszthetsz.",
  },
  // Status messages
  stLoaded: { en: 'Loaded "{name}" — {n} nodes.', hu: '„{name}” betöltve — {n} node.' },
  stGenerated: { en: "Generated. {n} AI field(s) filled.", hu: "Generálva. {n} AI-mező kitöltve." },
  stInvalidJson: { en: "Invalid workflow JSON: {e}", hu: "Érvénytelen workflow JSON: {e}" },
  stAiUpdated: { en: "Workflow updated by AI.", hu: "A workflow-t frissítette az AI." },
  stCopied: { en: "Copied {label}.", hu: "{label} kimásolva." },
  stDownloaded: { en: "Downloaded {file}.", hu: "{file} letöltve." },
  stIntake: { en: "Data-intake template generated.", hu: "Adatbekérő sablon elkészült." },
  stAiDefault: { en: "Updated the workflow.", hu: "A workflow frissült." },
  lblEnvTemplate: { en: ".env template", hu: ".env sablon" },
  lblChecklist: { en: "checklist", hu: "checklist" },
  previewBtn: { en: "▶ Preview (sandbox)", hu: "▶ Előnézet (sandbox)" },
  previewTitle: { en: "▶ Dry-run preview", hu: "▶ Száraz előnézet" },
  previewHint: {
    en: "What the workflow would do, step by step. Nothing is executed — side-effect steps are only simulated.",
    hu: "Mit csinálna a workflow, lépésről lépésre. Semmi nem fut le — a kifelé ható lépések csak szimuláltak.",
  },
  stPreview: { en: "Preview generated ({n} steps).", hu: "Előnézet kész ({n} lépés)." },
  effTrigger: { en: "trigger", hu: "indító" },
  effTransform: { en: "transform", hu: "átalakítás" },
  effExternal: { en: "external call", hu: "külső hívás" },
  "effSide-effect": { en: "sends/writes", hu: "küld/ír" },
  effAi: { en: "AI", hu: "AI" },
  effRead: { en: "reads", hu: "olvas" },
  ag2Title: { en: "🤖 AG2 Studio agents", hu: "🤖 AG2 Studio agentek" },
  ag2Name: { en: "Workflow name", hu: "Workflow neve" },
  ag2AddAgent: { en: "+ add agent", hu: "+ agent" },
  ag2AgentName: { en: "agent name", hu: "agent neve" },
  ag2SystemMsg: { en: "system message (what this agent does)", hu: "system message (mit csinál ez az agent)" },
  ag2Generate: { en: "Generate AG2 workflow", hu: "AG2 workflow generálása" },
  ag2ResultTitle: { en: "🤖 AG2 Studio workflow", hu: "🤖 AG2 Studio workflow" },
  ag2Hint: {
    en: "Copy or download this JSON and import it in the AG2 Studio (app.ag2.ai). Set your model's API key there.",
    hu: "Másold vagy töltsd le ezt a JSON-t, és importáld az AG2 Studióba (app.ag2.ai). A modell API-kulcsát ott állítsd be.",
  },
  ag2Remove: { en: "remove", hu: "törlés" },
  stAg2: { en: "AG2 workflow generated ({type}).", hu: "AG2 workflow kész ({type})." },
};

export function t(lang: Lang, key: keyof typeof STRINGS, vars?: Record<string, string | number>): string {
  let s = STRINGS[key]?.[lang] ?? STRINGS[key]?.en ?? String(key);
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.split(`{${k}}`).join(String(v));
  return s;
}

export function initialLang(): Lang {
  try {
    const saved = localStorage.getItem("lang");
    if (saved === "en" || saved === "hu") return saved;
    if (navigator.language?.toLowerCase().startsWith("hu")) return "hu";
  } catch {
    /* ignore */
  }
  return "en";
}

export function persistLang(lang: Lang): void {
  try {
    localStorage.setItem("lang", lang);
  } catch {
    /* ignore */
  }
}
