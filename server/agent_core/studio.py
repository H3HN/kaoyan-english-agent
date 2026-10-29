"""Compatibility facade for Studio tools.

New code should import from ``agent_core.tools``. This module remains so
existing tests/imports keep working while the tool modules are adopted.
"""

from .tools import (
    _ad_hoc_reading,
    _ad_hoc_sentence,
    _ad_hoc_vocab,
    _batch_vocab,
    _normalize_sentence_data,
    _paragraph_insight,
    _parse_ad_hoc_options,
    _practice,
    _word_insight,
)

__all__ = [
    "_ad_hoc_reading",
    "_ad_hoc_sentence",
    "_ad_hoc_vocab",
    "_batch_vocab",
    "_normalize_sentence_data",
    "_paragraph_insight",
    "_parse_ad_hoc_options",
    "_practice",
    "_word_insight",
]
