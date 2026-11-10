"""Deterministic synthetic fixtures only: no PDF, DB, network, or model needed."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('verify_bank_sample', Path(__file__).resolve().parents[1] / 'scripts/verify_bank_sample.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def fixture(number=21, answer='B'):
    return (f'【答案】 {answer} （细节题）\n【判型】synthetic only\n'
            f'{number}. What is the exact claim?\n'
            '[ A ] First claim\n[ B ] Second claim\n[ C ] Third claim\n[ D ] Fourth claim\n')


class SampleVerificationTests(unittest.TestCase):
    def test_explicit_whitespace_and_ligatures_only(self):
        self.assertEqual(v.normalize('a\u00a0b\nﬁ ﬂ ﬃ ﬄ ﬀ ﬅ ﬆ'), 'abfiflffifflffstst')
        self.assertNotEqual(v.normalize('A'), v.normalize('a'))
        self.assertNotEqual(v.normalize("it's"), v.normalize('it’s'))
        self.assertNotEqual(v.normalize('grid-\nbased'), v.normalize('gridbased'))
        self.assertNotEqual(v.normalize('①'), v.normalize('1'))

    def test_semantic_near_match_is_mismatch(self):
        self.assertEqual(v.comparison('workers need tips', 'workers require tips', [4])['status'], 'mismatch')
        self.assertEqual(v.comparison('do not pay', 'do pay', [4])['status'], 'mismatch')
        self.assertEqual(v.comparison('x', None, [4])['status'], 'pending')

    def test_full_stem_and_four_options_are_extracted(self):
        result = v.parse_questions(fixture())[21]
        self.assertEqual(result['content'], 'What is the exact claim?')
        self.assertEqual(result['options'], dict(zip('ABCD', ['First claim', 'Second claim', 'Third claim', 'Fourth claim'])))

    def test_unique_answer_must_bind_exact_question(self):
        text = fixture()
        original = v.parse_questions(text)[21]
        self.assertEqual(v.bind_answer(text, 21, original)['letter'], 'B')
        self.assertIsNone(v.bind_answer(text, 22, original))
        self.assertIsNone(v.bind_answer(text.replace('Second claim', 'Second altered claim'), 21, original))
        self.assertIsNone(v.bind_answer(text.replace('exact claim?', 'different claim?'), 21, original))

    def test_letter_somewhere_is_not_an_answer(self):
        original = v.parse_questions(fixture())[21]
        for text in [fixture().replace('【答案】 B （细节题）', 'B appears somewhere'),
                     fixture().replace('【答案】 B （细节题）', '【选项】 B 正确'),
                     fixture() + '\n【答案】 A （细节题）',
                     fixture() + fixture(22, 'A')]:
            self.assertIsNone(v.bind_answer(text, 21, original))

    def test_cross_page_answer_does_not_bind(self):
        original = v.parse_questions(fixture())[21]
        self.assertIsNone(v.bind_answer(fixture().split('\n', 1)[1], 21, original))
        self.assertIsNone(v.bind_answer('【答案】 B （细节题）', 21, original))

    def test_option_analysis_is_label_scoped(self):
        text = '【选项】 A) wrong\nfirst explanation\nB) ✓ 正确\nsecond explanation\nC) wrong\nthird explanation\nD) wrong\nfourth explanation'
        blocks = v.option_analysis(text)
        self.assertEqual(set(blocks), set('ABCD'))
        self.assertNotIn('second explanation', blocks['A']['explanation'])
        self.assertEqual(blocks['B']['trapType'], '正确')
        self.assertEqual(v.option_analysis('B occurs somewhere'), {})
        following = text + '\nA) next question translated choices\nnot current analysis'
        self.assertNotIn('next question', v.option_analysis(following)['D']['explanation'])
        self.assertEqual(v.option_analysis(text + '\nSENTENCE INSIGHTS\nunrelated')['D']['explanation'].strip(), 'fourth explanation')
        self.assertEqual(v.option_analysis(text.replace('C) wrong', 'B) wrong')), {})


if __name__ == '__main__':
    unittest.main()
