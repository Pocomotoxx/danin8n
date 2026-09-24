"""Generate an AG2 Studio workflow you can paste/import into https://app.ag2.ai/.

AG2 Studio uses a declarative JSON workflow. Two shapes:
- ``twoagents``: a userproxy ``sender`` and a single assistant ``receiver``.
- ``groupchat``: a userproxy ``sender`` and a group-chat-manager ``receiver`` whose
  ``groupchat_config.agents`` lists the assistants.

This mirrors the danin8n idea: design here, paste the JSON into the studio. No secrets are stored —
the model name goes into ``llm_config.config_list``; the API key is set in AG2 Studio itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class AG2Error(ValueError):
    """Raised when the agent design is not usable."""


@dataclass
class AG2Agent:
    name: str
    system_message: str = ""


def _llm_config(model: str) -> dict[str, Any]:
    return {
        "config_list": [{"model": model}],
        "temperature": 0.1,
        "timeout": 600,
        "cache_seed": 42,
    }


def _assistant(agent: AG2Agent, model: str) -> dict[str, Any]:
    return {
        "type": "assistant",
        "config": {
            "name": agent.name,
            "llm_config": _llm_config(model),
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 8,
            "system_message": agent.system_message or f"You are {agent.name}.",
        },
    }


def _userproxy() -> dict[str, Any]:
    return {
        "type": "userproxy",
        "config": {
            "name": "userproxy",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 5,
            "system_message": "",
            "llm_config": False,
            "code_execution_config": {"work_dir": None, "use_docker": False},
        },
    }


def build_ag2_workflow(
    name: str,
    description: str,
    agents: list[AG2Agent],
    *,
    model: str = "gpt-4o",
    max_round: int = 10,
) -> dict[str, Any]:
    """Build an AG2 Studio workflow JSON from a simple agent design."""
    agents = [a for a in agents if a.name.strip()]
    if not agents:
        raise AG2Error("Add at least one agent.")

    workflow: dict[str, Any] = {
        "name": name.strip() or "My Agent Workflow",
        "description": description.strip() or "Designed with the workflow factory.",
        "sender": _userproxy(),
    }

    if len(agents) == 1:
        workflow["type"] = "twoagents"
        workflow["receiver"] = _assistant(agents[0], model)
    else:
        workflow["type"] = "groupchat"
        workflow["receiver"] = {
            "type": "groupchat",
            "description": description.strip() or "A group chat workflow",
            "config": {
                "name": "group_chat_manager",
                "llm_config": _llm_config(model),
                "human_input_mode": "NEVER",
                "system_message": "Group chat manager",
            },
            "groupchat_config": {
                "admin_name": "Admin",
                "max_round": max_round,
                "speaker_selection_method": "auto",
                "agents": [_assistant(a, model) for a in agents],
            },
        }
    return workflow
