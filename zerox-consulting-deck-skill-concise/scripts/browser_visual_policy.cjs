/* 在真实浏览器中调用；函数自包含，可由 Playwright 序列化。诊断不作审美 PASS。
   第二参数是本次的密度档位：只有"空"到什么程度、由谁说，随档位变；判据本身不变。
   封面的留白是设计，正文的留白是成本——所以档位只作用于正文页的展品区。 */
function inspectSlide(slide, policy) {
  const errors = [], warnings = [], findings = [];
  const settings = policy && typeof policy === 'object' ? policy : {};
  const compact = settings.density === 'compact';
  const role = (slide.dataset && slide.dataset.pageRole) || slide.getAttribute('data-page-role') || '';
  const exempt = settings.exemptRoles || ['cover', 'back-cover', 'references'];
  const densityApplies = compact && !exempt.includes(role);
  const sr = slide.getBoundingClientRect(), scale = sr.width / (slide.offsetWidth || sr.width) || 1;
  const bounds = el => { const r = el.getBoundingClientRect(); return { x: (r.left-sr.left)/scale, y: (r.top-sr.top)/scale, width:r.width/scale, height:r.height/scale }; };
  const shown = el => { if (!el.getClientRects().length) return false; for(let n=el;n&&n.nodeType===1;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility!=='visible'||+s.opacity===0)return false;}const r=el.getBoundingClientRect();return r.width>0&&r.height>0; };
  const label = el => { const parts=[];for(let n=el;n&&n!==slide;n=n.parentElement){const tag=n.localName;parts.unshift(`${tag}:nth-child(${Array.prototype.indexOf.call(n.parentElement.children,n)+1})`);}return parts.join(' > ')||':scope'; };
  const add = (list,code,el,message,extra={}) => list.push({code,selector:label(el),message,bounds:bounds(el),...extra});
  const painted = c => c && c!=='transparent' && !/rgba?\([^)]*[,/]\s*0(?:\.0+)?\s*\)$/.test(c);
  const saturated = c => {const m=c.match(/[\d.]+/g);return m&&m.length>=3&&Math.max(...m.slice(0,3).map(Number))-Math.min(...m.slice(0,3).map(Number))>24;};
  const structural = el => el.matches('h1,h2,h3,h4,h5,h6,table,thead,tbody,tfoot,tr,td,th,hr,.source,.slide__title,.slide__lead,.slide__tracker,.slide__page,.bookend-footer') || el===slide;
  // 仅豁免真实页头下方的 quiet 细线：结构、位置、尺寸与低对比外观共同匹配，类名本身不是通行证。
  const quietHeaderRule = (el,pseudo,p) => {
    const header=slide.querySelector(':scope > .slide__header'),body=slide.querySelector(':scope > .slide__body');
    if(el!==header||pseudo!=='::after'||!body||!header.querySelector('.slide__title')||!(header.compareDocumentPosition(body)&Node.DOCUMENT_POSITION_FOLLOWING))return false;
    const frame=slide.getAttribute('data-frame')||document.documentElement.getAttribute('data-frame');
    if(frame!=='quiet'||slide.dataset.frameBoundary!=='line'||p.position!=='absolute'||Math.abs(parseFloat(p.height)-1)>.1||parseFloat(p.left)!==0||parseFloat(p.right)!==0||parseFloat(p.bottom)>=0||parseFloat(p.bottom)<-16||parseFloat(p.width)<slide.clientWidth*.75)return false;
    if(p.backgroundImage!=='none'||p.boxShadow!=='none'||['Top','Right','Bottom','Left'].some(side=>parseFloat(p['border'+side+'Width'])>0))return false;
    // Canvas 在离屏内只解析颜色；不读取页面像素、不改变报告 DOM。
    const ctx=document.createElement('canvas').getContext('2d');ctx.fillStyle=p.backgroundColor;ctx.fillRect(0,0,1,1);const rgb=[...ctx.getImageData(0,0,1,1).data].slice(0,3);
    return Math.max(...rgb)-Math.min(...rgb)<=24&&Math.min(...rgb)>=140;
  };
  const nodes=[...slide.querySelectorAll('*')].filter(shown);
  const textModule = el => el && !el.closest('svg,canvas,table') && !structural(el) && (el.textContent||'').trim().length>0 && bounds(el).width>=70 && bounds(el).height>=32;
  for (const el of nodes) {
    if(el.closest('svg')) continue;
    const s=getComputedStyle(el), b=bounds(el);
    if(textModule(el)) {
      const sides=['Top','Right','Bottom','Left'].map(side=>({side,width:parseFloat(s[`border${side}Width`]),color:s[`border${side}Color`],style:s[`border${side}Style`]}));
      const visible=sides.filter(x=>x.width>0&&x.style!=='none'&&painted(x.color));
      // 整圈普通框线、薄中性分隔线不是色条模块；粗单边或有色单边属于可识别禁用外观。
      const accent=visible.filter(x=>(x.width>=2||saturated(x.color))&&x.width<=16);
      if(accent.length && !(visible.length===4&&visible.every(x=>x.width===visible[0].width&&x.color===visible[0].color)))
        add(errors,'V-DECORATIVE-EDGE',el,'文字或数字模块使用装饰性边条，应重排为无边条表达。',{sides:accent.map(x=>x.side.toLowerCase())});
      // 常见零模糊、零扩散的 inset 阴影模拟边条；复杂阴影保留人工检查范围。
      if(s.boxShadow!=='none') {
        const shadows=s.boxShadow.split(/,(?![^()]*\))/);
        for(const shadow of shadows){const nums=shadow.replace(/rgba?\([^)]*\)/g,'').match(/-?[\d.]+px/g)||[];const [x,y,blur=0,spread=0]=nums.map(parseFloat);if(shadow.includes('inset')&&blur===0&&spread===0&&((Math.abs(x)>=2&&Math.abs(x)<=16&&y===0)||(Math.abs(y)>=2&&Math.abs(y)<=16&&x===0))){add(errors,'V-DECORATIVE-SHADOW',el,'模块以内嵌阴影模拟装饰边条。');break;}else add(findings,'V-SHADOW-MANUAL',el,'此阴影路径需实际看图确认是否构成装饰边条。');}
      }
      if(s.backgroundImage!=='none') add(findings,'V-BACKGROUND-MANUAL',el,'背景图像或渐变的视觉用途需实际看图，未自动判定是否模拟边条。');
      // 背景框真实文字结束后仍有大量空置，只作为定位线索，不使用填充率判定。
      if(painted(s.backgroundColor)&&!el.querySelector('svg,canvas,img,video,table')){
        const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT), rects=[];let n;
        while((n=walker.nextNode())){if(!n.textContent.trim()||!shown(n.parentElement))continue;const range=document.createRange();range.selectNodeContents(n);rects.push(...range.getClientRects());}
        if(rects.length){
          const bottom=Math.max(...rects.map(r=>r.bottom));const gap=(el.getBoundingClientRect().bottom-bottom)/scale;
          if(gap>72&&b.height>140){
            const message=`模块文字下方约 ${Math.round(gap)}px 无内容，需检查是否被轨道伸展成空框。`;
            // 空到超过模块自身四分之一、且绝对值过百像素，才不像是"上对齐的单元格留白"。
            if(densityApplies&&gap>120&&gap>b.height*.25)add(errors,'V-EMPTY-MODULE',el,message+`（密度档位 compact：占模块高度 ${Math.round(gap/b.height*100)}%，须重排或给出该留白的功能）`,{gap:Math.round(gap),moduleShare:Number((gap/b.height).toFixed(3))});
            else add(warnings,'V-EMPTY-MODULE',el,message,{gap:Math.round(gap)});
          }
        }
      }
    }
    if(textModule(el)) for(const pseudo of ['::before','::after']) {
      const p=getComputedStyle(el,pseudo);if(p.content==='none'||p.content==='normal'||p.display==='none'||p.visibility!=='visible'||+p.opacity===0)continue;
      if(quietHeaderRule(el,pseudo,p)){add(findings,'V-QUIET-HEADER',el,'已识别真实页头下方的低对比 quiet 母版细线。');continue;}
      const w=parseFloat(p.width),h=parseFloat(p.height),thin=(w>0&&w<=16&&h>=32)||(h>0&&h<=16&&w>=70);
      const edge=(parseFloat(p.left)===0||parseFloat(p.right)===0||parseFloat(p.top)===0||parseFloat(p.bottom)===0);
      if(thin&&edge&&painted(p.backgroundColor))add(errors,'V-DECORATIVE-PSEUDO',el,`${pseudo} 在文字模块边缘模拟装饰边条。`,{pseudo});
      else if(p.backgroundImage!=='none'||p.boxShadow!=='none'||['Top','Right','Bottom','Left'].some(k=>parseFloat(p[`border${k}Width`])>0))add(findings,'V-PSEUDO-MANUAL',el,`${pseudo} 的复杂绘制路径需实际看图补查。`,{pseudo});
    }
    // 无字窄色块紧贴有字模块边缘；不匹配独立图表数据条或坐标轴。
    if(!(el.textContent||'').trim()&&!el.children.length&&painted(s.backgroundColor)&&textModule(el.parentElement)&&s.position==='absolute') {
      const p=bounds(el.parentElement), thin=(b.width>0&&b.width<=16&&b.height>=p.height*.8)||(b.height>0&&b.height<=16&&b.width>=p.width*.8);
      const edge=Math.abs(b.x-p.x)<1||Math.abs(b.y-p.y)<1||Math.abs(b.x+b.width-p.x-p.width)<1||Math.abs(b.y+b.height-p.y-p.height)<1;
      if(thin&&edge)add(errors,'V-DECORATIVE-STRIP',el,'绝对定位窄色块贴在文字模块边缘，形成装饰边条。');
    }
  }
  for(const el of nodes.filter(el=>el.matches('svg,canvas,img,video,object,iframe'))) add(findings,'V-RASTER-VECTOR-MANUAL',el,'SVG、位图及嵌入内容的装饰边条与视觉均衡须结合整页和实际 PDF 人工检查；此检查器不证明其合规。');
  const body=slide.querySelector('.slide__body');
  if(body&&shown(body)){
    /* 展品区实际内容的下边界。文字必须按**文本节点**量，不能只看"没有子元素的元素"：
       一段以行内标签开头的多行说明（常见写法 <strong>口径提示</strong>后面接正文）里，
       标签后面的裸文本不是元素，于是底边停在标签那一行，凭空多出一段空置；
       实测同一段文字包进 <span> 与否，虚报量正好是标签之后的行高，页越长虚报越多。
       本文件里 V-EMPTY-MODULE 那段一直是用文本节点量的，这里对齐同一种量法。 */
    const contentBottom=()=>{
      let bottom=-Infinity;
      for(const el of body.querySelectorAll('svg,canvas,img,table'))if(shown(el)&&!el.closest('.source')){const b=bounds(el);bottom=Math.max(bottom,b.y+b.height);}
      const walker=document.createTreeWalker(body,NodeFilter.SHOW_TEXT);let node;
      while((node=walker.nextNode())){
        if(!node.nodeValue.trim()||!node.parentElement||!shown(node.parentElement)||node.parentElement.closest('.source'))continue;
        const range=document.createRange();range.selectNodeContents(node);
        for(const rect of range.getClientRects())bottom=Math.max(bottom,(rect.bottom-sr.top)/scale);
      }
      return bottom;
    };
    const leaves=[...body.querySelectorAll('*')].filter(el=>shown(el)&&!el.closest('.source')&&(el.matches('svg,canvas,img,table')||(!el.children.length&&(el.textContent||'').trim())));
    const br=bounds(body);
    const lastBottom=contentBottom();
    if(leaves.length&&lastBottom>-Infinity){
      const bottom=lastBottom,gap=br.y+br.height-bottom;
      if(gap>120){
        const message=`正文实际对象下方约 ${Math.round(gap)}px 剩余空间（占展品区 ${Math.round(gap/br.height*100)}%），需在整页检查其分组、强调或节奏用途。`;
        // 上一条只量"最后一个对象下方"，把空白推进模块之间就能躲开；所以档位从"占比"判，不只看绝对值。
        if(densityApplies&&gap>br.height*.2)add(errors,'V-BODY-REMAINDER',body,message+`（密度档位 compact：超过展品区 20%，须收短模块或重新分配整页空间）`,{gap:Math.round(gap),bodyShare:Number((gap/br.height).toFixed(3))});
        else add(warnings,'V-BODY-REMAINDER',body,message,{gap:Math.round(gap),bodyShare:Number((gap/br.height).toFixed(3))});
      }
    }
    // 模块之间的空白：只量末对象下方的话，用 space-between 把空白挪到中间就规避了。
    const modules=[...body.children].filter(el=>shown(el)&&!el.classList.contains('source'));
    if(modules.length>1){
      let largest=0,where=null;
      for(let i=1;i<modules.length;i++){const prev=bounds(modules[i-1]),cur=bounds(modules[i]);const gap=cur.y-(prev.y+prev.height);if(gap>largest){largest=gap;where=modules[i];}}
      if(largest>96&&where){
        const message=`相邻模块之间约有 ${Math.round(largest)}px 空白（占展品区 ${Math.round(largest/br.height*100)}%），需在整页检查是分组节奏还是被撑开的空档。`;
        if(densityApplies&&largest>br.height*.2)add(errors,'V-MODULE-GAP',where,message+'（密度档位 compact：模块间空白不是留白的正当去处）',{gap:Math.round(largest),bodyShare:Number((largest/br.height).toFixed(3))});
        else add(warnings,'V-MODULE-GAP',where,message,{gap:Math.round(largest),bodyShare:Number((largest/br.height).toFixed(3))});
      }
    }
    const source=slide.querySelector('.source');if(source&&shown(source)){const top=bounds(source).y;for(const el of leaves){const b=bounds(el);if(b.y<top&&b.y+b.height>top+1)add(warnings,'V-SOURCE-COLLISION',el,'正文对象进入来源区域，请检查来源安全区与关键限定。');}}
  }
  // 分隔页没有 .slide__body，上面所有检查都落空；它因此长期落在治理盲区里。这里单独量一次。
  if(!body||!shown(body)){
    const content=[...slide.querySelectorAll('*')].filter(el=>shown(el)&&!el.closest('.source')&&!structural(el)&&((el.textContent||'').trim().length>0||el.matches('svg,canvas,img')));
    if(content.length){
      const top=Math.min(...content.map(el=>bounds(el).y)),bottom=Math.max(...content.map(el=>{const b=bounds(el);return b.y+b.height;}));
      const used=(bottom-top)/sr.height;
      if(used<.35)add(warnings,'V-PAGE-VOID',slide,`本页没有展品区，可见内容只占页面高度 ${Math.round(used*100)}%（约 ${Math.round((1-used)*100)}% 为空白）。功能页（封面/封底/参考资料）按设计留白即可；内容页与分隔页要在 warningReview 里说明这段空白承载什么。`,{usedShare:Number(used.toFixed(3)),role:role||'unset'});
    }
  }
  findings.push({code:'V-COVERAGE',message:'自动范围：可见 HTML 模块的典型边框、简单伪元素/窄块、零模糊 inset 阴影，以及空置线索（模块内、末对象下方、模块之间、无展品区页的整页空白）。小于70×32px的文字装饰、复杂绘制、未声明对齐关系和整页重心仍须逐页实际审查；无错误不代表视觉通过。'+(densityApplies?'密度档位 compact 已生效：展品区的上述空白按占比升级为错误，功能页按设计豁免。':'密度档位未启用：空置只作为诊断线索，不阻塞。')});
  return {errors,warnings,findings};
}
/* 档位只有一个来源：任务合同。缺省按 compact——"紧凑"是本技能的默认交付形态，
   要松一点的稿子必须显式写 normal，而不是靠不写来默认松。 */
const DENSITY_DEFAULT='compact';
const policyFor=taskContract=>({density:(taskContract&&taskContract.densityPolicy)||DENSITY_DEFAULT,exemptRoles:['cover','back-cover','references']});
module.exports={inspectSlide,policyFor,DENSITY_DEFAULT};
