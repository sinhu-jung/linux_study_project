"""Guard editorial scope and ensure assistance never rewrites source or answers."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from reading_support import support, matcher
from beginner_foundations import apply, ROWS, PROMPTS
from lesson_storage import load_lessons


class ReadingSupportTest(unittest.TestCase):
    def test_individual_rewrites_preserve_questions_source_and_scope(self):
        lessons = [l for l in load_lessons(ROOT) if l.get('easy_review')]
        self.assertGreaterEqual(len(lessons),21)
        for l in lessons:
            old = l['technical_original']
            self.assertEqual(l['annotated'],old['annotated'])
            self.assertEqual(l['path'],old['path'])
            self.assertEqual(len(l['questions']),len(old['questions']))
            self.assertEqual(l['easy_review']['question_count'],len(l['questions']))
            for q,oq in zip(l['questions'],old['questions']):
                self.assertEqual(q['answer'],oq['answer'])
                self.assertEqual(q['original_options'],oq['options'])
                self.assertEqual(q['original_prompt'],oq['prompt'])
                self.assertEqual(q['original_explanation'],oq['explanation'])
                self.assertNotEqual(q['explanation'],oq['explanation'])
                self.assertTrue(q['explanation'].strip())
            for key in ('story','meaning','exercise'):
                self.assertTrue(l['beginner'][key].strip())

    def test_exact_english_identifiers_and_korean_inflections(self):
        p = matcher('IRQ|포인터')
        self.assertTrue(p.search('IRQ와 포인터를 읽어요'))
        self.assertFalse(p.search('my_IRQ_handler'))
        self.assertTrue(p.search('포인터를'))

    def test_support_preserves_all_authored_data_and_audits_each_question(self):
        a = [{'id':'sample','intro':'IRQ 포인터 ' + '긴문장'*50,
              'annotated':'IRQ raw_code <script>',
              'questions':[{'prompt':'메모리는 무엇인가?', 'options':['A','B'], 'answer':1,
                            'explanation':'포인터는 주소입니다.'}]}]
        original = copy.deepcopy(a)
        glossary, report = support(a)
        self.assertTrue(a[0].pop('reading_aid')['terms'])
        self.assertEqual(a, original)
        self.assertEqual(report['questions_checked'], 1)
        self.assertEqual(report['remaining_lessons_for_individual_rewrite'], 1)
        self.assertEqual(report['child_comprehension_tested'], 0)
        self.assertEqual(report['sentences_over_100_characters'], 1)
        self.assertNotIn('raw_code', report['lessons'][0]['unclassified_english_or_identifiers'])

    def test_all_foundations_have_authored_help_and_rebuild_is_idempotent(self):
        a = json.loads((ROOT/'course/foundations.json').read_text(encoding='utf-8'))
        self.assertEqual(len(a),30)
        self.assertEqual(len(ROWS),len(PROMPTS))
        before = copy.deepcopy(a)
        apply(a)
        self.assertEqual(a,before)
        for lesson in a:
            for key in ('story','meaning','exercise'):
                self.assertTrue(lesson['beginner'][key].strip())
            for q in lesson['questions']:
                self.assertTrue(q['original_prompt'])
                self.assertTrue(q['original_explanation'])
                self.assertIn(q['answer'],range(len(q['options'])))


if __name__ == '__main__': unittest.main()
