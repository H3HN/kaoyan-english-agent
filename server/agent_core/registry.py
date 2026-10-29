"""Tool registry: the only place intent names map to executable handlers."""
from __future__ import annotations

from typing import Callable

from . import handlers

Handler = Callable[..., dict]

TOOL_REGISTRY: dict[str, Handler] = {
    "auto_diagnosis": handlers.auto_diagnosis,
    "save_sentence": handlers.save_sentence,
    "explain_word_in_sentence": handlers.explain_word_in_sentence,
    "add_word_to_sentence": handlers.add_word_to_sentence,
    "word_insight": handlers.word_insight,
    "ad_hoc_reading": handlers.ad_hoc_reading,
    "ad_hoc_vocab": handlers.ad_hoc_vocab,
    "paragraph": handlers.paragraph,
    "ad_hoc_sentence": handlers.ad_hoc_sentence,
    "recommend": handlers.recommend,
    "summarize_content": handlers.summarize_content,
    "studio_home": handlers.studio_home,
    "listening_home": handlers.listening_home,
    "writing_home": handlers.writing_home,
    "reader_home": handlers.reader_home,
    "reading_home": handlers.reading_home,
    "vocab_home": handlers.vocab_home,
    "listening": handlers.listening,
    "writing": handlers.writing,
    "reader": handlers.reader,
    "practice": handlers.practice,
    "rare_words": handlers.rare_words,
    "batch_vocab": handlers.batch_vocab,
    "flashcard_review": handlers.flashcard_review,
    "schedule": handlers.schedule,
    "diagnosis": handlers.diagnosis,
    "similar_sentences": handlers.similar_sentences,
    "explain_sentence": handlers.explain_sentence,
    "sentence": handlers.sentence,
    "clarify": handlers.clarify,
    "generic": handlers.generic,
}
