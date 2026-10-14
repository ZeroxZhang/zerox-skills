/* 有限继承结构合成测试：文件摘要可核验，不表示实际PDF或目视质量通过。 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {hash,fileHash,stable,normalize}=require('./report_contract.cjs');
const {validate,layers}=require('./review_contract.cjs');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'deck-inheritance-'));
const results={};
function fixture(name){
 const dir=path.join(root,name),oldDir=path.join(dir,'old'),newDir=path.join(dir,'new');fs.mkdirSync(oldDir,{recursive:true});fs.mkdirSync(newDir);
 const create=(folder,changed)=>{
  const artifacts={};for(const medium of ['html','pdf']){const file=path.join(folder,'deck.'+medium);fs.writeFileSync(file,'synthetic '+medium+' artifact '+changed);artifacts[medium+'Artifact']={path:path.basename(file),sha256:fileHash(file)};}
  const deps=hash('shared stylesheet/font/runtime'),entries=[];
  for(let page=1;page<=2;page++)for(const medium of ['html','pdf']){const file=path.join(folder,medium+'-'+page+'.png');fs.writeFileSync(file,'synthetic '+medium+' screenshot page '+page+(page===2?changed:''));entries.push({id:medium+':p'+page,medium,page,pageId:'p'+page,path:path.basename(file),sha256:fileHash(file),pageSha256:hash('page '+page+(page===2?changed:'')),pageStyleSha256:hash('page style '+page+(page===2?changed:'')),sourceSha256:artifacts[medium+'Artifact'].sha256,dependenciesSha256:deps});}
  return {pages:2,geometryStatus:'PASS',errors:[],tier:'acceptance',acceptance:{complete:true,tier:'acceptance',missingStages:[]},documentContract:{reliability:'2',kind:'fragment'},taskContract:normalize({kind:'fragment',complexity:'simple'}),...artifacts,evidenceManifest:{version:1,dependenciesSha256:deps,entries}};
 };
 const coverage=pages=>({reviewer:'author',independence:'author',layers:[...layers],htmlPages:pages,pdfPages:pages,evidence:pages.flatMap(page=>['html','pdf'].map(m=>({id:m+':p'+page}))),attestation:pages.map((page,i)=>({page,note:'合成结构测试第 '+page+' 页所见 '+i}))});
 const review=(audit,rows)=>({schemaVersion:3,status:'complete',reviewer:'author',independence:'author',isolation:'same-session',htmlSha256:audit.htmlArtifact.sha256,pdfSha256:audit.pdfArtifact.sha256,auditSha256:hash(stable(audit)),checks:Object.fromEntries(['analysis','evidence','visual'].map(key=>[key,{status:'pass',basis:'仅合成结构测试 '+key}])),issues:[],coverage:rows});
 const oldAudit=create(oldDir,'old'),currentAudit=create(newDir,'new'),oldReview=review(oldAudit,[coverage([1,2])]);
 const auditFile=path.join(oldDir,'audit.json'),reviewFile=path.join(oldDir,'review.json');
 const saveOld=()=>{oldReview.auditSha256=hash(stable(oldAudit));fs.writeFileSync(auditFile,JSON.stringify(oldAudit));fs.writeFileSync(reviewFile,JSON.stringify(oldReview));};saveOld();
 const currentReview=review(currentAudit,[coverage([1]),coverage([2])]);
 const bind=()=>currentReview.coverage[0].inheritedFrom={basis:'仅第二页内容改变；第一页内容与共享依赖及渲染字节未变',audit:{path:'../old/audit.json',sha256:fileHash(auditFile)},review:{path:'../old/review.json',sha256:fileHash(reviewFile)}};bind();
 const run=()=>{currentReview.auditSha256=hash(stable(currentAudit));return validate(currentReview,currentAudit,{baseDir:newDir,auditDir:newDir});};
 return {dir,oldDir,newDir,oldAudit,currentAudit,oldReview,currentReview,saveOld,bind,run,coverage,auditFile,reviewFile};
}
function test(name,mutate,pattern){const f=fixture(name);if(mutate)mutate(f);const errors=f.run();if(pattern)assert.ok(errors.some(e=>pattern.test(e)),name+': '+errors.join('; '));else assert.deepEqual(errors,[],name);results[name]=pattern?'REJECTED':'PASS';}
try{
 test('unchanged_page_inherits_changed_page_reviewed');
 test('changed_page_cannot_inherit',f=>{f.currentReview.coverage[1].inheritedFrom=structuredClone(f.currentReview.coverage[0].inheritedFrom);},/须重新审查/);
 for(const type of ['style','font','runtime'])test(type+'_dependency_change',f=>{const dep=hash(type+' changed');f.currentAudit.evidenceManifest.dependenciesSha256=dep;f.currentAudit.evidenceManifest.entries.forEach(e=>e.dependenciesSha256=dep);},/须重新审查/);
 // 页级失效半径：unchanged_page_inherits_changed_page_reviewed 里的第二页同时改了 DOM 与样式作用域，
 // 第一页仍能继承。这里反过来证明第一页自己的样式作用域一变就必须重审——且不依赖 PNG 字节。
 test('page_style_only_change_cannot_inherit',f=>{const old=f.oldAudit.evidenceManifest.entries;for(const e of f.currentAudit.evidenceManifest.entries.filter(e=>e.page===1)){const p=old.find(o=>o.id===e.id);e.sha256=p.sha256;e.pageSha256=p.pageSha256;e.pageStyleSha256=hash('仅样式作用域改变');}},/须重新审查/);
 // 旧稿的证据清单没有 pageStyleSha256：两侧都缺时按"不可判"处理，不因为新字段把旧稿一律判死。
 test('legacy_manifest_without_page_style_still_inherits',f=>{for(const a of [f.oldAudit,f.currentAudit])a.evidenceManifest.entries.forEach(e=>delete e.pageStyleSha256);f.saveOld();f.bind();});
 test('non_acceptance_tier_cannot_be_inherited',f=>{f.oldAudit.tier='smoke';f.oldAudit.acceptance={complete:false,tier:'smoke',missingStages:['PDF产物校验']};f.saveOld();f.bind();},/不是验收档/);
 // audit 的告警必须逐条被处置过：可以判它不构成问题，但不能没人看过就交付。
 const warning='第1页标题超过两行建议，请目视判断';
 test('audit_warning_without_disposition',f=>{f.currentAudit.warnings=[warning];},/告警未处置/);
 test('audit_warning_disposition_partial',f=>{f.currentAudit.warnings=[warning,'第2页部分文字低于建议字号，请按实际可读性复核'];f.currentReview.warningReview=[{warning,status:'accepted',note:'已按实际尺寸看过，两行是该页标题的必要断行'}];},/告警未处置/);
 test('audit_warning_disposition_accepted',f=>{f.currentAudit.warnings=[warning];f.currentReview.warningReview=[{warning,status:'accepted',note:'已按实际尺寸看过，两行是该页标题的必要断行'}];});
 test('audit_warning_disposition_fixed',f=>{f.currentAudit.warnings=[warning];f.currentReview.warningReview=[{warning,status:'fixed',note:'已收短标题至一行并重跑验收档'}];});
 test('audit_warning_disposition_bad_status',f=>{f.currentAudit.warnings=[warning];f.currentReview.warningReview=[{warning,status:'ignored',note:'看过'}];},/告警处置格式无效/);
 test('audit_warning_disposition_without_note',f=>{f.currentAudit.warnings=[warning];f.currentReview.warningReview=[{warning,status:'accepted',note:'  '}];},/告警处置格式无效/);
 test('current_png_changed',f=>fs.appendFileSync(path.join(f.newDir,'html-1.png'),'tampered'),/当前渲染图缺失/);
 test('current_png_new_digest_still_rejects_inheritance',f=>{const e=f.currentAudit.evidenceManifest.entries[0];fs.appendFileSync(path.join(f.newDir,e.path),'new render');e.sha256=fileHash(path.join(f.newDir,e.path));},/须重新审查/);
 test('old_png_changed',f=>fs.appendFileSync(path.join(f.oldDir,'pdf-1.png'),'tampered'),/当前渲染图缺失/);
 for(const type of ['html','pdf'])test('old_'+type+'_artifact_changed',f=>fs.appendFileSync(path.join(f.oldDir,'deck.'+type),'tampered'),/旧产物缺失/);
 test('old_review_changed',f=>fs.appendFileSync(f.reviewFile,' '),/旧审查\/audit摘要/);
 test('old_audit_changed',f=>fs.appendFileSync(f.auditFile,' '),/旧审查\/audit摘要/);
 test('different_reviewer_cannot_inherit',f=>{f.currentReview.reviewer='other';f.currentReview.coverage.forEach(c=>c.reviewer='other');},/旧审查者未覆盖/);
 test('medium_mismatch',f=>f.currentReview.coverage[0].evidence=[{id:'html:p1'}],/页号\/媒介/);
 test('missing_open_issue',f=>{f.oldReview.issues=[{severity:'minor',status:'open',description:'旧稿尚存的小问题'}];f.saveOld();f.bind();},/丢失旧未决问题/);
 test('preserve_open_minor_issue',f=>{const issue={severity:'minor',status:'open',description:'旧稿尚存的小问题'};f.oldReview.issues=[issue];f.currentReview.issues=[structuredClone(issue)];f.saveOld();f.bind();});
 test('missing_change_basis',f=>f.currentReview.coverage[0].inheritedFrom.basis='',/变更依据/);
 test('old_incomplete_review',f=>{f.oldReview.status='incomplete';f.saveOld();f.bind();},/审查未完成/);
 test('old_engineering_failure',f=>{f.oldAudit.geometryStatus='FAIL';f.saveOld();f.bind();},/旧工程检查未通过/);
 test('old_audit_review_binding_mismatch',f=>{f.oldReview.auditSha256=hash('wrong');fs.writeFileSync(f.reviewFile,JSON.stringify(f.oldReview));f.bind();},/未绑定当前/);
 test('page_identity_changed',f=>{for(const e of f.currentAudit.evidenceManifest.entries.filter(e=>e.page===1)){e.pageId='renamed';e.id=e.medium+':renamed';}f.currentReview.coverage[0].evidence=[{id:'html:renamed'},{id:'pdf:renamed'}];},/须重新审查/);
 test('page_order_changed',f=>{f.currentAudit.evidenceManifest.entries.forEach(e=>e.page=3-e.page);for(const c of f.currentReview.coverage){c.htmlPages=c.htmlPages.map(p=>3-p);c.pdfPages=c.pdfPages.map(p=>3-p);}},/须重新审查/);
 console.log(JSON.stringify({pass:true,cases:Object.keys(results).length,scope:'synthetic inheritance structure only',results}));
}finally{fs.rmSync(root,{recursive:true,force:true});}
