"""Offline tests for the data-intake template builder."""

from __future__ import annotations

import json
from pathlib import Path

from backend.intake import build_intake, render_checklist, render_env

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = json.loads((ROOT / "samples" / "welcome_email.json").read_text())


def test_intake_from_sample_lists_credential_fields() -> None:
    intake = build_intake(SAMPLE)
    # The Send Email node declares an smtp credential; smtp needs a secret password.
    smtp = [c for c in intake.credentials if c.type == "smtp"]
    assert smtp, "smtp credential expected"
    field_names = {f["name"] for f in smtp[0].fields}
    assert {"host", "port", "user", "password"} <= field_names
    assert any(f["name"] == "password" and f["secret"] for f in smtp[0].fields)


def test_intake_classifies_config_field_types() -> None:
    intake = build_intake(SAMPLE)
    by_name = {f.name: f for f in intake.config_fields}
    assert by_name["website"].type == "url"
    assert by_name["from_email"].type == "email"
    assert intake.ai_fields  # [[ai: ...]] instructions surfaced


def test_intake_infers_credentials_from_node_types() -> None:
    # A workflow using a Gmail + Telegram node but declaring no credentials block.
    wf = {
        "name": "notify",
        "nodes": [
            {"name": "Read Mail", "type": "n8n-nodes-base.gmail", "parameters": {}},
            {"name": "Notify", "type": "n8n-nodes-base.telegram", "parameters": {}},
        ],
        "connections": {},
    }
    intake = build_intake(wf)
    types = {c.type for c in intake.credentials}
    assert "gmailOAuth2" in types
    assert "telegramApi" in types
    assert all(c.declared is False for c in intake.credentials)  # inferred, not declared


def test_password_field_is_secret() -> None:
    wf = {
        "name": "t",
        "nodes": [{"name": "n", "type": "x", "parameters": {"v": "[[api_key]]"}}],
        "connections": {},
    }
    intake = build_intake(wf)
    f = next(f for f in intake.config_fields if f.name == "api_key")
    assert f.secret and f.type == "password"


def test_render_env_and_checklist() -> None:
    intake = build_intake(SAMPLE)
    env = render_env(intake)
    assert "FROM_EMAIL=" in env
    assert "secret" in env.lower()  # secret fields flagged, never filled
    md = render_checklist(intake)
    assert "Setup checklist" in md
    assert "smtp" in md
