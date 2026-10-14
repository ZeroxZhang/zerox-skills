const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),themes=require('../assets/deck-themes.js'),kit=require('../assets/exhibit-kit.js');
const lum=h=>{const a=h.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return a[0]*.2126+a[1]*.7152+a[2]*.0722;};
const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
assert.equal(themes.get().id,'mckinsey');assert.throws(()=>themes.get('bain'));assert.throws(()=>themes.get('__proto__'));
let keys,geometry;
for(const id of themes.ids){
 const t=themes.get(id),v=t.tokens;assert.deepEqual(Object.keys(v).sort(),keys||Object.keys(v).sort());keys=Object.keys(v).sort();
 for(const val of Object.values(v))assert.match(val,/^#[0-9A-F]{6}$/);
 for(const [fg,bg] of [['on-brand','brand'],['on-accent','accent'],['ink','page-bg'],['gray-1','page-bg'],['gray-2','page-bg'],['ink','selected'],['gray-2','selected'],['good','good-soft'],['risk','risk-soft'],['caution','caution-soft']])assert.ok(ratio(v[fg],v[bg])>=4.5,`${id} ${fg}/${bg}`);
 for(let i=1;i<5;i++)assert.ok(lum(v['seq-'+i])>lum(v['seq-'+(i+1)]),id+'色阶不单调');
 t.tokens.accent='#000000';assert.notEqual(themes.get(id).tokens.accent,'#000000');
 const svg=kit.waterfall({palette:themes.palette(id),items:[{label:'起点',type:'total',value:10},{label:'增',type:'delta',value:3},{label:'减',type:'delta',value:-5},{label:'终点',type:'subtotal'}]});
 assert.ok(svg.includes(v['delta-positive'])&&svg.includes(v['delta-negative']));
 const shapes=svg.replace(/#[0-9a-f]{6}/ig,'COLOR');assert.equal(shapes,geometry||shapes);geometry=shapes;
 const heat=kit.heatmap({palette:themes.palette(id),rows:['样本'],columns:['低','高'],values:[[0,100]],domain:[0,100]});
 assert.ok(heat.includes('data-value="100"'));
 const html=themes.apply('<html><head></head><body></body></html>',id);assert.ok(html.includes('data-theme="'+id+'"'));assert.equal((themes.apply(html,id).match(/id="deck-theme"/g)||[]).length,1);
}
const assets=path.resolve(__dirname,'../assets');const engine=fs.readFileSync(path.join(assets,'deck_engine.html'),'utf8');assert.ok(engine.includes('<style id="deck-theme">'+themes.css()+'</style>'),'默认引擎快照漂移');
const source=fs.readFileSync(path.join(assets,'exhibit-kit.js'),'utf8');assert.ok(source.includes('const p0 = '+JSON.stringify(themes.palette())+';'),'组件默认快照漂移');
console.log('3 themes PASS: selection, isolation, contrast, monotonic scales, geometry, default snapshots');
