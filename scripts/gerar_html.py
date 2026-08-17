# -*- coding: utf-8 -*-
"""Gera o HTML autocontido a partir de dados.json."""

import json
import os


DADOS = os.environ.get("DADOS", "dados/dados.json")
CONSULTAS = os.environ.get("CONSULTAS", "dados/consultas.json")
SAIDA = os.environ.get("SAIDA", "index.html")

CSS = """
:root{
  --plane:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --ring:rgba(11,11,11,.10);
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100;
  --s5:#e87ba4; --s6:#008300; --s7:#4a3aa7; --s8:#e34948;
  --wash:rgba(42,120,214,.14);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]){
  --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --axis:#383835; --ring:rgba(255,255,255,.10);
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500;
  --s5:#d55181; --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --wash:rgba(57,135,229,.20);
  color-scheme:dark;
}}
:root[data-theme="dark"]{
  --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --axis:#383835; --ring:rgba(255,255,255,.10);
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500;
  --s5:#d55181; --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --wash:rgba(57,135,229,.20);
  color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);
  font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:48px 24px 96px}
header{margin-bottom:40px}
h1{font-size:clamp(28px,4.2vw,42px);line-height:1.15;letter-spacing:-.02em;margin:0 0 12px}
.sub{color:var(--ink-2);font-size:17px;max-width:64ch;margin:0}
.kicker{font-size:12px;letter-spacing:.10em;text-transform:uppercase;color:var(--muted);
  margin:0 0 10px;font-weight:600}
section{margin:56px 0 0}
h2{font-size:22px;letter-spacing:-.01em;margin:0 0 6px}
h2+p.note{margin:0 0 22px}
p.note{color:var(--ink-2);font-size:14.5px;max-width:72ch}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:14px;
  padding:22px 22px 14px}
.tiles{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin:28px 0 0}
.tile{background:var(--surface);border:1px solid var(--ring);border-radius:14px;padding:18px}
.tile .v{font-size:32px;line-height:1.1;letter-spacing:-.02em;font-weight:600}
.tile .l{font-size:13px;color:var(--ink-2);margin-top:6px}
.tile .h{font-size:12px;color:var(--muted);margin-top:2px}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;margin:14px 0 4px;font-size:13px;color:var(--ink-2)}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend i{width:11px;height:11px;border-radius:3px;display:inline-block;flex:0 0 auto}
.legend button.chip{font:inherit;font-size:13px;line-height:1.3;display:inline-flex;align-items:center;
  gap:7px;color:var(--ink-2);background:var(--surface);border:1px solid var(--ring);
  border-radius:999px;padding:5px 12px;cursor:pointer;transition:opacity .12s,border-color .12s}
.legend button.chip:hover{border-color:var(--muted)}
.legend button.chip[aria-pressed="false"]{opacity:.42;text-decoration:line-through}
.legend button.chip[aria-pressed="false"] i{filter:grayscale(1)}
.legend button.chip.reset{color:var(--muted);border-style:dashed}
.ctrl{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 18px;font-size:13.5px}
.ctrl button{font:inherit;font-size:13px;color:var(--ink-2);background:var(--surface);
  border:1px solid var(--ring);border-radius:999px;padding:6px 14px;cursor:pointer}
.ctrl button[aria-pressed="true"]{background:var(--ink);color:var(--surface);border-color:var(--ink)}
.chart{position:relative}
.chart svg{display:block;width:100%;height:auto;overflow:visible}
.tip{position:absolute;pointer-events:none;opacity:0;transition:opacity .12s;
  background:var(--surface);border:1px solid var(--ring);border-radius:10px;
  padding:9px 12px;font-size:13px;line-height:1.45;color:var(--ink);
  box-shadow:0 6px 24px rgba(0,0,0,.13);min-width:150px;z-index:5}
.tip b{font-weight:600}
.tip .row{display:flex;justify-content:space-between;gap:14px;color:var(--ink-2)}
.tip .row b{color:var(--ink);font-variant-numeric:tabular-nums}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:720px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--grid);vertical-align:middle}
th{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
  font-weight:600;position:sticky;top:0;background:var(--surface)}
td.num{text-align:right;font-variant-numeric:tabular-nums}
tbody tr:hover{background:color-mix(in srgb,var(--ink) 4%,transparent)}
.tag{font-size:11px;padding:2px 8px;border-radius:999px;border:1px solid var(--ring);
  color:var(--ink-2);white-space:nowrap}
.tiles.compact{margin:0 0 22px}
.tiles.compact .v{font-size:26px}
.q{color:var(--muted);font-size:12px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
ul.lim{color:var(--ink-2);font-size:14.5px;max-width:74ch;padding-left:20px}
ul.lim li{margin:8px 0}
footer{margin-top:64px;padding-top:20px;border-top:1px solid var(--grid);
  color:var(--muted);font-size:13px}
"""

