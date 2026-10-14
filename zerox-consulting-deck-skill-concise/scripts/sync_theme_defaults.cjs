/* 从唯一注册表生成可独立打开的默认快照；修改主题后运行。 */
const fs=require('node:fs'),path=require('node:path'),themes=require('../assets/deck-themes.js');
const base=path.resolve(__dirname,'../assets');
const engine=path.join(base,'deck_engine.html');fs.writeFileSync(engine,themes.apply(fs.readFileSync(engine,'utf8'),'mckinsey'));
const kit=path.join(base,'exhibit-kit.js');fs.writeFileSync(kit,fs.readFileSync(kit,'utf8').replace(/  const p0 = .*?;\n/,'  const p0 = '+JSON.stringify(themes.palette('mckinsey'))+';\n'));
