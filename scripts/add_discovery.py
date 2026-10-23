"""Shared add API: normalize, reject whole-map cycles, commit atomically, refresh."""
import argparse
import copy
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from check_discovery import probe
from graph_gate import GateError, apply_proposal, exclusive_lock, load_json

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'data/registry.json'


def refresh_map(registry_path):
    if registry_path.resolve()!=REGISTRY.resolve():
        raise ValueError('Automatic page refresh is for the shared project registry only.')
    # Lock through the build so copied JSON, derived links and tool banks agree.
    with exclusive_lock(registry_path,timeout=60):
        current=load_json(registry_path)
        checkpoint=ROOT/'data/checkpoint.json'
        if checkpoint.exists() and load_json(checkpoint).get('graph_revision')==current['revision']:
            return current['revision']
        result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/build_pages.py')],
                              cwd=ROOT,capture_output=True,text=True,check=True)
        return json.loads(result.stdout.strip().splitlines()[-1])['graph_revision']


def add_to_map(draft,registry_path=REGISTRY,refresh=True,max_retries=8):
    """Any agent may call this. Rejected additions never modify registry bytes."""
    registry_path=Path(registry_path).resolve()
    if not isinstance(draft,dict):return {'ok':False,'status':'rejected','code':'schema','message':'Supply a compact draft object.'}
    explicit_revision='base_revision' in draft
    request=copy.deepcopy(draft)
    if not request.get('new_items') and not request.get('expansions'):
        return {'ok':False,'status':'rejected','code':'empty','message':'Supply new items or expansions.'}
    reserved={'con','prn','aux','nul'}|{'com'+str(i) for i in range(1,10)}|{'lpt'+str(i) for i in range(1,10)}
    for item in request.get('new_items',[]):
        nid=item.get('id','')
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*',nid) or nid in reserved:
            return {'ok':False,'status':'rejected','code':'invalid_id','message':'Use a safe lowercase canonical ID.', 'id':nid}
    for attempt in range(max_retries):
        try:
            with exclusive_lock(registry_path):
                current=load_json(registry_path)
            selections=current['scenarios'][0]['selected_routes']
            batch=copy.deepcopy(request)
            if not explicit_revision:batch['base_revision']=current['revision']
            # Prevent two agents from silently replacing a previously expanded item.
            for item in batch.get('expansions',[]):
                output=item['output']
                if output not in selections:
                    named=[n['id'] for n in current['nodes'] if output.casefold() in
                           [str(value).casefold() for value in [n['name']]+n.get('aliases',[])]]
                    if len(named)==1:output=named[0]
                selected=selections.get(output)
                if selected:
                    if not explicit_revision or item.get('expected_route')!=selected:
                        raise GateError('already_discovered','Output already has a selected route. Intentional replacement needs base_revision and expected_route.',id=output,selected_route=selected)
            result=probe(current,batch)
            if not result['ok']:return {'ok':False,'status':'rejected',**result['error']}
            committed=apply_proposal(registry_path,result['proposal'])
            response={'ok':True,'status':'accepted','revision':committed['revision'],
                      'upsert_nodes':len(result['proposal']['upsert_nodes']),
                      'upsert_routes':len(result['proposal']['upsert_routes'])}
            if refresh:
                try:response.update(view_status='updated',rendered_revision=refresh_map(registry_path))
                except (OSError,ValueError,GateError,subprocess.SubprocessError) as exc:
                    response.update(view_status='failed',view_error=str(exc),
                                    recovery='Addition is already saved. Refresh the view; do not resubmit the addition.')
            else:response['view_status']='deferred'
            return response
        except GateError as exc:
            if exc.code=='stale_revision' and not explicit_revision and attempt+1<max_retries:continue
            return {'ok':False,'status':'rejected',**exc.as_dict()}
    return {'ok':False,'status':'rejected','code':'busy','message':'Map changed repeatedly; retry the addition.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draft',type=Path)
    parser.add_argument('--defer-view',action='store_true',help='Commit a bulk batch; refresh once after batching.')
    args=parser.parse_args()
    request=load_json(args.draft)
    try:result=add_to_map(request,refresh=not args.defer_view)
    except (OSError,TypeError,ValueError,KeyError) as exc:
        result={'ok':False,'status':'rejected','code':'input_or_io','message':str(exc)}
    # Compact per-request audit, avoiding a full registry copy for every node.
    audit=ROOT/'data/add-attempts';audit.mkdir(parents=True,exist_ok=True)
    attempt_path=audit/(uuid.uuid4().hex+'.json')
    attempt_path.write_text(json.dumps({'draft':request,'result':result},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    result['attempt_record']=str(attempt_path)
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['ok'] and result.get('view_status')!='failed' else 1)


if __name__=='__main__':main()
