/* Shared offline static and standalone UI. */
(function(global){
 'use strict';
 const colors={researched:'#197443',undiscovered:'#bc3438',unresearched:'#e1b52b','in-progress':'#3668a7',candidate:'#8d572b'},UP='#b9692e',DOWN='#237da6',CLEARANCE=58,coverageCache=new WeakMap();
 function model(){return global.RESEARCH_GRAPH;}
 function destination(id){return global.RESEARCH_STANDALONE?'#'+encodeURIComponent('nodes/'+id):(global.RESEARCH_ASSET_BASE||'.')+'/nodes/'+encodeURIComponent(id)+'.html';}
 function itemLink(id){
   const n=model().nodes[id],a=document.createElement('a');a.href=destination(id);a.dataset.page='nodes/'+id;a.dataset.itemStatus=n.status;a.textContent=n.name;
   const wrap=document.createElement('span'),badge=document.createElement('span'),dot=document.createElement('span'),text=document.createElement('span');wrap.append(a);
   badge.className='item-status status-'+n.status;badge.setAttribute('tabindex','0');badge.setAttribute('role','img');badge.setAttribute('aria-label',n.statusLabel);
   dot.textContent='●';dot.setAttribute('aria-hidden','true');text.className='status-text';text.textContent=n.statusLabel;text.setAttribute('aria-hidden','true');badge.append(dot,text);wrap.append(badge);return wrap;
 }
 function pathAt(target,rank){
   const g=model(),path=[target];if(rank<0n||rank>=BigInt(g.nodes[target].paths))throw new RangeError('Path outside range');
   while(target!==g.root){let found=false;for(const parent of g.nodes[target].parents){const size=BigInt(g.nodes[parent].paths);if(rank<size){target=parent;path.push(parent);found=true;break;}rank-=size;}if(!found)throw new Error('Inconsistent path counts');}return path.reverse();
 }
 function topological(g){
   if(g.topological)return g.topological;
   const incoming=new Map(Object.entries(g.nodes).map(([id,n])=>[id,n.parents.length])),queue=[];
   incoming.forEach((count,id)=>{if(!count)queue.push(id);});
   for(let i=0;i<queue.length;i++)for(const child of g.nodes[queue[i]].children){incoming.set(child,incoming.get(child)-1);if(!incoming.get(child))queue.push(child);}
   if(queue.length!==incoming.size)throw new Error('Coverage requires an acyclic graph');return queue;
 }
 function shortestRoute(g,target){
   const previous=g.predecessor||{},path=[target];
   if(!g.predecessor){const queue=[g.root],seen=new Set(queue);for(let i=0;i<queue.length;i++)for(const child of g.nodes[queue[i]].children)if(!seen.has(child)){seen.add(child);previous[child]=queue[i];queue.push(child);}}
   while(path[path.length-1]!==g.root){const parent=previous[path[path.length-1]];if(!parent)throw new Error('Missing root route');path.push(parent);}return path.reverse();
 }
 function coveragePaths(target,g=model()){
   if(g.nodes[target].level===null)return [];
   let cache=coverageCache.get(g);if(!cache){cache=new Map();coverageCache.set(g,cache);}if(cache.has(target))return cache.get(target);
   const ancestors=new Set(),stack=[target];
   while(stack.length){const id=stack.pop();if(ancestors.has(id))continue;ancestors.add(id);for(const p of g.nodes[id].parents)if(g.nodes[p].level!==null)stack.push(p);}
   const order=topological(g).filter(id=>ancestors.has(id)),routes=[shortestRoute(g,target)],uncovered=new Set(ancestors);routes[0].forEach(id=>uncovered.delete(id));
   while(uncovered.size){
     const scores=new Map([[g.root,0]]),lengths=new Map([[g.root,1]]),previous=new Map();
     for(const id of order){if(id===g.root)continue;let best=null;for(const p of g.nodes[id].parents)if(scores.has(p)&&(best===null||scores.get(p)>scores.get(best)||(scores.get(p)===scores.get(best)&&lengths.get(p)<lengths.get(best))))best=p;
       if(best===null)throw new Error('Missing coverage ancestor');scores.set(id,scores.get(best)+(uncovered.has(id)?1:0));lengths.set(id,lengths.get(best)+1);previous.set(id,best);}
     const route=[target];while(route[route.length-1]!==g.root)route.push(previous.get(route[route.length-1]));route.reverse();
     if(!route.some(id=>uncovered.has(id)))throw new Error('Route did not add coverage');routes.push(route);route.forEach(id=>uncovered.delete(id));
   }
   const counts=new Map(Array.from(ancestors,id=>[id,0]));routes.forEach(route=>route.forEach(id=>counts.set(id,counts.get(id)+1)));const keep=routes.map(()=>true);
   for(let i=routes.length-1;i>=0;i--)if(routes[i].every(id=>counts.get(id)>1)){keep[i]=false;routes[i].forEach(id=>counts.set(id,counts.get(id)-1));}
   const result=routes.filter((_,i)=>keep[i]);cache.set(target,result);return result;
 }
 function paths(section){
   if(section.dataset.uiReady)return;section.dataset.uiReady='true';
   const routes=coveragePaths(section.dataset.pathTarget),total=routes.length,list=section.querySelector('.path-list'),covered=new Set(routes.flat()).size;let offset=0;
   section.querySelector('.path-fallback').hidden=true;section.querySelector('.path-browser').hidden=false;
   const prev=section.querySelector('[data-path-prev]'),next=section.querySelector('[data-path-next]'),jump=section.querySelector('[data-path-jump]'),error=section.querySelector('.path-error');
   function show(){
     list.replaceChildren();const end=Math.min(offset+10,total);
     for(let rank=offset;rank<end;rank++){const li=document.createElement('li'),number=document.createElement('strong');li.setAttribute('aria-label','Coverage route '+(rank+1));number.textContent='Route '+(rank+1)+': ';li.append(number);routes[rank].forEach((id,i)=>{if(i)li.append(document.createTextNode(' → '));li.append(itemLink(id));});list.append(li);}
     list.style.listStyle='none';section.querySelector('.path-range').textContent='Showing routes '+(offset+1)+'–'+end+' of '+total+' · together covering all '+covered+' contributing items.';prev.disabled=offset===0;next.disabled=end===total;jump.value=String(offset+1);error.textContent='';
   }
   prev.onclick=()=>{offset=Math.max(0,offset-10);show();};next.onclick=()=>{offset+=10;show();};
   const go=()=>{const value=Number(jump.value.trim());if(!/^\d+$/.test(jump.value.trim())||!Number.isSafeInteger(value)||value<1||value>total){error.textContent='Enter a whole route number from 1 to '+total+'.';return;}offset=value-1;show();};
   section.querySelector('[data-path-go]').onclick=go;jump.onkeydown=e=>{if(e.key==='Enter')go();};show();
 }
 function orderedLevels(g,mode='shallowest'){
   if(mode==='deepest'&&g.deepestLevels)return g.deepestLevels;
   if(mode!=='deepest'&&g.levels)return g.levels;
   const deepest=new Map([[g.root,0]]);
   if(mode==='deepest')for(const id of topological(g))if(deepest.has(id))for(const child of g.nodes[id].children)deepest.set(child,Math.max(deepest.get(child)||0,deepest.get(id)+1));
   const levels=new Map();for(const [id,n] of Object.entries(g.nodes)){const level=mode==='deepest'?(deepest.get(id)??null):n.level;if(level!==null){if(!levels.has(level))levels.set(level,[]);levels.get(level).push(id);}}
   let previous=[g.root];const result=[];
   for(const level of Array.from(levels.keys()).sort((a,b)=>a-b)){
     if(!level){result.push({level:0,order:[g.root],groups:[{parent:null,items:[g.root]}]});continue;}
     const remaining=new Set(levels.get(level)),groups=previous.map(parent=>({parent,items:[],cursor:0}));
     let pendingGroups=groups;
     while(remaining.size){let added=false;const next=[];for(const group of pendingGroups){const children=g.nodes[group.parent].children;while(group.cursor<children.length&&!remaining.has(children[group.cursor]))group.cursor++;
       if(group.cursor<children.length){const id=children[group.cursor++];group.items.push(id);remaining.delete(id);added=true;if(group.cursor<children.length)next.push(group);}}
       if(!added)throw new Error('Level missing prior-level parent');pendingGroups=next;}
     const active=groups.filter(group=>group.items.length).map(({parent,items})=>({parent,items}));previous=active.flatMap(group=>group.items);result.push({level,order:previous,groups:active});
   }return result;
 }
 const LAYOUT={pitch:14,rowPitch:14*Math.sqrt(3)/2,nodeRadius:6.25,levelGap:12,groupGap:4,rootRadius:76};
 function ringPlan(groups,minimumRadius){
   const {pitch,groupGap}=LAYOUT,turn=2*Math.PI,capacity=turn-1e-6;
   function needed(radius,limit){
     const step=2*Math.asin(Math.min(1,pitch/(2*radius))),gap=2*Math.asin(Math.min(1,(pitch+groupGap)/(2*radius)));
     return groups.reduce((sum,group)=>sum+(group.items.length-1)/Math.min(limit,group.items.length)*step+gap,0);
   }
   let radius=minimumRadius,minimumRowsRequired=1;
   while(minimumRowsRequired<=4&&needed(radius,minimumRowsRequired)>capacity)minimumRowsRequired++;
   if(minimumRowsRequired>4){
     let low=radius,high=radius*2;while(needed(high,4)>capacity)high*=2;
     for(let i=0;i<40;i++){const middle=(low+high)/2;if(needed(middle,4)>capacity)low=middle;else high=middle;}
     radius=high*1.03; // A little slack lets small groups return to one row.
   }
   const step=2*Math.asin(Math.min(1,pitch/(2*radius))),gap=2*Math.asin(Math.min(1,(pitch+groupGap)/(2*radius)));
   const singleRowFits=needed(radius,1)<=capacity;
   let rowLimit=1;while(rowLimit<4&&needed(radius,rowLimit)>capacity)rowLimit++;
   const rows=groups.map(group=>Math.min(rowLimit,group.items.length));
   let occupied=groups.reduce((sum,group,i)=>sum+(group.items.length-1)/rows[i]*step+gap,0);
   const order=groups.map((group,i)=>i).sort((a,b)=>groups[a].items.length-groups[b].items.length||a-b);
   for(let target=1;target<rowLimit;target++)for(const i of order)if(rows[i]>target){
     const extra=(groups[i].items.length-1)*step*(1/target-1/rows[i]);
     if(occupied+extra<=capacity){rows[i]=target;occupied+=extra;}
   }
   return {radius,step,gap,rows,occupied,singleRowFits,rowLimit,minimumRowsRequired};
 }
 function packGroupCenters(groups,positions,plan){
   const turn=2*Math.PI;
   const entries=groups.map((group,i)=>({group,rows:plan.rows[i],targetAngle:(positions.get(group.parent).angle%turn+turn)%turn,
     span:(group.items.length-1)/plan.rows[i]*plan.step})).sort((a,b)=>a.targetAngle-b.targetAngle);
   let cut=0,biggest=-1;
   for(let i=0;i<entries.length;i++){const gap=(i===entries.length-1?entries[0].targetAngle+turn:entries[i+1].targetAngle)-entries[i].targetAngle;if(gap>biggest+1e-9){biggest=gap;cut=(i+1)%entries.length;}}
   const ordered=entries.slice(cut).concat(entries.slice(0,cut));
   let previous=-Infinity,prefix=0;
   for(const entry of ordered){while(entry.targetAngle<previous)entry.targetAngle+=turn;previous=entry.targetAngle;
     entry.width=entry.span+plan.gap;entry.offset=prefix+entry.width/2;prefix+=entry.width;}
   const windowStart=ordered[0].targetAngle-biggest/2,windowEnd=windowStart+turn;
   // Weighted isotonic projection preserves group order and minimizes displacement.
   const blocks=[];
   ordered.forEach((entry,i)=>{
     const weight=entry.group.items.length;blocks.push({start:i,end:i,weight,sum:weight*(entry.targetAngle-entry.offset)});
     while(blocks.length>1){
       const a=blocks[blocks.length-2],b=blocks[blocks.length-1];if(a.sum/a.weight<=b.sum/b.weight)break;
       blocks.splice(-2,2,{start:a.start,end:b.end,weight:a.weight+b.weight,sum:a.sum+b.sum});
     }
   });
   for(const block of blocks){
     const shift=Math.max(windowStart,Math.min(windowEnd-prefix,block.sum/block.weight));
     for(let i=block.start;i<=block.end;i++){
       const entry=ordered[i];entry.centerAngle=entry.offset+shift;
       entry.sectorLow=entry.centerAngle-entry.width/2;entry.sectorHigh=entry.centerAngle+entry.width/2;
     }
   }
   return ordered;
 }
 function layout(g,mode='shallowest'){
   const {pitch,rowPitch,nodeRadius,levelGap,rootRadius}=LAYOUT;
   const positions=new Map([[g.root,{x:0,y:0,radius:0,angle:-Math.PI/2}]]),bands=[];let radius=0;
   for(const level of orderedLevels(g,mode)){
     if(!level.level)continue;
     const placed=[],minimum=radius+levelGap+nodeRadius;
     if(level.level===1){
       const group=level.groups[0],n=group.items.length,r=Math.max(rootRadius,n>1?pitch/(2*Math.sin(Math.PI/n)):0);
       group.items.forEach((id,i)=>{const angle=-Math.PI/2+2*Math.PI*i/n;positions.set(id,{x:Math.cos(angle)*r,y:Math.sin(angle)*r,radius:r,angle,level:level.level,parent:group.parent,row:0});});
       placed.push({parent:group.parent,items:group.items,rows:1,baseRadius:r,sectorLow:-Math.PI/2,sectorHigh:3*Math.PI/2});
     }else{
       const plan=ringPlan(level.groups,minimum);
       for(const entry of packGroupCenters(level.groups,positions,plan)){
         const {group,rows,centerAngle,span}=entry;
         group.items.forEach((id,i)=>{
           const rowSpacing=rows>1?pitch*Math.sqrt(1-1/(rows*rows)):0;
           const angle=centerAngle-span/2+i/rows*plan.step,r=plan.radius+(i%rows)*rowSpacing;
           positions.set(id,{x:Math.cos(angle)*r,y:Math.sin(angle)*r,radius:r,angle,level:level.level,parent:group.parent,row:i%rows});
         });
         placed.push({parent:group.parent,items:group.items,rows,baseRadius:plan.radius,minimumBaseRadius:minimum,
           parentAngle:entry.targetAngle,centerAngle,sectorLow:entry.sectorLow,sectorHigh:entry.sectorHigh,span,
           singleRowFits:plan.singleRowFits,minimumRowsRequired:plan.minimumRowsRequired,placement:'flexible-group-packing'});
       }
     }
     let inner=Infinity,outer=0,rows=1;
     for(const group of placed){rows=Math.max(rows,group.rows);for(const id of group.items){const r=positions.get(id).radius;inner=Math.min(inner,r-nodeRadius);outer=Math.max(outer,r+nodeRadius);}}
     bands.push({level:level.level,inner,outer,rows,groups:placed});radius=outer;
   }
   return {positions,bands,radius};
 }
 function dotRadius(scale,root=false){return root?12:Math.max(.35,Math.min(28,LAYOUT.nodeRadius*scale));}
 function projected(p,scale,ox,oy){if(!p.radius)return {x:ox,y:oy};const radius=CLEARANCE+p.radius*scale;return {x:ox+p.x/p.radius*radius,y:oy+p.y/p.radius*radius};}
 function relationshipWidth(generation){return Math.max(1,2.5-.75*Math.max(0,generation-1));}
 function relationshipOpacity(generation){return generation<=1?1:generation===2?.5:.25;}
 function relationships(g,start,direction='both',limit=1){
   const ids=new Set([start]),edges=[];
   for(const way of ['ancestors','descendants']){
     if(direction!=='both'&&direction!==way)continue;
     const distances=new Map([[start,0]]),queue=[start],field=way==='ancestors'?'parents':'children';
     for(let i=0;i<queue.length;i++){
       const id=queue[i],generation=distances.get(id)+1;if(generation>limit)continue;
       for(const other of g.nodes[id][field]){
         ids.add(other);edges.push({from:id,to:other,generation,direction:way});
         if(!distances.has(other)){distances.set(other,generation);queue.push(other);}
       }
     }
   }
   return {ids,edges};
 }
 function makingGraph(g,root){
   const selected=relationships(g,root,'descendants',Infinity).ids,nodes={},queue=[root],distance=new Map([[root,0]]);
   for(let i=0;i<queue.length;i++)for(const child of g.nodes[queue[i]].children)if(!distance.has(child)){distance.set(child,distance.get(queue[i])+1);queue.push(child);}
   for(const id of selected)nodes[id]={...g.nodes[id],parents:g.nodes[id].parents.filter(p=>selected.has(p)),children:g.nodes[id].children.filter(c=>selected.has(c)),level:distance.get(id),deepestLevel:0};
   const result={root,revision:g.revision,nodes};
   for(const id of topological(result))for(const child of nodes[id].children)nodes[child].deepestLevel=Math.max(nodes[child].deepestLevel,nodes[id].deepestLevel+1);
   return result;
 }
 function dotMap(section){
   if(section.dataset.uiReady)return;section.dataset.uiReady='true';
   const fullGraph=model(),canvas=section.querySelector('canvas'),ctx=canvas.getContext('2d'),stage=canvas.parentElement,tooltip=section.querySelector('.map-tooltip'),depth=section.querySelector('[data-map-depth]');
   let g=fullGraph,entries=Object.entries(g.nodes),edges=[];
   let geometry=layout(g,depth.value),{positions,bands,radius}=geometry;
   for(const [id,n] of entries)if(positions.has(id))for(const child of n.children)if(positions.has(child))edges.push([id,child]);
   let width=1,height=1,scale=1,ox=0,oy=0,visible=[],page=0,hover=null,selected=null,pending=false,drag=null,moved=false,grid=new Map();
   const search=section.querySelector('[data-map-search]'),filter=section.querySelector('[data-map-filter]'),connections=section.querySelector('[data-map-connections]'),list=section.querySelector('.map-list'),prev=section.querySelector('[data-map-prev]'),next=section.querySelector('[data-map-next]');
   const direction=section.querySelector('[data-map-direction]'),generations=section.querySelector('[data-map-generations]'),reset=section.querySelector('[data-map-reset]'),context=section.querySelector('.map-context');
   function focus(){return selected||hover;}
   let relationshipCache=null;
   function highlighted(){const active=focus(),way=direction.value==='all'?'both':direction.value,limit=generations.value==='all'?Infinity:Number(generations.value);if(!active)return null;
     if(!relationshipCache||relationshipCache.g!==g||relationshipCache.active!==active||relationshipCache.way!==way||relationshipCache.limit!==limit)relationshipCache={g,active,way,limit,result:relationships(g,active,way,limit)};
     return relationshipCache.result;}
   function shown(){return visible;}
   function nodeLevel(n){return depth.value==='deepest'?n.deepestLevel:n.level;}
   function fits(){scale=Math.max(.0001,(Math.min(width,height)/2-CLEARANCE-14)/Math.max(1,radius));ox=width/2;oy=height/2;request();}
   function request(){if(!pending){pending=true;requestAnimationFrame(draw);}}
   function screen(id){const p=positions.get(id);return p?projected(p,scale,ox,oy):null;}
   function lines(edges){const groups=new Map();for(const edge of edges){const width=relationshipWidth(edge.generation),opacity=relationshipOpacity(edge.generation),key=edge.color+':'+width+':'+opacity;if(!groups.has(key))groups.set(key,{color:edge.color,width,opacity,edges:[]});groups.get(key).edges.push(edge);}
     for(const group of groups.values()){ctx.strokeStyle=group.color;ctx.lineWidth=group.width;ctx.globalAlpha=group.opacity;ctx.beginPath();for(const edge of group.edges){const from=screen(edge.from),to=screen(edge.to);if(!from||!to)continue;ctx.moveTo(from.x,from.y);ctx.lineTo(to.x,to.y);}ctx.stroke();}ctx.globalAlpha=1;}
   function clear(){selected=null;hover=null;tooltip.hidden=true;listPage();request();}
   function tree(id){g=makingGraph(fullGraph,id);entries=Object.entries(g.nodes);edges=entries.flatMap(([a,n])=>n.children.map(b=>[a,b]));geometry=layout(g,depth.value);({positions,bands,radius}=geometry);search.value='';filter.value='all';direction.value='descendants';generations.value='all';reset.hidden=false;context.textContent='Making tree: '+g.nodes[id].name;update();selected=id;listPage();fits();}
   function popup(id,x,y){
     tooltip.hidden=!id;if(!id)return;const n=g.nodes[id];tooltip.replaceChildren();
     const title=document.createElement('strong'),detail=document.createElement('p');title.textContent=n.name;detail.textContent=n.role+' · '+n.statusLabel+'\n'+depth.value+' level '+nodeLevel(n)+(n.frontier?' · Open frontier':'')+'\n'+n.parents.filter(p=>g.nodes[p].level!==null).length+' parent items · '+n.children.length+' required items';tooltip.append(title,detail);
     if(selected){const link=document.createElement('a'),making=document.createElement('button'),close=document.createElement('button');link.href=destination(id);link.dataset.page='nodes/'+id;link.textContent='Go to page';making.type='button';making.textContent='Making tree for this object';making.onclick=()=>tree(id);close.type='button';close.textContent='Close';close.onclick=clear;tooltip.append(link,making,close);}
     tooltip.className='map-tooltip'+(selected?' is-pinned':'');tooltip.style.left=Math.max(4,Math.min(width-300,x+15))+'px';tooltip.style.top=Math.max(4,Math.min(height-(tooltip.offsetHeight||210)-4,y+15))+'px';
   }
   function draw(){
     pending=false;ctx.clearRect(0,0,width,height);grid=new Map();ctx.lineWidth=1;ctx.font='12px system-ui';ctx.textAlign='center';
     for(const band of bands){const inner=CLEARANCE+band.inner*scale,outer=CLEARANCE+band.outer*scale;ctx.fillStyle=band.level%2?'#f5f8f6':'#fafcfb';ctx.beginPath();ctx.arc(ox,oy,outer+3,0,Math.PI*2);ctx.arc(ox,oy,Math.max(0,inner-3),0,Math.PI*2,true);ctx.fill();ctx.strokeStyle='#e3ebe6';ctx.beginPath();ctx.arc(ox,oy,outer+3,0,Math.PI*2);ctx.stroke();if(scale>.35){ctx.fillStyle='#6b8076';ctx.fillText('Level '+band.level,ox+40,oy-outer-6);}}
     const active=focus(),related=highlighted(),drawItems=new Map(shown());
     if(connections.checked){const ids=new Set(drawItems.keys()),faint=direction.value!=='all'&&related?related.edges:edges.map(([from,to])=>({from,to,generation:Math.max(1,nodeLevel(g.nodes[to]))}));lines(faint.filter(edge=>ids.has(edge.from)&&ids.has(edge.to)).map(edge=>({...edge,color:'rgba(39,74,89,.045)'})));}
     if(active&&positions.has(active)){drawItems.set(active,g.nodes[active]);lines(related.edges.filter(edge=>drawItems.has(edge.from)&&drawItems.has(edge.to)).map(edge=>({...edge,color:edge.direction==='ancestors'?UP:DOWN})));}
     for(const [id,n] of drawItems){const p=screen(id);if(!p||p.x<-15||p.y<-15||p.x>width+15||p.y>height+15)continue;const root=id===g.root,r=dotRadius(scale,root);ctx.beginPath();ctx.arc(p.x,p.y,r,0,2*Math.PI);ctx.fillStyle=colors[n.status]||colors['in-progress'];ctx.fill();
       if(n.frontier&&id!==active&&r>=2){ctx.strokeStyle='#526a60';ctx.lineWidth=1;ctx.beginPath();ctx.arc(p.x,p.y,Math.max(.35,r-.5),0,2*Math.PI);ctx.stroke();}
       if(root||r>=5){ctx.fillStyle=n.status==='unresearched'?'#19312f':'white';ctx.font='bold '+(root?12:9)+'px system-ui';ctx.fillText(n.role==='tool'?'T':n.role==='part'?'P':n.role[0].toUpperCase(),p.x,p.y+3);}
       if(root){ctx.fillStyle='#19312f';ctx.font='bold 13px system-ui';ctx.fillText(n.name,p.x,p.y+30);}const key=Math.floor(p.x/24)+','+Math.floor(p.y/24);if(!grid.has(key))grid.set(key,[]);grid.get(key).push({id,x:p.x,y:p.y,r});}
     // Selection uses corners outside the dot; frontier remains an independent ring.
     if(active&&positions.has(active)){
       const p=screen(active),r=dotRadius(scale,active===g.root);
       if(g.nodes[active].frontier){ctx.strokeStyle='#526a60';ctx.lineWidth=1;ctx.beginPath();ctx.arc(p.x,p.y,Math.max(3,r-.5),0,2*Math.PI);ctx.stroke();}
       const extent=Math.max(8,r+6),corner=Math.min(4,extent/2);
       ctx.strokeStyle=selected===active?'#7c3aed':'#136b7b';ctx.lineWidth=selected===active?2:1.5;ctx.beginPath();
       for(const sx of [-1,1])for(const sy of [-1,1]){const x=p.x+sx*extent,y=p.y+sy*extent;ctx.moveTo(x-sx*corner,y);ctx.lineTo(x,y);ctx.lineTo(x,y-sy*corner);}
       ctx.stroke();
     }
     if(filter.value==='outside'){ctx.fillStyle='#526960';ctx.font='15px system-ui';ctx.fillText('Disconnected items have no position in the Smartphone map.',width/2,height/2);}
     if(selected){const point=screen(selected);if(point)popup(selected,point.x,point.y);}
   }
   function listPage(){
     const items=shown();page=Math.min(page,Math.max(0,Math.ceil(items.length/50)-1));
     list.replaceChildren();items.slice(page*50,page*50+50).forEach(([id,n])=>{const li=document.createElement('li'),making=document.createElement('button');making.type='button';making.textContent='Making tree';making.setAttribute('aria-label','Making tree for '+n.name);making.onclick=()=>tree(id);li.append(itemLink(id),document.createTextNode(' · '+(n.level===null?'outside root map':'level '+nodeLevel(n))+(n.frontier?' · open frontier':'')));if(positions.has(id)){const select=document.createElement('button');select.type='button';select.textContent='Select';select.setAttribute('aria-label','Select '+n.name+' on map');select.onclick=()=>{selected=id;hover=null;page=0;listPage();request();};li.append(select);}li.append(making);list.append(li);});
     prev.disabled=page===0;next.disabled=(page+1)*50>=items.length;section.querySelector('.map-summary').textContent=items.length+' matching items · list '+(items.length?page*50+1:0)+'–'+Math.min((page+1)*50,items.length)+' · '+positions.size+' reachable / '+(entries.length-positions.size)+' outside root map · '+edges.length+' mapped connections · '+depth.value+' levels · revision '+g.revision;
   }
   function update(){const q=search.value.trim().toLowerCase(),f=filter.value;visible=entries.filter(([id,n])=>(f==='outside'?n.level===null:n.level!==null)&&(!q||(id+' '+n.name).toLowerCase().includes(q))&&(f==='all'||f==='outside'||(f==='frontier'?n.frontier:f==='part'||f==='tool'?n.role===f:n.status===f)));page=0;hover=null;selected=null;tooltip.hidden=true;listPage();request();}
   search.oninput=update;filter.onchange=update;connections.onchange=request;prev.onclick=()=>{page--;listPage();};next.onclick=()=>{page++;listPage();};
   direction.onchange=generations.onchange=()=>{if(direction.value!=='all'&&!focus())selected=g.root;page=0;listPage();request();};
   reset.onclick=()=>{g=fullGraph;entries=Object.entries(g.nodes);geometry=layout(g,depth.value);({positions,bands,radius}=geometry);edges=entries.flatMap(([a,n])=>positions.has(a)?n.children.filter(b=>positions.has(b)).map(b=>[a,b]):[]);direction.value='all';generations.value='1';search.value='';filter.value='all';reset.hidden=true;context.textContent='';update();fits();};
   depth.onchange=()=>{geometry=layout(g,depth.value);({positions,bands,radius}=geometry);fits();listPage();};
   function zoom(factor,x=width/2,y=height/2){const value=Math.max(.0001,Math.min(25,scale*factor));ox=x-(x-ox)*value/scale;oy=y-(y-oy)*value/scale;scale=value;request();}
   section.querySelector('[data-map-fit]').onclick=fits;section.querySelector('[data-map-in]').onclick=()=>zoom(1.5);section.querySelector('[data-map-out]').onclick=()=>zoom(1/1.5);
   canvas.addEventListener('wheel',e=>{e.preventDefault();const r=canvas.getBoundingClientRect();zoom(e.deltaY<0?1.15:1/1.15,e.clientX-r.left,e.clientY-r.top);},{passive:false});
   function hit(x,y){let best=null,distance=Infinity;const gx=Math.floor(x/24),gy=Math.floor(y/24),reach=Math.ceil((Math.max(12,dotRadius(scale))+5)/24);for(let dx=-reach;dx<=reach;dx++)for(let dy=-reach;dy<=reach;dy++)for(const p of grid.get((gx+dx)+','+(gy+dy))||[]){const d=Math.hypot(p.x-x,p.y-y);if(d<p.r+5&&d<distance){best=p.id;distance=d;}}return best;}
   canvas.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY,ox,oy};moved=false;canvas.setPointerCapture(e.pointerId);};
   canvas.onpointermove=e=>{const rect=canvas.getBoundingClientRect(),x=e.clientX-rect.left,y=e.clientY-rect.top;if(drag){const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>4)moved=true;ox=drag.ox+dx;oy=drag.oy+dy;if(!selected)tooltip.hidden=true;request();return;}if(selected)return;const id=hit(x,y);if(hover!==id){hover=id;listPage();request();}popup(id,x,y);};
   canvas.onpointerup=e=>{const rect=canvas.getBoundingClientRect(),x=e.clientX-rect.left,y=e.clientY-rect.top,id=hit(x,y);drag=null;if(!moved){selected=id;hover=null;page=0;listPage();popup(id,x,y);request();}};
   canvas.onpointercancel=()=>{drag=null;};canvas.onpointerleave=()=>{if(!drag&&!selected)clear();};
   canvas.onkeydown=e=>{if(e.key==='Escape')clear();if(e.key==='+'||e.key==='='){e.preventDefault();zoom(1.5);}if(e.key==='-'){e.preventDefault();zoom(1/1.5);}if(e.key==='0')fits();};
   const resize=()=>{const dpr=global.devicePixelRatio||1;width=stage.clientWidth;height=stage.clientHeight;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);fits();};
   const observer=new ResizeObserver(resize);observer.observe(stage);resize();update();section._dispose=()=>observer.disconnect();
 }
 function init(){if(!model())return;document.querySelectorAll('[data-path-target]').forEach(paths);document.querySelectorAll('.dot-map').forEach(dotMap);}
 global.ResearchUI={init,pathAt,coveragePaths,orderedLevels,layout,ringPlan,packGroupCenters,dotRadius,LAYOUT,projected,destination,relationships,relationshipWidth,relationshipOpacity,makingGraph};
 if(typeof document!=='undefined'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();}
})(typeof window!=='undefined'?window:globalThis);
