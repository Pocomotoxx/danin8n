"""Customize an n8n workflow template for a specific company.

Pipeline:
1. Classify placeholders: ``[[field]]`` (from the company profile) vs ``[[ai: instruction]]``
   (filled by an LLM using the company as context).
2. Resolve field placeholders from the profile; resolve AI placeholders via the completer.
3. Substitute everything into a deep copy of the workflow.
4. Optionally rename the workflow and label credential slots so the marketer knows what to wire
   up in n8n.

Secrets are never handled here: real API keys live in n8n's own credential store. This tool only
references credential *slots* by name.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .llm import Completer
from .n8n import find_placeholders, inspect_workflow, parse_workflow, substitute_placeholders

AI_PREFIX = "ai:"


@dataclass
class CustomizationReport:
    workflow_name: str
    fields_filled: dict[str, str] = field(default_factory=dict)
    ai_filled: dict[str, str] = field(default_factory=dict)
    unresolved: list[str] = field(default_factory=list)
    credentials_to_setup: list[str] = field(default_factory=list)


@dataclass
class CustomizationResult:
    workflow: dict[str, Any]
    report: CustomizationReport


def _company_context(profile: dict[str, str]) -> str:
    lines = [f"- {k}: {v}" for k, v in profile.items() if str(v).strip()]
    return "Company profile:\n" + "\n".join(lines) if lines else "Company profile: (none provided)"


def customize_workflow(
    workflow: dict[str, Any],
    profile: dict[str, str],
    *,
    completer: Completer | None = None,
    rename: bool = True,
) -> CustomizationResult:
    """Customize ``workflow`` for the company described by ``profile``.

    ``completer`` fills ``[[ai: ...]]`` placeholders; when ``None`` those are left unresolved and
    reported so the caller can prompt for a provider.
    """
    parse_workflow(workflow)
    placeholders = find_placeholders(workflow)

    values: dict[str, str] = {}
    report = CustomizationReport(workflow_name=workflow.get("name", "Untitled"))

    for raw in placeholders:
        if raw.lower().startswith(AI_PREFIX):
            instruction = raw[len(AI_PREFIX) :].strip()
            if completer is None:
                report.unresolved.append(raw)
                continue
            system = (
                "You customize marketing-automation content. Given a company profile and an "
                "instruction, output ONLY the requested text — no quotes, no preamble, concise."
            )
            user = f"{_company_context(profile)}\n\nInstruction: {instruction}"
            text = completer.complete(system, user).strip()
            values[raw] = text
            report.ai_filled[instruction] = text
        else:
            key = raw
            if key in profile and str(profile[key]).strip():
                values[key] = str(profile[key])
                report.fields_filled[key] = values[key]
            else:
                report.unresolved.append(raw)

    result = substitute_placeholders(workflow, values)

    if rename and profile.get("name"):
        base = workflow.get("name", "Workflow")
        result["name"] = f"{profile['name']} — {base}"
    report.workflow_name = result.get("name", report.workflow_name)

    report.credentials_to_setup = inspect_workflow(result).credentials_needed
    return CustomizationResult(workflow=result, report=report)
