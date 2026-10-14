/* 回归：500曾被按400测量，graphic.font简写曾绕过统一字体导致测量/显示不一致。 */
const assert=require('node:assert/strict'),{measurer}=require('./font_metrics.cjs'),{render}=require('./render_echarts_svg.cjs');
const measure=measurer('serif-report');
assert.ok(Math.abs(measure('Revenue gross margin',"500 18px 'Deck Inter'").width-191.49609375)<.001,'500字重必须用Inter500真实字形');
assert.ok(Math.abs(measure('1111.00',"400 18px 'Deck Inter'").width-measure('8888.00',"400 18px 'Deck Inter'").width)<.001,'SSR也须启用等宽数字');
const result=render({option:{graphic:[{type:'text',x:20,y:40,style:{text:'Revenue 1111.00',font:'500 18px Arial'}}]}});
assert.match(result.pages[0].svg,/Deck Inter/);assert.doesNotMatch(result.pages[0].svg,/Arial/,'font简写不得绕过统一字体配置');
assert.throws(()=>render({option:{graphic:[{type:'text',x:20,y:40,style:{text:'Revenue',font:'italic 18px Arial'}}]}}),/斜体/);
let installed;const fake={setPlatformAPI(api){installed=api.measureText;}};const {install}=require('./font_metrics.cjs');install(fake,'serif-report');const locked=installed;assert.equal(install(fake,'legacy-system'),'legacy-estimate');assert.notEqual(installed,locked,'legacy必须重置测量函数');assert.ok(installed('遗留字形 Ċ','14px Arial').width>0);
console.log('PASS: 真实500字重、tnum、font简写归一化与未提供斜体拒绝');
