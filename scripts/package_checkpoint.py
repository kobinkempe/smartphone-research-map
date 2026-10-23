"""Generate, audit and freeze a portable checkpoint; never bypass graph validation."""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from check_publication import audit, Links, check_dependency_destination
from graph_gate import validate_registry

ROOT=Path(__file__).resolve().parents[1]
RECOVERY=ROOT.parent/'research-staging'
BUDGET=25_000_000_000

def local_bytes():
    return sum(p.stat().st_size for folder in (ROOT,RECOVERY) for p in folder.rglob('*') if p.is_file())

def main():
    subprocess.run([sys.executable,'-B',str(ROOT/'scripts/build_pages.py')],check=True)
    report=audit()
    files={}
    for file in ROOT.rglob('*'):
        rel=file.relative_to(ROOT)
        if not file.is_file() or any(p in {'.git','node_modules','.sites-runtime','__pycache__','exports'} for p in rel.parts):continue
        if file.suffix in {'.zip','.lock'}:continue
        files[str(rel).replace('\\','/')]=file.read_bytes()
    for file in (RECOVERY/'prior-reference').rglob('*'):
        if file.is_file():files['recovery/'+str(file.relative_to(RECOVERY/'prior-reference')).replace('\\','/')]=file.read_bytes()
    # Audit the actual captured bytes, not only the mutable files that preceded them.
    registry=files['data/registry.json']
    captured_registry=json.loads(registry)
    validation=validate_registry(captured_registry)
    membership=({n['id'] for n in captured_registry['nodes']},{r['id'] for r in captured_registry['routes']})
    allowed={tuple(e) for e in validation['scenarios'][0]['structural_links']}
    seen=set()
    resolution_cache={}
    for name,body in files.items():
        if not name.startswith('dist/') or not name.endswith('.html') or name.endswith('/smartphone-research.html'):continue
        parser=Links();parser.feed(body.decode('utf-8'))
        for attrs in parser.links:
            if attrs.get('data-relation')=='dependency':
                edge=(attrs.get('data-dependency-source'),attrs.get('data-dependency-target'))
                if edge not in allowed:raise ValueError(f'Export contains unvalidated dependency: {name}: {edge}')
                check_dependency_destination(attrs,name[5:-5],parser,captured_registry,membership=membership,resolution_cache=resolution_cache)
                seen.add(edge)
    if seen!=allowed:raise ValueError('Export graph differs from captured registry')
    report['registry_sha256']=hashlib.sha256(registry).hexdigest()
    report['files_sha256']={name:hashlib.sha256(body).hexdigest() for name,body in files.items()}
    files['publication-audit.json']=(json.dumps(report,indent=2)+'\n').encode()
    if local_bytes()+sum(len(body) for body in files.values())>BUDGET:
        raise RuntimeError('Not enough room within the authorized 25 GB allocation for the export')
    folder=ROOT/'exports';folder.mkdir(exist_ok=True)
    target=folder/'smartphone-research-checkpoint.zip'
    temporary=folder/'smartphone-research-checkpoint.tmp'
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,body in sorted(files.items()):archive.writestr(name,body)
    temporary.replace(target)
    checkpoint=json.loads((ROOT/'data/checkpoint.json').read_text(encoding='utf-8'))
    checkpoint.update(local_bytes=local_bytes(),export_bytes=target.stat().st_size)
    (ROOT/'data/checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'export':str(target),'export_bytes':target.stat().st_size,'local_bytes':local_bytes(),'budget_bytes':BUDGET,'dependency_edges_checked':len(seen)}))

if __name__=='__main__':main()
