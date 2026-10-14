const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {inspectSlide}=require('./browser_visual_policy.cjs');
let pw;try{pw=require('playwright')}catch{pw=require(process.env.PLAYWRIGHT_MODULE||process.env.PLAYWRIGHT_PATH)}
(async()=>{const browser=await pw.chromium.launch({channel:'chrome',headless:true});try{
 const page=await browser.newPage({viewport:{width:1400,height:900}});
 const shell=attrs=>`<style>*{box-sizing:border-box} .slide{width:1280px;height:720px} .box{width:300px;min-height:80px;padding:12px;position:relative} </style><section class="slide"${attrs}>`;
 const check=async html=>{await page.setContent(shell('')+html+'</section>');return page.locator('.slide').evaluate(inspectSlide);};
 const checkPolicy=async(html,policy,attrs='')=>{await page.setContent(shell(attrs)+html+'</section>');return page.locator('.slide').evaluate(inspectSlide,policy);};
 for(const style of ['border-left:3px solid teal','border-top:4px solid navy','border-right:2px solid #888','border-bottom:1px solid purple','box-shadow:inset 4px 0 0 navy']){
  const r=await check(`<div class="box" style="${style}">关键限定不能删除</div>`);assert.ok(r.errors.length,style);
 }
 let r=await check(`<style>.box:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:teal}</style><div class="box">伪元素边条</div>`);assert.ok(r.errors.some(x=>x.code==='V-DECORATIVE-PSEUDO'));
 r=await check('<div class="box"><i style="position:absolute;left:0;top:0;width:4px;height:100%;background:teal"></i>独立色条节点</div>');assert.ok(r.errors.some(x=>x.code==='V-DECORATIVE-STRIP'));
 r=await check('<div class="box" style="background:#eee;height:250px">一行短文字</div>');assert.ok(r.warnings.some(x=>x.code==='V-EMPTY-MODULE'));
 r=await check('<div class="slide__body" style="height:500px"><p>正文只有上方一行</p></div>');assert.ok(r.warnings.some(x=>x.code==='V-BODY-REMAINDER'));
 r=await check('<div class="box" style="border:1px solid #aaa">普通完整框线</div><div class="box" style="border-bottom:1px solid #aaa">中性薄分隔线</div><h2 style="border-top:2px solid navy">展品标题边界</h2><table><tr><td style="border-left:3px solid navy">表格</td></tr></table><svg width="300" height="100"><rect width="4" height="100" fill="teal"/><text x="20" y="40">SVG需人工检查</text></svg><div style="width:50px;height:5px;background:teal"></div>');assert.equal(r.errors.length,0);assert.ok(r.findings.some(x=>x.code==='V-RASTER-VECTOR-MANUAL'));
 const bookends=fs.readFileSync(path.join(__dirname,'../assets/deck-bookends.css'),'utf8');await page.setContent(`<style>${bookends}</style><div class="bookend-kicker">封面引题</div>`);assert.equal(await page.locator('.bookend-kicker').evaluate(e=>getComputedStyle(e,'::before').content),'none');
 const frame=fs.readFileSync(path.join(__dirname,'../assets/deck-frame.css'),'utf8');
 await page.setContent(`<style>${frame}:root{--gray-2:#50606e;--page-bg:white}.slide{width:1280px;height:720px}.slide__header{height:70px}.callout{width:300px;height:80px;position:relative}.callout::after{content:'';position:absolute;left:0;top:0;width:4px;height:100%;background:teal}</style><section class="slide reading" data-frame="quiet" data-frame-boundary="line"><header class="slide__header"><h1 class="slide__title">真正页头</h1></header><div class="slide__body"><div class="callout slide__header">伪装页头类的文字模块</div></div></section>`);
 r=await page.locator('.slide').evaluate(inspectSlide);assert.equal(r.errors.length,1,JSON.stringify(r.errors));assert.ok(r.errors[0].selector.includes('div'));assert.ok(r.findings.some(x=>x.code==='V-QUIET-HEADER'));
 await page.addStyleTag({content:'.slide > .slide__header::after{height:4px;background:teal}'});r=await page.locator('.slide').evaluate(inspectSlide);assert.equal(r.errors.length,2,'真实页头改成粗色条也不能豁免');
 const engine=fs.readFileSync(path.join(__dirname,'../assets/deck_engine.html'),'utf8');const styles=[...engine.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map(m=>m[1]).join('\n');
 const layouts=fs.readFileSync(path.join(__dirname,'../assets/consulting-layouts.css'),'utf8');
 await page.setContent(`<style>${styles}\n${layouts}\n.slide{display:flex;position:relative;width:1280px;height:720px}</style><section class="slide reading"><div class="slide__body layout-paired"><div class="exhibit"><h2>展品标题</h2><div class="annotation">关键限定</div></div><div class="kpi-grid"><div class="kpi-card"><span class="kpi-val">38</span><span class="kpi-name">样本数量</span></div></div></div><div class="takeaway">保留判断</div></section>`);
 r=await page.locator('.slide').evaluate(inspectSlide);assert.equal(r.errors.length,0);const borders=await page.locator('.exhibit h2,.annotation,.takeaway,.kpi-card').evaluateAll(es=>es.map(e=>{const s=getComputedStyle(e);return ['Top','Right','Bottom','Left'].map(side=>parseFloat(s['border'+side+'Width']));}));assert.equal(borders.length,4);assert.ok(borders.flat().every(width=>width===0),JSON.stringify(borders));const heights=await page.locator('.annotation,.takeaway,.kpi-grid').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().height));assert.ok(heights.every(h=>h<160),JSON.stringify(heights));
 // 密度档位：判据一样，只有"由谁说"随档位变。compact 把展品区的空白升级为错误，功能页仍按设计豁免。
 {
  const tail='<div class="slide__body" style="height:500px"><p>正文只有上方一行</p></div>';
  const normal=await checkPolicy(tail,null);
  assert.ok(normal.warnings.some(x=>x.code==='V-BODY-REMAINDER'),'未启用档位时只报诊断');
  assert.equal(normal.errors.length,0,'未启用档位时不得阻塞');
  const compact=await checkPolicy(tail,{density:'compact'});
  assert.ok(compact.errors.some(x=>x.code==='V-BODY-REMAINDER'),JSON.stringify(compact.errors));
  assert.equal(compact.errors[0].bodyShare>0.2,true,'升级条件看占比，报错要带实测值');
  const cover=await checkPolicy(tail,{density:'compact'},' data-page-role="cover"');
  assert.equal(cover.errors.length,0,'封面留白是设计，不进密度门禁');
  assert.ok(cover.warnings.some(x=>x.code==='V-BODY-REMAINDER'),'豁免不等于不测量：诊断照报，供人判断');
  // 只量"末对象下方"的话，space-between 把空白挪到模块之间就能规避——所以模块间隙要单独量。
  const split='<div class="slide__body" style="height:600px;display:flex;flex-direction:column;justify-content:space-between"><div class="box">上模块</div><div class="box">下模块</div></div>';
  const spaced=await checkPolicy(split,{density:'compact'});
  assert.equal(spaced.warnings.some(x=>x.code==='V-BODY-REMAINDER'),false,'末对象贴着底部，脚部余量这条抓不到它');
  assert.ok(spaced.errors.some(x=>x.code==='V-MODULE-GAP'),JSON.stringify(spaced.errors));
  // 没有展品区的页（分隔页/封面）过去落在盲区：所有基于 .slide__body 的检查都落空。
  const divider=await checkPolicy('<header class="slide__header"><h1 class="slide__title">章节</h1></header><p>一句话</p>',{density:'compact'},' data-page-role="divider"');
  assert.ok(divider.warnings.some(x=>x.code==='V-PAGE-VOID'),'无展品区的页仍要被量到，否则它永远是盲区');
  assert.equal(divider.warnings.find(x=>x.code==='V-PAGE-VOID').role,'divider');
 }
 // 空置量的是页面，不是写法：同一段文字，标签后面的正文是裸文本节点还是被 <span> 包住，
 // 量到的底边必须一样。曾经只看"没有子元素的元素"，行内标签后面的多行正文因此量不到，
 // 凭空多出一段空置（实测同一版面差一整行高，页越长差越多），作者只好改 HTML 去迎合检查器。
 {
  const txt='表 1 是供给口径、表 2 是需求口径，两者之间没有节点对应关系，谁的支出给了谁在材料里未知，因此本稿不画任何流向图。'.repeat(2);
  const page=wrap=>`<div class="slide__body" style="height:400px;padding:16px"><div style="font-size:15px;line-height:24px"><strong style="display:block">口径提示</strong>${wrap?`<span>${txt}</span>`:txt}</div></div>`;
  const read=async html=>{const r=await checkPolicy(html,{density:'normal'});const m=[...r.warnings,...r.errors].find(x=>x.code==='V-BODY-REMAINDER');return m?m.gap:null;};
  const bare=await read(page(false)), wrapped=await read(page(true));
  assert.ok(bare!==null,'这段版面本来就该报出底部余量');
  assert.equal(bare,wrapped,'同样的版面，正文是不是裸文本节点不该改变空置量');
 }
 console.log('PASS visual policy: decorative borders/shadow/pseudo/strip, whitespace diagnostics (module gaps, no-body pages), density tiers, legal lines, SVG coverage and default natural heights');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
