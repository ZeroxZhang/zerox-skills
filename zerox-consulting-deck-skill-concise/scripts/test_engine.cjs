/* 真实 Chromium 验证引擎；PLAYWRIGHT_PATH 可覆盖本机依赖路径。 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
let pw;try{pw=require('playwright')}catch(e){const modulePath=process.env.PLAYWRIGHT_MODULE||process.env.PLAYWRIGHT_PATH;if(!modulePath)throw Error('请安装playwright或设置PLAYWRIGHT_MODULE');pw=require(modulePath)}
const {chromium}=pw;
const {pathToFileURL}=require('node:url');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-engine-test-'));
 try {
  const page=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const engine=path.resolve(__dirname,'../assets/deck_engine.html');
  await page.goto(pathToFileURL(engine).href+'#3');
  await page.waitForFunction(()=>window.echarts&&window.EChartsRecipes&&document.querySelector('.slide.active .chart svg'));
  assert.equal(await page.locator('.slide.active .slide__page').textContent(),'3');
  assert.equal(await page.locator('.chart canvas').count(),0);
  assert.equal(await page.locator('#download-pdf').isHidden(),true);
  assert.equal(await page.locator('#print-pdf').isEnabled(),true);
  assert.equal(await page.evaluate(()=>{const nativePrint=window.print;window.print=()=>{window.__printRequested=true};document.getElementById('print-pdf').click();window.print=nativePrint;return window.__printRequested}),true);
  assert.match(await page.evaluate(()=>echarts.version),/^6\./);
  assert.equal(await page.evaluate(()=>EChartsRecipes.version),'1.1.0');
  assert.equal(await page.locator('.slide.active .chart').getAttribute('data-recipe'),'rankedBar');
  await page.evaluate(()=>{location.hash='#6';});await page.waitForFunction(()=>document.querySelector('.slide.active .slide__page').textContent==='6');
  await page.evaluate(()=>{location.hash='#3';});await page.waitForFunction(()=>document.querySelector('.slide.active .slide__page').textContent==='3');
  const geometry=await page.evaluate(()=>{
   const opt=DeckRecipes.buildWaterfall([{name:'起点',type:'abs',value:10},{name:'跨零',type:'delta',value:-15},{name:'恢复',type:'delta',value:8},{name:'小计',type:'subtotal'},{name:'期末',type:'total',value:3}]);
   const outputs=opt.series[0].data.map(d=>opt.series[0].renderItem({}, {value:i=>d.value[i],coord:v=>[v[0]*100+50,300-v[1]*10],size:()=>[100,0]}));
   let rejects=false;try{DeckRecipes.buildWaterfall([{type:'abs',value:5},{type:'total',value:8}]);}catch(e){rejects=true;}
   return {values:opt.series[0].data.map(d=>d.value),shapes:outputs.map(g=>g.children[0].shape),rejects,animation:opt.animation};
  });
  assert.deepEqual(geometry.values[1].slice(1,3),[10,-5]);
  assert.equal(geometry.shapes[1].y,200);assert.equal(geometry.shapes[1].height,150);
  assert.equal(geometry.shapes[2].y,270);assert.equal(geometry.shapes[2].height,80);
  assert.equal(geometry.values[4][2],3);assert.ok(geometry.rejects);assert.equal(geometry.animation,false);
  await page.keyboard.press('g');assert.ok(await page.locator('body').evaluate(e=>e.classList.contains('overview')));
  assert.equal(await page.locator('.slide:visible').count(),7);
  await page.keyboard.press('Escape');assert.equal(await page.locator('.slide:visible').count(),1);
  await page.keyboard.press('ArrowRight');assert.match(page.url(),/#4$/);
  const wf=await page.locator('#waterfall-demo').evaluate(el=>({renderer:el._chart.getZr().painter.getType(),data:el._chart.getOption().series[0].data}));
  assert.equal(wf.renderer,'svg');assert.ok(Math.abs(wf.data[3].value[2]-10.4)<1e-8);
  await page.setViewportSize({width:800,height:600});
  await page.waitForFunction(()=>Number(document.getElementById('stage').style.getPropertyValue('--scale'))<1);
  const scale=await page.locator('#stage').evaluate(el=>Number(el.style.getPropertyValue('--scale')));assert.ok(scale>0&&scale<1);
  const displays=await page.locator('.slide').evaluateAll(es=>es.map(e=>e.style.display));
  await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));
  assert.equal(await page.locator('.slide:visible').count(),7);
  const sizes=await page.locator('.chart').evaluateAll(es=>es.map(e=>({width:e.clientWidth,chartWidth:e._chart.getWidth(),height:e.clientHeight,chartHeight:e._chart.getHeight()})));
  sizes.forEach(s=>{assert.ok(s.width>0&&s.height>0);assert.equal(s.width,s.chartWidth);assert.equal(s.height,s.chartHeight);});
  await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
  assert.deepEqual(await page.locator('.slide').evaluateAll(es=>es.map(e=>e.style.display)),displays);
  const pdf=path.join(dir,'16x9.pdf');await page.pdf({path:pdf,preferCSSPageSize:true,printBackground:true});
  assert.match(execFileSync('pdfinfo',[pdf],{encoding:'utf8'}),/Pages:\s+7/);
  fs.copyFileSync(path.resolve(__dirname,'../assets/echarts-recipes.js'),path.join(dir,'echarts-recipes.js'));
  fs.copyFileSync(path.resolve(__dirname,'../assets/chart-runtime.js'),path.join(dir,'chart-runtime.js'));
  const four=path.join(dir,'4x3.html');fs.writeFileSync(four,require('./pack_fonts.cjs').pack(fs.readFileSync(engine,'utf8').replace('<body data-ratio="16x9">','<body data-ratio="4x3">')));
  await page.goto(pathToFileURL(four).href+'#4');await page.waitForFunction(()=>window.echarts&&document.querySelector('#waterfall-demo svg'));
  assert.equal(await page.locator('#stage').evaluate(el=>getComputedStyle(el).width),'1024px');
  const pdf43=path.join(dir,'4x3.pdf');await page.pdf({path:pdf43,preferCSSPageSize:true,printBackground:true});
  const info=execFileSync('pdfinfo',[pdf43],{encoding:'utf8'});assert.match(info,/Pages:\s+7/);assert.match(info,/Page size:\s+768 x 576 pts/);
  await page.emulateMedia({media:'print'});assert.equal(await page.locator('#deck-actions').evaluate(e=>getComputedStyle(e).display),'none');await page.emulateMedia({media:'screen'});
  // 打印尺寸下实测不过关时只报具体问题：不产出替代表，也不留下能被当成成稿的图形。
  const failure=await page.evaluate(()=>{
   let root={label:'末级数据业务流程'};for(let i=8;i>=1;i--)root={label:'第'+i+'层业务处理步骤',children:[root]};
   const el=document.createElement('div');el.className='chart';el.style='position:fixed;left:0;top:0;width:720px;height:200px';el.dataset.recipe='tree';el.dataset.spec=JSON.stringify({root});document.body.appendChild(el);
   window.dispatchEvent(new Event('beforeprint'));
   const out={error:el.dataset.chartError||null,kind:el.dataset.renderKind||null,hasPlan:!!el._plan,html:el.innerHTML};
   if(el._chart)el._chart.dispose();el.remove();window.dispatchEvent(new Event('afterprint'));return out;
  });
  assert.match(failure.error||'',/文字验收未通过[\s\S]*(bounds|overlap|font)/,'实测不过关必须报出具体问题');
  assert.equal(failure.kind,null);assert.equal(failure.hasPlan,false);
  assert.doesNotMatch(failure.html,/<table|完整数据表/,'失败不能留下替代表格');
  assert.deepEqual(errors,[]);
  console.log('PASS: ECharts 6 recipe, signed waterfall geometry, total closure, SVG, #3, G/Escape, resize, print restoration, 16:9 and 4:3 PDFs. 临时产物已清理。'+'');
 } finally {await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
