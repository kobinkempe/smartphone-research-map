"""Audit generated static pages against the canonical validated graph."""
import hashlib
import json
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from graph_gate import load_json, validate_registry
from research_ui import graph_model
from research_publication import audit_published_artifacts

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=set()
        self.routes={}
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get('id'):self.ids.add(attrs['id'])
        if attrs.get('id') and attrs.get('data-route-id'):self.routes[attrs['id']]=attrs['data-route-id']
        if tag=='a' and 'href' in attrs:self.links.append(attrs)

def resolved(path,cache):
    path=Path(path)
    if path not in cache:cache[path]=path.resolve()
    return cache[path]


def check_dependency_destination(attrs,key,parser,registry,standalone=False,membership=None,resolution_cache=None):
    source,target=attrs.get('data-dependency-source'),attrs.get('data-dependency-target')
    node_ids,route_ids=membership if membership is not None else ({n['id'] for n in registry['nodes']},{r['id'] for r in registry['routes']})
    url=urlsplit(attrs['href'])
    cache=resolution_cache if resolution_cache is not None else {}
    if target in node_ids:
        expected='nodes/'+target
        if attrs.get('data-page')!=expected:raise ValueError('Dependency data-page opens a different target')
        if standalone:
            matches=url.path==expected+'.html'
        else:
            matches=resolved((OUT/(key+'.html')).parent/unquote(url.path),cache)==resolved(OUT/(expected+'.html'),cache)
        if not matches or url.fragment or url.scheme or url.netloc:
            raise ValueError('Dependency href opens a different target')
    elif target in route_ids:
        if key!='nodes/'+source or attrs['href']!='#making' or parser.routes.get('making')!=target:
            raise ValueError('Selected-route link does not open its own making section')
    else:raise ValueError('Unknown dependency target')

