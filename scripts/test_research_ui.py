"""Regression checks for compact complete map, truthful states and all-path access."""
import json
import subprocess
import unittest
from pathlib import Path
from research_ui import graph_model, item_status, shortest_path, path_at, path_tracker, coverage_paths, badge

ROOT=Path(__file__).resolve().parents[1]


def node(nid, **attrs):
    return dict(id=nid,name=nid,role='part',research_status='discovered',terminal=False,
                inventory_complete=False,spec_reviewed=False,**attrs)


def registry(edges, extras=()):
    ids=list(dict.fromkeys(['handset']+[key for pair in edges for key in pair]+list(extras)))
    children={key:[] for key in ids}
    for parent, child in edges:children[parent].append(child)
    return {'revision':7,'nodes':[node(key) for key in ids],
            'routes':[{'id':'make-'+key,'output':key,'requires':[{'target':child} for child in values]} for key,values in children.items() if values],
            'scenarios':[{'selected_routes':{key:'make-'+key for key,values in children.items() if values}}]}


class ResearchUITests(unittest.TestCase):
    def test_flexible_group_packing_avoids_long_radial_columns(self):
        edges=[('handset','p1'),('handset','p2'),('handset','p3')]
        for parent,count in [('p1',11),('p2',3),('p3',8)]:
            edges.extend((parent,parent+'-child'+str(i)) for i in range(count))
        crowded=[('handset','hub')]+[('hub','p'+str(i)) for i in range(8)]
        crowded.extend(('p'+str(i),'leaf'+str(i)+'-'+str(j)) for i in range(8) for j in range(6))
        shared=[('handset','a'),('handset','b'),('a','b')]+[('b','c'+str(i)) for i in range(12)]
        dense=[('handset','p'+str(i)) for i in range(12)]
        dense.extend(('p'+str(i),'leaf'+str(i)+'-'+str(j)) for i in range(12) for j in range(10))
        overfull=[('handset','p'+str(i)) for i in range(12)]
        overfull.extend(('p'+str(i),'overflow'+str(i)+'-'+str(j)) for i in range(12) for j in range(24))
        columns=[('handset','hub')]+[('hub','p'+str(i)) for i in range(6)]
        for i,count in enumerate([26,24,3,3,3,3]):
            columns.extend(('p'+str(i),'column'+str(i)+'-'+str(j)) for j in range(count))
        models=[graph_model(registry(example)) for example in (edges,crowded,shared,dense,columns,overfull)]
        result=subprocess.run(['node',str(ROOT/'scripts/test_map_layout.js'),str(ROOT/'scripts/assets/research-ui.js')],
                              input=json.dumps(models),capture_output=True,text=True,check=True)
        self.assertIn('Flexible parent groups',result.stdout)

    def test_longest_and_shortest_levels_bound_every_root_path(self):
        model=graph_model(registry([('handset','a'),('handset','c'),('a','b'),('b','c'),('c','d')],['outside']))
        self.assertEqual(model['nodes']['c']['level'],1)
        self.assertEqual(model['nodes']['c']['deepestLevel'],3)
        self.assertIsNone(model['nodes']['outside']['deepestLevel'])
        for key,n in model['nodes'].items():
            if n['level'] is None:
                continue
            lengths=[len(path_at(model,key,i))-1 for i in range(int(n['paths']))]
            self.assertEqual(n['level'],min(lengths))
            self.assertEqual(n['deepestLevel'],max(lengths))
        self.assertEqual([x['order'] for x in model['deepestLevels']],[['handset'],['a'],['b'],['c'],['d']])
        js="globalThis.RESEARCH_GRAPH="+json.dumps(model)+";\n"+(ROOT/'scripts/assets/research-ui.js').read_text(encoding='utf-8')
        js+="\nprocess.stdout.write(JSON.stringify(ResearchUI.orderedLevels(RESEARCH_GRAPH,'deepest')));"
        result=json.loads(subprocess.run(['node','-'],input=js,capture_output=True,text=True,encoding='utf-8',check=True).stdout)
        self.assertEqual(result,model['deepestLevels'])

    def test_coverage_collapses_user_example_to_two_routes(self):
        model=graph_model(registry([('handset','b'),('handset','c'),('b','c'),
                                   ('c','d'),('c','e'),('d','f'),('e','f')]))
        self.assertEqual(model['nodes']['f']['paths'],'4')
        routes=coverage_paths(model,'f')
        self.assertEqual(routes,[['handset','c','d','f'],['handset','b','c','e','f']])
        self.assertEqual(set().union(*map(set,routes)),{'handset','b','c','d','e','f'})
        self.assertNotIn('4</strong>',path_tracker(model,'f',lambda key,name:name))

    def test_coverage_handles_exponential_combinations_and_unreachable_nodes(self):
        edges=[('handset','a0'),('handset','b0')]
        for i in range(1,61):
            edges.extend((p+str(i-1),c+str(i)) for p in ('a','b') for c in ('a','b'))
        model=graph_model(registry(edges,['outside']))
        routes=coverage_paths(model,'a60')
        self.assertEqual(len(routes),2)
        self.assertEqual(len(set().union(*map(set,routes))),122)
        self.assertEqual(coverage_paths(model,'outside'),[])
        self.assertEqual(coverage_paths(model,'handset'),[['handset']])
        for route in routes:
            self.assertTrue(all(b in model['nodes'][a]['children'] for a,b in zip(route,route[1:])))

    def test_parent_grouping_is_round_robin_and_preserves_declared_order(self):
        model=graph_model(registry([('handset','p1'),('handset','p2'),('p1','shared'),
                                   ('p1','a'),('p1','b'),('p2','shared'),('p2','b'),('p2','c')]))
        level=model['levels'][2]
        self.assertEqual(level['groups'],[{'parent':'p1','items':['shared','a']},{'parent':'p2','items':['b','c']}])
        self.assertEqual(level['order'],['shared','a','b','c'])
        self.assertEqual(model['connections'],8)
        self.assertEqual(model['reachableConnections'],8)

    def test_javascript_coverage_and_parent_layout_match_python(self):
        model=graph_model(registry([('handset','b'),('handset','c'),('b','c'),
                                   ('c','d'),('c','e'),('d','f'),('e','f')]))
        js="globalThis.RESEARCH_GRAPH="+json.dumps(model)+";\n"+(ROOT/'scripts/assets/research-ui.js').read_text(encoding='utf-8')
        js+="\nprocess.stdout.write(JSON.stringify({paths:ResearchUI.coveragePaths('f'),levels:ResearchUI.orderedLevels(RESEARCH_GRAPH)}));"
        result=json.loads(subprocess.run(['node','-'],input=js,capture_output=True,text=True,encoding='utf-8',check=True).stdout)
        self.assertEqual(result['paths'],coverage_paths(model,'f'))
        self.assertEqual(result['levels'],model['levels'])

    def test_status_badge_has_accessible_hover_only_text(self):
        markup=badge('unresearched','Discovered & unresearched')
        self.assertIn('tabindex="0"',markup)
        self.assertIn('aria-label="Discovered &amp; unresearched"',markup)
        self.assertIn('class="status-text" aria-hidden="true"',markup)

    def test_shared_paths_exact_and_recipes_collapsed(self):
        model=graph_model(registry([('handset','a'),('handset','b'),('a','b'),('a','c'),('b','c')],['outside']))
        self.assertEqual(model['nodes']['c']['paths'],'3')
        self.assertEqual(model['nodes']['c']['level'],2)
        self.assertEqual({tuple(path_at(model,'c',i)) for i in range(3)},
                         {('handset','a','c'),('handset','b','c'),('handset','a','b','c')})
        self.assertEqual(shortest_path(model,'c'),['handset','a','c'])
        self.assertEqual(model['nodes']['outside']['paths'],'0')
        self.assertEqual(shortest_path(model,'outside'),[])
        self.assertEqual(path_at(model,'handset',0),['handset'])
        self.assertEqual(model['nodes']['handset']['name'],'Smartphone')
        with self.assertRaises(IndexError):path_at(model,'c',3)

    def test_exponential_paths_do_not_expand_model_or_lose_precision(self):
        edges=[('handset','a0'),('handset','b0')]
        for i in range(1,81):
            edges.extend((parent+str(i-1),child+str(i)) for parent in ('a','b') for child in ('a','b'))
        model=graph_model(registry(edges))
        self.assertEqual(model['nodes']['a80']['paths'],str(2**80))
        self.assertLess(len(json.dumps(model)),90000)
        self.assertEqual(len(path_at(model,'a80',2**80-1)),82)

    def test_every_level_is_in_model_including_beyond_five(self):
        model=graph_model(registry([('handset','n0')]+[('n'+str(i),'n'+str(i+1)) for i in range(100)]))
        self.assertEqual(model['nodes']['n100']['level'],101)

    def test_candidates_notes_and_review_gaps_never_show_as_complete(self):
        n=node('clay');n['discovery_leaf_kind']='candidate-natural-occurrence'
        self.assertEqual(item_status(n)[0],'candidate')
        n=node('notes');n['research_status']='inherited'
        self.assertEqual(item_status(n)[0],'in-progress')
        n['research_status']='reviewed';n.update(inventory_complete=True,spec_reviewed=True)
        self.assertEqual(item_status(n)[0],'in-progress')
        route={'reviewed':True,'inventory_complete':True}
        self.assertEqual(item_status(n,route)[0],'researched')
        n['unresolved_questions']=['missing input']
        self.assertEqual(item_status(n,route)[0],'in-progress')
        n['research_status']='discovered'
        self.assertEqual(item_status(n,route)[0],'unresearched')

    def test_nonphysical_boundaries_are_excluded(self):
        data=registry([('handset','software'),('handset','carrier'),('handset','a')])
        data['nodes'][1]['scope']='black-box-software'
        data['nodes'][2]['boundary']='external'
        model=graph_model(data)
        self.assertEqual(set(model['nodes']),{'handset','a'})

    def test_unreachable_tracker_is_explicit(self):
        model=graph_model(registry([],['outside']))
        body=path_tracker(model,'outside',lambda nid,label:label)
        self.assertIn('No selected physical path',body)
        self.assertNotIn('data-path-target',body)

    def test_javascript_unranking_matches_python_above_safe_integer(self):
        edges=[('handset','a0'),('handset','b0')]
        for i in range(1,61):
            edges.extend((parent+str(i-1),child+str(i)) for parent in ('a','b') for child in ('a','b'))
        data=registry(edges)
        model=graph_model(data)
        js="globalThis.RESEARCH_GRAPH="+json.dumps(model)+";\n"+(ROOT/'scripts/assets/research-ui.js').read_text(encoding='utf-8')
        last=2**60-1
        js+="\nprocess.stdout.write(JSON.stringify([ResearchUI.pathAt('a60',0n),ResearchUI.pathAt('a60',"+str(last)+"n)]));"
        result=subprocess.run(['node','-'],input=js,capture_output=True,text=True,encoding='utf-8',check=True)
        self.assertEqual(json.loads(result.stdout),[path_at(model,'a60',0),path_at(model,'a60',last)])

    def test_ui_controls_in_dom_doubles(self):
        result=subprocess.run(['node',str(ROOT/'scripts/test_ui_controls.js'),str(ROOT/'scripts/assets/research-ui.js')],capture_output=True,text=True,check=True)
        self.assertIn('passed in DOM doubles',result.stdout)


if __name__=='__main__':unittest.main()
