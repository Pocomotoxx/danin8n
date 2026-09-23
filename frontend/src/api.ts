export type N8nWorkflow = {
  name?: string;
  nodes: Array<Record<string, unknown>>;
  connections: Record<string, unknown>;
};

export interface Inspection {
  name: string;
  node_count: number;
  nodes: { name: string; type: string; credentials: string[] }[];
  credentials_needed: string[];
  placeholders: { fields: string[]; ai: string[] };
}

export interface CustomizeReport {
  workflow_name: string;
  fields_filled: Record<string, string>;
  ai_filled: Record<string, string>;
  unresolved: string[];
  credentials_to_setup: string[];
}

export interface CustomizeResult {
  workflow: N8nWorkflow;
  report: CustomizeReport;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    let detail = await resp.text();
    try {
      detail = JSON.parse(detail).detail ?? detail;
    } catch {
      /* keep raw text */
    }
    throw new Error(detail);
  }
  return resp.json() as Promise<T>;
}

export interface TemplateMeta {
  file: string;
  name: string;
  nodes: number;
  credentials: string[];
  integrations: string[];
}

export const listTemplates = () =>
  fetch("/api/templates").then((r) => r.json() as Promise<{ templates: TemplateMeta[] }>);

export const getTemplate = (file: string) =>
  fetch(`/api/templates/${file}`).then((r) => r.json() as Promise<{ workflow: N8nWorkflow }>);

export const inspect = (workflow: N8nWorkflow) => post<Inspection>("/api/inspect", { workflow });

export const customize = (
  workflow: N8nWorkflow,
  profile: Record<string, string>,
  use_llm: boolean,
  model?: string,
) => post<CustomizeResult>("/api/customize", { workflow, profile, use_llm, model });

export const buildWorkflow = (instruction: string, workflow: N8nWorkflow | null, model?: string) =>
  post<{ workflow: N8nWorkflow; notes: string }>("/api/build", { instruction, workflow, model });

export const getIntake = (workflow: N8nWorkflow) =>
  post<{ intake: unknown; env: string; checklist: string }>("/api/intake", { workflow });

export interface SimStep {
  order: number;
  node: string;
  type: string;
  effect: string;
  action: string;
  note: string;
  sample: Record<string, unknown>;
}

export const simulate = (workflow: N8nWorkflow) =>
  post<{ steps: SimStep[] }>("/api/simulate", { workflow });
