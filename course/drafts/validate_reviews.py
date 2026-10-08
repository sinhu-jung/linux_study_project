"""Check explicit pending-unit review references without modifying live lessons."""
import argparse,importlib.util,json,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def mod(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=argparse.ArgumentParser();p.add_argument('unit');p.add_argument('reviews');args=p.parse_args()
for name in [args.unit,args.reviews]:assert Path(name).name==name
b=mod('builder',ROOT/'tools/build_curriculum.py');mod('draft',ROOT/'course/drafts'/args.unit).register(b.module.topic,b.module.q,b.module.detail);topics={f'os{i:02d}':t for i,t in enumerate(b.module.TOPICS,17)}
git=os.environ.get('STUDY_GIT','git');sha=subprocess.check_output([git,'-C',str(ROOT/'linux'),'rev-parse','HEAD']).decode().strip();records=json.loads((ROOT/'course/drafts'/args.reviews).read_text());count=0
for path,record in records.items():
 assert record['sha']==sha and record['decision']=='explained' and record['evidence']
 raw=subprocess.check_output([git,'-C',str(ROOT/'linux'),'show','HEAD:'+path]).decode()
 for e in record['evidence']:
  t=topics[e['lesson']];allowed={'왜 필요한가','기술·자료구조·알고리즘의 원리','사용 방법과 적용 조건',*[d['title'] for d in t['details']]};assert set(e['sections'])<=allowed,(path,e['lesson'])
  assert all(s in raw for s in e['symbols']),(path,e['symbols']);assert len(e['review'])>=30;count+=1
print(f'PASS {len(records)} explicit source records, {count} lesson/section/symbol references; semantic decisions remain authored evidence')
