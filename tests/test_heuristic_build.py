"""Offline tests for the no-LLM rule-based build fallback."""

from __future__ import annotations

from backend.build import heuristic_build
from backend.n8n import parse_workflow


def test_builds_trigger_process_output_chain() -> None:
    r = heuristic_build(None, "every morning summarize the data and send it by email")
    parse_workflow(r.workflow)  # valid n8n workflow
    types = [n["type"] for n in r.workflow["nodes"]]
    assert types[0] == "n8n-nodes-base.scheduleTrigger"  # "every morning"
    assert types[-1] == "n8n-nodes-base.emailSend"  # "email"
    assert any("set" in t for t in types)  # "summarize" -> processing step
    # Nodes are wired in a chain.
    assert r.workflow["connections"]


def test_keywords_pick_telegram_and_webhook() -> None:
    r = heuristic_build(None, "on a webhook, post a message to telegram")
    types = [n["type"] for n in r.workflow["nodes"]]
    assert types[0] == "n8n-nodes-base.webhook"
    assert "n8n-nodes-base.telegram" in types


def test_extend_existing_workflow() -> None:
    base = heuristic_build(None, "webhook then email").workflow
    n_before = len(base["nodes"])
    r = heuristic_build(base, "also post to slack")
    assert len(r.workflow["nodes"]) == n_before + 1
    assert any(n["type"] == "n8n-nodes-base.slack" for n in r.workflow["nodes"])


def test_default_manual_trigger() -> None:
    r = heuristic_build(None, "do something")
    assert r.workflow["nodes"][0]["type"] == "n8n-nodes-base.manualTrigger"
