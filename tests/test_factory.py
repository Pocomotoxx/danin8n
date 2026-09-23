"""Offline tests for the n8n workflow factory. No LLM/provider calls (uses EchoCompleter)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.customize import customize_workflow
from backend.llm import EchoCompleter
from backend.n8n import (
    WorkflowError,
    find_placeholders,
    inspect_workflow,
    parse_workflow,
    substitute_placeholders,
)

SAMPLE = json.loads((Path(__file__).resolve().parents[1] / "samples" / "welcome_email.json").read_text())

PROFILE = {
    "name": "Acme Co",
    "company_name": "Acme Co",
    "website": "https://acme.example",
    "from_email": "hello@acme.example",
}


def test_parse_rejects_non_workflow() -> None:
    with pytest.raises(WorkflowError):
        parse_workflow({"nodes": []})
    with pytest.raises(WorkflowError):
        parse_workflow([])


def test_inspect_lists_nodes_creds_placeholders() -> None:
    info = inspect_workflow(SAMPLE)
    assert info.node_count == 3
    assert info.credentials_needed == ["smtp"]
    # Placeholders include both field and ai kinds; n8n {{ $json }} expressions are not placeholders.
    assert "website" in info.placeholders
    assert "company_name" in info.placeholders
    assert any(p.startswith("ai:") for p in info.placeholders)


def test_substitute_only_touches_double_brackets() -> None:
    out = substitute_placeholders(SAMPLE, {"website": "https://acme.example"})
    dumped = json.dumps(out)
    assert "https://acme.example" in dumped
    assert "[[website]]" not in dumped
    # n8n's own expression syntax must survive untouched.
    assert "{{ $json.email }}" in dumped
    assert "={{ $json.email }}" in dumped


def test_customize_fills_fields_and_ai_and_reports() -> None:
    result = customize_workflow(SAMPLE, PROFILE, completer=EchoCompleter())
    dumped = json.dumps(result.workflow)

    # Field placeholders resolved from the profile.
    assert "[[website]]" not in dumped
    assert "[[company_name]]" not in dumped
    assert "[[from_email]]" not in dumped
    assert "https://acme.example" in dumped

    # AI placeholders resolved (Echo returns the instruction text back).
    assert not any("[[ai:" in s for s in [dumped])
    assert result.report.ai_filled  # at least one ai field filled

    # Workflow renamed with company, credentials reported, n8n expressions intact.
    assert result.workflow["name"].startswith("Acme Co —")
    assert result.report.credentials_to_setup == ["smtp"]
    assert "{{ $json.name }}" in dumped


def test_customize_without_completer_leaves_ai_unresolved() -> None:
    result = customize_workflow(SAMPLE, PROFILE, completer=None)
    assert any(u.startswith("ai:") for u in result.report.unresolved)
    # Field placeholders still resolved even without an LLM.
    assert "[[website]]" not in json.dumps(result.workflow)


def test_unknown_field_placeholder_is_reported_not_dropped() -> None:
    wf = {
        "name": "t",
        "nodes": [{"name": "n", "type": "x", "parameters": {"v": "[[missing_field]]"}}],
        "connections": {},
    }
    result = customize_workflow(wf, {"name": "X"}, completer=EchoCompleter())
    assert "missing_field" in result.report.unresolved
    assert "[[missing_field]]" in json.dumps(result.workflow)  # left as-is, not silently removed
