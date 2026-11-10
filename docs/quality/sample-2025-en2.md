# 2025 英语二：20 题来源核验

**NOT teacher/manual approved.** 离线确定性文字核验，不代表教学审核或对来源答案的学术认可。

- Source SHA-256: `02766ba3ffa1de0c3c5f7c48b266ec83cf17cd5ba3bf7a86700a3f8f8dba80cf`; physical pages: 144
- Snapshot SHA-256: `e3de672d02ffc936724ecd2524c10afaf34787b161e9a233f3322fc8a8374459` (read-only; 72 passages / 360 questions)
- Extractor: pypdf 6.21.2
- Page numbers below are 1-based physical PDF pages, not printed page labels.
- Normalization: Remove Unicode whitespace; expand ﬀ ﬁ ﬂ ﬃ ﬄ ﬅ ﬆ only. Decode literal \n in snapshot passage as line breaks. No punctuation/case/fuzzy/semantic normalization.
- Passage text comes from original exam pp.4–8; questions/options pp.4–9. Answer/analysis pages are separately scoped.
- Q31 has a cross-page layout: numbered question on p.72, two explicit answer labels on p.73. Conservative same-page binding leaves Q31 and Q32 answer/analysis pending. Q31 evidence records the adjacent p.73 labels explicitly.
- Analysis checks require the ENTIRE stored explanation within its own answer-bound A/B/C/D block plus exact trapType; never an isolated keyword/letter.
- Pending analysis is absence of robust literal verification, not proof of an incorrect explanation. JSON includes per-option details and text-difference excerpts where applicable.
- Not checked: steps_json, pedagogical validity, copyright/license, visual glyph correctness beyond extracted text

## Actual results

Question totals: `{"match": 18, "mismatch": 0, "pending": 2}`

- Per-field totals (passage checks repeated for each question):
```json
{
  "analysis": {
    "match": 72,
    "pending": 8
  },
  "answer": {
    "match": 18,
    "pending": 2
  },
  "options": {
    "match": 80
  },
  "passage": {
    "match": 20
  },
  "question": {
    "match": 20
  }
}
```

| Q | Passage (pages) | Stem | Options A/B/C/D | Answer (pages) | Analysis A/B/C/D | Overall |
|---|---|---|---|---|---|---|
| 21 | match [4] | match | match/match/match/match | match [43] | match/match/match/match | match |
| 22 | match [4] | match | match/match/match/match | match [44] | match/match/match/match | match |
| 23 | match [4] | match | match/match/match/match | match [45] | match/match/match/match | match |
| 24 | match [4] | match | match/match/match/match | match [46] | match/match/match/match | match |
| 25 | match [4] | match | match/match/match/match | match [47] | match/match/match/match | match |
| 26 | match [5, 6] | match | match/match/match/match | match [57] | match/match/match/match | match |
| 27 | match [5, 6] | match | match/match/match/match | match [58] | match/match/match/match | match |
| 28 | match [5, 6] | match | match/match/match/match | match [59] | match/match/match/match | match |
| 29 | match [5, 6] | match | match/match/match/match | match [60] | match/match/match/match | match |
| 30 | match [5, 6] | match | match/match/match/match | match [61] | match/match/match/match | match |
| 31 | match [6, 7] | match | match/match/match/match | pending [72] | pending/pending/pending/pending | pending |
| 32 | match [6, 7] | match | match/match/match/match | pending [73] | pending/pending/pending/pending | pending |
| 33 | match [6, 7] | match | match/match/match/match | match [74] | match/match/match/match | match |
| 34 | match [6, 7] | match | match/match/match/match | match [75] | match/match/match/match | match |
| 35 | match [6, 7] | match | match/match/match/match | match [76] | match/match/match/match | match |
| 36 | match [8] | match | match/match/match/match | match [86] | match/match/match/match | match |
| 37 | match [8] | match | match/match/match/match | match [87] | match/match/match/match | match |
| 38 | match [8] | match | match/match/match/match | match [88] | match/match/match/match | match |
| 39 | match [8] | match | match/match/match/match | match [89] | match/match/match/match | match |
| 40 | match [8] | match | match/match/match/match | match [90] | match/match/match/match | match |

## Reproduce

Run from the repository root with the existing pypdf interpreter:

```bash
"D:/DSH/DSH Workplace/课程与项目/考研英语Agent/考研英语Agent/kaoyan-venv/Scripts/python.exe" server/scripts/verify_bank_sample.py
"D:/DSH/DSH Workplace/课程与项目/考研英语Agent/考研英语Agent/kaoyan-venv/Scripts/python.exe" -m unittest discover -s server/tests -p test_bank_sample.py -v
```

No network/model/API calls. No source PDF or source text dump is written. JSON output is deterministic for identical source, snapshot and extractor version. Exit 1 indicates a literal mismatch; pending alone is exit 0, never approval.
