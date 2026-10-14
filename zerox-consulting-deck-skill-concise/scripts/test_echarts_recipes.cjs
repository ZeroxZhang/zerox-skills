/* 验证数值保真、标签完整性、分页和三主题真实SVG，不仅检查文件存在。 */
const assert=require('node:assert/strict'),r=require('../assets/echarts-recipes.js'),rt=require('../assets/chart-runtime.js'),themes=require('../assets/deck-themes.js');
const {render}=require('./render_echarts_svg.cjs'),echarts=require(process.env.ECHARTS_MODULE||'echarts');
const cases={
  rankedBar:{items:[{label:'乙',value:2},{label:'甲',value:5,selected:true}],baseline:3},
  groupedBar:{categories:['甲','乙'],series:[{name:'本期',values:[8,-2]},{name:'上期',values:[6,1]}]},
  timeSeries:{periods:['2024','2025'],series:[{name:'收入',values:[10,12]}]},
  composition:{mode:'percent',items:[{label:'甲',segments:[{label:'核心',value:80},{label:'新业务',value:20}]}]},
  histogram:{bins:[{label:'0–10',value:3},{label:'10–20',value:7},{label:'20–30',value:2}]},
  scatter:{items:[{label:'甲',x:1,y:2,size:100},{label:'乙',x:2,y:1,size:25}]},
  heatmap:{rows:['市场'],columns:['规模','增长'],values:[[4,5]],min:1,max:5},
  sankey:{nodes:['入口','成交'],links:[{source:'入口',target:'成交',value:8}]},
  tree:{root:{label:'利润',value:888,children:[{label:'收入',value:999},{label:'成本',value:111}]}}
};
const texts=svg=>[...svg.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m=>m[1]).join('|');
assert.equal(echarts.version,require('../package.json').dependencies.echarts);
const bubble=r.scatter({items:[0,1,2,100].map((size,i)=>({label:String(i),x:i,y:i,size}))}).series[0].symbolSize;
assert.equal(bubble([0,0,0]),0);
assert.ok(Math.abs(bubble([0,0,2])**2/bubble([0,0,1])**2-2)<1e-12);
assert.equal(bubble([0,0,100]),42);
assert.throws(()=>r.scatter({items:[{label:'甲',x:0,y:0,size:2},{label:'乙',x:1,y:1}]}),/缺失/);
assert.throws(()=>r.rankedBar({items:[{label:'甲',value:10}],min:5}),/零/);
assert.throws(()=>r.sankey({nodes:['A','B'],links:[{source:'A',target:'B',value:1},{source:'B',target:'A',value:1}]}),/环/);
assert.throws(()=>r.sankey({nodes:['A','B','C'],links:[{source:'A',target:'B',value:10},{source:'B',target:'C',value:8}]}),/闭合/);
assert.throws(()=>r.sankey({nodes:['A'],links:[{source:'A',target:'B',value:1}]}),/未知节点/);
assert.throws(()=>r.heatmap({rows:['A'],columns:['B'],values:[[9]],min:0,max:5}),/覆盖/);
assert.throws(()=>r.composition({items:[{label:'A',segments:[{label:'x',value:1},{label:'x',value:2}]}]}),/唯一/);
const negative=r.timeSeries({periods:['一月','二月'],zeroBaseline:true,series:[{name:'净值',values:[-10,10]}]});
assert.equal(negative.yAxis.min,-10);assert.equal(negative.yAxis.max,10);

