"""Generate all research pages and the map from one cycle-validated registry."""
import html, json, re, shutil, sys, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from graph_gate import load_json, validate_registry
from discovery_audit import coverage, checked_trails
from agent_context import write_index, write_tool_bank
from research_ui import graph_model, item_status, badge, physical, path_tracker, parent_items, map_panel
from research_publication import checked_artifacts

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
DATA=ROOT/'data'
LOCAL_BUDGET_BYTES=25_000_000_000

def local_bytes():
    folders=(ROOT, ROOT.parent/'research-staging')
    return sum(p.stat().st_size for folder in folders for p in folder.rglob('*') if p.is_file())

if local_bytes()>LOCAL_BUDGET_BYTES:
    raise RuntimeError('Local research storage exceeds the authorized 25 GB budget')

def esc(s): return html.escape(str(s),quote=True)
def link_url(url,label=None):
    if urlparse(str(url)).scheme not in {'https','http'}: return esc(label or url)
    return '<a href="'+esc(url)+'" target="_blank" rel="noopener">'+esc(label or url)+'</a>'
artifact_pages={}
def rich(s, source_path=None):
    anchors=[]
    def anchor(match):
        anchors.append(link_url(match[2],match[1]))
        return 'LINKTOKEN'+str(len(anchors)-1)+'ENDTOKEN'
    s=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',anchor,str(s))
    if source_path:
        def local_anchor(match):
            target=(source_path.parent/match[2]).resolve()
            key=artifact_pages.get(target)
            if not key:return match[1]+' ('+match[2]+')'
            anchors.append('<a data-page="'+esc(key)+'" href="'+esc(key+'.html')+'">'+esc(match[1])+'</a>')
            return 'LINKTOKEN'+str(len(anchors)-1)+'ENDTOKEN'
        s=re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',local_anchor,s)
    s=esc(s)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'https?://[^\s<>\)]+',lambda m:link_url(html.unescape(m[0])),s)
    for i,a in enumerate(anchors):s=s.replace('LINKTOKEN'+str(i)+'ENDTOKEN',a)
    return s
def md(text, source_path=None):
    text=re.sub(r'<details>\s*<summary>(.*?)</summary>',r'\n## \1\n',text,flags=re.S)
    text=text.replace('</details>','')
    render=lambda value:rich(value,source_path)
    lines=text.splitlines(); out=[]; para=[]; in_list=False; i=0
    def flush():
        if para: out.append('<p>'+render(' '.join(para))+'</p>');para.clear()
    while i<len(lines):
        line=lines[i].strip()
        if line.startswith('|') and i+1<len(lines) and re.match(r'^\s*\|?\s*:?-{3}',lines[i+1]):
            flush()
            if in_list:out.append('</ul>');in_list=False
            headers=[t.strip() for t in line.strip('|').split('|')]
            out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+render(x)+'</th>' for x in headers)+'</tr></thead><tbody>');i+=2
            while i<len(lines) and lines[i].strip().startswith('|'):
                out.append('<tr>'+''.join('<td>'+render(x.strip())+'</td>' for x in lines[i].strip().strip('|').split('|'))+'</tr>');i+=1
            out.append('</tbody></table></div>');continue
        if line.startswith('#'):
            flush()
            if in_list:out.append('</ul>');in_list=False
            level=min(len(line)-len(line.lstrip('#')),4);label=line.lstrip('#').strip()
            out.append(f'<h{level}>'+render(label)+f'</h{level}>')
        elif re.match(r'^(- |\d+\. )',line):
            flush()
            if not in_list:out.append('<ul>');in_list=True
            out.append('<li>'+render(re.sub(r'^(- |\d+\. )','',line))+'</li>')
        elif not line:
            flush()
            if in_list:out.append('</ul>');in_list=False
        else:para.append(line)
        i+=1
    flush()
    if in_list:out.append('</ul>')
    return ''.join(out)

registry=load_json(DATA/'registry.json')
# Failure here aborts generation. No dependency link is emitted before this succeeds.
validation=validate_registry(registry)
scenario=validation['scenarios'][0]
nodes={n['id']:n for n in registry['nodes']}
research_artifacts={nid:checked_artifacts(ROOT,n) for nid,n in nodes.items()}
for artifacts in research_artifacts.values():
    for a in artifacts:
        artifact_pages[(ROOT/a['path']).resolve()]=a['page']
        if a.get('source_path'):artifact_pages[(ROOT/a['source_path']).resolve()]=a['page']
routes={r['id']:r for r in registry['routes']}
selection=registry['scenarios'][0]['selected_routes']
candidate_routes_by_output=defaultdict(list)
for rid,route in routes.items():
    if selection.get(route['output'])!=rid:candidate_routes_by_output[route['output']].append(route)
discovery=coverage(registry)
trails_path=DATA/'discovery-trails.json'
trails=[];stale_trails=[]
for trail in load_json(trails_path) if trails_path.exists() else []:
    try:trails.extend(checked_trails(registry,[trail]))
    except ValueError as exc:stale_trails.append({'name':trail.get('name','Resource trail'),'reason':str(exc)})
