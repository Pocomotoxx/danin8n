"""A safe dry-run preview of an n8n workflow.

Walks the workflow from its trigger(s) along the connections and, for each node, produces a
plain-language description of what it *would* do plus a small sample output. Nothing is executed and
no credentials are used — side-effect nodes (send e-mail, post message, write sheet) are clearly
marked as simulated.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any

from .n8n import parse_workflow

# effect kinds drive the UI badge/colour.
# node type (short) -> (effect, action template). {p} is filled from parameters when useful.
_NODE_INFO: dict[str, tuple[str, str]] = {
    "manualTrigger": ("trigger", "Starts when you run it manually."),
    "scheduleTrigger": ("trigger", "Starts automatically on a schedule."),
    "webhook": ("trigger", "Waits for an incoming web request (webhook)."),
    "formTrigger": ("trigger", "Starts when someone submits a form."),
    "chatTrigger": ("trigger", "Starts when a chat message arrives."),
    "emailReadImap": ("read", "Reads incoming e-mails from a mailbox."),
    "set": ("transform", "Builds or sets fields: {fields}."),
    "code": ("transform", "Runs custom code to transform the data."),
    "if": ("transform", "Branches the flow based on a condition."),
    "switch": ("transform", "Routes the flow into one of several branches."),
    "splitInBatches": ("transform", "Processes the items in batches."),
    "extractFromFile": ("transform", "Extracts data from an uploaded file."),
    "dataTable": ("transform", "Reads or writes the internal data table."),
    "httpRequest": ("external", "Calls an external API."),
    "gmail": ("side-effect", "Sends an e-mail via Gmail."),
    "emailSend": ("side-effect", "Sends an e-mail (SMTP)."),
    "telegram": ("side-effect", "Posts a message to Telegram."),
    "slack": ("side-effect", "Posts a message to Slack."),
    "googleSheets": ("side-effect", "Reads or writes a Google Sheet."),
    "googleCalendar": ("side-effect", "Creates or reads calendar events."),
    "agent": ("ai", "Asks an AI agent to reason and produce a result."),
    "lmChatOpenAi": ("ai", "Calls an AI chat model."),
    "lmChatAnthropic": ("ai", "Calls an AI chat model."),
    "openAi": ("ai", "Calls an AI model."),
}

_SIDE_EFFECT_NOTE = "Simulated only — nothing is actually sent or written in the preview."


@dataclass
class SimStep:
    order: int
    node: str
    type: str
    effect: str
    action: str
    note: str = ""
    sample: dict[str, Any] = field(default_factory=dict)


def _short(node_type: str) -> str:
    return node_type.replace("n8n-nodes-base.", "").replace("@n8n/n8n-nodes-langchain.", "")


def _set_fields(node: dict[str, Any]) -> str:
    vals = (((node.get("parameters") or {}).get("values") or {}).get("string")) or []
    names = [v.get("name", "") for v in vals if isinstance(v, dict) and v.get("name")]
    if not names:
        assignments = ((node.get("parameters") or {}).get("assignments") or {}).get("assignments") or []
        names = [a.get("name", "") for a in assignments if isinstance(a, dict) and a.get("name")]
    return ", ".join(n for n in names if n) or "(various)"


def _sample_for(short_type: str, node: dict[str, Any]) -> dict[str, Any]:
    if short_type in ("webhook", "formTrigger"):
        return {"name": "Jane Doe", "email": "jane@example.com"}
    if short_type == "set":
        return {f: f"<{f}>" for f in _set_fields(node).split(", ") if f and f != "(various)"}
    if short_type in ("gmail", "emailSend"):
        return {"to": "jane@example.com", "subject": "<subject>", "body": "<message>"}
    if short_type in ("telegram", "slack"):
        return {"channel": "<chat>", "text": "<message>"}
    if short_type in ("agent", "lmChatOpenAi", "lmChatAnthropic", "openAi"):
        return {"ai_output": "<generated text>"}
    if short_type == "httpRequest":
        return {"status": 200, "body": "<api response>"}
    return {}


def _order_nodes(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    """Return nodes in execution order: BFS from trigger nodes along connections."""
    by_name = {n["name"]: n for n in workflow["nodes"]}
    connections = workflow.get("connections") or {}
    triggers = [
        n["name"]
        for n in workflow["nodes"]
        if "trigger" in _short(n.get("type", "")).lower() or _short(n.get("type", "")) == "webhook"
    ]
    start = triggers or [workflow["nodes"][0]["name"]] if workflow["nodes"] else []

    ordered: list[str] = []
    seen: set[str] = set()
    queue: deque[str] = deque(start)
    while queue:
        name = queue.popleft()
        if name in seen or name not in by_name:
            continue
        seen.add(name)
        ordered.append(name)
        for group in (connections.get(name, {}) or {}).get("main", []) or []:
            for target in group or []:
                if target.get("node") not in seen:
                    queue.append(target["node"])
    # Append any nodes not reachable from a trigger, preserving definition order.
    for n in workflow["nodes"]:
        if n["name"] not in seen:
            ordered.append(n["name"])
    return [by_name[n] for n in ordered]


def simulate_workflow(workflow: dict[str, Any]) -> list[SimStep]:
    parse_workflow(workflow)
    steps: list[SimStep] = []
    for i, node in enumerate(_order_nodes(workflow), start=1):
        short = _short(node.get("type", ""))
        effect, template = _NODE_INFO.get(short, ("transform", f"Runs the '{short}' node."))
        action = template.replace("{fields}", _set_fields(node)) if "{fields}" in template else template
        steps.append(
            SimStep(
                order=i,
                node=node["name"],
                type=short,
                effect=effect,
                action=action,
                note=_SIDE_EFFECT_NOTE if effect == "side-effect" else "",
                sample=_sample_for(short, node),
            )
        )
    return steps


def to_dicts(steps: list[SimStep]) -> list[dict[str, Any]]:
    return [asdict(s) for s in steps]
