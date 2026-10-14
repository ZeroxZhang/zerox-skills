/* V10 可观察行为：新页实际布局/导航/打印、旧稿隔离，以及错误合同的拒绝。 */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {pathToFileURL}=require('node:url'),{execFileSync,spawnSync}=require('node:child_process');
const bookends=require('./bookends.cjs'),audit=require('./check_bookends.cjs'),fontAudit=require('./browser_font_audit.cjs');
let pw;try{pw=require('playwright')}catch(e){pw=require(process.env.PLAYWRIGHT_MODULE||process.env.PLAYWRIGHT_PATH)}
const root=path.resolve(__dirname,'..');
const refsPattern=/<section\b[^>]*data-page-role="references"[^>]*>[\s\S]*?<\/section>/;
const read=name=>fs.readFileSync(path.join(root,name),'utf8');
const fixtureSources=Array.from({length:12},(_,i)=>({id:'R'+(i+1),author:'Test documents',title:'Reference '+(i+1)+': service evidence and reporting boundaries',date:'2026',kind:'TEST FIXTURE',url:'https://example.com/reference-'+(i+1)}));
(async()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-bookends-test-'));
  const browser=await pw.chromium.launch({channel:process.env.CHROME_CHANNEL||'chrome',headless:true});
  try{
    const base=read('assets/bookends_example.html');
    assert.equal(bookends.applyStyles(bookends.applyStyles(base)),bookends.applyStyles(base),'样式注入幂等');
    // 首尾页同样要显式声明边界：data-frame="off" 只关装饰，不是 boundary 的替代字段。
    // 少了这一项，装配器对每一页都会失败——用它生成的封面到装配那一步必定卡住。
    for(const [name,frag] of [['封面',bookends.cover({title:'测试报告',date:'2026-09-19'})],['封底',bookends.backCover({title:'测试报告',shortTitle:'测试',date:'2026-09-19'})]])
      assert.match(frag,/data-frame-boundary="space"/,name+'必须带 data-frame-boundary="space"');
    const source=fixtureSources[0];
    assert.equal(bookends.normalizeSources([source,{...source}]).length,1,'同文献精确重复只列一次');
    assert.equal(bookends.normalizeSources([source,{...source,id:'next',date:'2025'}]).length,2,'同 URL 不同年份不误合并');
    assert.throws(()=>bookends.normalizeSources([source,{...source,title:'Conflict'}]),/冲突/);
    assert.throws(()=>bookends.references({sources:[{title:'bad',url:'javascript:alert(1)'}]}),/http/);
    assert.throws(()=>bookends.references({sources:fixtureSources,selectedIds:['absent']}),/未知/);
    assert.throws(()=>bookends.references({sources:fixtureSources,selectedIds:['R1','R1']}),/不重复/);
    assert.throws(()=>bookends.references({sources:fixtureSources,columns:2,splitAt:12}),/两栏/);
    assert.match(bookends.references({sources:fixtureSources,selectedIds:['R1'],note:'完整夹具随测试保存。'}),/1 项主要来源（共 12 项）/,'自定义底稿说明不覆盖节选数量');
    assert.match(bookends.cover({title:'A <script> & B',date:'2026'}),/A &lt;script&gt; &amp; B/);
    assert.doesNotMatch(bookends.cover({title:'A',date:'2026'}),/Confidential|bookend-client|bookend-producer|bookend-statement/);
    const refs=bookends.references({sources:fixtureSources,columns:2,splitAt:6,page:4});
    const file=path.join(dir,'report.html');fs.writeFileSync(file,base.replace(refsPattern,()=>refs));
    const page=await browser.newPage({viewport:{width:1400,height:900}});
    await fontAudit.attach(page);
    await page.context().route('https://example.com/**',r=>r.fulfill({contentType:'text/html',body:'<title>Source fixture</title><p>Reference fixture</p>'}));
    async function observe(html,ratio='16x9'){
      const target=path.join(dir,'observe.html');fs.writeFileSync(target,html.replace('<body data-ratio="16x9">',`<body data-ratio="${ratio}">`));
      await page.goto(pathToFileURL(target).href);await page.evaluate(()=>window.deckReady);
      const rows=[];
      for(let i=0;i<5;i++){
        await page.evaluate(()=>document.activeElement?.blur());await page.keyboard.press('Home');for(let j=0;j<i;j++)await page.keyboard.press('ArrowRight');
        rows.push({bookends:await page.locator('.slide.active').evaluate(audit.inspectPage)});
      }
      return rows;
    }
    let rows=await observe(fs.readFileSync(file,'utf8'));
    assert.deepEqual(audit.checkDocument(rows,{kind:'report'}).errors,[],'五页完整报告应可用');
    rows=await observe(fs.readFileSync(file,'utf8'),'4x3');
    assert.deepEqual(audit.checkDocument(rows,{kind:'report'}).errors,[],'4:3 实际布局不溢出');
    assert.equal(await page.locator('#stage').evaluate(e=>getComputedStyle(e).width),'1024px');
    // 真实链接点击与 Enter 均只访问来源，不改变报告页码。
    await page.goto(pathToFileURL(file).href+'#4');await page.evaluate(()=>window.deckReady);
    const anchor=page.locator('.slide.active a').first();
    let popupPromise=page.waitForEvent('popup');await anchor.click();let popup=await popupPromise;await popup.waitForLoadState();
    assert.equal(await popup.title(),'Source fixture');assert.match(page.url(),/#4$/);await popup.close();
    popupPromise=page.waitForEvent('popup');await anchor.press('Enter');popup=await popupPromise;await popup.waitForLoadState();assert.match(page.url(),/#4$/);await popup.close();
    await anchor.press(' ');assert.match(page.url(),/#4$/,'链接焦点空格不翻页');
    await page.evaluate(()=>document.activeElement.blur());await page.keyboard.press('g');
    const overviewPopup=[];page.on('popup',p=>overviewPopup.push(p));await page.locator('[data-page-role="references"] a').first().click();
    assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('overview')),false);assert.match(page.url(),/#4$/);assert.equal(overviewPopup.length,0,'总览选择页面不打开链接');
    await page.evaluate(()=>document.activeElement.blur());await page.keyboard.press('ArrowRight');assert.match(page.url(),/#5$/);
    await page.keyboard.press('Home');await page.locator('.slide.active').click({position:{x:1150,y:100}});assert.match(page.url(),/#2$/,'背景翻页继续可用');
    await page.keyboard.press('Home');
    const pdf=path.join(dir,'references.pdf');await page.pdf({path:pdf,printBackground:true,preferCSSPageSize:true});
    const urls=execFileSync('pdfinfo',['-url',pdf],{encoding:'utf8'});for(const source of fixtureSources)assert.ok(urls.includes(source.url),'PDF 来源链接 '+source.id);
    assert.match(execFileSync('pdfinfo',[pdf],{encoding:'utf8'}),/Pages:\s+5/);
    // 删除封底、数量伪报和内容隐藏不能成为合格完整稿。
    const valid=await observe(fs.readFileSync(file,'utf8'));
    assert.ok(audit.checkDocument(valid.slice(0,-1),{kind:'report'}).errors.length);
    const badCount=structuredClone(valid);badCount[3].bookends.total=13;assert.ok(audit.checkDocument(badCount,{kind:'report'}).errors.some(e=>/数量/.test(e)));
    const hidden=base.replace(refsPattern,()=>refs).replace('</head>','<style>[data-reference-id="R1"]{display:none}</style></head>');
    assert.ok(audit.checkDocument(await observe(hidden),{kind:'report'}).errors.some(e=>/不可见/.test(e)));
    for(const selector of ['.reference-columns','.reference-text']){
      const hiddenParent=base.replace(refsPattern,()=>refs).replace('</head>',`<style>${selector}{opacity:0}@media print{${selector}{opacity:1}}</style></head>`);
      assert.ok(audit.checkDocument(await observe(hiddenParent),{kind:'report'}).errors.some(e=>/不可见/.test(e)),selector+' 隐藏应被拒绝');
    }
    const hiddenText=base.replace(refsPattern,()=>refs).replace('</head>','<style>.reference-text{display:none}</style></head>');
    const hiddenRows=await observe(hiddenText);
    assert.ok(audit.checkDocument(hiddenRows,{kind:'report'}).errors.some(e=>/不可见/.test(e)));
    assert.ok(hiddenRows[3].bookends.entries[0].text.includes(source.title),'期望书目全文不因隐藏而退化成序号');
    const huge=Array.from({length:48},(_,i)=>({...fixtureSources[i%12],id:'O'+i,title:'Long reference '+i+' '+fixtureSources[i%12].title,url:'https://example.com/overflow-'+i}));
    const crowded=base.replace(refsPattern,()=>bookends.references({sources:huge,columns:2,page:4}));
    assert.ok(audit.checkDocument(await observe(crowded),{kind:'report'}).errors.some(e=>/容量/.test(e)),'不静默删条目或缩字');
    const selected=base.replace(refsPattern,()=>bookends.references({sources:fixtureSources,selectedIds:['R1','R2','R11'],page:4}));
    const selectedRows=await observe(selected);assert.deepEqual(audit.checkDocument(selectedRows,{kind:'report'}).errors,[]);assert.match(selectedRows[3].bookends.title,/节选/);assert.equal(selectedRows[3].bookends.total,12);
    assert.ok(selectedRows[3].bookends.entries.some(e=>e.id==='R11'&&e.text.startsWith('[R11]')),'书目可见标识保留正文原ID');
    // 样式注入不改变旧稿实际字体、位置与文本。
    const legacy=read('assets/reference_deck.html'),legacyFile=path.join(dir,'legacy.html');fs.writeFileSync(legacyFile,legacy);
    await page.goto(pathToFileURL(legacyFile).href+'#3');await page.evaluate(()=>window.deckReady);const before=await fontAudit.signature(page);
    fs.writeFileSync(legacyFile,bookends.applyStyles(legacy));await page.reload();await page.evaluate(()=>window.deckReady);assert.deepEqual(await fontAudit.signature(page),before);
    assert.deepEqual(audit.checkDocument([{bookends:{role:null}}],{}).errors,[],'旧稿不要求新首尾合同');
    assert.ok(audit.checkDocument(valid,{kind:'reports'}).errors.length,'显式未知类型不能静默降级');
    // 默认内置图标可用，不因一个未使用的在线增强模块发出网络请求。
    const iconModule=read('assets/deck_engine.html').match(/<script type="module">[\s\S]*?<\/script>/)[0];
    const requests=[],record=r=>{if(/^https?:/.test(r.url()))requests.push(r.url())};page.on('request',record);
    await observe(base.replace('</body>',iconModule+'</body>'));
    assert.deepEqual(requests,[],'默认图标不联网');assert.match(await page.evaluate(()=>icon('Trend')),/^<svg/);page.off('request',record);
    // 局部打印丢文献必须失败，即使普通正文覆盖率仍高于 85%。
    const printLoss=path.join(dir,'print-loss.html');fs.writeFileSync(printLoss,base.replace(refsPattern,()=>refs).replace('</head>','<style>@media print{[data-reference-id="R12"],[data-report-field="version"]{display:none!important}}</style></head>'));
    const out=path.join(dir,'print-loss');const result=spawnSync(process.execPath,[path.join(__dirname,'qa_deck.cjs'),printLoss,out],{encoding:'utf8',env:process.env,maxBuffer:4*1024*1024});
    assert.ok(fs.existsSync(path.join(out,'audit.json')),result.stderr+result.stdout);const qa=JSON.parse(fs.readFileSync(path.join(out,'audit.json'),'utf8'));
    assert.equal(result.status,1);assert.ok(qa.errors.some(e=>/缺少完整参考条目/.test(e)),JSON.stringify(qa.errors));
    assert.ok(qa.errors.some(e=>/缺少首尾元信息/.test(e)),JSON.stringify(qa.errors));
    console.log('PASS: 真实16:9/4:3布局、完整/节选书目、去重与版本、文本转义、鼠标与键盘链接、总览/背景导航、PDF链接、隐藏/超容量/缺页/伪报/打印漏项拒绝、旧稿样式与合同兼容。');
  }finally{await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1});
