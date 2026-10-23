"""Lifecycle, immutable evidence, metadata-only gates and discovery preservation."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from research_publication import artifact, safe_path, proposal_for, publish, BOOKKEEPING, checked_artifacts, snapshot_artifact
from research_ui import item_status
from test_graph_gate import node, route, registry
from add_discovery import add_to_map

class PublicationTests(unittest.TestCase):
    def setUp(self):
        scratch=Path(__file__).resolve().parents[2]/'.rpt'
        scratch.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=scratch);self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'proposals').mkdir();(self.root/'data').mkdir()
        self.reg=registry([node('a'),node('b')],[route('a',['b'])],{'a':'make-a'})
        for n in self.reg['nodes']:n.update(research_status='discovered',inventory_complete=False,spec_reviewed=False,unresolved_questions=['actual unknown grade'])
        self.report=self.file('report.md','# Real saved evidence','report')
    def file(self,name,text,kind):
        p=self.root/'proposals'/name;p.write_text(text,encoding='utf-8')
        return dict(path='proposals/'+name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),kind=kind,label=name)
    def manifest(self,state='completed',**extra):
        return dict(schema_version=1,items=[dict(id='a',state=state,scope='Bounded evidence, not qualification',artifacts=[self.report],**extra)])
    def proof(self,verdict='reviewed-as-draft'):
        audit=self.file('audit.json',json.dumps(dict(revision=84,reports=[dict(id='a',report_sha256=self.report['sha256'])])),'review-audit')
        decisions=self.file('decisions.json',json.dumps(dict(scope='review draft only',operations=[dict(record_ids=['a'],amended_decision=verdict)])),'review-decisions')
        return dict(audit=audit,decisions=decisions)
    def test_safe_paths_and_hashes_reject_escape_missing_and_tamper(self):
        for p in ['../report.md','C:/report.md','proposals/../data/a.json','proposals/missing.md','proposals\\report.md','https://x/a.md']:
            with self.subTest(p=p),self.assertRaises(ValueError):safe_path(self.root,p)
        bad={**self.report,'sha256':'0'*64}
        with self.assertRaises(ValueError):artifact(self.root,bad)
    def test_snapshot_provenance_cannot_escape_or_be_reassigned(self):
        snap=snapshot_artifact(self.root,self.report)
        for source in ['../outside.md','proposals/other.md',None,{'unsafe':True}]:
            with self.subTest(source=source),self.assertRaises(ValueError):artifact(self.root,{**snap,'source_path':source})
    def test_same_bytes_at_different_paths_keep_distinct_provenance(self):
        second=self.file('other.md','# Real saved evidence','report')
        self.assertNotEqual(artifact(self.root,self.report)['page'],artifact(self.root,second)['page'])
        first_snap=snapshot_artifact(self.root,self.report);second_snap=snapshot_artifact(self.root,second)
        self.assertNotEqual(first_snap['path'],second_snap['path'])
        self.assertNotEqual(first_snap['page'],second_snap['page'])
    def test_changed_source_does_not_break_historical_snapshot_new_version_needs_review(self):
        old_proof=self.proof()
        old=proposal_for(self.reg,self.manifest('reviewed',review_proof=old_proof),self.root)['upsert_nodes'][0]
        old_report=next(a for a in old['research_artifacts'] if a['kind']=='report')
        progress=self.file('progress.json','{"completed_reports":1}','progress')
        p_snapshot=snapshot_artifact(self.root,progress)
        self.file('report.md','# New expanded unreviewed research','report')
        self.file('progress.json','{"completed_reports":2}','progress')
        self.assertEqual(artifact(self.root,old_report)['sha256'],self.report['sha256'])
        self.assertEqual(artifact(self.root,p_snapshot)['sha256'],progress['sha256'])
        self.assertEqual((self.root/old_report['path']).read_text(encoding='utf-8'),'# Real saved evidence')
        self.reg['nodes'][0]=old
        new_report=self.file('report.md','# New expanded unreviewed research','report')
        m=self.manifest();m['items'][0]['artifacts']=[new_report]
        fresh=proposal_for(self.reg,m,self.root)['upsert_nodes'][0]
        self.assertEqual(fresh['research_status'],'research-draft');self.assertIsNone(fresh['research_activity']['review'])
        self.assertEqual(len([a for a in fresh['research_artifacts'] if a['kind']=='report']),2)
        self.assertTrue(checked_artifacts(self.root,fresh))
        m['items'][0].update(state='reviewed',review_proof=old_proof)
        with self.assertRaises(ValueError):proposal_for(self.reg,m,self.root)
    def test_file_existence_never_infers_completion(self):
        m=self.manifest('assigned');m['items'][0]['artifacts']=[]
        n=proposal_for(self.reg,m,self.root)['upsert_nodes'][0]
        self.assertEqual(n['research_status'],'discovered');self.assertEqual(n['research_activity']['state'],'assigned')
        self.assertEqual(n['research_artifacts'],[]);self.assertEqual(item_status(n)[0],'in-progress')
    def test_completed_requires_explicit_report_and_hash(self):
        m=self.manifest();m['items'][0]['artifacts']=[]
        with self.assertRaises(ValueError):proposal_for(self.reg,m,self.root)
    def test_reviewed_draft_remains_blue_and_quality_unknowns_preserved(self):
        n=proposal_for(self.reg,self.manifest('reviewed',review_proof=self.proof()),self.root)['upsert_nodes'][0]
        self.assertEqual(n['research_status'],'reviewed');self.assertEqual(item_status(n)[0],'in-progress')
        self.assertFalse(n['inventory_complete']);self.assertFalse(n['spec_reviewed'])
        self.assertEqual(n['unresolved_questions'],self.reg['nodes'][0]['unresolved_questions'])
    def test_current_started_research_keeps_old_hash_bound_review(self):
        n=proposal_for(self.reg,self.manifest('started',review_proof=self.proof()),self.root)['upsert_nodes'][0]
        self.assertEqual(n['research_status'],'reviewed');self.assertEqual(n['research_activity']['phase'],'researching')
        self.assertEqual(n['evidence_status'],'independently-reviewed-evidence-draft')
        self.assertEqual(n['research_activity']['review']['revision'],84)
        self.assertIn('earlier evidence draft reviewed',item_status(n)[1])
    def test_unreviewed_and_paused_report_labels_are_distinct(self):
        n=proposal_for(self.reg,self.manifest('completed',batch_state='paused'),self.root)['upsert_nodes'][0]
        self.assertIn('awaiting independent review',item_status(n)[1]);self.assertIn('batch paused',item_status(n)[1])
        m=self.manifest('paused');m['items'][0]['artifacts']=[]
        n=proposal_for(self.reg,m,self.root)['upsert_nodes'][0]
        self.assertIn('no completed report',item_status(n)[1])
    def test_prior_review_survives_started_then_paused_without_promotion(self):
        proof=self.proof()
        n=proposal_for(self.reg,self.manifest('started',review_proof=proof),self.root)['upsert_nodes'][0]
        self.reg['nodes'][0]=n
        paused=proposal_for(self.reg,self.manifest('paused',review_proof=proof,batch_state='paused'),self.root)['upsert_nodes'][0]
        self.assertEqual(paused['evidence_status'],'independently-reviewed-evidence-draft')
        self.assertEqual(paused['research_activity']['review']['revision'],84)
        self.assertFalse(paused['spec_reviewed'])
        self.assertIn('earlier evidence draft reviewed',item_status(paused)[1])
        self.assertNotIn('no completed report',item_status(paused)[1])
    def test_stale_lifecycle_cannot_overwrite_new_activity(self):
        with self.assertRaises(ValueError):proposal_for(self.reg,self.manifest('started',expected_activity={'state':'old'}),self.root)
    def test_complete_requires_review_certification_and_true_own_quality(self):
        proof=self.proof('research-complete');proof['certification']='immediate-record-complete'
        m=self.manifest('complete',review_proof=proof)
        with self.assertRaises(ValueError):proposal_for(self.reg,m,self.root)
        a=self.reg['nodes'][0];a.update(inventory_complete=True,spec_reviewed=True,unresolved_questions=[])
        n=proposal_for(self.reg,m,self.root)['upsert_nodes'][0]
        self.assertEqual(item_status(n,self.reg['routes'][0])[0],'researched')
        self.assertFalse(self.reg['nodes'][1]['inventory_complete']) # descendant closure is separate
    def test_draft_decision_cannot_be_promoted_to_full_completion(self):
        with self.assertRaises(ValueError):proposal_for(self.reg,self.manifest('complete',review_proof={**self.proof(),'certification':'immediate-record-complete'}),self.root)
    def test_complete_cannot_hide_unknown_immediate_requirement_contract(self):
        proof={**self.proof('research-complete'),'certification':'immediate-record-complete'}
        self.reg['nodes'][0].update(inventory_complete=True,spec_reviewed=True,unresolved_questions=[])
        self.reg['routes'][0]['requires'][0].update(compatibility='unknown',required_capability={'limits':'not yet specified'})
        with self.assertRaises(ValueError):proposal_for(self.reg,self.manifest('complete',review_proof=proof),self.root)
    def test_metadata_gate_preserves_graph_and_all_unrelated_node_fields(self):
        path=self.root/'data/registry.json';path.write_text(json.dumps(self.reg),encoding='utf-8')
        before=copy.deepcopy(self.reg);result=publish(self.manifest(),self.root,path,rebuild=False)
        saved=json.loads(path.read_text(encoding='utf-8'));self.assertEqual(result['revision'],1)
        self.assertEqual(saved['routes'],before['routes']);self.assertEqual(saved['scenarios'],before['scenarios'])
        self.assertEqual(saved['nodes'][1],before['nodes'][1])
        for field in ['inventory_complete','spec_reviewed','terminal','maturity','unresolved_questions']:
            self.assertEqual(saved['nodes'][0][field],before['nodes'][0][field])
    def test_only_obsolete_bookkeeping_can_be_replaced_and_history_retained(self):
        old=next(iter(BOOKKEEPING));self.reg['nodes'][0]['unresolved_questions'].append(old)
        upd=dict(before=old,after=BOOKKEEPING[old],reason='Saved report exists; real unknowns retained')
        n=proposal_for(self.reg,self.manifest(bookkeeping_updates=[upd]),self.root)['upsert_nodes'][0]
        self.assertIn('actual unknown grade',n['unresolved_questions']);self.assertEqual(n['research_bookkeeping_history'],[upd])
        with self.assertRaises(ValueError):proposal_for(self.reg,self.manifest(bookkeeping_updates=[dict(before='actual unknown grade',after='resolved',reason='unsafe')]),self.root)
    def test_discovery_replacement_preserves_activity_reports_and_evidence(self):
        n=proposal_for(self.reg,self.manifest('reviewed',review_proof=self.proof()),self.root)['upsert_nodes'][0]
        self.reg['nodes'][0]=n;path=self.root/'data/registry.json';path.write_text(json.dumps(self.reg),encoding='utf-8')
        result=add_to_map(dict(base_revision=0,expansions=[dict(output='a',expected_route='make-a',method='New unreviewed making recipe',requires=['b'])]),path,refresh=False)
        self.assertTrue(result['ok']);new=json.loads(path.read_text(encoding='utf-8'))['nodes'][0]
        for field in ['research_status','evidence_status','research_artifacts','research_activity']:
            self.assertEqual(new[field],n[field])
        self.assertFalse(new['inventory_complete']);self.assertFalse(new['spec_reviewed'])

if __name__=='__main__':unittest.main()
