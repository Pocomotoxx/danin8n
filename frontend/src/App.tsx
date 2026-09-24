import { useEffect, useMemo, useState } from "react";
import { Background, Controls, ReactFlow } from "@xyflow/react";

import {
  buildWorkflow,
  customize,
  generateAg2,
  getIntake,
  getTemplate,
  inspect,
  listTemplates,
  simulate,
  type Ag2AgentInput,
  type CustomizeResult,
  type Inspection,
  type N8nWorkflow,
  type SimStep,
  type TemplateMeta,
} from "./api";
import { initialLang, persistLang, t, type Lang } from "./i18n";
import { toGraph } from "./n8nGraph";

const SAMPLE = `{
  "name": "New lead welcome email",
  "nodes": [
    { "parameters": { "path": "new-lead" }, "name": "New Lead Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 1, "position": [240, 300] },
    { "parameters": { "values": { "string": [ { "name": "subject", "value": "[[ai: write a short friendly welcome email subject]]" }, { "name": "body", "value": "Hi {{ $json.name }},\\n[[ai: warm 2-sentence welcome]]\\nVisit [[website]].\\n— [[company_name]]" } ] } }, "name": "Compose Email", "type": "n8n-nodes-base.set", "typeVersion": 2, "position": [480, 300] },
    { "parameters": { "fromEmail": "[[from_email]]", "toEmail": "={{ $json.email }}" }, "name": "Send Email", "type": "n8n-nodes-base.emailSend", "typeVersion": 2, "position": [720, 300], "credentials": { "smtp": { "name": "Company SMTP" } } }
  ],
  "connections": {
    "New Lead Webhook": { "main": [[{ "node": "Compose Email", "type": "main", "index": 0 }]] },
    "Compose Email": { "main": [[{ "node": "Send Email", "type": "main", "index": 0 }]] }
  }
}`;

