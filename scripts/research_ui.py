"""Compact physical DAG presentation and routes covering its distinct ancestors."""
import html
from collections import deque
from graph_gate import unresolved


LABELS = {'discovered': 'Discovered · unresearched', 'inherited': 'Inherited notes · not reviewed',
          'research-draft': 'Research draft', 'source-checked': 'Source-checked · not reviewed',
          'reviewed': 'Reviewed · remaining gaps', 'experimentally-demonstrated': 'Demonstrated · remaining gaps',
          'undiscovered': 'Undiscovered', 'proposed': 'Undiscovered proposal'}


def physical(node):
    return node.get('scope') != 'black-box-software' and node.get('boundary') != 'external' and node['role'] != 'external'


def item_status(node, route=None):
    state = node.get('research_status', 'undiscovered')
    if node.get('discovery_leaf_kind') == 'candidate-natural-occurrence' and not node.get('terminal'):
        return 'candidate', 'Candidate raw material · not a reviewed natural endpoint'
    if (state in {'reviewed', 'experimentally-demonstrated'} and node.get('inventory_complete')
            and node.get('spec_reviewed') and not unresolved(node)
            and (node.get('terminal') or (route and route.get('reviewed') and route.get('inventory_complete') and not unresolved(route)))):
        return 'researched', 'Fully researched record · ' + state.replace('-', ' ')
    activity = node.get('research_activity', {})
    phase = activity.get('phase')
    if phase:
        labels = {'assigned':'Research assigned · no completed report',
                  'researching':'Research in progress · remaining gaps',
                  'paused':'Research assigned · paused · no completed report',
                  'draft-awaiting-review':'Research draft saved · awaiting independent review',
                  'draft-reviewed':'Independently reviewed evidence draft · remaining engineering gaps',
                  'blocked':'Research blocked · explicit unresolved issue',
                  'complete':'Research completion recorded · qualification flags determine green'}
        label = labels.get(phase, phase.replace('-', ' ').title())
        saved_reports=any(a.get('kind') in {'report','amended-report'} for a in node.get('research_artifacts',[]))
        if phase in {'assigned','paused'} and saved_reports:
            label = ('Research assigned' if phase=='assigned' else 'Current research paused')+' · earlier saved evidence available'
            if activity.get('review'):label+=' · earlier evidence draft reviewed'
        if phase=='complete' and activity.get('current_selected_route_reviewed') is False:
            label='Earlier own-node research completed · changed recipe requires review'
        if phase == 'researching' and activity.get('review'):
            label += ' · earlier evidence draft reviewed'
        if activity.get('batch_state') == 'paused' and phase not in {'paused','draft-reviewed'}:
            label += ' · batch paused'
        return 'in-progress', label
    if state in {'undiscovered', 'proposed'}:
        return 'undiscovered', LABELS[state]
    if state == 'discovered':
        return 'unresearched', LABELS[state]
    return 'in-progress', LABELS.get(state, state.replace('-', ' ').title())


def badge(code, label):
    safe = html.escape(label, quote=True)
    return '<span class="item-status status-' + code + '" tabindex="0" role="img" aria-label="' + safe + '"><span aria-hidden="true">●</span><span class="status-text" aria-hidden="true">' + html.escape(label) + '</span></span>'


