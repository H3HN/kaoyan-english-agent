"""Shared Agent/Cavas contracts.

These models are the single backend source of truth for the payloads the
frontend consumes. Tools may still return plain dicts, but canvas commands
must pass through these models before reaching the HTTP response.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CanvasUnit(BaseModel):
    id: str
    tier: Literal[
        "word", "phrase", "sentence", "paragraph", "plan", "vocab", "reading", "listening", "writing", "reader", "home"
    ]
    label: str
    data: dict[str, Any]
    saved: bool = False
    examSentenceId: str | None = None


class CanvasCommand(BaseModel):
    op: Literal["replace", "push", "update"] = "replace"
    unit: CanvasUnit


class CanvasAction(BaseModel):
    action_type: Literal["APPLY_CANVAS_COMMAND"] = "APPLY_CANVAS_COMMAND"
    payload: CanvasCommand


class TurnIntent(BaseModel):
    name: str
    payload: dict[str, Any] = Field(default_factory=dict)
