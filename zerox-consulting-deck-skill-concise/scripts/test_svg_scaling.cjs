/* getBBox曾正常而实际字形坐标随父级缩放偏移；必须核对字形位置而不只看元素框。 */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{pathToFileURL}=require('node:url');
const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright'),{build}=require('./build_typography_reference.cjs');
(async()=>{const out=fs.mkdtempSync(path.join(os.tmpdir(),'svg-scaling-')),file=build(out,'legacy-system'),b=await pw.chromium.launch({channel:'chrome',headless:true});try{
 const p=await b.newPage({viewport:{width:1400,height:820}});await p.goto(pathToFileURL(file).href);await p.evaluate(()=>window.deckReady);
 for(const width of [1400,800,2560]){
  await p.setViewportSize({width,height:820});await p.waitForTimeout(100);
  const gaps=await p.locator('.slide.active svg text').evaluateAll(es=>es.filter(e=>e.getAttribute('text-anchor')==='start').map(e=>({text:e.textContent,gap:Math.abs(e.getStartPositionOfChar(0).x-+e.getAttribute('x'))})));
  assert.ok(gaps.every(g=>g.gap<.05),'缩放后字形偏移: '+JSON.stringify(gaps));
 }
 console.log('PASS: 三种窗口尺寸下SVG字形与逻辑坐标一致');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
