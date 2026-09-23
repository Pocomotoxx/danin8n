"""n8n workflow domain model: parse, validate, inspect, and substitute placeholders.

An n8n workflow is a JSON object with at least ``nodes`` (a list) and ``connections`` (a dict).
Each node has ``name``, ``type``, ``typeVersion``, ``position`` and ``parameters``; some declare
``credentials``.

Templates authored for this tool may embed ``[[field]]`` placeholders (double square brackets),
which do NOT collide with n8n's own ``{{ $json... }}`` expression syntax, so substitution is safe.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Matches [[field]] and [[ai: instruction]] placeholders. Non-greedy so multiple per string work.
# Uses double square brackets, which never collide with n8n's own {{ $json... }} expressions.
PLACEHOLDER_RE = re.compile(r"\[\[\s*(.+?)\s*\]\]")


class WorkflowError(ValueError):
    """Raised when a JSON payload is not a usable n8n workflow."""


@dataclass
class NodeInfo:
    name: str
    type: str
    credentials: list[str] = field(default_factory=list)


@dataclass
class WorkflowInspection:
    name: str
    node_count: int
    nodes: list[NodeInfo]
    credentials_needed: list[str]
    placeholders: list[str]


def parse_workflow(payload: Any) -> dict[str, Any]:
    """Validate that ``payload`` is a usable n8n workflow and return it as a dict."""
    if not isinstance(payload, dict):
        raise WorkflowError("Workflow must be a JSON object.")
    nodes = payload.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise WorkflowError("Workflow must have a non-empty 'nodes' array.")
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise WorkflowError(f"Node #{i} is not an object.")
        if "name" not in node or "type" not in node:
            raise WorkflowError(f"Node #{i} must have 'name' and 'type'.")
    connections = payload.get("connections", {})
    if not isinstance(connections, dict):
        raise WorkflowError("'connections' must be an object.")
    return payload


def _walk_strings(value: Any):
    """Yield every string found anywhere in a nested structure."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _walk_strings(v)


def find_placeholders(workflow: dict[str, Any]) -> list[str]:
    """Return the sorted unique ``[[field]]`` placeholder names used anywhere in the workflow."""
    found: set[str] = set()
    for s in _walk_strings(workflow):
        for m in PLACEHOLDER_RE.findall(s):
            found.add(m.strip())
    return sorted(found)


def inspect_workflow(workflow: dict[str, Any]) -> WorkflowInspection:
    """Summarize the workflow: nodes, credentials required, and placeholders to fill."""
    parse_workflow(workflow)
    nodes: list[NodeInfo] = []
    creds: set[str] = set()
    for node in workflow["nodes"]:
        node_creds = list((node.get("credentials") or {}).keys())
        creds.update(node_creds)
        nodes.append(NodeInfo(name=node["name"], type=node["type"], credentials=node_creds))
    return WorkflowInspection(
        name=workflow.get("name", "Untitled"),
        node_count=len(nodes),
        nodes=nodes,
        credentials_needed=sorted(creds),
        placeholders=find_placeholders(workflow),
    )


def substitute_placeholders(workflow: dict[str, Any], values: dict[str, str]) -> dict[str, Any]:
    """Return a deep copy of ``workflow`` with ``[[field]]`` placeholders replaced from ``values``.

    Unknown placeholders are left as-is so nothing is silently dropped. Substitution is applied to
    every string, recursively.
    """

    def repl(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        return values.get(key, match.group(0))

    def transform(value: Any) -> Any:
        if isinstance(value, str):
            return PLACEHOLDER_RE.sub(repl, value)
        if isinstance(value, dict):
            return {k: transform(v) for k, v in value.items()}
        if isinstance(value, list):
            return [transform(v) for v in value]
        return value

    return transform(workflow)
