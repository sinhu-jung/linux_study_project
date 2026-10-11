"""Materialize individually authored whole-file lessons from a pinned Git tree."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from lesson_storage import _atomic_text

ROOT = Path(__file__).resolve().parents[1]
SHA = 'adc218676eef25575469234709c2d87185ca223a'


def build(root=ROOT):
    git = os.environ.get('STUDY_GIT', 'git')
    run = lambda *args: subprocess.check_output([git, '-C', str(root/'linux'), *args])
    if run('rev-parse', 'HEAD').decode().strip() != SHA:
        raise ValueError('Expected pinned Linux v6.12 source')
    paths, ids, manifest = set(), set(), []
    for unit_path in sorted((root/'course/file_units').glob('*.py')):
        spec=importlib.util.spec_from_file_location(unit_path.stem,unit_path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for row in module.ROWS:
            path=row['path']
            if path in paths: raise ValueError('Duplicate file lesson: '+path)
            paths.add(path)
            source=run('show', SHA+':'+path).decode('utf-8')
            file_id='file-'+hashlib.sha256(path.encode()).hexdigest()[:16]
            if file_id in ids: raise ValueError('File lesson ID collision')
            ids.add(file_id)
            questions=[]
            for index,(prompt,correct,wrong,explanation) in enumerate(row['questions']):
                options=[correct,wrong] if index%2==0 else [wrong,correct]
                questions.append(dict(prompt=prompt,options=options,answer=options.index(correct),explanation=explanation))
            sections=[{'title':title,'text':body} for title,body in row['sections']]
            lesson=dict(id=file_id,path=path,title=row['title'],area=row.get('area','CRC · 비트 연산 · 오류 검출'),
                track='files',kind='kernel',intro=row['intro'],
                guide=[row['principle'],row['use']],deep_dive=sections,questions=questions,
                concepts=[{'title':'파일 전체를 읽는 순서','text':'아래 전체 해설과 원본을 함께 읽고 선언·데이터·함수·메타데이터를 구분합니다.'}],
                practice={'command':'본문의 숫자 예제를 먼저 계산하고 원본의 표 인덱스·중간 상태·최종 반환값을 대조하세요.',
                          'expected':'계산 단계와 경계 조건은 파일 전체 해설과 문제별 풀이에 제시되어 있습니다. CRC 묶음의 표 전체 검산은 tests/test_crc_file_lessons.py로 재현하며 일반 파일은 명시된 소스 분기와 대조합니다.'},
                annotated=source,
                source_review={'sha':SHA,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
                    'scope':'whole-file','line_count':len(source.splitlines()),
                    'authoring_source':str(unit_path.relative_to(root)).replace('\\','/'),
                    'sections':[s['title'] for s in sections],
                    'verification':'파일 전체를 읽고 데이터·정의·선언·메타데이터와 경계 조건을 개별 작성. source_sha256은 원본 동일성을 검사하며 실행 정확성이나 의미 완전성의 자동 증명이 아님.'},
                references=[{'title':'고정 버전 전체 원본','url':f'https://github.com/torvalds/linux/blob/{SHA}/{path}'}])
            name=file_id+'.json'
            _atomic_text(root/'course/file-lessons'/name,json.dumps(lesson,ensure_ascii=False,indent=2)+'\n')
            manifest.append({'path':path,'file':name,'id':file_id,'questions':len(questions)})
    _atomic_text(root/'course/file-lessons.json',json.dumps({'sha':SHA,'files':manifest},ensure_ascii=False,indent=2)+'\n')
    print(f'{len(manifest)} whole-file lessons; {sum(r["questions"] for r in manifest)} questions')
    return manifest


def load_file_lessons(root):
    path=Path(root)/'course/file-lessons.json'
    if not path.exists():return []
    manifest=json.loads(path.read_text(encoding='utf-8'))
    result=[]
    for entry in manifest['files']:
        name=entry['file']
        if Path(name).name!=name or not name.endswith('.json'):raise ValueError('Invalid file lesson path')
        lesson=json.loads((Path(root)/'course/file-lessons'/name).read_text(encoding='utf-8'))
        if lesson['id']!=entry['id'] or lesson['path']!=entry['path']:raise ValueError('File lesson manifest mismatch')
        result.append(lesson)
    return result


if __name__=='__main__':build()
