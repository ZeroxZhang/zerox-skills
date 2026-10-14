/* 完整内部规范报告：来源为随包实际文档，不虚构外部文献或业务数据。 */
const fs=require('node:fs'),path=require('node:path'),bookends=require('./bookends.cjs'),frame=require('./apply_frame.cjs'),fonts=require('./pack_fonts.cjs'),themes=require('../assets/deck-themes.js');
const root=path.resolve(__dirname,'..');
const sources=[
  {id:'S1',author:'Consulting Deck Skill',title:'完整报告的封面、参考资料与封底',kind:'项目规范',locator:'references/bookends.md'},
  {id:'S2',author:'Consulting Deck Skill',title:'字体与角色基线',kind:'项目规范',locator:'references/type_frame.md，字体与角色'},
  {id:'S3',author:'Consulting Deck Skill',title:'证据契约与数据几何',kind:'项目规范',locator:'references/analysis.md，证据契约'},
  {id:'S4',author:'Consulting Deck Skill',title:'母版：页面边界与页边识别',kind:'项目规范',locator:'references/type_frame.md，母版'},
  {id:'S5',author:'Consulting Deck Skill',title:'咨询 deck 验收',kind:'项目规范',locator:'references/qa.md，完整报告首尾'},
  {id:'S6',author:'Consulting Deck Skill',title:'HTML＋PDF交付',kind:'项目规范',locator:'references/delivery.md，一致性与限制'}
];
const meta={title:'报告的开篇与收束\n建立统一的信息秩序',shortTitle:'清楚识别 · 有据可查 · 完整收束',type:'报告设计规范 · READING REPORT',date:'2026年9月8日',producer:'Consulting Deck Skill',subtitle:'封面、单页参考资料与封底呈现说明',version:'报告版本 1.0'};
function build({ratio='16x9',profile='serif-report-bold',theme='mckinsey'}={}){
  if(!['16x9','4x3'].includes(ratio))throw Error('不支持的画布比例');
  const page2=`<section class="slide reading" data-page-role="content" data-frame-boundary="integrated">
  <div class="slide__frame" aria-hidden="true"></div>
  <header class="slide__header"><h1 class="slide__title">从识别主题到查找依据，首尾页承担不同的阅读任务</h1><p class="slide__lead">统一结构使读者知道这是什么报告、依据在哪里，以及阅读何时结束。</p></header>
  <div class="slide__body role-comparison">
    <div class="role-block"><p class="role-label">01 / 封面</p><h2>识别报告</h2><p>出品方、主题和日期有稳定位置；主标题成为唯一视觉焦点。</p><p class="role-note">真实信息按需呈现，缺少的客户、编号或声明自然收起。</p></div>
    <div class="role-block"><p class="role-label">02 / 参考资料</p><h2>查找依据</h2><p>一页集中列示采用的资料；条目清楚、顺序稳定，允许明确节选。</p><p class="role-note">正文保留具体定位，必要底稿保留全部来源。</p></div>
    <div class="role-block"><p class="role-label">03 / 封底</p><h2>结束阅读</h2><p>延续封面的字体、色彩与对齐，减少信息，留下清楚的结束点。</p><p class="role-note">沿用同一报告身份和版本，不增加新观点或新资料。</p></div>
  </div>
  <p class="source"><b>Source:</b> [S1] 首尾页规则；[S2] 字体系统；[S4] 页面母版。各来源的文件定位见参考资料页。</p><div class="slide__page">2</div>
</section>`;
  const page3=`<section class="slide reading" data-page-role="content" data-frame-boundary="line">
  <div class="slide__frame" aria-hidden="true"></div>
  <header class="slide__header"><h1 class="slide__title">书目可以节选，关键证据与完整出处仍须保留</h1><p class="slide__lead">一页容量通过编辑取舍满足；不以缩小字号或隐藏条目换取表面完整。</p></header>
  <div class="slide__body source-workflow">
    <div><h2>先整理，再决定展示范围</h2><ol class="source-steps"><li><b>去重</b><span>同一文献的镜像与重复转述合并，实质不同的版本分别保留。</span></li><li><b>精编</b><span>保留作者、标题、年份与必要定位，去掉重复字段。</span></li><li><b>重排</b><span>按实际文字长度选择单栏或双栏，加载最终字体后检查容量。</span></li><li><b>节选</b><span>优先核心数据、关键方法和重要反证，明确标为“主要参考资料（节选）”。</span></li></ol></div>
    <aside class="source-responsibility"><h2>三个位置各有职责</h2><p><b>正文 Source</b><br>核对本页判断的具体出处与口径。</p><p><b>末页书目</b><br>识别全篇采用的资料及其版本。</p><p><b>必要来源底稿</b><br>保留全部实际使用来源，供进一步复查。</p><p class="role-note">HTML 与 PDF 使用同一展示集合，每个条目都应静态可读。</p></aside>
  </div><p class="source"><b>Source:</b> [S1] 首尾页规则；[S3] 证据契约；[S5] 成稿验收；[S6] HTML＋PDF交付。</p><div class="slide__page">3</div>
</section>`;
  let html=fs.readFileSync(path.join(root,'assets/deck_engine.html'),'utf8');
  const begin=html.indexOf('<div id="viewport"><div id="stage">'),end=html.indexOf('</div></div><!-- /stage /viewport -->');
  if(begin<0||end<begin)throw Error('引擎 stage 边界不匹配');
  html=html.slice(0,begin)+'<div id="viewport"><div id="stage">\n'+[bookends.cover(meta),page2,page3,bookends.references({sources,columns:2,splitAt:3,page:4}),bookends.backCover(meta)].join('\n')+'\n'+html.slice(end);
  html=html.replace('<title>Deck Title</title>','<title>报告的开篇与收束 · V10规范说明</title>').replace('<body data-ratio="16x9">',`<body data-ratio="${ratio}">`);
  // 无图表报告只需保留引擎；移除未使用的外链与运行库，离线内容独立完整。
  html=html.replace(/<script\b[^>]*src="(?:https?:[^\"]*|\.\/(?:echarts-recipes|chart-runtime)\.js)"[^>]*><\/script>/g,'');
  html=html.replace(/<script type="module">[\s\S]*?<\/script>/g,'');
  html=html.replace('</head>',`<style>
.slide.reading{padding:32px 40px 26px}.slide.reading .slide__lead{font-size:15px;line-height:1.5;color:var(--gray-2)}
.slide.reading .slide__body{margin-top:24px}.role-comparison{grid-template-columns:repeat(3,minmax(0,1fr));gap:32px;align-items:start}
.role-block{border:0;padding-top:0}.role-label{font-size:14px;color:var(--gray-2);margin-bottom:16px}
.role-block h2,.source-workflow h2{font-size:20px;margin-bottom:20px}.role-block p{font-size:17px;line-height:1.65}
.role-block .role-note,.role-note{font-size:15px;color:var(--gray-2);line-height:1.6;margin-top:24px}
.source-workflow{grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:48px;align-items:start}
.source-steps{list-style:none;display:grid;gap:22px}.source-steps li{display:grid;grid-template-columns:48px 1fr;gap:16px;font-size:17px;line-height:1.6}
.source-steps b{color:var(--brand)}.source-responsibility{border-left:1px solid var(--gray-3);padding-left:28px}.source-responsibility p{font-size:16px;line-height:1.6;margin-top:18px}
body[data-ratio="4x3"] .role-comparison{gap:24px}body[data-ratio="4x3"] .source-workflow{gap:28px;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr)}
</style>\n</head>`);
  return fonts.pack(bookends.applyStyles(frame.apply(themes.apply(html,theme)),{kind:'report'}),{profile});
}
if(require.main===module){const output=path.resolve(process.argv[2]||path.join(root,'assets/bookends_example.html'));fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,build({ratio:process.argv[3]||'16x9'}));console.log(output);}
module.exports={build,meta,sources};
