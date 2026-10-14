/* 两类原始输入的证据、派生、选型与最终输出测试；不以文件存在充当通过。 */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {build,analyze}=require('./build_dense_reference.cjs'),{render}=require('./render_echarts_svg.cjs'),themes=require('../assets/deck-themes.js');
const input=path.resolve(__dirname,'../assets/dense-input-example'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'dense-input-test-'));
const data=analyze(),byId=new Map(data.evidence.map(e=>[e.id,e]));
assert.equal(data.rows.length,1152);assert.equal(data.evidence.filter(e=>e.source.title==='operations.csv'&&e.status==='synthetic').length,1152);
assert.equal(data.inventory[1].paragraphs,42);assert.equal(data.coding.cases.length,6);
for(const c of data.coding.cases)for(const kind of ['support','boundary']){const item=c[kind];assert.ok(item.evidence_ids.length>1);assert.equal(item.evidence_ids.map(id=>byId.get(id).claim).join(''),item.quote);for(const id of item.evidence_ids){const e=byId.get(id);assert.equal(item.quote.slice(e.source.char_start,e.source.char_end),e.claim);}}
for(const e of data.evidence.filter(e=>e.formula?.startsWith('SUM'))){assert.ok(e.input_ids.length);assert.equal(e.value,e.input_ids.reduce((v,id)=>v+byId.get(id).value,0));}
assert.equal(byId.get('D-GROWTH').value,(byId.get('D-Y2025').value/byId.get('D-Y2024').value-1)*100);
assert.equal(data.regions.reduce((n,r)=>n+r.value,0),byId.get('D-Y2025').value);
for(const theme of themes.ids){
 const result=build(path.join(tmp,theme),theme);
 // 字体子集的 base64 可能偶然包含“NaN”字符，不是页面中的非有限数值；只扫描可解释的 HTML/CSS/SVG。
 const inspectable=result.html.replace(/<style\b[^>]*id="deck-fonts"[^>]*>[\s\S]*?<\/style>/g,'');
 assert.equal(result.pages,6);assert.doesNotMatch(result.html,/<script\s+src=/);assert.doesNotMatch(inspectable,/NaN|Infinity/);
 for(const p of result.plans)for(const id of p.evidence_ids)assert.ok(byId.has(id),'页面孤立证据 '+id);
 // 24项单图实测遮挡后拆成两个同量尺分面：成稿仍是图，全部24个地区一个不少。
 const expected=[...data.regions].sort((a,b)=>b.value-a.value),labels=[];
 for(const m of result.plans[1].modules){
  assert.equal(m.render_route,'echarts-recipe');
  const r=render({recipe:m.recipe,spec:m.spec,width:590,height:440,theme_id:theme});
  assert.equal(r.pages[0].kind,'chart');
  // 成稿里必须真的出现这一分面的每个标签与数值，不能只核对输入 spec。
  const texts=[...r.pages[0].svg.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(x=>x[1].replace(/<[^>]*>/g,''));
  for(const item of m.spec.items){
   assert.ok(texts.includes(item.label),'分面缺少地区 '+item.label);
   assert.ok(texts.includes(item.value.toLocaleString('zh-CN',{maximumFractionDigits:2})),'分面缺少数值 '+item.value);
   labels.push(item.label);
  }
 }
 assert.deepEqual(labels,expected.map(d=>d.label));assert.equal(result.plans[1].modules[0].spec.max,result.plans[1].modules[1].spec.max,'两个分面必须共用同一数值量尺');
 // 逐月查数且占比0–0.4%的页主动选表，不是绘图失败后的替换。
 const small=result.plans[2].modules[0];
 assert.equal(small.render_route,'html-css');assert.equal(small.selected_visual,'月度构成明细表');assert.equal(small.recipe,null);
 assert.equal((result.html.match(/data-composition-month=/g)||[]).length,24);
 const zeroMonths=data.composition.filter(m=>m.segments[1].value===0).length;
 assert.ok(zeroMonths>0,'夹具必须含零值');assert.equal((result.html.match(/data-zero="true"/g)||[]).length,zeroMonths*2);
 for(const c of data.coding.cases){assert.ok(result.html.includes(c.support.quote));assert.ok(result.html.includes(c.boundary.quote));assert.ok(result.html.includes(c.action));assert.ok(result.html.includes('data-case="'+c.id+'"'));}
 assert.ok(result.plans.slice(3).every(p=>p.modules[0].reader_operation==='A-15'&&p.modules[0].render_route==='html-css'));
 assert.equal(result.plans[0].modules[0].selected_visual,'timeSeries','有空间的趋势图应保持图形表达');
}
// 破坏输入验证真正的门禁，不只核对同一实现输出的元数据。
const bad=path.join(tmp,'invalid');fs.mkdirSync(bad);for(const name of ['operations.csv','field-notes.md','text-coding.json'])fs.copyFileSync(path.join(input,name),path.join(bad,name));
const csv=fs.readFileSync(path.join(input,'operations.csv'),'utf8');
fs.writeFileSync(path.join(bad,'operations.csv'),csv.replace(',万元,',',亿元,'));assert.throws(()=>analyze(bad),/单位/);
fs.writeFileSync(path.join(bad,'operations.csv'),csv.replace('R01-202401-B','R01-202401-A'));assert.throws(()=>analyze(bad),/重复/);
fs.writeFileSync(path.join(bad,'operations.csv'),csv);const coding=JSON.parse(fs.readFileSync(path.join(input,'text-coding.json'),'utf8'));coding.cases[0].support.quote+='不存在的句子';fs.writeFileSync(path.join(bad,'text-coding.json'),JSON.stringify(coding));assert.throws(()=>analyze(bad),/引文/);
console.log('PASS: 1152条明细→逐条来源与派生校验→24地区两栏同量尺排名/逐月零值明细表；42段长文本→6案例支持/边界/建议；三主题6页离线输出；拒绝错误单位、重复主键与虚假引文。临时证据：'+tmp);
