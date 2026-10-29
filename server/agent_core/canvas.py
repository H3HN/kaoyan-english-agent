import hashlib
import json
from typing import Any

def _canvas_unit(
    tier: str,
    data: dict[str, Any],
    label: str,
    *,
    saved: bool = False,
    exam_sentence_id: str | None = None,
) -> dict[str, Any]:
    from .contracts import CanvasUnit

    digest = hashlib.sha1(
        json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:12]
    return CanvasUnit(
        id=f"{tier}-{digest}",
        tier=tier,
        label=label,
        data=data,
        saved=saved,
        examSentenceId=exam_sentence_id,
    ).model_dump()


def _canvas_action(
    tier: str,
    data: dict[str, Any],
    label: str,
    *,
    saved: bool = False,
    exam_sentence_id: str | None = None,
) -> dict[str, Any]:
    from .contracts import CanvasAction, CanvasCommand, CanvasUnit

    return CanvasAction(
        payload=CanvasCommand(
            op="replace",
            unit=CanvasUnit(
                **_canvas_unit(
                    tier,
                    data,
                    label,
                    saved=saved,
                    exam_sentence_id=exam_sentence_id,
                )
            ),
        )
    ).model_dump()
