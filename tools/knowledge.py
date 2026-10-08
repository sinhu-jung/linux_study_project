import json
from lesson_storage import load_lessons
import re
from pathlib import Path
from index_knowledge import build

class Knowledge:
 def __init__(self,root,sha):
  self.path=root/'data/knowledge.json'
  if self.path.exists():
   self.data=json.loads(self.path.read_text(encoding='utf-8'))
   if self.data.get('sha')!=sha or 'binding_specs' not in self.data:self.data=build()
  else:self.data=build()
  lessons=load_lessons(root)
  self.data['lessons']=[{'id':l['id'],'title':l['title'],'path':l['path'],'excerpt':l.get('excerpt'),'group':l.get('area','OS 시작'),'summary':l['concepts'][1]['text'],'questions':len(l['questions']),'ready':True} for l in lessons if l.get('track')=='os']
  self.data['coverage_note']=f"해설·원리·사용 조건·문제·답지가 있는 OS 수업 {len(self.data['lessons'])}개를 분야별로 제공합니다. 각 수업은 고정된 Linux v6.12 원본에 연결됩니다. 전체 원본·공식 문서도 별도 탐색할 수 있습니다."
 def handle(self,query):
  data=self.data;term=query.get('q','').lower();group=query.get('group','');mode=query.get('mode','lessons');offset=max(0,int(query.get('offset',0)))
  items=data['files'] if mode=='files' else data['lessons'] if mode=='lessons' else data['topics']
  selected=[i for i in items if (not group or i.get('group',i.get('subsystem'))==group) and (not term or term in (i.get('title','')+' '+i['path']+' '+i.get('summary','')).lower())]
  if mode == 'documents':
   boundary=re.compile(r'(?<![a-z0-9])'+re.escape(term)+r'(?![a-z0-9])') if term else None
   preferred={'core-api':0,'mm':1,'scheduler':2,'locking':3,'RCU':4,'networking':5,'filesystems':6}
   def rank(item):
    prose=0 if item['path'].endswith(('.rst','.md','.txt')) else 1
    if boundary:
     relevance=0 if boundary.search(item['title'].lower()) else 1 if boundary.search(item['path'].lower()) else 2
     return relevance,prose,item['path'],item.get('line',0)
    return preferred.get(item.get('group'),20),prose,item['path'],item.get('line',0)
   selected.sort(key=rank)
  groups=sorted({i.get('group',i.get('subsystem')) for i in items})
  return {'files':len(data['files']),'documents':data['documents'],'prose_documents':data['prose_documents'],'binding_specs':data['binding_specs'],'headings':len(data['topics']),'guided':len(data['lessons']),'questions':sum(l['questions'] for l in data['lessons']),'lessons':data['lessons'],'coverage_note':data['coverage_note'],'sha':data['sha'],'groups':groups,'items':selected[offset:offset+50],'total':len(selected),'offset':offset}
