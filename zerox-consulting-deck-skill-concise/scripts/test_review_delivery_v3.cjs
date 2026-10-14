/* 合成合同夹具：验证聚合与打包共用拒绝路径，不声称真实目视验收。 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {aggregate}=require('./aggregate_reviews.cjs');
const {validateReview,validateAudit}=require('./package_delivery.cjs');
const contract=require('./report_contract.cjs');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-review-v3-'));
let cases=0;
function check(name,fn){fn();cases++;}
try{
 const html=contract.install('<html><head></head><body><section class="slide"></section></body></html>',{kind:'report',complexity:'simple'});
 const htmlFile=path.join(dir,'deck.html'),pdfFile=path.join(dir,'deck.pdf');
 fs.writeFileSync(htmlFile,html);fs.writeFileSync(pdfFile,'synthetic pdf artifact');
 const audit={input:htmlFile,pages:1,pdfPages:1,geometryStatus:'PASS',errors:[],documentContract:{reliability:'2',kind:'report'},taskContract:contract.read(html),htmlArtifact:{path:htmlFile,sha256:contract.fileHash(htmlFile)},pdfArtifact:{path:pdfFile,sha256:contract.fileHash(pdfFile)},evidenceManifest:{dependenciesSha256:contract.hash('dependencies'),entries:[]}};
 for(const medium of ['html','pdf']){
  const file=path.join(dir,medium+'.png');fs.writeFileSync(file,'synthetic '+medium+' screenshot bytes');
  audit.evidenceManifest.entries.push({id:medium+':page-1',medium,page:1,pageId:'page-1',path:path.basename(file),sha256:contract.fileHash(file),sourceSha256:audit[medium+'Artifact'].sha256,pageSha256:contract.hash('page-1'),dependenciesSha256:audit.evidenceManifest.dependenciesSha256});
 }
 const response=(a,role)=>({schemaVersion:3,status:'complete',reviewer:role,independence:role,isolation:'fresh-context',htmlSha256:a.htmlArtifact.sha256,pdfSha256:a.pdfArtifact.sha256,auditSha256:contract.hash(contract.stable(a)),coverage:[{reviewer:role,independence:role,layers:['page','exhibit','annotation','typography'],htmlPages:[1],pdfPages:[1],evidence:a.evidenceManifest.entries.map(e=>({id:e.id})),attestation:[{page:1,note:'合成合同测试第 1 页的可见所见'}]}],issues:[],checks:Object.fromEntries(['analysis','evidence','visual'].map(k=>[k,{status:'pass',basis:'合成合同测试 '+role+' '+k}]))});
 const run=(a,values)=>aggregate(a,values,{baseDir:dir,auditDir:dir});
 const saveAndCheck=(a,review)=>{const file=path.join(dir,'review.json');fs.writeFileSync(file,JSON.stringify(review));return validateReview(file,{audit:a,auditDir:dir,htmlSha256:a.htmlArtifact.sha256,pdfSha256:a.pdfArtifact.sha256,pages:1});};
 check('简单完整报告作者可完成',()=>{const review=run(audit,[response(audit,'author')]);assert.equal(review.status,'complete');assert.doesNotThrow(()=>saveAndCheck(audit,review));});
 const complex=structuredClone(audit);complex.taskContract=contract.normalize({kind:'fragment',complexity:'complex'});complex.documentContract.kind='fragment';
 check('复杂片段必须独立审查',()=>{assert.equal(run(complex,[response(complex,'author')]).status,'incomplete');assert.throws(()=>saveAndCheck(complex,response(complex,'author')),/independent/);});
 check('复杂片段双方合并通过',()=>{const review=run(complex,[response(complex,'author'),response(complex,'independent')]);assert.equal(review.status,'complete');assert.doesNotThrow(()=>saveAndCheck(complex,review));});
 check('高影响简单片段仍须独立',()=>{const a=structuredClone(complex);a.taskContract=contract.normalize({kind:'fragment',complexity:'simple',majorConclusion:true});assert.equal(run(a,[response(a,'author')]).status,'incomplete');});
 check('状态及依据聚合与输入顺序无关',()=>{const author=response(complex,'author'),other=response(complex,'independent');other.checks.analysis.status='not_applicable';const ab=run(complex,[author,other]),ba=run(complex,[other,author]);assert.deepEqual(ab,ba);assert.equal(ab.checks.analysis.status,'pass');});
 for(const [name,mutate] of [
  ['旧schema',r=>r.schemaVersion=2],['旧audit',r=>r.auditSha256=contract.hash('old')],['HTML冒充PDF',r=>r.coverage[0].evidence=[{id:'html:page-1'}]],['缺本份检查',r=>delete r.checks.visual],['非法状态',r=>r.checks.analysis.status='unknown'],['未完成',r=>r.status='incomplete'],['未决重大问题',r=>r.issues=[{severity:'major',status:'open',description:'示例问题'}]],['错误证据身份',r=>r.coverage[0].evidence[0].id='html:wrong']
 ])check(name,()=>{const r=response(audit,'author');mutate(r);assert.equal(run(audit,[r]).status,'incomplete');assert.throws(()=>saveAndCheck(audit,r));});
 check('独立结果不能掩盖作者失败',()=>{const author=response(complex,'author'),other=response(complex,'independent');author.checks.visual.status='fail';for(const values of [[author,other],[other,author]])assert.equal(run(complex,values).status,'incomplete');});
 check('原始作者结果不能追加独立身份',()=>{const author=response(complex,'author');author.coverage.push(...response(complex,'independent').coverage);assert.equal(run(complex,[author]).status,'incomplete');assert.throws(()=>saveAndCheck(complex,author),/身份/);});
 check('作者独立审查者不能同名',()=>{const author=response(complex,'author'),other=response(complex,'independent');other.reviewer='author';other.coverage[0].reviewer='author';assert.equal(run(complex,[author,other]).status,'incomplete');});
 check('同页不同pageId不能借用证据',()=>{const a=structuredClone(audit),extra=structuredClone(a.evidenceManifest.entries[0]);extra.id='html:other';extra.pageId='other';a.evidenceManifest.entries.push(extra);assert.equal(run(a,[response(a,'author')]).status,'incomplete');assert.throws(()=>saveAndCheck(a,response(a,'author')),/重复|身份/);});
 check('manifest缺媒介即使未引用仍拒绝',()=>{const a=structuredClone(audit);a.evidenceManifest.entries=a.evidenceManifest.entries.filter(e=>e.medium==='html');const r=response(a,'author');r.coverage[0].pdfPages=[];assert.equal(run(a,[r]).status,'incomplete');assert.throws(()=>saveAndCheck(a,r),/缺页/);});
 check('自然语言及空输入不放行',()=>{assert.equal(run(audit,['未看PDF']).status,'incomplete');assert.equal(run(audit,[]).status,'incomplete');});
 // 独立性与逐页取证：两者都只能自述，但空洞的自述要能被当场问住。
 {
  const bad=response(audit,'independent');bad.isolation='fork';
  const r=run(complex,[bad]);
  assert.equal(r.status,'incomplete');
  assert.ok(r.aggregationErrors.some(e=>/fresh-context/.test(e)),JSON.stringify(r.aggregationErrors));
 }
 {const bad=response(audit,'author');delete bad.isolation;assert.ok(run(audit,[bad]).aggregationErrors.some(e=>/isolation/.test(e)),'isolation 缺失不能默默通过');}
 {const bad=response(audit,'author');bad.coverage[0].attestation=[{page:1,note:'   '}];assert.ok(run(audit,[bad]).aggregationErrors.some(e=>/attestation/.test(e)),'空取证不能通过');}
 {const bad=response(audit,'author');bad.coverage[0].attestation=[];assert.ok(run(audit,[bad]).aggregationErrors.some(e=>/attestation/.test(e)),'声称看过却没写取证不能通过');}
 {
  // 多页时"同一条复制到底"必须被拦住——否则取证退化成一个占位符。
  const two=structuredClone(audit);
  for(const medium of ['html','pdf']){const file=path.join(dir,medium+'-2.png');fs.writeFileSync(file,'synthetic '+medium+' page2');two.evidenceManifest.entries.push({id:medium+':page-2',medium,page:2,pageId:'page-2',path:path.basename(file),sha256:contract.fileHash(file),sourceSha256:two[medium+'Artifact'].sha256,pageSha256:contract.hash('page-2'),dependenciesSha256:two.evidenceManifest.dependenciesSha256});}
  two.pages=2;two.pdfPages=2;
  const r=response(two,'author');
  r.coverage[0].htmlPages=[1,2];r.coverage[0].pdfPages=[1,2];r.coverage[0].evidence=two.evidenceManifest.entries.map(e=>({id:e.id}));
  r.coverage[0].attestation=[{page:1,note:'同一句话'},{page:2,note:'同一句话'}];
  assert.ok(run(two,[r]).aggregationErrors.some(e=>/完全相同/.test(e)),'复制粘贴的取证必须被拦下');
  r.coverage[0].attestation=[{page:1,note:'第 1 页左下象限空着'},{page:2,note:'第 2 页两根柱几乎等高'}];
  assert.equal(run(two,[r]).status,'complete',JSON.stringify(run(two,[r]).aggregationErrors));
 }
 check('渲染文件改变同时阻断两入口',()=>{fs.writeFileSync(path.join(dir,'pdf.png'),'changed');const r=response(audit,'author');assert.equal(run(audit,[r]).status,'incomplete');assert.throws(()=>saveAndCheck(audit,r),/改变/);fs.writeFileSync(path.join(dir,'pdf.png'),'synthetic pdf screenshot bytes');});
 check('不同review输出目录保留audit证据根目录',()=>{const output=path.join(dir,'nested');fs.mkdirSync(output);const review=aggregate(audit,[response(audit,'author')],{baseDir:output,auditDir:dir});assert.equal(review.status,'complete');});
 check('audit任务合同必须与HTML一致',()=>{const file=path.join(dir,'audit.json');const options={inputHtml:htmlFile,inputPdf:pdfFile,html,pdf:fs.readFileSync(pdfFile),htmlPages:1,pdfPages:1,pdfSha256:audit.pdfArtifact.sha256};fs.writeFileSync(file,JSON.stringify(audit));assert.doesNotThrow(()=>validateAudit(file,options));const wrong=structuredClone(audit);wrong.taskContract=contract.normalize({kind:'report',complexity:'complex'});fs.writeFileSync(file,JSON.stringify(wrong));assert.throws(()=>validateAudit(file,options),/任务合同/);});
 check('legacy继续可用且状态顺序无关',()=>{const a={pages:1,htmlArtifact:{sha256:'h'},pdfArtifact:{sha256:'p'}},r={schemaVersion:2,status:'complete',htmlSha256:'h',pdfSha256:'p',reviewer:'author',independence:'author',coverage:[{reviewer:'author',independence:'author',layers:['page','exhibit','annotation','typography'],htmlPages:[1],pdfPages:[1],evidence:[{path:path.join(dir,'html.png'),sha256:contract.fileHash(path.join(dir,'html.png'))}]}],checks:response(audit,'author').checks,issues:[]};const other=structuredClone(r);other.checks.analysis.status='not_applicable';const ab=run(a,[r,other]),ba=run(a,[other,r]);assert.equal(ab.status,'complete');assert.deepEqual(ab.checks,ba.checks);assert.doesNotThrow(()=>saveAndCheck(a,ab));});
 console.log(JSON.stringify({pass:true,cases,scope:'synthetic review contract integration'}));
}finally{fs.rmSync(dir,{recursive:true,force:true});}
