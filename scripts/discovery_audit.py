"""Discovery coverage measures output hops, never recipe nodes or physical closure."""
from collections import Counter, deque


def coverage(registry, root='handset', limit=5):
    nodes = {n['id']: n for n in registry['nodes']}
    routes = {r['id']: r for r in registry['routes']}
    selected = registry['scenarios'][0]['selected_routes']
    children = {nid: [r['target'] for r in routes[rid]['requires']]
                for nid, rid in selected.items()}
    distance = {root: 0}
    queue = deque([root])
    while queue:
        parent = queue.popleft()
        for child in children.get(parent, []):
            if child not in distance:
                distance[child] = distance[parent] + 1
                queue.append(child)
    physical = {nid: depth for nid, depth in distance.items()
                if nodes[nid].get('scope') != 'black-box-software'
                and nodes[nid].get('boundary') != 'external'
                and nodes[nid]['role'] != 'external'}
    candidates = sorted(nid for nid in physical
                        if nodes[nid].get('discovery_leaf_kind') == 'candidate-natural-occurrence')
    frontiers = sorted(nid for nid in physical if not children.get(nid)
                       and nid not in candidates and nodes[nid]['terminal'] is False)
    levels = []
    for depth in range(limit + 1):
        items = sorted(nid for nid, d in physical.items() if d == depth)
        levels.append({'level': depth, 'items': items,
                       'expanded': sum(bool(children.get(nid)) for nid in items),
                       'unexpanded': [nid for nid in items if nid in frontiers],
                       'candidate_occurrences': [nid for nid in items if nid in candidates]})
    return {'root': root, 'level_definition': 'Shortest physical output-to-output dependency distance; root is level 0. Recipe records do not add levels.',
            'graph_revision': registry['revision'], 'levels': levels,
            'reachable_physical_outputs': len(physical),
            'unreachable_physical_outputs': sorted(nid for nid, n in nodes.items()
                if nid not in physical and n.get('scope') != 'black-box-software'
                and n.get('boundary') != 'external' and n['role'] != 'external'),
            'maximum_shortest_level': max(physical.values(), default=0),
            'unexpanded_frontiers': frontiers, 'candidate_natural_occurrences': candidates,
            'gaps_before_level_5': [nid for nid in frontiers if physical[nid] < limit],
            'distance': physical,
            'discovery_complete_through_level_5': not any(physical[nid] < limit for nid in frontiers)
                and bool(children.get(root)),
            'warning': 'An expanded hypothesis is not a complete inventory. Candidate natural occurrences are unapproved; no closure follows from discovery depth.'}


def checked_trails(registry, trails):
    nodes = {n['id']: n for n in registry['nodes']}
    routes = {r['id']: r for r in registry['routes']}
    selected = registry['scenarios'][0]['selected_routes']
    for trail in trails:
        path = trail['path']
        if len(path) < 2 or any(nid not in nodes for nid in path):
            raise ValueError('Discovery trail has a missing output')
        for parent, child in zip(path, path[1:]):
            if parent not in selected or child not in {r['target'] for r in routes[selected[parent]]['requires']}:
                raise ValueError('Discovery trail does not follow selected graph: ' + parent + ' -> ' + child)
        if nodes[path[-1]].get('discovery_leaf_kind') != 'candidate-natural-occurrence':
            raise ValueError('Highlighted raw-material trail must end at a candidate natural occurrence')
    return trails