allowed=set(tuple(p) for p in scenario['structural_links'])
emitted=set()
sources=load_json(DATA/'source-index.json')
source_by_url={s['url']:s for s in sources}
seed=load_json(DATA/'seed-proposals.json')
seed_candidate_count=sum(len(n.get('proposed_requires',[])) for n in seed['nodes'])
counts=scenario['counts']
physical_nodes={nid:n for nid,n in nodes.items() if n.get('scope')!='black-box-software' and n.get('boundary')!='external' and n['role']!='external'}
ui_graph=graph_model(registry)
software_boundaries=[n for n in nodes.values() if n.get('scope')=='black-box-software']
status=Counter(n['research_status'] for n in physical_nodes.values())
inherited=sorted((n for n in nodes.values() if n['research_status']=='inherited'),key=lambda n:n['name'])
discovered=status['discovered'];total=len(physical_nodes)
unexpanded_physical=sum(nid in physical_nodes for nid in scenario['unexpanded_outputs'])
closed_count=counts['closed_outputs_excluding_terminals']
natural_count=counts['closed_natural_endpoints']
evidence_labels={'discovered':'Discovered · not researched','inherited':'Inherited notes',
    'research-draft':'Research draft','source-checked':'Source-checked','reviewed':'Reviewed',
    'experimentally-demonstrated':'Experimentally demonstrated'}
shared_requirements=Counter(req['target'] for rid in selection.values() for req in routes[rid]['requires'])
by_domain=defaultdict(list)
for n in physical_nodes.values():by_domain[n.get('domain') or 'workshop'].append(n)

def internal(key,label,**attrs):
    # Resolved href is generated for web pages AND for the standalone edition.
    indicator=''
    if key.startswith('nodes/') and key[6:] in physical_nodes:
        code,status_label=item_status(nodes[key[6:]],routes.get(selection.get(key[6:])))
        attrs.update(item_status=code)
        indicator=badge(code,status_label)
    return '<a data-page="'+esc(key)+'" '+''.join('data-'+k.replace('_','-')+'="'+esc(v)+'" ' for k,v in attrs.items())+'href="'+esc(key+'.html')+'">'+esc(label)+'</a>'+indicator
def node_link(nid,label=None):return internal('nodes/'+nid,label or nodes[nid]['name'],relation='navigation')
def dep_link(output,target,label):
    rid=selection[output]
    if (rid,target) not in allowed:raise ValueError('Attempt to render unapproved dependency '+rid+' -> '+target)
    emitted.add((rid,target))
    return internal('nodes/'+target,label,relation='dependency',dependency_source=rid,dependency_target=target)
def output_route_link(output):
    rid=selection[output]
    if (output,rid) not in allowed:raise ValueError('Unapproved route selection')
    emitted.add((output,rid))
    return '<a href="#making" data-relation="dependency" data-dependency-source="'+esc(output)+'" data-dependency-target="'+esc(rid)+'">Making steps</a>'
def stat(value,label):return '<div class="stat"><strong>'+esc(value)+'</strong><span>'+esc(label)+'</span></div>'
def node_table(items):
    return '<div class="table-wrap"><table class="inventory-table"><thead><tr><th>Item</th><th>Role</th><th>Evidence</th></tr></thead><tbody>'+''.join('<tr><td>'+node_link(n['id'])+'</td><td>'+esc(n['role'].title())+'</td><td>'+esc(evidence_labels.get(n['research_status'],n['research_status']))+'</td></tr>' for n in sorted(items,key=lambda n:n['name']))+'</tbody></table></div>'

pages={}
pages['index']=('<div class="eyebrow">Target v1 · graph revision '+str(registry['revision'])+' · review checkpoint</div><h1>Smartphone Building research</h1>'
    + '<p>Physical hardware for a flagship-equivalent handset from untouched Earth, ready for software installation, charging and real-world networks after import. Software implementation is a black box. This checkpoint recovers earlier research and exposes remaining work; it is not a complete manufacturing plan.</p>'
    + '<div class="stats">'+stat(total,'discovered items')+stat(str(round(100*discovered/total,1))+'%','discovered, unresearched ('+str(discovered)+'/'+str(total)+')')+stat(len(inherited),'inherited research pages')+stat(closed_count,'paths closed to nature')+'</div>'
    + '<div class="notice">'+internal('docs/research-rules','Read the research contract')+' and '+internal('docs/research-agent-prompt','agent prompt')+' for the scope. Bulk discovery and research were authorized on 8 October 2026. Numerical capability targets remain open. The saved batch includes the recovered chat and reports.</div>'
    + '<h2>Recovered research</h2><p>Inventories and sources are preserved. They have not been rechecked for completeness, tolerances or feasibility.</p>'+node_table(inherited)
    + '<h2>Explore the discovered map</h2><div class="domain-grid">'+''.join('<a data-page="map" href="map.html"><strong>'+esc(d.title())+'</strong><span>'+str(len(items))+' items</span></a>' for d,items in sorted(by_domain.items()))+'</div>'
    + '<h2>Known boundaries</h2><p>Cell towers, household outlets, standard external chargers and carrier services are external interfaces. Software implementation is a black box. Phone charging electronics, radios, antennas, computing and loading hardware, and manufacturing equipment remain in scope. External boundaries never count as natural endpoints.</p>')

