// Injected into pages to draw numbered red boxes + yellow highlights for evidence screenshots.
// API: __mk.text(str,{hl,up,visible}) | __mk.wa() floating chat/WhatsApp button (or any small fixed bottom-right widget) | __mk.btn(startsWithText) | __mk.sel(cssSelector) | __mk.box(el)

window.__mk = {
  n: 1,
  css() { if (document.getElementById('__mkc')) return; const s = document.createElement('style'); s.id='__mkc';
    s.textContent = `.__box{position:absolute;z-index:2147483646;border:4px solid #e11d48;border-radius:8px;pointer-events:none;box-shadow:0 0 0 3px rgba(255,255,255,.7)}
    .__b{position:absolute;z-index:2147483647;background:#e11d48;color:#fff;font:700 15px/1 Arial;padding:5px 9px;border-radius:999px;box-shadow:0 2px 6px rgba(0,0,0,.35)}
    .__hl{background:#fde047 !important;color:#111 !important;border-radius:2px}`; document.head.appendChild(s); },
  box(el, pad=4) { this.css(); const r = el.getBoundingClientRect(); const fixed = [...function*(e){while(e){yield e;e=e.parentElement}}(el)].some(e=>getComputedStyle(e).position==='fixed');
    const d = document.createElement('div'); d.className='__box'; d.style.position = fixed?'fixed':'absolute';
    const ox = fixed?0:scrollX, oy = fixed?0:scrollY;
    d.style.left=(r.left+ox-pad)+'px'; d.style.top=(r.top+oy-pad)+'px'; d.style.width=(r.width+pad*2)+'px'; d.style.height=(r.height+pad*2)+'px';
    const b = document.createElement('div'); b.className='__b'; b.textContent=this.n++; b.style.position=d.style.position;
    b.style.left=(r.left+ox-pad-14)+'px'; b.style.top=(r.top+oy-pad-14)+'px';
    document.body.appendChild(d); document.body.appendChild(b); return true; },
  findText(t, visibleOnly=true) { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let best=null;
    while (w.nextNode()) { const n=w.currentNode; if (n.nodeValue.toLowerCase().includes(t.toLowerCase())) { const e=n.parentElement; const r=e.getBoundingClientRect();
      if (!visibleOnly || (r.width>0 && r.height>0 && r.bottom>0 && r.top<innerHeight)) { best=n; break; } } } return best; },
  text(t, opts={}) { const n = this.findText(t, opts.visible!==false); if (!n) return false;
    if (opts.hl!==false) { try { const i=n.nodeValue.toLowerCase().indexOf(t.toLowerCase()); const rg=document.createRange(); rg.setStart(n,i); rg.setEnd(n,i+t.length); const sp=document.createElement('span'); sp.className='__hl'; rg.surroundContents(sp);} catch(e){} }
    let el = n.parentElement; if (opts.up) for (let i=0;i<opts.up;i++) el=el.parentElement;
    while (getComputedStyle(el).display==='inline' && el.parentElement) el=el.parentElement;
    return this.box(el); },
  wa() { const vis=e=>{const r=e.getBoundingClientRect();return r.width>20&&r.width<140&&r.top<innerHeight&&r.bottom>0};
    let c=[...document.querySelectorAll('a[href*="wa.me"],a[href*="whatsapp"],[class*=whatsapp],[id*=whatsapp],[class*=chat-button],[class*=chat-widget]')].filter(vis);
    if(!c.length) c=[...document.querySelectorAll('body *')].filter(e=>getComputedStyle(e).position==='fixed'&&vis(e)&&e.getBoundingClientRect().right>innerWidth*0.7&&e.getBoundingClientRect().bottom>innerHeight*0.6);
    if(!c.length) return false; return this.box(c[c.length-1]); },
  btn(t) { const c=[...document.querySelectorAll('button,a,input[type=submit]')].filter(e=>(e.innerText||e.value||'').trim().toLowerCase().startsWith(t.toLowerCase())).filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.top<innerHeight&&r.bottom>0}); if(!c.length) return false; return this.box(c[c.length-1]); },
  sel(q) { const e=[...document.querySelectorAll(q)].find(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.top<innerHeight&&r.bottom>0}); return e?this.box(e):false; }
};
