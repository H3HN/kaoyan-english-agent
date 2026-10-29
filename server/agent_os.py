"""Compatibility facade for tests and older imports.

The implementation lives in :mod:`agent_core`. New code should import from
``agent_core.orchestrator`` or the specific tool module.
"""
from agent_core.orchestrator import run_agent_turn
from agent_core.studio import _parse_ad_hoc_options
from agent_core.text import _external_english

__all__ = ["run_agent_turn", "_external_english", "_parse_ad_hoc_options"]
