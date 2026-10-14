const frame=require('./apply_frame.cjs');
/* 六页合成数据验证稿；复制既有引擎并内联SVG/HTML，保留导航与打印。 */
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),kit=require('../assets/exhibit-kit.js'),themes=require('../assets/deck-themes.js');
const baseline=require('../assets/analysis_baseline.json');
const typography=require('../assets/deck-typography.js'),{pack}=require('./pack_fonts.cjs');
const args=process.argv.slice(2),themeId=(args.find(v=>v.startsWith('--theme='))||'--theme=mckinsey').slice(8),palette=themes.palette(themeId);
const profile=(args.find(v=>v.startsWith('--typography='))||'--typography=serif-report-bold').slice(13);
const chart=(type,s)=>kit[type]({width:585,height:360,fontSize:16,palette,typography_id:profile,...s});
const ex=(title,unit,body,note)=>`<div class="exhibit"><h2>${title}</h2><div class="unit">${unit}</div><div class="graphic">${body}</div><div class="annotation">${note}</div></div>`;
const paired=(a,b)=>`<div class="layout-paired">${a}${b}</div>`;
const slides=[];
const pagesContract=[];
function page(title,lead,body,decision,form='html.text'){
 pagesContract.push({page:pagesContract.length+1,proves:title,form});
  const n=slides.length+1;slides.push(`<section class="slide reading analytical${n===1?' active':''}" data-form="${form}">${frame.markup}<div class="slide__tracker">分析表达升级 · ${String(n).padStart(2,'0')}</div><div class="slide__sticker">${n===5?'建议 · 非执行承诺':'示意数据 · 非真实结论'}</div><header class="slide__header"><h1 class="slide__title">${title}</h1><div class="slide__lead">${lead}</div></header><div class="slide__body">${body}<div class="decision-strip">${decision}</div></div><div class="source">来源：本技能合成数据与流程建议，仅用于验证表达方式；前后对照源于本项目v3组件，非think-cell官方样例。</div><div class="slide__page">${n}</div></section>`);
}
page('净减少0.8亿元，可直接从贡献桥读出','相同数据、同一尺寸：在贡献分解之外，把起止净变化和相对变化放在图内。',paired(
  ex('基础版本｜贡献柱已闭合','收入，亿元',baseline.svg[themeId].waterfall,'起止值11.2和10.4都可见，净差额与变化率需要读者自行换算。'),
  ex('升级版本｜直接标出关键比较','收入，亿元；括号比较期初与期末',chart('waterfall',{items:baseline.waterfall,format:{decimals:1},comparison:{from:0,to:4,decimals:1,suffix:'亿元',showRelative:true}}),'商超减少1.1亿元，电商增加0.4亿元；净变化由原始数据计算。')
),'只有当比较帮助解释本页判断时才添加标注；不把括号作为每张图的装饰。','kit.waterfall');
const periods=[{label:'2023年',segments:[{label:'核心',value:80},{label:'新业务',value:20}]},{label:'2024年',segments:[{label:'核心',value:96},{label:'新业务',value:24}]},{label:'2025年',segments:[{label:'核心',value:104},{label:'新业务',value:56}]}];
page('收入增长60%，新业务份额提高15个百分点','同一份数据的两个问题：总量用普通堆积，结构用100%堆积；2023至2025年跨两个年度间隔。',paired(
  ex('规模｜总量从100增至160','收入，亿元；柱高=总量，柱上数字=总量',chart('stacked',{height:375,items:periods,mode:'absolute',comparison:{from:0,to:2,mode:'cagr',periods:2,decimals:1}}),'累计增长60%；两年CAGR约26.5%，不能把3个观测年当作3个间隔。'),
  ex('构成｜新业务从20%升至35%','柱高=100%；柱上数字=收入总量（亿元）',chart('stacked',{height:375,items:periods,mode:'percent',labelContent:'share'}),'份额增加15个百分点；相对增幅为75%，两者不能混写。')
),'先确定读者要比较“多少”还是“占比”；不因图型复杂就默认使用Mekko。','kit.stacked');
page('窄列中的5个单位，仍应有完整可查的分项','Mekko的列宽与面积保持按值比例；标签放不下时改走同侧引线通道，不放大小片，也不改成表格。',paired(
  ex('基础版本｜小片标签被省略','销售额，任意单位；列宽=地区总量',baseline.svg[themeId].mekko,'南区总量为5，但图中没有呈现核心3、新业务2的分项。'),
  ex('升级版本｜引线标注绑回窄列','列宽=总量；引线栏=该列的原值与份额',chart('mekko',{height:385,items:baseline.mekko,labelContent:'both'}),'引线把南区的核心3、新业务2和总量5绑回该列；零值只留位置标记并写明0，不虚增面积。')
),'若读者主要需要逐格查精确值，另起一个比较表展品；图形本身仍要能读出小片的分项。','kit.mekko');
const channelColumns=[{key:'name',label:'渠道'},{key:'start',label:'2024年',type:'number',unit:'亿元',format:{decimals:1}},{key:'end',label:'2025年',type:'number',unit:'亿元',format:{decimals:1}},{key:'delta',label:'收入变化',type:'number',unit:'亿元',derive:{from:'start',to:'end'},format:{decimals:1},bar:{domain:[-1.2,.6]}},{key:'growth',label:'相对变化',type:'number',derive:{from:'start',to:'end',mode:'relative'},format:{decimals:1}},{key:'note',label:'下一步验证'}];
const channels=[{values:{name:'商超',start:6.4,end:5.3,note:'拆分门店、客户、价格与销量'}},{values:{name:'电商',start:1.6,end:2,note:'核验增量的毛利与获客成本'}},{values:{name:'经销',start:3.2,end:3.1,note:'核验库存与客户结构'}},{kind:'total',values:{name:'总计',start:11.2,end:10.4,note:'贡献合计−0.8亿元'}}];
page('商超解释主要降幅，比较表把规模、差额和线索放在同一行','把查数任务留给表格：同一列同一单位，变化条共享零基线与量尺；总计使用给定值。',
`<div class="exhibit">${kit.comparisonTable({palette,title:'渠道经营复核',columns:channelColumns,rows:channels})}<div class="annotation">差异列从原值自动计算；数据条表达数学增减，颜色本身不判定经营好坏。</div></div>`,
'将经营解释与数值核对放在同一行；不用六组KPI卡分散读者的注意力。','kit.comparisonTable');
page('进入下一阶段，需同时明确责任、交付物与放行条件','阶段长度表示顺序，不表示时长；这是流程建议，未虚构日期、预算或已达标的结果。',
ex('试点到复制｜条件化推进','建议流程；箭头表示满足条件后进入下一阶段',chart('processFlow',{width:1200,height:355,stages:[{label:'01 进入验证',owner:'业务负责人 + 法务',output:'目标市场清单\n准入和风险评估',gate:'准入路径明确\n预算与退出条件获批'},{label:'02 限额试点',owner:'区域团队 + 财务',output:'客户试点结果\n完整单位经济性',gate:'达到已批准的收益门槛\n现金周转可承受'},{label:'03 复制或调整',owner:'经营管理层',output:'资源配置决定\n复制标准与复盘安排',gate:'达到标准则复制\n否则调整或退出'}],transitions:['通过','达标']}),'责任、交付、放行条件按行对齐，可横向核对各阶段准备是否充分。'),
'若存在跨部门依赖、回路或并行分支，改用泳道或专门关系图。','kit.processFlow');
page('口径不同的增长信号，保留表格更准确','反例：相同的“增长”一词，不代表可以共用柱长、面积或颜色强度。以下全部为合成示例。',
`<div class="exhibit">${kit.comparisonTable({palette,title:'先查口径，再决定能否排序',columns:[{key:'object',label:'指标对象'},{key:'period',label:'期间'},{key:'scale',label:'规模 / 单位'},{key:'growth',label:'变化率'},{key:'limit',label:'比较边界'}],rows:[{kind:'group',label:'行业指标'},{values:{object:'设备出货',period:'2025全年',scale:'120万台',growth:'+30%',limit:'出货量不等于收入或利润'}},{values:{object:'软件服务',period:'2025上半年',scale:'80亿元',growth:'+18%',limit:'半年口径不与全年直接排名'}},{kind:'group',label:'公司样本'},{values:{object:'甲品牌海外',period:'2025全年',scale:'12亿元',growth:'+45%',limit:'单公司不能代表整个行业'}},{values:{object:'乙产品试点',period:'试点首季度',scale:null,growth:null,limit:'缺失以“—”表示，不能当作零'}}]})}<div class="annotation">没有可比的共同量纲与范围，因此不添加数据条、气泡或统一排名。</div></div>`,
'专业完成度取决于读者是否正确理解证据；简单表格可以是最终设计。','kit.comparisonTable');
let html=fs.readFileSync(path.join(root,'assets/deck_engine.html'),'utf8');html=html.slice(html.indexOf('<!DOCTYPE html>'));
const start=html.indexOf('<section class="slide'),end=html.indexOf('</div></div><!-- /stage /viewport -->');if(start<0||end<start)throw Error('引擎边界缺失');
html=html.slice(0,start)+slides.join('\n')+'\n'+html.slice(end);
const css=fs.readFileSync(path.join(root,'assets/consulting-layouts.css'),'utf8')+'\n.reading .slide__body{grid-template-rows:minmax(0,1fr) auto}.analytical .graphic{align-items:flex-start}.analytical .graphic>svg{height:auto;max-height:100%}.analytical .data-table{font-size:16px}.analytical .data-table td{padding:13px 9px}.analytical .slide__sticker{font-size:12px}';
html=html.replace('</style>',css+'\n</style>').replace('<title>Deck Title</title>','<title>分析表达升级 · 六页验证样稿</title>');
html=html.replace(/<script src="[^"]+"><\/script>/g,'').replace(/<script type="module">[\s\S]*?<\/script>/g,'');
html=html.replace("if(!window.echarts){ document.body.classList.add('no-charts'); return; }","if(!window.echarts){ if(document.querySelector('.chart')) document.body.classList.add('no-charts'); return; }");
html=themes.apply(html,themeId);
// 旧快照仍比较原始图形设计；统一文字字体以避免混淆两种变量。
html=html.replace(/font-family:Arial,'PingFang SC','Microsoft YaHei',sans-serif/g,'font-family:'+typography.get(profile).body);
html=pack(frame.apply(html),{profile});
const output=path.resolve(args.find(v=>!v.startsWith('--'))||path.join(root,'assets/analysis_reference_deck.html'));
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,html);
fs.writeFileSync(output.slice(0,-5)+'.pages.json',JSON.stringify({version:1,pages:pagesContract},null,2));
console.log(`6页分析样稿 → ${output}`);
