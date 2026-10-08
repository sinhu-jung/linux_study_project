#!/usr/bin/env python3
"""Inventory every tracked file and every RST/Markdown heading in Documentation.
An inventory is evidence of indexed source coverage, not of explained technology coverage.
"""
import json
from lesson_storage import load_lessons
import os
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parent.parent
GIT=os.environ.get('STUDY_GIT','git')
if Path('/opt/homebrew/bin/git').is_file() and not os.environ.get('STUDY_GIT'):
 GIT='/opt/homebrew/bin/git'

def build():
 def git(*args): return subprocess.check_output([GIT,'-C',str(ROOT/'linux'),*args])
 sha=git('rev-parse','HEAD').decode().strip()
 records=git('ls-tree','-r','-z','HEAD').decode().split('\0')[:-1]
 files=[]
 for record in records:
  metadata,path=record.split('\t',1)
  mode,kind,blob=metadata.split()
  files.append({'path':path,'blob':blob,'kind':kind,'subsystem':path.split('/')[0] if '/' in path else 'root'})
 lessons=load_lessons(ROOT)
 ready={}
 for lesson in lessons:
  if lesson['kind']=='kernel': ready.setdefault(lesson['path'],[]).append(lesson['id'])
 docs=[f for f in files if f['path'].startswith('Documentation/')]
 prose_count=sum(f['path'].endswith(('.rst','.md','.txt')) for f in docs)
 binding_count=sum(f['path'].endswith('.yaml') for f in docs)
 topics=[]
 batch=subprocess.Popen([GIT,'-C',str(ROOT/'linux'),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 try:
  for n,doc in enumerate(docs):
   batch.stdin.write((doc['blob']+'\n').encode());batch.stdin.flush()
   header=batch.stdout.readline().decode().split();size=int(header[2]);data=batch.stdout.read(size);assert batch.stdout.read(1)==b'\n'
   binary=b'\0' in data[:8192]
   lines=[] if binary else data.decode('utf-8','replace').splitlines()
   headings=[]
   for i,line in enumerate(lines):
    stripped=line.strip()
    if not stripped: continue
    if doc['path'].endswith('.md') and re.match(r'^#{1,6} ',stripped): headings.append((i,stripped.lstrip('#').strip()))
    elif i+1<len(lines) and len(lines[i+1].strip())>=3 and re.fullmatch(r'[=\-~^"`+#*:]+',lines[i+1].strip()) and len(set(lines[i+1].strip()))==1 and not stripped.startswith(('..','|','+')):
     headings.append((i,stripped))
   if not headings:
    yaml_title=next(((i,re.sub(r'^title:\s*', '',line).strip().strip(chr(34))) for i,line in enumerate(lines) if line.startswith('title: ') and line[7:].strip() not in ('|','>')),None)
    headings=[yaml_title or (0,Path(doc['path']).name)]
   group=doc['path'].split('/')[1] if len(doc['path'].split('/'))>2 else 'general'
   for j,(line,title) in enumerate(headings):
    end=headings[j+1][0] if j+1<len(headings) else len(lines)
    paragraph=[]
    for raw in lines[line+1:end]:
     stripped=raw.strip()
     if not stripped or re.fullmatch(r'[=\-~^"`+#*:]+',stripped) or stripped.startswith(('..',':')): continue
     paragraph.append(stripped)
     if len(' '.join(paragraph))>500: break
    topics.append({'path':doc['path'],'title':title,'line':line+1,'group':group,'summary':' '.join(paragraph)[:700],'document':headings[0][1]})
   if (n+1)%1000==0: print(f'文書'.replace('文書','문서')+f' {n+1}/{len(docs)} 색인 완료',flush=True)
 finally:
  batch.stdin.close();batch.stdout.close();batch.wait()
 bygroup={}
 for f in files: bygroup[f['subsystem']]=bygroup.get(f['subsystem'],0)+1
 output={'version':'v6.12','sha':sha,'files':files,'topics':topics,'documents':len(docs),'prose_documents':prose_count,'binding_specs':binding_count,'groups':bygroup,'lessons':[{'id':l['id'],'title':l['title'],'path':l['path'],'excerpt':l.get('excerpt')} for l in lessons if l.get('track')=='os'],'coverage_note':'모든 추적 파일과 Documentation의 문서·장치 바인딩 규격·보조 파일을 목록화했습니다. 제목 목록은 모든 기술·알고리즘의 완전한 의미 목록이 아니며, 색인된 항목 전체에 쉬운 해설·실험·문제가 작성된 것은 아닙니다.'}
 destination=ROOT/'data/knowledge.json';destination.parent.mkdir(exist_ok=True);temporary=destination.with_suffix('.tmp');temporary.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')),encoding='utf-8');temporary.replace(destination)
 print(f'{len(files):,}개 파일, {len(docs):,}개 문서, {len(topics):,}개 제목 색인 완료',flush=True)
 return output

if __name__=='__main__':build()
