/* Flexible parent-centered group packing, without browser visual claims. */
'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm');
vm.runInThisContext(fs.readFileSync(process.argv[2],'utf8'));
const fixtures=JSON.parse(fs.readFileSync(0,'utf8')),L=ResearchUI.LAYOUT;
assert(2*ResearchUI.dotRadius(1)/L.pitch>.85);
assert(2*ResearchUI.dotRadius(1)/L.pitch<1);
let expanded=0,multirows=0,singleRows=0,crowdedRows=0;
for(let fixtureIndex=0;fixtureIndex<fixtures.length;fixtureIndex++)for(const mode of ['shallowest','deepest']){
 const graph=fixtures[fixtureIndex],geometry=ResearchUI.layout(graph,mode),positions=geometry.positions;
 assert.equal(positions.size,Object.values(graph.nodes).filter(n=>n.level!==null).length);
 for(let i=1;i<geometry.bands.length;i++)assert(geometry.bands[i].inner-geometry.bands[i-1].outer>=L.levelGap-1e-7);
 for(const band of geometry.bands){
  for(const group of band.groups){
   if(band.level===1)continue;
   assert(group.rows<=4,'crowded full rings must not exceed four rows');
   if(group.rows>2){crowdedRows++;assert(group.minimumRowsRequired>2,'extra rows were caused by local crowding instead of full-ring capacity');}
   assert(group.centerAngle>=group.sectorLow-1e-7&&group.centerAngle<=group.sectorHigh+1e-7);
   assert(group.baseRadius>=group.minimumBaseRadius-1e-7);
   if(group.baseRadius>group.minimumBaseRadius+1e-7)expanded++;
   if(group.rows===1)singleRows++;else multirows++;
   if(group.singleRowFits)assert.equal(group.rows,1,'one row fits around ring but extra rows were used');
   const parent=positions.get(group.parent);
   for(const id of group.items){
    const p=positions.get(id);
    assert(p.angle>=group.sectorLow-1e-7&&p.angle<=group.sectorHigh+1e-7,'child crossed another group interval');
    assert(p.radius>parent.radius);
   }
   if(fixtureIndex===0&&band.level===2){
    assert.equal(group.rows,1);
    assert(Math.abs(group.centerAngle-group.parentAngle)<1e-6,'sparse group should stay centered at its parent');
   }
  }
  const groups=band.groups.filter(group=>band.level>1).slice().sort((a,b)=>a.sectorLow-b.sectorLow);
  for(let i=1;i<groups.length;i++)assert(groups[i-1].sectorHigh<=groups[i].sectorLow+1e-7,'group intervals overlap');
  const ids=band.groups.flatMap(group=>group.items);
  for(let i=0;i<ids.length;i++)for(let j=0;j<i;j++){
   const a=positions.get(ids[i]),b=positions.get(ids[j]),required=a.parent===b.parent?L.pitch:L.pitch+L.groupGap;
   assert(Math.hypot(a.x-b.x,a.y-b.y)>=required-1e-7,'dots or groups overlap');
  }
 }
 const points=Array.from(positions.values());
 for(let i=1;i<points.length;i++)for(let j=0;j<i;j++)assert(Math.hypot(points[i].x-points[j].x,points[i].y-points[j].y)>=L.pitch-1e-7);
}
assert(expanded>0&&multirows>0&&singleRows>0&&crowdedRows>0);
const centers=ResearchUI.packGroupCenters([{parent:'a',items:['a1','a2','a3']},{parent:'b',items:['b1','b2','b3']}],
 new Map([['a',{angle:0}],['b',{angle:0}]]),{rows:[1,1],step:.1,gap:.1});
assert(Math.abs(centers[0].centerAngle+centers[1].centerAngle)<1e-7,'groups should split nearby free space around their parents');
assert(centers[0].sectorHigh<=centers[1].sectorLow+1e-7);
console.log('Flexible parent groups, up to four rows only for full-ring crowding, nearby centering, spacing and both views passed.');
