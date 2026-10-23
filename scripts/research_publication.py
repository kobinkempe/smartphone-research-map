"""Validate explicit research lifecycle/artifacts and gate metadata-only publication."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import uuid
import os
import tempfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from graph_gate import apply_proposal, exclusive_lock, load_json, unresolved, has_unknown, GateError

ROOT=Path(__file__).resolve().parents[1]
STATES={'assigned','started','paused','completed','reviewed','complete','blocked'}
PHASES={'assigned':'assigned','started':'researching','paused':'paused','completed':'draft-awaiting-review','reviewed':'draft-reviewed','complete':'complete','blocked':'blocked'}
KINDS={'report','original-report','amended-report','review','review-decisions','review-audit','manifest','progress','source-evidence'}
FIELDS={'research_status','evidence_status','research_activity','research_artifacts','research_bookkeeping_history','unresolved_questions'}
BOOKKEEPING={
 'Making route and target-level requirements not researched.':'Bounded making-page evidence is saved; the complete immediate method, target specification, inventory and actual caller qualification still require comprehensive research and independent review.',
 'Identified requirement; no researched making route or qualified output yet.':'Bounded making-page evidence is saved; a complete reviewed making method and qualified output are not established.',
 'Discovery hypothesis only: quantitative demands, full recipe, quantities, losses, compatibility and acceptance remain to be researched.':'Reviewed bounded evidence is saved; quantitative demands, complete recipe, quantities, losses, compatibility and acceptance still need comprehensive research and review.',
 'No cutting method, glass/salt recipe, test threshold or numeric target selected. Specialist stress/strength identities must exist canonically before parent publication.':'No cutting method, glass/salt recipe, test threshold or numeric target selected. Specialist stress/strength identities are now canonical discovery hypotheses; their actual-glass measurement/reference suitability remains unqualified.',
 'Electronics-owned formation-cycler exposes independent source/load/meters/cutoffs/controller/loading hardware; its first-making route remains unselected. No sealed cell is accepted before leakage, formation and safety/target tests.':'Electronics-owned formation-cycler has a selected discovery inventory for source/load/meters/cutoffs/controller/loading hardware; its physical suitability and first-making capability remain unqualified. No sealed cell is accepted before leakage, formation and safety/target tests.'}

def safe_path(root,value):
    if not isinstance(value,str) or '\\' in value or ':' in value:
        raise ValueError('Artifact must use a project-relative POSIX path')
    p=PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0]!='proposals' or p.suffix not in {'.md','.json'}:
        raise ValueError('Artifact must be a Markdown/JSON file under proposals/')
    path=(root/p).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_relative_to((root/'proposals').resolve()) or not path.is_file():
        raise ValueError('Missing or escaping research artifact: '+value)
    return path

def artifact(root,record):
    a=copy.deepcopy(record)
    if a.get('kind') not in KINDS or not isinstance(a.get('label'),str) or not a['label']:
        raise ValueError('Artifact kind and readable label are required')
    path=safe_path(root,a.get('path'))
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if not re.fullmatch('[0-9a-f]{64}',str(a.get('sha256'))) or a['sha256']!=actual:
        raise ValueError('Artifact hash mismatch: '+a['path'])
    source=a.get('source_path') if a.get('immutable_snapshot') else a['path']
    if a.get('immutable_snapshot'):
        if a.get('immutable_snapshot') is not True or not isinstance(source,str):raise ValueError('Immutable snapshot source path must be a string')
        sp=PurePosixPath(source)
        prefix='proposals/research-artifact-archive/'+hashlib.sha256(source.encode()).hexdigest()[:12]+'/'
        if (not isinstance(source,str) or ':' in source or '\\' in source or sp.is_absolute() or '..' in sp.parts or not sp.parts or sp.parts[0]!='proposals' or sp.suffix not in {'.md','.json'} or a.get('source_sha256')!=actual or a['path']!=prefix+actual+sp.suffix):
            raise ValueError('Immutable snapshot provenance is malformed')
    a['page']='research-artifacts/'+actual+'-'+hashlib.sha256(source.encode()).hexdigest()[:12]
    return a

def snapshot_artifact(root,record):
    """Verify current source once, freeze those exact bytes, retain source provenance."""
    a=artifact(root,record)
    if a.get('immutable_snapshot'):return a
    source=a['path'];blob=safe_path(root,source).read_bytes()
    if hashlib.sha256(blob).hexdigest()!=a['sha256']:
        raise ValueError('Source changed while capturing immutable snapshot')
    rel='proposals/research-artifact-archive/'+hashlib.sha256(source.encode()).hexdigest()[:12]+'/'+a['sha256']+PurePosixPath(source).suffix
    target=root/rel;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.resolve().is_relative_to(root.resolve()):raise ValueError('Snapshot storage escapes project')
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest()!=a['sha256']:raise ValueError('Existing immutable snapshot is corrupted')
    else:
        temp=None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent,prefix='archive-',suffix='.tmp',delete=False) as handle:
                temp=Path(handle.name);handle.write(blob);handle.flush();os.fsync(handle.fileno())
            os.replace(temp,target);temp=None
        finally:
            if temp is not None:temp.unlink(missing_ok=True)
    a.update(path=rel,source_path=source,source_sha256=a['sha256'],immutable_snapshot=True)
    return artifact(root,a)

def checked_artifacts(root,node):
    return [artifact(root,a) for a in node.get('research_artifacts',[])]

def audit_published_artifacts(registry,root,output,views):
    class ResearchLinks(HTMLParser):
        def __init__(self):super().__init__();self.references=[];self.pages=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag=='a' and 'data-research-path' in a:self.references.append((a['data-research-path'],a.get('data-research-sha256'),a.get('data-page')))
            if 'data-research-artifact-page-path' in a:self.pages.append((a['data-research-artifact-page-path'],a.get('data-research-artifact-page-sha256')))
    count=0
    for node in registry['nodes']:
        artifacts=checked_artifacts(root,node)
        if not artifacts:continue
        expected={(a['path'],a['sha256'],a['page']) for a in artifacts}
        for body in [(output/'nodes'/f"{node['id']}.html").read_text(encoding='utf-8'),views['nodes/'+node['id']]]:
            parser=ResearchLinks();parser.feed(body)
            if set(parser.references)!=expected:raise ValueError('Published node research links differ from hash-bound metadata: '+node['id'])
        for a in artifacts:
            for body in [(output/(a['page']+'.html')).read_text(encoding='utf-8'),views[a['page']]]:
                parser=ResearchLinks();parser.feed(body)
                if parser.pages!=[(a['path'],a['sha256'])]:raise ValueError('Artifact page provenance differs: '+a['path'])
            count+=1
    return count

def review_proof(root,item,artifacts):
    proof=item.get('review_proof',{})
    audit=snapshot_artifact(root,proof.get('audit',{}))
    decisions=snapshot_artifact(root,proof.get('decisions',{}))
    data=load_json(safe_path(root,audit['path']))
    decision=load_json(safe_path(root,decisions['path']))
    matches=[r for r in data.get('reports',[]) if r.get('id')==item['id']]
    reports=[a for a in artifacts if a['kind'] in {'report','amended-report'}]
    if len(matches)!=1 or not reports or any(a['sha256'] not in {matches[0].get('amended_sha256'),matches[0].get('report_sha256')} for a in reports):
        raise ValueError('Independent review audit does not bind this report hash')
    if any(a['sha256']!=matches[0].get('original_sha256') for a in artifacts if a['kind']=='original-report'):
        raise ValueError('Independent audit does not bind the original report hash')
    verdicts=[o for o in decision.get('operations',[]) if item['id'] in o.get('record_ids',[])]
    if not verdicts or any(o.get('amended_decision') not in {'reviewed-as-draft','research-complete'} for o in verdicts):
        raise ValueError('Independent reviewed-report decision is missing')
    if item['state']=='complete' and (proof.get('certification')!='immediate-record-complete' or any(o.get('amended_decision')!='research-complete' for o in verdicts)):
        raise ValueError('Research completion needs explicit independent immediate-record certification')
    return dict(audit=audit,decisions=decisions,scope=decision.get('scope','Independent bounded evidence review'),revision=data.get('revision'),primary_sources_checked=decision.get('independently_opened_primary_sources'))

def proposal_for(registry,manifest,root=ROOT):
    if manifest.get('schema_version')!=1 or not isinstance(manifest.get('items'),list) or not manifest['items']:
        raise ValueError('Publication needs schema_version:1 and explicit lifecycle items')
    by_id={n['id']:n for n in registry['nodes']};routes={r['id']:r for r in registry['routes']}
    selection=registry['scenarios'][0]['selected_routes'];changes=[];seen=set()
    for item in manifest['items']:
        nid=item.get('id');state=item.get('state')
        if nid not in by_id or nid in seen or state not in STATES or not item.get('scope'):
            raise ValueError('Unknown/duplicate ID or missing lifecycle/scope')
        seen.add(nid);original=by_id[nid];n=copy.deepcopy(original)
        if 'expected_activity' in item and item['expected_activity']!=original.get('research_activity'):
            raise ValueError('Research activity changed; reread the assignment before updating it')
        arts=[snapshot_artifact(root,a) for a in item.get('artifacts',[])]
        reports=[a for a in arts if a['kind'] in {'report','amended-report'}]
        if state in {'completed','reviewed','complete'} and not reports:
            raise ValueError('Explicit completion requires a saved hash-bound report')
        review=review_proof(root,item,arts) if state in {'reviewed','complete'} or item.get('review_proof') else None
        if state=='complete':
            route=routes.get(selection.get(nid))
            if not (n.get('inventory_complete') and n.get('spec_reviewed') and not unresolved(n) and route and route.get('reviewed') and route.get('inventory_complete') and not unresolved(route)):
                raise ValueError('Own-node inventory/spec/selected route remain incomplete; descendants need not be closed')
            if any(req.get('compatibility')!='reviewed' or has_unknown(req.get('required_capability')) for req in route.get('requires',[])):
                raise ValueError('Immediate requirement demands or interface compatibility remain unreviewed; this is separate from making the descendants')
        old=[snapshot_artifact(root,a) for a in checked_artifacts(root,n)]
        merged={(a['path'],a['sha256']):a for a in old}
        merged.update({(a['path'],a['sha256']):a for a in arts})
        if review:
            merged.update({(a['path'],a['sha256']):a for a in [review['audit'],review['decisions']]})
        n['research_artifacts']=list(merged.values())
        phase=PHASES[state]
        n['research_activity']=dict(state=state,phase=phase,section=item.get('section',manifest.get('section','bounded-research')),scope=item['scope'],reason=item.get('reason',''),batch_state=item.get('batch_state',state),review=review,report_scope_revision=item.get('report_scope_revision'),current_selected_route_reviewed=False if state!='complete' else True)
        if review:
            n.update(research_status='reviewed',evidence_status='independently-reviewed-immediate-record' if state=='complete' else 'independently-reviewed-evidence-draft')
        elif reports:
            n.update(research_status='research-draft',evidence_status='saved-research-draft-not-independently-reviewed')
        for update in item.get('bookkeeping_updates',[]):
            before,after=update['before'],update['after']
            if BOOKKEEPING.get(before)!=after:
                raise ValueError('Only exact obsolete bookkeeping assertions can be replaced; real engineering questions are protected')
            if 'identities are now canonical' in after and not {'glass-stress-profile-instrument','glass-edge-impact-and-bend-fixture'} <= set(by_id):
                raise ValueError('Specialized glass identities are not canonical')
            if 'formation-cycler has a selected' in after and 'formation-cycler' not in selection:
                raise ValueError('Formation cycler is not selected')
            if before not in n.get('unresolved_questions',[]):
                raise ValueError('Bookkeeping assertion no longer matches live record')
            if not after or not update.get('reason'):
                raise ValueError('Bookkeeping update needs retained scoped gaps and reason')
            n['unresolved_questions']=[after if q==before else q for q in n['unresolved_questions']]
            n.setdefault('research_bookkeeping_history',[]).append(copy.deepcopy(update))
        if any(n.get(k)!=original.get(k) for k in set(n)|set(original) if k not in FIELDS):
            raise ValueError('Publication changed non-research node fields')
        changes.append(n)
    return dict(base_revision=registry['revision'],upsert_nodes=changes,proposal_id=manifest.get('publication_id','research-lifecycle-publication'),author=manifest.get('author','research worker'),reason='Hash-validated research lifecycle/report metadata only; selected graph and qualification flags preserved.')

def publish(manifest,root=ROOT,registry_path=None,rebuild=True):
    root=Path(root);path=Path(registry_path or root/'data/registry.json')
    for retry in range(8):
        with exclusive_lock(path,timeout=60):current=load_json(path)
        proposal=proposal_for(current,manifest,root)
        try:
            report=apply_proposal(path,proposal,lock_timeout=60)
            break
        except GateError as exc:
            if exc.code!='stale_revision' or retry==7:raise
    result=dict(ok=True,revision=report['revision'],nodes=len(proposal['upsert_nodes']),view_status='deferred')
    audit=root/'data/research-publication-attempts';audit.mkdir(parents=True,exist_ok=True)
    record=audit/(uuid.uuid4().hex+'.json')
    record.write_text(json.dumps(dict(manifest=manifest,proposal=proposal,result=result),indent=2)+'\n',encoding='utf-8')
    result['attempt_record']=str(record)
    if rebuild:
        try:
            with exclusive_lock(path,timeout=60):
                proc=subprocess.run([sys.executable,'-B',str(root/'scripts/build_pages.py')],cwd=root,capture_output=True,text=True,check=True)
                result.update(view_status='updated',rendered_revision=json.loads(proc.stdout.strip().splitlines()[-1])['graph_revision'])
        except (OSError,subprocess.SubprocessError,ValueError) as exc:
            result.update(view_status='failed',view_error=str(exc),recovery='Metadata already accepted. Rebuild under registry lock without republishing.')
    record.write_text(json.dumps(dict(manifest=manifest,proposal=proposal,result=result),indent=2)+'\n',encoding='utf-8')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    pub=sub.add_parser('publish');pub.add_argument('manifest',type=Path)
    act=sub.add_parser('activity');act.add_argument('--state',choices=['assigned','started','paused','blocked'],required=True);act.add_argument('--items',nargs='+',required=True);act.add_argument('--section',required=True);act.add_argument('--reason',required=True)
    a=p.parse_args()
    if a.command=='publish':m=load_json(a.manifest)
    else:
        registry=load_json(ROOT/'data/registry.json');nodes={n['id']:n for n in registry['nodes']}
        m=dict(schema_version=1,section=a.section,items=[])
        for nid in a.items:
            n=nodes.get(nid,{})
            state=a.state
            # Pause the batch without pretending already saved per-item drafts became unwritten.
            old=n.get('research_activity',{}).get('state')
            if state=='paused' and old in {'completed','reviewed'}:state=old
            row=dict(id=nid,state=state,scope='Bounded own-node research; physical completeness and acceptance not inferred.',reason=a.reason,batch_state=a.state,artifacts=n.get('research_artifacts',[]))
            row['expected_activity']=n.get('research_activity')
            if n.get('research_activity',{}).get('review'):row['review_proof']=n['research_activity']['review']
            m['items'].append(row)
    try:result=publish(m)
    except (ValueError,GateError,OSError) as exc:
        print(json.dumps(dict(ok=False,message=str(exc))));return 1
    print(json.dumps(result));return 0 if result['view_status']!='failed' else 1

if __name__=='__main__':raise SystemExit(main())
