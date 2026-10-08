#!/usr/bin/env python3
"""Track open authoring work without turning source inventories into lessons.

Linked means one lesson refers to a file; it never means the file's entire
implementation has been explained. Completion requires explicit review evidence.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from lesson_storage import ensure_lessons_cache
ROOT = Path(__file__).resolve().parent.parent
GIT = os.environ.get('STUDY_GIT', '/opt/homebrew/bin/git' if Path('/opt/homebrew/bin/git').exists() else 'git')

def build():
    ensure_lessons_cache(ROOT)
    git = lambda *args: subprocess.check_output([GIT, '-C', str(ROOT/'linux'), *args])
    sha = git('rev-parse', 'HEAD').decode().strip()
    files = git('ls-tree','-r','--name-only','-z','HEAD').decode().split('\0')[:-1]
    lessons = [l for l in json.loads((ROOT/'course/lessons.json').read_text(encoding='utf-8')) if l.get('track')=='os']
    links = {}
    for lesson in lessons:
        links.setdefault(lesson['path'], []).append(lesson['id'])
    reviews_path = ROOT/'course/source_reviews.json'
    reviews = json.loads(reviews_path.read_text(encoding='utf-8')) if reviews_path.exists() else {}
    audit = []
    for path in files:
        record = reviews.get(path, {})
        # No automatic path/type exemptions; exclusions must be explained.
        evidence = record.get('evidence', [])
        reviewed = bool(record.get('sha') == sha and evidence and record.get('decision') in ('explained','noninstructional'))
        audit.append({'path': path, 'lessons': links.get(path, []),
                      'status': record['decision'] if reviewed else 'linked' if path in links else 'pending',
                      'evidence': evidence if reviewed else []})
    (ROOT/'course/source-audit.json').write_text(json.dumps({'sha':sha, 'files':audit,
        'note':'수업 연결과 파일 전체 검토를 구분합니다. linked는 전체 해설 완료가 아닙니다.'}, ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    planned_path = ROOT/'course/planned_topics.json'
    planned = json.loads(planned_path.read_text(encoding='utf-8')) if planned_path.exists() else []
    ready_by_title = {l['title']:l for l in lessons}
    requirements = []
    for lesson in lessons:
        requirements.append({'key':lesson['id'], 'title':lesson['title'], 'area':lesson.get('area','OS 시작'),
            'source':lesson['path'], 'lessons':[lesson['id']], 'status':'authored',
            'verification':'원본·내용 구조·문제·답지 검사. 의미 검토는 별도 증거로 관리.'})
    for item in planned:
        ready = ready_by_title.get(item['title'])
        if not ready:
            requirements.append({**item,'lessons':[],'status':'pending'})
    (ROOT/'course/requirements.json').write_text(json.dumps({'sha':sha,'items':requirements},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    groups = {}
    for item in audit:
        parts = item['path'].split('/')
        group = '/'.join(parts[:2]) if len(parts)>2 else parts[0]
        counts = groups.setdefault(group, {'files':0,'linked':0,'reviewed':0})
        counts['files']+=1
        counts['linked']+=bool(item['lessons'])
        counts['reviewed']+=item['status'] in ('explained','noninstructional')
    current_digest=hashlib.sha256((ROOT/'course/lessons.json').read_bytes()).hexdigest()
    summary={'sha':sha,'curriculum_sha256':current_digest,'authored_lessons':len(lessons),
        'authored_questions':sum(len(l['questions']) for l in lessons),
        'identified_pending_topics':sum(i['status']=='pending' for i in requirements),
        'tracked_files':len(audit),'linked_files':len(links),'reviewed_files':sum(g['reviewed'] for g in groups.values()),
        'source_groups':groups,'completion':False,
        'completion_requirements':['식별한 미작성 주제 0개','모든 원본 경로의 명시적인 내용 검토 또는 비학습 자료 판정과 증거','해설·원리·사용법·문제·풀이 검사','현재 교재 버전에 대한 전체 검수 101회 이상']}
    (ROOT/'data/coverage-audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{len(lessons)} lessons; {summary['identified_pending_topics']} explicitly pending topics; {summary['reviewed_files']}/{len(audit)} files fully reviewed")
    return summary

if __name__=='__main__':build()
