"""Apply individually authored editorial batches without changing source or answers.

Run after authors have saved tools/easy_batches/*.json. Existing completed lessons
are skipped; a differing previously applied row is an error, never an overwrite.
"""
import copy
import hashlib
import json
from pathlib import Path
from lesson_storage import _atomic_text, ensure_lessons_cache

ROOT = Path(__file__).resolve().parents[1]

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def apply():
    rows = {}
    batch_dir = ROOT / 'tools/easy_batches'
    paths = [batch_dir / f'{name}.json' for name in 'abcdef']
    paths += [batch_dir / 'files.json']
    paths += [batch_dir / f'files_{name}.json' for name in 'abcdef']
    for p in sorted(path for path in paths if path.exists()):
        batch = json.loads(p.read_text())
        for key, row in batch.items():
            if key in rows:
                raise ValueError('Duplicate authored ID: ' + key)
            rows[key] = (row, str(p.relative_to(ROOT)))
    containers = [(p, json.loads(p.read_text()), False) for p in sorted((ROOT/'course/lesson-parts').glob('*.json'))]
    containers += [(p, [json.loads(p.read_text())], True) for p in sorted((ROOT/'course/file-lessons').glob('*.json'))]
    found, changed = set(), []
    pending = []
    for path, lessons, single in containers:
        touched = False
        for lesson in lessons:
            key = lesson['id']
            if key not in rows:
                continue
            found.add(key)
            row, source = rows[key]
            row_digest = digest(row)
            if lesson.get('beginner'):
                review = lesson.get('easy_review', {})
                if review.get('authoring_source') == source and review.get('authoring_sha256') != row_digest:
                    raise ValueError('Previously applied row changed; review explicitly: ' + key)
                continue
            if single and len(row.get('guide', [])) < 3:
                raise ValueError('Whole-file lesson needs at least three authored sections: ' + key)
            if 'deep_dive' in row:
                sections = row['deep_dive']
                if not isinstance(sections, list) or (single and len(sections) < 3):
                    raise ValueError('Invalid authored deep sections: ' + key)
                for section in sections:
                    if not isinstance(section, dict) or any(
                        not isinstance(section.get(field), str) or not section[field].strip()
                        for field in ('title', 'text')
                    ):
                        raise ValueError('Empty authored deep section: ' + key)
            original = copy.deepcopy(lesson)
            if len(row['questions']) != len(original['questions']):
                raise ValueError('Question count changed: ' + key)
            for field in ('story', 'meaning', 'exercise'):
                if not isinstance(row[field], str) or not row[field].strip():
                    raise ValueError('Missing authored text: ' + key + '/' + field)
            if not row['guide'] or any(not isinstance(s,str) or not s.strip() for s in row['guide']):
                raise ValueError('Missing guide: ' + key)
            questions = []
            for old, new in zip(original['questions'], row['questions']):
                if len(old['options']) != len(new['options']):
                    raise ValueError('Option count changed: ' + key)
                if any(not isinstance(s,str) or not s.strip() for s in [new['prompt'],new['explanation'],*new['options']]):
                    raise ValueError('Empty question text: ' + key)
                if new['explanation'] == old['explanation']:
                    raise ValueError('Unwritten explanation: ' + key)
                q = copy.deepcopy(old)
                q.update(new)
                q['answer'] = old['answer']
                q['original_prompt'] = old['prompt']
                q['original_options'] = old['options']
                q['original_explanation'] = old['explanation']
                questions.append(q)
            lesson['technical_original'] = original
            lesson['intro'] = row['meaning']
            lesson['guide'] = row['guide']
            lesson['beginner'] = {k:row[k] for k in ('story','meaning','exercise')}
            lesson['goal'] = row.get('goal', row['meaning'])
            lesson['questions'] = questions
            # All original technical detail remains accessible under technical_original.
            lesson['concepts'] = row.get('concepts', [])
            lesson['deep_dive'] = row.get('deep_dive', [
                {'title':f'원문 읽기 {i + 1}', 'text':text}
                for i, text in enumerate(row['guide'])
            ] if single else [])
            if single and 'deep_dive' not in row:
                lesson['guide'] = [row['meaning']]
            lesson['reading_support'] = None
            lesson['experiment'] = {'title':'종이에 따라 해 보기','steps':[row['exercise']]}
            lesson.setdefault('practice', {})['expected'] = row['exercise']
            lesson['easy_review'] = {'version':1,'authoring_source':source,
                'authoring_sha256':row_digest,
                'scope':['intro','guide','questions.prompt','questions.options','questions.explanation'],
                'question_count':len(questions),'source_code_preserved':True,
                'child_comprehension_tested':False}
            changed.append(key)
            touched = True
        if touched:
            pending.append((path, lessons[0] if single else lessons))
    if found != set(rows):
        raise ValueError('Unknown IDs: ' + str(set(rows)-found))
    for path, value in pending:
        _atomic_text(path, json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    ensure_lessons_cache(ROOT)
    return {'new_lessons':len(changed),'new_ids':changed}

if __name__ == '__main__':
    print(json.dumps(apply(),ensure_ascii=False))