for(const theme_id of themes.ids){
 const t=themes.get(theme_id).tokens,settings={tokens:t,width:720,height:360};
 for(const [recipe,spec] of Object.entries(cases)){
  const result=render({recipe,spec,theme_id,width:720,height:360});
  assert.ok(result.pages.length);
  for(const p of result.pages){assert.match(p.svg,/^<svg/);assert.doesNotMatch(p.svg,/NaN|Infinity/);assert.ok(texts(p.svg).length>1);}
  if(recipe==='tree')assert.match(texts(result.pages[0].svg),/888/);
 }
 const items=Array.from({length:24},(_,i)=>({label:'渠道'+String(i+1).padStart(2,'0'),value:100-i}));
 // 画布不够时不产出替代表：预算只给风险提示，实测遮挡直接阻止输出。
 const tight=rt.prepare('rankedBar',{items},settings);
 assert.equal(tight.pages.length,1);assert.equal(tight.pages[0].kind,'chart');
 assert.ok(tight.risks.some(r=>r.code==='category-space'&&r.message.includes('24')));
 assert.equal('fallback' in tight,false);assert.equal('reason' in tight,false);assert.equal(rt.tablePages,undefined);
 assert.throws(()=>render({recipe:'rankedBar',spec:{items},theme_id,width:720,height:360}),/文字验收未通过[\s\S]*渠道/);
 const full=render({recipe:'rankedBar',spec:{items},theme_id,width:1200,height:800});
 assert.equal(full.pages[0].kind,'chart');items.forEach(d=>assert.ok(texts(full.pages[0].svg).includes(d.label)));
 assert.throws(()=>render({recipe:'composition',spec:{mode:'percent',items:[{label:'渠道',segments:[{label:'大项',value:99},{label:'小项',value:1},{label:'零项',value:0}]}]},theme_id,width:720,height:360}),/文字验收未通过[\s\S]*小项|文字验收未通过/);
 assert.throws(()=>rt.prepare('sankey',{nodes:['A','B'],links:[{source:'A',target:'B',value:0}]},settings),/全部流量为零/);
 const zeroBubble=rt.prepare('scatter',{items:[{label:'甲',x:1,y:2,size:0},{label:'乙',x:2,y:1,size:25}]},settings);
 assert.ok(zeroBubble.risks.some(r=>r.code==='zero-size'));
 assert.deepEqual(zeroBubble.pages[0].option.series[0].data[0].symbolSize,[9,9]);
 assert.match(zeroBubble.pages[0].option.graphic[0].style.text,/零规模的位置标记/);
 // 散点轴范围：运行时曾无条件写成"含零再向两侧留 12% 空白"，全为正的营收数据因此得到一条
 // 到 −49.44 的横轴——等于在图上声明负值可能发生；作者给的 min/max 也被静默覆写。
 {
  const axes=(spec)=>{const o=rt.prepare('scatter',spec,settings).pages[0].option;return {x:[o.xAxis.min,o.xAxis.max],y:[o.yAxis.min,o.yAxis.max]};};
  const pos=axes({items:[{label:'甲',x:98,y:18},{label:'乙',x:412,y:10}]});
  assert.equal(pos.x[0],0,'全正数据的横轴必须从 0 起，不能留出负向空白');
  assert.equal(pos.y[0],0,'全正数据的纵轴必须从 0 起');
  assert.ok(pos.x[1]>412,'正向留白仍要给最右标签让位');
  const neg=axes({items:[{label:'甲',x:-98,y:-18},{label:'乙',x:-412,y:-10}]});
  assert.equal(neg.x[1],0,'全负数据的横轴必须到 0 止，不能留出正向空白');
  assert.equal(neg.y[1],0,'全负数据的纵轴必须到 0 止');
  const span=axes({items:[{label:'甲',x:-98,y:-18},{label:'乙',x:412,y:16}]});
  assert.ok(span.x[0]<-98&&span.x[1]>412,'跨零数据仍要在两侧各自留白');
  const fixed=axes({items:[{label:'甲',x:98,y:18},{label:'乙',x:412,y:10}],xMin:90,xMax:420});
  assert.deepEqual(fixed.x,[90,420],'显式范围必须生效，不能被运行时覆写');
  assert.throws(()=>r.scatter({items:[{label:'甲',x:98,y:18},{label:'乙',x:412,y:10}],xMax:300}),/散点会被裁掉/,'收窄不能切掉数据');
  assert.throws(()=>r.scatter({items:[{label:'甲',x:98,y:18}],xMin:400,xMax:300}),/必须小于/);
  assert.doesNotThrow(()=>r.scatter({items:[{label:'甲',x:98,y:18},{label:'乙',x:412,y:10}],xMax:420}),'覆盖全部取值的收窄本来就该放行');
 }
 const flow=rt.prepare('sankey',cases.sankey,settings).pages[0].option;
 assert.equal(flow.series[0].data[0].itemStyle.color,t.accent);
 // 期间必须逐个画出来：轴标签被自动抽稀时要报 missing；画下但互相遮挡时报 overlap。两者都不能静默通过。
 for(const [periods,width,height] of [[14,588,300],[18,760,365]]){
  const dense=Array.from({length:periods},(_,i)=>(i+1)+'月');
  const r=render({recipe:'timeSeries',spec:{periods:dense,series:[{name:'收入',values:dense.map((_,i)=>10+i)}]},theme_id,width,height});
  const axisTexts=[...r.pages[0].svg.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m=>m[1].replace(/<[^>]*>/g,''));
  dense.forEach(p=>assert.ok(axisTexts.includes(p),periods+' 期 @'+width+' 少了期号 '+p));
 }
 assert.throws(()=>render({recipe:'timeSeries',spec:{periods:Array.from({length:36},(_,i)=>(i+1)+'月'),series:[{name:'收入',values:Array.from({length:36},(_,i)=>10+i)}]},theme_id,width:760,height:365}),/文字验收未通过[\s\S]*overlap/,'36 期在 760 宽内会互相遮挡，必须报出并交由作者分面');
 let root={label:'末级数据业务流程'};for(let i=8;i>=1;i--)root={label:'第'+i+'层业务处理步骤',children:[root]};
 const deep=rt.prepare('tree',{root},settings);
 assert.ok(deep.risks.some(r=>r.code==='node-space'));assert.equal('table' in deep.pages[0],false);
 const collision={xLabel:'收入',xUnit:'亿元',yLabel:'利润',yUnit:'亿元',sizeUnit:'人',items:[1,2,3,4,5].map(size=>({label:'对象'+size,x:1,y:1,size}))};
 assert.throws(()=>render({recipe:'scatter',spec:collision,theme_id,width:720,height:360}),/文字验收未通过/);
 assert.throws(()=>render({recipe:'groupedBar',spec:{categories:['甲'],series:[{name:'很长的系列名称和口径说明'.repeat(8),values:[5]}]},theme_id,width:720,height:360}),/文字验收未通过/);
 // 逐个探测连续色阶，用ECharts实际映射底色测量，不复述阈值实现。
 for(let step=0;step<=100;step++){
  const value=step/100,option=rt.prepare('heatmap',{rows:['A'],columns:['B'],values:[[value]],min:0,max:1},settings).pages[0].option;
  const c=echarts.init(null,null,{renderer:'svg',ssr:true,width:720,height:360});
  try{c.setOption(option);const bg=c.getModel().getSeriesByIndex(0).getData().getItemVisual(0,'style').fill,fg=option.series[0].data[0].label.color;
    assert.ok(rt.contrast(bg,fg)>=4.5,theme_id+' '+value+' 对比度不足');}finally{c.dispose();}
 }
 // 纵轴名字是横排、按中点对齐在网格左缘的，超过 7 个字就往画布外跑。
 // 作者只能把名字压短、把单位挪出坐标轴；这里断言超长名字改为折行而不是越界。
 const longName='纵轴名称甲乙丙丁',oneItem={items:[{label:'甲',x:1,y:2,size:9}]};
 assert.doesNotThrow(()=>render({recipe:'scatter',spec:{...oneItem,yLabel:longName},theme_id,width:720,height:360}),
  '八字纵轴名必须能出图：这一档过去报「标签超出画布」');
 assert.match(rt.prepare('scatter',{...oneItem,yLabel:longName},settings).pages[0].option.yAxis.name,/\n/,'超长轴名须折行');
 // 带单位的名字断在括号处，不把单位拆散。
 assert.equal(rt.prepare('scatter',{...oneItem,yLabel:'交付达成率',yUnit:'万元'},settings).pages[0].option.yAxis.name,'交付达成率\n（万元）');
 // 短名字维持原样：折行不能顺手改掉现有版面。
 const shortAxis=rt.prepare('scatter',{...oneItem,yLabel:'销量'},settings).pages[0].option;
 assert.equal(shortAxis.yAxis.name,'销量');assert.equal(shortAxis.grid.top,48,'短名字的顶部预留不能变');
}
console.log('PASS: 9配方×3主题、气泡面积/零值位置标记、画布不足只报问题不退表、Sankey闭合/环/零流量拒绝、303个实际热力色阶反差');