def ordered_levels(nodes, root, depth_field='level'):
    """Lease each child once, round-robin across parents in prior-level order."""
    by_level = {}
    for nid, node in nodes.items():
        if node[depth_field] is not None:
            by_level.setdefault(node[depth_field], []).append(nid)
    levels = []
    previous = [root]
    for level, ids in sorted(by_level.items()):
        if level == 0:
            levels.append({'level': 0, 'order': [root], 'groups': [{'parent': None, 'items': [root]}]})
            continue
        remaining = set(ids)
        groups = {parent: [] for parent in previous}
        cursors = dict.fromkeys(previous, 0)
        active = previous
        while remaining:
            added = False
            next_active = []
            for parent in active:
                children = nodes[parent]['children']
                cursor = cursors[parent]
                while cursor < len(children) and children[cursor] not in remaining:
                    cursor += 1
                if cursor < len(children):
                    child = children[cursor]
                    groups[parent].append(child)
                    remaining.remove(child)
                    cursor += 1
                    added = True
                    if cursor < len(children):
                        next_active.append(parent)
                cursors[parent] = cursor
            if not added:
                raise ValueError('Reachable level has no preceding-level parent')
            active = next_active
        grouped = [{'parent': parent, 'items': children} for parent, children in groups.items() if children]
        previous = [child for group in grouped for child in group['items']]
        levels.append({'level': level, 'order': previous, 'groups': grouped})
    return levels


def graph_model(registry, root='handset'):
    """O(V+E) representation and DP; decimal counts avoid JavaScript precision loss."""
    nodes = {n['id']: n for n in registry['nodes'] if physical(n)}
    routes = {r['id']: r for r in registry['routes']}
    selected = registry['scenarios'][0]['selected_routes']
    children = {nid: list(dict.fromkeys(q['target'] for q in routes[selected[nid]]['requires'] if q['target'] in nodes))
                if nid in selected else [] for nid in nodes}
    parents = {nid: [] for nid in nodes}
    for nid, requirements in children.items():
        for target in requirements:
            parents[target].append(nid)
    distance, predecessor = {}, {}
    queue = deque()
    if root in nodes:
        distance[root] = 0
        queue.append(root)
    while queue:
        nid = queue.popleft()
        for target in children[nid]:
            if target not in distance:
                distance[target] = distance[nid] + 1
                predecessor[target] = nid
                queue.append(target)
    incoming = {nid: len(parents[nid]) for nid in nodes}
    queue = deque(nid for nid, count in incoming.items() if count == 0)
    counts = dict.fromkeys(nodes, 0)
    deepest = dict.fromkeys(nodes, None)
    if root in nodes:
        counts[root] = 1
        deepest[root] = 0
    topological = []
    while queue:
        nid = queue.popleft()
        topological.append(nid)
        for target in children[nid]:
            counts[target] += counts[nid]
            if deepest[nid] is not None:
                deepest[target] = max(deepest[target] or 0, deepest[nid] + 1)
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    if len(topological) != len(nodes):
        raise ValueError('Physical presentation requires an acyclic validated graph')
    items = {}
    for nid, n in nodes.items():
        code, label = item_status(n, routes.get(selected.get(nid)))
        items[nid] = {'name': 'Smartphone' if nid == root else n['name'], 'role': n['role'],
                      'status': code, 'statusLabel': label, 'level': distance.get(nid), 'deepestLevel': deepest[nid],
                      'frontier': not children[nid] and not n.get('terminal') and code != 'candidate',
                      'parents': parents[nid], 'children': children[nid], 'paths': str(counts[nid])}
    return {'root': root, 'revision': registry['revision'], 'nodes': items, 'predecessor': predecessor,
            'topological': topological, 'levels': ordered_levels(items, root),
            'deepestLevels': ordered_levels(items, root, 'deepestLevel'),
            'connections': sum(len(n['children']) for n in items.values()),
            'reachableConnections': sum(len(n['children']) for n in items.values() if n['level'] is not None)}


def shortest_path(model, nid):
    if model['nodes'][nid]['level'] is None:
        return []
    path = [nid]
    while path[-1] != model['root']:
        path.append(model['predecessor'][path[-1]])
    return path[::-1]


def path_at(model, nid, rank):
    """Unrank any root-to-node physical path without listing earlier paths."""
    if not 0 <= rank < int(model['nodes'][nid]['paths']):
        raise IndexError('Path rank outside range')
    path = [nid]
    while nid != model['root']:
        for parent in model['nodes'][nid]['parents']:
            count = int(model['nodes'][parent]['paths'])
            if rank < count:
                nid = parent
                path.append(nid)
                break
            rank -= count
        else:
            raise ValueError('Inconsistent physical path counts')
    return path[::-1]


