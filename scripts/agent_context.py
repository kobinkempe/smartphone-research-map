"""Compact canonical search and revision-stamped scoped context for large maps."""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compact_index(registry):
    selected = registry['scenarios'][0]['selected_routes']
    for node in registry['nodes']:
        yield {'id': node['id'], 'name': node['name'], 'role': node['role'],
               'domain': node.get('domain'), 'aliases': node.get('aliases', []),
               'function': node.get('summary', '')[:360],
               'research_status': node.get('research_status'),
               'selected_route': selected.get(node['id']),
               'scope': node.get('scope', 'physical')}


def scoped_context(registry, root, depth, max_nodes=250):
    nodes = {n['id']: n for n in registry['nodes']}
    routes = {r['id']: r for r in registry['routes']}
    selected = registry['scenarios'][0]['selected_routes']
    if root not in nodes: raise ValueError('Unknown root: ' + root)
    if max_nodes < 1: raise ValueError('Node cap must be positive')
    distances, queue, included_routes = {root: 0}, deque([root]), set()
    omitted=set()
    while queue:
        parent = queue.popleft()
        if distances[parent] >= depth: continue
        rid = selected.get(parent)
        if not rid: continue
        included_routes.add(rid)
        for req in routes[rid]['requires']:
            child = req['target']
            if child not in distances:
                if len(distances)>=max_nodes:
                    omitted.add(child)
                    continue
                distances[child] = distances[parent]+1
                queue.append(child)
    candidates = [r for r in registry['routes'] if r['output'] in distances and r['id'] not in included_routes
                  and selected.get(r['output']) != r['id']]
    outside = sorted({q['target'] for r in candidates for q in r['requires']} - distances.keys())
    selected_outside=sorted({q['target'] for rid in included_routes for q in routes[rid]['requires']} - distances.keys())
    return {'base_revision': registry['revision'], 'root': root, 'physical_output_depth': depth,
            'scope_warning': 'Consult global canonical index and full records before adding IDs. Candidates are unselected; references outside this slice do not mean missing canonical records.',
            'nodes': [nodes[nid] for nid in sorted(distances)],
            'selected_routes': [routes[rid] for rid in sorted(included_routes)],
            'unselected_candidate_routes': candidates,
            'outside_candidate_reference_ids': outside,
            'outside_selected_reference_ids': selected_outside,
            'max_nodes': max_nodes, 'omitted_by_node_cap':sorted(omitted),
            'frontier_ids': sorted(nid for nid in distances if nid not in selected),
            'distance': distances}


def write_index(registry, source_path, target):
    metadata = {'kind': 'metadata', 'base_revision': registry['revision'],
                'source_path':str(source_path.resolve()),
                'registry_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
                'records': len(registry['nodes']), 'scope': 'Identities in this registry snapshot; staged source files contain proposals. No physically built stock is implied.'}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf-8') as out:
        out.write(json.dumps(metadata, ensure_ascii=False)+'\n')
        for item in compact_index(registry): out.write(json.dumps(item, ensure_ascii=False)+'\n')
    return metadata


def write_tool_bank(registry,folder):
    tools=sorted((n for n in registry['nodes'] if n['role']=='tool' and n.get('scope')!='black-box-software'),key=lambda n:(n['name'].casefold(),n['id']))
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'tool-names.txt').write_text(''.join(n['name']+'\n' for n in tools),encoding='utf-8')
    rows=compact_index({'nodes':tools,'scenarios':registry['scenarios']})
    with (folder/'tool-index.jsonl').open('w',encoding='utf-8') as out:
        for row in rows:out.write(json.dumps(row,ensure_ascii=False)+'\n')
    return len(tools)


def relationship_inventory(registry, root, ids_only=False):
    """Partition the complete canonical inventory by reverse selected reachability."""
    records = {item['id']: item for item in compact_index(registry)}
    if root not in records:
        raise ValueError('Unknown root: ' + root)
    routes = {r['id']: r for r in registry['routes']}
    selected = registry['scenarios'][0]['selected_routes']
    reverse = {}
    for parent, rid in selected.items():
        for req in routes[rid]['requires']:
            reverse.setdefault(req['target'], set()).add(parent)
    parents = reverse.get(root, set()) - {root}
    ancestors, queue = set(), deque(sorted(parents))
    while queue:
        item = queue.popleft()
        if item == root or item in ancestors:
            continue
        ancestors.add(item)
        queue.extend(sorted(reverse.get(item, set()) - ancestors))
    groups = {'direct_parents': parents, 'other_ancestors': ancestors - parents,
              'non_ancestors': records.keys() - ancestors - {root}}
    result = {'base_revision': registry['revision'], 'root': root,
            'scope': 'Complete canonical inventory; relationships use selected routes only. Refresh for every item and after commits. Pending drafts are not included.',
            'loop_rule': 'Requiring self or any ancestor creates a selected dependency loop. Non-ancestors are reuse candidates, not proof of suitability or safety of combined pending additions; the full add gate remains mandatory.',
            'self': records[root], 'forbidden_requirement_ids': sorted(ancestors | {root}),
            'counts': {key: len(ids) for key, ids in groups.items()},
            **{key: sorted(ids) if ids_only else [records[nid] for nid in sorted(ids)]
               for key, ids in groups.items()}}
    if ids_only:
        result['record_format'] = 'Canonical IDs only; use search/full registry records for names, functions and suitability. The partitions still cover every canonical identity.'
    return result