JS = r"""
const D = window.__DADOS__;
const AMB = D.topicos;
const N = D.eixo.length;
const SLOT = ['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'];
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const virg = t => String(t).replace('.',',');
const fmt = v => virg(v>=100?Math.round(v):(v>=10?v.toFixed(1):v.toFixed(2)));
// rótulo de tick: inteiro quando o passo do eixo é inteiro
const fmtTick = (v,passo) => passo>=1 ? String(Math.round(v)) : virg(parseFloat(v.toFixed(2)));

function soma(lista){
  const out = new Array(N).fill(0);
  lista.forEach(t=>{ for(let i=0;i<N;i++) out[i]+=t.valores[i]; });
  return out;
}
// rótulo curto do eixo: "jan. de 2016" -> "2016"
const anos = D.eixo.map(l=>{const m=l.match(/(\d{4})/);return m?m[1]:l;});
// "1 de jan. de 2016" -> "jan/2016"
const meses = D.eixo.map(l=>{
  const m=l.match(/([a-zçã]+)\.?\s+de\s+(\d{4})/i);
  return m?`${m[1]}/${m[2]}`:l;
});

/* ---------------- gráfico de linha (consolidado) ---------------- */
const W=1000, H=340, PAD={t:18,r:22,b:34,l:46};
function eixoY(max){
  const passos=[.02,.05,.1,.2,.25,.5,1,2,5,10,20,25,50,100,200,250,500,1000,2000,5000];
  const alvo=max/5;  // 5 intervalos deixa o topo mais colado no dado
  const p=passos.find(x=>x>=alvo)||Math.ceil(alvo/1000)*1000;
  const topo=Math.ceil(max/p)*p;
  const ticks=[]; for(let v=0;v<=topo+1e-9;v+=p) ticks.push(v);
  return {topo,ticks,passo:p};
}
// escala log: piso e topo caem em passos 1-3 (…0,03 · 0,1 · 0,3 · 1 · 3…)
const PASSOS_LOG=[.001,.003,.01,.03,.1,.3,1,3,10,30,100,300,1000];
function eixoLog(max,minPos){
  const piso = [...PASSOS_LOG].reverse().find(p=>p<=minPos) || PASSOS_LOG[0];
  const topo = PASSOS_LOG.find(p=>p>=max) || PASSOS_LOG[PASSOS_LOG.length-1];
  return {piso, topo, ticks: PASSOS_LOG.filter(p=>p>=piso && p<=topo)};
}
const fmtLog = v => v>=1 ? String(v) : v.toFixed(String(v).length-2).replace('.',',');

function desenharLinha(el, serie, opts){
  opts = opts||{};
  const log = opts.escala==='log';
  const positivos = serie.filter(v=>v>0);
  const L = log ? eixoLog(Math.max(...serie)||1, Math.min(...positivos)) : null;
  const {topo,ticks,passo} = log
    ? {topo:L.topo, ticks:L.ticks, passo:null}
    : eixoY(Math.max(...serie)||1);
  const x = i => PAD.l + i*(W-PAD.l-PAD.r)/(N-1);
  const y = log
    ? v => H-PAD.b - (Math.log(Math.max(v,L.piso)/L.piso)/Math.log(L.topo/L.piso))*(H-PAD.t-PAD.b)
    : v => H-PAD.b - (v/topo)*(H-PAD.t-PAD.b);
  const linha = serie.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' ');
  const area = linha+` L ${x(N-1).toFixed(1)} ${y(0)} L ${x(0).toFixed(1)} ${y(0)} Z`;
  let g='';
  ticks.forEach(v=>{ g+=`<line x1="${PAD.l}" x2="${W-PAD.r}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}" stroke="${v?'var(--grid)':'var(--axis)'}" stroke-width="1"/>`
    +`<text x="${PAD.l-9}" y="${(y(v)+4).toFixed(1)}" text-anchor="end" font-size="11" fill="var(--muted)">${log?fmtLog(v):fmtTick(v,passo)}</text>`; });
  let anosVistos=new Set(), xt='';
  anos.forEach((a,i)=>{ if(!anosVistos.has(a)){ anosVistos.add(a);
    xt+=`<text x="${x(i).toFixed(1)}" y="${H-PAD.b+20}" text-anchor="middle" font-size="11" fill="var(--muted)">${a}</text>`; }});
  // anotações do topo
  let ann='';
  (opts.marcos||[]).forEach(m=>{
    const i=m.i; if(i<0||i>=N) return;
    ann+=`<line x1="${x(i).toFixed(1)}" x2="${x(i).toFixed(1)}" y1="${PAD.t}" y2="${H-PAD.b}" stroke="var(--axis)" stroke-width="1"/>`
      +`<text x="${(x(i)+(m.dir||1)*6).toFixed(1)}" y="${PAD.t+ (m.dy||10)}" text-anchor="${(m.dir||1)>0?'start':'end'}" font-size="11" fill="var(--ink-2)">${m.t}</text>`;
  });
  const pico = serie.indexOf(Math.max(...serie));
  // no log o pico encosta no topo, onde ficam as anotações: joga o rótulo para baixo
  const picoY = y(serie[pico]);
  const rotuloPicoY = picoY < PAD.t + 40 ? picoY + 22 : picoY - 12;
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${opts.aria||'Busca consolidada'}">
    ${g}${xt}${ann}
    ${log?'':`<path d="${area}" fill="var(--wash)"/>`}
    <path d="${linha}" fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="${x(pico).toFixed(1)}" cy="${y(serie[pico]).toFixed(1)}" r="4.5" fill="var(--s1)" stroke="var(--surface)" stroke-width="2"/>
    <text x="${x(pico).toFixed(1)}" y="${rotuloPicoY.toFixed(1)}" text-anchor="${pico>N*0.8?'end':'middle'}" font-size="12" font-weight="600" fill="var(--ink)">pico · ${meses[pico]}</text>
    <g class="cursor" opacity="0"><line y1="${PAD.t}" y2="${H-PAD.b}" stroke="var(--axis)" stroke-width="1"/>
      <circle r="4.5" fill="var(--s1)" stroke="var(--surface)" stroke-width="2"/></g>
    <rect class="hit" x="${PAD.l}" y="${PAD.t}" width="${W-PAD.l-PAD.r}" height="${H-PAD.t-PAD.b}" fill="transparent"/>
  </svg>`;
  return {x,y,topo};
}

/* ---------------- área empilhada ---------------- */
/* `visiveis` é um Set de índices de faixa. A cor segue a faixa, nunca a posição
   atual: desligar uma série não repinta as outras. O eixo, sim, se reajusta ao
   que restou — é o que permite ler as curvas pequenas. */
function desenharPilha(el, faixas, visiveis){
  const ativas = faixas.map((f,k)=>({...f,k})).filter(f=>visiveis.has(f.k));
  const total = new Array(N).fill(0);
  ativas.forEach(f=>{for(let i=0;i<N;i++) total[i]+=f.valores[i];});
  const {topo,ticks,passo} = eixoY(Math.max(...total)||0.02);
  const x = i => PAD.l + i*(W-PAD.l-PAD.r)/(N-1);
  const y = v => H-PAD.b - (v/topo)*(H-PAD.t-PAD.b);
  let g='';
  ticks.forEach(v=>{ g+=`<line x1="${PAD.l}" x2="${W-PAD.r}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}" stroke="${v?'var(--grid)':'var(--axis)'}" stroke-width="1"/>`
    +`<text x="${PAD.l-9}" y="${(y(v)+4).toFixed(1)}" text-anchor="end" font-size="11" fill="var(--muted)">${fmtTick(v,passo)}</text>`; });
  let anosVistos=new Set(), xt='';
  anos.forEach((a,i)=>{ if(!anosVistos.has(a)){ anosVistos.add(a);
    xt+=`<text x="${x(i).toFixed(1)}" y="${H-PAD.b+20}" text-anchor="middle" font-size="11" fill="var(--muted)">${a}</text>`; }});
  const base=new Array(N).fill(0);
  let paths='';
  ativas.forEach(f=>{
    const topoArr=f.valores.map((v,i)=>base[i]+v);
    let d='M '+x(0).toFixed(1)+' '+y(base[0]).toFixed(1);
    for(let i=0;i<N;i++) d+=' L '+x(i).toFixed(1)+' '+y(base[i]).toFixed(1);
    let d2='';
    for(let i=N-1;i>=0;i--) d2+=' L '+x(i).toFixed(1)+' '+y(topoArr[i]).toFixed(1);
    paths+=`<path d="${d}${d2} Z" fill="${f.cor}" fill-opacity="${f.resto?0.55:0.9}"/>`;
    // 2px da cor da superfície separando as faixas, em vez de contorno
    const linhaTopo = topoArr.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' ');
    paths+=`<path d="${linhaTopo}" fill="none" stroke="var(--surface)" stroke-width="2"/>`;
    for(let i=0;i<N;i++) base[i]=topoArr[i];
  });
  el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Composição da busca consolidada por matéria">
    ${g}${xt}${paths}
    <g class="cursor" opacity="0"><line y1="${PAD.t}" y2="${H-PAD.b}" stroke="var(--ink)" stroke-width="1"/></g>
    <rect class="hit" x="${PAD.l}" y="${PAD.t}" width="${W-PAD.l-PAD.r}" height="${H-PAD.t-PAD.b}" fill="transparent"/>
  </svg>`;
  return {ativas, topo};
}

/* ---------------- tooltip / crosshair ---------------- */
function ligarHover(box, get){
  const svg=box.querySelector('svg'), tip=box.querySelector('.tip');
  const cur=svg.querySelector('.cursor'), hit=svg.querySelector('.hit');
  const xi = i => PAD.l + i*(W-PAD.l-PAD.r)/(N-1);
  function mover(ev){
    const r=svg.getBoundingClientRect();
    const px=(ev.clientX-r.left)/r.width*W;
    let i=Math.round((px-PAD.l)/((W-PAD.l-PAD.r)/(N-1)));
    i=Math.max(0,Math.min(N-1,i));
    const info=get(i);
    cur.setAttribute('opacity','1');
    cur.querySelector('line').setAttribute('x1',xi(i)); cur.querySelector('line').setAttribute('x2',xi(i));
    const c=cur.querySelector('circle');
    if(c){ c.setAttribute('cx',xi(i)); c.setAttribute('cy',info.cy); }
    tip.innerHTML=info.html; tip.style.opacity='1';
    const left = Math.min(box.clientWidth-tip.offsetWidth-6, Math.max(0, xi(i)/W*box.clientWidth - tip.offsetWidth/2));
    tip.style.left=left+'px'; tip.style.top='6px';
  }
  hit.addEventListener('mousemove',mover);
  hit.addEventListener('mouseleave',()=>{tip.style.opacity='0';cur.setAttribute('opacity','0');});
  svg.addEventListener('touchmove',e=>{if(e.touches[0])mover(e.touches[0]);},{passive:true});
}

/* ---------------- montagem ---------------- */
const boxLinha=document.getElementById('linha');
let escala='log';
const marcos=[];
function idxDe(alvo){ return D.eixo.findIndex(l=>l.includes(alvo)); }

function render(){
  const lista = AMB;
  const s = soma(lista);
  const ref = desenharLinha(boxLinha, s, {marcos, escala,
    aria:'Busca consolidada pelas matérias ambientais no Google Trends Brasil'});
  document.getElementById('btn-log').setAttribute('aria-pressed', String(escala==='log'));
  document.getElementById('btn-lin').setAttribute('aria-pressed', String(escala!=='log'));
  ligarHover(boxLinha, i=>({
    cy: ref.y(s[i]).toFixed(1),
    html: `<b>${meses[i]}</b><div class="row"><span>Índice consolidado</span><b>${fmt(s[i])}</b></div>`
      + `<div class="row"><span>Principal tema</span><b>${(lista.slice().sort((a,b)=>b.valores[i]-a.valores[i])[0]||{}).id||'—'}</b></div>`
  }));
  const pico=s.indexOf(Math.max(...s));
  document.getElementById('t-pico').textContent=meses[pico];
  document.getElementById('t-picov').textContent=fmt(Math.max(...s));
}

document.getElementById('btn-log').onclick=()=>{escala='log';render();};
document.getElementById('btn-lin').onclick=()=>{escala='linear';render();};

// pilha: 7 maiores + as demais agrupadas
const ord = AMB.slice().sort((a,b)=>b.nivel-a.nivel);
const tops = ord.slice(0,7), resto = ord.slice(7);
const FAIXAS = tops.map((t,k)=>({
  rotulo: t.id, ementa: t.ementa, valores: t.valores, cor:`var(${SLOT[k]})`, resto:false
})).concat([{
  rotulo:`Outras ${resto.length} matérias`, ementa:'somadas', valores: soma(resto),
  cor:'var(--axis)', resto:true
}]);

const boxPilha=document.getElementById('pilha');
const legPilha=document.getElementById('leg-pilha');
const visiveis=new Set(FAIXAS.map((_,k)=>k));

function pintarLegenda(){
  legPilha.innerHTML = FAIXAS.map((f,k)=>{
    const on = visiveis.has(k);
    return `<button class="chip" data-k="${k}" aria-pressed="${on}" title="${f.ementa}">`
      + `<i style="background:${f.cor}"></i>${f.rotulo}${f.resto?'':' · '+f.ementa}</button>`;
  }).join('')
  + `<button class="chip reset" id="pilha-tudo">Mostrar todas</button>`;
}

function pintarPilha(){
  desenharPilha(boxPilha, FAIXAS, visiveis);
  const ativas = FAIXAS.filter((_,k)=>visiveis.has(k));
  const totais = new Array(N).fill(0);
  ativas.forEach(f=>{for(let i=0;i<N;i++) totais[i]+=f.valores[i];});
  ligarHover(boxPilha, i=>{
    const linhas = ativas.map(f=>`<div class="row"><span><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${f.cor}"></i> ${f.rotulo}</span><b>${fmt(f.valores[i])}</b></div>`).join('');
    return {cy:0, html:`<b>${meses[i]}</b>${linhas}`
      + `<div class="row"><span><b>Total visível</b></span><b>${fmt(totais[i])}</b></div>`};
  });
  pintarLegenda();
}

legPilha.addEventListener('click', ev=>{
  const b = ev.target.closest('button'); if(!b) return;
  if(b.id==='pilha-tudo'){ FAIXAS.forEach((_,k)=>visiveis.add(k)); }
  else {
    const k = +b.dataset.k;
    if(visiveis.has(k)) visiveis.delete(k); else visiveis.add(k);
    if(!visiveis.size) FAIXAS.forEach((_,i)=>visiveis.add(i)); // nunca vazio
  }
  pintarPilha();
});
pintarPilha();

// barras de nível
{
  const top = ord.slice(0,20);
  const max = Math.max(...top.map(t=>t.nivel))||1;
  const bw = 640, bh = 26;
  document.getElementById('barras').innerHTML =
    `<svg viewBox="0 0 ${bw} ${top.length*bh+10}" role="img" aria-label="Nível de busca por matéria">`
    + top.map((t,k)=>{
        const w = Math.max(1.5, t.nivel/max*(bw-250));
        const yy = k*bh+6;
        return `<text x="0" y="${yy+13}" font-size="11.5" fill="var(--ink-2)">${t.id}</text>`
          + `<rect x="86" y="${yy+3}" width="${w.toFixed(1)}" height="13" rx="4" fill="var(--s1)"/>`
          + `<text x="${(86+w+8).toFixed(1)}" y="${yy+14}" font-size="11" fill="var(--muted)">${fmt(t.nivel)}</text>`;
      }).join('')
    + `</svg>`;
}


/* ---------------- consulta pública: barras divergentes ---------------- */
{
  const MIN_VOTOS = 20;
  const linhas = D.topicos.filter(t=>t.consulta && t.consulta.total >= MIN_VOTOS)
                          .sort((a,b)=>a.consulta.pct_sim-b.consulta.pct_sim);
  const bw=1000, rh=30, padL=96, meio=520, meia=300; // meia = 100% da escala
  const alt = linhas.length*rh+34;
  let svg = `<svg viewBox="0 0 ${bw} ${alt}" role="img" aria-label="Votos Sim e Não na consulta pública do e-Cidadania, por matéria">`;
  // eixo central e referência
  svg += `<line x1="${meio}" x2="${meio}" y1="16" y2="${alt-18}" stroke="var(--axis)" stroke-width="1"/>`;
  svg += `<text x="${meio-6}" y="12" text-anchor="end" font-size="11" fill="var(--muted)">← Não</text>`
       + `<text x="${meio+6}" y="12" text-anchor="start" font-size="11" fill="var(--muted)">Sim →</text>`;
  linhas.forEach((t,k)=>{
    const c=t.consulta, y=k*rh+24, h=14;
    const wS = c.sim/c.total*meia, wN = c.nao/c.total*meia;
    svg += `<text x="0" y="${y+11}" font-size="11.5" fill="var(--ink-2)">${t.id}</text>`
        // gap de 2px na superfície entre as duas faixas
        + `<rect x="${(meio-wN).toFixed(1)}" y="${y}" width="${Math.max(0,wN-1).toFixed(1)}" height="${h}" rx="3" fill="var(--s8)"/>`
        + `<rect x="${(meio+1).toFixed(1)}" y="${y}" width="${Math.max(0,wS-1).toFixed(1)}" height="${h}" rx="3" fill="var(--s1)"/>`
        + `<text x="${(meio-wN-7).toFixed(1)}" y="${y+11}" text-anchor="end" font-size="11" fill="var(--muted)">${c.nao.toLocaleString('pt-BR')}</text>`
        + `<text x="${(meio+wS+7).toFixed(1)}" y="${y+11}" font-size="11" fill="var(--muted)">${c.sim.toLocaleString('pt-BR')}</text>`
        + `<text x="${bw}" y="${y+11}" text-anchor="end" font-size="11" fill="var(--ink-2)" font-weight="600">${c.pct_sim.toFixed(0)}% sim</text>`;
  });
  svg += `</svg>`;
  document.getElementById('consulta').innerHTML = svg;
}

// tabela
{
  const linhas = D.topicos.slice().sort((a,b)=>b.nivel-a.nivel).map(t=>{
    const mx=Math.max(...t.valores)||1;
    const pts=t.valores.map((v,i)=>`${(i/(N-1)*100).toFixed(1)},${(16-v/mx*14).toFixed(1)}`).join(' ');
    const spark = t.nivel>0 ? `<svg viewBox="0 0 100 18" preserveAspectRatio="none" style="width:110px;height:18px"><polyline points="${pts}" fill="none" stroke="var(--s1)" stroke-width="1.6" vector-effect="non-scaling-stroke"/></svg>` : '<span style="color:var(--muted)">—</span>';
    return `<tr><td><b>${t.id}</b><div class="q">${t.query}</div></td>`
      + `<td>${t.ementa}</td>`
      + `<td><span class="tag">${t.virou_norma?'virou norma':'em tramitação'}</span></td>`
      + `<td class="num">${fmt(t.nivel)}</td><td>${spark}</td>`
      + `<td class="num">${t.consulta&&t.consulta.total?t.consulta.total.toLocaleString('pt-BR'):'—'}</td>`
      + `<td class="num">${t.consulta&&t.consulta.total?t.consulta.pct_sim.toFixed(0)+'%':'—'}</td></tr>`;
  }).join('');
  document.getElementById('tbody').innerHTML=linhas;
}

// marcos temporais no gráfico de linha
[['mai. de 2024','Enchentes no RS',-1,12],
 ['jul. de 2025','PL 2159 aprovado',-1,12],
 ['nov. de 2025','COP30',1,28]]
  .forEach(([rot,txt,dir,dy])=>{const i=idxDe(rot); if(i>=0) marcos.push({i,t:txt,dir,dy});});
render();
"""


