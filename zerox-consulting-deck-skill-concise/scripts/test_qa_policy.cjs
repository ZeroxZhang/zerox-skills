/* 对实际HTML/PDF做定向突变，验证建议可放宽而明显不可读与打印丢图仍被阻止。 */
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-qa-policy-'));
try{
 const source=fs.readFileSync(path.join(root,'assets/reference_deck.html'),'utf8');
 const cases=[
  ['baseline','',true],
  ['small-warning','.source{font-size:11px!important}',true],
  ['unreadable','.source{font-size:8px!important}',false],
  ['print-loss','@media print{.slide svg{display:none!important}}',false],
  ['html-print-loss','@media print{.slide:nth-of-type(2) .slide__body{display:none!important}}',false]
 ];
 for(const [name,css,pass] of cases){
  const html=path.join(dir,name+'.html'),out=path.join(dir,name);fs.writeFileSync(html,source.replace('</head>','<style>'+css+'</style></head>'));
  const result=spawnSync(process.execPath,[path.join(__dirname,'qa_deck.cjs'),html,out],{encoding:'utf8',env:process.env,maxBuffer:20*1024*1024});
  if(!fs.existsSync(path.join(out,'audit.json')))throw Error(name+'未产生审计：'+result.stderr+result.stdout);
  const audit=JSON.parse(fs.readFileSync(path.join(out,'audit.json'),'utf8'));
  assert.equal(audit.geometryStatus,pass?'PASS':'FAIL',name+': '+JSON.stringify(audit.errors));assert.equal(result.status,pass?0:1);
  if(name==='small-warning'){assert.ok(audit.warnings.length);assert.ok(audit.rows.every(r=>!r.unreadableText.length));}
  if(name==='unreadable')assert.ok(audit.rows.some(r=>r.unreadableText.length));
  if(name==='print-loss'){assert.ok(audit.printCheck.missing.length);assert.ok(audit.errors.some(e=>/打印缺少/.test(e)));}
  if(name==='html-print-loss')assert.ok(audit.errors.some(e=>/正文文字覆盖率不足/.test(e)));
  console.log(name+': '+audit.geometryStatus+'; warnings='+audit.warnings.length+'; printMissing='+audit.printCheck.missing.length);
 }
 console.log('PASS: baseline / 建议字号放宽 / 明显不可读阻止 / SVG与HTML正文打印丢失阻止。');
}finally{fs.rmSync(dir,{recursive:true,force:true});}
