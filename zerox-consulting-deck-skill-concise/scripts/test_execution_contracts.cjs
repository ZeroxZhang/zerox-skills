/* 执行契约正反例：实际浏览器/PDF，独立审查缺结果、数据版本、可见性、缺页与错位。 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {aggregate}=require('./aggregate_reviews.cjs'),{check}=require('./check_planner_execution.cjs'),{loadPlanner}=require('./load_viz_planner.cjs');
const {inspect}=require('./audit_pdf_geometry.cjs'),geometry=require('./browser_geometry_audit.cjs'),{validateAudit}=require('./package_delivery.cjs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const sha=v=>crypto.createHash('sha256').update(v).digest('hex'),fileHash=f=>sha(fs.readFileSync(f));
(async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-execution-')),browser=await chromium.launch({channel:'chrome',headless:true}),results={};
 const equal=(name,actual,expected)=>{assert.equal(actual,expected,name);results[name]=actual;};
 try{
  const p=await browser.newPage({viewport:{width:1280,height:720}}),evidence=path.join(dir,'evidence.png');
  await p.setContent('<section class="slide active"><table><tbody><tr><td>A</td><td>10</td></tr></tbody></table></section>');await p.screenshot({path:evidence});
  const audit={pages:1,htmlArtifact:{sha256:'h'},pdfArtifact:{sha256:'p'}};
  const response=role=>({status:'complete',htmlSha256:'h',pdfSha256:'p',coverage:[{reviewer:role,independence:role,layers:['page','exhibit','annotation','typography'],htmlPages:[1],pdfPages:[1],evidence:[{path:evidence,sha256:fileHash(evidence)}]}],issues:[],checks:Object.fromEntries(['analysis','evidence','visual'].map(k=>[k,{status:'pass',basis:'合成测试夹具，不声明已完成人工复核'}]))});
  const author=response('author'),independent=response('independent'),aggregateCase=value=>aggregate(audit,[author,value],{requireIndependent:true}).status;
  equal('complete_results',aggregateCase(independent),'complete');
  for(const [name,edit] of [
   ['missing_own_checks',r=>delete r.checks],['missing_one_check',r=>delete r.checks.visual],['empty_basis',r=>r.checks.visual.basis=''],
   ['incomplete_status',r=>r.status='incomplete'],['failed_status',r=>r.status='failed'],['missing_status',r=>delete r.status],
   ['missing_independent_pdf_page',r=>r.coverage[0].pdfPages=[]],['stale_result',r=>r.pdfSha256='old']
  ]){const r=structuredClone(independent);edit(r);equal(name,aggregateCase(r),'incomplete');}
  equal('natural_language',aggregateCase('未检查PDF但看起来没问题'),'incomplete');
  const dataFile=path.join(dir,'data.json');fs.writeFileSync(dataFile,'[{"category":"A","value":10}]');
  const plan={contract_version:'1.1',output_level:'decision',mode:'api',status:'ok',summary:'按类别查值',echarts:{version:'6.1.0',deps:[],renderer:'svg'},intent:{goal:'查值',scenario:'executive',inferred:false,confidence:'high'},data:{sha256:fileHash(dataFile),ref:{type:'file',id:'data.json'},profile:{rows:1,dimensions:['category'],measures:['value']},binding:{mode:'dataset.source',expects:'array<object>',required_fields:['category','value']}},plan:[{role:'primary',capability_id:'table.detail',question:'值是多少',match:'strong',rationale:'查数任务',spec:{kind:'table',message:'按类别查值',evidence_refs:['data.json'],boundaries:[],columns:[{field:'category',label:'类别'},{field:'value',label:'值'}],row_organization:'每类别一行',lookup_task:'查值'},bindings:[{target:'table.rows',ref:{type:'file',id:'data.json'},expects:'array<object>',required_fields:['category','value']}]}]};
  const planFile=path.join(dir,'plan.json'),resource=loadPlanner({offline:true});assert.equal(resource.status,'ok');
  const savePlan=value=>{fs.writeFileSync(planFile,JSON.stringify(value));return fileHash(planFile);};
  const record={data:{path:dataFile,sha256:fileHash(dataFile)},planner:{root:resource.skill_root,sourceSha256:resource.source_sha256},plans:[{path:planFile,sha256:savePlan(plan)}],pages:[{page:1,proves:'查值',roles:{primary:'表'},readingOrder:['表头','数值'],alignment:['行轨道'],plan:0,relationships:[{selector:'tbody tr',minCount:1,meaning:'类别与数值共同行'}]}]};
  const checked=()=>check(record,p,{baseDir:dir});
  equal('planner_bound', (await checked()).status,'PASS');
  const different=path.join(dir,'different.json');fs.writeFileSync(different,'[{"category":"A","value":999}]');record.data={path:different,sha256:fileHash(different)};
  equal('planner_wrong_input',(await checked()).status,'FAIL');record.data={path:dataFile,sha256:fileHash(dataFile)};
  fs.writeFileSync(dataFile,'[{"category":"A","value":999}]');record.data.sha256=fileHash(dataFile);
  equal('planner_stale_input_digest',(await checked()).status,'FAIL');fs.writeFileSync(dataFile,'[{"category":"A","value":10}]');record.data.sha256=fileHash(dataFile);
  const missingDigest=structuredClone(plan);delete missingDigest.data.sha256;record.plans[0].sha256=savePlan(missingDigest);
  equal('planner_missing_digest',(await checked()).status,'FAIL');record.plans[0].sha256=savePlan(plan);
  for(const selector of ['tbody tr','table']){await p.locator(selector).evaluate(e=>e.style.opacity='0');equal('planner_invisible_'+selector,(await checked()).status,'FAIL');await p.locator(selector).evaluate(e=>e.style.opacity='');}
  equal('planner_restored',(await checked()).status,'PASS');
  await p.setContent('<section class="slide" style="width:1280px;height:720px"><svg width="500" height="300"><rect data-geo-baseline="b" x="20" y="20" width="30" height="20"/><rect data-geo-baseline="b" x="80" y="50" width="30" height="20"/></svg></section>');
  equal('svg_nontext_anchor',(await p.locator('.slide').evaluate(geometry.inspectSlide)).status,'FAIL');
  // 首行、末行与真实PDF打印；等宽列防止反例改变其他文字的位置。
  const html='<html data-deck-kind="fragment" data-reliability-version="1"><head><style>@page{size:1280px 720px;margin:0}body{margin:0}.slide{width:1280px;height:720px;font:20px Arial;box-sizing:border-box;padding:40px}.row{display:flex;gap:50px}.cell{display:inline-block;line-height:28px;width:220px}.last{margin-top:30px;align-items:last baseline}.first{margin-top:30px;align-items:first baseline}</style></head><body><section class="slide active"><div class="row"><span class="cell" data-geo-baseline="single">ALPHA BETA</span><span class="cell" data-geo-baseline="single">GAMMA</span></div><div class="row last"><span class="cell" data-geo-baseline="last" data-geo-line="last">FIRST<br>LAST LINE</span><span class="cell" data-geo-baseline="last" data-geo-line="last">SECOND<br>LAST VALUE</span></div><div class="row first"><span class="cell" data-geo-baseline="first">FIRST LINE<br>SECOND LINE</span><span class="cell" data-geo-baseline="first">FIRST VALUE</span></div></section></body></html>';
  await p.setContent(html);const relations=await p.locator('.slide').evaluate(geometry.inspectSlide);equal('html_multiline',relations.status,'PASS');
  assert.deepEqual(relations.measurements.filter(m=>m.group==='baseline:last').map(m=>m.lineText),['LAST LINE','LAST VALUE']);
  assert.deepEqual(relations.measurements.filter(m=>m.group==='baseline:first').map(m=>m.lineText),['FIRST LINE','FIRST VALUE']);
  const pdf=path.join(dir,'valid.pdf');await p.pdf({path:pdf,preferCSSPageSize:true,printBackground:true});
  const good={pages:1,pdfPages:1,pdfArtifact:{path:pdf,sha256:fileHash(pdf),pages:1},rows:[{page:1,relations}]};
  equal('pdf_multiline',(await inspect(good,path.join(dir,'pdf-good'))).status,'PASS');
  equal('pdf_missing_page',(await inspect({...good,pages:2,pdfPages:2},path.join(dir,'pdf-missing'))).status,'FAIL');
  equal('pdf_missing_rows',(await inspect({...good,rows:[]},path.join(dir,'pdf-no-rows'))).status,'FAIL');
  equal('pdf_undeclared',(await inspect({...good,rows:[{page:1,relations:{status:'NOT_DECLARED',measurements:[]}}]},path.join(dir,'pdf-undeclared'))).status,'PARTIAL');
  const mutatePdf=async(name,content)=>{await p.locator('.cell').first().evaluate((e,html)=>e.innerHTML=html,content);const f=path.join(dir,name+'.pdf');await p.pdf({path:f,preferCSSPageSize:true,printBackground:true});return inspect({...good,pdfArtifact:{path:f,sha256:fileHash(f),pages:1}},path.join(dir,name));};
  equal('pdf_missing_fragment',(await mutatePdf('partial','ALPHA')).status,'FAIL');
  equal('pdf_shifted_fragment',(await mutatePdf('shifted','<span>ALPHA</span><span style="position:relative;top:18px"> BETA</span>')).status,'FAIL');
  equal('pdf_restored',(await mutatePdf('restored','ALPHA BETA')).status,'PASS');
  // 真实Chrome的小数行高/位置夹具：打印基线最近像素量化，同行关系仍须<=.35px。
  const fractional='<style>@page{size:1280px 720px;margin:0}body{margin:0}.slide{width:1280px;height:720px;position:relative;font:20px Arial}.row{position:absolute;left:40px;display:flex;gap:50px}.cell{width:220px;line-height:28.375px}</style><section class="slide">'+Array.from({length:8},(_,i)=>'<div class="row" style="top:'+(30+i*65+i/8)+'px"><span class="cell" data-geo-baseline="r'+i+'">LEFT '+i+'</span><span class="cell" data-geo-baseline="r'+i+'">RIGHT '+i+'</span></div>').join('')+'</section>';
  await p.setContent(fractional);const fractionalRelations=await p.locator('.slide').evaluate(geometry.inspectSlide);equal('html_fractional',fractionalRelations.status,'PASS');
  const inspectFractional=async name=>{const f=path.join(dir,name+'.pdf');await p.pdf({path:f,preferCSSPageSize:true,printBackground:true});return inspect({...good,pdfArtifact:{path:f,sha256:fileHash(f),pages:1},rows:[{page:1,relations:fractionalRelations}]},path.join(dir,name));};
  const calibrated=await inspectFractional('fractional');equal('pdf_fractional',(calibrated).status,'PASS');
  assert.ok(calibrated.rows[0].checks.some(c=>c.error>.35),'夹具必须实际触发跨媒介亚像素偏移');
  assert.ok(calibrated.rows[0].groups.some(g=>g.position==='CALIBRATED_BASELINE_ROUNDING'),'单独报告已校准共同偏移');
  assert.ok(calibrated.rows[0].groups.every(g=>g.spread<=.35),'未放宽实际组内精度');
  for(const shift of [2,4]){await p.locator('.cell').first().evaluate((e,n)=>e.style.transform='translateY('+n+'px)',shift);equal('pdf_single_'+shift+'px',(await inspectFractional('single-'+shift)).status,'FAIL');}
  await p.locator('.cell').first().evaluate(e=>e.style.transform='');await p.locator('.row').first().evaluate(e=>e.style.transform='translateY(4px)');
  equal('pdf_uniform_4px',(await inspectFractional('uniform-4')).status,'FAIL');
  await p.locator('.row').first().evaluate(e=>e.style.transform='');equal('pdf_fractional_restored',(await inspectFractional('fractional-restored')).status,'PASS');
  const htmlFile=path.join(dir,'valid.html');fs.writeFileSync(htmlFile,html);const auditFile=path.join(dir,'audit.json');
  const packaging={...good,input:htmlFile,geometryStatus:'PASS',errors:[],htmlArtifact:{sha256:sha(html)},documentContract:{reliability:'1',kind:'fragment'}};
  const options={inputHtml:htmlFile,inputPdf:pdf,html,pdf:fs.readFileSync(pdf),htmlPages:1,pdfPages:1,pdfSha256:fileHash(pdf)};
  fs.writeFileSync(auditFile,JSON.stringify(packaging));assert.doesNotThrow(()=>validateAudit(auditFile,options));delete packaging.documentContract;fs.writeFileSync(auditFile,JSON.stringify(packaging));assert.throws(()=>validateAudit(auditFile,options),/V11/);results.package_missing_contract='FAIL_AS_EXPECTED';
  console.log(JSON.stringify({pass:true,cases:Object.keys(results).length,results}));
 }finally{await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
