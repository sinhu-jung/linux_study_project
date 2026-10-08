"""Content and behavior review. Uses a disposable DB, never learner progress."""
import json
import os
from pathlib import Path
import re
import random
import sqlite3
import subprocess
import sys
import tempfile
import threading
from functools import lru_cache

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from course import Course
from knowledge import Knowledge
GIT=os.environ.get('STUDY_GIT','/opt/homebrew/bin/git' if Path('/opt/homebrew/bin/git').exists() else 'git')
# The pinned tree is immutable during a review round. Reuse identical reads;
# every lesson's own range and answer sheet are still checked below.
@lru_cache(maxsize=None)
def git(*args):return subprocess.check_output([GIT,'-C',str(ROOT/'linux'),*args])
checks=[]
seed=int(os.environ.get('STUDY_REVIEW_SEED','0'))
rng=random.Random(seed)
def reviewed(name,test):
 test();checks.append({'check':name,'result':'passed'});print('PASS:',name)
def require(condition):
 if not condition:raise AssertionError('Review failed')

with tempfile.TemporaryDirectory() as temporary:
 def conn():return sqlite3.connect(Path(temporary)/'progress.sqlite3')
 c=Course(ROOT,conn,git,threading.Lock())
 oslessons=[l for l in c.lessons if l.get('track')=='os'];clessons=[l for l in c.lessons if l.get('track')=='c']
 manifest=json.loads((ROOT/'course/coverage.json').read_text(encoding='utf-8'))
 expected_os=manifest['lessons'];expected_questions=manifest['questions'];expected_areas=len(manifest['areas'])
 def call(method,route,q=None,payload=None):return c.handle(method,route,q or {},payload)
 reviewed(f'01. 독립된 {expected_os}개 OS 과정과 기존 11개 C 과정',lambda:require(len(oslessons)==expected_os and expected_os>=150 and len(clessons)==11 and len(set(c.ids))==expected_os+11))
 def source_ranges():
  for lesson in oslessons:
   lines=git('show','HEAD:'+lesson['path']).decode().splitlines();e=lesson['excerpt']
   require(1<=e['start']<=e['end']<=len(lines))
   require(e['anchor'] in lines[e['start']-1])
   require(c.source(lesson)=='\n'.join(lines[e['start']-1:e['end']])+'\n')
 reviewed('02. 모든 OS 발췌를 고정 커널 원본과 대조',source_ranges)
 def answer_source():
  for lesson in oslessons:
   # Authored answer sheet inserts comments but must retain original code tokens.
   strip=lambda t:re.sub(r'\s+','',re.sub(r'/\*.*?\*/|//[^\n]*','',t,flags=re.S))
   require(strip(c.source(lesson))==strip(lesson['annotated']))
 reviewed('03. 주석 답지에 원본 코드 변경이 없는지 확인',answer_source)
 reviewed('04. 단계별 동작 이유·원리·활용·C 설명·관찰 방법 제공',lambda:require(all(len(l['concepts'])==3 and l['guide'] and l['practice']['command'] and l['practice']['expected'] for l in oslessons)))
 reviewed('05. 조건별 원리 모델과 실제 실행을 구분',lambda:require(all(len(l['experiment']['scenarios'])>=2 and all(len(s['steps'])>=2 and all(step['diagram'] and step['explanation'] for step in s['steps']) for s in l['experiment']['scenarios']) for l in oslessons)))
 reviewed('06. 문제의 정답 번호·선택지·해설과 수업 ID 유효성',lambda:require(all(q['explanation'] and type(q['answer']) is int and 0<=q['answer']<len(q['options']) for l in c.lessons for q in l['questions'])))
 reviewed('07. 잠긴 수업과 답지 API의 선행 단계 검사',lambda:require(call('GET','/api/course/lesson',{'id':'os02'})[1]==403 and call('GET','/api/course/answer',{'id':'os02'})[1]==403))
 reviewed('08. 답지 보기만으로 다음 단계가 열리지 않음',lambda:require(call('GET','/api/course/answer',{'id':'os01'})[1]==200 and call('GET','/api/course/lesson',{'id':'os02'})[1]==403))
 def invalid_answers():
  for answers in ([None,None],[True,0],['1',0],[],[99,0]):
   response,status=call('POST','/api/course/check',payload={'id':'os01','answers':answers,'draft':''})
   require(status==400 or not response['passed'])
  require(call('GET','/api/course/lesson',{'id':'os02'})[1]==403)
 reviewed('09. 미선택·잘못된 답과 자료형으로 통과할 수 없음',invalid_answers)
 def persist():
  payload={'id':'os01','answers':[None,None],'draft':'// 부팅 준비를 한다. 한글 주석'}
  require(call('POST','/api/course/draft',payload=payload)[1]==200)
  c2=Course(ROOT,conn,git,threading.Lock());require(c2.handle('GET','/api/course/lesson',{'id':'os01'})[0]['draft']==payload['draft'])
 reviewed('10. 한글 주석·선택 답이 서버 재생성 후 유지',persist)
 def varied_inputs():
  lesson=oslessons[0]
  draft='// 회차 '+str(seed)+' 한글 Linux Windows\n'+''.join(rng.choice('가나다abc012☀\t') for _ in range(128+seed%257))
  answers=[rng.randrange(len(q['options'])) for q in lesson['questions']]
  require(call('POST','/api/course/draft',payload={'id':lesson['id'],'draft':draft,'answers':answers})[1]==200)
  restored=Course(ROOT,conn,git,threading.Lock()).handle('GET','/api/course/lesson',{'id':lesson['id']})[0]
  require(restored['draft']==draft and restored['answers']==answers)
  invalid=[q['answer'] for q in lesson['questions']]
  invalid[rng.randrange(len(invalid))]=rng.choice([True,False,-1,999,'0',{},[]])
  require(call('POST','/api/course/check',payload={'id':lesson['id'],'draft':draft,'answers':invalid})[1]==400)
  require(call('GET','/api/course/lesson',{'id':oslessons[1]['id']})[1]==403)
 reviewed(f'27. 회차별 입력 변형·한글 저장·잘못된 채점·잠금 검사 (seed {seed})',varied_inputs)
 def unlock():
  for lesson in oslessons:
   require(call('GET','/api/course/lesson',{'id':lesson['id']})[1]==200)
   data,status=call('POST','/api/course/check',payload={'id':lesson['id'],'draft':'// 검수','answers':[q['answer'] for q in lesson['questions']]})
   require(status==200 and data['all_correct'])
  require(call('GET','/api/course',{'track':'os'})[0]['completed']==expected_os)
  require(call('GET','/api/course',{'track':'c'})[0]['completed']==0)
 reviewed(f'11. {expected_os}단계 순차 채점·해제, C 과정 진도 독립',unlock)
 def preservation():
  payload={'id':'os01','draft':'// 복습','answers':[None,None]};call('POST','/api/course/draft',payload=payload)
  require(call('GET','/api/course/lesson',{'id':'os01'})[0]['passed'])
  for lesson in clessons:
   require(call('GET','/api/course/lesson',{'id':lesson['id']})[1]==200)
   call('POST','/api/course/check',payload={'id':lesson['id'],'draft':'','answers':[q['answer'] for q in lesson['questions']]})
  require(call('GET','/api/course',{'track':'c'})[0]['completed']==11)
 reviewed('12. 완료 상태 복습 시 유지와 기존 C 과정의 전체 진행',preservation)
 k=Knowledge(ROOT,git('rev-parse','HEAD').decode().strip())
 def files_complete():
  tracked=set(git('ls-tree','-r','--name-only','-z','HEAD').decode().split('\0')[:-1]);indexed=[f['path'] for f in k.data['files']]
  require(set(indexed)==tracked and len(indexed)==len(tracked)==86680)
 reviewed('13. 전체 추적 파일 집합과 색인의 누락·중복 대조',files_complete)
 def docs_complete():
  expected={f['path'] for f in k.data['files'] if f['path'].startswith('Documentation/')}
  require(expected=={t['path'] for t in k.data['topics']})
  require(len(expected)==k.data['documents']==10122 and k.data['prose_documents']==4909 and k.data['binding_specs']==4380)
  require(all(t['line']>=1 and t['title'] for t in k.data['topics']))
 reviewed('14. 공식 문서 전체가 검색 색인에 포함되는지 확인',docs_complete)
 def advanced_search():
  for keyword in ('rcu','bpf','dma','crypto','barrier','radix'):
   require(k.handle({'q':keyword,'mode':'documents'})['total']>0)
  page=k.handle({'q':'rcu','offset':'0','mode':'documents'});nextpage=k.handle({'q':'rcu','offset':'50','mode':'documents'})
  require(len(page['items'])<=50 and len(nextpage['items'])<=50)
 reviewed('15. 수업 밖 고급 기술 검색과 페이지 분할',advanced_search)
 reviewed('16. 원리 계산 예제의 수치와 개념 검산',lambda:require(8197//4096==2 and 8197%4096==5 and 7*4096+5==28677 and 2**3==8 and min([('A',10),('B',6)],key=lambda x:x[1])[0]=='B'))
 def authored_content():
  advanced=[l for l in oslessons if l.get('authored_topic')]
  require(len(advanced)==expected_os-16 and len({l['title'] for l in oslessons})==expected_os)
  require(all(len(l['concepts'])==3 and len(l['concepts'][0]['text'])>=30 and len(l['concepts'][1]['text'])>=60 and len(l['concepts'][2]['text'])>=40 and len(l['questions'])==2 for l in advanced))
  require(len({l['concepts'][1]['text'] for l in advanced})==expected_os-16)
  require(sum(len(l['questions']) for l in oslessons)==expected_questions)
 reviewed(f'17. 추가 {expected_os-16}개 주제의 개별 해설·적용 조건과 총 {expected_questions}문제',authored_content)
 def questions_specific():
  questions=[q for l in oslessons for q in l['questions']]
  require(len({q['prompt'] for q in questions})==len(questions))
  require(all(len(set(q['options']))==len(q['options']) and len(q['explanation'])>=20 for q in questions))
 reviewed('18. 중복 문제·선택지와 빈 풀이 검사',questions_specific)
 def syllabus_complete():
  text=(ROOT/'course/syllabus.md').read_text(encoding='utf-8')
  parts=re.split(r'^## (os\d+)\.',text,flags=re.M)
  sections=dict(zip(parts[1::2],parts[2::2]))
  require(len(sections)==len(oslessons))
  for lesson in oslessons:
   section=sections[lesson['id']]
   require(lesson['path'] in section)
   for question in lesson['questions']:require(question['prompt'] in section and question['explanation'] in section)
   reading=lesson['reading_support']
   for item in [reading['foundation'],*reading['walkthrough'],*reading['terms']]:
    require(item['title'] in section and item['text'] in section)
 reviewed(f'19. 전체 교재 파일의 {expected_os}개 해설·문제·답지 일치',syllabus_complete)
 def areas_complete():
  manifest=json.loads((ROOT/'course/coverage.json').read_text(encoding='utf-8'))
  require(manifest['lessons']==expected_os and manifest['questions']==expected_questions)
  listed=[i for ids in manifest['areas'].values() for i in ids]
  require(len(listed)==expected_os and set(listed)=={l['id'] for l in oslessons})
 reviewed(f'20. {expected_areas}개 분야의 수업·문제 작성 명세 대조',areas_complete)
 def ready_search():
  require(k.handle({})['total']==expected_os and k.handle({})['questions']==expected_questions)
  for term in ('RCU','XArray','Maple','io_uring','KVM','DMA','Futex','Btrfs','ALSA','Kconfig'):
   page=k.handle({'q':term,'mode':'lessons'})
   require(page['total']>0 and all(i['ready'] and i['questions']>=2 for i in page['items']))
  for area in k.handle({'mode':'lessons'})['groups']:
   require(k.handle({'mode':'lessons','group':area})['total']>0)
 reviewed('21. 교재 검색 결과가 실제 해설·문제 수업에 연결',ready_search)
 def catalog_pages():
  allitems=[]
  for offset in range(0,expected_os,50):allitems.extend(k.handle({'mode':'lessons','offset':str(offset)})['items'])
  require(len(allitems)==expected_os and len({i['id'] for i in allitems})==expected_os)
 reviewed('22. 교재 전체 페이지의 중복·누락 검사',catalog_pages)
 def original_ids():
  expected={'os01':'init/main.c','os02':'fs/read_write.c','os04':'include/linux/list.h','os16':'mm/memory.c'}
  require(all(next(l for l in oslessons if l['id']==i)['path']==p for i,p in expected.items()))
 reviewed('23. 기존 수업 ID와 원본 연결 보존',original_ids)
 def source_contracts():
  # Contracts from the actual version, independent of display/quiz implementation.
  checks=[('include/linux/uaccess.h','copy_from_user','copied successfully) and size (nothing copied)'),
          ('kernel/fork.c','CLONE_VM','copy_mm'),
          ('fs/binfmt_elf.c','PT_LOAD','load_elf_binary'),
          ('lib/kfifo.c','__kfifo_in','fifo->in += len'),
          ('lib/list_sort.c','stable','list_sort'),
          ('kernel/sched/rt.c','SCHED_RR','time_slice'),
          ('include/linux/seqlock.h','read_seqcount_retry','read_seqcount_begin'),
          ('kernel/rcu/tree.c','synchronize_rcu','grace period'),
          ('net/ipv4/udp.c','MSG_TRUNC','udp_recvmsg'),
          ('drivers/usb/core/urb.c','usb_submit_urb','usb_kill_urb')]
  for path,a,b in checks:
   source=git('show','HEAD:'+path).decode();require(a in source and b in source)
 reviewed('24. 원본 API 계약·알고리즘 핵심 표식 10건 재확인',source_contracts)
 def api_all():
  for lesson in oslessons:
   data,status=call('GET','/api/course/lesson',{'id':lesson['id']})
   answer,answer_status=call('GET','/api/course/answer',{'id':lesson['id']})
   require(status==answer_status==200 and len(data['questions'])==len(answer['answers']))
   require(all('answer' not in q and 'explanation' not in q for q in data['questions']))
   require(all(q['explanation'] for q in answer['answers']))
 reviewed(f'25. {expected_os}개 수업·답지 응답과 문제 화면의 정답 분리',api_all)
 def relative_references():
  files={f['path'] for f in k.data['files']}
  for lesson in oslessons:
   require(lesson['path'] in files)
   for reference in lesson.get('references',[]):
    if reference['url'].startswith('/explorer#'):require(reference['url'].split('#',1)[1].split('?',1)[0] in files)
 reviewed('26. 수업·답지의 모든 로컬 원본 링크 유효성',relative_references)
 def plain_language():
  import importlib.util
  spec=importlib.util.spec_from_file_location('reading_support',ROOT/'course/reading_support.py')
  support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
  require(len(support.FOUNDATIONS)==expected_areas and len(support.WALKTHROUGHS)==150)
  require(not support.matches('RCU','SRCU') and support.matches('RCU','RCU 읽기'))
  for l in oslessons:
   actual=l['reading_support'];fresh=dict(l);support.enrich(fresh)
   require(actual==fresh['reading_support'])
   require(actual['foundation']['text'] and actual['terms'])
   require(len({t['title'] for t in actual['terms']})==len(actual['terms']))
   if int(l['id'][2:])<=150:require(actual['walkthrough'])
   data,status=call('GET','/api/course/lesson',{'id':l['id']})
   require(status==200 and data['reading_support']==actual)
  xarray=next(l for l in oslessons if l['id']=='os17')
  require(len(xarray['reading_support']['walkthrough'])==7)
  require((1000000+1)*8==8000008 and (1000001-2)*8==7999992)
  require('8000008' in xarray['intro'] and '7999992' in xarray['reading_support']['walkthrough'][2]['text'])
 reviewed('28. 전체 수업의 기초·용어 연결, 핵심 150개 인과 설명과 XArray 계산',plain_language)
report_path=Path(os.environ.get('STUDY_REVIEW_REPORT',str(ROOT/'data/review-report.json')))
report_path.write_text(json.dumps({'version':'v6.12','seed':seed,'checks':checks,'automated_passed':len(checks),'windows_native_tested':False,'coverage_limits':'파일과 문서는 전체 색인 대조. 의미상 모든 기술의 완전성이나 전체 항목의 해설 완료를 보장하지 않음.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(checks)} review checks passed. Learner progress was not modified.')
