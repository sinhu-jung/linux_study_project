"""Offline learning room integrity and HTTP integration; no learner data writes."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_learning import build
from lesson_storage import load_lessons
from study import Handler


class LearningTest(unittest.TestCase):
    def test_offline_launcher_never_prepares_kernel_repository(self):
        spec=importlib.util.spec_from_file_location('study_launcher', ROOT / 'start-study.py')
        launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
        with patch.object(sys,'argv',['start-study.py','--offline']), \
             patch.object(launcher,'prepare',side_effect=AssertionError('Unexpected kernel download')), \
             patch('build_learning.build',return_value={'lessons':1,'questions':2}) as builder, \
             patch('webbrowser.open') as opener:
            self.assertEqual(launcher.main(),0)
            builder.assert_called_once_with(ROOT)
            opener.assert_called_once_with((ROOT / 'tools/learning.html').as_uri())

    def fixture(self, root):
        (root / 'course/lesson-parts').mkdir(parents=True)
        lesson = {'id':'one', 'questions':[{'prompt':'질문', 'options':['A','B'],
                  'answer':1, 'explanation':'B인 이유'}], 'annotated':'원본 주석'}
        (root / 'course/lesson-parts.json').write_text(json.dumps({'parts':['0001.json'],'lessons':1}), encoding='utf-8')
        (root / 'course/lesson-parts/0001.json').write_text(json.dumps([lesson]), encoding='utf-8')
        (root / 'course/foundations.json').write_text('[]', encoding='utf-8')
        return lesson

    def test_every_existing_question_and_answer_is_preserved(self):
        original = load_lessons(ROOT)
        foundations = json.loads((ROOT / 'course/foundations.json').read_text(encoding='utf-8'))
        expected = foundations + original
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'course').mkdir()
            (root / 'course/foundations.json').write_text(json.dumps(foundations), encoding='utf-8')
            with patch('build_learning.load_lessons', return_value=copy.deepcopy(original)):
                report = build(root)
            data = (root / 'data/learning-bank.js').read_text(encoding='utf-8')
            bank = json.loads(data.removeprefix('window.LEARNING_BANK = ').removesuffix(';\n'))
            for actual, source in zip(bank['lessons'], expected):
                for q in actual['questions']:
                    self.assertRegex(q.pop('fingerprint'), r'^[0-9a-f]{24}$')
                self.assertEqual(actual, source)
            self.assertEqual(len(bank['lessons']), len(expected))
            self.assertEqual(report['questions'], sum(len(l['questions']) for l in expected))
            self.assertEqual(report['missing_explanations'], 0)

    def test_invalid_answer_or_missing_explanation_rejected(self):
        for change in ({'explanation':' '}, {'answer':True}, {'answer':2}, {'options':['A']}):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as folder:
                root=Path(folder); lesson=self.fixture(root)
                lesson['questions'][0].update(change)
                (root / 'course/lesson-parts/0001.json').write_text(json.dumps([lesson]), encoding='utf-8')
                with self.assertRaises(ValueError): build(root)

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); lesson=self.fixture(root)
            (root / 'course/foundations.json').write_text(json.dumps([lesson]), encoding='utf-8')
            with self.assertRaises(ValueError): build(root)

    def test_content_change_invalidates_progress_fingerprint(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); lesson=self.fixture(root); build(root)
            before=(root / 'data/learning-bank.js').read_text(encoding='utf-8')
            lesson['questions'][0]['explanation']='새 해설'
            (root / 'course/lesson-parts/0001.json').write_text(json.dumps([lesson]), encoding='utf-8')
            build(root)
            after=(root / 'data/learning-bank.js').read_text(encoding='utf-8')
            parse=lambda text: json.loads(text.removeprefix('window.LEARNING_BANK = ').removesuffix(';\n'))['lessons'][0]['questions'][0]['fingerprint']
            self.assertNotEqual(parse(before),parse(after))

    def test_learning_routes_serve_correct_assets_and_reject_unknown_host(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            for path, mime, marker in [('/learning','text/html',b'learning.js'),('/learning.js','text/javascript',b'LEARNING_BANK'),('/data/learning-bank.js','text/javascript',b'fingerprint')]:
                conn=HTTPConnection('127.0.0.1',server.server_port)
                conn.request('GET',path);r=conn.getresponse()
                self.assertEqual(r.status,200);self.assertIn(mime,r.getheader('Content-Type'));self.assertIn(marker,r.read());conn.close()
            for path, headers, status in [('/learning',{'Host':'untrusted.example'},403),('/data/../../README.md',{},404)]:
                conn=HTTPConnection('127.0.0.1',server.server_port)
                conn.request('GET',path,headers=headers);r=conn.getresponse()
                self.assertEqual(r.status,status);r.read();conn.close()
        finally:server.shutdown();server.server_close();worker.join()


if __name__=='__main__': unittest.main()
