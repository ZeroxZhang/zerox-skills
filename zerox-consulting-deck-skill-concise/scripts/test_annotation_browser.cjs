/* 独立读取浏览器实际 SVG：锚点声明必须等于真实几何，引线端点必须落在声明边界上。 */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url'),{execFileSync}=require('node:child_process');
const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');

async function audit(page){return page.evaluate(()=>{
  const close=(a,b,t)=>Math.abs(a-b)<=t;
  const overlap=(a,b,t=0)=>a.x<b.x+b.width-t&&a.x+a.width-t>b.x&&a.y<b.y+b.height-t&&a.y+a.height-t>b.y;
  const inside=(box,vb,t=.5)=>box.x>=vb.x-t&&box.y>=vb.y-t&&box.x+box.width<=vb.x+vb.width+t&&box.y+box.height<=vb.y+vb.height+t;
  const edgeDistance=(p,b)=>{const dx=Math.max(b.x-p.x,0,p.x-(b.x+b.width)),dy=Math.max(b.y-p.y,0,p.y-(b.y+b.height));return Math.hypot(dx,dy);};
  const findings=[];
  for(const svg of document.querySelectorAll('svg[data-exhibit-type],svg[data-typography]')){
    const section=svg.closest('.card')||svg.parentElement,name=(section.querySelector('h2')||{}).textContent||'exhibit';
    const vb=svg.viewBox.baseVal,issues=[];
    // getBBox() 给的是元素自己坐标系里的框：既不含元素自身的 transform，也不含祖先 <g> 的位移。
    // 声明框是根坐标（引线与标注就画在根上），所以量到的几何一律换算到根空间再比；
    // 对没有 transform、也不在 <g> 里的图元，这个换算是恒等变换。
    const toRoot=(el,p)=>new DOMPoint(p.x,p.y).matrixTransform(el.getScreenCTM()).matrixTransform(svg.getScreenCTM().inverse());
    const rootBox=el=>{const b=el.getBBox(),a=toRoot(el,{x:b.x,y:b.y}),z=toRoot(el,{x:b.x+b.width,y:b.y+b.height});return {x:a.x,y:a.y,width:z.x-a.x,height:z.y-a.y};};
    const texts=[...svg.querySelectorAll('text')].map(el=>({el,id:el.dataset.annotationId||el.dataset.labelId||el.textContent.slice(0,12),annotation:el.dataset.role==='annotation',box:rootBox(el)}));
    const anchorEls=[...svg.querySelectorAll('[data-anchor-id]')];
    // 1. 锚点声明必须等于真实图元几何，不能只写不实。
    for(const el of anchorEls){
      const declared=(el.dataset.anchorBox||'').split(',').map(Number);
      if(declared.length!==4||!declared.every(Number.isFinite)){issues.push({code:'anchor-box-missing',anchor:el.dataset.anchorId});continue;}
      const real=rootBox(el);
      if(!close(declared[0],real.x,.5)||!close(declared[1],real.y,.5)||!close(declared[2],real.width,.5)||!close(declared[3],real.height,.5))
        issues.push({code:'anchor-box-untrue',anchor:el.dataset.anchorId,declared,real:{x:real.x,y:real.y,width:real.width,height:real.height}});
    }
    const anchors={};for(const el of anchorEls)anchors[el.dataset.anchorId]={el,x:+el.dataset.anchorX,y:+el.dataset.anchorY,side:el.dataset.anchorSide,box:rootBox(el)};
    // 2. 标注文字必须落在画布内、互不遮挡、不压住外置图元。
    const anns=texts.filter(t=>t.annotation);
    for(const t of anns){
      if(!inside(t.box,vb))issues.push({code:'annotation-outside',annotation:t.id});
      // 声明框必须包住真实字形，且不能大到与测量无关。
      const raw=(t.el.dataset.labelBox||'').split(',').map(Number);
      if(raw.length!==4||!raw.every(Number.isFinite)){issues.push({code:'label-box-missing',annotation:t.id});continue;}
      const declared={x:raw[0],y:raw[1],width:raw[2],height:raw[3]};
      if(t.box.x<declared.x-1.5||t.box.y<declared.y-1.5||t.box.x+t.box.width>declared.x+declared.width+1.5||t.box.y+t.box.height>declared.y+declared.height+1.5)
        issues.push({code:'label-box-untrue',annotation:t.id,declared,real:{x:t.box.x,y:t.box.y,width:t.box.width,height:t.box.height}});
      if(declared.width>t.box.width+Math.max(8,t.box.width*.2))issues.push({code:'label-box-inflated',annotation:t.id,declared:declared.width,real:t.box.width});
    }
    for(const t of anns){
      for(const other of texts)if(other.el!==t.el&&overlap(t.box,other.box,.5))issues.push({code:'annotation-text-collision',annotation:t.id,against:other.id});
      const placement=t.el.dataset.placement;
      for(const el of anchorEls){
        const real=rootBox(el);
        if(!overlap(t.box,real,0))continue;
        const isOwner=el.dataset.anchorId===t.el.dataset.anchorRef;
        if(placement!=='inside'||!isOwner)issues.push({code:'annotation-over-mark',annotation:t.id,mark:el.dataset.anchorId});
      }
    }
    // 3. 引线端点必须绑定真实锚点边界与标签框边缘。
    for(const lead of svg.querySelectorAll('path[data-role="leader"]')){
      const p0=lead.getPointAtLength(0),pn=lead.getPointAtLength(lead.getTotalLength());
      const a=anchors[lead.dataset.anchorRef],label=anns.find(t=>t.id===lead.dataset.annotationId);
      if(!a){issues.push({code:'leader-anchor-missing',route:lead.dataset.annotationId});continue;}
      const side=lead.dataset.leaderSide||a.side||'right';
      const expect=side==='right'?{x:a.box.x+a.box.width,y:a.y}:side==='left'?{x:a.box.x,y:a.y}:side==='top'?{x:a.x,y:a.box.y}:{x:a.x,y:a.box.y+a.box.height};
      if(!close(p0.x,expect.x,.5)||!close(p0.y,expect.y,.5))issues.push({code:'leader-start-off-anchor',route:lead.dataset.annotationId,at:{x:p0.x,y:p0.y},expect});
      if(!label)issues.push({code:'leader-label-missing',route:lead.dataset.annotationId});
      else {const raw=(label.el.dataset.labelBox||'').split(',').map(Number);
        const declared={x:raw[0],y:raw[1],width:raw[2],height:raw[3]};
        if(edgeDistance({x:pn.x,y:pn.y},declared)>1)issues.push({code:'leader-end-off-label',route:lead.dataset.annotationId,at:{x:pn.x,y:pn.y},declared,real:{x:label.box.x,y:label.box.y,width:label.box.width,height:label.box.height}});}
    }
    // 4. 声明尺寸必须等于实际 viewBox。
    if(svg.dataset.actualSize){const [aw,ah]=svg.dataset.actualSize.split('×').map(Number);
      if(!close(aw,vb.width,.5)||!close(ah,vb.height,.5))issues.push({code:'declared-size-mismatch',declared:svg.dataset.actualSize,viewBox:[vb.width,vb.height]});}
    findings.push({name,recipe:section.dataset.recipe||null,ok:issues.length===0,anchors:anchorEls.length,annotations:anns.length,leaders:svg.querySelectorAll('path[data-role="leader"]').length,issues});
  }
  return {ok:findings.length>0&&findings.every(v=>v.ok),findings};
});}

