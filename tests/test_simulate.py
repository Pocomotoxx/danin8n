"""Offline tests for the dry-run preview (sandbox)."""

from __future__ import annotations

import json
from pathlib import Path

from backend.simulate import simulate_workflow

SAMPLE = json.loads((Path(__file__).resolve().parents[1] / "samples" / "welcome_email.json").read_text())


def test_simulate_orders_from_trigger() -> None:
    steps = simulate_workflow(SAMPLE)
    names = [s.node for s in steps]
    # Webhook (trigger) first, then Compose, then Send — following the connections.
    assert names == ["New Lead Webhook", "Compose Email", "Send Email"]
    assert steps[0].order == 1


def test_simulate_marks_side_effects() -> None:
    steps = simulate_workflow(SAMPLE)
    send = next(s for s in steps if s.node == "Send Email")
    assert send.effect == "side-effect"
    assert "Simulated only" in send.note
    assert send.sample.get("to")  # a mock recipient is shown


def test_simulate_describes_set_fields() -> None:
    steps = simulate_workflow(SAMPLE)
    compose = next(s for s in steps if s.node == "Compose Email")
    assert compose.effect == "transform"
    assert "subject" in compose.action and "body" in compose.action


def test_simulate_handles_unknown_nodes() -> None:
    wf = {
        "name": "t",
        "nodes": [{"name": "X", "type": "n8n-nodes-base.somethingNew", "parameters": {}}],
        "connections": {},
    }
    steps = simulate_workflow(wf)
    assert steps[0].effect == "transform"
    assert "somethingNew" in steps[0].action


def test_unreachable_nodes_still_listed() -> None:
    wf = {
        "name": "t",
        "nodes": [
            {"name": "T", "type": "n8n-nodes-base.manualTrigger", "parameters": {}},
            {"name": "Orphan", "type": "n8n-nodes-base.set", "parameters": {}},
        ],
        "connections": {},
    }
    names = [s.node for s in simulate_workflow(wf)]
    assert set(names) == {"T", "Orphan"}
