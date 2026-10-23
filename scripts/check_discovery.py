"""Normalize a compact memory-first discovery batch and probe the entire graph."""
import argparse
import copy
import json
from pathlib import Path
from graph_gate import GateError, load_json, validate_registry

ROOT=Path(__file__).resolve().parents[1]


def probe(registry,draft):
    if draft.get('base_revision')!=registry['revision']:
        raise GateError('stale_revision','Discovery draft must use its supplied snapshot revision.')
    validate_registry(registry)
    candidate=copy.deepcopy(registry)
    nodes={n['id']:n for n in candidate['nodes']}
    routes={r['id']:r for r in candidate['routes']}
    changed_nodes={};changed_routes={}
    for item in draft.get('new_items',[]):
        nid=item['id']
        if nid in nodes:raise GateError('duplicate_identity','New ID already exists; reuse its record.',id=nid)
        role=item['role'].lower()
        if role not in {'part','tool'}:raise GateError('role','New physical items must be Parts or Tools.',id=nid)
        n={'id':nid,'name':item['name'],'role':role,'domain':item.get('domain','discovery'),
           'summary':item.get('function','Discovered physical requirement; caller demands remain open.'),
           'aliases':item.get('aliases',[]),'terminal':False,'maturity':'proposed',
           'research_status':'discovered','evidence_status':'memory-first-discovery',
           'inventory_complete':False,'spec_reviewed':False,
           'unresolved_questions':['Manufacture, quantities, suitability and complete inventory remain unreviewed.'],
           'reuse_assessment':item.get('reuse_assessment','New provisional identity; coordinator reuse review pending.')}
        if item.get('candidate_natural_occurrence'):n['discovery_leaf_kind']='candidate-natural-occurrence'
        nodes[nid]=n;changed_nodes[nid]=n

    def resolve(value):
        if value in nodes:return value
        matches=[nid for nid,n in nodes.items() if value.casefold() in
                 [str(x).casefold() for x in [n['name']]+n.get('aliases',[])]]
        if len(matches)!=1:raise GateError('identity','Requirement name must resolve to exactly one ID.',name=value,matches=matches)
        return matches[0]

    scenario=candidate['scenarios'][0]
    expanded_outputs=set()
    for item in draft.get('expansions',[]):
        output=resolve(item['output']);n=nodes[output]
        if output in expanded_outputs:raise GateError('duplicate_expansion','Choose one method per output in a batch.',id=output)
        expanded_outputs.add(output)
        if n['terminal'] is not False:raise GateError('terminal','Do not expand a reviewed occurrence into a making route; use a collected-stock state.',id=output)
        method=item['method'];requirements=[]
        for q in item['requires']:
            if isinstance(q,str):q={'target':q}
            target=resolve(q['target']);child=nodes[target]
            if child.get('scope')=='black-box-software' or child.get('boundary')=='external':
                raise GateError('boundary','Software/services belong in boundary metadata, not manufactured inputs.',id=target)
            role=q.get('role',child['role'])
            if role not in {'part','tool','verification','utility'}:raise GateError('role','Invalid requirement role.',id=target)
            if (child['role']=='tool' and role=='part') or (child['role']=='part' and role=='tool'):
                raise GateError('role_mismatch','Caller classification conflicts with canonical identity.',id=target)
            requirements.append({'target':target,'role':role,'use':q.get('use','Use/allocation not yet specified'),
                                 'required_capability':{'function':q.get('reason','Required for '+method),'limits':'not yet specified'},
                                 'compatibility':'unknown'})
        if len({q['target'] for q in requirements})!=len(requirements):
            raise GateError('duplicate_requirement','Combine multiple uses of one ID rather than duplicating its row.',id=output)
        rid=item.get('route_id','discovery-memory-'+output+'-v1')
        route={'id':rid,'output':output,'name':method,'requires':requirements,
               'inventory_complete':False,'reviewed':False,'research_status':'discovered',
               'unresolved_questions':item.get('unknowns',[])+['Memory-first hypothesis; inventory and compatibility unreviewed.']}
        n['prior_discovery_outline']={k:copy.deepcopy(n[k]) for k in ['making_steps','required_inventory','research_status','evidence_status','maturity'] if k in n}
        # A new recipe does not erase saved report/activity provenance. Its own route is still unreviewed.
        saved_research={key:copy.deepcopy(n[key]) for key in ('research_status','evidence_status')
                        if key in n and (n.get('research_artifacts') or n.get('research_activity'))}
        n.update(inventory_complete=False,spec_reviewed=False,reviewed=False,maturity='proposed',research_status='discovered',
                 evidence_status='memory-first-discovery',required_inventory=requirements,
                 making_steps=[method,'Detailed procedure and acceptance remain unresearched.'])
        n.update(saved_research)
        if n.get('research_activity'):
            n['research_activity']['current_selected_route_reviewed']=False
        n.setdefault('unresolved_questions',[]).append('Current memory-first method needs source and compatibility review.')
        routes[rid]=route;changed_routes[rid]=route;changed_nodes[output]=n
        scenario['selected_routes'][output]=rid
    candidate['nodes']=list(nodes.values());candidate['routes']=list(routes.values())
    proposal={'base_revision':registry['revision'],'proposal_id':draft.get('proposal_id','memory-first-discovery'),
              'author':draft.get('author','discovery agent'),'reason':'Staged memory-first inventory, no physical acceptance/closure.',
              'upsert_nodes':list(changed_nodes.values()),'upsert_routes':list(changed_routes.values()),
              'scenarios':candidate['scenarios']}
    try:return {'ok':True,'proposal':proposal,'candidate':candidate,'validation':validate_registry(candidate)}
    except GateError as exc:return {'ok':False,'proposal':proposal,'candidate':candidate,'error':exc.as_dict()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draft',type=Path)
    parser.add_argument('--registry',type=Path,default=ROOT/'data/registry.json')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if not args.out.resolve().is_relative_to((ROOT/'proposals').resolve()):parser.error('Write probe output inside proposals/.')
    if args.out.exists() and any(args.out.iterdir()):parser.error('Use a fresh attempt directory so prior results cannot be mistaken for this probe.')
    try:result=probe(load_json(args.registry),load_json(args.draft))
    except GateError as exc:result={'ok':False,'error':exc.as_dict()}
    args.out.mkdir(parents=True,exist_ok=True)
    for key in ['proposal','candidate','validation','error']:
        if key in result:(args.out/(key+'.json')).write_text(json.dumps(result[key],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'ok':result['ok'],'output':str(args.out),'error':result.get('error')}))
    raise SystemExit(0 if result['ok'] else 1)


if __name__=='__main__':main()
