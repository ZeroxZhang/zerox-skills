/* 从唯一配置生成源模板的本地字体样式；成稿通过 pack_fonts 内嵌子集。 */
const fs=require('node:fs'),path=require('node:path'),type=require('../assets/deck-typography.js');
const root=path.resolve(__dirname,'../assets'),manifest=require('../assets/fonts/manifest.json');
fs.writeFileSync(path.join(root,'fonts/deck-fonts.css'),type.fontCSS(manifest.faces,f=>f.file)+'\n');
const file=path.join(root,'deck_engine.html');let html=fs.readFileSync(file,'utf8');
const tag='<style id="deck-typography-style">'+type.css(type.defaultId)+'</style>';
html=html.replace(/data-typography="[^"]*"/,'data-typography="'+type.defaultId+'"').replace(/data-typography-version="[^"]*"/,'data-typography-version="'+type.version+'"');
html=html.replace(/<style id="deck-typography-style">[\s\S]*?<\/style>/g,'').replace('</head>',tag+'\n</head>');
fs.writeFileSync(file,html);console.log('字体 CSS 与引擎配置已同步');