pages['progress']=('<h1>Research progress</h1><p>Snapshot '+esc(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))+'. Denominators cover the discovered inventory at revision '+str(registry['revision'])+', not every requirement the project will eventually uncover.</p>'
    + '<div class="stats">'+stat(total,'discovered outputs')+stat(discovered,'not researched')+stat(len(inherited),'inherited notes')+stat(len(selection),'bounded draft routes')+'</div>'
    + '<table><thead><tr><th>Measure</th><th>Current value</th><th>Meaning</th></tr></thead><tbody>'
    + '<tr><td>Discovered but unresearched</td><td>'+str(discovered)+'/'+str(total)+' ('+str(round(100*discovered/total,1))+'%)</td><td>Items with no recovered making page or new research.</td></tr>'
    + '<tr><td>Inherited pages</td><td>'+str(len(inherited))+'</td><td>Prior conceptual notes with known inventories; not source-checked this turn.</td></tr>'
    + '<tr><td>Research drafts / source-checked / reviewed / experimentally demonstrated</td><td>'+str(status['research-draft'])+' / '+str(status['source-checked'])+' / '+str(status['reviewed'])+' / '+str(status['experimentally-demonstrated'])+'</td><td>Technical research, separate from graph software tests.</td></tr>'
    + '<tr><td>Selected draft routes / dependency edges</td><td>'+str(len(selection))+' / '+str(counts['dependency_edges'])+'</td><td>Cycle-checked structural links, with capability and inventory gaps.</td></tr>'
    + '<tr><td>Unexpanded physical outputs</td><td>'+str(unexpanded_physical)+'/'+str(total)+'</td><td>No selected making route; not natural endpoints.</td></tr>'
    + '<tr><td>Black-box software boundary records</td><td>'+str(len(software_boundaries))+'</td><td>Excluded from the physical research denominator; software development is outside scope.</td></tr>'
    + '<tr><td>Reviewed natural endpoints / closed manufacturing paths</td><td>'+str(natural_count)+' / '+str(closed_count)+'</td><td>Closure is calculated by the gate; physical acceptance is a separate claim.</td></tr>'
    + '<tr><td>Unselected seed relationship proposals</td><td>'+str(seed_candidate_count)+'</td><td>Older hypotheses; cyclic and alternative-mixing suggestions remain staged.</td></tr>'
    + '<tr><td>Declared selected cycles</td><td>0</td><td>Code validation succeeded; this is not a feasibility result.</td></tr></tbody></table>'
    + '<h2>What actually ends?</h2>'+(('<p>Reviewed natural endpoints: '+', '.join(node_link(nid) for nid in scenario['natural_endpoints'])+'</p>') if natural_count else '<p>No reviewed natural endpoints yet. Native copper occurrence, natural water and host rock remain candidates with unresolved availability, recognition and acquisition.</p>')
    + ('<p>Closed manufacturing outputs: '+', '.join(node_link(nid) for nid in scenario['closed_outputs'] if nid not in scenario['natural_endpoints'])+'</p>' if closed_count else '')
    + '<h2>Open frontiers</h2><p>'+str(unexpanded_physical)+' physical items still need a selected making route. Their individual pages show current unknowns. Software implementation records are excluded.</p>'+internal('map','Browse all open items')
    + '<h2>Next research sequence</h2><p>Freeze measurable flagship targets; research natural-resource acquisition and non-electrical coarse tooling; establish reference surfaces and earlier power; then trace copper, wire and speaker quality. Dedicated reviews cover glass, batteries, display, semiconductor tooling, physical control/loading interfaces and real-network compatibility.</p>'
    + '<h2>Shared prerequisites to investigate for reuse</h2><p>Counts show selected routes calling the same record, not available physical stock. Capability and build-order qualification are still required.</p><ul>'+''.join('<li>'+node_link(nid)+' — '+str(amount)+' routes</li>' for nid,amount in shared_requirements.most_common(10) if amount>1)+'</ul>'
    + '<h2>Code gate</h2><p>21 adversarial checks passed for self-loops, multi-node and concurrent cycles, stale revisions, missing targets, false terminals, unreviewed capabilities, unspecified demands and atomic failure. Every generated dependency link is matched against the validated graph and its actual destination.</p>'+internal('docs/graph-gate-readme','Read the gate guarantees and limits')
    + '<h2>Storage and publishing</h2><p>The user has allocated about 25 GB on this computer. The build checks that local project and recovery files stay within that budget. Text, code and source links remain compact; cloud storage for larger attachments is undecided. The standalone edition remains usable offline; the private hosted edition supplies the same validated reading pages and a compressed standalone download.</p>'+internal('docs/storage-plan','Read the storage options'))

pages['map']='<h1>Discovered map</h1><p>Explore the physical inventory below. Linked routes are cycle-checked discovery or research hypotheses. Their inventories, capability demands and resource availability remain open.</p>'
pages['map']+=map_panel(ui_graph,internal('map-view','⛶ Expand map'))
pages['map-view']='<div class="map-expanded"><h1>Dependency map</h1>'+map_panel(ui_graph,internal('map','Back to overview'),expanded=True)+'</div>'
pages['map']+='<label>Find an item or requirement <input type="search" placeholder="Try speaker, silicon, clay…" style="display:block;width:100%;padding:12px;margin:8px 0;border:1px solid #9cb7ae;border-radius:6px;font:inherit" oninput="const q=this.value.toLowerCase();document.querySelectorAll(\'.route,.inventory-table tbody tr\').forEach(e=>e.hidden=!e.textContent.toLowerCase().includes(q));"></label>'
pages['map']+='<div class="stats">'+stat(total,'physical items')+stat(len(selection),'linked draft routes')+stat(discovery['maximum_shortest_level'],'deepest shortest level')+stat(len(discovery['gaps_before_level_5']),'open frontiers before level 5')+'</div>'
pages['map']+='<h2>Discovery depth</h2><p>The handset is level 0. Each physical requirement adds one level; recipe records add none. Shared items appear at their shortest distance. Counts measure the declared map, not the unknown total inventory.</p><table><thead><tr><th>Level</th><th>Items</th><th>Expanded hypotheses</th><th>Open frontiers</th><th>Raw occurrence candidates</th></tr></thead><tbody>'
for level in discovery['levels']:
    pages['map']+='<tr><td>'+str(level['level'])+'</td><td>'+str(len(level['items']))+'</td><td>'+str(level['expanded'])+'</td><td>'+str(len(level['unexpanded']))+'</td><td>'+str(len(level['candidate_occurrences']))+'</td></tr>'
