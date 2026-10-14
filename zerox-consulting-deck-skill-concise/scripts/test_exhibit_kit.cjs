/* 验证数学编码、不变式、转义和输入边界；不依赖浏览器。 */
const assert = require('node:assert/strict');
const kit = require('../assets/exhibit-kit.js');
const wf=kit.waterfall({items:[{type:'total',label:'期初',value:10},{type:'delta',label:'下降',value:-15},{type:'delta',label:'回升',value:8},{type:'subtotal',label:'期末'}]});
assert.match(wf,/data-from="10" data-to="-5"/);assert.match(wf,/data-from="-5" data-to="3"/);assert.match(wf,/data-from="0" data-to="3"/);assert.doesNotMatch(wf,/NaN|Infinity/);
const mk=kit.mekko({items:[{label:'甲',segments:[{label:'一',value:10},{label:'二',value:30}]},{label:'乙',segments:[{label:'一',value:60},{label:'二',value:20}]}]});
const rects=[...mk.matchAll(/<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"[^>]+data-value="([^"]+)"/g)];assert.equal(rects.length,4);const ratios=rects.map(m=>+m[3]*+m[4]/+m[5]);ratios.forEach(r=>assert.ok(Math.abs(r-ratios[0])<1e-6));
assert.match(kit.dumbbell({items:[{label:'<script>&"',start:-2,end:4}]}),/&lt;script&gt;&amp;&quot;/);
for(const [fn,spec] of Object.entries({slope:{items:[{label:'A',start:-1,end:2}]},bullet:{items:[{label:'A',value:30,target:50,max:100}]},heatmap:{rows:['A'],columns:['B'],values:[[-3]]},tree:{root:{label:'A',children:[{label:'B'},{label:'C'}]}},swimlane:{lanes:['A'],stages:['B','C'],items:[{id:'a',label:'任务',lane:0,stage:0},{id:'b',label:'交付',lane:0,stage:1}],edges:[{from:'a',to:'b'}]}})){const svg=kit[fn](spec);assert.ok(svg.startsWith('<svg'));assert.doesNotMatch(svg,/NaN|Infinity|undefined/);}
assert.throws(()=>kit.waterfall({items:[{type:'total',value:NaN}]}));assert.throws(()=>kit.waterfall({items:[{type:'total',value:3},{type:'subtotal',value:5}]}));assert.throws(()=>kit.waterfall({domain:[0,1],items:[{type:'total',value:2}]}));
assert.throws(()=>kit.mekko({items:[{segments:[{value:-1}]}]}));assert.throws(()=>kit.heatmap({rows:['a'],columns:['b'],values:[[1,2]]}));assert.throws(()=>kit.bullet({items:[{value:10,target:5,max:8}]}));assert.throws(()=>kit.dumbbell({fontSize:10,items:[{label:'a',start:0,end:1}]}));
const cycle={label:'a'};cycle.children=[cycle];assert.throws(()=>kit.tree({root:cycle}));assert.throws(()=>kit.swimlane({lanes:['a'],stages:['b'],items:[{id:'x',lane:1,stage:0}]}));
const db=kit.dumbbell({width:960,domain:[-10,10],items:[{label:'a',start:-10,end:10}]});assert.match(db,/<circle cx="190"[^>]+data-role="start"/);assert.match(db,/<circle cx="875"[^>]+data-role="end"/);
const bl=kit.bullet({width:960,items:[{label:'a',value:50,target:75,max:100}]});assert.match(bl,/<rect x="190"[^>]+width="340"[^>]+data-value="50"/);assert.match(bl,/<line x1="700"[^>]+data-role="target"/);
const sl=kit.slope({height:500,domain:[0,100],items:[{label:'a',start:0,end:100}]});assert.match(sl,/<line x1="180" y1="435" x2="780" y2="60"/);
assert.throws(()=>kit.swimlane({lanes:['a'],stages:['b'],items:[{id:'x',lane:0,stage:0},{id:'y',lane:0,stage:0}]}));
assert.throws(()=>kit.waterfall({items:[{type:'total',value:10},{type:'delta',value:-4},{type:'total',value:9}]}),/总计/);
assert.doesNotThrow(()=>kit.waterfall({items:[{label:'起点',type:'total',value:10},{label:'变化',type:'delta',value:-14},{label:'期末',type:'total',value:-4}]}));
const singleBand=kit.bullet({items:[{label:'a',value:30,target:50,max:100}]});
assert.equal([...singleBand.matchAll(/height="30"/g)].length,1);
const threeBands=kit.bullet({items:[{label:'a',value:30,target:50,max:100,ranges:[50,80,100]}]});
assert.equal([...threeBands.matchAll(/height="30"/g)].length,3);
function lum(rgb){return rgb.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);}
function channels(hex){return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));}
for(const accent of ['#176B91','#AED6EE','#FFE000','#111111']){
 const svg=kit.heatmap({rows:['a'],columns:['a','b','c','d','e'],values:[[1,2,3,4,5]],domain:[0,5],palette:{accent}});
 // 单元格矩形允许夹带锚点属性（data-anchor-*）；对比度不变式不受属性顺序影响。
 const cells=[...svg.matchAll(/fill="(#[0-9A-Fa-f]+)"[^>]*? fill-opacity="([^"]+)" data-value="[^"]+"\/><text[^>]+fill="(#[0-9A-Fa-f]+)"/g)];
 assert.equal(cells.length,5);
 cells.forEach(m=>{const alpha=+m[2],bg=lum(channels(m[1]).map(v=>alpha*v+(1-alpha)*255)),fg=lum(channels(m[3]));assert.ok((Math.max(bg,fg)+.05)/(Math.min(bg,fg)+.05)>=4.5,'热力标签对比度不足');});
}
console.log('ExhibitKit core geometry, signed waterfall, area proportionality, escaping and invalid-input checks passed.');

