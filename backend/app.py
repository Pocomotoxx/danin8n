"""FastAPI backend for the n8n workflow factory.

Endpoints:
- GET  /api/health
- POST /api/inspect    -> summarize a pasted n8n workflow (nodes, credentials, placeholders).
- POST /api/customize  -> fill placeholders for a company and return a ready-to-import workflow.

No OpenAI SDK: LLM features go through LiteLLM (any provider). The deterministic path (field
placeholders + credential report) needs no LLM and no key, so the tool is useful offline.
Secrets are never stored: real API keys live in n8n's own credential store.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .build import build_workflow
from .customize import AI_PREFIX, customize_workflow
from .llm import EchoCompleter, LiteLLMCompleter
from .n8n import WorkflowError, inspect_workflow, parse_workflow

app = FastAPI(title="n8n Workflow Factory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class InspectRequest(BaseModel):
    workflow: dict[str, Any]


class CustomizeRequest(BaseModel):
    workflow: dict[str, Any]
    profile: dict[str, str] = {}
    # LLM control (all optional). use_llm=False keeps it fully deterministic/offline.
    use_llm: bool = False
    model: str | None = None


def _classify(placeholders: list[str]) -> dict[str, list[str]]:
    fields, ai = [], []
    for p in placeholders:
        (ai if p.lower().startswith(AI_PREFIX) else fields).append(p)
    return {"fields": fields, "ai": [p[len(AI_PREFIX):].strip() for p in ai]}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/inspect")
def inspect(req: InspectRequest) -> dict[str, Any]:
    try:
        info = inspect_workflow(req.workflow)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "name": info.name,
        "node_count": info.node_count,
        "nodes": [{"name": n.name, "type": n.type, "credentials": n.credentials} for n in info.nodes],
        "credentials_needed": info.credentials_needed,
        "placeholders": _classify(info.placeholders),
    }


@app.post("/api/customize")
def customize(req: CustomizeRequest) -> dict[str, Any]:
    try:
        parse_workflow(req.workflow)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    completer = None
    if req.use_llm:
        try:
            completer = LiteLLMCompleter(model=req.model)
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=502, detail=f"LLM init failed: {exc}") from exc

    try:
        result = customize_workflow(req.workflow, req.profile, completer=completer)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # surface provider/key errors cleanly
        raise HTTPException(status_code=502, detail=f"Customize failed: {exc}") from exc

    r = result.report
    return {
        "workflow": result.workflow,
        "report": {
            "workflow_name": r.workflow_name,
            "fields_filled": r.fields_filled,
            "ai_filled": r.ai_filled,
            "unresolved": r.unresolved,
            "credentials_to_setup": r.credentials_to_setup,
        },
    }


# Preview endpoint for offline demos: deterministic echo fill, no provider needed.
@app.post("/api/customize_preview")
def customize_preview(req: CustomizeRequest) -> dict[str, Any]:
    result = customize_workflow(req.workflow, req.profile, completer=EchoCompleter())
    return {"workflow": result.workflow, "report": {"ai_filled": result.report.ai_filled}}


# --- Iterative AI builder ---------------------------------------------------------------------


class BuildRequest(BaseModel):
    instruction: str
    workflow: dict[str, Any] | None = None
    model: str | None = None


@app.post("/api/build")
def build(req: BuildRequest) -> dict[str, Any]:
    if not req.instruction.strip():
        raise HTTPException(status_code=400, detail="Instruction is empty.")
    try:
        completer = LiteLLMCompleter(model=req.model)
        result = build_workflow(req.workflow, req.instruction, completer=completer)
    except WorkflowError as exc:
        raise HTTPException(status_code=422, detail=f"Model output invalid: {exc}") from exc
    except Exception as exc:  # provider/key/parse errors surfaced cleanly
        raise HTTPException(status_code=502, detail=f"Build failed: {exc}") from exc
    return {"workflow": result.workflow, "notes": result.notes}


# --- Template library (curated n8n workflows shipped with the tool) ---------------------------

_TEMPLATES = Path(__file__).resolve().parents[1] / "templates"


@app.get("/api/templates")
def list_templates() -> dict[str, Any]:
    index = _TEMPLATES / "index.json"
    if not index.is_file():
        return {"templates": []}
    import json

    return {"templates": json.loads(index.read_text(encoding="utf-8"))}


@app.get("/api/templates/{file}")
def get_template(file: str) -> dict[str, Any]:
    # Guard against path traversal: only a bare filename inside templates/ is allowed.
    if "/" in file or "\\" in file or not file.endswith(".json") or file == "index.json":
        raise HTTPException(status_code=400, detail="Invalid template name.")
    path = _TEMPLATES / file
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Template not found.")
    import json

    return {"workflow": json.loads(path.read_text(encoding="utf-8"))}


# Serve the built SPA from the same origin when present (single-server deployment).
_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if _DIST.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="frontend")