pages['map']+='</tbody></table><p>'+str(discovery['reachable_physical_outputs'])+' physical outputs are linked from the handset; '+str(len(discovery['unreachable_physical_outputs']))+' remain outside that root map. Expanding an item does not establish a complete inventory.</p>'
if trails:
    pages['map']+='<h2>Trails toward raw materials</h2><p>These trails follow the linked graph to natural occurrence candidates. They are discovery paths; collection, location, usable quantity, quality and all other branch prerequisites still need review.</p>'
    for trail in trails:
        pages['map']+='<section class="route"><h3>'+esc(trail['name'])+'</h3><p>'+' → '.join(node_link(nid) for nid in trail['path'])+'</p><p>'+esc(trail.get('limitations','No manufacturing closure is claimed.'))+'</p></section>'
if stale_trails:
    pages['map']+='<details><summary>Previous resource highlights awaiting retracing · '+str(len(stale_trails))+'</summary><p>Selected recipes changed. These old paths are withheld until they follow the current graph.</p><ul>'+''.join('<li>'+esc(t['name'])+'</li>' for t in stale_trails)+'</ul></details>'
if 'handset' in selection:
    pages['map']+='<h2>Start with the handset</h2><p>Open an assembly, then follow its required Parts and Tools. Each page carries its current unknowns.</p><div class="domain-grid">'+''.join('<div>'+dep_link('handset',r['target'],nodes[r['target']]['name'])+'</div>' for r in routes[selection['handset']]['requires'])+'</div>'
pages['map']+='<h2>Frontiers before level 5</h2><p>These are the next breadth-first assignments. Raw occurrence candidates are listed separately and are not approved natural endpoints.</p><details><summary>'+str(len(discovery['gaps_before_level_5']))+' unresolved expansion fronts</summary><ul>'+''.join('<li>Level '+str(discovery['distance'][nid])+' · '+node_link(nid)+'</li>' for nid in sorted(discovery['gaps_before_level_5'],key=lambda nid:(discovery['distance'][nid],nodes[nid]['name'])))+'</ul></details>'
pages['map']+='<noscript><h2>Linked draft routes</h2><p>All known required inputs in each selected hypothesis are shown here. Unselected recipes and old seed suggestions remain separate.</p>'
for output,rid in sorted(selection.items()):
    pages['map']+='<details class="route"><summary>'+esc(nodes[output]['name'])+' · '+str(len(routes[rid]['requires']))+' requirements</summary><h3>'+node_link(output)+'</h3><p>'+', '.join(dep_link(output,r['target'],nodes[r['target']]['name']) for r in routes[rid]['requires'])+'</p></details>'
pages['map']+='<h2>Complete discovered inventory</h2>'+''.join('<section id="'+esc(d)+'"><h3>'+esc(d.title())+' · '+str(len(items))+'</h3>'+node_table(items)+'</section>' for d,items in sorted(by_domain.items()))
pages['map']+='<h2>Software black boxes</h2><p>These boundary records are retained for interfaces and provenance, not software manufacture.</p>'+node_table(software_boundaries)
pages['map']+='</noscript><p class="small">Open a linked item for its complete selected inventory, making outline and path tracker. The accessible list above pages through the full physical inventory; the full inventory also remains available with JavaScript disabled.</p>'

