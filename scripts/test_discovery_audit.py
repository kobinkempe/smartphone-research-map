import unittest
from discovery_audit import coverage, checked_trails


class DiscoveryCoverageTests(unittest.TestCase):
    def fixture(self):
        return {'revision': 1, 'nodes': [dict(id=n, role='part', terminal=False,
                **({'discovery_leaf_kind': 'candidate-natural-occurrence'} if n == 'sand' else {}))
                for n in ['handset', 'glass', 'furnace', 'sand', 'fuel']],
                'routes': [{'id': 'phone-route', 'output': 'handset', 'requires': [{'target': 'glass'}, {'target': 'fuel'}]},
                           {'id': 'glass-route', 'output': 'glass', 'requires': [{'target': 'furnace'}, {'target': 'sand'}]},
                           {'id': 'furnace-route', 'output': 'furnace', 'requires': [{'target': 'fuel'}]}],
                'scenarios': [{'selected_routes': {'handset': 'phone-route', 'glass': 'glass-route', 'furnace': 'furnace-route'}}]}

    def test_shared_prerequisite_has_shortest_output_distance(self):
        result = coverage(self.fixture())
        self.assertEqual(result['distance']['fuel'], 1)
        self.assertEqual(result['distance']['sand'], 2)
        self.assertEqual(result['reachable_physical_outputs'], 5)
        self.assertEqual(result['gaps_before_level_5'], ['fuel'])
        self.assertFalse(result['discovery_complete_through_level_5'])

    def test_candidate_is_distinct_from_open_manufactured_frontier(self):
        result = coverage(self.fixture())
        self.assertEqual(result['candidate_natural_occurrences'], ['sand'])
        self.assertNotIn('sand', result['unexpanded_frontiers'])

    def test_trails_cannot_skip_a_missing_edge(self):
        checked_trails(self.fixture(), [{'path': ['handset', 'glass', 'sand']}])
        with self.assertRaises(ValueError):
            checked_trails(self.fixture(), [{'path': ['handset', 'sand']}])


if __name__ == '__main__':
    unittest.main()
