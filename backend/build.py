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
