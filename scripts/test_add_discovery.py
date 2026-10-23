import json
import tempfile
import threading
import unittest
from pathlib import Path
from add_discovery import add_to_map
from graph_gate import load_json


class SharedAddTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'registry.json'
        self.data={'revision':0,'nodes':[{'id':x,'name':x,'role':'part','terminal':False,'maturity':'proposed','inventory_complete':False}
                        for x in ['a','b','feed']], 'routes':[],
                   'scenarios':[{'id':'draft','roots':['a'],'selected_routes':{}}]}
        self.path.write_text(json.dumps(self.data),encoding='utf-8')

    def draft(self,output,target):
        return {'expansions':[{'output':output,'method':'Make '+output,'requires':[target]}]}

    def add(self,draft):return add_to_map(draft,self.path,refresh=False)

    def test_valid_commit_then_cycle_rejection_preserves_exact_bytes(self):
        self.assertTrue(self.add(self.draft('a','b'))['ok'])
        before=self.path.read_bytes()
        rejected=self.add(self.draft('b','a'))
        self.assertFalse(rejected['ok']);self.assertEqual(rejected['code'],'cycle')
        self.assertEqual(rejected['cycle'][0],rejected['cycle'][-1])
        self.assertEqual(before,self.path.read_bytes())

    def test_concurrent_joint_cycle_has_one_commit_and_one_rejection(self):
        barrier=threading.Barrier(2);results=[]
        def worker(output,target):
            barrier.wait();results.append(self.add(self.draft(output,target)))
        workers=[threading.Thread(target=worker,args=('a','b')),threading.Thread(target=worker,args=('b','a'))]
        for worker in workers:worker.start()
        for worker in workers:worker.join(10);self.assertFalse(worker.is_alive())
        self.assertEqual(sum(r['ok'] for r in results),1)
        self.assertEqual([r['code'] for r in results if not r['ok']],['cycle'])
        self.assertEqual(load_json(self.path)['revision'],1)

    def test_replacement_requires_explicit_current_revision_and_route(self):
        self.add(self.draft('a','feed'));before=self.path.read_bytes()
        self.assertEqual(self.add(self.draft('a','b'))['code'],'already_discovered')
        self.assertEqual(before,self.path.read_bytes())
        draft=self.draft('a','b');draft['base_revision']=1
        draft['expansions'][0]['expected_route']='discovery-memory-a-v1'
        self.assertTrue(self.add(draft)['ok'])

    def test_stale_explicit_request_and_invalid_id_do_not_write(self):
        before=self.path.read_bytes()
        draft=self.draft('a','feed');draft['base_revision']=99
        self.assertEqual(self.add(draft)['code'],'stale_revision')
        self.assertEqual(self.add({'new_items':[{'id':'../sources/bad','name':'bad','role':'part'}]})['code'],'invalid_id')
        self.assertEqual(before,self.path.read_bytes())

    def test_alias_cannot_bypass_concurrent_replacement_guard(self):
        self.data['nodes'][0]['aliases']=['widget']
        self.path.write_text(json.dumps(self.data),encoding='utf-8')
        self.add(self.draft('a','feed'));before=self.path.read_bytes()
        self.assertEqual(self.add(self.draft('widget','b'))['code'],'already_discovered')
        self.assertEqual(before,self.path.read_bytes())


if __name__=='__main__':unittest.main()
