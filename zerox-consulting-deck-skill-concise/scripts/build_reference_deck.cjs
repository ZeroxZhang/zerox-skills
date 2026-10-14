const frame=require('./apply_frame.cjs');
/* 从同一模板与组件构建可复现的验证样稿。前六页数字为用户旧稿材料，未在本次重核。 */
const fs=require('node:fs'), path=require('node:path');
const root=path.resolve(__dirname,'..'), kit=require('../assets/exhibit-kit.js');
const themes=require('../assets/deck-themes.js');
const typography=require('../assets/deck-typography.js'),{pack}=require('./pack_fonts.cjs');
const args=process.argv.slice(2), themeArg=args.find(v=>v.startsWith('--theme=')),themeId=themeArg?themeArg.slice(8):'mckinsey';
const palette=themes.palette(themeId);
const profile=(args.find(v=>v.startsWith('--typography='))||'--typography=serif-report-bold').slice(13);
const chart=(type,s)=>kit[type]({palette,typography_id:profile,...s});
const ex=(title,unit,body,note='')=>`<div class="exhibit"><h2>${title}</h2><div class="unit">${unit}</div><div class="graphic">${body}</div>${note?`<div class="annotation">${note}</div>`:''}</div>`;
const notes=rows=>rows.map(([h,t])=>`<div class="evidence-note"><strong>${h}</strong>${t}</div>`).join('');
const table=(heads,rows,widths=[])=>`<table class="data-table"><colgroup>${heads.map((h,i)=>`<col${widths[i]?` style="width:${widths[i]}%"`:''}>`).join('')}</colgroup><thead><tr>${heads.map(h=>`<th${/规模|同比/.test(h)?' class="num"':''}>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map((c,i)=>`<td${/规模|同比/.test(heads[i])?' class="num"':''}>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
let slides=[];
const src='来源：用户测试稿 china-go-global（2026-09-05），对应页码见页眉；本轮用于设计验证，沿用数字未重新核验。';
const pagesContract=[];
function page(title,lead,body,source=src,tracker='出海研究 · 设计迭代样稿',form='html.text',status='材料沿用 · 待事实复核'){
 pagesContract.push({page:pagesContract.length+1,proves:title,form});
 const n=slides.length+1;slides.push(`<section class="slide reading${n===1?' active':''}" data-form="${form}" data-frame-boundary="integrated">${frame.markup}<div class="slide__tracker">${tracker}</div><div class="slide__sticker">${status}</div><header class="slide__header"><h1 class="slide__title">${title}</h1><div class="slide__lead">${lead}</div></header><div class="slide__body">${body}</div><div class="source">${source}</div><div class="slide__page">${n}</div></section>`);
}
page('跨市场口径尚未统一，先核实基准再讨论海外扩张目标','分开展示原稿记录与缺失的定义，不从不同样本直接推导企业可实现的增长空间。',
`<div class="layout-split">${ex('01｜原稿数字与比较资格','2024年；下列样本范围尚未核实，不作共轴排名',table(['原稿对象','原稿占比','比较前需要核验'],[
['中国A股','15%','上市样本、地域与收入分母'],['欧洲','54%','国家/公司覆盖与汇总方法'],['日本','51%','企业样本与海外业务定义'],['美国','40%','行业结构、分母与统计范围']],[23,18,59]),'原稿数值只作为待核记录；样本构成、期间和收入定义一致后才建立可比较基线。')}<div class="exhibit"><h2>02｜企业层面需要的证据</h2>${notes([['需求与可进入市场','明确可服务客户、准入条件与竞争基准。'],['贡献与资本占用','核对价格、全成本、现金周转和实施投入。'],['目标形成方式','从企业能力与可获得增量构建目标，不用跨市场百分比差直接外推。']])}</div></div>`,src,'原稿P04 → 比较资格与证据需求','html.table');
page('行业指标与公司样本应分组解读，增速不直接等于投资优先级','保留六项增长信号，同时显式列出指标对象、量纲及下一步应验证的经营问题。',
`<div class="exhibit"><h2>01｜增长证据台账</h2>${table(['指标对象 / 范围','2025规模','同比','能够支持的判断','仍需验证'],[
['新能源汽车出口 · 行业','261.5万辆','+103.7%','出口量快速扩张','单车利润、关税及本地产能'],['储能电池出货 · 行业','630 GWh','+85%','出货需求增长','海外占比、量增能否转为利润'],['跨境电商进出口 · 行业','2.84万亿元','+4.8%','总量大、增速趋缓','履约成本、获客与合规'],['游戏海外收入 · 行业','204.55亿美元','+10.2%','收入增长恢复','产品周期、区域及平台依赖'],['名创优品海外 · 公司','86.3亿元','+29.3%','该公司海外业务增长','不能代表消费品牌整体'],['MiniMax收入 · 公司','旧稿未列统一规模','+158.9%','公司样本显示高增长','收入地域口径、基数与盈利']],[23,15,11,25,26])}<div class="layout-three">${notes([['量的增长｜车与储能','销量与出货是需求信号；利润验证还需要价格、成本与本地交付数据。'],['收入增长｜电商与游戏','先核对地域、交易额/收入定义、修订口径，再解释增长可持续性。'],['公司样本｜品牌与AI','用于提出机制假设，不能从单个公司的增速外推行业排名。']])}</div></div><div class="decision-strip">研究顺序：先核实口径 → 再比较经济性 → 最后评估企业的进入条件；不输出“六赛道增速排行榜”。</div>`,src,'原稿P08 → 分组证据表','html.table');
page('样本支持检验经营能力，但尚不能证明统一成功公式','在同一组维度下同时呈现正向样本与反例，把经营事实和因果推断分开。',
`<div class="exhibit"><h2>01｜同维度案例对照</h2>${table(['样本','本地经营 / 渠道','品牌 / 产品 / 技术','旧稿结果信号','解释与边界'],[
['<b>安克创新</b>','境外收入96.62%；亚马逊渠道52%','研发占营收9.48%；多渠道建设','营收305.14亿元<br>同比+23.49%','研发与增长并存；<br>需监测渠道集中风险'],['<b>比亚迪</b>','海外产能与经销网络','垂直整合与新能源产品组合','海外销量约105万辆<br>同比+145%','销量不等于盈利；核实海外利润和产能利用'],['<b>名创优品</b>','海外门店3583家；本地伙伴','IP合作与本地选品','海外收入86.3亿元<br>同比+29.3%','需区分同店、开店与汇率贡献'],['<b>传音控股</b>','渠道与支付本地化','低价产品组合；存储成本压力','净利25.81亿元<br>同比−53.5%','本地化不是充分条件；旧稿利润数值存在待核分歧']],[13,24,22,18,23])}</div><div class="layout-three">${notes([['机制假设','本地运营可能降低进入摩擦，产品差异化可能改善价格与毛利。'],['反例价值','本地渠道基础强，不代表能抵御成本变化和竞争升级。'],['下一步验证','补充同店、单位经济性、成本桥与可比公司，避免只选成功样本。']])}</div>`,src,'原稿P16 → 案例 + 反例 + 推断边界','html.table');
page('评分缺少锚点时，先呈现评价依据与待验证条件','保留原稿的研究维度，将未经支持的分值退出比较编码，避免形成假精度。',
`<div class="exhibit"><h2>01｜建立评价依据</h2>${table(['维度','需要的定义与事实','可接受的表达','当前处理'],[
['规模','同范围市场口径、期间、币种和可服务边界','可比数值或区间；样本分组','先核实范围'],['增速','相同时间窗口与基数，实际/预测区别','趋势、分布与异常解释','不由增速直接排优先'],['壁垒','客户、技术、渠道、合规的具体机制','有依据的能力/机制比较','不凭主观1–5分定强弱'],['政策风险','适用市场、情景、传导机制与暴露','条件分支与应对措施','高低档需可观察锚点']],[12,35,29,24])}</div><div class="layout-three">${notes([['保留框架价值','用共同维度组织尽调，丰富材料可以继续扩展分析。'],['避免伪精确','原稿无评分定义与证据，暂不使用色阶、面积或综合分。'],['获得证据后再比较','补齐锚点、权重和敏感性，或直接用经济性与约束作取舍。']])}</div>`,src+' 原稿评分仅作为历史输入，不作为本页分析结果。','原稿P17 → 定性证据框架','html.matrix','评价依据 · 待验证');
page('市场、模式与进入条件必须成套比较，投入建议才能执行','把三列独立建议改为“业务组合—条件—证据缺口—下一动作”的决策表。',
`<div class="exhibit"><h2>01｜条件化方案比较</h2>${table(['业务组合','区域 / 模式','成立条件','未决证据','下一步动作'],[
['<b>新能源车 / 储能</b>','东盟、中东、拉美<br>本地产能或合资','准入清晰、渠道具备、产能与需求匹配','全成本、关税、利用率、伙伴能力','进入市场尽调，核验投资门槛'],['<b>AI内容 / IP品牌</b>','按细分市场选择<br>产品与生态合作','内容/数据合规、留存和获客经济性成立','区域收入、付费、毛利与合规成本','开展可回收的产品/渠道试点'],['<b>跨境电商存量</b>','既有市场<br>海外仓、半托管','履约和库存效率可改善贡献利润','退货、仓租、库存周转与平台费','先优化单元经济性再扩规模'],['<b>低价直邮 / 重资产扩店</b>','逐市场评估<br>不统一默认退出','现金流可承受且有可验证差异化','政策情景与盈亏平衡','限额试验，设止损条件']],[19,22,22,21,16])}<div class="layout-three">${notes([['收益门槛｜财务牵头','将价格、履约、税费、获客和资本占用纳入同一模型；由企业批准回报门槛。'],['进入门槛｜业务与法务','列明市场准入、伙伴能力和资源依赖；无法满足时调整区域或进入模式。'],['退出门槛｜运营牵头','试点前确定复盘时点、损失上限与停止条件，避免因沉没成本持续加码。']])}</div></div><div class="decision-strip">本轮决策请求：批准尽调与试点范围；大规模投入须在收益、风险和退出条件明确后另行审议。</div>`,src+' 方案为设计示例中的条件化建议，不构成已验证的投资结论。','原稿P18 → 决策表','html.matrix','建议 · 条件待验证');
page('实施计划需绑定责任、交付与退出条件，而不仅是三个阶段','以下18个月为原稿建议时间窗；用泳道表达工作衔接，用门禁约束投入。',
`<div class="exhibit"><h2>01｜责任泳道与阶段依赖</h2><div class="graphic">${chart('swimlane',{width:1200,height:280,lanes:['合规 / 法务','业务 / 区域','财务 / 运营'],stages:['A启动 → 0–6月验证','B扩张 → 6–12月运营','C复制 → 12–18月迭代'],items:[{id:'a',label:'准入及风险清单',lane:0,stage:0},{id:'b',label:'本地制度落实',lane:0,stage:1},{id:'c',label:'合规复核',lane:0,stage:2},{id:'d',label:'市场与伙伴筛选',lane:1,stage:0},{id:'e',label:'客户与渠道试点',lane:1,stage:1},{id:'f',label:'达标市场扩张',lane:1,stage:2},{id:'g',label:'全成本模型',lane:2,stage:0},{id:'h',label:'单位经济性复盘',lane:2,stage:1},{id:'i',label:'资源再配置',lane:2,stage:2}],edges:[{from:'a',to:'b'},{from:'b',to:'c'},{from:'d',to:'e'},{from:'e',to:'f'},{from:'g',to:'h'},{from:'h',to:'i'}]})}</div></div><div class="layout-three">${notes([['门禁A｜允许启动','准入路径、责任人、预算上限及退出条件齐备；条件未满足不进入试点。'],['门禁B｜允许扩张','试点实际毛利、现金周转与客户指标达到企业批准阈值。'],['门禁C｜复制或退出','达到复制标准才放大；未达标则调整假设、缩减投入或退出。']])}</div>`,src+' 时间为建议窗口；阈值需依据企业基线批准，未伪造达标数字。','原稿P19 → 泳道 + 阶段门禁','kit.swimlane','建议 · 时间窗口非承诺');
const synth='来源：本技能合成数据，仅验证图形、计算与布局；不代表任何真实企业或市场。';
page('商超减少1.1亿元，电商增长仅抵消其约36%的拖累','同一份合成数据同时用贡献桥、期初期末对比验证；期末收入10.4亿元，较期初减少0.8亿元。',
`<div class="layout-paired">${ex('01｜收入变动的贡献分解','亿元；贡献柱附正负号，总计单独表示，不等同经营评价',chart('waterfall',{width:585,height:330,items:[{label:'期初',type:'total',value:11.2},{label:'电商',type:'delta',value:.4},{label:'商超',type:'delta',value:-1.1},{label:'经销',type:'delta',value:-.1},{label:'期末',type:'subtotal'}]}),'电商抵消商超拖累约'+kit.formatNumber(.4/1.1*100,{decimals:0})+'%；闭合：11.2 + 0.4 − 1.1 − 0.1 = 10.4。')}${ex('02｜渠道规模变化复核','亿元；空心=2024年，实心=2025年',chart('dumbbell',{width:585,height:330,startLabel:'2024年',endLabel:'2025年',items:[{label:'商超',start:6.4,end:5.3},{label:'电商',start:1.6,end:2},{label:'经销',start:3.2,end:3.1}]}),'商超占下滑的主要部分；贡献解释不等于已经识别客户流失的因果。')}</div><div class="decision-strip">下一步分析：按门店、客户与价格/销量拆解商超缺口，再选择渠道干预措施。</div>`,synth,'组件验证01 · waterfall / dumbbell','kit.waterfall','示意数据 · 非真实结论');
page('构成和规模需同时展示，份额变化应与绝对量分开阅读','左侧Mekko同时编码市场大小与产品构成；右侧坡度图比较两个时点的同口径份额。',
`<div class="layout-paired">${ex('01｜地区规模 × 产品构成','合成销售额（任意单位）；列宽=地区总量，段面积=绝对销售额',chart('mekko',{width:585,height:330,items:[{label:'东区',segments:[{label:'核心',value:60},{label:'新业务',value:40}]},{label:'西区',segments:[{label:'核心',value:30},{label:'新业务',value:20}]},{label:'南区',segments:[{label:'核心',value:30},{label:'新业务',value:70}]}]}),'地区总量100 / 50 / 100；色块直接标注业务名称；同实体跨地区保持同色。')}${ex('02｜客户组合份额迁移','%；左右时点分别合计100%，线色=客户类别',chart('slope',{width:585,height:330,startLabel:'2024年',endLabel:'2025年',items:[{label:'企业',start:60,end:50},{label:'中小',start:30,end:35},{label:'个人',start:10,end:15}]}),'企业份额下降10个百分点；份额下降不代表绝对收入下降。')}</div><div class="decision-strip">两图回答不同问题：规模与构成决定资源覆盖，份额迁移提示进一步验证客群经济性。</div>`,synth,'组件验证02 · mekko / slope','kit.mekko','示意数据 · 非真实结论');
page('指标缺口与驱动机制并列呈现，才能把监控转为诊断','子弹图呈现实际对目标；驱动树展示分析拆解，不把虚构的因果强度编码进连线。',
`<div class="layout-paired">${ex('01｜目标差距','同一指标内实际与目标可比；各行量尺独立',chart('bullet',{width:585,height:330,items:[{label:'交付达成率%',value:76,target:90,max:100},{label:'留存率%',value:68,target:80,max:100},{label:'计划覆盖率%',value:85,target:95,max:100}]}),'粗短线=目标；底条=0至100；指标上升是否更好由业务定义。')}${ex('02｜交付结果的分析拆解','连线表示拆解关系，不表示已证实因果',chart('tree',{width:585,height:330,root:{label:'交付达成',children:[{label:'供给可用',children:[{label:'产能'},{label:'备货'}]},{label:'履约效率',children:[{label:'排程'},{label:'物流'}]}]}}),'先按驱动分项取数，再验证哪个因素解释目标差距。')}</div><div class="decision-strip">每个落后指标都应连接到可验证的驱动、责任人与下一次复盘，不只展示红黄绿。</div>`,synth,'组件验证03 · bullet / tree','kit.bullet','示意数据 · 非真实结论');
let engine=fs.readFileSync(path.join(root,'assets/deck_engine.html'),'utf8');
engine=engine.slice(engine.indexOf('<!DOCTYPE html>'));
engine='<!-- v9设计与组件验证：前6页沿用历史材料且未重核，后3页为合成数据；全部静态SVG/HTML。 -->\n'+engine;
pagesContract[2].repetitionReason='第 1–3 页是同一份材料的三类核对：原稿记录、增长证据台账、案例对照。三页都由精确查值承担证明责任；共用表格不是想不出别的画法，而是这三处都不能用模式扫描代替逐格核对。';
let a=engine.indexOf('<section class="slide'),z=engine.indexOf('</div></div><!-- /stage /viewport -->');
if(a<0||z<a)throw Error('引擎页面边界缺失');engine=engine.slice(0,a)+slides.join('\n')+'\n'+engine.slice(z);
const css=fs.readFileSync(path.join(root,'assets/consulting-layouts.css'),'utf8')+`\n.reading .slide__body{grid-template-rows:minmax(0,1fr) auto}.reading .slide__sticker{font-size:12px}.reading .data-table{font-size:15px}.reading .data-table td{padding:11px 9px}`;
engine=engine.replace('</style>',css+'\n</style>').replace('<title>Deck Title</title>','<title>咨询Deck v9 · 设计与组件样例</title>');
// 本样稿全部为静态SVG/HTML，去除无需使用的外部库，实现真正离线自包含。
engine=engine.replace(/<script src="[^"]+"><\/script>/g,'').replace(/<script type="module">[\s\S]*?<\/script>/g,'');
engine=engine.replace('if(!window.echarts){ document.body.classList.add(\'no-charts\'); return; }',"if(!window.echarts){ if(document.querySelector('.chart')) document.body.classList.add('no-charts'); return; }");
engine=themes.apply(engine,themeId);
engine=engine.replace("font:16px Arial,'PingFang SC',sans-serif",'font:16px '+typography.get(profile).body);
engine=pack(frame.apply(engine),{profile});
const output=path.resolve(args.find(v=>!v.startsWith('--'))||path.join(root,'assets/reference_deck.html'));fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,engine);
// 样稿同样受族分布约束：这里是组件示范稿，按入口逐个演示表单与四个构建期组件，
// 「精确查数」族因此偏高；缺席族逐条写明为什么这份样稿不承载。真实报告的取值另算。
const contract={version:1,
 familyDiversityReason:'这是按入口逐个演示的组件样稿，不是一份报告：它依次展示表单、矩阵与四个构建期组件，所以「精确查数」族占比偏高是示范顺序的结果，不代表真实报告的编码分布。',
 unusedFamilies:{trend:'样稿不承载时间维度：没有演示序列数据',distribution:'样稿数据是离散类别，没有原始观测可装箱',correlation:'样稿没有成对的两变量观测',flow:'样稿没有守恒可核的流量',hierarchy:'样稿没有需要逐层拆分的总体'},
 pages:pagesContract};
fs.writeFileSync(output.replace(/\.html$/,'')+'.pages.json',JSON.stringify(contract,null,2));
console.log(`${slides.length}页 → ${output}`);
