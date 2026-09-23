"""Build a data-intake template for a workflow.

Given an n8n workflow, list everything the user must provide before it can run:
- Credentials (API keys, passwords, tokens) — inferred from each node's declared ``credentials``
  and from node types that always need one (e.g. a Gmail node needs Gmail credentials).
- Config fields — the ``[[field]]`` placeholders (company data: emails, URLs, names, …).
- AI fields — the ``[[ai: …]]`` placeholders written by an LLM.

Security: secret values are NEVER collected or stored by this tool. The intake is a blank
*specification*. Secret fields are flagged so the UI can warn "enter this in n8n, not here", and
the generated .env template lists names only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .customize import AI_PREFIX
from .n8n import find_placeholders, parse_workflow

# Credential type -> the fields it needs, with a secret flag. (name, secret)
CRED_FIELDS: dict[str, list[tuple[str, bool]]] = {
    "smtp": [("host", False), ("port", False), ("user", False), ("password", True)],
    "imap": [("host", False), ("port", False), ("user", False), ("password", True)],
    "httpBasicAuth": [("user", False), ("password", True)],
    "httpHeaderAuth": [("name", False), ("value", True)],
    "httpQueryAuth": [("name", False), ("value", True)],
    "oAuth2Api": [("clientId", False), ("clientSecret", True)],
    "openAiApi": [("apiKey", True)],
    "anthropicApi": [("apiKey", True)],
    "telegramApi": [("accessToken", True)],
    "slackApi": [("accessToken", True)],
    "slackOAuth2Api": [("clientId", False), ("clientSecret", True)],
    "gmailOAuth2": [("clientId", False), ("clientSecret", True)],
    "googleSheetsOAuth2Api": [("clientId", False), ("clientSecret", True)],
    "googleCalendarOAuth2Api": [("clientId", False), ("clientSecret", True)],
    "googleApi": [("email", False), ("privateKey", True)],
    "openWeatherMapApi": [("apiKey", True)],
    "twilioApi": [("accountSid", False), ("authToken", True)],
    "notionApi": [("apiKey", True)],
    "airtableTokenApi": [("apiKey", True)],
    "pineconeApi": [("apiKey", True)],
    "postgres": [("host", False), ("port", False), ("database", False), ("user", False), ("password", True)],
    "mySql": [("host", False), ("port", False), ("database", False), ("user", False), ("password", True)],
}

# Node type (short, base name) -> the credential type it normally requires.
NODE_CRED: dict[str, str] = {
    "gmail": "gmailOAuth2",
    "emailSend": "smtp",
    "emailReadImap": "imap",
    "telegram": "telegramApi",
    "slack": "slackApi",
    "googleSheets": "googleSheetsOAuth2Api",
    "googleCalendar": "googleCalendarOAuth2Api",
    "openWeatherMap": "openWeatherMapApi",
    "twilio": "twilioApi",
    "notion": "notionApi",
    "airtable": "airtableTokenApi",
    "postgres": "postgres",
    "mySql": "mySql",
    # LangChain AI nodes
    "lmChatOpenAi": "openAiApi",
    "openAi": "openAiApi",
    "embeddingsOpenAi": "openAiApi",
    "lmChatAnthropic": "anthropicApi",
    "vectorStorePinecone": "pineconeApi",
}


def _short_type(node_type: str) -> str:
    return node_type.replace("n8n-nodes-base.", "").replace("@n8n/n8n-nodes-langchain.", "")


def _cred_fields(cred_type: str) -> list[dict[str, Any]]:
    fields = CRED_FIELDS.get(cred_type) or [("apiKey", True)]
    return [{"name": n, "secret": s} for n, s in fields]


def _guess_field_type(name: str) -> tuple[str, bool]:
    """Return (input type, secret) guessed from a placeholder/field name."""
    n = name.lower()
    if any(k in n for k in ("password", "secret", "apikey", "api_key", "token", "key")):
        return "password", True
    if "email" in n or "mail" in n:
        return "email", False
    if any(k in n for k in ("url", "website", "link", "endpoint", "webhook")):
        return "url", False
    if any(k in n for k in ("phone", "number", "count", "port")):
        return "text", False
    return "text", False


@dataclass
class IntakeCredential:
    node: str
    type: str
    fields: list[dict[str, Any]]
    declared: bool  # True if the workflow already references this credential slot


@dataclass
class IntakeField:
    name: str
    type: str
    secret: bool
    source: str  # "field" or "ai"


@dataclass
class Intake:
    workflow_name: str
    credentials: list[IntakeCredential] = field(default_factory=list)
    config_fields: list[IntakeField] = field(default_factory=list)
    ai_fields: list[str] = field(default_factory=list)


def build_intake(workflow: dict[str, Any]) -> Intake:
    parse_workflow(workflow)
    intake = Intake(workflow_name=workflow.get("name", "Untitled"))

    seen_creds: set[tuple[str, str]] = set()
    for node in workflow["nodes"]:
        name = node["name"]
        # Declared credential slots on the node.
        for cred_type in (node.get("credentials") or {}):
            key = (name, cred_type)
            if key not in seen_creds:
                seen_creds.add(key)
                intake.credentials.append(
                    IntakeCredential(name, cred_type, _cred_fields(cred_type), declared=True)
                )
        # Inferred credential from the node type.
        inferred = NODE_CRED.get(_short_type(node.get("type", "")))
        if inferred:
            key = (name, inferred)
            if key not in seen_creds:
                seen_creds.add(key)
                intake.credentials.append(
                    IntakeCredential(name, inferred, _cred_fields(inferred), declared=False)
                )

    for raw in find_placeholders(workflow):
        if raw.lower().startswith(AI_PREFIX):
            intake.ai_fields.append(raw[len(AI_PREFIX):].strip())
        else:
            ftype, secret = _guess_field_type(raw)
            intake.config_fields.append(IntakeField(raw, ftype, secret, source="field"))

    return intake


def to_dict(intake: Intake) -> dict[str, Any]:
    return asdict(intake)


def render_env(intake: Intake) -> str:
    """A blank .env-style intake template (names only; secrets flagged, never filled)."""
    lines = [f"# Data intake for: {intake.workflow_name}", "# Fill values in YOUR environment. Never commit real secrets.", ""]
    if intake.config_fields:
        lines.append("# --- Config (non-secret) ---")
        for f in intake.config_fields:
            tag = "  # secret" if f.secret else f"  # {f.type}"
            lines.append(f"{f.name.upper()}={tag}")
        lines.append("")
    if intake.credentials:
        lines.append("# --- Credentials → create these in n8n (do NOT store real secrets here) ---")
        for c in intake.credentials:
            lines.append(f"# {c.node}: n8n credential '{c.type}'")
            for fld in c.fields:
                mark = " (SECRET)" if fld["secret"] else ""
                lines.append(f"#   - {fld['name']}{mark}")
        lines.append("")
    return "\n".join(lines)


def render_checklist(intake: Intake) -> str:
    """A human-friendly Markdown intake checklist."""
    out = [f"# Setup checklist — {intake.workflow_name}", ""]
    if intake.credentials:
        out.append("## Credentials to create in n8n")
        for c in intake.credentials:
            fields = ", ".join(f"{f['name']}{'🔒' if f['secret'] else ''}" for f in c.fields)
            note = "" if c.declared else " _(inferred from node type)_"
            out.append(f"- [ ] **{c.type}** for node *{c.node}*{note} — {fields}")
        out.append("")
    if intake.config_fields:
        out.append("## Company / config data")
        for f in intake.config_fields:
            out.append(f"- [ ] `{f.name}` ({f.type})")
        out.append("")
    if intake.ai_fields:
        out.append("## AI-written fields (filled automatically with an LLM)")
        for a in intake.ai_fields:
            out.append(f"- {a}")
        out.append("")
    return "\n".join(out)
