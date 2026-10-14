'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const bank = window.LEARNING_BANK;
  if (!bank) {
    $('welcome').append(Object.assign(document.createElement('p'), {className:'error',textContent:'교재 데이터가 없습니다. start-learning.bat 또는 python start-study.py --offline을 실행해 주세요.'}));
    return;
  }
  const KEY = 'linux-cs-learning-v1', PAGE = 30, intervals = [1,3,7,14,30];
  const lessons = bank.lessons, byId = new Map(lessons.map(l => [l.id,l]));
  if(bank.reading_audit&&$('readingProgress'))$('readingProgress').textContent=`현재 ${bank.reading_audit.introductions_and_answer_sets_rewritten}개 수업과 ${bank.reading_audit.questions_rewritten}개 문제를 쉬운 말로 다시 썼습니다. 나머지 ${bank.reading_audit.remaining_lessons_for_individual_rewrite.toLocaleString()}개 수업은 개별 재작성 중입니다. 낱말 풀이만 추가한 수업은 완료로 세지 않습니다.`;
  const fileOption=document.createElement('option');fileOption.value='files';fileOption.textContent='파일 전체 해설 · 작성 완료 묶음';$('track').append(fileOption);
  if(bank.file_progress){const p=document.createElement('p');p.className='notice';p.textContent=`전체 ${bank.file_progress.total.toLocaleString()}개 원본 파일 중 현재 새 파일별 교재 ${bank.file_progress.authored.toLocaleString()}개. 기존 함수별 수업 연결은 파일 전체 완료로 세지 않습니다. 나머지 파일은 작성·재검토 중입니다.`;document.querySelector('header').after(p);}
  const qmap = new Map();
  const signature = q => q.fingerprint;
  lessons.forEach(l => l.questions.forEach((q,i) => qmap.set(`${l.id}:${i}`,signature(q))));
  let state = {version:1,answers:{},notes:{},last:null}, page=0, selected=null;
  function tell(text) { $('status').textContent=text; }
  function validate(raw) {
    if (!raw || raw.version!==1 || typeof raw.answers!=='object' || !raw.answers || Array.isArray(raw.answers) || typeof raw.notes!=='object' || !raw.notes || Array.isArray(raw.notes)) throw Error('지원하지 않는 백업 형식입니다.');
    const clean={version:1,answers:{},notes:{},last:byId.has(raw.last)?raw.last:null};
    for (const [key,r] of Object.entries(raw.answers)) {
      if (!qmap.has(key) || !r || r.signature!==qmap.get(key)) continue;
      if (typeof r.correct!=='boolean' || !Number.isInteger(r.streak) || r.streak<0 || r.streak>5 || !Number.isFinite(r.due) || r.due<0 || !Number.isFinite(r.reviewed) || r.reviewed<0 || !Number.isInteger(r.attempts) || r.attempts<1 || r.attempts>1000000) throw Error('진도 값이 올바르지 않습니다.');
      clean.answers[key]={correct:r.correct,streak:r.streak,due:r.due,reviewed:r.reviewed,attempts:r.attempts,signature:r.signature};
    }
    for (const [id,n] of Object.entries(raw.notes)) {
      if (!byId.has(id)) continue;
      if (typeof n!=='string' || n.length>100000) throw Error('노트가 너무 길거나 잘못되었습니다.');
      clean.notes[id]=n;
    }
    return clean;
  }
  try { const raw=localStorage.getItem(KEY); if(raw)state=validate(JSON.parse(raw)); }
  catch(e) { tell('저장 진도를 읽지 못했습니다. 백업을 복원할 수 있습니다: '+e.message); }
  function save() {
    try { localStorage.setItem(KEY,JSON.stringify(state)); tell('이 브라우저에 저장했습니다.'); return true; }
    catch(e) { tell('브라우저 저장 실패. 현재 진도를 백업하세요: '+e.message); return false; }
  }
  function el(tag,text,cls) { const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(cls)e.className=cls; return e; }
  function stats() {
    const all=Object.values(state.answers), mastered=all.filter(r=>r.correct).length, due=all.filter(r=>r.due<=Date.now()).length;
    $('stats').replaceChildren(...[[lessons.length.toLocaleString(),'수업'],[bank.questions.toLocaleString(),'해설 있는 문제'],[mastered.toLocaleString(),'최근 정답'],[due.toLocaleString(),'복습 대기']].map(([n,t])=>{const d=el('div',undefined,'stat');d.append(el('b',n),document.createTextNode(t));return d;}));
  }
  function areas() {
    const track=$('track').value;
    const names=[...new Set(lessons.filter(l=>track==='all'||l.track===track).map(l=>l.area||'C 기초'))].sort();
    $('area').replaceChildren(Object.assign(el('option','전체 분야'),{value:''}),...names.map(n=>Object.assign(el('option',n),{value:n})));
  }
  const searchText=new Map(lessons.map(l=>[l.id,JSON.stringify([l.title,l.area,l.id,l.intro,l.guide,l.concepts,l.questions,l.path,l.beginner]).toLowerCase()]));
  function qualifies(l) {
    const track=$('track').value, area=$('area').value, term=$('search').value.trim().toLowerCase(), mode=$('mode').value;
    if(track!=='all'&&l.track!==track || area&&(l.area||'C 기초')!==area || term&&!searchText.get(l.id).includes(term))return false;
    return mode==='all'||l.questions.some((_,i)=>{const r=state.answers[`${l.id}:${i}`];return mode==='new'?!r:mode==='wrong'?r&&!r.correct:r&&r.due<=Date.now();});
  }
  function listing() {
    const matches=lessons.filter(qualifies);page=Math.min(page,Math.max(0,Math.ceil(matches.length/PAGE)-1));
    $('listCount').textContent=`${matches.length.toLocaleString()}개 수업 · ${matches.length?page+1:0}/${Math.ceil(matches.length/PAGE)}쪽`;
    $('list').replaceChildren(...matches.slice(page*PAGE,(page+1)*PAGE).map(l=>{
      const count=l.questions.filter((_,i)=>state.answers[`${l.id}:${i}`]?.correct).length;
      const b=el('button',`${l.id} · ${l.title}\n최근 정답 ${count}/${l.questions.length}`,'lesson-link');b.setAttribute('aria-current',String(selected?.id===l.id));b.onclick=()=>open(l.id);return b;
    }));
    if(!matches.length)$('list').append(el('p','조건에 맞는 수업이 없습니다. 검색어나 복습 필터를 바꿔보세요.','muted'));
    $('prevPage').disabled=page===0;$('nextPage').disabled=(page+1)*PAGE>=matches.length;
  }
  // Render authored nested learning material with text nodes only.
  function rich(parent,value) {
    if(value===null||value===undefined)return;
    if(typeof value==='string'||typeof value==='number'){parent.append(el('p',String(value)));return;}
    if(Array.isArray(value)){value.forEach(v=>rich(parent,v));return;}
    for(const [key,v] of Object.entries(value)){
      if(key==='title'||key==='heading')parent.append(el('h3',String(v)));
      else if(key==='command'||key==='code'||key==='diagram')parent.append(el('pre',typeof v==='string'?v:JSON.stringify(v,null,2)));
      else rich(parent,v);
    }
  }
  function detail(parent,title,value) {if(!value)return;const d=el('details');d.append(el('summary',title));rich(d,value);parent.append(d);return d;}
  function glossary(parent, terms, question=false) {
    if(!terms?.length)return;
    const d=el('details',undefined,'glossary');d.open=!question;
    d.append(el('summary',question?'문제에 나온 말 찾아보기':'이 수업의 낱말 사전'));
    if(!question){
      const label=el('label','모르는 말을 찾아보세요'),input=el('input');input.type='search';input.placeholder='예: 포인터, IRQ';label.append(input);d.append(label);
      input.oninput=()=>{for(const row of d.querySelectorAll('.glossary-entry'))row.hidden=!row.dataset.search.includes(input.value.trim().toLowerCase());};
    }
    const list=el('dl');
    for(const term of terms){const row=el('div',undefined,'glossary-entry');row.dataset.search=[term.term,...term.aliases,term.meaning].join(' ').toLowerCase();row.append(el('dt',term.aliases.join(' / ')),el('dd',term.meaning));list.append(row);}d.append(list);
    parent.append(d);
  }
  const glossaryPatterns=(bank.glossary||[]).map(t=>t.aliases.map(a=>new RegExp(/^[\x00-\x7F]+$/.test(a)?'(^|[^A-Za-z0-9_])'+a.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'($|[^A-Za-z0-9_])':a.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'i')));
  function questionTerms(q){const text=[q.prompt,...q.options,q.explanation].join(' ');return (bank.glossary||[]).filter((_,i)=>glossaryPatterns[i].some(p=>p.test(text)));}
  function rememberNote(){if(selected&&$('note').value!==state.notes[selected.id]){state.notes[selected.id]=$('note').value;save();}}
  function open(id) {
    rememberNote();selected=byId.get(id);if(!selected)return;
    state.last=id;save();location.hash=encodeURIComponent(id);
    const l=selected, box=$('lesson');box.classList.remove('hidden');box.replaceChildren();
    $('welcome').classList.add('hidden');
    const easy=$('readingMode').value==='easy';
    box.append(el('div',`${l.id} / ${l.area||'C 기초'}`,'tag'),el('h2',l.title));
    if(easy&&l.beginner){
      const b=el('section',undefined,'beginner');
      b.append(el('h3','생활 속에서 생각해 보기'),el('p',l.beginner.story),el('h3','컴퓨터에서는 이렇게 불러요'),el('p',l.beginner.meaning),el('h3','종이와 연필로 해 보기'),el('p',l.beginner.exercise));box.append(b);
    }else box.append(el('p',l.intro));
    if(easy&&!l.beginner)box.append(el('p','이 수업은 아직 전문 내용을 담고 있어요. 아래 낱말 사전을 보며 한 문장씩 읽어 보세요. 입문 30단계를 먼저 읽으면 도움이 됩니다. 쉬운 말로 고치는 작업이 더 필요합니다.','notice'));
    if(l.path)box.append(el('p','연결 소스: '+l.path+(l.excerpt?` · ${l.excerpt.start}–${l.excerpt.end}행`:''),'muted'));
    if(easy)glossary(box,(l.reading_aid?.terms||[]).map(i=>bank.glossary[i]));
    const concepts=easy&&l.beginner?el('details'):el('section');
    if(easy&&l.beginner)concepts.append(el('summary',l.easy_review?'코드를 한 단계씩 읽기':'더 깊이 읽기 · 원래 개념 설명'),el('p',l.intro));
    rich(concepts,l.guide);rich(concepts,l.concepts);box.append(concepts);
    const deep=detail(box,l.track==='files'?'파일 전체 해설 · 동작과 주의할 조건':'더 깊이 읽기 · 원리 설명',l.deep_dive);if(!easy&&l.track==='files'&&deep)deep.open=true;detail(box,'추가 읽기 도움말',l.reading_support);
    if(l.practice){const p=el('section');p.append(el('h3','직접 해보기'),el('p','아래 실습은 자동 실행되지 않습니다. Linux 명령은 Linux/WSL에서 실행하세요.','muted'));if(l.practice.command)p.append(el('pre',l.practice.command));if(l.practice.expected){const d=el('details');d.append(el('summary','예상 결과·확인 기준'));rich(d,l.practice.expected);p.append(d);}box.append(p);}
    detail(box,'단계별 원리 실험',l.experiment);
    if(l.technical_original){const old=l.technical_original;detail(box,'원래 전문 설명과 비교하기',{intro:old.intro,guide:old.guide,concepts:old.concepts,deep_dive:old.deep_dive,practice:old.practice,experiment:old.experiment,reading_support:old.reading_support});}
    if(l.annotated){const d=el('details');d.append(el('summary',l.source_review?'파일 전체 원본':'전체 코드 해설·주석 답지'),el('pre',l.annotated));box.append(d);}
    if(l.references){const d=el('details');d.append(el('summary','참고 자료'));for(const ref of l.references){const url=typeof ref==='string'?ref:(ref.url||ref.href);if(url&&/^https?:\/\//.test(url)){const a=el('a',typeof ref==='object'?(ref.title||url):url);a.href=url;a.target='_blank';a.rel='noopener noreferrer';d.append(a,el('br'));}else rich(d,ref);}box.append(d);}
    const practice=$('practice');practice.classList.remove('hidden');practice.replaceChildren(el('h2','문제 · 정답의 이유까지 확인하기'),el('p','답을 선택해 채점하거나 풀이를 먼저 볼 수 있습니다. 풀이 열람은 진도를 올리지 않습니다.','muted'));
    l.questions.forEach((q,i)=>renderQuestion(practice,l,q,i));
    const nav=el('div',undefined,'toolbar'),index=lessons.indexOf(l);
    for(const [label,target] of [['이전 수업',lessons[index-1]],['다음 수업',lessons[index+1]]]){const b=el('button',label);b.disabled=!target;b.onclick=()=>{open(target.id);$('lesson').scrollIntoView({behavior:'smooth'});};nav.append(b);}practice.append(nav);
    $('notes').classList.remove('hidden');$('note').value=state.notes[id]||'';listing();
  }
  function renderQuestion(parent,l,q,i) {
    const key=`${l.id}:${i}`, field=el('fieldset',undefined,'question'),legend=el('legend',`${i+1}. ${q.prompt}`);field.append(legend);
    const previous=state.answers[key];
    if(previous)field.append(el('p',`최근 ${previous.correct?'정답':'오답'} · ${previous.attempts}회 응시 · 복습 ${new Date(previous.due).toLocaleString('ko-KR')}`,'muted'));
    const radios=q.options.map((option,j)=>{const label=el('label',undefined,'option'),radio=document.createElement('input');radio.type='radio';radio.name=`q-${l.id}-${i}`;radio.value=j;label.append(radio,el('span',option));field.append(label);return radio;});
    const controls=el('div',undefined,'toolbar'),check=el('button','채점','primary'),retry=el('button','다시 풀기');retry.hidden=true;controls.append(check,retry);field.append(controls);
    const feedback=el('div');feedback.setAttribute('role','status');field.append(feedback);
    const solution=el('details');solution.append(el('summary','정답과 해설 보기'),el('p',`정답: ${q.options[q.answer]}`));
    const answer=el('div',undefined,'answer');
    // Paragraph breaks only: preserve every authored character and code token.
    if($('readingMode').value==='easy')for(const sentence of q.explanation.split(/(?<=[.!?])\s+(?=[가-힣A-Z0-9])/u))answer.append(el('p',sentence));
    else answer.append(el('p',q.explanation));
    solution.append(answer);field.append(solution);
    if(q.original_explanation)detail(solution,'원래 전문 해설과 비교하기',q.original_explanation);
    if($('readingMode').value==='easy')glossary(field,questionTerms(q),true);
    check.onclick=()=>{
      const choice=radios.findIndex(r=>r.checked);if(choice<0){feedback.textContent='답을 먼저 선택해 주세요.';return;}
      const correct=choice===q.answer, now=Date.now(), old=state.answers[key], sameDay=old&&new Date(old.reviewed).toDateString()===new Date(now).toDateString();
      const streak=correct?(sameDay&&old.correct?old.streak:Math.min(5,(old?.streak||0)+1)):0;
      state.answers[key]={correct,streak,due:correct?(sameDay&&old.correct?old.due:now+intervals[streak-1]*86400000):now+600000,reviewed:now,attempts:(old?.attempts||0)+1,signature:qmap.get(key)};
      feedback.className='feedback '+(correct?'correct':'incorrect');feedback.textContent=correct?'정답입니다. 이유를 자기 말로 설명해보세요.':'오답입니다. 선택한 답과 정답의 차이를 해설에서 확인하세요.';
      solution.open=true;check.disabled=true;radios.forEach(r=>r.disabled=true);retry.hidden=false;save();stats();listing();
    };
    retry.onclick=()=>{solution.open=false;check.disabled=false;retry.hidden=true;radios.forEach(r=>{r.disabled=false;r.checked=false;});feedback.textContent='';feedback.className='';};
    parent.append(field);
  }
  $('track').onchange=()=>{areas();page=0;listing();};$('area').onchange=$('mode').onchange=()=>{page=0;listing();};
  $('readingMode').onchange=()=>{if(selected)open(selected.id);};
  let searchTimer;$('search').oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{page=0;listing();},150);};
  $('prevPage').onclick=()=>{page--;listing();};$('nextPage').onclick=()=>{page++;listing();};
  $('begin').onclick=()=>open(lessons.find(l=>l.track==='foundations'&&l.questions.some((_,i)=>!state.answers[`${l.id}:${i}`]?.correct))?.id||'cs01');
  $('saveNote').onclick=()=>{rememberNote();save();};
  $('export').onclick=()=>{rememberNote();const blob=new Blob([JSON.stringify(state,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download='linux-cs-progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);tell('백업 파일을 내려받았습니다.');};
  $('import').onchange=async()=>{
    const file=$('import').files[0];if(!file)return;
    try{
      if(file.size>25000000)throw Error('백업 파일은 25MB 이하여야 합니다.');
      const imported=validate(JSON.parse(await file.text()));rememberNote();
      const merged={...state,answers:{...state.answers},notes:{...state.notes}};
      for(const [k,r]of Object.entries(imported.answers)){
        if(!merged.answers[k]||r.reviewed>merged.answers[k].reviewed)merged.answers[k]=r;
      }
      for(const [id,n]of Object.entries(imported.notes)){
        if(!merged.notes[id])merged.notes[id]=n;
        else if(n&&n!==merged.notes[id]&&!merged.notes[id].includes(n))merged.notes[id]+='\n\n[백업에서 복원]\n'+n;
      }
      state=validate(merged);
      const saved=save();
      if(selected){$('note').value=state.notes[selected.id]||'';open(selected.id);}
      stats();listing();
      tell(saved?'백업을 병합했습니다. 중복 문제는 더 최근 응시 기록을 유지합니다.':'백업은 메모리에 병합했지만 브라우저 저장에 실패했습니다. 다시 백업하세요.');
    }catch(e){tell('복원 실패: '+e.message);}finally{$('import').value='';}
  };
  $('note').maxLength=100000;
  window.addEventListener('beforeunload',rememberNote);
  window.addEventListener('hashchange',()=>{let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}if(byId.has(id)&&selected?.id!==id)open(id);});
  areas();stats();listing();
  let requested;try{requested=decodeURIComponent(location.hash.slice(1));}catch{requested='';}
  if(byId.has(requested))open(requested);else if(state.last)open(state.last);
})();
