// Structural evidence complements (does not replace) individual semantic review.
const fs=require('fs'),assert=require('assert/strict'),crypto=require('crypto');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x??null)).digest('hex');
let lessons=read('course/foundations.json');
for(const p of read('course/lesson-parts.json').parts) lessons.push(...read('course/lesson-parts/'+p));
for(const f of read('course/file-lessons.json').files) lessons.push(read('course/file-lessons/'+f.file));
const baseline=read('data/easy-review-20261014/baseline.json');
assert.equal(lessons.length,baseline.lessons);
assert.equal(new Set(lessons.map(l=>l.id)).size,lessons.length);
let added=[], preservedCompleted=0;
const authoringCache=new Map();
for(let i=0;i<lessons.length;i++){
 const l=lessons[i],b=baseline.items[i];
 assert.equal(l.id,b.id,'Lesson order');
 assert.equal(l.path,b.path,'Source path '+l.id);
 assert.equal(hash(l.annotated),b.code_hash,'Source text '+l.id);
 assert.deepEqual(l.questions.map(q=>q.answer),b.answers,'Answer indices '+l.id);
 assert.equal(l.questions.length,b.question_count);
 if(b.completed){assert.equal(hash(l),b.hash,'Previously completed lesson changed '+l.id);preservedCompleted++;}
 else if(l.beginner){
  assert.equal(hash(l.technical_original),b.hash,'Complete original snapshot '+l.id);
  assert.ok(l.easy_review && l.easy_review.authoring_sha256,'Provenance '+l.id);
  const source=l.easy_review.authoring_source;
  if(!authoringCache.has(source))authoringCache.set(source,read(source));
  const authored=authoringCache.get(source)[l.id];
  assert.ok(authored,'Authored row '+l.id);
  for(const k of ['story','meaning','exercise'])assert.equal(l.beginner[k],authored[k],'Authored beginner '+l.id);
  const wholeFile=l.id.startsWith('file-');
  assert.deepEqual(l.guide,wholeFile&&!authored.deep_dive?[authored.meaning]:authored.guide,'Authored guide '+l.id);
  assert.deepEqual(l.deep_dive,authored.deep_dive||(wholeFile?authored.guide.map((text,i)=>({title:'원문 읽기 '+(i+1),text})):[]),'Authored deep guide '+l.id);
  for(let j=0;j<l.questions.length;j++){
   const q=l.questions[j],o=l.technical_original.questions[j];
   for(const k of Object.keys(o).filter(k=>!['prompt','options','explanation'].includes(k)))assert.deepEqual(q[k],o[k],'Original question identity/metadata '+l.id+'/'+j+'/'+k);
   assert.equal(q.original_prompt,o.prompt);
   assert.equal(q.original_explanation,o.explanation);
   assert.deepEqual(q.original_options,o.options);
   assert.equal(q.options.length,o.options.length);
   assert.notEqual(q.explanation,o.explanation);
   for(const k of ['prompt','options','explanation'])assert.deepEqual(q[k],authored.questions[j][k],'Authored question '+l.id);
  }
  assert.deepEqual(l.practice.command,l.technical_original.practice.command,'Practice command '+l.id);
  added.push(l);
 } else assert.equal(hash(l),b.hash,'Unprocessed lesson changed '+l.id);
 for(const q of l.questions){assert.ok(Number.isInteger(q.answer)&&q.answer>=0&&q.answer<q.options.length); for(const s of [q.prompt,q.explanation,...q.options])assert.ok(typeof s==='string'&&s.trim());}
}
const bank=JSON.parse(fs.readFileSync('data/learning-bank.js','utf8').replace(/^window.LEARNING_BANK = /,'').replace(/;\s*$/,''));
assert.deepEqual(bank.lessons.map(l=>l.id),lessons.map(l=>l.id),'Bank lesson order');
for(let i=0;i<lessons.length;i++){
 const l=lessons[i],bl=bank.lessons[i];
 assert.deepEqual(bl.guide,l.guide,'Bank guide '+l.id);
 assert.deepEqual(bl.beginner,l.beginner,'Bank beginner '+l.id);
 assert.equal(bl.annotated,l.annotated,'Bank source '+l.id);
 assert.deepEqual(bl.deep_dive,l.deep_dive,'Bank deep guide '+l.id);
 assert.deepEqual(bl.technical_original,l.technical_original,'Bank original '+l.id);
 for(let j=0;j<l.questions.length;j++)for(const k of ['prompt','options','answer','explanation'])assert.deepEqual(bl.questions[j][k],l.questions[j][k],'Bank question '+l.id);
}
const remaining=lessons.filter(l=>!l.beginner),done=lessons.filter(l=>l.beginner);
const syllabus=fs.readFileSync('course/syllabus.md','utf8');
const osLessons=lessons.filter(l=>l.track==='os');
const headings=[...syllabus.matchAll(/^## (os\d+)\. /gm)];
assert.deepEqual(headings.map(m=>m[1]),osLessons.map(l=>l.id),'Syllabus order');
for(let i=0;i<osLessons.length;i++){
 const l=osLessons[i],section=syllabus.slice(headings[i].index,headings[i+1]?.index??syllabus.length);
 for(const s of [...Object.values(l.beginner||{}),...l.guide,...(l.deep_dive||[]).map(x=>x.text),l.practice.command])assert.ok(section.includes(s),'Syllabus prose '+l.id);
 let cursor=section.indexOf('### 문제와 풀이');
 for(let j=0;j<l.questions.length;j++){
  const q=l.questions[j];
  for(const s of [`${j+1}. ${q.prompt}`,...q.options.map(x=>`   - ${x}`),`   **정답:** ${q.options[q.answer]}`,`   **풀이:** ${q.explanation}`]){
   const next=section.indexOf(s,cursor);assert.ok(next>=cursor,'Syllabus question/order '+l.id+'/'+j);cursor=next+s.length;
  }
 }
}
const result={complete:remaining.length===0,total_lessons:lessons.length,total_questions:lessons.reduce((s,l)=>s+l.questions.length,0),previously_completed_preserved:preservedCompleted,new_lessons:added.length,new_questions:added.reduce((s,l)=>s+l.questions.length,0),rewritten_lessons:done.length,rewritten_questions:done.reduce((s,l)=>s+l.questions.length,0),remaining_lessons:remaining.length,remaining_questions:remaining.reduce((s,l)=>s+l.questions.length,0),checks:['original snapshots exact','source text/path exact','lesson/question order and answer indices exact','original options preserved','existing completed and unprocessed lessons unchanged','practice commands unchanged','learning bank guides and questions match','OS syllabus prose/questions/order match','question identity and metadata preserved','question validity'],limits:['Structural checks do not prove semantic equivalence of all options.','Actual child comprehension has not been tested.'],new_ids:added.map(l=>l.id)};
fs.writeFileSync('data/easy-review-20261014/validation.json',JSON.stringify(result,null,2)+'\n');
fs.writeFileSync('data/easy-review-20261014/remaining.json',JSON.stringify(remaining.map(l=>({id:l.id,path:l.path,title:l.title,questions:l.questions.length})),null,2)+'\n');
const p=read('course/easy-reading-progress.json');for(const k of ['complete','total_lessons','total_questions','rewritten_lessons','rewritten_questions','remaining_lessons','remaining_questions'])assert.equal(p[k],result[k],k);
const continuation=read('data/easy-reading-continuation.json');
continuation.complete=result.complete;
const previouslyRecorded=new Set(continuation.progress?.rewritten_ids||[]);
const newest=added.filter(l=>!previouslyRecorded.has(l.id)).map(l=>l.id);
if(newest.length)continuation.last_batch=newest;
continuation.authoring_source='tools/apply_easy_batches.py';
continuation.authoring_sources=[...new Set(added.map(l=>l.easy_review.authoring_source))];
continuation.next_ids=remaining.slice(0,12).map(l=>l.id);
continuation.progress=p;
continuation.remaining_questions=result.remaining_questions;
continuation.remaining_manifest='data/easy-review-20261014/remaining.json';
continuation.verified=result.checks;
continuation.notes=[...new Set([...(continuation.notes||[]),'2026-10-14: lesson-by-lesson authoring continues in tools/easy_batches; generated counts do not certify child comprehension.'])];
fs.writeFileSync('data/easy-reading-continuation.json',JSON.stringify(continuation,null,2)+'\n');
const logPath='data/easy-review-20261014/checkpoints.json';
const log=fs.existsSync(logPath)?read(logPath):[];
if(!log.length||log.at(-1).new_lessons!==result.new_lessons){log.push({...result,new_ids:undefined,verified_at:new Date().toISOString()});fs.writeFileSync(logPath,JSON.stringify(log,null,2)+'\n');}
console.log(JSON.stringify({...result,new_ids:undefined},null,2));