def bfs_plan(registry, root, depth=3, bootstrap_ids=()):
    """Read-only live BFS work list; no node cap or physical discovery decisions."""
    if depth < 1:
        raise ValueError('Expansion depth must be positive')
    nodes = {n['id']: n for n in registry['nodes']}
    if root not in nodes:
        raise ValueError('Unknown root: ' + root)
    records = {n['id']: n for n in compact_index(registry)}
    routes = {r['id']: r for r in registry['routes']}
    selected = registry['scenarios'][0]['selected_routes']
    distance, queue = {root: 0}, deque([root])
    while queue:
        parent = queue.popleft()
        if distance[parent] >= depth:
            continue
        for req in routes.get(selected.get(parent), {}).get('requires', []):
            child = req['target']
            if child not in distance:
                distance[child] = distance[parent] + 1
                queue.append(child)
    blocked = set(bootstrap_ids)
    levels = []
    for level in range(depth):
        work, reused, skipped = [], [], []
        for nid in sorted(n for n, d in distance.items() if d == level):
            n = nodes[nid]
            # Existing recipes must still be traversed to find undiscovered descendants.
            if nid in selected:
                reused.append(nid)
                continue
            reason = None
            if n.get('scope') == 'black-box-software' or n.get('boundary') == 'external' or n.get('role') == 'external':
                reason = 'external/software boundary'
            elif n.get('terminal') or n.get('discovery_leaf_kind') == 'candidate-natural-occurrence':
                reason = 'terminal/natural-occurrence candidate'
            elif nid in blocked:
                reason = 'bootstrap queue'
            elif n.get('discovery_leaf_kind') == 'blocked-frontier':
                reason = 'saved blocked frontier'
            if reason:
                skipped.append({'id': nid, 'reason': reason})
            else:
                work.append(records[nid])
        levels.append({'relative_depth': level, 'needs_inventory': work,
                       'existing_inventory_ids': reused, 'skipped': skipped})
    return {'base_revision': registry['revision'], 'root': root, 'expansion_depth': depth,
            'levels': levels, 'boundary_ids': sorted(n for n, d in distance.items() if d == depth),
            'distance_counts': {str(d): sum(x == d for x in distance.values()) for d in range(depth + 1)},
            'refresh_rule': 'Rerun after each depth batch. New root/child requirements reveal later work. This is the complete known selected slice, not proof of undiscovered requirements or physical feasibility. Live ownership must be checked separately.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=ROOT/'data/registry.json')
    sub = parser.add_subparsers(dest='action', required=True)
    index = sub.add_parser('index')
    index.add_argument('--output', type=Path, default=ROOT/'data/agent-index.jsonl')
    search = sub.add_parser('search')
    search.add_argument('terms', nargs='+')
    search.add_argument('--limit', type=int, default=30)
    scope = sub.add_parser('slice')
    scope.add_argument('root')
    scope.add_argument('--depth', type=int, default=2)
    scope.add_argument('--max-nodes', type=int, default=250)
    scope.add_argument('--output', type=Path, required=True)
    inventory = sub.add_parser('inventory', help='Complete identities separated into parents, ancestors and non-ancestors')
    inventory.add_argument('root')
    inventory.add_argument('--output', type=Path, required=True)
    inventory.add_argument('--ids-only', action='store_true', help='Complete relationship partitions without repeating full canonical records')
    bfs = sub.add_parser('bfs', help='Automatic deduplicated work list by relative depth')
    bfs.add_argument('root')
    bfs.add_argument('--depth', type=int, default=3)
    bfs.add_argument('--bootstrap-queue', type=Path, default=ROOT/'data/bootstrap-queue.json')
    bfs.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    registry_bytes = args.registry.read_bytes()
    registry = json.loads(registry_bytes.decode('utf-8-sig'))
    if args.action == 'index':
        result = write_index(registry, args.registry, args.output)
        result['tool_names']=write_tool_bank(registry,args.output.parent)
    elif args.action == 'search':
        terms = [term.casefold() for term in args.terms]
        matches = [item for item in compact_index(registry)
                   if all(term in json.dumps(item, ensure_ascii=False).casefold() for term in terms)]
        result = {'base_revision': registry['revision'], 'matched': len(matches), 'records': matches[:args.limit]}
    elif args.action == 'inventory':
        result = relationship_inventory(registry, args.root, ids_only=args.ids_only)
        result['registry_sha256'] = hashlib.sha256(registry_bytes).hexdigest()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        result = {'base_revision': registry['revision'], 'root': args.root,
                  'output': str(args.output), 'counts': result['counts']}
    elif args.action == 'bfs':
        backlog = json.loads(args.bootstrap_queue.read_text(encoding='utf-8-sig'))
        result = bfs_plan(registry, args.root, args.depth, (x['item'] for x in backlog['items']))
        result['registry_sha256'] = hashlib.sha256(registry_bytes).hexdigest()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        result = {'base_revision': registry['revision'], 'root': args.root, 'output': str(args.output),
                  'levels': [{'depth': x['relative_depth'], 'open': len(x['needs_inventory']),
                              'existing': len(x['existing_inventory_ids']), 'skipped': len(x['skipped'])}
                             for x in result['levels']]}
    else:
        if args.depth < 0: parser.error('Depth must be nonnegative')
        result = scoped_context(registry, args.root, args.depth, args.max_nodes)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        result = {'base_revision': registry['revision'], 'output': str(args.output), 'nodes': len(result['nodes']),
                  'selected_routes': len(result['selected_routes'])}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
