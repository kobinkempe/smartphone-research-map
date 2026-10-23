"""Import the recovery checkpoint without promoting any claim to verified research."""
import json, re, shutil, sys
from pathlib import Path
from graph_gate import validate_registry

HERE = Path(__file__).resolve().parents[1]
STAGING = HERE.parent / 'research-staging'

def read(name):
    return json.loads((STAGING / name).read_text(encoding='utf-8-sig'))

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

seed = read('seed-nodes.json')
pages = read('inherited-pages.json')
sources = read('recovered-sources.json')
if isinstance(sources, dict):
    sources = sources.get('sources', sources.get('urls', []))

node_map = {n['id']: dict(n) for n in seed['nodes']}
material_ids = {'plant-fiber','fiber-cord','charcoal','refractories','iron-stock','copper-stock','aluminum-stock','alloy-stock','rare-earth-stock','magnet-stock','copper-wire','bearing-stock','seals','hard-tool-materials','pure-water','acids-bases','solvents','ceramics-stock','glass-stock','polymers','adhesives','silicon-feed','photoresist','battery-materials','display-chemicals','transparent-conductors','carbon-materials'}
renames = {'natural-resource-survey':'Resource survey kit','heat-treatment':'Heat treatment equipment','ore-crushing':'Ore crusher','mineral-separation':'Mineral separation equipment','dimensional-metrology':'Dimensional instruments','optical-metrology':'Optical instruments','crystal-growth':'Crystal growing equipment','wafer-preparation':'Wafer preparation equipment','doping':'Doping equipment','lithography':'Exposure equipment','mask-making':'Mask making equipment','etching':'Etching equipment','thin-film-deposition':'Deposition equipment','planarization':'Planarization equipment','integrated-circuit-fabrication':'Chip fabrication equipment','chip-packaging':'Chip packaging equipment','chip-test':'Chip test equipment','pcb-fabrication':'Circuit board equipment','plating':'Plating equipment','battery-production':'Battery making equipment','display-production':'Display making equipment','touch-production':'Touch panel equipment','optics-production':'Optics making equipment','magnetic-parts-production':'Magnetic parts equipment','acoustic-test':'Acoustic test equipment','camera-calibration':'Camera calibration equipment','sensor-calibration':'Sensor calibration equipment','rf-test':'Radio test equipment','thermal-test':'Thermal test equipment','handset-validation':'Phone test equipment','network-compatibility-test':'Network compatibility equipment','antenna-tuning':'Antenna tuning equipment','surface-cleaning':'Cleaning equipment','wire-drawing':'Wire drawing equipment','handset':'Working handset'}
for n in node_map.values():
    n['seed_proposed_requires'] = n.pop('proposed_requires', [])
    n['name'] = renames.get(n['id'], n['name'])
    if n['id'] in material_ids: n['role'] = 'part'
    n.update(maturity='proposed',research_status='discovered',evidence_status='knowledge-seed',inventory_complete=False,spec_reviewed=False,terminal=False,unresolved_questions=['Making route and target-level requirements not researched.'])

ids = {'inherited-phone':'handset','inherited-speaker':'speaker','inherited-coil':'voice-coil','inherited-coated':'insulated-wire','inherited-bare':'fine-copper-wire','inherited-rod':'copper-rod','inherited-refined':'refined-copper','inherited-native':'native-copper-stock','inherited-deposit':'native-copper-deposit','inherited-magnet':'permanent-magnet','inherited-iron':'iron-flux-parts','inherited-winding-fixture':'winding-fixture','inherited-alignment-fixture':'alignment-fixture','inherited-verification':'speaker-test-setup','inherited-power':'generator','inherited-ore':'copper-route-comparison','inherited-lithography':'lithography','inherited-foundations':'workshop-foundations'}
tool_pages = {'inherited-winding-fixture','inherited-alignment-fixture','inherited-verification','inherited-power','inherited-ore','inherited-lithography','inherited-foundations'}
aliases = {'soc':'processor','ram':'memory','flash storage':'storage','modem':'modem-baseband','rf amplifiers':'power-amplifiers','rf filters':'rf-filters','antennas':'antennas','sim or equivalent identity hardware':'sim-esim','pcb':'main-board','passives':'board-passives','audio electronics':'audio-codec','display stack':'display-panel','cover glass':'cover-glass','charging circuits':'charging-control','power-management circuits':'power-management','image sensors':'image-sensor','camera lenses':'camera-optics','microphone':'microphone','speaker':'speaker','heat spreaders':'thermal-system','haptic motor':'haptic-actuator','ports':'connectors','flexible circuits':'flexible-interconnect','connectors':'connectors','screws':'fasteners','seals':'seals','adhesives':'adhesives','adhesive':'adhesives','insulated copper voice coil':'voice-coil','permanent magnet':'permanent-magnet','soft-iron pole and return':'iron-flux-parts','winding fixture':'winding-fixture','winder + mandrel':'winding-fixture','alignment fixture':'alignment-fixture','meter':'meter','audio signal source':'audio-signal-source','audio amplifier':'audio-amplifier','measurement microphone':'measurement-microphone','power source':'regulated-power','dc electrical source':'regulated-power','controlled dc power source':'regulated-power','dimensional gauge':'dimensional-metrology','magnetic-field meter':'magnetic-field-meter','insulated wire':'insulated-wire','fine bare wire':'fine-copper-wire','copper rod':'copper-rod','refined copper':'refined-copper','recovered copper':'native-copper-stock','natural copper deposit':'native-copper-deposit','natural native copper':'natural-native-copper','clean water':'clean-water','water':'natural-water','calibration standards':'calibration-standards','earlier computer or programmer':'bootstrap-computer','electrical test instruments':'electrical-instruments','optical test instruments':'optical-metrology','acoustic test instruments':'acoustic-test','rf test instruments':'rf-test','bearings':'bearing-stock','fasteners':'fasteners','mechanical drive':'mechanical-power','lathe':'lathe','milling machine':'milling-machine','drill':'drill','silicon wafer':'silicon-wafer','photoresist':'photoresist','control software':'process-control','chip test instruments':'chip-test','reticle writer':'mask-making'}