assert.throws(()=>kit.tree({root:{children:[{label:'child'}]}}),/文字标签/);
assert.throws(()=>kit.dumbbell({items:[{start:1,end:2}]}),/文字标签/);

/* 泳道连线：箭头必须跟着方向翻。曾经不管目标在左还是在右，箭头一律朝右——
   线向左走、箭头朝右，把关系画反，而这类图读的就是方向。跨阶段的连线一并拒绝：
   它的水平段会从中间那些节点框上穿过去，画出来读不出关系。 */
{
 const pal=(require('../assets/deck-themes.js')).palette('mckinsey');
 const lane=(from,to)=>kit.swimlane({palette:pal,typography_id:'serif-report-bold',width:900,height:400,
  lanes:['甲','乙'],stages:['一','二','三'],
  items:[{id:'a',label:'起点',lane:0,stage:from},{id:'b',label:'终点',lane:1,stage:to}],edges:[{from:'a',to:'b'}]});
 const arrow=svg=>{const m=svg.match(/<path d="M ([\d.]+) [\d.]+ L ([\d.]+) [\d.]+ L [\d.]+ [\d.]+"/);return m?{base:+m[1],tip:+m[2]}:null;};
 const right=arrow(lane(0,1));
 assert.ok(right&&right.tip>right.base,'向右的连线，箭头必须朝右');
 const left=arrow(lane(2,1));
 assert.ok(left&&left.tip<left.base,'向左的连线，箭头必须朝左（原缺陷：箭头恒朝右）');
 assert.throws(()=>lane(2,0),/只支持相邻阶段/,'跨阶段连线必须当场拒绝，而不是画一条穿过节点框的线');
}
console.log('ExhibitKit swimlane edge direction and adjacent-stage limit passed.');

