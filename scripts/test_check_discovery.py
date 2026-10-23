import copy
import unittest
from check_discovery import probe
from graph_gate import GateError


class DiscoveryProbeTests(unittest.TestCase):
    def registry(self):
        return {'revision':2,'nodes':[{'id':x,'name':x,'role':r,'terminal':False,'maturity':'proposed','inventory_complete':False}
                for x,r in [('a','part'),('b','part'),('tool','tool')]],'routes':[],
                'scenarios':[{'id':'draft','roots':['a'],'selected_routes':{}}]}

    def test_cycle_is_preserved_and_source_is_unchanged(self):
        source=self.registry();before=copy.deepcopy(source)
        result=probe(source,{'base_revision':2,'expansions':[
            {'output':'a','method':'make a','requires':['b']},
            {'output':'b','method':'make b','requires':['a']}]})
        self.assertFalse(result['ok']);self.assertEqual(result['error']['code'],'cycle')
        self.assertEqual(len(result['proposal']['upsert_routes']),2)
        self.assertEqual(source,before)

    def test_reused_tool_and_new_stock_remain_unreviewed(self):
        result=probe(self.registry(),{'base_revision':2,'new_items':[{'id':'stock','name':'Stock','role':'part'}],
            'expansions':[{'output':'a','method':'form a','requires':[{'target':'tool','use':'reused'},'Stock']}]})
        self.assertTrue(result['ok'])
        req=result['proposal']['upsert_routes'][0]['requires']
        self.assertEqual([q['target'] for q in req],['tool','stock'])
        self.assertEqual(req[0]['role'],'tool')
        self.assertFalse(result['validation']['scenarios'][0]['target_research_closed'])

    def test_tool_role_error_is_distinct_from_cycle(self):
        with self.assertRaises(GateError) as caught:
            probe(self.registry(),{'base_revision':2,'expansions':[{'output':'a','method':'form','requires':[{'target':'tool','role':'part'}]}]})
        self.assertEqual(caught.exception.code,'role_mismatch')


if __name__=='__main__':unittest.main()
