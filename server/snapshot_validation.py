"""Validate portable bank snapshots before any database is created or changed."""
from __future__ import annotations

import json

from exam_import import LETTERS, QUESTION_TYPES, expected_numbers
from question_bank import validate_entry


class SnapshotValidationError(ValueError):
    """The manifest or its referenced bank content is invalid."""


def _require(condition, message):
    if not condition:
        raise SnapshotValidationError(message)


def _json(row, key, kind):
    raw = row.get(key)
    _require(isinstance(raw, str), f'{key} must be JSON text')
    try:
        value = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise SnapshotValidationError(f'invalid {key}: {exc}') from exc
    _require(isinstance(value, kind), f'{key} has the wrong JSON structure')
    return value


def validate_snapshot(data):
    """Return actual counts after checking manifest, uniqueness and all references.

    No fixed bank size is assumed. A manifest cannot hide truncation, duplicate
    IDs/slots or malformed questions behind INSERT OR REPLACE's lossy behavior.
    """
    _require(isinstance(data, dict), 'snapshot must be an object')
    _require(data.get('format') == 'kaoyan-demo-snapshot', 'unexpected snapshot format')
    _require(type(data.get('version')) is int and data['version'] == 1,
             'unsupported snapshot version')
    names = ('passages', 'sentences', 'questions', 'breakdowns')
    counts = data.get('counts')
    _require(isinstance(counts, dict) and set(counts) == set(names), 'invalid counts manifest')
    actual = {}
    indexes = {}
    for name in names:
        rows = data.get(name)
        _require(isinstance(rows, list), f'{name} must be a list')
        actual[name] = len(rows)
        _require(type(counts[name]) is int and counts[name] >= 0 and counts[name] == len(rows),
                 f'{name} count mismatch: manifest={counts[name]!r}, actual={len(rows)}')
        index = {}
        key = 'sentence_id' if name == 'breakdowns' else 'id'
        for row in rows:
            _require(isinstance(row, dict), f'{name} rows must be objects')
            identity = row.get(key)
            _require(isinstance(identity, str) and bool(identity.strip()), f'{name}: invalid {key}')
            _require(identity not in index, f'{name}: duplicate {key} {identity}')
            index[identity] = row
        indexes[name] = index
    _require(actual['passages'] > 0, 'snapshot contains no passages')
    passages, sentences = indexes['passages'], indexes['sentences']
    slots = set()
    grouped = {pid: [] for pid in passages}
    for p in passages.values():
        _require(type(p.get('year')) is int and 2000 <= p['year'] <= 2100, 'invalid passage year')
        _require(p.get('exam_type') in ('英语一', '英语二'), 'invalid exam_type')
        _require(type(p.get('text_number')) is int and p['text_number'] in range(1, 5),
                 'invalid text_number')
        slot = (p['year'], p['exam_type'], p['text_number'])
        _require(slot not in slots, f'duplicate passage slot: {slot}')
        slots.add(slot)
        _require(type(p.get('revision', 1)) is int and p.get('revision', 1) >= 1, 'invalid revision')
        _require(isinstance(p.get('text'), str) and bool(p['text'].strip()), 'missing passage text')
        _require(isinstance(p.get('source_note'), str) and bool(p['source_note'].strip()),
                 'missing passage source_note')

    sentence_slots = set()
    for name in ('sentences', 'questions'):
        for row in data[name]:
            pid = row.get('passage_id')
            _require(isinstance(pid, str) and pid in passages, f'{name}: unknown passage reference {pid!r}')
            p = passages[pid]
            _require(all(type(row.get(k)) is type(p[k]) and row[k] == p[k]
                         for k in ('year', 'exam_type', 'text_number')),
                     f'{name}: passage metadata mismatch for {row["id"]}')
            if name == 'sentences':
                _require(isinstance(row.get('text'), str) and bool(row['text'].strip()), 'missing sentence text')
                for key in ('paragraph', 'sentence_index'):
                    _require(type(row.get(key)) is int and row[key] >= 1, f'invalid {key}')
                slot = (pid, row['paragraph'], row['sentence_index'])
                _require(slot not in sentence_slots, f'duplicate sentence position: {slot}')
                sentence_slots.add(slot)
                _require(isinstance(row.get('source_label'), str), 'invalid source_label')
                _json(row, 'grammar_tags', list)
                start, end = row.get('char_start'), row.get('char_end')
                if start is not None or end is not None:
                    _require(type(start) is int and type(end) is int and 0 <= start < end <= len(p['text']),
                             'invalid sentence offsets')
                    _require(p['text'][start:end] == row['text'], 'sentence offsets do not match text')
            else:
                sid = row.get('source_sentence_id')
                _require('source_sentence_id' in row, 'missing source_sentence_id')
                _require(sid is None or (isinstance(sid, str) and sid in sentences
                                        and sentences[sid]['passage_id'] == pid),
                         f'question {row["id"]}: invalid source sentence reference')
                _require(type(row.get('number')) is int, 'question number must be an integer')
                _require(row.get('correct_answer') in LETTERS, 'invalid correct_answer')
                _require(row.get('question_type') in QUESTION_TYPES, 'invalid question_type')
                question = {**row, 'options': _json(row, 'options_json', dict)}
                analysis, steps = _json(row, 'analysis_json', dict), _json(row, 'steps_json', list)
                if analysis:
                    question['analysis'] = analysis
                if steps:
                    question['steps'] = steps
                grouped[pid].append(question)

    for pid, p in passages.items():
        qs = grouped[pid]
        _require(len(qs) == 5 and {q['number'] for q in qs} == set(expected_numbers(p['text_number'])),
                 f'{pid}: missing or duplicate question numbers')
        _require(any(slot[0] == pid for slot in sentence_slots), f'{pid}: no sentences')
        # Reuse the same structural gate used by practice_readiness, before writes.
        try:
            validate_entry({**p, 'paragraphs': p['text'].split('\n\n'), 'questions': qs})
        except (ValueError, TypeError, KeyError) as exc:
            raise SnapshotValidationError(f'{pid}: {exc}') from exc
        for q in qs:
            _require(q.get('answer_source') in ('provided', 'manual')
                     and isinstance(q.get('answer_source_note'), str) and bool(q['answer_source_note'].strip()),
                     f'{q["id"]}: missing supplied answer provenance')
    for row in data['breakdowns']:
        _require(row['sentence_id'] in sentences, 'breakdown: unknown sentence reference')
        _json(row, 'data_json', dict)
        _require(type(row.get('llm_used')) is int and row['llm_used'] in (0, 1), 'invalid llm_used')
        _require(isinstance(row.get('created_at'), str), 'invalid breakdown created_at')
    return actual
