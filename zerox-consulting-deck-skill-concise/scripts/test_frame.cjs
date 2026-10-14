/* 母版开发回归：选择继承、几何不变、语义线保留、主题与画幅、打印。 */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const frame=require('./apply_frame.cjs'),themes=require('../assets/deck-themes.js');
let pw;try{pw=require('playwright')}catch{pw=require(process.env.PLAYWRIGHT_MODULE)}
const source=`<!DOCTYPE html><html><head><style>
*{box-sizing:border-box;margin:0;padding:0}.slide{position:relative;display:flex;flex-direction:column;width:1280px;height:720px;padding:32px 40px 26px;background:var(--page-bg);color:var(--ink)}
.slide__title{font:700 30px/1.22 Arial;margin-bottom:8px}.slide__lead{font:16px/1.45 Arial}.slide__body{margin-top:16px;flex:1;min-height:0}.slide__page{position:absolute;right:40px;bottom:18px}
.semantic-line{border-top:3px solid var(--accent)}.slide__tracker{position:absolute;top:12px;left:40px}
</style></head><body><section class="slide reading">
${frame.markup}<div class="slide__tracker">章节</div><header class="slide__header"><h1 class="slide__title">Title with <em>authored emphasis</em></h1><p class="slide__lead">Scope and evidence</p></header>
<div class="slide__body"><div class="semantic-line">正文结构线</div><svg width="240" height="100"><path d="M0 20H220" stroke="red"/><text x="10" y="70">Data 42</text></svg></div><div class="slide__page">01</div></section></body></html>`;
const framed=frame.apply(source);
assert.equal(frame.apply(framed),framed,'重复注入必须幂等');
assert.equal((framed.match(/id="deck-frame"/g)||[]).length,1);
assert.ok(framed.includes(source.match(/<section[\s\S]*?<\/section>/)[0]),'样式注入不可改正文');
const unquoted=source.replace('<html>','<html data-frame=off data-frame-version=old>');
assert.match(frame.apply(unquoted),/<html data-frame="off" data-frame-version="1\.0\.0">/);
assert.equal((frame.apply(unquoted).match(/<html\b[^>]*>/i)[0].match(/data-frame=/g)||[]).length,1);
assert.match(frame.apply(frame.apply(source,{style:'off'})),/data-frame="off"/);
assert.match(frame.apply(frame.apply(source,{style:'off'}),{style:'quiet'}),/data-frame="quiet"/);
assert.throws(()=>frame.apply(source,{style:'bright'}),/quiet \/ off/);
assert.equal(frame.apply(fs.readFileSync(path.join(__dirname,'../assets/deck_engine.html'),'utf8')),fs.readFileSync(path.join(__dirname,'../assets/deck_engine.html'),'utf8'),'引擎母版副本须同步：引擎是 apply_frame 的构建产物，运行 node scripts/sync_frame.cjs 重新同步后再提交');
(async()=>{
 const browser=await pw.chromium.launch({channel:'chrome',headless:true});
 try{
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const theme of themes.ids){
   for(const width of [1280,1024]){
    await page.setContent(themes.apply(framed,theme));
    await page.evaluate(w=>{const s=document.querySelector('.slide');s.style.width=w+'px';s.style.height=(w===1280?720:768)+'px';},width);
    const geometry=()=>page.evaluate(()=>[...document.querySelectorAll('.slide__title,.slide__lead,.slide__body,.semantic-line,svg,.slide__page')].map(e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]}));
    const before=await geometry();
    await page.evaluate(()=>{const h=document.querySelector('.slide__header');h.replaceWith(...h.childNodes)});
    assert.deepEqual(await geometry(),before,`${theme}/${width}：标题组不得挤占正文`);
    await page.setContent(themes.apply(framed,theme));
    await page.evaluate(w=>{const s=document.querySelector('.slide');s.style.width=w+'px';s.style.height=(w===1280?720:768)+'px';},width);
    const state=()=>page.evaluate(()=>{const s=document.querySelector('.slide'),h=s.querySelector('.slide__header'),f=s.querySelector('.slide__frame'),c=getComputedStyle(h,'::after');const rgb=color=>{const ctx=document.createElement('canvas').getContext('2d');ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].slice(0,3)};return {line:c.content,display:getComputedStyle(f).display,pointer:getComputedStyle(f).pointerEvents,color:rgb(c.backgroundColor),accent:rgb(getComputedStyle(s.querySelector('.semantic-line')).borderTopColor),semantic:getComputedStyle(s.querySelector('.semantic-line')).borderTopWidth,hidden:f.getAttribute('aria-hidden')}});
    let current=await state();assert.equal(current.line,'""');assert.equal(current.display,'block');assert.equal(current.pointer,'none');assert.equal(current.hidden,'true');
    assert.notDeepEqual(current.color,current.accent);
    assert.ok(current.color.reduce((a,b)=>a+b)>current.accent.reduce((a,b)=>a+b),'白底主题的装饰须弱于正文强调色');
    // 作者样式即使先于母版注入，也应覆盖默认位置。
    await page.evaluate(()=>{const style=document.createElement('style');style.textContent='.slide.reading{--frame-rule-offset:7px}';document.head.prepend(style)});
    assert.equal(await page.locator('.slide__header').evaluate(h=>getComputedStyle(h,'::after').bottom),'7px');
    for(const boundary of ['integrated','space']){
     await page.locator('.slide').evaluate((s,v)=>s.dataset.frameBoundary=v,boundary);
     current=await state();assert.equal(current.line,'none');assert.equal(current.semantic,'3px');assert.equal(current.display,'block');
    }
    await page.locator('.slide').evaluate(s=>{delete s.dataset.frameBoundary;s.dataset.frame='off'});
    assert.equal((await state()).display,'none');assert.equal((await state()).line,'none');
    await page.evaluate(()=>{document.documentElement.dataset.frame='off';document.querySelector('.slide').dataset.frame='quiet'});
    assert.equal((await state()).display,'block');assert.equal((await state()).line,'""');
    await page.emulateMedia({media:'print'});assert.equal((await state()).display,'block');assert.equal((await state()).line,'""');await page.emulateMedia({media:'screen'});
   }
  }
  assert.deepEqual(errors,[]);console.log('PASS: 母版幂等、正文不变、主题/画幅、边界合并、逐页启停、无点击拦截与打印样式。');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
