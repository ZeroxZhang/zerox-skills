const frame=require('./apply_frame.cjs');
/* 合成大表/长文本的端到端示例；显式编码和选型，不冒充通用自动分析器。 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {render}=require('./render_echarts_svg.cjs'),themes=require('../assets/deck-themes.js');
const root=path.resolve(__dirname,'..'),fixture=path.join(root,'assets/dense-input-example');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>n.toLocaleString('zh-CN',{maximumFractionDigits:2}),sum=rows=>rows.reduce((s,r)=>s+r.revenue,0);
function analyze(inputDir=fixture){
 const raw=fs.readFileSync(path.join(inputDir,'operations.csv'),'utf8'),notes=fs.readFileSync(path.join(inputDir,'field-notes.md'),'utf8'),coding=JSON.parse(fs.readFileSync(path.join(inputDir,'text-coding.json'),'utf8'));
 // 本夹具为无引号逗号表；真实CSV/Excel需先用合适解析器归一化，不能套用此简化读取器。
 if(raw.includes('"'))throw Error('示例CSV不支持带引号字段，请先归一化');
 const [head,...lines]=raw.trim().split(/\r?\n/),fields=head.split(','),keys=new Set();
 if(head!=='record_id,region,period,product,revenue,unit,scope,status')throw Error('字段契约不符');
 const rows=lines.map((line,i)=>{
  const cells=line.split(',');if(cells.length!==fields.length)throw Error('列数不符：'+(i+2));
  const r=Object.fromEntries(fields.map((k,j)=>[k,cells[j]]));
  if(!r.record_id||keys.has(r.record_id))throw Error('重复或空记录ID');keys.add(r.record_id);
  if(r.unit!=='万元'||r.scope!=='合并经营收入'||r.status!=='synthetic')throw Error('单位/范围/合成状态不符');
  if(!/^202[45]-(0[1-9]|1[0-2])$/.test(r.period)||!/^区域(0[1-9]|1\d|2[0-4])$/.test(r.region)||!['核心业务','试点业务'].includes(r.product))throw Error('维度不符');
  if(!r.revenue.trim()||!Number.isFinite(Number(r.revenue))||Number(r.revenue)<0)throw Error('无效收入');
  return {...r,revenue:Number(r.revenue),line:i+2};
 });
 const dimensions=new Set(rows.map(r=>[r.region,r.period,r.product].join('|')));
 if(rows.length!==1152||dimensions.size!==1152)throw Error('24地区×24月×2业务应有1152条唯一明细');
 const paragraphs=Object.fromEntries([...notes.matchAll(/^## (T\d{2}\.p\d+)\n\n([\s\S]*?)(?=\n## |$)/gm)].map(m=>[m[1],m[2].trim()]));
 if(Object.keys(paragraphs).length!==42||coding.status!=='synthetic'||coding.cases.length!==6)throw Error('文本夹具范围不符');
 const evidence=rows.map(r=>({id:'E-'+r.record_id,claim:r.region+' '+r.period+' '+r.product+'收入',value:r.revenue,unit:r.unit,period:r.period,scope:r.scope,denominator:null,status:'synthetic',retrieved:null,source:{title:'operations.csv',url:null,locator:'行'+r.line,record_id:r.record_id},formula:null,limitations:'合成数据，非真实业务事实'}));
 function aggregate(id,selected,claim){const value=sum(selected);evidence.push({id,claim,value,unit:'万元',period:[...new Set(selected.map(r=>r.period))],scope:'合并经营收入',denominator:null,status:'derived',synthetic:true,retrieved:null,source:{title:'operations.csv',url:null,locator:'input_ids逐条定位'},input_ids:selected.map(r=>'E-'+r.record_id),formula:'SUM(input_ids.value)',limitations:'仅合成数据同口径加总'});return {id,value};}
 const totals=[2024,2025].map(y=>aggregate('D-Y'+y,rows.filter(r=>r.period.startsWith(y)),y+'年总收入'));
 const monthly=[2024,2025].map(y=>Array.from({length:12},(_,i)=>{const period=y+'-'+String(i+1).padStart(2,'0');return aggregate('D-M'+period,rows.filter(r=>r.period===period),period+'总收入');}));
 const regions=Array.from({length:24},(_,i)=>{const label='区域'+String(i+1).padStart(2,'0');return {label,...aggregate('D-'+label,rows.filter(r=>r.region===label&&r.period.startsWith('2025')),label+'2025年收入')};});
 const composition=Array.from({length:12},(_,i)=>{const period='2025-'+String(i+1).padStart(2,'0');return {label:period,segments:['核心业务','试点业务'].map((label,j)=>({label,...aggregate('D-C'+i+'-'+j,rows.filter(r=>r.region==='区域24'&&r.period===period&&r.product===label),'区域24 '+period+' '+label)}))};});
 evidence.push({id:'D-GROWTH',claim:'2025年相对2024年收入增长率',value:(totals[1].value/totals[0].value-1)*100,unit:'%',period:'2025 vs 2024',scope:'合并经营收入',denominator:totals[0].value,status:'derived',synthetic:true,retrieved:null,source:{title:'operations.csv',url:null,locator:'D-Y2024、D-Y2025'},input_ids:totals.map(d=>d.id),formula:'(D-Y2025 / D-Y2024 - 1) * 100',limitations:'收入增长不代表利润或因果关系'});
 const caseIds=new Set();for(const c of coding.cases){
  if(caseIds.has(c.id))throw Error('重复案例ID');caseIds.add(c.id);
  for(const kind of ['support','boundary']){const item=c[kind];if(paragraphs[item.locator]!==item.quote||!item.locator.startsWith(c.id+'.'))throw Error('引文与原文定位不一致：'+item.locator);
   // 段落是页面上的上下文，不把整段作为一个事实；每个可定位句子独立入库。
   item.evidence_ids=[];let offset=0;
   for(const [i,sentence] of [...item.quote.matchAll(/[^。！？]+[。！？]?/g)].map(m=>m[0]).entries()){
    const id='E-'+item.locator+'.s'+(i+1);item.evidence_ids.push(id);
    evidence.push({id,claim:sentence,value:null,unit:null,period:null,scope:c.name,denominator:null,status:'synthetic',retrieved:null,source:{title:'field-notes.md',url:null,locator:item.locator,sentence:i+1,char_start:offset,char_end:offset+sentence.length},formula:null,limitations:kind==='boundary'?'反证/适用边界':'记录中的动作或陈述，不证明经营效果'});offset+=sentence.length;
   }
  }
  if(c.action_status!=='建议')throw Error('建议必须与原文事实区分');
 }
 const inventory=[{file:'operations.csv',sha256:crypto.createHash('sha256').update(raw).digest('hex'),rows:rows.length,columns:fields.length,fields,primary_key:'record_id',grain:'地区×月×业务',unit:'万元',scope:'合并经营收入',range:'2024-01—2025-12',missing:0,duplicates:0,zero_values:rows.filter(r=>r.revenue===0).length,status:'synthetic-validated',input_shapes:['I-01','I-02','I-04']},{file:'field-notes.md',sha256:crypto.createHash('sha256').update(notes).digest('hex'),characters:notes.length,paragraphs:Object.keys(paragraphs).length,case_count:6,locators:Object.keys(paragraphs),coded_locators:coding.cases.flatMap(c=>[c.support.locator,c.boundary.locator]),omission_rule:'其余30段为背景、口径和方法说明；保留原文，不转为统计值',method:coding.method,status:'synthetic-manually-coded',input_shapes:['I-14']}];
 return {rows,evidence,inventory,coding,totals,monthly,regions,composition};
}
function build(out,themeId='mckinsey',inputDir=fixture,profile='serif-report-bold'){
 const data=analyze(inputDir),slides=[],plans=[];
 const common={mode:'reading',comparability:'同单位万元、同合并范围；同比只比较相同月份/完整年度',label_plan:'静态显示；原值与零值不省略',fit_plan:'画布不足时分面、提高模块高度或换实现；不缩字号，也不把图改成表格'};
 function page(title,lead,body,decision,source,modules){
  const n=slides.length+1;plans.push({page:n,claim:title,proof_obligation:lead,mode:'reading',evidence_ids:[...new Set(modules.flatMap(m=>m.evidence_ids))],modules,reading_order:modules.map(m=>m.id),limits:'全部为合成材料；选型和文本编码由作者明确指定，非自动语义判断'});
  slides.push(`<section class="slide reading dense${n===1?' active':''}">${frame.markup}<div class="slide__tracker">高密度输入验收 · ${n<=3?'经营数据':'文本证据'}</div><div class="slide__sticker">合成材料 · 非真实业务结论</div><header class="slide__header"><h1 class="slide__title">${esc(title)}</h1><div class="slide__lead">${esc(lead)}</div></header><div class="slide__body">${body}<div class="decision-strip">${esc(decision)}</div></div><div class="source">${esc(source)}</div><div class="slide__page">${n}</div></section>`);
 }
 function exhibit(id,recipe,spec,width,height,meta){
  const rendered=render({recipe,spec,width,height,theme_id:themeId,typography_id:profile});
  return {rendered,module:{...common,id,...meta,recipe,render_route:'echarts-recipe',selected_visual:recipe,risks:rendered.risks,encoding:meta.encoding||'按配方编码，保留完整原值',density_plan:{width,height,min_font_px:14,output_pages:1},spec}};
 }
 const trend=exhibit('M1','timeSeries',{periods:Array.from({length:12},(_,i)=>(i+1)+'月'),unit:'万元',zeroBaseline:true,series:data.monthly.map((values,i)=>({name:String(2024+i),values:values.map(d=>d.value)}))},760,365,{input_shape:'I-02',reader_operation:'A-04',question:'同月比较是否也支持全年增长',evidence_ids:data.monthly.flat().map(d=>d.id),candidates:[{visual:'折线',decision:'保留：连续月份与两年同月比较'},{visual:'全年柱形',decision:'淘汰：不能单独揭示月度形态'}]});
 if(trend.rendered.pages.length!==1)throw Error('趋势模块需重新分页');
 const growth=data.evidence.find(e=>e.id==='D-GROWTH').value;
 const summary=`<div><h2>全年规模与比较边界</h2><table class="data-table"><thead><tr><th>指标</th><th>数值</th></tr></thead><tbody>${data.totals.map((d,i)=>`<tr><td>${2024+i}年收入</td><td class="num">${fmt(d.value)} 万元</td></tr>`).join('')}<tr><td>同比增长</td><td class="num">${fmt(growth)}%</td></tr></tbody></table><p class="dense-note">口径：24地区 × 12个月 × 2业务。年度与月度合计来自同一批明细。</p><p class="dense-note">当前数据没有利润、成本和客户指标；不能据收入增长推断盈利改善或管理举措有效。</p></div>`;
 page('全年收入增长'+fmt(growth)+'%，仍需区分规模与经营效果','1,152条明细先核对主键、单位与覆盖范围，再聚合为月度比较和年度总量。',`<div class="dense-pair"><div><h2>两年同月比较 · 收入，万元</h2>${trend.rendered.pages[0].svg}</div>${summary}</div>`,'后续诊断应补利润、客户和成本；这份收入表足以比较规模，不足以解释原因。','来源：operations.csv 全部1,152条合成明细；D-M*、D-Y2024、D-Y2025、D-GROWTH；公式见 evidence.json。',[trend.module,{...common,id:'M2',input_shape:'I-01',reader_operation:'A-03',question:'全年规模如何变化',evidence_ids:[...data.totals.map(d=>d.id),'D-GROWTH'],render_route:'html-css',recipe:null,selected_visual:'年度比较表',density_plan:{rows:3,columns:2,width:416,min_font_px:16}}]);
 // 24项单图在588×460内实测文字相互遮挡；按同一量尺拆成两个12项分面，仍保留全体排序。
 const sorted=[...data.regions].sort((a,b)=>b.value-a.value),sharedScale={unit:'万元',min:0,max:sorted[0].value};
 const rankParts=[sorted.slice(0,12),sorted.slice(12)].map((part,i)=>exhibit('M'+(i+1),'rankedBar',{...sharedScale,items:part.map(d=>({label:d.label,value:d.value}))},588,460,{input_shape:'I-01',reader_operation:'A-02',question:(i?'后12个地区':'前12个地区')+'收入排序',evidence_ids:part.map(d=>d.id),candidates:[{visual:'12项条形×2分面',decision:'保留：同一量尺并排显示全部24地区，标签可读'},{visual:'24项单图',decision:'淘汰：588×460内实测标签互相遮挡'},{visual:'Top 10',decision:'淘汰：本页要求查全体，不能省掉尾部地区'}]}));
 page(sorted[0].label+'收入最高；24地区分两栏保留完整排序','从2025年576条月度业务记录聚合为24个地区；不只取Top 10，也不靠缩字塞入条形。',`<div class="dense-equal">${rankParts.map(p=>`<div>${p.rendered.pages[0].svg}</div>`).join('')}</div>`,'先左后右读取全部排名；两栏共用同一数值量尺；排名仅描述收入规模，不表示盈利或投资优先级。','来源：operations.csv，2025年；D-区域01…D-区域24。展示值与排序均由聚合原值派生。',rankParts.map(p=>p.module));
 // 试点业务逐月为0或1万元，占比0–0.4%；读者要逐月查数并确认零值，属于查数任务，主动选用明细表而不是图。
 const months=data.composition,sum=s=>months.reduce((n,m)=>n+m.segments[s].value,0);
 const shareFmt=v=>Number(v.toFixed(1)).toLocaleString('zh-CN',{maximumFractionDigits:1})+'%';
 const share=(m,s)=>m.segments[s].value/(m.segments[0].value+m.segments[1].value)*100;
 const comp=`<table class="data-table"><caption>区域24 · 2025年逐月构成，万元；份额=该业务/当月两业务合计</caption><thead><tr><th>项目</th>${months.map(m=>`<th class="num">${m.label.slice(5)}月</th>`).join('')}<th class="num">全年</th></tr></thead><tbody>
<tr><td class="row-label">核心业务</td>${months.map(m=>`<td class="num" data-composition-month="${m.label}">${fmt(m.segments[0].value)}</td>`).join('')}<td class="num">${fmt(sum(0))}</td></tr>
<tr><td class="row-label">试点业务</td>${months.map(m=>`<td class="num" data-composition-month="${m.label}"${m.segments[1].value===0?' data-zero="true"':''}>${fmt(m.segments[1].value)}</td>`).join('')}<td class="num">${fmt(sum(1))}</td></tr>
<tr><td class="row-label">试点月内份额</td>${months.map(m=>`<td class="num"${m.segments[1].value===0?' data-zero="true"':''}>${shareFmt(share(m,1))}</td>`).join('')}<td class="num">—</td></tr>
<tr><td class="row-label">月内合计</td>${months.map(m=>`<td class="num">${fmt(m.segments[0].value+m.segments[1].value)}</td>`).join('')}<td class="num">${fmt(sum(0)+sum(1))}</td></tr>
</tbody></table>`;
 const compModule={...common,id:'M1',input_shape:'I-04',reader_operation:'A-05',question:'小额试点收入和零值是否完整可查',evidence_ids:months.flatMap(m=>m.segments.map(s=>s.id)),comparability:'同一区域、同一口径的逐月明细；份额分母为当月两业务合计',candidates:[{visual:'100%堆积',decision:'淘汰：试点占比0–0.4%，12个月的小片与零值在静态图里无法逐个可读，且本页是逐月查数'},{visual:'原值／份额明细表',decision:'保留：零值与1万元小项逐月可查，合计由原值相加得到'}],render_route:'html-css',recipe:null,selected_visual:'月度构成明细表',encoding:'数值即原值；份额由当月合计派生，零值显式标出',label_plan:'月份为列、项目为行；缺失与零分开',density_plan:{rows:4,columns:14,width:1200,min_font_px:14}};
 page('试点收入逐月仅0或1万元，明细表保留小项与零值','区域24的2025年逐月构成；零值与1万元小项逐月可查，合计由原值相加得到。',comp,'零值不画假面积，也不并入其他；表格在这里是读者查数任务的主动选择。','来源：operations.csv，区域24、2025年，共24条明细；D-C*。份额=该业务收入/该月两业务收入合计。',[compModule]);
 const claims=['补货记录证明协作方式变化，尚未证明履约改善','回款材料支持动作完成，尚不足以归因到账效果','准入准备仍有多重约束，不能据记录推算延误贡献'];
 for(let group=0;group<3;group++){
  const cases=data.coding.cases.slice(group*2,group*2+2);
  const table=`<table class="data-table text-evidence"><colgroup><col style="width:14%"><col style="width:32%"><col style="width:28%"><col style="width:26%"></colgroup><thead><tr><th>案例 / 主题</th><th>记录支持什么 · 原文</th><th>边界 / 替代解释 · 原文</th><th>下一步验证 · 作者建议</th></tr></thead><tbody>${cases.map(c=>`<tr data-case="${c.id}"><td class="row-label">${esc(c.name)}<span class="locator">${c.id} · ${esc(c.topic)}</span></td><td>${esc(c.support.quote)}<span class="locator">[${c.support.locator}]</span></td><td>${esc(c.boundary.quote)}<span class="locator">[${c.boundary.locator}]</span></td><td>${esc(c.action)}<span class="locator">建议，非已发生事实</span></td></tr>`).join('')}</tbody></table>`;
  page(claims[group],'按案例 × 支持证据 × 边界 × 验证动作对齐；保留原文定位，不从目的性案例计算发生率。',table,'原始记录与作者建议分列；每条机制解释都需继续核对基线、时间顺序与替代解释。','来源：field-notes.md，'+cases.map(c=>c.id+'.p2–p3').join('；')+'；人工编码见 text-coding.json；全部为合成材料。',[{id:'M1',input_shape:'I-14',reader_operation:'A-15',question:'案例说明了哪些动作、哪些效果尚未证明',evidence_ids:cases.flatMap(c=>[...c.support.evidence_ids,...c.boundary.evidence_ids]),comparability:'仅按共同论证维度比较；样本目的性选择，不估算总体频次',candidates:[{visual:'案例—边界矩阵',decision:'保留：逐条对齐支持、限制与下一步'},{visual:'主题占比图或因果链',decision:'淘汰：没有总体分母或可识别的因果证据'}],render_route:'html-css',recipe:null,selected_visual:'案例—边界矩阵',encoding:'等宽列不表示量值；支持与边界均为完整段落原引文，行动明确标建议',label_plan:'自动换行、保留段落ID；不删边界迁就版面',density_plan:{rows:2,columns:4,width:1200,min_font_px:16},fit_plan:'任一行超出正文高度时按案例拆页，禁止缩字',case_ids:cases.map(c=>c.id)}]);
 }
 const ids=new Set(data.evidence.map(e=>e.id));for(const e of data.evidence)for(const id of e.input_ids||[])if(!ids.has(id))throw Error('派生指标缺输入：'+id);
 for(const p of plans)for(const id of p.evidence_ids)if(!ids.has(id))throw Error('页面缺证据：'+id);
 let html=fs.readFileSync(path.join(root,'assets/deck_engine.html'),'utf8');html=html.slice(html.indexOf('<!DOCTYPE html>'));
 const start=html.indexOf('<section class="slide'),end=html.indexOf('</div></div><!-- /stage /viewport -->');if(start<0||end<start)throw Error('引擎边界缺失');
 html=html.slice(0,start)+slides.join('\n')+html.slice(end);
 const css=fs.readFileSync(path.join(root,'assets/consulting-layouts.css'),'utf8')+`\n.slide.dense{--frame-rule-offset:-6px}.dense .slide__body{grid-template-rows:minmax(0,1fr) auto;gap:8px;margin-top:12px}.dense-pair{display:grid;grid-template-columns:760px 416px;gap:24px}.dense-equal{display:grid;grid-template-columns:588px 588px;gap:24px}.dense h2{font-size:18px;color:var(--brand);margin:0 0 8px}.dense svg{display:block;flex:none;max-width:none}.dense-note{font-size:16px;line-height:1.55;margin:14px 0}.dense .decision-strip{background:transparent;color:var(--ink);border:0;padding:0;font-size:16px}.dense .text-evidence{align-self:start;font-size:16px;line-height:1.5}.dense .text-evidence td{padding:18px 12px}.dense .text-evidence th{padding:10px 12px}.locator{display:block;margin-top:8px;font-size:12px;font-weight:400;color:var(--gray-2)}.dense .slide__sticker{font-size:12px}.dense .source{font-size:12px}`;
 html=html.replace('</style>',()=>css+'\n</style>').replace('<title>Deck Title</title>','<title>高密度输入 · 六页端到端验收</title>');
 html=html.replace(/<script src="[^"]+"><\/script>/g,'').replace(/<script type="module">[\s\S]*?<\/script>/g,'').replace("if(!window.echarts){ document.body.classList.add('no-charts'); return; }","if(!window.echarts){ if(document.querySelector('.chart')) document.body.classList.add('no-charts'); return; }");
 html=require('./pack_fonts.cjs').pack(frame.apply(themes.apply(html,themeId)),{profile});fs.mkdirSync(out,{recursive:true});
 const write=(file,value)=>fs.writeFileSync(path.join(out,file),typeof value==='string'?value:JSON.stringify(value,null,2));
 write('dense_reference_deck.html',html);write('source_inventory.json',data.inventory);write('evidence.json',data.evidence);write('page_plan.json',plans);
 write('run_manifest.json',{theme_id:themeId,selection_basis:'三主题验证；最终默认mckinsey',typography_id:profile,typography_version:require('../assets/deck-typography.js').version,typography_selection_basis:'构建参数；缺省研究报告方案',font_delivery:'embedded-subset',status:'synthetic',pages:slides.length,input_rows:data.rows.length,evidence_count:data.evidence.length,case_count:data.coding.cases.length,echarts:require('../package.json').dependencies.echarts,recipes:require('../assets/echarts-recipes.js').version,runtime:require('../assets/chart-runtime.js').version,limits:['该脚本验证固定示例输入，不提供通用CSV/Excel/PDF抽取','文本编码和视觉选型由作者指定，不冒称自动语义理解','渲染与来源定位可验证，但现实事实和因果仍需研究核验']});
 return {out,pages:slides.length,plans,data,html};
}
if(require.main===module){try{const [out,...args]=process.argv.slice(2);if(!out)throw Error('用法: node scripts/build_dense_reference.cjs output-dir [--theme=mckinsey|bcg|accenture] [--typography=serif-report-bold]');const id=(args.find(x=>x.startsWith('--theme='))||'--theme=mckinsey').slice(8),profile=(args.find(x=>x.startsWith('--typography='))||'--typography=serif-report-bold').slice(13);const result=build(path.resolve(out),id,fixture,profile);console.log(JSON.stringify({pages:result.pages,output:result.out,rows:result.data.rows.length,typography_id:profile}));}catch(e){console.error(e);process.exitCode=1;}}
module.exports={analyze,build};
