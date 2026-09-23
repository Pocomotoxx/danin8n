import { useEffect, useMemo, useState } from "react";
import { Background, Controls, ReactFlow } from "@xyflow/react";

import {
  buildWorkflow,
  customize,
  getTemplate,
  inspect,
  listTemplates,
  type CustomizeResult,
  type Inspection,
  type N8nWorkflow,
  type TemplateMeta,
} from "./api";
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
      setStatus({ kind: "ok", msg: `Loaded "${info.name}" — ${info.node_count} nodes.` });
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
      setStatus({ kind: "err", msg: `Invalid workflow JSON: ${String(e)}` });
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
      const n = Object.keys(res.report.ai_filled).length;
      setStatus({ kind: "ok", msg: `Generated. ${n} AI field(s) filled.` });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const copyJson = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(JSON.stringify(result.workflow, null, 2));
    setStatus({ kind: "info", msg: "Copied workflow JSON to clipboard." });
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
      setChat((c) => [...c, { role: "ai", text: notes || "Updated the workflow." }]);
      setStatus({ kind: "ok", msg: "Workflow updated by AI." });
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
        <span className="sub">import a template → add company data → copy a ready workflow</span>
        {status && <span className={`status ${status.kind}`}>{status.msg}</span>}
      </header>

      <div className="body">
        <aside className="panel left">
          <div className="section">🛠 Build with AI</div>
          {chat.length > 0 && (
            <div className="chat">
              {chat.map((m, i) => (
                <div key={i} className={`msg ${m.role}`}>{m.text}</div>
              ))}
            </div>
          )}
          <textarea
            className="chat-in"
            placeholder="Describe or change the workflow, e.g. 'watch a Gmail label, summarize new mail, post to Telegram'"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) doBuild();
            }}
          />
          <label>model
            <input value={buildModel} onChange={(e) => setBuildModel(e.target.value)} />
          </label>
          <button className="primary" disabled={busy || !instruction.trim()} onClick={doBuild}>
            {result || workflow ? "Send (update workflow)" : "Send (create workflow)"}
          </button>
          <p className="hint">Ctrl/⌘+Enter to send. Needs a provider key (any LiteLLM model).</p>

          <div className="section">1 · Import n8n workflow</div>
          {templates.length > 0 && (
            <label>
              Start from a template
              <select defaultValue="" disabled={busy} onChange={(e) => loadTemplate(e.target.value)}>
                <option value="">— choose a template ({templates.length}) —</option>
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
            placeholder="…or paste an n8n workflow JSON here"
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
          />
          <div className="row">
            <button onClick={() => setRaw(SAMPLE)}>Load sample</button>
            <button disabled={busy || !raw.trim()} onClick={doInspect}>Inspect</button>
          </div>

          {insp && (
            <>
              <div className="section">2 · Company data</div>
              {Object.keys(profile).map((f) => (
                <label key={f}>
                  {f}
                  <input value={profile[f]} onChange={(e) => setProfile({ ...profile, [f]: e.target.value })} />
                </label>
              ))}

              {insp.placeholders.ai.length > 0 && (
                <>
                  <div className="section">AI-written fields</div>
                  <ul className="ai-list">
                    {insp.placeholders.ai.map((a, i) => <li key={i}>{a}</li>)}
                  </ul>
                  <label className="check">
                    <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} />
                    Fill with an LLM
                  </label>
                  {useLlm && (
                    <label>model
                      <input value={model} onChange={(e) => setModel(e.target.value)} />
                    </label>
                  )}
                </>
              )}

              {insp.credentials_needed.length > 0 && (
                <p className="hint">Credentials to set up in n8n: {insp.credentials_needed.join(", ")}</p>
              )}

              <button className="primary" disabled={busy} onClick={doGenerate}>Generate workflow</button>
            </>
          )}
        </aside>

        <main className="canvas">
          <ReactFlow nodes={graph.nodes} edges={graph.edges} fitView>
            <Background />
            <Controls />
          </ReactFlow>
        </main>

        <aside className="panel right">
          {result ? (
            <>
              <div className="section">3 · Ready workflow <button onClick={copyJson}>Copy JSON</button></div>
              {result.report.unresolved.length > 0 && (
                <p className="warn">Unresolved: {result.report.unresolved.join(", ")}</p>
              )}
              {result.report.credentials_to_setup.length > 0 && (
                <p className="hint">Set up in n8n: {result.report.credentials_to_setup.join(", ")}</p>
              )}
              <pre className="code">{JSON.stringify(result.workflow, null, 2)}</pre>
            </>
          ) : (
            <p className="hint">Inspect a workflow, add company data, then Generate to get a workflow you can paste into n8n.</p>
          )}
        </aside>
      </div>
    </div>
  );
}
