"""Fresh inventory; never equate a lesson link with whole-file completion."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from build_file_lessons import load_file_lessons, SHA
from lesson_storage import load_lessons, _atomic_text

ROOT=Path(__file__).resolve().parents[1]


def audit(root=ROOT):
    git=os.environ.get('STUDY_GIT','git')
    run=lambda *args:subprocess.check_output([git,'-C',str(root/'linux'),*args])
    actual=run('rev-parse','HEAD').decode().strip()
    if actual!=SHA:raise ValueError('Wrong source commit')
    paths=run('ls-tree','-r','--name-only','-z',SHA).decode().strip('\0').split('\0')
    pathset=set(paths)
    legacy=load_lessons(root)
    linked={l['path'] for l in legacy if l.get('track')=='os'}
    authored={}
    for lesson in load_file_lessons(root):
        path=lesson['path']
        if path not in pathset:raise ValueError('Source path missing: '+path)
        source=run('show',SHA+':'+path)
        review=lesson['source_review']
        if (review['sha']!=SHA or review['scope']!='whole-file'
            or review['source_sha256']!=hashlib.sha256(source).hexdigest()
            or lesson['annotated'].encode()!=source
            or len(source.decode().splitlines())!=review['line_count']):
            raise ValueError('Source mismatch: '+path)
        if not lesson['deep_dive'] or not lesson['questions'] or any(not q['explanation'] for q in lesson['questions']):
            raise ValueError('Missing authored teaching content: '+path)
        authored[path]=lesson['id']
    old=json.loads((root/'course/source_reviews.json').read_text(encoding='utf-8'))
    summary={'sha':SHA,'tracked_files':len(paths),'current_legacy_linked_files':len(linked&pathset),
        'whole_file_authored_and_source_checked':len(authored),
        'legacy_review_claims_requiring_revalidation':len(set(old)-set(authored)),
        'remaining_without_current_whole_file_lesson':len(pathset-set(authored)),
        'complete':False,
        'note':'Current whole-file source/content audit is separate from legacy review claims. Source checks do not prove every explanation semantically correct.'}
    entries=[{'path':p,'status':'whole-file-authored' if p in authored else 'legacy-linked' if p in linked else 'pending',
              'lesson':authored.get(p)} for p in paths]
    _atomic_text(root/'data/file-learning-audit.json',json.dumps({'summary':summary,'files':entries},ensure_ascii=False,separators=(',',':'))+'\n')
    _atomic_text(root/'course/file-learning-progress.json',json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
    return summary


if __name__=='__main__':audit()
