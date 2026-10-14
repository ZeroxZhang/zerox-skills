/* 任务选择的优先级与冻结记录；不把结构验证冒称成稿审美通过。 */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const c=require('./report_contract.cjs'),{args}=require('./assemble_deck.cjs');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'task-contract-'));
try{
 const selected={mode:'presentation',theme:'bcg',typography:'sans-presentation',ratio:'4x3',complexity:'simple',kind:'report'};
 const f=path.join(dir,'task.json');fs.writeFileSync(f,JSON.stringify(selected));
 assert.deepEqual(c.load(f,path.join(dir,'deck.html')).mode,'presentation');
 const result=c.load(f,path.join(dir,'deck.html'),{theme:'mckinsey',ratio:'16x9'});
 assert.equal(result.theme,'bcg');assert.equal(result.ratio,'4x3');assert.equal(result.reviewPolicy,'author');
 assert.equal(c.normalize({kind:'fragment',complexity:'complex'}).reviewPolicy,'independent');
 assert.equal(c.normalize({complexity:'simple',majorConclusion:true}).reviewPolicy,'independent');
 assert.throws(()=>c.normalize({...selected,reviewPolicy:'independent'}),/冲突/);
 assert.throws(()=>c.normalize({critical:[{id:'a',text:'x'},{id:'a',text:'x'}]}),/唯一/);
 assert.throws(()=>c.normalize({planner:{mode:'unavailable'}}),/限制/);
 assert.throws(()=>c.normalize({planner:{mode:'used',record:'a'}}),/sha256/);
 const record=path.join(dir,'spec.json');fs.writeFileSync(record,'{}');
 fs.writeFileSync(f,JSON.stringify({...selected,planner:{mode:'used',record:'spec.json'}}));
 const bound=c.load(f,path.join(dir,'nested/deck.html'));
 assert.equal(bound.planner.record,'../spec.json');assert.equal(bound.planner.sha256,c.fileHash(record));
 fs.writeFileSync(f,JSON.stringify({...selected,planner:{mode:'used',record:'spec.json',sha256:bound.planner.sha256}}));
 fs.writeFileSync(record,'{"changed":true}');assert.throws(()=>c.load(f,path.join(dir,'deck.html')),/版本/);
 const html=c.install('<html><head></head><body></body></html>',selected);
 assert.equal(c.read(html).theme,'bcg');assert.match(html,/data-reliability-version="2"/);
 assert.equal(c.read(c.install(html,{...selected,theme:'accenture'})).theme,'accenture');
 assert.throws(()=>c.read(html.replace('</head>',html.match(/<script[\s\S]*<\/script>/)[0]+'</head>')),/重复/);
 assert.equal(args(['pages','deck','--contract','task']).contractFile,'task');
 assert.equal(args(['pages','deck','--contract','task']).theme,undefined);
 console.log('PASS task contract: preference precedence, risk policy, critical ids, planner digest, embedded roundtrip, CLI omissions');
}finally{fs.rmSync(dir,{recursive:true,force:true})}
