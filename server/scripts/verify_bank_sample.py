#!/usr/bin/env python3
"""Read-only, offline verification of the fixed 2025 English-II 20-question sample.

Writes only the requested JSON/Markdown reports; never changes the bank or DB.
Exit 0 = no mismatch (pending is NOT approval); exit 1 = mismatch; exit 2 = error.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = Path('D:/DSH/DSH Workplace/课程与项目/考研英语Agent/考研英语Agent/kaoyan-review/bank-batch-20261025/2025-en2/source.pdf')
LIGATURES = str.maketrans({'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl', 'ﬅ': 'st', 'ﬆ': 'st'})
QUESTION = re.compile(r'(?m)^(2[1-9]|3[0-9]|40)\.\s+(.+?)(?=\n\[\s*A\s*\])', re.S)
ANSWER = re.compile(r'【答案】\s*([ABCD])\s*（[^）]+）')
FOOTER = re.compile(r'(?m)^懒笔记.*$')


def normalize(value: str) -> str:
    """Delete Unicode whitespace and expand only the seven listed ligatures.

    No case folding, punctuation replacement, dehyphenation, Unicode NFKC,
    spelling correction, semantic equivalence, or fuzzy matching.
    """
    return re.sub(r'\s+', '', value.translate(LIGATURES))


def clean_page(text: str) -> str:
    return FOOTER.sub('', text)


def parse_questions(text: str) -> dict:
    """Parse numbered question + four bracket-labelled options, never bare letters."""
    found = {}
    matches = list(QUESTION.finditer(text))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[match.end():end]
        block = re.split(r'(?m)^(?:Text [1-4]|Part B|Five Steps)', block)[0]
        options = list(re.finditer(r'\[\s*([ABCD])\s*\]\s*', block))
        if [m.group(1) for m in options] != list('ABCD'):
            continue
        found[int(match.group(1))] = {
            'content': match.group(2).strip(),
            'options': {m.group(1): block[m.end():options[j + 1].start() if j < 3 else len(block)].strip()
                        for j, m in enumerate(options)},
        }
    return found


def comparison(expected: str, actual: str | None, pages: list[int]) -> dict:
    if actual is None:
        return {'status': 'pending', 'pages': pages, 'reason': 'No uniquely scoped extraction'}
    a, b = normalize(expected), normalize(actual)
    result = {'status': 'match' if a == b else 'mismatch', 'pages': pages,
              'snapshot_normalized_sha256': hashlib.sha256(a.encode()).hexdigest(),
              'source_normalized_sha256': hashlib.sha256(b.encode()).hexdigest()}
    if a != b:
        pos = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        result.update(first_difference=pos, snapshot_excerpt=a[max(0, pos-35):pos+65],
                      source_excerpt=b[max(0, pos-35):pos+65])
    return result


def bind_answer(text: str, number: int, original: dict) -> dict | None:
    """Conservative page binding: exactly one question AND one explicit answer label.

    The full numbered stem and all four options must equal the original exam
    extraction on that page. Ambiguous or cross-page layouts remain pending.
    """
    questions = parse_questions(text)
    labels = list(ANSWER.finditer(text))
    if set(questions) != {number} or len(labels) != 1:
        return None
    candidate = questions[number]
    if normalize(candidate['content']) != normalize(original['content']):
        return None
    if any(normalize(candidate['options'][k]) != normalize(original['options'][k]) for k in 'ABCD'):
        return None
    label = labels[0]
    return {'letter': label.group(1), 'start': label.start(), 'label': label.group(0)}


def option_analysis(segment: str) -> dict:
    """Extract only the labelled option-analysis section of a bounded answer block."""
    if '【选项】' not in segment:
        return {}
    body = segment.split('【选项】', 1)[1].lstrip()
    labels = list(re.finditer(r'(?m)^([ABCD])\)\s*(?:✓\s*)?([^\n]+)\n', body))
    if [m.group(1) for m in labels[:4]] != list('ABCD'):
        return {}
    # The next translated question can introduce another A) line before its
    # answer label. Never consume that next set as this question's analysis.
    end = labels[4].start() if len(labels) > 4 else len(body)
    end = min(end, body.find('SENTENCE INSIGHTS') if 'SENTENCE INSIGHTS' in body else len(body))
    return {m.group(1): {'trapType': m.group(2).strip(),
                       'explanation': body[m.end():labels[i+1].start() if i < 3 else end]}
            for i, m in enumerate(labels[:4])}


def verify(snapshot: Path, source: Path) -> dict:
    from pypdf import PdfReader
    raw = snapshot.read_bytes()
    data = json.loads(raw)
    reader = PdfReader(source)
    pages = {i+1: clean_page(p.extract_text() or '') for i, p in enumerate(reader.pages)}
    selected = sorted((p for p in data['passages'] if p['year'] == 2025 and p['exam_type'] == '英语二'), key=lambda p: p['text_number'])
    if len(selected) != 4 or len(reader.pages) != 144:
        raise ValueError('Expected four passages and 144 physical PDF pages')
    # Original exam pages, NOT the bilingual explanation section. The PDF text
    # order places the next passage before the preceding passage's questions.
    passage_sources = [
        (pages[4].split('(40 points)\n', 1)[1].split('Section II Reading Comprehension', 1)[0], [4]),
        (pages[5].split('22. Compared', 1)[0] + pages[6].split('Heat action plans, or HAPs', 1)[0], [5, 6]),
        ('Heat action plans, or HAPs' + pages[6].split('Heat action plans, or HAPs', 1)[1].split('26. According', 1)[0] + pages[7].split('31. According', 1)[0], [6, 7]),
        (pages[8].split('34. Kotharkar', 1)[0], [8]),
    ]
    original = {}
    question_pages = {}
    for page in range(4, 10):
        for number, q in parse_questions(pages[page]).items():
            if number in original:
                raise ValueError('Duplicate original question')
            original[number] = q
            question_pages[number] = page
    if set(original) != set(range(21, 41)):
        raise ValueError('Could not extract exactly original questions 21–40')
    results = []
    for passage, (text, pp) in zip(selected, passage_sources):
        passage_check = comparison(passage['text'].replace('\\n', '\n'), text, pp)
        qs = sorted((q for q in data['questions'] if q['passage_id'] == passage['id']), key=lambda q: q['number'])
        if len(qs) != 5:
            raise ValueError('Expected five questions per passage')
        for q in qs:
            n = q['number']
            orig = original[n]
            checks = {'passage': passage_check,
                      'question': comparison(q['content'], orig['content'], [question_pages[n]]),
                      'options': {k: comparison(json.loads(q['options_json'])[k], orig['options'][k], [question_pages[n]]) for k in 'ABCD'}}
            # Independently scan only the passage's explanation pages, without
            # trusting source_note, answer_source_note or snapshot key letters.
            start, end = [(42, 48), (56, 62), (71, 77), (85, 91)][passage['text_number']-1]
            candidates = [(p, b) for p in range(start, end+1) if (b := bind_answer(pages[p], n, orig))]
            evidence = {'pages_with_numbered_question': [p for p in range(start, end+1) if n in parse_questions(pages[p])],
                        'explicit_answer_labels': [{'page': p, 'labels': [m.group(0) for m in ANSWER.finditer(pages[p])]} for p in range(start, end+1) if n in parse_questions(pages[p])]}
            evidence['adjacent_page_answer_labels'] = [
                {'page': p + 1, 'labels': [m.group(0) for m in ANSWER.finditer(pages.get(p + 1, ''))]}
                for p in evidence['pages_with_numbered_question']]
            analysis = {}
            if len(candidates) == 1:
                ap, binding = candidates[0]
                checks['answer'] = {'status': 'match' if q['correct_answer'] == binding['letter'] else 'mismatch',
                                    'pages': [ap], 'snapshot': q['correct_answer'], 'source': binding['letter'],
                                    'evidence': binding['label'], 'binding': 'unique numbered full stem + all four options + unique explicit answer on same page'}
                segment = pages[ap][binding['start']:] + '\n' + pages.get(ap+1, '')
                # Stop before the next explicit answer; never search the whole PDF.
                next_label = ANSWER.search(segment, len(binding['label']))
                if next_label:
                    segment = segment[:next_label.start()]
                analysis = option_analysis(segment)
                analysis_pages = [ap, ap+1]
            else:
                checks['answer'] = {'status': 'pending', 'pages': evidence['pages_with_numbered_question'],
                                    'reason': 'No unique same-page question/answer binding; cross-page or multiple-answer layout', 'evidence': evidence}
                analysis_pages = evidence['pages_with_numbered_question']
            checks['analysis'] = {}
            for k, value in json.loads(q['analysis_json']).items():
                if k not in analysis:
                    check = {'status': 'pending', 'pages': analysis_pages, 'reason': 'No unambiguous answer-bound option analysis block'}
                else:
                    # Full explanation, not an isolated quote or keyword, must
                    # occur in the correct option's scoped analysis block.
                    expected = normalize(value['explanation'])
                    match = bool(expected) and expected in normalize(analysis[k]['explanation']) and normalize(value['trapType']) == normalize(analysis[k]['trapType'])
                    check = {'status': 'match' if match else 'pending', 'pages': analysis_pages,
                             'method': 'full normalized explanation contained in answer-bound labelled option block; exact trapType',
                             'reason': 'Full text found' if match else 'Full explanation/trapType not established; no semantic judgement'}
                checks['analysis'][k] = check
            leaves = [checks['passage'], checks['question'], checks['answer'], *checks['options'].values(), *checks['analysis'].values()]
            status = 'mismatch' if any(c['status'] == 'mismatch' for c in leaves) else 'pending' if any(c['status'] == 'pending' for c in leaves) else 'match'
            results.append({'id': q['id'], 'number': n, 'passage_id': passage['id'], 'status': status, 'checks': checks})
    if snapshot.read_bytes() != raw:
        raise ValueError('Snapshot changed during verification')
    return {'schema': 'bank-sample-verification-v1', 'sample': '2025 英语二 / four passages / questions 21–40',
            'source': {'path': str(source.resolve()), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'physical_pages': len(reader.pages), 'extractor': 'pypdf', 'extractor_version': __import__('pypdf').__version__},
            'snapshot': {'path': 'server/data/demo_snapshot.json', 'sha256': hashlib.sha256(raw).hexdigest(), 'counts': data['counts']},
            'policy': {'normalization': 'Remove Unicode whitespace; expand ﬀ ﬁ ﬂ ﬃ ﬄ ﬅ ﬆ only. Decode literal \\n in snapshot passage as line breaks. No punctuation/case/fuzzy/semantic normalization.',
                       'approval': 'NOT teacher/manual approved; matches mean source transcription consistency only, not correctness of source explanations.',
                       'not_checked': ['steps_json', 'pedagogical validity', 'copyright/license', 'visual glyph correctness beyond extracted text'],
                       'pending': 'Unestablished evidence is pending, never approved. Original question content and explanation-section answers are independently extracted.'},
            'summary': {s: sum(r['status'] == s for r in results) for s in ('match', 'mismatch', 'pending')},
            'check_totals': {
                field: dict(Counter(check['status'] for r in results for check in
                           (list(r['checks'][field].values()) if field in ('options', 'analysis') else [r['checks'][field]])))
                for field in ('passage', 'question', 'options', 'answer', 'analysis')},
            'questions': results}


def markdown(report: dict) -> str:
    lines = ['# 2025 英语二：20 题来源核验', '', '**NOT teacher/manual approved.** 离线确定性文字核验，不代表教学审核或对来源答案的学术认可。', '',
             f"- Source SHA-256: `{report['source']['sha256']}`; physical pages: {report['source']['physical_pages']}",
             f"- Snapshot SHA-256: `{report['snapshot']['sha256']}` (read-only; 72 passages / 360 questions)",
             f"- Extractor: pypdf {report['source']['extractor_version']}",
             '- Page numbers below are 1-based physical PDF pages, not printed page labels.',
             '- Normalization: ' + report['policy']['normalization'],
             '- Passage text comes from original exam pp.4–8; questions/options pp.4–9. Answer/analysis pages are separately scoped.',
             '- Q31 has a cross-page layout: numbered question on p.72, two explicit answer labels on p.73. Conservative same-page binding leaves Q31 and Q32 answer/analysis pending. Q31 evidence records the adjacent p.73 labels explicitly.',
             '- Analysis checks require the ENTIRE stored explanation within its own answer-bound A/B/C/D block plus exact trapType; never an isolated keyword/letter.',
             '- Pending analysis is absence of robust literal verification, not proof of an incorrect explanation. JSON includes per-option details and text-difference excerpts where applicable.',
             '- Not checked: ' + ', '.join(report['policy']['not_checked']), '',
             '## Actual results', '', f"Question totals: `{json.dumps(report['summary'], sort_keys=True)}`", '',
             '- Per-field totals (passage checks repeated for each question):',
             '```json', json.dumps(report['check_totals'], ensure_ascii=False, sort_keys=True, indent=2), '```', '',
             '| Q | Passage (pages) | Stem | Options A/B/C/D | Answer (pages) | Analysis A/B/C/D | Overall |', '|---|---|---|---|---|---|---|']
    for q in report['questions']:
        c = q['checks']
        lines.append(f"| {q['number']} | {c['passage']['status']} {c['passage']['pages']} | {c['question']['status']} | {'/'.join(v['status'] for v in c['options'].values())} | {c['answer']['status']} {c['answer']['pages']} | {'/'.join(v['status'] for v in c['analysis'].values())} | {q['status']} |")
    lines += ['', '## Reproduce', '', 'Run from the repository root with the existing pypdf interpreter:', '', '```bash', '"D:/DSH/DSH Workplace/课程与项目/考研英语Agent/考研英语Agent/kaoyan-venv/Scripts/python.exe" server/scripts/verify_bank_sample.py', '"D:/DSH/DSH Workplace/课程与项目/考研英语Agent/考研英语Agent/kaoyan-venv/Scripts/python.exe" -m unittest discover -s server/tests -p test_bank_sample.py -v', '```', '', 'No network/model/API calls. No source PDF or source text dump is written. JSON output is deterministic for identical source, snapshot and extractor version. Exit 1 indicates a literal mismatch; pending alone is exit 0, never approval.']
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--snapshot', type=Path, default=ROOT / 'server/data/demo_snapshot.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/quality/sample-2025-en2.json')
    args = parser.parse_args()
    report = verify(args.snapshot, args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.output.with_suffix('.md').write_text(markdown(report), encoding='utf-8')
    print(json.dumps(report['summary'], sort_keys=True))
    return int(bool(report['summary'].get('mismatch')))


if __name__ == '__main__':
    raise SystemExit(main())
