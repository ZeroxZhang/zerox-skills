/* 只同步 V10 封面示例和局部样式，其他示例的页序、内容与尺寸保持原样。 */
const fs=require('node:fs'),path=require('node:path'),bookends=require('./bookends.cjs');
const file=path.resolve(__dirname,'../assets/deck_engine.html');
let html=fs.readFileSync(file,'utf8');
const cover=bookends.cover({title:'收入下滑的诊断\n与渠道重构建议',type:'董事会材料 · 版式示例',client:'北辰食品（虚构案例）',date:'2026-09-05',subtitle:'合成数据仅用于展示分析与页面结构'}).replace('class="slide cover"','class="slide cover active"');
const pattern=/<section class="slide cover[^>]*>[\s\S]*?<\/section>/;
if(!pattern.test(html))throw Error('未找到引擎封面，请检查源文件结构');
html=html.replace(pattern,()=>cover);
fs.writeFileSync(file,bookends.applyStyles(html,{kind:'collection'}));
console.log('首尾样式与封面示例已同步；引擎保持组件集合。');
