"""Offline tests for the AG2 Studio workflow generator (matches the app.ag2.ai schema)."""

from __future__ import annotations

import pytest

from backend.ag2 import AG2Agent, AG2Error, build_ag2_workflow


def test_single_agent_is_twoagents() -> None:
    wf = build_ag2_workflow("Solo", "desc", [AG2Agent("assistant", "Be helpful.")], model="gpt-4o")
    assert wf["type"] == "twoagents"
    assert wf["sender"]["type"] == "userproxy"
    assert wf["receiver"]["type"] == "assistant"
    assert wf["receiver"]["config"]["name"] == "assistant"
    assert wf["receiver"]["config"]["system_message"] == "Be helpful."
    assert wf["receiver"]["config"]["llm_config"]["config_list"][0]["model"] == "gpt-4o"


def test_multiple_agents_is_groupchat() -> None:
    wf = build_ag2_workflow(
        "Team",
        "a team",
        [AG2Agent("planner", "Plan."), AG2Agent("writer", "Write."), AG2Agent("reviewer", "Review.")],
        model="gpt-4o-mini",
    )
    assert wf["type"] == "groupchat"
    assert wf["receiver"]["type"] == "groupchat"
    gc = wf["receiver"]["groupchat_config"]
    assert [a["config"]["name"] for a in gc["agents"]] == ["planner", "writer", "reviewer"]
    # Model propagates into every agent's llm_config.
    assert all(a["config"]["llm_config"]["config_list"][0]["model"] == "gpt-4o-mini" for a in gc["agents"])


def test_userproxy_sender_has_no_llm() -> None:
    wf = build_ag2_workflow("x", "", [AG2Agent("a", "m")])
    assert wf["sender"]["config"]["llm_config"] is False


def test_empty_agents_raises() -> None:
    with pytest.raises(AG2Error):
        build_ag2_workflow("x", "", [])
    with pytest.raises(AG2Error):
        build_ag2_workflow("x", "", [AG2Agent("   ", "")])


def test_defaults_fill_in() -> None:
    wf = build_ag2_workflow("", "", [AG2Agent("a")])
    assert wf["name"]  # a default name is provided
    assert wf["receiver"]["config"]["system_message"]  # a default system message is provided
