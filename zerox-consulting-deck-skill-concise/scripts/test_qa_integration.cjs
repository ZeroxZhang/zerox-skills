/* 真正装配、浏览器打印和 PDF 栅格路径的集成反例；保留旧 QA 测试独立运行。 */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {assemble}=require('./assemble_deck.cjs');
const contracts=require('./report_contract.cjs');
(async()=>{const dir=fs.mkdtempSync(path.join(os.tmpdir(),'qa-integration-'));try{
 const pages=path.join(dir,'pages.html'),deck=path.join(dir,'deck.html'),taskFile=path.join(dir,'task.json');
 const pagesContract=path.join(dir,'pages.json');
 fs.writeFileSync(pagesContract,JSON.stringify({version:1,pages:[{page:1,proves:'样本比例不能被读成最终收入比',form:'html.text'}]}));
 // 密度档位写 normal：这份夹具的正文区只有一行结论，考的是集成链而不是版式密度。
 const task={workMode:'editorial',complexity:'simple',densityPolicy:'normal',critical:[{id:'limit',text:'不是最终收入比',target:'value'}],pages:{record:'pages.json'}};
 fs.writeFileSync(taskFile,JSON.stringify(task));
 fs.writeFileSync(pages,'<section class="slide reading" data-page-id="evidence" data-frame-boundary="space" data-form="html.text" data-proves="样本比例不能被读成最终收入比"><header class="slide__header"><h1 class="slide__title">关键限定完整性</h1></header><div class="slide__body" style="align-content:start"><div id="value">样本比例 38%</div><p data-critical-id="limit" data-critical-for="value">不是最终收入比</p></div><div class="source">合成验证材料</div><div class="slide__page">1</div></section>');
 await assemble({pagesFile:pages,outputFile:deck,contractFile:taskFile});const source=fs.readFileSync(deck,'utf8');
 const cases=[
  ['baseline',source,true,null],
  // 关联对象是内嵌 <style> 的 SVG（ECharts SSR 就这样）：CSS 选择器不是图上看得见的内容，
  // 混进 targetText 会让 PDF 的"关联对象不完整"把一页正常稿子判成失败。
  ['critical-on-svg',source.replace('<div id="value">样本比例 38%</div>',
    '<div id="value"><svg width="360" height="120" viewBox="0 0 360 120"><style>.zr123-cls-0:hover{fill:#123456}</style><rect x="4" y="4" width="300" height="16" fill="#8899aa"/><text x="8" y="70">样本比例 38%</text></svg></div>'),true,null],
  ['print-loss',source.replace('</head>','<style>@media print{[data-critical-id]{display:none!important}}</style></head>'),false,/关键语义|关键文字/],
  ['custom-edge',source.replace('</head>','<style>[data-critical-id]{border-left:3px solid teal;padding:12px}</style></head>'),false,/视觉禁令/],
  ['task-mismatch',source.replace('data-ratio="16x9"','data-ratio="4x3"'),false,/ratio不一致/],
  ['planner-missing',contracts.install(source,{...contracts.read(source),planner:{mode:'used',record:'missing.json',sha256:'a'.repeat(64)}}),false,/planner合同/]
 ];
 for(const [name,html,pass,expected] of cases){const file=path.join(dir,name+'.html'),out=path.join(dir,name);fs.writeFileSync(file,html);const proc=spawnSync(process.execPath,[path.join(__dirname,'qa_deck.cjs'),file,out],{env:process.env,encoding:'utf8',maxBuffer:20*1024*1024});if(!fs.existsSync(path.join(out,'audit.json')))throw Error(name+': '+proc.stderr+proc.stdout);const audit=JSON.parse(fs.readFileSync(path.join(out,'audit.json')));assert.equal(audit.geometryStatus,pass?'PASS':'FAIL',name+JSON.stringify(audit.errors));if(expected)assert.ok(audit.errors.some(e=>expected.test(e)),name+JSON.stringify(audit.errors));if(pass){assert.equal(audit.plannerExecution.status,'DIRECT');assert.equal(audit.evidenceManifest.entries.length,2);assert.ok(audit.evidenceManifest.entries.some(e=>e.medium==='pdf'&&e.path==='pdf-p01.png'));assert.deepEqual(audit.rows[0].criticalPdf.errors,[]);assert.equal(audit.taskContract.reviewPolicy,'author');}console.log(name+': '+audit.geometryStatus);}
 // 声明为图却只给表格：不带数据条的替代表要失败，带数据条 sparkline 的替代表也要失败。
 const svgPages=path.join(dir,'svg-pages.html'),svgDeck=path.join(dir,'svg-deck.html'),svgTask=path.join(dir,'svg-task.json'),svgRecord=path.join(dir,'svg-pages.json');
 fs.writeFileSync(svgRecord,JSON.stringify({version:1,pages:[{page:1,proves:'两条渠道的差额与量级',form:'kit.dumbbell'}]}));
 fs.writeFileSync(svgTask,JSON.stringify({workMode:'editorial',complexity:'simple',densityPolicy: 'normal', planner:{mode:'direct'},pages:{record:'svg-pages.json'},critical:[]}));
 const body=table=>`<section class="slide reading" data-frame-boundary="space" data-form="kit.dumbbell" data-proves="两条渠道的差额与量级"><header class="slide__header"><h1 class="slide__title">渠道差额</h1></header><div class="slide__body">${table}</div><div class="source">合成验证材料</div><div class="slide__page">1</div></section>`;
 fs.writeFileSync(svgPages,body('<table class="data-table"><thead><tr><th>渠道</th><th>差额</th></tr></thead><tbody><tr><td>商超</td><td>−1.1</td></tr></tbody></table>'));
 await assemble({pagesFile:svgPages,outputFile:svgDeck,contractFile:svgTask});
 const sparkline='<svg class="table-bar" viewBox="0 0 160 14"><rect x="0" y="3" width="80" height="8" fill="#000080" data-value="1"/></svg>';
 const bypass=fs.readFileSync(svgDeck,'utf8').replace('</tbody>',`<tr><td>电商</td><td>${sparkline}</td></tr></tbody>`);
 for(const [name,html] of [['svg-form-as-table',fs.readFileSync(svgDeck,'utf8')],['svg-form-as-table-with-sparkline',bypass]]){
  const file=path.join(dir,name+'.html'),out=path.join(dir,name);fs.writeFileSync(file,html);
  const proc=spawnSync(process.execPath,[path.join(__dirname,'qa_deck.cjs'),file,out],{env:process.env,encoding:'utf8',maxBuffer:20*1024*1024});
  const audit=JSON.parse(fs.readFileSync(path.join(out,'audit.json')));
  assert.equal(audit.geometryStatus,'FAIL',name+' 必须失败：'+JSON.stringify(audit.errors));
  assert.ok(audit.errors.some(e=>/是图形实现，但正文里没有 SVG/.test(e)),name+' 未命中声明不一致：'+JSON.stringify(audit.errors));
  console.log(name+': '+audit.geometryStatus);
 }
 console.log('PASS QA integration: actual PDF evidence, critical text, decoration, task identity, planner binding and svg-form substitution');
}finally{fs.rmSync(dir,{recursive:true,force:true})}})().catch(e=>{console.error(e);process.exitCode=1});
