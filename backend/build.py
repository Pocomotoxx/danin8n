"""Iterative AI workflow builder.

Given the current workflow (or nothing) and a natural-language instruction, an LLM returns an
updated COMPLETE n8n workflow plus a short note on what changed. Provider-agnostic (LiteLLM);
the completer is injectable so the pipeline is testable offline.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .llm import Completer
from .n8n import WorkflowError, parse_workflow

# A compact cheat-sheet so the model emits valid node types/shape without a huge prompt.
_SYSTEM = """You are an expert n8n workflow builder. You edit a single n8n workflow as JSON.

An n8n workflow is: {"name": str, "nodes": [...], "connections": {...}}.
A node is: {"name": str (unique), "type": str, "typeVersion": number, "position": [x, y],
"parameters": {...}, optionally "credentials": {<credType>: {"name": str}}}.
Common node types: n8n-nodes-base.manualTrigger, .scheduleTrigger, .webhook, .formTrigger,
.gmail, .telegram, .slack, .httpRequest, .set, .if, .code, .googleSheets, .emailSend;
AI nodes: @n8n/n8n-nodes-langchain.agent, .lmChatOpenAi, .lmChatAnthropic, .chatTrigger.
connections maps a SOURCE node name to {"main": [[{"node": <target name>, "type": "main",
"index": 0}]]}. Lay nodes left-to-right: increase position x by ~220 per step.

Rules:
- Keep existing nodes and connections unless the instruction asks to change them.
- Output ONLY one JSON object, no markdown fences, of the shape:
  {"workflow": <the full updated workflow>, "notes": <one sentence on what changed>}."""


@dataclass
class BuildResult:
    workflow: dict[str, Any]
    notes: str


def _extract_json(text: str) -> dict[str, Any]:
    """Pull a JSON object out of the model output, tolerating code fences / stray prose."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise WorkflowError("Model did not return JSON.") from None
        return json.loads(text[start : end + 1])


def build_workflow(
    current: dict[str, Any] | None,
    instruction: str,
    *,
    completer: Completer,
) -> BuildResult:
    """Apply ``instruction`` to ``current`` (or build from scratch) via the LLM completer."""
    base = json.dumps(current, ensure_ascii=False) if current else "(no workflow yet — create one)"
    user = f"Current workflow:\n{base}\n\nInstruction: {instruction}"
    raw = completer.complete(_SYSTEM, user)

    payload = _extract_json(raw)
    workflow = payload.get("workflow", payload)  # tolerate a bare workflow object
    parse_workflow(workflow)  # raises WorkflowError if the model produced something invalid
    notes = str(payload.get("notes", "")) if isinstance(payload, dict) else ""
    return BuildResult(workflow=workflow, notes=notes)


# --- Rule-based fallback (demo mode, no LLM key needed) ----------------------------------------

# keyword -> (node type, display name). Order matters: first match wins for the trigger/output.
_TRIGGERS: list[tuple[tuple[str, ...], str, str]] = [
    (("schedule", "every", "daily", "morning", "cron", "hour"), "n8n-nodes-base.scheduleTrigger", "Schedule"),
    (("form",), "n8n-nodes-base.formTrigger", "Form Submitted"),
    (("chat", "message arrives"), "@n8n/n8n-nodes-langchain.chatTrigger", "Chat Message"),
    (("webhook", "incoming", "request", "http"), "n8n-nodes-base.webhook", "Webhook"),
]
_OUTPUTS: list[tuple[tuple[str, ...], str, str]] = [
    (("gmail",), "n8n-nodes-base.gmail", "Send Gmail"),
    (("email", "mail", "e-mail"), "n8n-nodes-base.emailSend", "Send Email"),
    (("telegram",), "n8n-nodes-base.telegram", "Send Telegram"),
    (("slack",), "n8n-nodes-base.slack", "Post to Slack"),
    (("sheet", "spreadsheet"), "n8n-nodes-base.googleSheets", "Update Sheet"),
    (("http", "api", "fetch", "call"), "n8n-nodes-base.httpRequest", "HTTP Request"),
]


def _node(name: str, ntype: str, x: int) -> dict[str, Any]:
    return {"name": name, "type": ntype, "typeVersion": 1, "position": [x, 300], "parameters": {}}


def _match(text: str, table: list[tuple[tuple[str, ...], str, str]]) -> tuple[str, str] | None:
    for keys, ntype, label in table:
        if any(k in text for k in keys):
            return ntype, label
    return None


def heuristic_build(current: dict[str, Any] | None, instruction: str) -> BuildResult:
    """A no-LLM fallback: assemble a simple linear workflow from keywords in the instruction."""
    text = instruction.lower()

    if current and current.get("nodes"):
        # Extend the existing workflow: add an output/processing node wired after the last node.
        wf = json.loads(json.dumps(current))
        out = _match(text, _OUTPUTS) or ("n8n-nodes-base.set", "Process")
        last = max(wf["nodes"], key=lambda n: (n.get("position") or [0, 0])[0])
        new = _node(out[1], out[0], (last.get("position") or [0, 300])[0] + 220)
        wf["nodes"].append(new)
        wf.setdefault("connections", {}).setdefault(last["name"], {}).setdefault("main", [[]])
        wf["connections"][last["name"]]["main"][0].append({"node": new["name"], "type": "main", "index": 0})
        return BuildResult(workflow=wf, notes=f"Added a '{out[1]}' node after '{last['name']}'.")

    # Build a fresh linear workflow: trigger -> (process) -> output.
    trig = _match(text, _TRIGGERS) or ("n8n-nodes-base.manualTrigger", "When clicked")
    steps = [_node(trig[1], trig[0], 240)]
    if any(k in text for k in ("summar", "ai", "generate", "classif", "write", "extract", "process")):
        steps.append(_node("Prepare / AI step", "n8n-nodes-base.set", 460))
    out = _match(text, _OUTPUTS)
    if out:
        steps.append(_node(out[1], out[0], 240 + 220 * len(steps)))

    connections: dict[str, Any] = {}
    for a, b in zip(steps, steps[1:]):
        connections[a["name"]] = {"main": [[{"node": b["name"], "type": "main", "index": 0}]]}

    name = instruction.strip()[:60] or "New workflow"
    workflow = {"name": name, "nodes": steps, "connections": connections}
    return BuildResult(workflow=workflow, notes=f"Built a {len(steps)}-step workflow from your description.")
