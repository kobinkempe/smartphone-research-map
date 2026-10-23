import unittest
from agent_context import compact_index, scoped_context, relationship_inventory, bfs_plan


class ScopedContextTests(unittest.TestCase):
    def registry(self):
        return {'revision': 9,
                'nodes': [{'id': n, 'name': n, 'role': 'part', 'aliases': ['stored program'] if n == 'memory' else []}
                          for n in ['phone', 'chip', 'memory', 'power']],
                'routes': [{'id': 'assemble', 'output': 'phone', 'requires': [{'target': 'chip'}]},
                           {'id': 'chip-route', 'output': 'chip', 'requires': [{'target': 'memory'}]},
                           {'id': 'alternative', 'output': 'chip', 'requires': [{'target': 'power'}]}],
                'scenarios': [{'selected_routes': {'phone': 'assemble', 'chip': 'chip-route'}}]}

    def test_slice_keeps_candidate_distinct_and_does_not_expand_it(self):
        result = scoped_context(self.registry(), 'phone', 2)
        self.assertEqual(result['base_revision'], 9)
        self.assertEqual(set(result['distance']), {'phone', 'chip', 'memory'})
        self.assertEqual(result['outside_candidate_reference_ids'], ['power'])
        self.assertEqual([r['id'] for r in result['unselected_candidate_routes']], ['alternative'])

    def test_global_index_keeps_alias_and_canonical_identity(self):
        records = {n['id']: n for n in compact_index(self.registry())}
        self.assertEqual(records['memory']['aliases'], ['stored program'])
        self.assertEqual(records['chip']['selected_route'], 'chip-route')

    def test_cap_keeps_missing_context_references_explicit(self):
        result=scoped_context(self.registry(),'phone',3,max_nodes=2)
        self.assertEqual(set(result['distance']),{'phone','chip'})
        self.assertEqual(result['omitted_by_node_cap'],['memory'])
        self.assertEqual(result['outside_selected_reference_ids'],['memory'])
        self.assertEqual(result['outside_candidate_reference_ids'],['power'])

    def test_inventory_partitions_full_registry_and_ignores_unselected_routes(self):
        result = relationship_inventory(self.registry(), 'memory')
        self.assertEqual([n['id'] for n in result['direct_parents']], ['chip'])
        self.assertEqual([n['id'] for n in result['other_ancestors']], ['phone'])
        self.assertEqual([n['id'] for n in result['non_ancestors']], ['power'])
        self.assertEqual(result['forbidden_requirement_ids'], ['chip', 'memory', 'phone'])
        self.assertEqual(relationship_inventory(self.registry(), 'power')['counts']['direct_parents'], 0)

    def test_inventory_includes_disconnected_shared_and_distant_ancestors(self):
        registry = self.registry()
        registry['nodes'].append({'id': 'fixture', 'name': 'fixture', 'role': 'tool'})
        registry['routes'].append({'id': 'fixture-route', 'output': 'fixture', 'requires': [{'target': 'memory'}]})
        registry['scenarios'][0]['selected_routes']['fixture'] = 'fixture-route'
        result = relationship_inventory(registry, 'memory')
        self.assertEqual([n['id'] for n in result['direct_parents']], ['chip', 'fixture'])
        self.assertEqual(result['counts'], {'direct_parents': 2, 'other_ancestors': 1, 'non_ancestors': 1})

    def test_inventory_rejects_unknown_item(self):
        with self.assertRaises(ValueError):
            relationship_inventory(self.registry(), 'missing')

    def test_ids_only_inventory_preserves_complete_partitions(self):
        full = relationship_inventory(self.registry(), 'memory')
        lean = relationship_inventory(self.registry(), 'memory', ids_only=True)
        self.assertEqual(full['counts'], lean['counts'])
        for key in ['direct_parents', 'other_ancestors', 'non_ancestors']:
            self.assertEqual([n['id'] for n in full[key]], lean[key])

    def test_bfs_traverses_existing_routes_and_stops_at_boundary(self):
        plan = bfs_plan(self.registry(), 'phone', depth=2)
        self.assertEqual(plan['levels'][0]['existing_inventory_ids'], ['phone'])
        self.assertEqual(plan['levels'][1]['existing_inventory_ids'], ['chip'])
        self.assertEqual(plan['boundary_ids'], ['memory'])
        self.assertNotIn('power', plan['boundary_ids'])
        self.assertEqual(bfs_plan(self.registry(), 'phone', 3)['levels'][2]['needs_inventory'][0]['id'], 'memory')

    def test_bfs_deduplicates_shared_outputs_at_shortest_distance(self):
        registry = self.registry()
        registry['routes'][0]['requires'].append({'target': 'memory'})
        plan = bfs_plan(registry, 'phone', depth=3)
        self.assertEqual([n['id'] for n in plan['levels'][1]['needs_inventory']], ['memory'])
        self.assertEqual(plan['levels'][2]['needs_inventory'], [])

    def test_bfs_skips_bootstrap_and_natural_frontiers(self):
        registry = self.registry()
        plan = bfs_plan(registry, 'phone', 3, bootstrap_ids=['memory'])
        self.assertEqual(plan['levels'][2]['skipped'], [{'id': 'memory', 'reason': 'bootstrap queue'}])
        registry['nodes'][2]['discovery_leaf_kind'] = 'candidate-natural-occurrence'
        plan = bfs_plan(registry, 'phone', 3)
        self.assertEqual(plan['levels'][2]['needs_inventory'], [])
        self.assertIn('natural-occurrence', plan['levels'][2]['skipped'][0]['reason'])

    def test_bfs_rejects_invalid_depth_or_root(self):
        with self.assertRaises(ValueError):
            bfs_plan(self.registry(), 'phone', 0)
        with self.assertRaises(ValueError):
            bfs_plan(self.registry(), 'missing', 3)


if __name__ == '__main__': unittest.main()
