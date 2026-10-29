"""Agent turn orchestration: plan once, dispatch through the tool registry."""
from __future__ import annotations

import sqlite3
from typing import Any

from .context import _ctx
from .intent_llm import infer_intent
from .planner import plan_turn
from .registry import TOOL_REGISTRY


def run_agent_turn(
    conn: sqlite3.Connection,
    message: str,
    client_context: dict[str, Any] | None,
    trigger_mode: str = "USER_CHAT",
) -> dict[str, Any]:
    ctx = _ctx(client_context)
    planned = plan_turn(message, ctx, trigger_mode)
    intent = None
    if trigger_mode == "USER_CHAT":
        intent = infer_intent(message, ctx)
    if intent is None:
        intent = planned
    elif intent.name in {"generic", "clarify"} and planned.name not in {"generic", "clarify"}:
        # The LLM is allowed to choose the skill, but a concrete deterministic
        # action wins over an unnecessary generic/clarify fallback.
        intent = planned
    handler = TOOL_REGISTRY.get(intent.name, TOOL_REGISTRY["generic"])
    return handler(conn, message, ctx, intent)
