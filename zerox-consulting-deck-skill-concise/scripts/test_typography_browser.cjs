/* 捕捉“CSS 看似正确但字体没加载”、DM 伪粗、图表回退字体和离线 PDF 漂移。 */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process'),{pathToFileURL}=require('node:url');
const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{const browser=await pw.chromium.launch({channel:'chrome',headless:true}),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'typography-browser-'));
try{
 const p=await browser.newPage();await p.route('https://cdn.jsdelivr.net/npm/echarts@*/dist/echarts.min.js',r=>r.fulfill({path:require.resolve('echarts/dist/echarts.min.js'),contentType:'application/javascript'}));
 await p.goto(pathToFileURL(path.resolve(__dirname,'../assets/deck_engine.html')).href);await p.evaluate(()=>document.fonts.ready);
 assert.equal(await p.evaluate(()=>document.documentElement.dataset.fontStatus),'ready','生产入口必须先完成字体门禁');
 const {pack}=require('./pack_fonts.cjs');
 const fixtures='<h1 class="slide__title">收入增长13%：Revenue grows</h1><h2>经营复核</h2><p class="body-copy">中文收入 Revenue 2026</p><p class="case-copy" style="text-transform:uppercase">zebra quux</p><div class="num"><span id="n1">1111.00</span><span id="n2">8888.00</span></div><svg width="400" height="100"><text x="5" y="30" style="font-family:var(--font-body);font-size:16px">经营收入 Revenue 1234</text></svg>';
 const template='<html lang="zh-CN"><head><style>.slide{width:1200px;transform:scale(1.05);transform-origin:top left}.num span{display:inline-block}</style></head><body><section class="slide active">'+fixtures+'</section><script>window.deckReady=DeckTypography.ready(document).then(s=>(window.__deckFontState=s));</script></body></html>';
 for(const profile of ['serif-report','serif-playfair','sans-presentation','serif-report-bold']){
  const file=path.join(tmp,profile+'.html');fs.writeFileSync(file,pack(template,{profile}));const q=await browser.newPage();await q.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());await q.goto(pathToFileURL(file).href);await q.evaluate(()=>window.deckReady);
  const check=await q.evaluate(()=>({state:document.documentElement.dataset.fontStatus,weight:getComputedStyle(document.querySelector('.type-latin')).fontWeight,synthesis:getComputedStyle(document.querySelector('h1')).fontSynthesis,widths:['n1','n2'].map(id=>document.getElementById(id).getBoundingClientRect().width)}));
  assert.equal(check.state,'ready');assert.equal(check.weight,profile==='serif-report'?'400':profile==='serif-playfair'?'500':profile==='serif-report-bold'?'700':'600');assert.equal(check.synthesis,'none');assert.ok(Math.abs(check.widths[0]-check.widths[1])<.05,'数据数字必须等宽');
  const glyphX=await q.locator('svg text').evaluate(e=>e.getStartPositionOfChar(0).x);assert.ok(Math.abs(glyphX-5)<.05,'缩放不能改变SVG字形的逻辑坐标');
  const cdp=await q.context().newCDPSession(q);await cdp.send('DOM.enable');await cdp.send('CSS.enable');const {root}=await cdp.send('DOM.getDocument');
  for(const selector of ['h1','.body-copy','.case-copy','svg text']){const {nodeId}=await cdp.send('DOM.querySelector',{nodeId:root.nodeId,selector});const {fonts}=await cdp.send('CSS.getPlatformFontsForNode',{nodeId});assert.ok(fonts.length);assert.ok(fonts.every(f=>f.isCustomFont),'实际使用了系统回退: '+selector+' '+JSON.stringify(fonts));}
  const pdf=path.join(tmp,profile+'.pdf');await q.pdf({path:pdf});const info=execFileSync('pdffonts',[pdf],{encoding:'utf8'});assert.match(info,/DMSerif|Playfair|Inter/);for(const row of info.split('\n').slice(2).filter(Boolean))assert.match(row,/\s+yes\s+yes\s+yes\s+/,'PDF 字体必须嵌入、子集化且可映射字符');
  await q.close();
 }
 const audit=require('./browser_font_audit.cjs'),wrong=await browser.newPage();await wrong.goto(pathToFileURL(path.join(tmp,'serif-report.html')).href);await wrong.evaluate(()=>window.deckReady);await wrong.locator('.body-copy').evaluate(e=>e.style.fontFamily="'Deck DM Serif Text','Deck Noto Serif SC',serif");assert.equal((await audit.inspect(wrong)).identity,'FAIL','已加载但角色错误的字体也必须拒绝');await wrong.close();
 const broken=path.join(tmp,'broken.html');fs.writeFileSync(broken,pack(template,{profile:'serif-report'}).replace(/data:font\/woff2;base64,[A-Za-z0-9+/=]+/,'data:font/woff2;base64,AAAA'));const bad=await browser.newPage();await bad.goto(pathToFileURL(broken).href);const refusal=await bad.evaluate(async()=>{try{await window.deckReady;return false;}catch{return document.documentElement.dataset.fontStatus==='error';}});assert.ok(refusal,'字体失败必须阻止正式就绪');await bad.close();
 console.log('PASS: 生产字体门禁；四配置真实中西文字体、字重、数字等宽、断网和 PDF 嵌入；坏字体拒绝；'+tmp);
}finally{await browser.close();fs.rmSync(tmp,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1;});
