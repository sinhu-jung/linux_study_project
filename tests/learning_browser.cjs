// Run after tools/build_learning.py. Requires Playwright, not needed by learners.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const root=path.resolve(__dirname,'..'), key='linux-cs-learning-v1';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.STUDY_BROWSER_CHANNEL?{channel:process.env.STUDY_BROWSER_CHANNEL}:{})});
 try {
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  const page=await context.newPage(), errors=[];page.on('pageerror',e=>errors.push(e.message));
  const url=pathToFileURL(path.join(root,'tools/learning.html')).href;
  await page.goto(url);await page.locator('#begin').click();
  await page.locator('#practice .question').first().locator('button').filter({hasText:/^채점$/}).click();
  assert.match(await page.locator('#practice .question').first().innerText(),/답을 먼저/);
  // Wrong answer creates a review item, revealing alone does not grade.
  let first=page.locator('#practice .question').first();
  await first.getByText('정답과 해설 보기',{exact:true}).click();
  assert.equal(await page.evaluate(k=>Object.keys(JSON.parse(localStorage.getItem(k)).answers).length,key),0);
  await first.locator('input').nth(0).check();await first.getByRole('button',{name:'채점',exact:true}).click();
  let record=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).answers['cs01:0'],key);
  assert.equal(record.correct,false);assert.equal(record.streak,0);assert.ok(record.due-record.reviewed===600000);
  await page.locator('#mode').selectOption('wrong');assert.match(await page.locator('#list').innerText(),/cs01/);
  await first.getByRole('button',{name:'다시 풀기',exact:true}).click();await first.locator('input').nth(1).check();await first.getByRole('button',{name:'채점',exact:true}).click();
  record=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).answers['cs01:0'],key);
  assert.equal(record.correct,true);assert.equal(record.streak,1);
  await first.getByRole('button',{name:'다시 풀기',exact:true}).click();await first.locator('input').nth(1).check();await first.getByRole('button',{name:'채점',exact:true}).click();
  assert.equal(await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).answers['cs01:0'].streak,key),1);
  // Navigation saves notes, reload retains grades and notes.
  await page.locator('#note').fill('테스트 노트 <script> 문자 그대로');await page.getByRole('button',{name:'다음 수업',exact:true}).click();
  await page.getByRole('button',{name:'이전 수업',exact:true}).click();assert.equal(await page.locator('#note').inputValue(),'테스트 노트 <script> 문자 그대로');
  await page.reload();assert.equal(await page.locator('#note').inputValue(),'테스트 노트 <script> 문자 그대로');
  const downloadPromise=page.waitForEvent('download');await page.locator('#export').click();const download=await downloadPromise;
  const backup=await fs.readFile(await download.path(),'utf8');assert.ok(JSON.parse(backup).answers['cs01:0'].correct);
  await page.evaluate(k=>localStorage.removeItem(k),key);await page.reload();
  await page.locator('#import').setInputFiles({name:'progress.json',mimeType:'application/json',buffer:Buffer.from(backup)});
  await page.waitForFunction(k=>JSON.parse(localStorage.getItem(k)||'{}').answers?.['cs01:0']?.correct,key);
  await page.locator('#import').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"version":999}')});
  await page.waitForFunction(()=>document.getElementById('status').textContent.includes('복원 실패'));
  assert.equal(await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).answers['cs01:0'].correct,key),true);
  // Review due date and question revision invalidation.
  await page.evaluate(k=>{let s=JSON.parse(localStorage.getItem(k));s.answers['cs01:0'].due=1;localStorage.setItem(k,JSON.stringify(s));},key);await page.reload();await page.locator('#mode').selectOption('due');
  assert.match(await page.locator('#list').innerText(),/cs01/);
  await page.evaluate(k=>{let s=JSON.parse(localStorage.getItem(k));s.answers['cs01:0'].signature='obsolete';localStorage.setItem(k,JSON.stringify(s));},key);await page.reload();await page.locator('#mode').selectOption('due');
  assert.match(await page.locator('#listCount').innerText(),/^0개/);
  // Every foundation plus representative lessons from every source part renders.
  const samples=await page.evaluate(()=>window.LEARNING_BANK.lessons.filter((l,i)=>l.track==='foundations'||l.track==='files'||l.easy_review||i%50===0||i===window.LEARNING_BANK.lessons.length-1).map(l=>({id:l.id,title:l.title,count:l.questions.length})));
  for(const l of samples){await page.evaluate(id=>location.hash=id,l.id);await page.waitForFunction(title=>document.querySelector('#lesson h2')?.textContent===title,l.title);assert.equal(await page.locator('#practice .question').count(),l.count);}
  await page.locator('#track').selectOption('files');await page.locator('#mode').selectOption('all');
  const fileCount=await page.evaluate(()=>window.LEARNING_BANK.whole_file_lessons);
  assert.match(await page.locator('#listCount').innerText(),new RegExp('^'+fileCount+'개'));
  await page.locator('#track').selectOption('all');await page.locator('#mode').selectOption('all');await page.locator('#search').fill('cs30');await page.waitForFunction(()=>document.querySelector('#listCount').textContent.startsWith('1개'));
  await page.locator('#list button').first().click();assert.match(await page.locator('#lesson h2').innerText(),/키·값/);
  assert.equal(await page.locator('#readingMode').inputValue(),'easy');
  assert.match(await page.locator('#lesson .beginner').innerText(),/이름표/);
  assert.ok(await page.locator('#lesson .glossary-entry').count()>0);
  assert.ok(await page.locator('#practice .question').first().locator('.glossary-entry').count()>0);
  const glossarySearch=page.locator('#lesson .glossary input');await glossarySearch.fill('메모리');
  assert.ok(await page.locator('#lesson .glossary-entry:visible').count()>0);
  await glossarySearch.fill('no-such-word-123');assert.equal(await page.locator('#lesson .glossary-entry:visible').count(),0);
  await glossarySearch.fill('');
  await page.locator('#readingMode').selectOption('technical');assert.equal(await page.locator('#lesson .beginner').count(),0);
  await page.locator('#readingMode').selectOption('easy');assert.equal(await page.locator('#lesson .beginner').count(),1);
  await page.screenshot({path:path.join(root,'data/learning-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(root,'data/learning-mobile.png'),fullPage:true});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({browser:'chromium',sampledLessons:samples.length,passed:['grading','reveal without credit','wrong filter','due filter','spaced repetition','notes','reload','backup roundtrip','invalid import rejection','revision invalidation','search','beginner mode','contextual glossary','glossary search','technical mode','desktop','mobile'],errors},null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
