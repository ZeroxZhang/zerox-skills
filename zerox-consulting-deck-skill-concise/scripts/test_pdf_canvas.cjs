/* 实际 PDF：渐变与透明叠加必须保留颜色；两条检查路径共用同一 Canvas 提供者。 */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const canvas=require(process.env.PDF_CANVAS_MODULE||'@napi-rs/canvas');
const {render}=require('./render_pdf_pages.cjs'),{inspect}=require('./audit_pdf_geometry.cjs');
(async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'pdf-canvas-'));let browser;
 try{
  browser=await chromium.launch({channel:process.env.CHROME_CHANNEL||'chrome',headless:true});const page=await browser.newPage();
  await page.setContent('<style>@page{size:300px 160px;margin:0}body{margin:0}</style><svg width="300" height="160" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="g"><stop stop-color="#ff0000"/><stop offset="1" stop-color="#0000ff"/></linearGradient></defs><rect x="10" y="10" width="100" height="90" fill="url(#g)"/><rect x="140" y="10" width="100" height="90" fill="#ff0000"/><g opacity="0.5"><rect x="140" y="10" width="100" height="90" fill="#0000ff"/></g><text x="10" y="135" font-size="20">Gradient and opacity</text></svg>');
  const pdf=path.join(dir,'test.pdf');await page.pdf({path:pdf,preferCSSPageSize:true,printBackground:true});
  const rows=await render(pdf,path.join(dir,'pages'));assert.equal(rows.length,1);
  const bytes=fs.readFileSync(pdf),audit={pages:1,pdfPages:1,pdfArtifact:{path:pdf,pages:1,sha256:crypto.createHash('sha256').update(bytes).digest('hex')},rows:[{page:1}]};
  const geometry=await inspect(audit,path.join(dir,'geometry'));assert.equal(geometry.status,'PARTIAL','没有声明几何锚点不能冒认精度通过');assert.deepEqual(geometry.errors,[]);
  for(const file of [rows[0].path,geometry.rows[0].image]){
   const image=await canvas.loadImage(file),surface=canvas.createCanvas(image.width,image.height),ctx=surface.getContext('2d');ctx.drawImage(image,0,0);
   const pixel=(x,y)=>Array.from(ctx.getImageData(x,y,1,1).data);
   const left=pixel(15,40),right=pixel(105,40),blend=pixel(180,40);
   assert.ok(left[0]>220&&left[2]<35,JSON.stringify(left));assert.ok(right[2]>220&&right[0]<35,JSON.stringify(right));
   assert.ok(Math.abs(blend[0]-127)<=3&&blend[1]<=2&&Math.abs(blend[2]-128)<=3,JSON.stringify(blend));
  }
  console.log('PASS real PDF gradient and transparency pixels in page review and geometry audit; undeclared geometry remains PARTIAL');
 }finally{if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1});
