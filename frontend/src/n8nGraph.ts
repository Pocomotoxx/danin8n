import type { Edge, Node } from "@xyflow/react";
import type { N8nWorkflow } from "./api";

// Convert an n8n workflow into React Flow nodes/edges using n8n's own node positions.
export function toGraph(workflow: N8nWorkflow): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = (workflow.nodes ?? []).map((n, i) => {
    const name = String((n as { name?: string }).name ?? `node_${i}`);
    const type = String((n as { type?: string }).type ?? "").replace("n8n-nodes-base.", "");
    const pos = (n as { position?: [number, number] }).position;
    return {
      id: name,
      position: { x: pos?.[0] ?? 240, y: pos?.[1] ?? 120 + i * 120 },
      data: { label: `${name}\n(${type})` },
      style: {
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        padding: 8,
        background: "#fff",
        fontSize: 11,
        whiteSpace: "pre-line" as const,
        textAlign: "center" as const,
      },
    };
  });

  const edges: Edge[] = [];
  const connections = (workflow.connections ?? {}) as Record<
    string,
    { main?: Array<Array<{ node: string }>> }
  >;
  for (const [source, conn] of Object.entries(connections)) {
    for (const group of conn.main ?? []) {
      for (const target of group ?? []) {
        edges.push({
          id: `${source}->${target.node}`,
          source,
          target: target.node,
          animated: true,
        });
      }
    }
  }
  return { nodes, edges };
}
