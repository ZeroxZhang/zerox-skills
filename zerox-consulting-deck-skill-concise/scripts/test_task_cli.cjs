/* 实际CLI/Chrome验证任务选择继承；planner文件仅为路径夹具，不冒称选型通过。 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process'),{pathToFileURL}=require('node:url');
const contract=require('./report_contract.cjs');
const playwright=require(process.env.PLAYWRIGHT_MODULE||process.env.PLAYWRIGHT_PATH||'playwright');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-task-cli-'));
(async()=>{
 let browser;
 try{
  const source=path.join(dir,'source'),output=path.join(dir,'output'),moved=path.join(dir,'different','nested');
  for(const folder of [source,output,moved])fs.mkdirSync(folder,{recursive:true});
  const pages=path.join(source,'pages.html'),task=path.join(source,'task.json'),record=path.join(source,'planner-record.json'),deck=path.join(output,'deck.html'),copy=path.join(moved,'deck.html');
  fs.writeFileSync(record,JSON.stringify({synthetic:true,purpose:'Only test planner record path and digest preservation'}));
  fs.writeFileSync(path.join(source,'pages.json'),JSON.stringify({version:1,pages:[{page:1,proves:'合同继承与 4:3 模式切换',form:'html.text'}]}));
  fs.writeFileSync(pages,'<section class="slide" data-page-id="one" data-frame-boundary="space" data-form="html.text" data-proves="合同继承与 4:3 模式切换"><header class="slide__header"><h1 class="slide__title">Contract inheritance</h1></header><div class="slide__body"><p>Presentation at 4:3</p></div><div class="slide__page">1</div></section>');
  fs.writeFileSync(task,JSON.stringify({version:1,workMode:'editorial',complexity:'simple',majorConclusion:false,mode:'presentation',theme:'bcg',typography:'sans-presentation',ratio:'4x3',kind:'fragment',planner:{mode:'used',record:'planner-record.json'},pages:{record:'pages.json'}}));
  // 从与skill无关的工作目录调用真实CLI，仅合同提供风格与比例。
  const call=(script,args)=>execFileSync(process.execPath,[path.join(__dirname,script),...args],{cwd:dir,encoding:'utf8',env:process.env,maxBuffer:10*1024*1024});
  call('assemble_deck.cjs',[pages,deck,'--contract',task]);
  const assertTask=file=>{
   const value=contract.read(fs.readFileSync(file,'utf8'));
   for(const [key,expected] of Object.entries({mode:'presentation',theme:'bcg',typography:'sans-presentation',ratio:'4x3',complexity:'simple',reviewPolicy:'author'}))assert.equal(value[key],expected,key);
   assert.equal(path.resolve(path.dirname(file),value.planner.record),record,'planner引用原始实际文件');assert.equal(value.planner.sha256,contract.fileHash(record));
   return value;
  };
  const initial=assertTask(deck);
  call('apply_theme.cjs',[deck,copy]);
  const inherited=assertTask(copy);assert.notEqual(inherited.planner.record,initial.planner.record,'跨层目录移动必须重定位相对路径');
  browser=await playwright.chromium.launch({channel:process.env.CHROME_CHANNEL||'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:1400,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const file of [deck,copy]){
   await page.goto(pathToFileURL(file).href);await page.evaluate(async()=>{await window.deckReady;await document.fonts.ready;});
   const actual=await page.evaluate(()=>{const slide=document.querySelector('.slide');return {theme:document.documentElement.dataset.theme,typography:document.documentElement.dataset.typography,ratio:document.body.dataset.ratio,reading:slide.classList.contains('reading'),aspect:slide.offsetWidth/slide.offsetHeight,fonts:document.fonts.status,layoutCount:document.querySelectorAll('#deck-layouts').length,taskCount:document.querySelectorAll('#deck-task-contract').length};});
   assert.equal(actual.theme,'bcg');assert.equal(actual.typography,'sans-presentation');assert.equal(actual.ratio,'4x3');assert.equal(actual.reading,false);assert.ok(Math.abs(actual.aspect-4/3)<.001);assert.equal(actual.fonts,'loaded');assert.equal(actual.layoutCount,1);assert.equal(actual.taskCount,1);
  }
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({pass:true,cases:4,scope:'real CLI assembly, contract inheritance, planner path/digest relocation, actual Chrome mode/theme/type/ratio; no planner quality claim'}));
 }finally{if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