def main():
    with open(DADOS, encoding="utf-8") as fh:
        d = json.load(fh)

    consultas = {}
    if os.path.exists(CONSULTAS):
        with open(CONSULTAS, encoding="utf-8") as fh:
            consultas = {k: v for k, v in json.load(fh).items() if v}
    for t in d["topicos"]:
        c = consultas.get(t["id"])
        t["consulta"] = c if (c and c.get("total")) else None

    amb = d["topicos"]
    com_sinal = [t for t in amb if t["nivel"] > 0]
    n = len(d["eixo"])
    consolidado = [sum(t["valores"][i] for t in amb) for i in range(n)]
    pico = max(range(n), key=lambda i: consolidado[i])
    pico_val = consolidado[pico]
    pico_fmt = f"{pico_val:.2f}".replace(".", ",")
    concentracao = 0.0
    if sum(t["nivel"] for t in amb):
        top3 = sorted((t["nivel"] for t in amb), reverse=True)[:3]
        concentracao = 100 * sum(top3) / sum(t["nivel"] for t in amb)

    com_voto = [t for t in amb if t["consulta"]]
    votos_total = sum(t["consulta"]["total"] for t in com_voto)
    mais_votada = max(com_voto, key=lambda t: t["consulta"]["total"], default=None)
    conc_voto = (100 * mais_votada["consulta"]["total"] / votos_total) if votos_total else 0
    rejeitadas = [t for t in com_voto
                  if t["consulta"]["total"] >= 20 and t["consulta"]["pct_sim"] < 50]

    ini, fim = d["timeframe"].split(" ")

    html = f"""<title>Busca por Leis Ambientais</title>
<style>{CSS}</style>
<div class="wrap">
<header>
  <p class="kicker">Estudo de Roberto Federicci · Google Trends Brasil · {ini[:4]}–{fim[:4]}</p>
  <h1>O que o Brasil procura das leis ambientais</h1>
  <p class="sub">As matérias ambientais no legislativo, de 2017 a 2026, que foram consultadas por
  brasileiros: número do PL + tema — <span class="q">PL 2159 / lei geral do licenciamento ambiental +
  PL da devastação</span>.</p>
</header>

<div class="tiles">
  <div class="tile"><div class="v">{len(amb)}</div><div class="l">matérias ambientais no índice</div>
    <div class="h">levantamento legislativo do Senado, 2017–2026</div></div>
  <div class="tile"><div class="v">{len(com_sinal)}</div><div class="l">com busca detectável</div>
    <div class="h">{len(amb) - len(com_sinal)} não registram volume no Trends</div></div>
  <div class="tile"><div class="v" id="t-picov">—</div><div class="l">pico do índice consolidado</div>
    <div class="h">em <span id="t-pico">—</span></div></div>
  <div class="tile"><div class="v">{concentracao:.0f}%</div><div class="l">da busca em 3 temas</div>
    <div class="h">concentração no topo da lista</div></div>
</div>

<section>
  <h2>Busca consolidada por todas as matérias</h2>
  <p class="note">Soma das {len(amb)} curvas. Para que curvas de consultas diferentes pudessem ser somadas,
  todas foram postas numa régua comum — e essa régua é uma busca de referência que <b>não faz parte do
  índice</b>: a procura pela expressão genérica “meio ambiente”, cujo pico na década vale 100.
  Lê-se assim: no melhor mês, jul/2025, a atenção somada a <b>todas</b> as {len(amb)} leis ambientais
  chegou a {pico_fmt} — cerca de {pico_val:.0f}% do que os brasileiros procuram quando digitam
  simplesmente “meio ambiente”.</p>
  <div class="card">
    <div class="ctrl">
      <button id="btn-log" aria-pressed="true">Escala log</button>
      <button id="btn-lin" aria-pressed="false">Escala linear</button>
      <span style="color:var(--muted)">o log abre o cotidiano da série; a linear mostra o tamanho real do
      pico. No log, o único mês sem volume medido aparece no piso do eixo</span>
    </div>
    <div class="chart" id="linha"><div class="tip"></div></div>
  </div>
</section>

<section>
  <h2>De onde vem a curva</h2>
  <p class="note">As sete matérias de maior nível, empilhadas, mais o conjunto das demais. A linha
  consolidada é quase inteiramente formada por poucos temas de alta relevância pública.
  <b>Clique nos rótulos para ligar e desligar cada matéria</b> — o eixo se reajusta ao que ficou visível,
  o que permite ler as curvas menores sem o esmagamento do pico de 2025.</p>
  <div class="card">
    <div class="chart" id="pilha"><div class="tip"></div></div>
    <div class="legend" id="leg-pilha"></div>
  </div>
</section>

<section>
  <h2>Nível de busca por matéria</h2>
  <p class="note">Máximo de cada curva na régua global, 20 maiores. É a medida de quanto cada tema aparece
  na busca, não de quanto o projeto tramitou.</p>
  <div class="card"><div class="chart" id="barras"></div></div>
</section>

<section>
  <h2>Participação pública: a consulta do e-Cidadania</h2>
  <p class="note">Toda proposição que tramita no Senado fica aberta a voto Sim/Não no portal e-Cidadania
  (Resolução 26/2013). É opinião manifestada por quem se mobilizou, não amostra da população — mas é o
  único registro direto de posição do cidadão sobre estas matérias, e conversa com a curva de busca.</p>

  <div class="tiles compact">
    <div class="tile"><div class="v">{votos_total:,}</div><div class="l">votos nas {len(com_voto)} matérias
      com manifestação</div><div class="h">de {len(amb)} no índice</div></div>
    <div class="tile"><div class="v">{conc_voto:.0f}%</div><div class="l">deles numa única matéria</div>
      <div class="h">{mais_votada['id']} — {mais_votada['ementa']}</div></div>
    <div class="tile"><div class="v">{len(rejeitadas)}</div><div class="l">matérias com maioria contrária</div>
      <div class="h">entre as que passaram de 20 votos</div></div>
  </div>

  <div class="card">
    <div class="chart" id="consulta"></div>
    <div class="legend">
      <span><i style="background:var(--s8)"></i>Não</span>
      <span><i style="background:var(--s1)"></i>Sim</span>
      <span style="color:var(--muted)">matérias com 20 votos ou mais, da mais rejeitada à mais apoiada</span>
    </div>
  </div>
</section>

<section>
  <h2>As {len(amb)} matérias</h2>
  <p class="note">Consulta usada, situação e nível de busca. A minissérie mostra o formato da curva
  (normalizada em si mesma), não a magnitude.</p>
  <div class="card scroll">
    <table>
      <thead><tr><th>Matéria / consulta</th><th>Ementa</th><th>Situação</th>
        <th class="num">Nível</th><th>Curva</th><th class="num">Votos</th>
        <th class="num">% sim</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</section>

<section>
  <h2>Esclarecimentos</h2>
  <ul class="lim">
    <li><b>As chaves de busca combinam o número da proposição e o tópico associado a ela</b> — por exemplo,
    <span class="q">PL 2159 / lei geral do licenciamento ambiental + PL da devastação</span>. A expressão
    temática é sempre a que descreve o objeto da lei, e não o assunto amplo em volta dela, justamente para
    evitar a poluição por temas correlatos em pauta na mídia.</li>
    <li><b>A escala é reconstruída.</b> O Trends normaliza 0–100 dentro de cada consulta. Para somar as
    curvas, cada tópico foi medido contra buscas de referência e depois reescalado. Os níveis pequenos têm
    pouca resolução: o Trends devolve inteiros, então um tema fraco pode aparecer como zero sem ter volume
    literalmente nulo.</li>
    <li><b>Granularidade mensal.</b> Janelas acima de cinco anos vêm em meses; picos de poucos dias somem
    dentro do mês.</li>
    <li><b>O voto do e-Cidadania é autosselecionado.</b> Vota quem foi mobilizado a votar — entidade,
    bancada, campanha de rede social. Serve para ler <i>direção e intensidade de mobilização</i>, nunca
    como pesquisa de opinião: {conc_voto:.0f}% dos votos estão numa só matéria, e {len(amb) - len(com_voto)}
    matérias não tiveram voto nenhum.</li>
    <li><b>Recorte:</b> matérias ambientais <i>aprovadas pelo Senado</i> entre 2017 e 2026. Projetos
    ambientais rejeitados ou ainda parados na Câmara não estão aqui — inclusive alguns de alta
    relevância.</li>
  </ul>
</section>

<footer>
  Estudo de <b>Roberto Federicci</b> — parte da série de análises publicada em
  <a href="https://github.com/RobertoFedericci" style="color:inherit">github.com/RobertoFedericci</a>.<br>
  Fontes: Google Trends (Brasil, todas as categorias, {ini}&nbsp;a&nbsp;{fim}) e portal e-Cidadania do
  Senado Federal, consultado em agosto de 2026.
</footer>
</div>
<script>window.__DADOS__ = {json.dumps(d, ensure_ascii=False)};</script>
<script>{JS}</script>
"""
    with open(SAIDA, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"ok -> {SAIDA} ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
