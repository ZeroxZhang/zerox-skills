/* 实际坐标断言：换尺寸/改文字/反馈/角色；包含故意移位反例。 */
'use strict';
const assert=require('node:assert/strict');
const {layout,render}=require('./render_diagram.cjs');
const {anchor,crosses,nodeHeight}=require('./diagram_layout.cjs');
const type=require('../assets/deck-typography.js').get();
const measure=require('./font_metrics.cjs').measurer(type.id);
function check(result){
  const map=new Map(result.nodes.map(n=>[n.id,n]));
  for(const n of result.nodes){assert(n.x>=0&&n.y>=0&&n.x+n.w<=result.width+.01&&n.y+n.h<=result.height+.01);assert(n.h>=nodeHeight(n,n.w,type,measure));}
  for(const [i,a] of result.nodes.entries())for(const b of result.nodes.slice(i+1))assert(!(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y),'节点不得重叠');
  for(const e of result.edges){
    const points=e.resolvedPoints;
    assert.deepEqual(points[0],anchor(map.get(e.from),e.fromSide),'起点必须绑定当前节点');
    assert.deepEqual(points.at(-1),anchor(map.get(e.to),e.toSide),'终点必须绑定当前节点');
    points.forEach(p=>assert(p[0]>=0&&p[1]>=0&&p[0]<=result.width&&p[1]<=result.height));
    for(let i=1;i<points.length;i++)for(const n of result.nodes)assert(!crosses(points[i-1],points[i],n),'边不可穿过节点 '+n.id);
  }
  for(const box of result.layout_result.label_boxes)for(const n of result.nodes)assert(!(box.x<n.x+n.w&&box.x+box.w>n.x&&box.y<n.y+n.h&&box.y+box.h>n.y),'边标签不可覆盖节点');
  assert.match(render(result),/data-node=/);
}
const base={width:1080,height:540,layout:{stages:['识别','决策','执行'],lanes:['客户','团队'],headers:true},nodes:[
  {id:'need',title:'客户提出需求',body:'保留原文与业务约束',lane:'客户',stage:'识别'},
  {id:'review',title:'交付条件核验',body:'依据已核验材料确定边界',lane:'团队',stage:'决策'},
  {id:'approve',title:'确认范围',lane:'客户',stage:'决策'},
  {id:'deliver',title:'实施与验证',body:'HTML + PDF 同版验收',lane:'团队',stage:'执行'}
],edges:[{from:'need',to:'review',label:'提交'},{from:'review',to:'approve',label:'核验'},{from:'approve',to:'deliver',label:'授权'},{from:'deliver',to:'review',label:'返工',role:'feedback',dashed:true}]};
let count=0;
for(const size of [[1080,540],[760,720],[600,900],[1440,700]]){const result=layout({...base,width:size[0],height:size[1]});check(result);count++;}
const grown=layout({...base,width:540,height:220});assert(grown.layout_result.resized);check(grown);count++;
const shifted=structuredClone(layout(base));shifted.nodes.find(n=>n.id==='deliver').x+=4;assert.throws(()=>check(shifted),/终点|起点/);count++;
const long=structuredClone(base);long.nodes[1].title='跨团队客户交付责任与必要条件核验';long.nodes[1].body='Revenue 12.75 与中文混排\n字重与多行换行使用实际交付字体';check(layout(long));count++;
const sameCell=structuredClone(base);sameCell.nodes.push({id:'parallel',title:'并行验证',lane:'团队',stage:'决策'});sameCell.edges.push({from:'need',to:'parallel'});check(layout(sameCell));count++;
const topology={width:1050,height:600,layout:{headers:false},nodes:[{id:'a',title:'开始'},{id:'b',title:'满足条件？',role:'decision'},{id:'c',title:'完成',role:'outcome'}],edges:[{from:'a',to:'b'},{from:'b',to:'c',label:'是'},{from:'b',to:'a',label:'补充',role:'feedback'}]};check(layout(topology));count++;
assert.equal(layout(topology).nodes.find(n=>n.id==='b').shape,'diamond');
assert.throws(()=>layout({...base,width:300,height:120,layout:{...base.layout,fit:'error'}}),/超过/);
assert.throws(()=>layout({...topology,edges:[{from:'a',to:'b'},{from:'b',to:'a'}]}),/循环依赖/);
assert.throws(()=>layout({...base,nodes:[...base.nodes,base.nodes[0]]}),/唯一/);
assert.throws(()=>layout({...base,edges:[{from:'need',to:'missing'}]}),/不存在/);
assert.throws(()=>layout({...base,layout:{...base.layout,stages:['错误阶段']}}),/未知/);
assert.deepEqual(layout(base),layout(base),'相同输入布局应可复现');
console.log(`PASS: ${count} 个真实布局/反例；4种尺寸、内容变长、同格多节点、反馈、条件角色、端点绑定与节点避让；5类无效输入。`);