for nid,n in nodes.items():
    if n.get('scope')=='black-box-software':
        pages['nodes/'+nid]='<div class="eyebrow">Software boundary · outside manufacturing research</div><h1>'+esc(n['name'])+'</h1><p>Implementation is a black box under the user\'s scope allowance. Compatible software may be installed on the phone after import into the real world.</p><p>Specify its required function and hardware interfaces. Physical host, memory, controllers, loading fixtures, cables and power remain explicit wherever needed. A program required during fabrication needs an earlier availability stage; final handset installation cannot power an earlier process.</p><p>This boundary is excluded from research-completion percentages and never counts as a natural endpoint.</p>'+internal('map','Return to the map')
        continue
    role=n['role'].title();is_inherited=n['research_status']=='inherited'
    assessment=n.get('reuse_assessment',{})
    frontier_description=assessment.get('reason',assessment.get('decision','')) if isinstance(assessment,dict) else ''
    summary=n.get('summary') or frontier_description or 'A discovered physical requirement. Its caller-specific capability and making inventory remain open.'
    body='<div class="eyebrow">'+esc(role)+' · '+esc(n.get('domain') or 'workshop')+'</div><h1>'+esc(n['name'])+'</h1><p>'+esc(summary)+'</p>'
    closure_label='External interface' if n.get('boundary')=='external' or n['role']=='external' else ('Closed to nature' if scenario['closure'][nid] else ('Blocked' if n.get('blockers') else 'Open'))
    body+='<p class="status"><span>'+esc(item_status(n,routes.get(selection.get(nid)))[1])+'</span><span>Closure: '+closure_label+'</span><span>Inventory '+('declared complete' if n['inventory_complete'] else 'incomplete')+'</span></p>'
    if n.get('research_activity'):
        activity=n['research_activity']
        body+='<section class="research-publication"><h2>Saved research and review</h2><p>'+esc(activity.get('scope',''))+'</p><p>'+esc(activity.get('reason',''))+'</p><p>Evidence review is separate from immediate-record completeness, current recipe qualification and manufacturing closure. Reports retain their original scope; later engineering changes require their own review.</p>'
        if activity.get('report_scope_revision') is not None:
            body+='<p class="small">Saved report scope revision '+esc(activity['report_scope_revision'])+' · independent review revision '+esc((activity.get('review') or {}).get('revision','pending'))+' · current graph revision '+str(registry['revision'])+'. Earlier claims about preserved inventories apply to their saved scope, not automatically to later enlarged selected routes.</p>'
        if research_artifacts[nid]:
            body+='<ul>'+''.join('<li>'+internal(a['page'],a['label'],research_path=a['path'],research_sha256=a['sha256'])+' <span class="small">'+esc(a['kind'])+' · SHA256 '+esc(a['sha256'])+'</span></li>' for a in research_artifacts[nid])+'</ul>'
        else:body+='<p>No completed report is attached yet. Assignment/activity is recorded; report completion is not inferred.</p>'
        body+='</section>'
    if n.get('discovery_leaf_kind')=='candidate-natural-occurrence':
        body+='<div class="notice">Candidate natural occurrence. Availability, recognition, usable quantity and acquisition have not been approved. This is not a closed natural endpoint.</div>'
    own_complete=item_status(n,routes.get(selection.get(nid)))[0]=='researched'
    capability_text=('This immediate record has a reviewed specification and complete reviewed inventory/making route. Descendant availability, actual manufacture and closure remain separately tracked; read the recorded specification and review scope below.' if own_complete else 'Consumer-specific numerical targets, quantities and acceptance limits remain open or incompletely reviewed. No smartphone-grade suitability is claimed. Distinct capability tiers require their own making route and qualification.')
    body+='<details><summary>Capability requirements and tolerances</summary><p>'+capability_text+'</p></details>'
    if nid in selection:body+='<p>'+output_route_link(nid)+(' · reviewed immediate making record; actual manufacture and descendant closure are separate.' if own_complete else ' · draft selected for navigation; not a validated fabrication specification.')+'</p>'
    inv=n.get('required_inventory',[])
    if nid in selection:
        legacy_labels={r['target']:r.get('label',nodes[r['target']]['name']) for r in inv if r.get('target') in nodes}
        inv=[{'target':r['target'],'label':legacy_labels.get(r['target'],nodes[r['target']]['name']),
              'role':nodes[r['target']]['role'],'compatibility':r.get('compatibility','unknown'),
              'use':r.get('use','Use and allocation not yet specified')} for r in routes[selection[nid]]['requires']]
    if inv:
        body+='<h2>Known Parts and Tools</h2><p>The selected route supplies this page\'s inventory and the map\'s dependency links from one record. Further requirements may be missing; review flags do not prove physical suitability.</p><div class="table-wrap"><table><thead><tr><th>Requirement</th><th>Role</th><th>Use</th><th>Relationship status</th></tr></thead><tbody>'
        for req in inv:
            target=nodes.get(req.get('target'),{})
            label=req.get('label') or target.get('name') or req.get('name') or req.get('target','Unspecified requirement')
            name=dep_link(nid,req['target'],label) if nid in selection else esc(label)
            body+='<tr><td>'+name+'</td><td>'+esc(req.get('role',target.get('role','part')).title())+'</td><td>'+esc(req.get('use','Use and allocation not yet specified'))+'</td><td>'+('Cycle-checked; compatibility '+esc(req['compatibility']) if nid in selection else 'Unselected proposal')+'</td></tr>'
        body+='</tbody></table></div>'
    else:body+='<h2>Parts and Tools needed</h2><p>No researched inventory yet. This is an unexpanded frontier; an empty list does not mean the item can be obtained directly from nature.</p>'
    candidates=candidate_routes_by_output.get(nid,[])
    if candidates:
        body+='<details><summary>Unselected candidate inventories · '+str(len(candidates))+'</summary><p>These records expose known requirements and alternative or blocked hypotheses. They add no manufacturing links or selected discovery depth.</p>'
        for candidate in candidates:
            body+='<h3>'+esc(candidate.get('name',candidate.get('hypothesis',candidate['id'])))+'</h3><p>'+esc(candidate.get('method_summary',candidate.get('hypothesis','Method remains open.')))+'</p><ul>'+''.join('<li>'+esc(nodes[q['target']]['name'])+' · '+esc(q['role'])+'</li>' for q in candidate['requires'])+'</ul>'
            body+='<p>'+esc(' '.join(candidate.get('unresolved_questions',[])))+'</p>'
        body+='</details>'
    software_requirements=routes[selection[nid]].get('software_requirements',[]) if nid in selection else n.get('software_requirements',[])
    if software_requirements:
        body+='<details><summary>Black-box software requirements</summary><pre>'+esc(json.dumps(software_requirements,indent=2))+'</pre></details>'
    if n.get('inventory_context'):
        body+='<details><summary>Legacy inventory corrections</summary>'+''.join('<p>'+esc(c['name'])+': '+esc(c['reason'])+'</p>' for c in n['inventory_context'])+'</details>'
    if n.get('making_steps'):
        body+='<h2 id="making"'+(' data-route-id="'+esc(selection[nid])+'"' if nid in selection else '')+'>Making outline</h2><ol>'
        for step in n['making_steps']:
            if isinstance(step,dict):step=' — '.join(str(v) for v in step.values())
            body+='<li>'+esc(step)+'</li>'
        body+='</ol>'
    elif nid in selection:
        body+='<h2 id="making" data-route-id="'+esc(selection[nid])+'">Making outline</h2><p>Steps not yet researched.</p>'
    body+='<h2>What remains unresolved</h2><ul>'+''.join('<li>'+esc(q)+'</li>' for q in n.get('unresolved_questions',[]))+'</ul>'
    if n.get('seed_proposed_requires'):
        body+='<details><summary>Unselected discovery proposals</summary><p>These are research questions, not published manufacturing dependencies. The seed combines alternatives, operating requirements and verification relationships.</p><p>'+', '.join(esc(nodes[t]['name']) for t in n['seed_proposed_requires'])+'</p></details>'
    if n.get('source_urls'):
        body+='<h2>Sources and leads</h2><p>Source scope and research notes determine which claims have been checked. A URL does not establish a complete making route.</p><ul>'
        for url in n['source_urls']:
            src=source_by_url.get(url,{})
            body+='<li>'+link_url(url,src.get('title',url))+'</li>'
        body+='</ul>'
    for field,label in [('source_claims','Source claim scope'),('reuse_assessment','Canonical reuse assessment'),('specification','Proposed capability specification')]:
        if n.get(field):
            body+='<details><summary>'+label+'</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+esc(json.dumps(n[field],indent=2,ensure_ascii=False))+'</pre></details>'
    if n.get('provenance'):
        body+='<details><summary>Earlier research provenance</summary><ul>'+''.join('<li>'+esc(p)+'</li>' for p in n['provenance'])+'</ul></details>'
    if n.get('bounded_research_pages'):
        body+='<h2>Bounded research drafts</h2><p>Read the source scope, known inventory and remaining limitations. These drafts do not approve the complete selected route.</p><ul>'+''.join('<li>'+internal(key,'Read '+key.split('/')[-1].replace('-',' '))+'</li>' for key in n['bounded_research_pages'])+'</ul>'
    body+='<p>'+internal('map','Return to the discovered map')+'</p>'
    if nid in physical_nodes:
        body+=parent_items(ui_graph,nid,node_link)
        body+=path_tracker(ui_graph,nid,node_link)
    pages['nodes/'+nid]=body

