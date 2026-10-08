"""Versioned C and OS lessons; source excerpts always come from the pinned Git tree."""
import json

class Course:
    TRACKS = {'os': 'OS 원리 · 기술 · 자료구조', 'c': '필요할 때 배우는 C 기초'}

    def __init__(self, root, connection, git, lock):
        self.root, self.connection, self.git, self.lock = root, connection, git, lock
        self.lessons = json.loads((root / 'course/lessons.json').read_text(encoding='utf-8'))
        self.ids = [lesson['id'] for lesson in self.lessons]
        with connection() as db:
            db.execute('CREATE TABLE IF NOT EXISTS course_progress(id TEXT PRIMARY KEY, passed INTEGER NOT NULL DEFAULT 0, draft TEXT NOT NULL DEFAULT \'\', answers TEXT NOT NULL DEFAULT \'[]\', updated TEXT DEFAULT CURRENT_TIMESTAMP)')

    def state(self, db, lessons):
        rows = {r[0]: {'passed': bool(r[1]), 'draft': r[2], 'answers': json.loads(r[3])} for r in db.execute('SELECT id,passed,draft,answers FROM course_progress')}
        first = next((i for i, lesson in enumerate(lessons) if not rows.get(lesson['id'], {}).get('passed')), len(lessons))
        return rows, first

    def source(self, lesson):
        if lesson['kind'] == 'kernel':
            text = self.git('show', 'HEAD:' + lesson['path']).decode()
            if 'excerpt' in lesson:
                excerpt = lesson['excerpt']
                lines = text.splitlines()
                if excerpt['anchor'] not in lines[excerpt['start']-1]:
                    raise ValueError('커널 원본과 수업의 발췌 위치가 다릅니다.')
                return '\n'.join(lines[excerpt['start']-1:excerpt['end']]) + '\n'
            return text
        return (self.root / lesson['path']).read_text(encoding='utf-8')

    def handle(self, method, route, query, payload=None):
        payload = payload or {}
        lesson_id = query.get('id') if method == 'GET' else payload.get('id')
        selected = next((l for l in self.lessons if l['id'] == lesson_id), None)
        track = selected.get('track','c') if selected else query.get('track', payload.get('track','os'))
        if track not in self.TRACKS:
            return {'error': '과정을 찾을 수 없습니다.'}, 404
        lessons = [l for l in self.lessons if l.get('track','c') == track]
        ids = [l['id'] for l in lessons]
        with self.lock, self.connection() as db:
            rows, first = self.state(db, lessons)
            if route == '/api/course' and method == 'GET':
                return {'tracks': self.TRACKS, 'track': track, 'lessons': [{'id': l['id'], 'title': l['title'], 'path': l['path'], 'area': l.get('area','OS 시작' if track=='os' else 'C 기초'), 'passed': rows.get(l['id'], {}).get('passed', False), 'locked': i > first} for i,l in enumerate(lessons)], 'current': ids[min(first, len(ids)-1)], 'completed': sum(rows.get(i, {}).get('passed', False) for i in ids), 'total': len(ids)}, 200
            if lesson_id not in ids:
                return {'error': '학습 단계를 찾을 수 없습니다.'}, 404
            index = ids.index(lesson_id)
            if index > first:
                return {'error': '앞 단계의 문제를 먼저 풀어주세요.'}, 403
            lesson = lessons[index]
            previous = rows.get(lesson_id, {'passed': False, 'draft': '', 'answers': []})
            if method == 'GET' and route == '/api/course/lesson':
                return {**{k: lesson[k] for k in ('id','title','path','kind','intro','guide')}, **{k: lesson[k] for k in ('excerpt','concepts','practice','experiment','references','goal','area','authored_topic','deep_dive','reading_support') if k in lesson}, 'track':track, 'source': self.source(lesson), 'questions': [{k: q[k] for k in ('prompt','options')} for q in lesson['questions']], 'draft': previous['draft'], 'answers': previous['answers'], 'passed': previous['passed'], 'index': index, 'total': len(ids)}, 200
            if method == 'GET' and route == '/api/course/answer':
                return {'annotated': lesson['annotated'], 'answers': [{'answer': q['answer'], 'explanation': q['explanation']} for q in lesson['questions']]}, 200
            if method == 'POST' and route in ('/api/course/draft','/api/course/check'):
                draft, answers = payload.get('draft', ''), payload.get('answers', [])
                if not isinstance(draft,str) or len(draft)>100000 or not isinstance(answers,list) or len(answers) != len(lesson['questions']):
                    return {'error': '입력 형식을 확인해주세요.'}, 400
                if any(a is not None and (type(a) is not int or not 0 <= a < len(q['options'])) for a,q in zip(answers,lesson['questions'])):
                    return {'error': '선택한 답을 확인해주세요.'}, 400
                correct = [a == q['answer'] for a,q in zip(answers, lesson['questions'])]
                passed_now = route.endswith('/check') and all(correct)
                passed = previous['passed'] or passed_now
                db.execute('INSERT INTO course_progress(id,passed,draft,answers) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET passed=excluded.passed,draft=excluded.draft,answers=excluded.answers,updated=CURRENT_TIMESTAMP', (lesson_id, int(passed), draft, json.dumps(answers)))
                if route.endswith('/draft'):
                    return {'saved': True}, 200
                return {'passed': passed, 'all_correct': passed_now, 'correct': correct, 'feedback': ['정답입니다.' if ok else ('답을 선택해주세요.' if answer is None else '설명·실험·답지를 참고해 다시 생각해보세요.') for answer,ok in zip(answers,correct)], 'next': ids[index+1] if passed and index+1 < len(ids) else None}, 200
            return {'error':'Not found'}, 404
