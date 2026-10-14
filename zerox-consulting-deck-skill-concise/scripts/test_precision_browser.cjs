/* 独立读取浏览器实际图元与字体 bbox；4px 图元/标注/标签突变必须失败。 */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {samples}=require('./test_precision_exhibit.cjs');
async function browserAudit(page){return page.evaluate(specs=>{
  const findings=[];const between=(a,b,t)=>Math.abs(a-b)<=t;
  const overlap=(a,b)=>a.x<b.x+b.width-.3&&a.x+a.width>b.x+.3&&a.y<b.y+b.height-.3&&a.y+a.height>b.y+.3;
  const contained=(a,b)=>b.x>=a.x-.4&&b.x+b.width<=a.x+a.width+.4&&b.y>=a.y-.4&&b.y+b.height<=a.y+a.height+.4;
  for(const [name,spec] of Object.entries(specs)){
    const section=document.querySelector(`[data-sample="${name}"]`),svg=section.querySelector('svg'),metadata=JSON.parse(svg.querySelector('metadata').textContent),issues=[];
    const toLocal=(el,p)=>new DOMPoint(p.x,p.y).matrixTransform(el.getScreenCTM()).matrixTransform(svg.getScreenCTM().inverse());
    const box=el=>{const b=el.getBBox(),a=toLocal(el,{x:b.x,y:b.y}),z=toLocal(el,{x:b.x+b.width,y:b.y+b.height});return {x:a.x,y:a.y,width:z.x-a.x,height:z.y-a.y};};
    const yOf=line=>toLocal(line,{x:line.x1.baseVal.value,y:line.y1.baseVal.value}).y;
    const zero=svg.querySelector('[data-role="zero-axis"]'),y0=yOf(zero);
    const breakDefs=spec.axisBreaks||[];
    // 独立按可见数值长度拟合尺度；取真实轴线，不消费 renderer 的 geometry/audit。
    const compressed=value=>{let v=value;for(const b of breakDefs)if(value>=b.to)v-=b.to-b.from;return v;};
    const pixelGaps=value=>breakDefs.filter(b=>value>=b.to).reduce((s,b)=>s+(b.gap===undefined?14:b.gap),0);
    const axis=[...svg.querySelectorAll('[data-role="axis-grid"]')].find(el=>+el.dataset.axisValue!==0&&compressed(+el.dataset.axisValue)!==0);
    const axisValue=+axis.dataset.axisValue,unit=(y0-yOf(axis)-pixelGaps(axisValue))/compressed(axisValue);
    const y=value=>y0-compressed(value)*unit-pixelGaps(value);
    const expected=[];let acc=0;
    spec.items.forEach((item,index)=>{const itemId=String(item.id===undefined?index:item.id);
      if(spec.type==='stacked'){let running=0;item.segments.forEach(seg=>{const from=running;running+=seg.value;expected.push({id:itemId+'::'+String(seg.id===undefined?seg.label:seg.id),item:itemId,value:seg.value,from,to:running});});}
      else if(spec.type==='waterfall'){const from=item.type==='delta'?acc:0,to=item.type==='delta'?acc+item.value:item.type==='subtotal'?acc:item.value;acc=to;expected.push({id:itemId,item:itemId,value:item.type==='delta'?item.value:to,from,to});}
      else expected.push({id:itemId,item:itemId,value:item.value,from:0,to:item.value});
    });
    for(const mark of expected){
      const actual=[...svg.querySelectorAll('[data-role="bar"]')].filter(el=>el.dataset.markId===mark.id),pieces=[];let from=Math.min(mark.from,mark.to),to=Math.max(mark.from,mark.to);
      for(const b of breakDefs){if(b.from>from&&b.from<to){pieces.push([from,b.from]);from=b.to;}}pieces.push([from,to]);
      if(actual.length!==pieces.length)issues.push({code:'piece-count',mark:mark.id});
      actual.forEach((el,i)=>{const b=box(el),p=pieces[i];if(!p)return;if(!between(b.y,Math.min(y(p[0]),y(p[1])),.5)||!between(b.height,Math.abs(y(p[0])-y(p[1])),.5))issues.push({code:'actual-mark-scale',mark:mark.id});if(+el.dataset.value!==mark.value)issues.push({code:'raw-value',mark:mark.id});});
    }
    const texts=[...svg.querySelectorAll('text')].map(el=>({el,id:el.dataset.labelId,b:box(el)})),marks=[...svg.querySelectorAll('[data-role="bar"]')].map(el=>({id:el.dataset.markId,b:box(el)}));
    for(let i=0;i<texts.length;i++){
      const t=texts[i];for(let j=i+1;j<texts.length;j++)if(overlap(t.b,texts[j].b))issues.push({code:'actual-text-collision',labels:[t.id,texts[j].id]});
      if(!contained({x:0,y:0,width:spec.width,height:spec.height},t.b))issues.push({code:'actual-text-outside',label:t.id});
      if(t.el.dataset.placement==='inside'){if(!marks.some(m=>m.id===t.el.dataset.markId&&contained(m.b,t.b)))issues.push({code:'actual-inside-label',label:t.id});}
      else if(marks.some(m=>overlap(t.b,m.b)))issues.push({code:'actual-label-mark',label:t.id});
    }
    const resolve=ref=>{ref=typeof ref==='string'?{item:ref}:ref;const item=spec.items.find(v=>String(v.id)===String(ref.item));const key=String(ref.item)+(ref.series?'::'+ref.series:'');let raw,axisValue;
      if(ref.series){const m=expected.find(v=>v.id===key);raw=m.value;axisValue=m.to;}
      else if(spec.type==='stacked'){raw=item.segments.reduce((s,v)=>s+v.value,0);axisValue=raw;}
      else {const m=expected.find(v=>v.id===key);raw=m.value;axisValue=m.to;}
      const els=marks.filter(v=>ref.series?v.id===key:v.id===key||v.id.startsWith(key+'::')),x=els[0].b.x+els[0].b.width/2;return {x,y:y(axisValue),raw};};
    const comparisonPaths=[...svg.querySelectorAll('[data-role="comparison"]')];
    for(let i=0;i<(spec.comparisons||[]).length;i++){
      const actual=comparisonPaths[i],c=spec.comparisons[i];let a=resolve(c.from),b=resolve(c.to);
      if(c.from?.series&&c.to?.series){
        const bars=[c.from,c.to].map(ref=>[...svg.querySelectorAll('[data-role="layer-bar"]')].find(el=>el.dataset.markId===String(ref.item)+'::'+ref.series));if(!bars.every(Boolean)){issues.push({code:'missing-layer-track',comparison:i});continue;}const boxes=bars.map(box);
        if(!bars.every(Boolean)||!between(boxes[0].x,boxes[1].x,.5)||!between(boxes[0].width*(b.raw||1),boxes[1].width*(a.raw||1),.5))issues.push({code:'actual-layer-scale',comparison:i});
        a={...a,x:boxes[0].x+boxes[0].width,y:boxes[0].y+boxes[0].height/2};b={...b,x:boxes[1].x+boxes[1].width,y:boxes[1].y+boxes[1].height/2};
        const arrow=svg.querySelector('[data-role="comparison-arrow"][data-route-id="'+actual.dataset.routeId+'"]');
        if(a.raw!==b.raw){const tip=toLocal(arrow,arrow.getPointAtLength(arrow.getTotalLength()/2)),tail=toLocal(arrow,arrow.getPointAtLength(0));if(Math.sign(tip.x-tail.x)!==Math.sign(b.raw-a.raw))issues.push({code:'actual-layer-direction',comparison:i});}
        bars.forEach((bar,j)=>{const main=svg.querySelector('[data-role="value"][data-mark-id="'+bar.dataset.markId+'"]');if(!main||main.dataset.reference!==bar.dataset.reference)issues.push({code:'actual-layer-reference',comparison:i});});
      }
      const first=toLocal(actual,actual.getPointAtLength(0)),last=toLocal(actual,actual.getPointAtLength(actual.getTotalLength()));
      if(!between(first.x,a.x,.5)||!between(first.y,a.y,.5)||!between(last.x,b.x,.5)||!between(last.y,b.y,.5))issues.push({code:'actual-comparison-endpoint',comparison:i});
      if(!between(+actual.dataset.delta,b.raw-a.raw,1e-8))issues.push({code:'actual-comparison-delta',comparison:i});
    }
    for(const el of svg.querySelectorAll('[data-role="leader"]')){
      const p=toLocal(el,el.getPointAtLength(0)),target=marks.filter(m=>m.id===el.dataset.markId);
      if(!target.some(m=>(between(p.x,m.b.x,.5)||between(p.x,m.b.x+m.b.width,.5))&&p.y>=m.b.y-.5&&p.y<=m.b.y+m.b.height+.5))issues.push({code:'actual-leader-endpoint',route:el.dataset.routeId});
    }
    findings.push({name,ok:issues.length===0,marks:marks.length,texts:texts.length,issues});
  }
  return {ok:findings.every(v=>v.ok),findings};
},samples);}
(async()=>{
  // 夹具自带：旧版依赖一个已不随仓库发布的历史目录，测试只会抛出指向不存在脚本的错误。
  const dir=path.resolve(process.argv[2]||path.join(os.tmpdir(),'deck-precision-gallery')),html=path.join(dir,'gallery.html');
  if(!fs.existsSync(html)){const built=require('./build_precision_gallery.cjs').build(dir);console.log('已生成夹具：'+built.file+'（samples: '+built.samples.length+'）');}
  if(!fs.existsSync(html))throw Error('无法生成精度样张夹具：'+html);
  const browser=await pw.chromium.launch({channel:'chrome',headless:true}),page=await browser.newPage({viewport:{width:1280,height:760},deviceScaleFactor:1});
  try{
    await page.goto(pathToFileURL(html).href);await page.evaluate(()=>window.deckReady);await page.evaluate(()=>document.fonts.ready);
    const result=await browserAudit(page);fs.writeFileSync(path.join(dir,'browser-measurements.json'),JSON.stringify(result,null,2));assert.ok(result.ok,JSON.stringify(result.findings.filter(v=>!v.ok)));
    const client=await page.context().newCDPSession(page);await client.send('DOM.enable');await client.send('CSS.enable');const doc=await client.send('DOM.getDocument');const fonts=[];
    for(const selector of ['[data-sample="axisBreak"] [data-role="category"]','[data-sample="smallStack"] [data-role="value"]']){const {nodeId}=await client.send('DOM.querySelector',{nodeId:doc.root.nodeId,selector});const f=await client.send('CSS.getPlatformFontsForNode',{nodeId});fonts.push({selector,...f});assert.ok(f.fonts.length&&f.fonts.every(v=>v.isCustomFont),'实际 SVG 必须使用已嵌入字体');}
    const mutations=[];
    for(const [name,selector,code] of [['mark','[data-sample="axisBreak"] [data-role="bar"]','actual-mark-scale'],['comparison','[data-sample="continuous"] [data-role="comparison"]','actual-comparison-endpoint'],['leader','[data-sample="smallStack"] [data-role="leader"]','actual-leader-endpoint']]){
      await page.locator(selector).first().evaluate(el=>el.setAttribute('transform','translate(0 4)'));
      if(name==='leader')await page.locator(selector).first().evaluate(el=>el.setAttribute('transform','translate(4 0)'));
      const bad=await browserAudit(page);assert.ok(!bad.ok&&bad.findings.flatMap(v=>v.issues).some(v=>v.code===code),name+' 突变必须被真实对象检查检出');mutations.push({name,offset:4,caught:code});await page.locator(selector).first().evaluate(el=>el.removeAttribute('transform'));
    }
    const layerPathSelector='[data-sample="smallStack"] path[data-role="comparison"][data-space="layer-value"]';
    await page.locator(layerPathSelector).evaluate(el=>{el.dataset.savedPath=el.getAttribute('d');const svg=el.ownerSVGElement,meta=JSON.parse(svg.querySelector('metadata').textContent),a=meta.anchors[el.dataset.fromKey],b=meta.anchors[el.dataset.toKey];el.setAttribute('d','M '+a.x+' '+a.y+' L '+b.x+' '+b.y);});
    const oldCumulative=await browserAudit(page);assert.ok(oldCumulative.findings.flatMap(v=>v.issues).some(v=>v.code==='actual-comparison-endpoint'));mutations.push({name:'rejected-cumulative-layer-anchor',caught:'actual-comparison-endpoint'});
    await page.locator(layerPathSelector).evaluate(el=>{el.setAttribute('d',el.dataset.savedPath);delete el.dataset.savedPath;});
    const layerSelector='[data-sample="smallStack"] [data-role="layer-bar"]';
    await page.locator(layerSelector).first().evaluate(el=>{el.dataset.originalWidth=el.getAttribute('width');el.setAttribute('width',String(+el.getAttribute('width')+4));});
    const badLayer=await browserAudit(page);assert.ok(badLayer.findings.flatMap(v=>v.issues).some(v=>v.code==='actual-layer-scale'));mutations.push({name:'layer-width',offset:4,caught:'actual-layer-scale'});
    await page.locator(layerSelector).first().evaluate(el=>{el.setAttribute('width',el.dataset.originalWidth);delete el.dataset.originalWidth;});
    const arrowSelector='[data-sample="smallStack"] [data-role="comparison-arrow"][data-route-id="comparison-1"]';
    await page.locator(arrowSelector).evaluate(el=>{const b=el.getBBox();el.setAttribute('transform','translate('+(2*(b.x+b.width/2))+' 0) scale(-1 1)');});
    const badDirection=await browserAudit(page);assert.ok(badDirection.findings.flatMap(v=>v.issues).some(v=>v.code==='actual-layer-direction'));mutations.push({name:'layer-arrow-reversed',caught:'actual-layer-direction'});
    await page.locator(arrowSelector).evaluate(el=>el.removeAttribute('transform'));
    await page.evaluate(()=>{const svg=document.querySelector('[data-sample="smallStack"] svg'),texts=[...svg.querySelectorAll('[data-role="value"]')];texts[0].dataset.savedX=texts[0].getAttribute('x');texts[0].dataset.savedY=texts[0].getAttribute('y');texts[0].setAttribute('x',texts[1].getAttribute('x'));texts[0].setAttribute('y',texts[1].getAttribute('y'));});
    const collision=await browserAudit(page);assert.ok(collision.findings.flatMap(v=>v.issues).some(v=>v.code==='actual-text-collision'));mutations.push({name:'text-collision',caught:'actual-text-collision'});
    await page.evaluate(()=>{const el=document.querySelector('[data-sample="smallStack"] [data-saved-x]');el.setAttribute('x',el.dataset.savedX);el.setAttribute('y',el.dataset.savedY);delete el.dataset.savedX;delete el.dataset.savedY;});
    assert.ok((await browserAudit(page)).ok,'恢复后必须通过');
    for(const name of Object.keys(samples))await page.locator(`[data-sample="${name}"]`).screenshot({path:path.join(dir,name+'.png')});
    await page.pdf({path:path.join(dir,'gallery.pdf'),printBackground:true,preferCSSPageSize:true});
    const final={...result,fontEvidence:fonts,mutations,pdf:'gallery.pdf',scope:'Chrome 实际 SVG、字体、文字 bbox、数值尺度、比较端点与引线；突变恢复后导出 PDF'};fs.writeFileSync(path.join(dir,'browser-measurements.json'),JSON.stringify(final,null,2));console.log(JSON.stringify({ok:final.ok,samples:final.findings.length,mutations:mutations.length,fonts:fonts.map(v=>v.fonts.map(f=>f.familyName)),pdf:path.join(dir,'gallery.pdf')}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
