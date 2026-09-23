"""Offline API tests (FastAPI TestClient). No provider calls."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app  # noqa: E402

client = TestClient(app)
SAMPLE = json.loads((Path(__file__).resolve().parents[1] / "samples" / "welcome_email.json").read_text())
PROFILE = {"name": "Acme Co", "company_name": "Acme Co", "website": "https://acme.example", "from_email": "hi@acme.example"}


def test_health() -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_inspect_classifies_placeholders() -> None:
    data = client.post("/api/inspect", json={"workflow": SAMPLE}).json()
    assert data["node_count"] == 3
    assert data["credentials_needed"] == ["smtp"]
    assert "website" in data["placeholders"]["fields"]
    assert data["placeholders"]["ai"]  # at least one AI instruction surfaced


def test_inspect_rejects_bad_workflow() -> None:
    assert client.post("/api/inspect", json={"workflow": {"nodes": []}}).status_code == 400


def test_customize_deterministic_no_llm() -> None:
    resp = client.post("/api/customize", json={"workflow": SAMPLE, "profile": PROFILE, "use_llm": False})
    assert resp.status_code == 200
    data = resp.json()
    dumped = json.dumps(data["workflow"])
    assert "[[website]]" not in dumped  # field filled
    assert "{{ $json.email }}" in dumped  # n8n expression preserved
    assert any(u.startswith("ai:") for u in data["report"]["unresolved"])  # ai left for LLM


def test_customize_preview_fills_ai_offline() -> None:
    data = client.post("/api/customize_preview", json={"workflow": SAMPLE, "profile": PROFILE}).json()
    assert "[[ai:" not in json.dumps(data["workflow"])
    assert data["report"]["ai_filled"]