for file in (ROOT/'docs').glob('*.md'):
    pages['docs/'+file.stem]=md(file.read_text(encoding='utf-8-sig'))
for artifacts in research_artifacts.values():
    for a in artifacts:
        path=ROOT/a['path']
        content=path.read_text(encoding='utf-8-sig')
        content=md(content,ROOT/a.get('source_path',a['path'])) if path.suffix=='.md' else '<pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+esc(content)+'</pre>'
        origin='Original source '+esc(a['source_path'])+' · original SHA256 '+a['source_sha256']+' · immutable published snapshot '+esc(a['path']) if a.get('immutable_snapshot') else esc(a['path'])
        pages[a['page']]='<section data-research-artifact-page-path="'+esc(a['path'])+'" data-research-artifact-page-sha256="'+a['sha256']+'"><h1>'+esc(a['label'])+'</h1><p class="small">Saved '+esc(a['kind'])+' · '+origin+' · SHA256 '+a['sha256']+'</p><p class="notice">Bounded research/review evidence. This artifact does not certify physical manufacturing closure or later changed routes.</p>'+content+'</section>'
draft_readings={
    'bootstrap-copper':'research/copper.md','bootstrap-ignition':'research/ignition.md',
    'bootstrap-cord':'research/cord.md','bootstrap-clay-vessel':'research/clay-vessel.md',
    'mems-research':'research/mems/report.md',
    'electrolyte-research':'materials/breadth-pass-03-making-page.md'}
for key,rel in draft_readings.items():
    path=ROOT/'proposals/2026-10-08-discovery'/rel
    if path.exists():
        text=path.read_text(encoding='utf-8-sig')
        text=re.sub(r'<details><summary>(.*?)</summary>',r'\n## \1\n',text)
        text=text.replace('</details>','')
        pages['docs/'+key]=md(text)
if 'docs/discovery-batch-02' in pages:
    pages['docs/discovery-batch-02']+='<h2>Read the full bounded drafts</h2><ul>'+''.join('<li>'+internal('docs/'+key,key.replace('-',' ').title())+'</li>' for key in draft_readings if 'docs/'+key in pages)+'</ul>'
    pages['index']+='<h2>Coordinated discovery and research</h2><p>'+internal('docs/discovery-batch-02','Read the current checkpoint and findings')+'. The map reports expanded hypotheses, unresolved frontiers and candidate raw-material trails separately from manufacturing closure.</p>'
if 'docs/research-batch-01' in pages:
    pages['index'] += '<h2>Saved research batch 01</h2><p>Four researcher reports and the independent review have been recovered as drafts. '+internal('docs/research-batch-01','Read the findings and recovery status')+'. The checkpoint archive includes the complete reports and retrieved conversation records.</p>'
pages['docs/graph-gate-readme']=md((ROOT/'graph-gate-readme.md').read_text(encoding='utf-8-sig'))
pages['sources']='<h1>Source index</h1><p>'+str(len(sources))+' unique technical URLs. Records distinguish inherited leads from newly checked claims; neither establishes a complete manufacturing route.</p><ol>'
for s in sources:
    pages['sources']+='<li>'+link_url(s['url'],s.get('title',s['url']))+'<p class="small">'+esc(s.get('topic',''))+' · '+esc(s.get('status','source lead'))+'</p></li>'
    if s.get('claim_scopes'):
        pages['sources']+='<details><summary>Recorded claim scope and limitations</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+esc(json.dumps(s['claim_scopes'],indent=2,ensure_ascii=False))+'</pre></details>'