/* 哑铃的数值标签：行距紧时必须换摆法，不能把相邻两行的标签叠在同一列上。
   曾经固定放在点的上方(y−13)与下方(y+25)，两者共需 dy≥fs*2+28；`rows()` 的守卫只要求
   dy≥fs+12，于是在 1200×288、5 行（dy≈40）时静默画出互相压住的两行数字。
   同一条根因还会让标注层无处落位：585×330 下给每个端点挂标注会报"68 个候选全被拒"，
   作者只能放弃这个图型改自绘——那才是真正的代价。 */
{
 const pal=(require('../assets/deck-themes.js')).palette('mckinsey');
 // 刻意让相邻两行的点落在同一列（这一行的终点就是下一行的起点）：链式区间在真实材料里很常见，
 // 也正是标签会叠住的那种排布；用不共列的数据测这条等于没测。
 const rows=[{label:'甲',start:10,end:30},{label:'乙',start:30,end:45},{label:'丙',start:45,end:52},{label:'丁',start:52,end:70},{label:'戊',start:70,end:88}];
 const nums=svg=>[...svg.matchAll(/<text x="([\d.]+)" y="([\d.]+)" text-anchor="(?:middle|end|start)"[^>]*>([\d.,]+)<\/text>/g)].map(m=>({x:+m[1],y:+m[2],t:m[3]}));
 for(const h of [288,300,330,380,400]){
  const labels=nums(kit.dumbbell({palette:pal,typography_id:'serif-report-bold',width:1200,height:h,items:rows}));
  assert.equal(labels.length,rows.length*2,'高 '+h+'：每行的起始值与结束值都必须画出来，不能靠丢标签避让');
  for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++)
   assert.ok(!(Math.abs(labels[i].x-labels[j].x)<26&&Math.abs(labels[i].y-labels[j].y)<20),
     '高 '+h+'：'+labels[i].t+' 与 '+labels[j].t+' 同列且垂直间距不足，会叠在一起');
 }
 assert.doesNotThrow(()=>kit.dumbbell({palette:pal,typography_id:'serif-report-bold',width:585,height:330,items:rows,
  annotations:rows.map(d=>({on:'end:'+d.label,kind:'delta',from:'start:'+d.label,text:d.label+' {delta}'}))}),
  '紧行距下端点标注仍要摆得下：摆不下会让作者放弃这个图型');
}
// 子弹图的 target 锚点过去在行距紧时报「68 个候选全部被拒」，作者据此判定这个图型不能用、
// 改去自绘。两种行距分别断言：宽裕时要真的摆得下，不足时要说清是行距不够。
{
 const pal=(require('../assets/deck-themes.js')).palette('mckinsey');
 const names=['交付达成率%','留存率%','毛利率%','周转天数','客单价','复购率'];
 const items=n=>Array.from({length:n},(_,i)=>({label:names[i],value:40+i*6,target:60+i*5,max:100}));
 const ann=[{on:'target:交付达成率%',kind:'value',text:'目标 {value}'}];
 assert.doesNotThrow(()=>kit.bullet({palette:pal,typography_id:'serif-report-bold',width:880,height:200,items:items(3),annotations:ann,title:'t'}),
  '行距 36.7px 时 target 锚点标注要摆得下：这一档过去报「68 个候选全部被拒」');
 assert.throws(()=>kit.bullet({palette:pal,typography_id:'serif-report-bold',width:880,height:240,items:items(5),annotations:ann,title:'t'}),
  /行与行之间没有空隙放标注/, '行距等于色带高时必须说清是行距不够，不能只报一串候选');
 // 不挂标注时行带相接是正常画法，不能被容量守卫误伤。
 assert.doesNotThrow(()=>kit.bullet({palette:pal,typography_id:'serif-report-bold',width:880,height:240,items:items(5),title:'t'}),
  '无标注时同一构型必须照常出图');
 // 目标刻度线与声明框等长，锚点框必须与实画图元一致。
 const svg=kit.bullet({palette:pal,typography_id:'serif-report-bold',width:880,height:330,items:items(3),title:'t'});
 const tick=/<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"[^>]*data-role="target"/.exec(svg);
 assert.ok(tick,'目标刻度线必须画出来');
 assert.ok(Math.abs((+tick[4]-+tick[2])-30)<1e-6,'刻度线高度须等于色带高 30px，否则声明框与图元不一致');
}
console.log('ExhibitKit dumbbell label spacing across row heights passed.');
