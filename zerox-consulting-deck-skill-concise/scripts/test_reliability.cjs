const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {pathToFileURL}=require('node:url'),{execFileSync}=require('node:child_process');
const {aggregate,inspectCoverage}=require('./aggregate_reviews.cjs');
const geometry=require('./browser_geometry_audit.cjs'),rows=require('./render_comparison_rows.cjs'),{pack}=require('./pack_fonts.cjs');
const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const saved=process.argv[2],dir=saved?path.resolve(saved):fs.mkdtempSync(path.join(os.tmpdir(),'deck-reliability-'));fs.mkdirSync(dir,{recursive:true});
 const browser=await pw.chromium.launch({channel:'chrome',headless:true});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:900}}),results={};
  await p.route('https://cdn.jsdelivr.net/npm/echarts@*/dist/echarts.min.js',r=>r.fulfill({path:require.resolve('echarts/dist/echarts.min.js'),contentType:'application/javascript'}));
  const spec={id:'precision',domain:[-150,3000],columns:[{key:'label',label:'品类'},{key:'value',label:'数值'},{key:'bar',label:'共同量尺'},{key:'cycle',label:'周期'},{key:'team',label:'团队'}],rows:[{label:'中文与 AI Revenue 长标签\n换行保留首行关系',value:10.25,cycle:'按天',team:'1–2人'},{label:'负值与混排',value:-125.75,cycle:'2–4周\n估计',team:'3–10人'},{label:'3D 漫剧',value:2250,cycle:'周级',team:'10人+'},{label:'仿真人精品漫剧',value:3000,cycle:'周级',team:'10人+'}]};
  assert.match(rows.render({...spec,decimals:2,rows:[{...spec.rows[0],value:.00015}]}),/0\.00015/);
  assert.doesNotThrow(()=>rows.render({...spec,domain:undefined,rows:[{...spec.rows[0],value:0}]}));
  const css=fs.readFileSync(path.resolve(__dirname,'../assets/deck-geometry.css'),'utf8');
  const html=pack(`<html><head><style>*{box-sizing:border-box}body{margin:0}.slide{width:1280px;height:720px;padding:40px;font-family:var(--font-body);font-size:16px;--gray-3:#ddd;--gray-2:#50606E;--brand:#000080}.precision-row:nth-child(3){font-weight:600}${css}</style></head><body><section class="slide active">${rows.render(spec)}</section><script>window.deckReady=DeckTypography.ready(document);</script></body></html>`,{profile:'serif-report-bold'});
  const file=path.join(dir,'representative.html');fs.writeFileSync(file,html);await p.goto(pathToFileURL(file).href);await geometry.settle(p);
  const measure=()=>p.locator('.slide').evaluate(geometry.inspectSlide);
  results.mixed=await measure();assert.equal(results.mixed.status,'PASS',JSON.stringify(results.mixed.errors));
  await p.locator('.slide').screenshot({path:path.join(dir,'representative.png')});
  await p.locator('.slide').evaluate(e=>e.style.zoom=2);results.zoom=await measure();assert.equal(results.zoom.status,'PASS');await p.locator('.slide').evaluate(e=>e.style.zoom='');
  await p.locator('[data-geo-baseline]').nth(1).evaluate(e=>e.style.transform='translateY(2px)');results.injected=await measure();assert.equal(results.injected.status,'FAIL');assert.ok(results.injected.errors.some(e=>e.code==='G-ALIGN'&&e.spread>=1.99));
  await p.locator('[data-geo-baseline]').nth(1).evaluate(e=>e.style.transform='');results.restored=await measure();assert.equal(results.restored.status,'PASS');
  await p.locator('[data-geo-bar]').first().evaluate(e=>e.style.width='25%');results.badMapping=await measure();assert.ok(results.badMapping.errors.some(e=>e.code==='G-MAPPING'));
  await p.goto(pathToFileURL(file).href);await geometry.settle(p);await p.emulateMedia({media:'print'});results.print=await measure();assert.equal(results.print.status,'PASS');await p.pdf({path:path.join(dir,'representative.pdf'),width:'1280px',height:'720px',printBackground:true});await p.emulateMedia({media:'screen'});
  // 已知4px旧缺陷：只增加观察锚点，不修改其CSS或文本。
  const known=path.resolve(__dirname,'../_local/review_visual_reliability_2026-09-08/final-html-audit');
  for(const [name,source] of [['knownBefore','baseline-evidence/before.html'],['knownAfter','composition-demo.html']])if(fs.existsSync(path.join(known,source))){
   await p.goto(pathToFileURL(path.join(known,source)).href);await p.evaluate(()=>document.fonts.ready);
   await p.evaluate(()=>document.querySelectorAll('.data-row').forEach((r,i)=>{const c=[...r.children];[r.querySelector('.category')||c[0],r.querySelector('.value'),r.querySelector('.cycle')||c[2],r.querySelector('.team')||c[3]].forEach(e=>e.dataset.geoBaseline='known-'+i);}));
   results[name]=await measure();assert.equal(results[name].status,name==='knownBefore'?'FAIL':'PASS');
   if(name==='knownBefore')assert.ok(results[name].errors.some(e=>e.spread>=3.99));
  }
  // 初始化应自己装配关键CSS，实测计算样式，而非只找字符串。
  const init=path.join(dir,'init.html');execFileSync(process.execPath,[path.join(__dirname,'apply_theme.cjs'),path.resolve(__dirname,'../assets/deck_engine.html'),init,'mckinsey','serif-report-bold'],{env:process.env});
  await p.goto(pathToFileURL(init).href);await geometry.settle(p);
  results.initialization=await p.evaluate(()=>{const d=document.createElement('div');d.className='layout-split';document.body.append(d);const c=getComputedStyle(d),r={display:c.display,columns:c.gridTemplateColumns,copies:document.querySelectorAll('#deck-layouts').length};d.remove();return r;});assert.equal(results.initialization.display,'grid');assert.equal(results.initialization.copies,1);
  const evidence=path.join(dir,'representative.png'),audit={pages:2,htmlArtifact:{sha256:'h'},pdfArtifact:{sha256:'p'}};
  const one=role=>({status:'complete',htmlSha256:'h',pdfSha256:'p',coverage:[{reviewer:role,independence:role,layers:['page','exhibit','annotation','typography'],htmlPages:[1,2],pdfPages:[1,2],evidence:[{path:evidence,sha256:sha(fs.readFileSync(evidence))}]}],issues:[],checks:Object.fromEntries(['analysis','evidence','visual'].map(k=>[k,{status:'pass',basis:'自动测试夹具，不代表实际人工验收'}]))});
  const author=one('author'),independent=one('independent');assert.equal(aggregate(audit,[author,independent],{requireIndependent:true}).status,'complete');
  for(const [name,input] of [['natural',[author,'检查无问题']],['missingPage',[author,{...independent,coverage:[{...independent.coverage[0],pdfPages:[1]}]}]],['shrunk',[author,{...independent,coverage:[{...independent.coverage[0],layers:['annotation']}]}]],['stale',[author,{...independent,htmlSha256:'old'}]],['missingResult',[author,null]]]){
   const r=aggregate(audit,input,{requireIndependent:true});assert.equal(r.status,'incomplete',name);(results.aggregation??={})[name]=r.aggregationErrors;
  }
  results.pass=true;results.browser=browser.version();fs.writeFileSync(path.join(dir,'test-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify({pass:true,evidence:dir,known4px:results.knownBefore?.errors,injected2px:results.injected.errors}));
 }finally{await browser.close();if(!saved)fs.rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
