/* 验证派生计算、编码比例、数据完整性与错误回退，不把固定文案当测试目标。 */
const assert=require('node:assert/strict'),kit=require('../assets/exhibit-kit.js'),themes=require('../assets/deck-themes.js');
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
close(kit.difference(11.2,10.4).value,-.8);
close(kit.difference(100,160,{mode:'relative'}).value,60);
close(kit.difference(.2,.35,{mode:'pp',basis:'fraction'}).value,15);
close(kit.difference(20,35,{mode:'pp',basis:'percent'}).value,15);
close(kit.difference(100,160,{mode:'cagr',periods:2}).value,(Math.sqrt(1.6)-1)*100);
assert.equal(kit.formatNumber(-.0001,{decimals:1}),'0.0');
assert.equal(kit.formatNumber(1234.5,{decimals:2}),'1,234.50');
for(const args of [[0,2,{mode:'relative'}],[-2,4,{mode:'relative'}],[.2,.3,{mode:'pp'}],[10,0,{mode:'cagr',periods:2}],[10,20,{mode:'cagr',periods:0}]])assert.throws(()=>kit.difference(...args));
const items=[{label:'甲',segments:[{label:'核心',value:80},{label:'新业务',value:20}]},{label:'乙',segments:[{label:'核心',value:90},{label:'新业务',value:60}]}];
const rects=svg=>[...svg.matchAll(/<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"[^>]+data-value="([^"]+)"/g)].map(m=>({x:+m[1],y:+m[2],w:+m[3],h:+m[4],v:+m[5]}));
for(const id of themes.ids){
  const palette=themes.palette(id);
  const a=rects(kit.stacked({palette,items})),p=rects(kit.stacked({palette,items,mode:'percent'})),m=rects(kit.mekko({palette,items}));
  a.forEach(r=>close(r.h/r.v,a[0].h/a[0].v));
  close(p[0].h+p[1].h,p[2].h+p[3].h);
  m.forEach(r=>close(r.w*r.h/r.v,m[0].w*m[0].h/m[0].v));
  close(m[2].w/m[0].w,1.5);
  const wf=kit.waterfall({palette,items:[{label:'起点',type:'total',value:10},{label:'下降',type:'delta',value:-15},{label:'恢复',type:'delta',value:8},{label:'终点',type:'subtotal'}],comparison:{from:0,to:3}});
  assert.match(wf,/data-from="10" data-to="-5"/);assert.match(wf,/>−7<\/text>/);
  assert.doesNotMatch(wf,/NaN|Infinity|undefined/);
  const t=kit.comparisonTable({palette,columns:[{key:'d',label:'变化',type:'number',derive:{from:'a',to:'b'},bar:{domain:[-2,2]}}],rows:[{values:{a:1,b:2}},{values:{a:2,b:1}}]});
  assert.match(t,new RegExp('fill="'+palette.positive+'" data-value="1"'));
  assert.match(t,new RegExp('fill="'+palette.negative+'" data-value="-1"'));
  const valueTable=kit.comparisonTable({palette,columns:[{key:'a',label:'原值',type:'number',bar:{domain:[0,2]}}],rows:[{values:{a:1}}]});
  assert.match(valueTable,new RegExp('fill="'+palette.accent+'" data-value="1"'));
}
const narrow=[{label:'甲',segments:[{label:'核心',value:100},{label:'新业务',value:0}]},{label:'乙',segments:[{label:'核心',value:1},{label:'新业务',value:1}]}];
// 小片、零值与窄列改走同侧引线通道：面积编码不变，图形与关键标注仍留在图上，不再自动转表。
const callouts=kit.mekko({width:620,height:440,items:narrow,labelContent:'both'});
assert.match(callouts,/>新业务 0 \(0%\)<\/text>/);assert.match(callouts,/>核心 1 \(50%\)<\/text>/);
assert.match(callouts,/>乙<\/text>/);assert.match(callouts,/data-role="zero-mark"/);
assert.equal([...callouts.matchAll(/data-role="leader"/g)].length,5);
assert.equal(rects(callouts).find(r=>r.v===0).h,0);
assert.doesNotMatch(callouts,/<table|完整数据表/);
const wide=[{label:'甲',segments:[{label:'核心',value:80},{label:'新业务',value:20}]},{label:'乙',segments:[{label:'核心',value:90},{label:'新业务',value:60}]}];
for(const type of ['stacked','mekko']){
  const shares=kit[type]({width:800,height:500,items:wide,labelContent:'share'});
  assert.match(shares,/>80%<\/text>/);assert.doesNotMatch(shares,/>80<\/text>/);
  assert.doesNotMatch(kit[type]({width:800,height:500,items:wide}),/data-role="leader"/,'放得下时不出现引线通道');
}
assert.throws(()=>kit.mekko({width:320,height:200,items:narrow}),/绘图区/);
assert.throws(()=>kit.mekko({items:narrow,labels:'table'}),/改表开关/);
// 收窄绘图区会带出更长的外置标注；通道宽度必须跟着重算，不能把标签画到画布外。
const overlong=[{label:'二二二二二二二二二二二二二二二二二二二二',segments:[{label:'甲',value:900},{label:'乙',value:1}]},{label:'乙列',segments:[{label:'甲',value:1},{label:'乙',value:1}]}];
assert.throws(()=>kit.stacked({width:800,height:500,items:overlong}),/超出通道可用宽度/);
for(const type of ['stacked','mekko']){
  const svg=kit[type]({width:800,height:500,items:[{label:'甲',segments:[{label:'核心',value:900},{label:'小项',value:1}]},{label:'乙',segments:[{label:'核心',value:1},{label:'小项',value:1}]}]});
  const minX=Math.min(...[...svg.matchAll(/<text x="([\d.-]+)"/g)].map(m=>+m[1]));
  assert.ok(minX>=0,type+' 外置标注越出画布左边界：'+minX);
}
const crowded=[{label:'成熟市场',segments:[{label:'主业',value:600},{label:'试点',value:400}]},{label:'新市场甲',segments:[{label:'主业',value:1},{label:'试点',value:1}]},{label:'新市场乙',segments:[{label:'主业',value:2},{label:'试点',value:1}]}];
// 两个窄列的分项都进引线通道，通道用满整幅高度；画布真的放不下时明确拒绝，仍不给表格。
const cramped=kit.mekko({width:800,height:500,items:crowded,labelContent:'both'});
assert.equal([...cramped.matchAll(/data-role="leader"/g)].length,8);assert.doesNotMatch(cramped,/<table/);
assert.throws(()=>kit.mekko({width:400,height:200,items:crowded,labelContent:'both'}),/绘图区|通道/);
assert.throws(()=>kit.mekko({items:[{label:'甲',segments:[{label:'一',value:2},{label:'一',value:3}]}]}),/唯一/);
assert.throws(()=>kit.stacked({items:[...items,{label:'缺项',segments:[{label:'核心',value:2}]}]}),/显式/);
assert.throws(()=>kit.stacked({items:[{label:'未知',segments:[{label:'核心',value:null}]}]}),/数值/);
const columns=[{key:'name',label:'对象'},{key:'a',label:'原值',type:'number',bar:{domain:[-10,10]}},{key:'delta',label:'差额',type:'number',derive:{from:'a',to:'b'}}];
const html=kit.comparisonTable({columns,rows:[{values:{name:'<script>',a:-5,b:2}},{values:{name:'零',a:0,b:0}},{values:{name:'缺失',a:null,b:10}}]});
assert.match(html,/&lt;script&gt;/);assert.match(html,/>\+7<\/td>/);assert.match(html,/aria-label="缺失"/);
const bars=rects(html);assert.equal(bars.length,2);close(bars[0].w,39.5);close(bars[1].w,0);
for(const d of [[0,0],[1,5],[-10,-2],[10,-10]])assert.throws(()=>kit.comparisonTable({columns:[{key:'a',label:'值',type:'number',bar:{domain:d}}],rows:[{values:{a:2}}]}));
assert.throws(()=>kit.comparisonTable({columns,rows:[{values:{a:11}}]}),/截断/);
assert.throws(()=>kit.waterfall({items:[{label:'初',type:'total',value:1},{label:'终',type:'subtotal'}],comparison:{from:1,to:0}}),/索引/);
const stages=[{label:'验证',owner:'业务',output:'清单',gate:'准入通过'},{label:'试点',owner:'财务',output:'经济性',gate:'达到门槛'}];
assert.match(kit.processFlow({stages,transitions:['通过']}),/准入通过/);
assert.throws(()=>kit.processFlow({stages,transitions:['通过','通过']}),/条件/);
assert.throws(()=>kit.processFlow({stages:[{...stages[0],output:'信息'.repeat(200)},stages[1]],transitions:['通过']}),/过长/);
console.log('v5 PASS: differences, CAGR intervals, signed/zero values, shared scales, composition geometry, zero and small-segment callouts, theme compatibility and invalid inputs');
