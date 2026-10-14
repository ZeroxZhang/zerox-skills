/* 双格式交付回归：页数门禁、离线下载、字节一致、状态保持与打印入口。 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');
const {packageDelivery}=require('./package_delivery.cjs');
let pw;try{pw=require('playwright')}catch(error){const modulePath=process.env.PLAYWRIGHT_MODULE||process.env.PLAYWRIGHT_PATH;if(!modulePath)throw Error('请安装playwright或设置PLAYWRIGHT_MODULE');pw=require(modulePath)}
const digest=value=>crypto.createHash('sha256').update(value).digest('hex');

(async()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'deck-delivery-test-'));
  const browser=await pw.chromium.launch({channel:process.env.CHROME_CHANNEL||'chrome',headless:true});
  try{
    const source=path.resolve(__dirname,'../assets/reference_deck.html');
    const sourcePage=await browser.newPage({viewport:{width:1400,height:820}});
    await sourcePage.goto(pathToFileURL(source).href,{waitUntil:'networkidle'});
    await sourcePage.evaluate(()=>window.deckReady);
    const pdf=path.join(dir,'validated.pdf');
    await sourcePage.pdf({path:pdf,printBackground:true,preferCSSPageSize:true});
    const onePage=path.join(dir,'one-page.pdf');
    await sourcePage.pdf({path:onePage,printBackground:true,preferCSSPageSize:true,pageRanges:'1'});
    const htmlBuffer=fs.readFileSync(source),pdfBuffer=fs.readFileSync(pdf);
    const audit={
      input:source,pages:9,pdfPages:9,geometryStatus:'PASS',errors:[],
      pagesCheck:{status:'PASS',inventory:{pages:9,forms:{},families:{},distinctForms:0,annotations:0,regions:0,longestRun:0,runs:[]}},
      htmlArtifact:{path:source,bytes:htmlBuffer.length,sha256:digest(htmlBuffer)},
      pdfArtifact:{path:pdf,bytes:pdfBuffer.length,sha256:digest(pdfBuffer),pages:9}
    };
    fs.writeFileSync(path.join(dir,'audit.json'),JSON.stringify(audit));
    assert.throws(()=>packageDelivery({htmlFile:source,pdfFile:onePage,outputDir:path.join(dir,'bad')}),/拒绝打包不同版本/);
    assert.throws(()=>packageDelivery({htmlFile:source,pdfFile:pdf,auditFile:path.join(dir,'missing-audit.json'),outputDir:path.join(dir,'bad')}),/缺少 S7 audit/);
    const failedAudit=path.join(dir,'failed-audit.json');fs.writeFileSync(failedAudit,JSON.stringify({...audit,geometryStatus:'FAIL'}));
    assert.throws(()=>packageDelivery({htmlFile:source,pdfFile:pdf,auditFile:failedAudit,outputDir:path.join(dir,'bad')}),/验收未通过/);
    // 逐页形式声明缺失时不能正式交付，只能用预览。
    const noPagesAudit=path.join(dir,'no-pages-audit.json');fs.writeFileSync(noPagesAudit,JSON.stringify({...audit,pagesCheck:{status:'NOT_PROVIDED',reason:'夹具'}}));
    assert.throws(()=>packageDelivery({htmlFile:source,pdfFile:pdf,auditFile:noPagesAudit,outputDir:path.join(dir,'bad')}),/逐页形式声明/);
    const failedPagesAudit=path.join(dir,'failed-pages-audit.json');fs.writeFileSync(failedPagesAudit,JSON.stringify({...audit,pagesCheck:{status:'FAIL',errors:['第3页 data-form 与 pages.json 不一致']}}));
    assert.throws(()=>packageDelivery({htmlFile:source,pdfFile:pdf,auditFile:failedPagesAudit,outputDir:path.join(dir,'bad')}),/逐页形式声明/);
    assert.equal(packageDelivery({htmlFile:source,pdfFile:pdf,auditFile:noPagesAudit,outputDir:path.join(dir,'no-pages-preview'),preview:true,baseName:'no-pages'}).status,'preview');
    const changedHtml=path.join(dir,'changed.html');fs.writeFileSync(changedHtml,fs.readFileSync(source,'utf8').replace('<title>','<title>已修改'));
    const changedHtmlAudit=path.join(dir,'changed-html-audit.json');fs.writeFileSync(changedHtmlAudit,JSON.stringify({...audit,input:changedHtml,htmlArtifact:{...audit.htmlArtifact,path:changedHtml}}));
    assert.throws(()=>packageDelivery({htmlFile:changedHtml,pdfFile:pdf,auditFile:changedHtmlAudit,outputDir:path.join(dir,'bad')}),/HTML 在 S7 验收后已修改/);
    assert.throws(()=>packageDelivery({htmlFile:changedHtml,pdfFile:pdf,outputDir:path.join(dir,'bad')}),/对应另一份 HTML/);
    const changedPdf=path.join(dir,'changed.pdf');fs.writeFileSync(changedPdf,Buffer.concat([pdfBuffer,Buffer.from('\n')]));
    const changedPdfAudit=path.join(dir,'changed-pdf-audit.json');fs.writeFileSync(changedPdfAudit,JSON.stringify({...audit,pdfArtifact:{...audit.pdfArtifact,path:changedPdf}}));
    assert.throws(()=>packageDelivery({htmlFile:source,pdfFile:changedPdf,auditFile:changedPdfAudit,outputDir:path.join(dir,'bad')}),/PDF 不是 S7 验收产物/);

    const reviewFile=path.join(dir,'review.json');
    const review={status:'complete',reviewer:'自动测试夹具，不代表实际目视',independence:'author',htmlSha256:audit.htmlArtifact.sha256,pdfSha256:audit.pdfArtifact.sha256,checks:{analysis:{status:'not_applicable',basis:'运行契约测试夹具'},evidence:{status:'not_applicable',basis:'运行契约测试夹具'},visual:{status:'pass',basis:'模拟状态，仅用于测试校验行为'}},issues:[]};
    const opts={htmlFile:source,pdfFile:pdf,outputDir:path.join(dir,'review-tests')};
    assert.throws(()=>packageDelivery(opts),/缺少成稿 review/);
    const preview=packageDelivery({...opts,preview:true});
    assert.equal(preview.status,'preview');assert.match(preview.html,/-preview\.html$/);
    assert.match(fs.readFileSync(preview.html,'utf8'),/<title>预览 · /);
    const variedHtml=fs.readFileSync(source,'utf8').replace('<head>','<HEAD data-build="test">').replace('<title>','<TITLE lang="zh-CN">');
    const variedSource=path.join(dir,'varied.html');fs.writeFileSync(variedSource,variedHtml);
    const variedAudit=path.join(dir,'varied-audit.json');fs.writeFileSync(variedAudit,JSON.stringify({...audit,input:variedSource,htmlArtifact:{...audit.htmlArtifact,path:variedSource,sha256:digest(variedHtml)}}));
    const varied=packageDelivery({...opts,htmlFile:variedSource,auditFile:variedAudit,outputDir:path.join(dir,'varied'),preview:true});
    const variedOutput=fs.readFileSync(varied.html,'utf8');assert.match(variedOutput,/<meta name="deck-delivery-status" content="preview">/);assert.match(variedOutput,/<TITLE lang="zh-CN">预览 · /);
    assert.throws(()=>packageDelivery({...opts,auditFile:failedAudit,preview:true,baseName:'failed-preview'}),/工程验收未通过/);
    for(const [mutation,pattern] of [
      [{...review,htmlSha256:'old'},/旧版/],
      [{...review,checks:{...review.checks,visual:{status:'not_applicable',basis:'未看图'}}},/visual/],
      [{...review,checks:{...review.checks,evidence:{status:'fail',basis:'数据待核'}}},/evidence/],
      [{...review,issues:[{severity:'major',status:'open',description:'主图缺失'}]},/未解决/],
      [{...review,reviewer:''},/审查者/]
    ]){fs.writeFileSync(reviewFile,JSON.stringify(mutation));assert.throws(()=>packageDelivery(opts),pattern);}
    fs.writeFileSync(reviewFile,JSON.stringify({...review,issues:[{severity:'minor',status:'open',description:'不影响阅读的样式偏好'}]}));
    const allowedMinor=packageDelivery({...opts,baseName:'minor'});assert.equal(allowedMinor.status,'complete');
    fs.writeFileSync(reviewFile,JSON.stringify(review));

    const result=packageDelivery({htmlFile:source,pdfFile:pdf,outputDir:path.join(dir,'delivery'),baseName:'董事会报告'});
    assert.equal(result.pages,9);
    assert.match(execFileSync('pdfinfo',[result.pdf],{encoding:'utf8'}),/Pages:\s+9/);
    assert.throws(()=>packageDelivery({htmlFile:source,pdfFile:pdf,outputDir:path.join(dir,'delivery'),baseName:'董事会报告'}),/已存在/);
    packageDelivery({htmlFile:source,pdfFile:pdf,outputDir:path.join(dir,'delivery'),baseName:'董事会报告',force:true});

    const page=await browser.newPage({acceptDownloads:true,viewport:{width:1400,height:820}}),requests=[],errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text())});
    await page.route('**/*',route=>/^https?:/.test(route.request().url())?(requests.push(route.request().url()),route.abort()):route.continue());
    await page.goto(pathToFileURL(result.html).href+'#3',{waitUntil:'networkidle'});
    await page.evaluate(()=>window.deckReady);
    assert.equal(await page.locator('#download-pdf').isVisible(),true);
    assert.equal(await page.locator('#download-pdf').isEnabled(),true);
    assert.equal(await page.locator('#print-pdf').textContent(),'打印 / 另存 PDF');
    assert.equal(await page.locator('#deck-pdf-payload').getAttribute('data-sha256'),result.pdfSha256);
    const before=await page.evaluate(()=>({hash:location.hash,overview:document.body.classList.contains('overview')}));
    const event=page.waitForEvent('download');
    await page.locator('#download-pdf').click();
    const download=await event,downloaded=path.join(dir,'downloaded.pdf');
    await download.saveAs(downloaded);
    assert.equal(download.suggestedFilename(),'董事会报告.pdf');
    assert.deepEqual(fs.readFileSync(downloaded),fs.readFileSync(result.pdf));
    assert.deepEqual(await page.evaluate(()=>({hash:location.hash,overview:document.body.classList.contains('overview')})),before);
    assert.equal(digest(fs.readFileSync(downloaded)),result.pdfSha256);
    assert.equal(requests.length,0);
    await page.evaluate(()=>{window.print=()=>{window.__printRequested=true}});
    await page.locator('#print-pdf').click();
    assert.equal(await page.evaluate(()=>window.__printRequested),true);
    await page.emulateMedia({media:'print'});
    assert.equal(await page.locator('#deck-actions').evaluate(e=>getComputedStyle(e).display),'none');
    assert.deepEqual(errors,[]);
    console.log('PASS: HTML + PDF 双格式、S7审计/页数/覆盖门禁、离线一键下载、字节一致、打印隐藏与状态保持。临时产物已清理。');
  }finally{await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1});
