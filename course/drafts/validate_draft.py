"""Validate one pending authored unit against the live pinned curriculum."""
import argparse,importlib.util,json,re,subprocess,inspect
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
parser=argparse.ArgumentParser();parser.add_argument('unit');parser.add_argument('--after',action='append',default=[]);args=parser.parse_args()
assert Path(args.unit).name==args.unit and args.unit.endswith('.py')
builder=module('builder',ROOT/'tools/build_curriculum.py')
original_topic=builder.module.topic
def pending_topic(*args,source_occurrence=1,**kwargs):
 original_topic(*args,**kwargs)
 if source_occurrence!=1:builder.module.TOPICS[-1]['source_occurrence']=source_occurrence
builder.module.topic=pending_topic
for extra in args.after:
 assert Path(extra).name==extra and extra.endswith('.py')
 module('preceding_'+extra,ROOT/'course/drafts'/extra).register(builder.module.topic,builder.module.q,builder.module.detail)
previous=list(builder.module.TOPICS);start=len(previous)
module('draft',ROOT/'course/drafts'/args.unit).register(builder.module.topic,builder.module.q,builder.module.detail)
topics=builder.module.TOPICS[start:];titles={t['title'] for t in previous};prompts={q['prompt'] for t in previous for q in t['questions']}
def draft_source(path,symbol,occurrence=1):
 try:
  if occurrence!=1:
   code=inspect.getsource(builder.source).replace('def source(path, symbol):','def source(path, symbol, occurrence=1):').replace('start = candidates[0]','assert occurrence >= 1\n    start = candidates[occurrence-1]')
   namespace=dict(builder.__dict__);exec(code,namespace);return namespace['source'](path,symbol,occurrence)
  return builder.source(path,symbol)
 except ValueError:
  # Pending table lesson: require an exact initialized array definition.
  raw=subprocess.check_output([builder.GIT,'-C',str(ROOT/'linux'),'show','HEAD:'+path]).decode().splitlines()
  kernel_paths=('lib/fdt.c','lib/fdt_ro.c','lib/fdt_wip.c','lib/fdt_rw.c','lib/fdt_sw.c','lib/fdt_strerror.c','lib/fdt_empty_tree.c','lib/fdt_addresses.c','include/linux/libfdt.h')
  found=[i for i,line in enumerate(raw) if (path in kernel_paths and symbol.startswith('#include ') and line.strip()==symbol) or (path=='include/linux/libfdt_env.h' and re.match(r'^typedef\s+__be(?:16|32|64)\s+'+re.escape(symbol)+r'\s*;',line))]
  if found:
   start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  found=[i for i,line in enumerate(raw) if path=='include/linux/irqreturn.h' and re.match(r'^typedef\s+enum\s+irqreturn\s+'+re.escape(symbol)+r'\s*;',line)]
  if found:
   start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  found=[i for i,line in enumerate(raw) if re.match(r'^typedef\s+[^;]*\(\s*\*\s*'+re.escape(symbol)+r'\s*\)\s*\(',line) or re.match(r'^#define\s+'+re.escape(symbol)+r'(?:\s|$)',line)]
  if found:
   start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  found=[i for i,line in enumerate(raw) if path in ('arch/arm64/include/asm/fixmap.h','include/linux/irqreturn.h') and re.match(r'^enum\s+'+re.escape(symbol)+r'\s*\{',line)]
  if found:
   start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  found=[i for i,line in enumerate(raw) if path in ('scripts/dtc/libfdt/libfdt_internal.h','include/linux/irqreturn.h') and re.match(r'^\s*'+re.escape(symbol)+r'\s*=',line)]
  if found:
   start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  if Path(path).name.startswith('Kconfig'):
   found=[i for i,line in enumerate(raw) if re.match(r'^(?:config|menuconfig)\s+'+re.escape(symbol)+r'\s*$',line)]
   if found:
    start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  if Path(path).name in ('Makefile','Kbuild') or path.endswith('.mk'):
   found=[i for i,line in enumerate(raw) if re.match(r'^'+re.escape(symbol)+r'\s*(?::=|\+=|\?=|=)',line.lstrip())]
   if found:
    start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  if path.endswith(('.h','.S','.s')):
   found=[i for i,line in enumerate(raw) if re.match(r'^\s*\.macro\s+'+re.escape(symbol)+r'(?:\s|$)',line)]
   if found:
    start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  if path.endswith('.rst'):
   found=[i for i,line in enumerate(raw[:-1]) if line.strip()==symbol and re.fullmatch(r'[=~^`:+#-]+',raw[i+1].strip())]
   if found:
    start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  if path.endswith(('.h','.c')):
   found=[i for i,line in enumerate(raw) if re.match(r'^register\s+unsigned\s+long\s+'+re.escape(symbol)+r'\s+asm\s*\("[A-Za-z0-9_]+"\)\s*;',line)]
   if found:
    start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  found=[i for i,line in enumerate(raw) if path=='arch/arm64/kernel/alternative.c' and re.match(r'^static\s+const\s+struct\s+\w+\s+'+re.escape(symbol)+r'\s+\w*\s*=\s*\{',line)]
  if found:
   start=found[occurrence-1];end=min(start+26,len(raw));return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
  pattern=re.compile(r'^\S.*\b'+re.escape(symbol)+r'\s*\[[^]]*\]\s*=\s*\{')
  found=[i for i,line in enumerate(raw) if pattern.search(line)]
  if not found:
   pattern=re.compile(r'^struct\s+'+re.escape(symbol)+r'\s*\{')
   found=[i for i,line in enumerate(raw) if pattern.search(line)]
  if len(found)!=1:raise
  start=found[0];end=min(start+26,len(raw))
  return '\n'.join(raw[start:end])+'\n',{'start':start+1,'end':end,'anchor':symbol}
path=ROOT/'course/planned_topics.json';plans=json.loads(path.read_text());bytitle={p['title']:p for p in plans};number=max(int(p['key'].split('-')[-1]) for p in plans)+1;anchors=[]
for index,t in enumerate(topics,start+17):
 assert t['title'] not in titles;titles.add(t['title']);code,excerpt=draft_source(t['path'],t['symbol'],t.get('source_occurrence',1));assert t['symbol'] in code
 assert len(t['why'])>=30 and len(t['principle'])>=60 and len(t['use'])>=40 and len(t['questions'])==2 and len(t['details'])>=2
 for q in t['questions']:
  assert q['prompt'] not in prompts;prompts.add(q['prompt']);assert q['correct']!=q['wrong'] and len(q['explanation'])>=20
 p=bytitle.get(t['title'])
 if p is None:p={'key':f'planned-{number:03d}'};number+=1;plans.append(p)
 p.update(title=t['title'],source=t['path'],symbol=t['symbol'],area=t['area']);
 if 'source_occurrence' in t:p['source_occurrence']=t['source_occurrence']
 anchors.append(dict(planned_lesson=f'os{index:02d}',title=t['title'],path=t['path'],excerpt=excerpt))
path.write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
result={'draft_lessons':len(topics),'questions':sum(len(t['questions']) for t in topics),'anchors':anchors};(ROOT/'course/drafts'/args.unit.replace('.py','_validation.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(f"PASS {len(topics)} drafts, {result['questions']} worked questions and exact source anchors")
