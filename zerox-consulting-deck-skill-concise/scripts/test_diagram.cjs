/* 开放图示运行边界：多形状、分组、折线、字体与无固定节点配额。 */
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {execFileSync}=require('node:child_process');
const {render}=require('./render_diagram.cjs');
const spec={id:'flow',width:1000,height:500,title:'交付 & 反馈 <关系>',groups:[{x:10,y:10,w:980,h:480,title:'跨职能协作',radius:10}],nodes:[
 {id:'a',x:40,y:80,w:200,h:100,shape:'round',title:'需求',body:'输入与证据'},
 {id:'b',x:350,y:60,w:240,h:150,shape:'diamond',title:'判断'},
 {id:'c',x:730,y:80,w:220,h:100,shape:'ellipse',title:'结果'},
 {id:'d',x:370,y:330,w:200,h:100,shape:'text',title:'反馈',body:'改变判断的证据'}
],edges:[{from:'a',to:'b',label:'提出'},{from:'b',to:'c',label:'支持'},{from:'c',to:'d',fromSide:'bottom',toSide:'right',points:[[840,380]],dashed:true},{from:'d',to:'b',fromSide:'top',toSide:'bottom'}],annotations:[{text:'连线表示工作关系，并非定量因果',x:40,y:470}]};
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-diagram-test-'));
try{
 for(const theme of ['mckinsey','bcg','accenture'])for(const typography of ['serif-report','serif-playfair','sans-presentation']){
  const svg=render({...spec,theme_id:theme,typography_id:typography});
  assert.match(svg,/交付 &amp; 反馈 &lt;关系&gt;/);assert.equal((svg.match(/data-node=/g)||[]).length,4);assert.equal((svg.match(/<polyline /g)||[]).length,4);
  const file=path.join(dir,'diagram.svg');fs.writeFileSync(file,svg);
  execFileSync(process.env.FONT_PYTHON||'python3',['-c','import sys,xml.etree.ElementTree as E; E.parse(sys.argv[1])',file]);
 }
 const many={width:1400,height:1100,nodes:Array.from({length:60},(_,i)=>({id:'n'+i,x:20+i%10*138,y:30+Math.floor(i/10)*175,w:120,h:110,title:'节点'+i}))};
 assert.equal((render(many).match(/data-node=/g)||[]).length,60);
 const invalid=[
  [{...spec,nodes:[...spec.nodes,spec.nodes[0]]},/唯一/],
  [{...spec,edges:[{from:'missing',to:'a'}]},/不存在/],
  [{...spec,nodes:[{...spec.nodes[0],x:990}]},/超出/],
  [{...spec,edges:[],nodes:[{...spec.nodes[0],w:30,h:30,body:'不能通过截断丢弃这段文字'}]},/字宽|装不下/],
  [{...spec,edges:[{from:'a',to:'b',points:[[Infinity,100]]}]},/有限/],
  [{...spec,annotations:[{text:'bad',x:10,y:40,anchor:'bad'}]},/锚点/],
  [{...spec,groups:[{...spec.groups[0],radius:'x'}]},/有限/],
  [{...spec,typography_id:'legacy-system'},/已注册字体/]
 ];
 for(const [input,pattern] of invalid)assert.throws(()=>render(input),pattern);
 assert.notEqual(render({...spec,id:undefined}).match(/data-diagram="([^"]+)/)[1],render({...spec,id:undefined,title:'另图'}).match(/data-diagram="([^"]+)/)[1]);
 console.log('PASS: 3主题×3字体、多形状/分组/折线、XML与字形测量、60节点、8类无效输入；不代表自动布局或语义正确。');
}finally{fs.rmSync(dir,{recursive:true,force:true});}