export default function App() {
  const [lang, setLang] = useState<Lang>(initialLang);
  const [raw, setRaw] = useState("");
  const [workflow, setWorkflow] = useState<N8nWorkflow | null>(null);
  const [insp, setInsp] = useState<Inspection | null>(null);
  const [profile, setProfile] = useState<Record<string, string>>({ name: "" });
  const [useLlm, setUseLlm] = useState(false);
  const [model, setModel] = useState("anthropic/claude-sonnet-4-20250514");
  const [result, setResult] = useState<CustomizeResult | null>(null);
  const [status, setStatus] = useState<{ kind: "ok" | "err" | "info"; msg: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [templates, setTemplates] = useState<TemplateMeta[]>([]);
  const [chat, setChat] = useState<{ role: "you" | "ai"; text: string }[]>([]);
  const [instruction, setInstruction] = useState("");
  const [buildModel, setBuildModel] = useState("anthropic/claude-sonnet-4-20250514");
  const [intake, setIntake] = useState<{ env: string; checklist: string } | null>(null);
  const [sim, setSim] = useState<SimStep[] | null>(null);
  const [ag2Name, setAg2Name] = useState("My Agent Team");
  const [ag2Model, setAg2Model] = useState("gpt-4o");
  const [ag2Agents, setAg2Agents] = useState<Ag2AgentInput[]>([
    { name: "assistant", system_message: "You are a helpful assistant." },
  ]);
  const [ag2Result, setAg2Result] = useState<Record<string, unknown> | null>(null);

  const tr = (key: Parameters<typeof t>[1], vars?: Record<string, string | number>) => t(lang, key, vars);
  const effKey = (e: string): Parameters<typeof t>[1] =>
    (({
      trigger: "effTrigger",
      transform: "effTransform",
      external: "effExternal",
      "side-effect": "effSide-effect",
      ai: "effAi",
      read: "effRead",
    } as Record<string, Parameters<typeof t>[1]>)[e] ?? "effTransform");
  const toggleLang = () => {
    const next: Lang = lang === "en" ? "hu" : "en";
    setLang(next);
    persistLang(next);
  };

  useEffect(() => {
    listTemplates()
      .then((r) => setTemplates(r.templates))
      .catch(() => undefined);
  }, []);

  const graph = useMemo(() => {
    const wf = result?.workflow ?? workflow;
    return wf ? toGraph(wf) : { nodes: [], edges: [] };
  }, [workflow, result]);

  const inspectWorkflow = async (wf: N8nWorkflow) => {
    setBusy(true);
    setResult(null);
    try {
      setWorkflow(wf);
      const info = await inspect(wf);
      setInsp(info);
      setProfile((p) => {
        const next: Record<string, string> = { ...p, name: p.name || "" };
        for (const f of info.placeholders.fields) if (!(f in next)) next[f] = "";
        return next;
      });
      setStatus({ kind: "ok", msg: tr("stLoaded", { name: info.name, n: info.node_count }) });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doInspect = () => {
    try {
      inspectWorkflow(JSON.parse(raw) as N8nWorkflow);
    } catch (e) {
      setStatus({ kind: "err", msg: tr("stInvalidJson", { e: String(e) }) });
    }
  };

  const loadTemplate = async (file: string) => {
    if (!file) return;
    setBusy(true);
    try {
      const { workflow: wf } = await getTemplate(file);
      setRaw(JSON.stringify(wf, null, 2));
      await inspectWorkflow(wf);
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
      setBusy(false);
    }
  };

  const doGenerate = async () => {
    if (!workflow) return;
    setBusy(true);
    try {
      const res = await customize(workflow, profile, useLlm, useLlm ? model : undefined);
      setResult(res);
      setStatus({ kind: "ok", msg: tr("stGenerated", { n: Object.keys(res.report.ai_filled).length }) });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const copyText = async (text: string, label: string) => {
    await navigator.clipboard.writeText(text);
    setStatus({ kind: "info", msg: tr("stCopied", { label }) });
  };

  const slug = () => {
    const name = result?.workflow.name ?? workflow?.name ?? "workflow";
    return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "workflow";
  };

  const download = (filename: string, text: string, type = "text/plain;charset=utf-8") => {
    const url = URL.createObjectURL(new Blob([text], { type }));
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    setStatus({ kind: "info", msg: tr("stDownloaded", { file: filename }) });
  };

  const doAg2 = async () => {
    setBusy(true);
    try {
      const res = await generateAg2(ag2Name, "", ag2Agents, ag2Model);
      setAg2Result(res.workflow);
      setStatus({ kind: "ok", msg: tr("stAg2", { type: res.type }) });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doSimulate = async () => {
    const wf = result?.workflow ?? workflow;
    if (!wf) return;
    setBusy(true);
    try {
      const res = await simulate(wf);
      setSim(res.steps);
      setStatus({ kind: "ok", msg: tr("stPreview", { n: res.steps.length }) });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doIntake = async () => {
    const wf = result?.workflow ?? workflow;
    if (!wf) return;
    setBusy(true);
    try {
      const res = await getIntake(wf);
      setIntake({ env: res.env, checklist: res.checklist });
      setStatus({ kind: "ok", msg: tr("stIntake") });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doBuild = async () => {
    const text = instruction.trim();
    if (!text) return;
    setBusy(true);
    setChat((c) => [...c, { role: "you", text }]);
    setInstruction("");
    try {
      const current = result?.workflow ?? workflow;
      const { workflow: built, notes } = await buildWorkflow(text, current, buildModel);
      setWorkflow(built);
      setResult({
        workflow: built,
        report: { workflow_name: built.name ?? "", fields_filled: {}, ai_filled: {}, unresolved: [], credentials_to_setup: [] },
      });
      setChat((c) => [...c, { role: "ai", text: notes || tr("stAiDefault") }]);
      setStatus({ kind: "ok", msg: tr("stAiUpdated") });
    } catch (e) {
      setChat((c) => [...c, { role: "ai", text: `⚠️ ${String(e)}` }]);
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <strong>n8n Workflow Factory</strong>
        <span className="sub">{tr("subtitle")}</span>
        <button className="lang" onClick={toggleLang} title="Language / Nyelv">
          {lang === "en" ? "🇭🇺 Magyar" : "🇬🇧 English"}
        </button>
        {status && <span className={`status ${status.kind}`}>{status.msg}</span>}
      </header>

      <div className="body">
        <aside className="panel left">
          <div className="section">{tr("buildTitle")}</div>
          {chat.length > 0 && (
            <div className="chat">
              {chat.map((m, i) => (
                <div key={i} className={`msg ${m.role}`}>{m.text}</div>
              ))}
            </div>
          )}
          <textarea
            className="chat-in"
            placeholder={tr("buildPh")}
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) doBuild();
            }}
          />
          <label>{tr("model")}
            <input value={buildModel} onChange={(e) => setBuildModel(e.target.value)} />
          </label>
          <button className="primary" disabled={busy || !instruction.trim()} onClick={doBuild}>
            {result || workflow ? tr("sendUpdate") : tr("sendCreate")}
          </button>
          <p className="hint">{tr("sendHint")}</p>

          <div className="section">{tr("importTitle")}</div>
          {templates.length > 0 && (
            <label>
              {tr("tplLabel")}
              <select defaultValue="" disabled={busy} onChange={(e) => loadTemplate(e.target.value)}>
                <option value="">{tr("tplChoose", { n: templates.length })}</option>
                {templates.map((t) => (
                  <option key={t.file} value={t.file}>
                    {t.name} · {t.nodes} nodes
                  </option>
                ))}
              </select>
            </label>
          )}
          <textarea
            className="json-in"
            placeholder={tr("pastePh")}
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
          />
          <div className="row">
            <button onClick={() => setRaw(SAMPLE)}>{tr("loadSample")}</button>
            <button disabled={busy || !raw.trim()} onClick={doInspect}>{tr("inspect")}</button>
          </div>

          {insp && (
            <>
              <div className="section">{tr("companyTitle")}</div>
              {Object.keys(profile).map((f) => (
                <label key={f}>
                  {f}
                  <input value={profile[f]} onChange={(e) => setProfile({ ...profile, [f]: e.target.value })} />
                </label>
              ))}

              {insp.placeholders.ai.length > 0 && (
                <>
                  <div className="section">{tr("aiTitle")}</div>
                  <ul className="ai-list">
                    {insp.placeholders.ai.map((a, i) => <li key={i}>{a}</li>)}
                  </ul>
                  <label className="check">
                    <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} />
                    {tr("fillLlm")}
                  </label>
                  {useLlm && (
                    <label>{tr("model")}
                      <input value={model} onChange={(e) => setModel(e.target.value)} />
                    </label>
                  )}
                </>
              )}

              {insp.credentials_needed.length > 0 && (
                <p className="hint">{tr("credsSetup", { list: insp.credentials_needed.join(", ") })}</p>
              )}

              <button className="primary" disabled={busy} onClick={doGenerate}>{tr("generate")}</button>
              <button disabled={busy} onClick={doIntake} style={{ width: "100%", marginTop: 8 }}>
                {tr("intakeBtn")}
              </button>
              <button disabled={busy} onClick={doSimulate} style={{ width: "100%", marginTop: 8 }}>
                {tr("previewBtn")}
              </button>
            </>
          )}

          <div className="section" style={{ marginTop: 18, borderTop: "1px solid #e2e8f0", paddingTop: 12 }}>
            {tr("ag2Title")}
          </div>
          <label>{tr("ag2Name")}
            <input value={ag2Name} onChange={(e) => setAg2Name(e.target.value)} />
          </label>
          <label>{tr("model")}
            <input value={ag2Model} onChange={(e) => setAg2Model(e.target.value)} />
          </label>
          {ag2Agents.map((a, i) => (
            <div key={i} className="card">
              <input
                placeholder={tr("ag2AgentName")}
                value={a.name}
                onChange={(e) => setAg2Agents(ag2Agents.map((x, j) => (j === i ? { ...x, name: e.target.value } : x)))}
              />
              <textarea
                placeholder={tr("ag2SystemMsg")}
                value={a.system_message}
                onChange={(e) => setAg2Agents(ag2Agents.map((x, j) => (j === i ? { ...x, system_message: e.target.value } : x)))}
              />
              {ag2Agents.length > 1 && (
                <button onClick={() => setAg2Agents(ag2Agents.filter((_, j) => j !== i))}>{tr("ag2Remove")}</button>
              )}
            </div>
          ))}
          <div className="row">
            <button onClick={() => setAg2Agents([...ag2Agents, { name: "", system_message: "" }])}>
              {tr("ag2AddAgent")}
            </button>
            <button className="primary" disabled={busy} onClick={doAg2} style={{ flex: 1 }}>
              {tr("ag2Generate")}
            </button>
          </div>
        </aside>

        <main className="canvas">
          <ReactFlow nodes={graph.nodes} edges={graph.edges} fitView>
            <Background />
            <Controls />
          </ReactFlow>
        </main>

        <aside className="panel right">
          {ag2Result && (
            <>
              <div className="section">
                {tr("ag2ResultTitle")}
                <span>
                  <button onClick={() => download("ag2-workflow.json", JSON.stringify(ag2Result, null, 2), "application/json")}>{tr("dlJson")}</button>{" "}
                  <button onClick={() => copyText(JSON.stringify(ag2Result, null, 2), "JSON")}>{tr("copyJson")}</button>
                </span>
              </div>
              <p className="hint">{tr("ag2Hint")}</p>
              <pre className="code" style={{ maxHeight: "45vh" }}>{JSON.stringify(ag2Result, null, 2)}</pre>
            </>
          )}
          {sim && (
            <>
              <div className="section">{tr("previewTitle")}</div>
              <p className="hint">{tr("previewHint")}</p>
              <ol className="sim">
                {sim.map((s) => (
                  <li key={s.order} className={`sim-step eff-${s.effect}`}>
                    <div className="sim-head">
                      <strong>{s.node}</strong>
                      <span className="badge">{tr(effKey(s.effect))}</span>
                    </div>
                    <div className="sim-action">{s.action}</div>
                    {s.note && <div className="sim-note">⚠️ {s.note}</div>}
                    {Object.keys(s.sample).length > 0 && (
                      <div className="sim-sample">{JSON.stringify(s.sample)}</div>
                    )}
                  </li>
                ))}
              </ol>
            </>
          )}
          {intake && (
            <>
              <div className="section">{tr("intakeTitle")}</div>
              <div className="files">
                <button onClick={() => download(`${slug()}.env`, intake.env)}>{tr("dlEnv")}</button>
                <button onClick={() => download(`${slug()}-checklist.md`, intake.checklist, "text/markdown;charset=utf-8")}>{tr("dlChecklist")}</button>
                <button onClick={() => copyText(intake.env, tr("lblEnvTemplate"))}>{tr("copyEnv")}</button>
                <button onClick={() => copyText(intake.checklist, tr("lblChecklist"))}>{tr("copyChecklist")}</button>
              </div>
              <p className="hint">{tr("intakeHint")}</p>
              <pre className="code" style={{ maxHeight: "40vh" }}>{intake.checklist}</pre>
            </>
          )}
          {result ? (
            <>
              <div className="section">
                {tr("readyTitle")}
                <span>
                  <button onClick={() => download(`${slug()}.json`, JSON.stringify(result.workflow, null, 2), "application/json")}>{tr("dlJson")}</button>{" "}
                  <button onClick={() => copyText(JSON.stringify(result.workflow, null, 2), "JSON")}>{tr("copyJson")}</button>
                </span>
              </div>
              {result.report.unresolved.length > 0 && (
                <p className="warn">{tr("unresolved", { list: result.report.unresolved.join(", ") })}</p>
              )}
              {result.report.credentials_to_setup.length > 0 && (
                <p className="hint">{tr("setupN8n", { list: result.report.credentials_to_setup.join(", ") })}</p>
              )}
              <pre className="code">{JSON.stringify(result.workflow, null, 2)}</pre>
            </>
          ) : (
            !intake && !sim && !ag2Result && <p className="hint">{tr("rightPlaceholder")}</p>
          )}
        </aside>
      </div>
    </div>
  );
}