pages['sources']+='</ol>'
pages['downloads']='<h1>Download and continue</h1><p>The research record uses portable JSON and Markdown. The same validated record generates the map, manufacturing links and reading pages.</p><ul><li><a href="research-data.json" download>Dependency registry (JSON)</a></li><li><a href="research-validation.json" download>Graph validation report</a></li><li><a href="research-sources.json" download>Recovered source index</a></li><li><a href="smartphone-research.html" download>Standalone linked research edition</a></li></ul><p>Coordinated discovery and research are active under the research contract. The full source archive is delivered with the chat.</p>'

# Exact link set: every published making edge has passed the gate; no declared edge is hidden.
if emitted != allowed:
    raise ValueError('Dependency rendering differs from validated graph: '+str(allowed-emitted)+' / '+str(emitted-allowed))

css='''*{box-sizing:border-box}body{margin:0;background:#fbfcfa;color:#19312f;font:16px/1.55 system-ui,sans-serif}a{color:#136b7b;text-underline-offset:3px}a:hover{color:#093b47}header{padding:16px 24px;border-bottom:1px solid #d6e1da;background:#fff;position:sticky;top:0;z-index:1}header strong{margin-right:24px}nav{display:inline-flex;gap:18px;flex-wrap:wrap}main{max-width:1050px;margin:auto;padding:30px 24px 70px}h1{font-size:34px;line-height:1.2;margin:10px 0 20px}h2{font-size:23px;margin:32px 0 12px}h3{font-size:19px;margin:20px 0 8px}p{margin:12px 0}li{margin:6px 0}code{overflow-wrap:anywhere;font-size:.9em}details{background:#f1f5ee;border:1px solid #d9e2d3;border-radius:8px;padding:12px 16px;margin:14px 0}summary{cursor:pointer;font-weight:600}.eyebrow,.small{font-size:14px;color:#526960}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.stat{padding:18px;background:#fff;border:1px solid #d3dfd8;border-top:3px solid #47a08c;border-radius:8px}.stat strong{display:block;font-size:28px;line-height:1.2}.stat span{display:block;font-size:14px;margin-top:8px}.notice{padding:16px;background:#fff6da;border-left:4px solid #d8a746}.domain-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.domain-grid a{background:white;border:1px solid #d3dfd8;padding:14px;border-radius:8px;text-decoration:none}.domain-grid span{display:block;color:#596c66;font-size:14px}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;margin:12px 0;font-size:15px}td,th{padding:10px 12px;text-align:left;border-bottom:1px solid #d6e0da;vertical-align:top}th{background:#edf3ed}tr:nth-child(even){background:#fff}.status{display:flex;flex-wrap:wrap;gap:8px}.status span{background:#e7f0ec;padding:4px 9px;font-size:14px;border-radius:4px}.route{padding:8px 18px;border-left:3px solid #7daca0;background:#fff;margin:12px 0}.route h3{margin:8px 0}footer{padding:16px 24px;border-top:1px solid #d6e1da;font-size:14px;color:#526960}.hidden{display:none}@media(max-width:650px){main{padding:22px 16px 50px}header{padding:12px 16px;position:static}header strong{display:block;margin-bottom:8px}nav{gap:10px 16px;font-size:14px}h1{font-size:27px}.stats{grid-template-columns:repeat(2,1fr)}.domain-grid{grid-template-columns:repeat(2,1fr)}td,th{padding:8px}table{font-size:14px}.stat strong{font-size:25px}}'''
favicon='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect x=%228%22 y=%223%22 width=%2216%22 height=%2226%22 rx=%224%22 fill=%22%23136b7b%22/%3E%3Ccircle cx=%2216%22 cy=%2224%22 r=%222%22 fill=%22%23ffe1a0%22/%3E%3C/svg%3E'
css+=(ROOT/'scripts/assets/research-ui.css').read_text(encoding='utf-8')
ui_script=(ROOT/'scripts/assets/research-ui.js').read_text(encoding='utf-8')
graph_script='window.RESEARCH_GRAPH='+json.dumps(ui_graph,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';'
navkeys=[('index','Research'),('progress','Progress'),('map','Map'),('docs/research-rules','Rules'),('docs/research-agent-prompt','Agent prompt'),('sources','Sources'),('downloads','Download')]
shell_head='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Smartphone manufacturing research, dependency inventory and progress"><link rel="icon" href="'+favicon+'"><style>'+css+'</style><title>Smartphone Building research</title></head><body><header><strong>Smartphone Building</strong><nav>'+''.join(internal(k,label) for k,label in navkeys)+'</nav></header>'
shell_footer='<footer>Target v1 · recovered notes and discovery drafts · no path yet verified to natural resources</footer></body></html>'
OUT.mkdir(exist_ok=True)
(OUT/'assets').mkdir(exist_ok=True)
(OUT/'assets/physical-graph.js').write_text(graph_script,encoding='utf-8')
(OUT/'assets/research-ui.js').write_text(ui_script,encoding='utf-8')
for key,body in pages.items():
    file=OUT/(key+'.html');file.parent.mkdir(parents=True,exist_ok=True)
    depth=len(Path(key).parts)-1;prefix='../'*depth
    page_head=shell_head.replace('<body>','<body class="map-view-page">') if key=='map-view' else shell_head
    document=page_head+'<main>'+body+'</main><script>window.RESEARCH_ASSET_BASE="'+(prefix.rstrip('/') or '.')+'";</script><script src="'+prefix+'assets/physical-graph.js"></script><script src="'+prefix+'assets/research-ui.js"></script>'+shell_footer
    # Pages stay readable with JavaScript disabled. The standalone version uses the same bodies.
    document=re.sub(r'href="((?:nodes|docs|research-artifacts)/[^"#]+\.html|(?:index|progress|map|sources|downloads)\.html)(#[^"]*)?"',lambda m:'href="'+prefix+m[1]+(m[2] or '')+'"',document)
    file.write_text(document,encoding='utf-8')

payload=json.dumps(pages,ensure_ascii=False).replace('</','<\\/')
standalone=shell_head+'<main id="content">'+pages['index']+'</main><script>window.RESEARCH_STANDALONE=true;'+graph_script+'</script><script>'+ui_script+'</script><script>const pages='+payload+''';function render(){const key=decodeURIComponent(location.hash.slice(1))||'index';document.querySelectorAll('.dot-map').forEach(e=>e._dispose?.());document.getElementById('content').innerHTML=pages[key]||pages.index;document.querySelectorAll('a[data-page]').forEach(a=>a.href='#'+encodeURIComponent(a.dataset.page));document.querySelectorAll('a[href="research-data.json"],a[href="research-validation.json"],a[href="research-sources.json"],a[href="smartphone-research.html"]').forEach(a=>{a.removeAttribute('download');a.onclick=e=>{e.preventDefault();alert('Use the separate source archive supplied with the chat for data files.');};});document.title=(document.querySelector('main h1')?.textContent||'Research')+' · Smartphone Building';window.scrollTo(0,0);ResearchUI.init();}window.addEventListener('hashchange',render);render();</script>'''+shell_footer
standalone=standalone.replace("window.addEventListener('hashchange',render);", "document.addEventListener('click',e=>{const a=e.target.closest('a[href=\"#making\"]');if(a){e.preventDefault();document.getElementById('making')?.scrollIntoView();}});window.addEventListener('hashchange',render);")
standalone=standalone.replace("document.getElementById('content').innerHTML=pages[key]||pages.index;",
                              "document.body.classList.toggle('map-view-page',key==='map-view');document.getElementById('content').innerHTML=pages[key]||pages.index;")
(OUT/'smartphone-research.html').write_text(standalone,encoding='utf-8')
(DATA/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
(DATA/'discovery-coverage.json').write_text(json.dumps(discovery,indent=2)+'\n',encoding='utf-8')
(DATA/'stale-discovery-trails.json').write_text(json.dumps(stale_trails,indent=2)+'\n',encoding='utf-8')
write_index(registry,DATA/'registry.json',DATA/'agent-index.jsonl')
write_tool_bank(registry,DATA)
for a,b in [('registry.json','research-data.json'),('validation.json','research-validation.json'),('source-index.json','research-sources.json')]:shutil.copyfile(DATA/a,OUT/b)
# Keep the offline HTML intact; Sites has a 25 MiB per-file hosting limit.
hosted=ROOT/'out'
shutil.copytree(OUT,hosted,dirs_exist_ok=True,ignore=shutil.ignore_patterns('smartphone-research.html'))
download_page=hosted/'downloads.html'
download_page.write_text(download_page.read_text(encoding='utf-8').replace('href="smartphone-research.html"','href="smartphone-research.zip"').replace('Standalone linked research edition</a>','Standalone linked research edition (ZIP)</a>'),encoding='utf-8')
with zipfile.ZipFile(hosted/'smartphone-research.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    archive.write(OUT/'smartphone-research.html','smartphone-research.html')
if any(p.stat().st_size>26_214_400 for p in hosted.rglob('*') if p.is_file()):
    raise RuntimeError('Hosted output exceeds the 25 MiB per-file limit')
size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
snapshot={'target_version':'v1','graph_revision':registry['revision'],'outputs':total,'unresearched':discovered,'unresearched_percent':round(100*discovered/total,1),'inherited_pages':len(inherited),'selected_routes':len(selection),'dependency_edges':len(allowed),'natural_endpoints':0,'closed_paths':0,'source_urls':len(sources),'html_pages':len(pages),'static_bytes':size,'dependency_link_audit':'all published dependency links match validated selected graph','bulk_research':'authorized 2026-10-08; coordinated discovery and research','hosting':'private Sites publication configured; exact standalone edition supplied as a compressed download'}
(DATA/'checkpoint.json').write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
snapshot.update(local_bytes=local_bytes(),local_budget_bytes=LOCAL_BUDGET_BYTES)
snapshot.update(natural_endpoints=natural_count,closed_paths=closed_count,evidence_counts=dict(status))
snapshot.update(all_registry_outputs=len(nodes),black_box_software_records=len(software_boundaries),unexpanded_physical_outputs=unexpanded_physical)
snapshot.update(discovery_reachable=discovery['reachable_physical_outputs'],discovery_maximum_shortest_level=discovery['maximum_shortest_level'],discovery_frontiers_before_level_5=len(discovery['gaps_before_level_5']),highlighted_raw_material_trails=len(trails))
if snapshot['local_bytes']>LOCAL_BUDGET_BYTES:
    raise RuntimeError('Generated project exceeds the authorized local storage budget')
(DATA/'checkpoint.json').write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
print(json.dumps(snapshot))