(async()=>{
  const dir=path.resolve(process.argv[2]||path.join(os.tmpdir(),'deck-annotation-gallery'));
  const html=path.join(dir,'annotation-gallery.html');
  /* 夹具不随仓库发布，缺失时自己造；克隆后可直接跑，不必先手动执行构建脚本。
     **但只判"存在"会留下陈旧夹具**：构建脚本加了新卡片之后，缓存里的旧样张不会重建，
     测试就一直红着——而红灯被人学会忽略，比不红更糟。所以按依赖的修改时间判失效。 */
  const builder=path.join(__dirname,'build_annotation_example.cjs');
  const deps=[builder,
    path.join(__dirname,'render_echarts_svg.cjs'),path.join(__dirname,'render_precision_exhibit.cjs'),
    path.join(__dirname,'render_diagram.cjs'),path.join(__dirname,'font_metrics.cjs'),
    ...fs.readdirSync(path.join(__dirname,'..','assets')).map(f=>path.join(__dirname,'..','assets',f)).filter(f=>fs.statSync(f).isFile())];
  const mtime=file=>{try{return fs.statSync(file).mtimeMs}catch{return 0}};
  const newest=Math.max(...deps.map(mtime));
  if(!fs.existsSync(html)||mtime(html)<newest){
    if(fs.existsSync(html))fs.rmSync(html);
    execFileSync(process.execPath,[builder,'--no-raster',dir],{stdio:'inherit'});
  }
  const browser=await pw.chromium.launch({channel:process.env.CHROME_CHANNEL||'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:1360,height:1200},deviceScaleFactor:1});
  try{
    await page.goto(pathToFileURL(html).href,{waitUntil:'networkidle'});
    await page.evaluate(()=>document.fonts.ready);
    const clean=await audit(page);
    assert.ok(clean.ok,'干净样张必须通过：'+JSON.stringify(clean.findings.filter(v=>!v.ok)));
    const covered=clean.findings.filter(v=>v.annotations>0&&v.leaders>0);
    assert.ok(covered.length>=5,'至少五个图型必须带引线标注');
    // 配方卡一个锚点都没有时，干净样张看起来和通过一模一样；这里点名要它们真有锚点。
    const recipes=clean.findings.filter(v=>v.recipe);
    assert.ok(recipes.length>=4,'样张必须覆盖至少四个 ECharts 配方');
    for(const card of recipes)assert.ok(card.anchors>0,card.recipe+' 卡一个锚点都没有，旁解读无处可挂');
    const mutations=[];
    async function mutate(label,setup,expected){
      const codes=[].concat(expected);
      await page.evaluate(setup);
      const bad=await audit(page);
      const caught=bad.findings.flatMap(v=>v.issues).map(v=>v.code).filter(code=>codes.includes(code));
      assert.ok(!bad.ok&&caught.length,label+' 必须被真实几何检查检出（期望 '+codes.join('/')+'）');
      mutations.push({label,caught:[...new Set(caught)]});
    }
    // 反例 1：标注文字下移 4px，引线末端与标签框脱开。
    await mutate('annotation-text-4px',()=>{const el=document.querySelector('[data-role="annotation"]');el.dataset.sx=el.getAttribute('x');el.dataset.sy=el.getAttribute('y');el.setAttribute('x',String(+el.dataset.sx+4));},['label-box-untrue','annotation-text-collision','leader-end-off-label']);
    await page.evaluate(()=>{const el=document.querySelector('[data-role="annotation"]');el.setAttribute('x',el.dataset.sx);el.setAttribute('y',el.dataset.sy);delete el.dataset.sx;delete el.dataset.sy;});
    // 反例 2：引线整体平移 4px，起点离开锚点边界。
    await mutate('leader-4px',()=>{const el=document.querySelector('path[data-role="leader"]');el.dataset.sd=el.getAttribute('d');el.setAttribute('d',el.dataset.sd.replace(/^M ([\d.-]+)/,(m,x)=>'M '+(+x+4)));},'leader-start-off-anchor');
    await page.evaluate(()=>{const el=document.querySelector('path[data-role="leader"]');el.setAttribute('d',el.dataset.sd);delete el.dataset.sd;});
    // 反例 3：图元真实几何改 4px，锚点声明变成假话。
    await mutate('anchor-box-4px',()=>{const el=[...document.querySelectorAll('[data-anchor-id]')].find(e=>e.tagName==='rect');el.dataset.sw=el.getAttribute('width');el.setAttribute('width',String(+el.dataset.sw+4));},'anchor-box-untrue');
    await page.evaluate(()=>{const el=[...document.querySelectorAll('[data-anchor-id]')].find(e=>e.tagName==='rect');el.setAttribute('width',el.dataset.sw);delete el.dataset.sw;});
    // 反例 4：标注文字挪到另一条标注上，文字互相遮挡。
    await mutate('annotation-overlap',()=>{const all=[...document.querySelectorAll('[data-role="annotation"]')],a=all[0],b=all.find(t=>t!==a);
      a.dataset.sx=a.getAttribute('x');a.dataset.sy=a.getAttribute('y');a.dataset.sa=a.getAttribute('text-anchor');
      a.setAttribute('x',b.getAttribute('x'));a.setAttribute('y',b.getAttribute('y'));a.setAttribute('text-anchor',b.getAttribute('text-anchor'));},'annotation-text-collision');
    await page.evaluate(()=>{const el=document.querySelector('[data-role="annotation"]');el.setAttribute('x',el.dataset.sx);el.setAttribute('y',el.dataset.sy);el.setAttribute('text-anchor',el.dataset.sa);delete el.dataset.sx;delete el.dataset.sy;delete el.dataset.sa;});
    const restored=await audit(page);
    assert.ok(restored.ok,'突变恢复后必须回到通过');
    const final={...clean,mutations,scope:'Chrome 实际 SVG：锚点声明对真实图元 bbox、标注越界与遮挡、引线两端绑定、声明尺寸与实际 viewBox；不含审美判断'};
    fs.writeFileSync(path.join(dir,'browser-measurements.json'),JSON.stringify(final,null,2));
    console.log(JSON.stringify({ok:final.ok,exhibits:final.findings.length,annotations:final.findings.reduce((s,v)=>s+v.annotations,0),leaders:final.findings.reduce((s,v)=>s+v.leaders,0),mutations:mutations.length,detail:final.findings.map(v=>({name:v.name,ok:v.ok,anchors:v.anchors,annotations:v.annotations,leaders:v.leaders}))},null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
