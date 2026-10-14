/* 实际加载主题引擎与共用runtime，检查九种配方的浏览器/SSR一致性。 */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url'),{execFileSync}=require('node:child_process');
const themes=require('../assets/deck-themes.js'),cases=require('../assets/recipe-examples.json'),{render}=require('./render_echarts_svg.cjs');
const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-themes-')),browser=await pw.chromium.launch({channel:'chrome',headless:true});
 try{
  for(const id of themes.ids){
   const file=path.join(dir,id+'.html');
   execFileSync(process.execPath,[path.resolve(__dirname,'apply_theme.cjs'),path.resolve(__dirname,'../assets/deck_engine.html'),file,id]);
   const p=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];
   p.on('pageerror',e=>errors.push(e.message));
   await p.route('https://cdn.jsdelivr.net/npm/echarts@*/dist/echarts.min.js',route=>route.fulfill({path:require.resolve('echarts/dist/echarts.min.js'),contentType:'application/javascript'}));
   await p.goto(pathToFileURL(file).href+'#3');await p.evaluate(()=>window.deckReady);await p.waitForFunction(()=>window.ChartRuntime&&document.querySelector('.slide.active .chart svg'));
   assert.equal(await p.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()),themes.get(id).tokens.accent);
   for(const [name,spec] of Object.entries(cases)){
    const server=render({recipe:name,spec,theme_id:id,width:720,height:360});
    const result=await p.evaluate(({name,spec,tokens})=>{
     let plan=ChartRuntime.prepare(name,spec,{tokens,width:720,height:360});
     const el=document.createElement('div');el.style='position:fixed;left:0;top:0;width:720px;height:360px;background:white';document.body.appendChild(el);
     const c=echarts.init(el,null,{renderer:'svg'});c.setOption(plan.pages[0].option);
     const report=ChartRuntime.check(c,plan);
     const text=[...el.querySelectorAll('text')].map(t=>t.textContent),bad=[];
     for(const t of el.querySelectorAll('text')){const r=t.getBoundingClientRect(),b=el.getBoundingClientRect();if(r.left<b.left-1||r.right>b.right+1||r.top<b.top-1||r.bottom>b.bottom+1)bad.push(t.textContent);}
     const colors=name==='sankey'?plan.pages[0].option.series[0].data.map(d=>d.itemStyle.color):[];
     const out={status:report.status,problems:report.problems,text,bad,colors};c.dispose();el.remove();return out;
    },{name,spec,tokens:themes.get(id).tokens});
    assert.equal(result.status,'ok',id+' '+name+'浏览器实测未通过：'+JSON.stringify(result.problems));
    assert.equal(server.report.status,'ok');assert.equal(server.pages[0].kind,'chart');
    const serverTexts=[...server.pages[0].svg.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m=>m[1]);
    assert.deepEqual(result.text.slice().sort(),serverTexts.sort(),id+' '+name+'文本路径不同');
    assert.deepEqual(result.bad,[],id+' '+name+'浏览器标签越界');
    if(name==='sankey')assert.equal(result.colors[0],themes.get(id).tokens.accent);
   }
   assert.deepEqual(errors,[]);await p.close();
  }
  console.log('PASS: 3主题×9配方，浏览器实际加载、SSR文字一致、标签边界、Sankey实体色');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
