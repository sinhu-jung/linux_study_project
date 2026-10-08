#!/usr/bin/env python3
"""Versioned, resumable full checks with distinct input cases. Never semantic proof."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent

def digest():
    paths=sorted([* (ROOT/'tools').glob('*.py'),* (ROOT/'tools').glob('*.html'),
                 * (ROOT/'course').glob('*.py'),ROOT/'course/lessons.json',
                 ROOT/'course/units.json',ROOT/'tests/review_course.py'])
    h=hashlib.sha256()
    for p in paths:h.update(str(p.relative_to(ROOT)).encode());h.update(p.read_bytes())
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--rounds',type=int,default=101)
    args=parser.parse_args()
    if args.rounds<1:parser.error('--rounds must be positive')
    revision=digest()
    lesson_digest=hashlib.sha256((ROOT/'course/lessons.json').read_bytes()).hexdigest()
    folder=ROOT/'data/reviews'/revision
    folder.mkdir(parents=True,exist_ok=True)
    ledger_path=folder/'ledger.json'
    ledger=json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else {'revision':revision,'lessons_sha256':lesson_digest,'rounds':[]}
    while len(ledger['rounds'])<args.rounds:
        if digest()!=revision:raise SystemExit('교재 또는 검사 코드가 변경되어 중단했습니다. 새 버전으로 다시 실행하세요.')
        number=len(ledger['rounds'])+1
        result_path=folder/f'round-{number:03d}.json'
        env=dict(os.environ,STUDY_REVIEW_SEED=str(number),STUDY_REVIEW_REPORT=str(result_path))
        run=subprocess.run([sys.executable,str(ROOT/'tests/review_course.py')],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
        (folder/f'round-{number:03d}.log').write_text(run.stdout+run.stderr,encoding='utf-8')
        if run.returncode:print(run.stdout+run.stderr);raise SystemExit(run.returncode)
        if digest()!=revision:raise SystemExit('검사 도중 교재가 변경되어 이 회차를 완료로 기록하지 않았습니다.')
        result=json.loads(result_path.read_text(encoding='utf-8'))
        ledger['rounds'].append({'round':number,'seed':number,'checks_passed':result['automated_passed'],'completed_at':datetime.now(timezone.utc).isoformat(),'report':str(result_path.relative_to(ROOT))})
        temporary=ledger_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temporary.replace(ledger_path)
        print(f'Round {number}/{args.rounds}: {result["automated_passed"]} passed',flush=True)
    lessons=[l for l in json.loads((ROOT/'course/lessons.json').read_text(encoding='utf-8')) if l.get('track')=='os']
    result=json.loads((folder/f'round-{len(ledger["rounds"]):03d}.json').read_text(encoding='utf-8'))
    result.update(revision=revision,lessons_sha256=lesson_digest,full_suite_rounds=ledger['rounds'],
                  os_lessons=len(lessons),os_questions=sum(len(l['questions']) for l in lessons),
                  areas=len({l.get('area','OS 시작') for l in lessons}),
                  total_successful_check_executions=sum(r['checks_passed'] for r in ledger['rounds']),
                  semantic_completion=False,
                  semantic_review=f'원본·API·입력 변형 검사 {len(ledger["rounds"])}회 기록입니다. 자동 검사는 모든 기술의 해설 완성을 증명하지 않습니다.')
    (ROOT/'data/review-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'검사 기록: {ledger_path.relative_to(ROOT)}')
if __name__=='__main__':main()