def coverage_paths(model, nid):
    """Greedy node coverage, not an enumeration or a claim of minimum set cover."""
    if model['nodes'][nid]['level'] is None:
        return []
    nodes, root = model['nodes'], model['root']
    ancestors, stack = set(), [nid]
    while stack:
        key = stack.pop()
        if key in ancestors:
            continue
        ancestors.add(key)
        stack.extend(parent for parent in nodes[key]['parents'] if nodes[parent]['level'] is not None)
    order = [key for key in model['topological'] if key in ancestors]
    paths = [shortest_path(model, nid)]
    uncovered = ancestors.difference(paths[0])
    while uncovered:
        scores, lengths, predecessor = {root: 0}, {root: 1}, {}
        for key in order:
            if key == root:
                continue
            choices = [p for p in nodes[key]['parents'] if p in scores]
            parent = max(choices, key=lambda p: (scores[p], -lengths[p]))
            scores[key] = scores[parent] + (key in uncovered)
            lengths[key] = lengths[parent] + 1
            predecessor[key] = parent
        path, key = [nid], nid
        while key != root:
            key = predecessor[key]
            path.append(key)
        path.reverse()
        if not uncovered.intersection(path):
            raise ValueError('Coverage route failed to add an ancestor')
        paths.append(path)
        uncovered.difference_update(path)
    # Later routes can make earlier ones redundant. Retain all item coverage.
    counts = dict.fromkeys(ancestors, 0)
    for path in paths:
        for key in path:
            counts[key] += 1
    keep = [True] * len(paths)
    for i in range(len(paths) - 1, -1, -1):
        if all(counts[key] > 1 for key in paths[i]):
            keep[i] = False
            for key in paths[i]:
                counts[key] -= 1
    return [path for path, included in zip(paths, keep) if included]


def parent_items(model, nid, node_link):
    parents = sorted(model['nodes'][nid]['parents'], key=lambda key: model['nodes'][key]['name'].casefold())
    body = '<section class="used-by"><h2>Used by</h2>'
    if not parents:
        return body + '<p>No parent items are currently recorded in the selected map.</p></section>'
    body += '<p>Items that directly require this item in their selected inventory.</p><ul class="used-by-list">'
    for parent in parents:
        item = model['nodes'][parent]
        body += '<li>' + node_link(parent, item['name']) + '</li>'
    return body + '</ul></section>'


def path_tracker(model, nid, node_link):
    if model['nodes'][nid]['level'] is None:
        return '<section class="path-tracker"><h2>Paths from Smartphone</h2><p>No selected physical path from Smartphone reaches this item. It is outside the current root map; no path is invented.</p></section>'
    first = ' → '.join(node_link(key, model['nodes'][key]['name']) for key in shortest_path(model, nid))
    return ('<section class="path-tracker" data-path-target="' + html.escape(nid, quote=True) + '"><h2>Paths from Smartphone</h2>'
            '<p>These routes together include every item that can lead from Smartphone to this item. Repeated path combinations are collapsed; recipes are omitted.</p>'
            '<div class="path-fallback"><p>Shortest route: ' + first + '</p><p>Enable JavaScript to see the routes covering every contributing item.</p></div>'
            '<div class="path-browser" hidden><p class="path-range" aria-live="polite"></p><ol class="path-list"></ol>'
            '<div class="ui-controls"><button type="button" data-path-prev>Previous 10</button><button type="button" data-path-next>Next 10</button>'
            '<label>Start at route <input data-path-jump inputmode="numeric" value="1" aria-label="Coverage route number"></label><button type="button" data-path-go>Go</button></div>'
            '<p class="path-error" role="alert"></p></div></section>')