def ensure(nid, name, role, domain, summary):
    if nid not in node_map:
        node_map[nid] = dict(id=nid,name=name,role=role,domain=domain,summary=summary,maturity='proposed',research_status='discovered',evidence_status='knowledge-seed',origin='inherited-requirement',inventory_complete=False,spec_reviewed=False,terminal=False,seed_proposed_requires=[],unresolved_questions=['Identified requirement; no researched making route or qualified output yet.'])
    return nid

for p in pages:
    nid = ids[p['id']]
    ensure(nid,p['name'],'tool' if p['id'] in tool_pages else 'part','inherited',p['summary'])

for p in pages:
    nid = ids[p['id']]
    n = node_map[nid]
    n.update(research_status='inherited',evidence_status='inherited-not-rechecked',origin='recovered-artifacts',summary=p['summary'],source_urls=p['sources'],provenance=p['provenance'],making_steps=p['steps'],unresolved_questions=p['gaps'],inventory_complete=False,spec_reviewed=False)
    n['required_inventory'] = []
    for role, names in [('part',p['known_parts']),('tool',p['known_tools'])]:
        for name in names:
            key = name.lower()
            target = aliases.get(key)
            if key == 'frame': target = 'speaker-frame' if p['id'] == 'inherited-speaker' else 'enclosure'
            if not target: target = slug(name)
            if target == nid:
                # This is output/operation context, not evidence for a self-making input.
                n.setdefault('inventory_context',[]).append({'name':name,'role':role,'reason':'Legacy list mixes output/operation context with input requirements; do not create a self dependency.'})
                continue
            ensure(target,name,role,n['domain'],'A requirement identified in recovered research; its making path remains open.')
            n['required_inventory'].append({'target':target,'label':name,'role':role,'status':'inherited candidate','required_capability':None,'compatibility':'unknown'})

# Only bounded conceptual recipes are selected for structural navigation.
# Comparisons/whole-industry notes stay unselected and their proposed links stay plain text.
selected_page_ids = set(ids) - {'inherited-phone','inherited-ore','inherited-lithography','inherited-foundations','inherited-verification','inherited-deposit'}
routes, selected = [], {}
for p in pages:
    if p['id'] not in selected_page_ids: continue
    nid = ids[p['id']]
    n = node_map[nid]
    seen = set()
    requirements=[]
    for req in n['required_inventory']:
        if req['target'] in seen: continue
        seen.add(req['target'])
        requirements.append({k:req[k] for k in ('target','role','required_capability','compatibility')})
    rid='route-'+nid+'-inherited-v1'
    routes.append(dict(id=rid,output=nid,requires=requirements,inventory_complete=False,reviewed=False,unresolved_questions=['Recovered conceptual route; complete prerequisites and flagship-quality capability are unverified.']))
    selected[nid]=rid

registry=dict(revision=1,target_version='v1',target='Flagship-equivalent handset compatible with real-world charging and networks',nodes=list(node_map.values()),routes=routes,scenarios=[dict(id='recovery-checkpoint-v1',roots=['handset'],selected_routes=selected,unresolved_questions=['Final quantitative target is not frozen; handset assembly route not selected.'])],revision_log=[dict(revision=1,outcome='initialized',reason='Recovery checkpoint, not an executable build plan.')])
report=validate_registry(registry)
HERE.joinpath('data').mkdir(exist_ok=True)
for name,data in [('registry.json',registry),('validation.json',report),('source-index.json',sources),('inherited-pages.json',pages),('seed-proposals.json',seed)]:
    (HERE/'data'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['graph-contract.md','recovered-prior.md','landscape.md']:
    shutil.copyfile(STAGING/name,HERE/'docs'/name)
print(json.dumps({'outputs':len(node_map),'inherited_pages':len(pages),'selected_draft_routes':len(routes),'known_requirements':sum(len(n.get('required_inventory',[])) for n in node_map.values()),'selected_dependency_edges':report['scenarios'][0]['counts']['dependency_edges'],'closed_to_nature':len(report['scenarios'][0]['closed_outputs'])}))
