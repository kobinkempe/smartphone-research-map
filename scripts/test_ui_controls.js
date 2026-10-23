/* Pure DOM/canvas doubles: exercises controls without bypassing browser URL policy. */
'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm');
class Element{
 constructor(){this.children=[];this.dataset={};this.style={};this.hidden=false;this.value='';this.textContent='';this.disabled=false;this.checked=false;this.attrs={};this.selectors={};}
 get textContent(){return this._text+this.children.map(n=>typeof n==='string'?n:n.textContent||'').join('');}
 set textContent(value){this._text=value;this.children=[];}
 append(...values){this.children.push(...values);} replaceChildren(...values){this.children=values;}
 setAttribute(key,value){this.attrs[key]=value;} querySelector(key){assert(this.selectors[key],key);return this.selectors[key];}
 addEventListener(key,fn){this['on'+key]=fn;}
}
function section(keys){const e=new Element();keys.forEach(key=>e.selectors[key]=new Element());return e;}
const tracker=section(['.path-list','.path-fallback','.path-browser','[data-path-prev]','[data-path-next]','[data-path-jump]','.path-error','.path-range','[data-path-go]']);tracker.dataset.pathTarget='end';
const map=section(['canvas','.map-tooltip','[data-map-search]','[data-map-filter]','[data-map-depth]','[data-map-connections]','.map-list','[data-map-prev]','[data-map-next]','.map-summary','[data-map-fit]','[data-map-in]','[data-map-out]','[data-map-direction]','[data-map-generations]','[data-map-reset]','.map-context']);
map.selectors['[data-map-filter]'].value='all';
map.selectors['[data-map-depth]'].value='shallowest';
map.selectors['[data-map-direction]'].value='all';map.selectors['[data-map-generations]'].value='1';
const canvas=map.selectors.canvas;canvas.parentElement={clientWidth:700,clientHeight:470};canvas.getBoundingClientRect=()=>({left:0,top:0});canvas.setPointerCapture=()=>{};
const strokeColors=[],strokes=[],context={
 beginPath(){this.path=[];},
 arc(x,y,r){this.path.push({kind:'arc',x,y,r});},
 moveTo(x,y){this.path.push({kind:'move',x,y});},
 lineTo(x,y){this.path.push({kind:'line',x,y});},
 stroke(){strokeColors.push(this.strokeStyle);strokes.push({color:this.strokeStyle,width:this.lineWidth,opacity:this.globalAlpha??1,path:this.path.slice()});}
};
canvas.getContext=()=>new Proxy(context,{get:(o,key)=>key in o?o[key]:()=>{},set:(o,key,value)=>{o[key]=value;return true;}});
globalThis.document={readyState:'complete',createElement:()=>new Element(),createTextNode:text=>({textContent:text}),querySelectorAll:key=>key==='[data-path-target]'?[tracker]:key==='.dot-map'?[map]:[]};
globalThis.ResizeObserver=class{observe(){}disconnect(){}};globalThis.requestAnimationFrame=fn=>fn();globalThis.location={href:''};
const nodes={};function add(id,level,parents,paths){nodes[id]={name:id==='handset'?'Smartphone':id,role:'part',status:'unresearched',statusLabel:'Discovered · unresearched',level,deepestLevel:level,parents,children:[],paths:String(paths),frontier:true};}
add('handset',0,[],1);add('a',1,['handset'],1);add('b',1,['handset'],1);add('end',2,Array.from({length:16},(_,i)=>'leaf'+i),16);add('outside',null,[],0);
for(let i=0;i<120;i++)add('leaf'+i,1,['handset'],1);
nodes.b.parents.push('a');nodes.b.deepestLevel=2;nodes.b.paths='2';
for(let i=3;i<=10;i++)add('deep'+i,i,[i===3?'end':'deep'+(i-1)],16);
for(const [id,n] of Object.entries(nodes))for(const p of n.parents)nodes[p].children.push(id);
globalThis.RESEARCH_GRAPH={root:'handset',revision:7,nodes};
vm.runInThisContext(fs.readFileSync(process.argv[2],'utf8'));
assert.equal(tracker.selectors['.path-list'].children.length,10);
assert.match(tracker.selectors['.path-range'].textContent,/1–10 of 16/);
assert.equal(tracker.selectors['[data-path-next]'].disabled,false);
tracker.selectors['[data-path-next]'].onclick();assert.match(tracker.selectors['.path-range'].textContent,/11–16 of 16/);assert.equal(tracker.selectors['[data-path-next]'].disabled,true);
tracker.selectors['[data-path-prev]'].onclick();assert.match(tracker.selectors['.path-range'].textContent,/1–10 of 16/);
tracker.selectors['[data-path-jump]'].value='16';tracker.selectors['[data-path-go]'].onclick();
assert.match(tracker.selectors['.path-range'].textContent,/16–16 of 16/);
tracker.selectors['[data-path-jump]'].value='17';tracker.selectors['[data-path-go]'].onclick();assert.match(tracker.selectors['.path-error'].textContent,/1 to 16/);
assert.equal(map.selectors['.map-list'].children.length,50);map.selectors['[data-map-next]'].onclick();assert.match(map.selectors['.map-summary'].textContent,/list 51–100/);
map.selectors['[data-map-search]'].value='end';map.selectors['[data-map-search]'].oninput();assert.equal(map.selectors['.map-list'].children.length,1);
map.selectors['[data-map-search]'].value='';map.selectors['[data-map-filter]'].value='outside';map.selectors['[data-map-filter]'].onchange();assert.equal(map.selectors['.map-list'].children.length,1);
map.selectors['[data-map-filter]'].value='all';map.selectors['[data-map-filter]'].onchange();
canvas.onpointermove({clientX:350,clientY:235});assert.match(map.selectors['.map-tooltip'].textContent,/Smartphone/);
canvas.onpointerdown({clientX:350,clientY:235,pointerId:1});canvas.onpointerup({clientX:350,clientY:235});assert.equal(location.href,'');
const popup=map.selectors['.map-tooltip'];assert.equal(popup.children.find(n=>n.textContent==='Go to page').href,'./nodes/handset.html');
const selectedMark=strokes.findLast?strokes.findLast(s=>s.color==='#7c3aed'):strokes.slice().reverse().find(s=>s.color==='#7c3aed');
assert(selectedMark);assert(selectedMark.path.some(p=>p.kind==='line'));assert(!selectedMark.path.some(p=>p.kind==='arc'));
assert(strokes.some(s=>s.color==='#526a60'&&s.path.some(p=>p.kind==='arc'&&p.x===350&&p.y===235)));
strokes.length=0;nodes.handset.frontier=false;map.selectors['[data-map-connections]'].onchange();
assert(strokes.some(s=>s.color==='#7c3aed'));
assert(!strokes.some(s=>s.color==='#526a60'&&s.path.some(p=>p.kind==='arc'&&p.x===350&&p.y===235)));
assert(!popup.textContent.includes('Open frontier'));
strokes.length=0;nodes.handset.frontier=true;map.selectors['[data-map-connections]'].onchange();
assert(strokes.some(s=>s.color==='#7c3aed'));
assert(strokes.some(s=>s.color==='#526a60'&&s.path.some(p=>p.kind==='arc'&&p.x===350&&p.y===235)));
assert(popup.textContent.includes('Open frontier'));
canvas.onpointerleave();assert.equal(popup.hidden,false);assert(strokeColors.includes('#237da6'));
canvas.onkeydown({key:'Escape'});assert.equal(popup.hidden,true);
map.selectors['[data-map-connections]'].checked=true;map.selectors['[data-map-connections]'].onchange();assert(strokeColors.includes('rgba(39,74,89,.045)'));
const geometry=ResearchUI.layout(RESEARCH_GRAPH);assert(geometry.positions.get('a').radius>=76);
assert.equal(ResearchUI.dotRadius(1),6.25);
for(let i=1;i<geometry.bands.length;i++)assert(geometry.bands[i].inner-geometry.bands[i-1].outer>=12-1e-7);
for(const band of geometry.bands)for(const group of band.groups)if(band.level>1)for(const id of group.items){const point=geometry.positions.get(id);assert(point.angle>=group.sectorLow-1e-7&&point.angle<=group.sectorHigh+1e-7);}
for(const [id,p] of geometry.positions)if(nodes[id].level===1){const point=ResearchUI.projected(p,.0001,0,0);assert(Math.hypot(point.x,point.y)>58);}
assert.equal(ResearchUI.layout(RESEARCH_GRAPH,'deepest').positions.get('b').level,2);
assert.equal(ResearchUI.layout(RESEARCH_GRAPH,'shallowest').positions.get('b').level,1);
map.selectors['[data-map-depth]'].value='deepest';map.selectors['[data-map-depth]'].onchange();assert.match(map.selectors['.map-summary'].textContent,/deepest levels/);
map.selectors['[data-map-depth]'].value='shallowest';map.selectors['[data-map-depth]'].onchange();assert.match(map.selectors['.map-summary'].textContent,/shallowest levels/);
// Directional traversal does not wander into siblings or repeated shared paths.
assert.deepEqual([...ResearchUI.relationships(RESEARCH_GRAPH,'a','descendants',1).ids],['a','b']);
assert.deepEqual(new Set(ResearchUI.relationships(RESEARCH_GRAPH,'b','ancestors',2).ids),new Set(['b','handset','a']));
assert(!ResearchUI.relationships(RESEARCH_GRAPH,'b','ancestors',2).ids.has('leaf0'));
assert(!ResearchUI.relationships(RESEARCH_GRAPH,'handset','descendants',1).ids.has('end'));
assert(ResearchUI.relationships(RESEARCH_GRAPH,'handset','descendants',2).ids.has('end'));
for(let i=1;i<20;i++){assert(ResearchUI.relationshipWidth(i)>=1);if(i>1)assert(ResearchUI.relationshipWidth(i)<=ResearchUI.relationshipWidth(i-1));}
assert.equal(ResearchUI.relationshipWidth(99),1);
const subtree=ResearchUI.makingGraph(RESEARCH_GRAPH,'a');assert.deepEqual(Object.keys(subtree.nodes),['a','b']);
assert.equal(subtree.nodes.a.level,0);assert.equal(subtree.nodes.b.level,1);assert.deepEqual(subtree.nodes.b.parents,['a']);
for(const mode of ['shallowest','deepest'])assert.equal(ResearchUI.layout(subtree,mode).positions.size,2);
assert.equal(RESEARCH_GRAPH.nodes.a.level,1);assert.equal(RESEARCH_GRAPH.nodes.b.parents.length,2);
canvas.onpointerup({clientX:350,clientY:235});
const direction=map.selectors['[data-map-direction]'],generations=map.selectors['[data-map-generations]'];
direction.value='descendants';direction.onchange();generations.value='1';generations.onchange();
assert.equal(map.selectors['.map-list'].children.length,50);assert(map.selectors['.map-list'].textContent.includes('end'));
generations.value='2';strokes.length=0;generations.onchange();assert(strokes.some(s=>s.color==='#237da6'&&s.width===1.75&&s.opacity===.5));assert(strokes.some(s=>s.color==='#237da6'&&s.width===2.5&&s.opacity===1));assert.equal(context.globalAlpha,1);
assert.deepEqual([1,2,3,4,10].map(ResearchUI.relationshipOpacity),[1,.5,.25,.25,.25]);
generations.value='all';strokes.length=0;generations.onchange();
const deepStrokes=strokes.filter(s=>s.color==='#237da6'&&s.opacity===.25);
assert.equal(deepStrokes.length,1);assert.equal(deepStrokes[0].width,1);assert.equal(deepStrokes[0].path.filter(p=>p.kind==='line').length,8);assert.equal(context.globalAlpha,1);
direction.value='ancestors';strokes.length=0;direction.onchange();assert.equal(map.selectors['.map-list'].children.length,50);assert(!strokes.some(s=>s.color==='#237da6'));assert(!strokes.some(s=>s.color==='rgba(39,74,89,.045)'));
direction.value='all';direction.onchange();
const aRow=map.selectors['.map-list'].children.find(n=>n.children[0].children[0].textContent==='a');aRow.children.find(n=>n.textContent==='Select').onclick();
direction.value='ancestors';strokes.length=0;direction.onchange();assert(strokes.some(s=>s.color==='#b9692e'));assert(!strokes.some(s=>s.color==='#237da6'));
popup.children.find(n=>n.textContent==='Making tree for this object').onclick();
assert.match(map.selectors['.map-context'].textContent,/Making tree: a/);assert.equal(map.selectors['.map-list'].children.length,2);assert.equal(map.selectors['[data-map-reset]'].hidden,false);
assert.equal(direction.value,'descendants');assert.equal(generations.value,'all');
map.selectors['[data-map-depth]'].value='deepest';map.selectors['[data-map-depth]'].onchange();assert.equal(map.selectors['.map-list'].children.length,2);
map.selectors['[data-map-reset]'].onclick();assert.equal(map.selectors['.map-list'].children.length,50);assert.equal(map.selectors['.map-context'].textContent,'');
map.selectors['[data-map-filter]'].value='outside';map.selectors['[data-map-filter]'].onchange();map.selectors['.map-list'].children[0].children.find(n=>n.textContent==='Making tree').onclick();
assert.equal(map.selectors['.map-list'].children.length,1);assert.match(map.selectors['.map-context'].textContent,/outside/);assert.match(popup.textContent,/outside/);
map.selectors['[data-map-reset]'].onclick();
globalThis.RESEARCH_STANDALONE=true;assert.equal(ResearchUI.destination('handset'),'#nodes%2Fhandset');
map.selectors['[data-map-in]'].onclick();map.selectors['[data-map-out]'].onclick();map.selectors['[data-map-fit]'].onclick();
console.log('Coverage routes, grouping, radial gaps, pinned popup, colored/faint connections, search/filter, zoom and standalone URLs passed in DOM doubles.');