def audit():
    registry=load_json(ROOT/'data/registry.json')
    validation=validate_registry(registry)
    physical_graph=graph_model(registry)
    graph_text=(OUT/'assets/physical-graph.js').read_text(encoding='utf-8')
    published_graph=json.JSONDecoder().raw_decode(graph_text.split('window.RESEARCH_GRAPH=',1)[1])[0]
    if published_graph!=physical_graph:raise ValueError('Interactive physical map differs from validated registry')
    membership=({n['id'] for n in registry['nodes']},{r['id'] for r in registry['routes']})
    allowed={tuple(edge) for edge in validation['scenarios'][0]['structural_links']}
    seen=set()
    parsed={}
    resolution_cache={}
    output_root=resolved(OUT,resolution_cache)
    for file in OUT.rglob('*.html'):
        if file.name=='smartphone-research.html':continue
        parser=Links();parser.feed(file.read_text(encoding='utf-8'));parsed[resolved(file,resolution_cache)]=parser
    local_links=0
    for file,parser in parsed.items():
        for attrs in parser.links:
            page=attrs.get('data-page','')
            if page.startswith('nodes/') and page[6:] in physical_graph['nodes']:
                if attrs.get('data-item-status')!=physical_graph['nodes'][page[6:]]['status']:
                    raise ValueError('Physical item link has missing or incorrect research status: '+page)
            if attrs.get('data-relation')=='dependency':
                edge=(attrs.get('data-dependency-source'),attrs.get('data-dependency-target'))
                if edge not in allowed:raise ValueError(f'Unvalidated dependency in {file.name}: {edge}')
                check_dependency_destination(attrs,str(file.relative_to(output_root).with_suffix('')).replace('\\','/'),parser,registry,membership=membership,resolution_cache=resolution_cache)
                seen.add(edge)
            url=urlsplit(attrs['href'])
            if url.scheme or url.netloc:continue
            target=resolved(file.parent/unquote(url.path),resolution_cache) if url.path else file
            if not target.is_relative_to(output_root):raise ValueError(f'Link escapes publication: {attrs["href"]}')
            if not target.exists():raise ValueError(f'Missing local target: {file.name} -> {attrs["href"]}')
            if url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                raise ValueError(f'Missing fragment: {file.name} -> {attrs["href"]}')
            local_links+=1
    if seen!=allowed:raise ValueError('Publication dependency set differs from validated registry')
    standalone=(OUT/'smartphone-research.html').read_text(encoding='utf-8')
    payload=standalone.split('const pages=',1)[1]
    standalone_graph=json.JSONDecoder().raw_decode(standalone.split('window.RESEARCH_GRAPH=',1)[1])[0]
    if standalone_graph!=physical_graph:raise ValueError('Standalone physical map differs from validated registry')
    views=json.JSONDecoder().raw_decode(payload)[0]
    standalone_edges=set()
    for key,body in views.items():
        parser=Links();parser.feed(body)
        for attrs in parser.links:
            page=attrs.get('data-page','')
            if page.startswith('nodes/') and page[6:] in physical_graph['nodes']:
                if attrs.get('data-item-status')!=physical_graph['nodes'][page[6:]]['status']:
                    raise ValueError('Standalone physical item link has incorrect status: '+page)
            if attrs.get('data-page') and attrs['data-page'] not in views:
                raise ValueError(f'Missing standalone view: {key} -> {attrs["data-page"]}')
            if attrs.get('data-relation')=='dependency':
                edge=(attrs.get('data-dependency-source'),attrs.get('data-dependency-target'))
                if edge not in allowed:raise ValueError(f'Unvalidated standalone dependency: {edge}')
                check_dependency_destination(attrs,key,parser,registry,standalone=True,membership=membership)
                standalone_edges.add(edge)
    if standalone_edges!=allowed:raise ValueError('Standalone dependency set differs from validated registry')
    research_links=audit_published_artifacts(registry,ROOT,OUT,views)
    # Byte equality carries the full graph/link audit into the hosted edition.
    hosted=ROOT/'out'
    manifest=json.loads((ROOT/'.openai/hosting.json').read_text(encoding='utf-8'))
    if manifest['static']['directory']!='out':raise ValueError('Hosting must use the size-checked output')
    expected={p.relative_to(OUT) for p in OUT.rglob('*') if p.is_file() and p.name!='smartphone-research.html'}
    actual={p.relative_to(hosted) for p in hosted.rglob('*') if p.is_file()}
    if actual!=expected|{Path('smartphone-research.zip')}:raise ValueError('Hosted output file set differs from the audited edition')
    for relative in expected:
        original=(OUT/relative).read_bytes()
        if relative==Path('downloads.html'):
            original=original.decode('utf-8').replace('href="smartphone-research.html"','href="smartphone-research.zip"').replace('Standalone linked research edition</a>','Standalone linked research edition (ZIP)</a>').encode('utf-8')
        if (hosted/relative).read_bytes()!=original:raise ValueError('Hosted output differs from audited content: '+str(relative))
    with zipfile.ZipFile(hosted/'smartphone-research.zip') as archive:
        if archive.namelist()!=['smartphone-research.html'] or archive.read('smartphone-research.html')!=(OUT/'smartphone-research.html').read_bytes():
            raise ValueError('Hosted standalone download differs from the audited edition')
    if any((hosted/p).stat().st_size>26_214_400 for p in actual):raise ValueError('Hosted file exceeds the per-file limit')
    return {'ok':True,'html_pages_audited':len(parsed),'local_links_checked':local_links,
            'standalone_views_checked':len(views),
            'hosted_files_checked':len(actual),'hosted_standalone_zip_checked':True,
            'dependency_edges_checked':len(seen),'interactive_physical_nodes_checked':len(physical_graph['nodes']),
            'registry_sha256':hashlib.sha256((ROOT/'data/registry.json').read_bytes()).hexdigest(),
            'hash_bound_research_links_checked_static_and_standalone':research_links}

if __name__=='__main__':print(json.dumps(audit()))
