"""Offline tests for the iterative AI builder (fake completer — no provider calls)."""

from __future__ import annotations

import json

import pytest

from backend.build import build_workflow
from backend.n8n import WorkflowError

WF = {
    "name": "Test",
    "nodes": [{"name": "Trigger", "type": "n8n-nodes-base.manualTrigger", "typeVersion": 1, "position": [0, 0], "parameters": {}}],
    "connections": {},
}


class FakeCompleter:
    def __init__(self, text: str) -> None:
        self.text = text
        self.seen: tuple[str, str] | None = None

    def complete(self, system: str, user: str) -> str:
        self.seen = (system, user)
        return self.text


def test_build_from_scratch_parses_valid_workflow() -> None:
    fake = FakeCompleter(json.dumps({"workflow": WF, "notes": "created a trigger"}))
    result = build_workflow(None, "make a manual trigger", completer=fake)
    assert result.workflow["nodes"][0]["name"] == "Trigger"
    assert result.notes == "created a trigger"
    # The current workflow (none) and instruction are passed to the model.
    assert "no workflow yet" in fake.seen[1]
    assert "manual trigger" in fake.seen[1]


def test_build_passes_current_workflow_as_context() -> None:
    fake = FakeCompleter(json.dumps({"workflow": WF, "notes": "unchanged"}))
    build_workflow(WF, "add a Slack node", completer=fake)
    assert "Trigger" in fake.seen[1]  # current workflow serialized into the prompt
    assert "add a Slack node" in fake.seen[1]


def test_build_tolerates_code_fences() -> None:
    fenced = "```json\n" + json.dumps({"workflow": WF, "notes": "ok"}) + "\n```"
    result = build_workflow(None, "x", completer=FakeCompleter(fenced))
    assert result.workflow["name"] == "Test"


def test_build_tolerates_bare_workflow_object() -> None:
    result = build_workflow(None, "x", completer=FakeCompleter(json.dumps(WF)))
    assert result.workflow["nodes"][0]["name"] == "Trigger"


def test_build_rejects_invalid_model_output() -> None:
    with pytest.raises(WorkflowError):
        build_workflow(None, "x", completer=FakeCompleter("sorry, I cannot do that"))
    with pytest.raises(WorkflowError):
        build_workflow(None, "x", completer=FakeCompleter(json.dumps({"workflow": {"nodes": []}})))
