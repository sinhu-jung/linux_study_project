"""Fresh checkout and round-trip checks without touching learner progress."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from lesson_storage import load_lessons, write_lessons, ensure_lessons_cache

class LessonStorageTest(unittest.TestCase):
    def test_fresh_checkout_matches_existing_course(self):
        expected = json.loads((ROOT / 'course/lessons.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'course').mkdir()
            shutil.copy(ROOT / 'course/lesson-parts.json', root / 'course')
            shutil.copytree(ROOT / 'course/lesson-parts', root / 'course/lesson-parts')
            self.assertFalse((root / 'course/lessons.json').exists())
            self.assertEqual(load_lessons(root), expected)
            cache = ensure_lessons_cache(root)
            self.assertEqual(cache.read_bytes(), (ROOT / 'course/lessons.json').read_bytes())
            stamp = cache.stat().st_mtime_ns
            ensure_lessons_cache(root)
            self.assertEqual(cache.stat().st_mtime_ns, stamp)

    def test_parts_remain_authoritative_and_shrink(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [{'id': str(i), 'text': '한글 해설'} for i in range(101)]
            write_lessons(root, rows)
            self.assertEqual(len(list((root / 'course/lesson-parts').glob('*.json'))), 3)
            (root / 'course/lessons.json').write_text('[]', encoding='utf-8')
            self.assertEqual(load_lessons(root), rows)
            write_lessons(root, rows[:2])
            self.assertEqual(len(list((root / 'course/lesson-parts').glob('*.json'))), 1)
            self.assertEqual(load_lessons(root), rows[:2])

if __name__ == '__main__':
    unittest.main()