def map_panel(model, view_link='', expanded=False):
    panel = '''<section class="dot-map"><h2>Physical dependency map</h2>
<p>Smartphone is centered. Choose shallowest (shortest path) or deepest (longest path) levels. Groups stay bunched near their parents and share available arc space without overlapping. Crowded full rings can use up to four rows; quieter rings use fewer. Shared items appear once. T = Tool; P = Part.</p>
<div class="map-legend"><span class="status-researched">● Fully researched record</span><span class="status-undiscovered">● Undiscovered proposal</span><span class="status-unresearched">● Discovered, unresearched</span><span class="status-in-progress">● Notes / research in progress</span><span class="status-candidate">● Candidate raw material (unapproved)</span><span>◯ Open frontier</span><span class="selection-key">⌜⌟ Selected</span></div>
<p class="small">Green requires reviewed evidence, complete inventory and specification, no recorded unresolved conditions, and a reviewed complete making route (or a reviewed terminal). It does not certify the whole manufacturing path. Red is used only for an explicitly undiscovered/proposed or missing research state; unknown undiscovered requirements cannot yet be plotted.</p>
<div class="ui-controls"><label>Find <input data-map-search type="search" placeholder="Name or canonical ID"></label>
<label>Levels <select data-map-depth><option value="shallowest">Shallowest · shortest path</option><option value="deepest">Deepest · longest path</option></select></label>
<label>Show <select data-map-filter><option value="all">All reachable items</option><option value="frontier">Open frontiers</option><option value="candidate">Candidate raw materials</option><option value="tool">Tools</option><option value="part">Parts</option><option value="unresearched">Discovered, unresearched</option><option value="researched">Fully researched</option><option value="outside">Outside Smartphone map</option></select></label>
<label>Relationships <select data-map-direction><option value="all">Whole map</option><option value="both">Ancestors and descendants</option><option value="descendants">Only descendants</option><option value="ancestors">Only ancestors</option></select></label>
<label>Relationship levels <select data-map-generations>''' + ''.join('<option value="' + str(i) + '">' + str(i) + '</option>' for i in range(1, 11)) + '''<option value="all">All levels</option></select></label>
<button type="button" data-map-fit>Fit all</button><button type="button" data-map-in aria-label="Zoom in">+</button><button type="button" data-map-out aria-label="Zoom out">−</button>
<label><input type="checkbox" data-map-connections> Show faint connections</label><button type="button" data-map-reset hidden>Back to Smartphone map</button><!-- MAP_VIEW_LINK --></div>
<p class="map-context" aria-live="polite"></p>
<div class="connection-legend"><span class="connection-up">━ Up to parent items</span><span class="connection-down">━ Down to required items</span></div>
<p class="map-summary" aria-live="polite"></p><div class="map-stage"><canvas class="map-canvas" tabindex="0" aria-label="Physical dependency map. Drag to pan, use plus and minus to zoom. Use the linked item list below for keyboard navigation."></canvas><div class="map-tooltip" hidden></div></div>
<p class="small">Hover for details; click a dot to pin it. Relationships are relative to that object: 2 levels shows children and grandchildren, or parents and grandparents. Choose “Making tree for this object” in its info box to center its requirements. Click empty space or press Escape to clear. Drag to pan; scroll to zoom. Parent paths are orange; descendant paths are blue and taper to 1px.</p>
<details open><summary>Accessible linked item list</summary><p>Uses the same search and filter; includes disconnected items when “Outside Smartphone map” is selected.</p><ul class="map-list"></ul><div class="ui-controls"><button type="button" data-map-prev>Previous 50</button><button type="button" data-map-next>Next 50</button></div></details>
<noscript><p>The interactive map and path browser require JavaScript. The complete linked inventory, route list and shortest paths below remain readable.</p></noscript></section>'''
    if expanded:
        panel = panel.replace('<details open>', '<details>')
        panel = panel.replace('The complete linked inventory, route list and shortest paths below remain readable.',
                              'Use Back to overview to browse the linked inventory without JavaScript.')
    return panel.replace('<!-- MAP_VIEW_LINK -->', '<span class="map-view-link">' + view_link + '</span>')
