"""Build a portable, offline study room from every authored question."""
import hashlib
import json
from pathlib import Path
from lesson_storage import load_lessons, _atomic_text
from build_file_lessons import load_file_lessons
from reading_support import support
from build_syllabus import render_syllabus

ROOT = Path(__file__).resolve().parent.parent


def build(root=ROOT):
    lessons = load_lessons(root)
    foundations = json.loads((root / 'course/foundations.json').read_text(encoding='utf-8'))
    files = load_file_lessons(root)
    combined = foundations + lessons + files
    ids = set()
    count = 0
    for lesson in combined:
        if lesson['id'] in ids:
            raise ValueError('Duplicate lesson: ' + lesson['id'])
        ids.add(lesson['id'])
        if not lesson.get('questions'):
            raise ValueError('Empty lesson: ' + lesson['id'])
        for q in lesson['questions']:
            if (not q.get('prompt', '').strip() or not q.get('explanation', '').strip()
                    or type(q.get('answer')) is not int
                    or not 0 <= q['answer'] < len(q['options'])
                    or len(q['options']) < 2 or any(not str(o).strip() for o in q['options'])):
                raise ValueError('Invalid question: ' + lesson['id'])
            count += 1
            q['fingerprint'] = hashlib.sha256(json.dumps(
                [q['prompt'], q['options'], q['answer'], q['explanation']],
                ensure_ascii=False).encode('utf-8')).hexdigest()[:24]
    glossary, reading_audit = support(combined)
    render_syllabus(root, combined, glossary)
    # Keep authored technical material; reading support does not certify its difficulty.
    bank = {'version': 1, 'lessons': combined, 'questions': count,
            'existing_lessons': len(lessons), 'existing_questions': sum(len(l['questions']) for l in lessons),
            'foundations': len(foundations), 'whole_file_lessons':len(files)}
    bank['glossary'] = glossary
    bank['reading_audit'] = {k:v for k,v in reading_audit.items() if k not in ('lessons', 'frequent_unclassified_english_or_identifiers')}
    progress_path=root/'course/file-learning-progress.json'
    if progress_path.exists():
        progress=json.loads(progress_path.read_text(encoding='utf-8'))
        bank['file_progress']={'total':progress['tracked_files'],'authored':len(files)}
    output = root / 'data'
    output.mkdir(exist_ok=True)
    _atomic_text(output / 'learning-bank.js', 'window.LEARNING_BANK = ' + json.dumps(bank, ensure_ascii=False) + ';\n')
    report = {'lessons': len(combined), 'questions': count, 'missing_explanations': 0,
              'foundations': len(foundations), 'existing_lessons': len(lessons), 'whole_file_lessons':len(files),
              'note': 'Structural validation only; this does not certify every technical explanation.'}
    _atomic_text(output / 'learning-audit.json', json.dumps(report, ensure_ascii=False, indent=2))
    _atomic_text(output / 'reading-audit.json', json.dumps(reading_audit, ensure_ascii=False, indent=2))
    _atomic_text(root / 'course/easy-reading-progress.json', json.dumps({
        'objective':'모든 작성 수업의 설명과 문제를 초등학생이 이해할 수 있는 말로 개별 재작성',
        'total_lessons':len(combined),
        'total_questions':count,
        'remaining_questions':sum(len(l['questions']) for l in combined if not l.get('beginner')),
        'rewritten_lessons':reading_audit['introductions_and_answer_sets_rewritten'],
        'rewritten_questions':reading_audit['questions_rewritten'],
        'remaining_lessons':reading_audit['remaining_lessons_for_individual_rewrite'],
        'rewritten_ids':reading_audit['rewritten_lesson_ids'],
        'child_comprehension_tested':False,
        'complete':reading_audit['remaining_lessons_for_individual_rewrite']==0,
        'note':'용어 풀이만 추가한 수업은 재작성에 포함하지 않습니다. 개별 기술 정확성과 읽기 난이도 검토가 필요합니다.'
    },ensure_ascii=False,indent=2)+'\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), ensure_ascii=False))
