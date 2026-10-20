import tempfile
import unittest
from pathlib import Path
from libraries.echo_sentence_cards import SentenceCards,sense_id,lexicon_from_zip
from libraries.catalog_box import Conflict
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'cards.sqlite';self.e=SentenceCards(self.path)
        self.data={w:{'senses':[{'pos':p,'def':d}]} for w,p,d in [('poodle','noun','a dog'),('dog','noun','an animal'),('animal','noun','an entity'),('parcel','noun','an object'),('object','noun','a thing'),('carry','verb','transport'),('have','verb','possess'),('sleep','verb','rest')]}
        self.e.ingest(self.data,source={'test':True})
        for cid,a,b in [('pd','poodle','dog'),('da','dog','animal'),('po','parcel','object')]:self.e.subtype(cid,sense_id(a,0),sense_id(b,0),evidence={'fixture':'explicit assumption'})
        self.slots=[{'role':r,'sense':sense_id(w,0)} for r,w in [('agent','poodle'),('predicate','carry'),('patient','parcel')]]
        self.e.frame('s',self.slots)
    def tearDown(self):self.e.close();self.tmp.cleanup()
    def test_sense_separation(self):
        self.e.ingest({'move':{'senses':[{'pos':'noun','def':'an act'},{'pos':'verb','def':'change location'}]}},source={})
        self.assertNotEqual(sense_id('move',0),sense_id('move',1))
        self.assertEqual(self.e._sense(sense_id('move',1))['body']['pos'],'verb')
    def test_retry_no_revisions(self):
        n=len(self.e.box.events());self.e.ingest(self.data,source={'test':True});self.assertEqual(n,len(self.e.box.events()))
    def test_generalize_chain_preserves_positions_and_original(self):
        r=self.e.transform('s','s:0',sense_id('animal',0),mode='generalize',expected_revision=1)
        self.assertEqual(r['body']['history'][0]['evidence'],['pd','da'])
        self.assertEqual(r['body']['slots'][0]['position_id'],'s:0')
        self.assertEqual(self.e.box.get('cards','s',1)['body']['slots'][0]['selected']['id'],sense_id('poodle',0))
    def test_specialization_is_candidate(self):
        self.e.transform('s','s:0',sense_id('animal',0),mode='generalize',expected_revision=1)
        r=self.e.transform('s','s:0',sense_id('poodle',0),mode='specialize',expected_revision=2)
        self.assertEqual(r['body']['claim_status'],'candidate-needs-instance-evidence')
    def test_unrelated_substitution_no_write(self):
        n=len(self.e.box.events())
        with self.assertRaises(ValueError):self.e.transform('s','s:0',sense_id('object',0),mode='generalize',expected_revision=1)
        self.assertEqual(n,len(self.e.box.events()))
    def test_direction(self):
        with self.assertRaises(ValueError):self.e.transform('s','s:0',sense_id('animal',0),mode='specialize',expected_revision=1)
    def test_universal_and_negative_not_inferred(self):
        for scope in ('universal','negative'):
            with self.assertRaises(ValueError):self.e.frame('bad',self.slots,scope=scope)
    def test_wrong_role(self):
        self.slots[0]['sense']=sense_id('carry',0)
        with self.assertRaises(ValueError):self.e.frame('bad',self.slots)
    def test_reorder_does_not_swap_entity_roles(self):
        r=self.e.reorder('s',['s:2','s:1','s:0'],expected_revision=1)
        self.assertEqual(r['body']['slots'][0]['role'],'patient');self.assertEqual(self.e.render('s')['decision'],'ABSTAIN')
        self.e.reorder('s',['s:0','s:1','s:2'],expected_revision=2)
        self.assertEqual(self.e.render('s')['sentence'],'Some poodle carries some parcel.')
    def test_missing_position(self):
        with self.assertRaises(ValueError):self.e.reorder('s',['s:0','s:1'],expected_revision=1)
    def test_stale_write(self):
        with self.assertRaises(Conflict):self.e.transform('s','s:0',sense_id('dog',0),mode='generalize',expected_revision=9)
        self.assertEqual(self.e.box.get('cards','s')['revision'],1)
    def test_restart(self):
        self.e.transform('s','s:0',sense_id('dog',0),mode='generalize',expected_revision=1)
        self.e.close();self.e=SentenceCards(self.path)
        self.assertEqual(self.e.render('s')['sentence'],'Some dog carries some parcel.')
        self.assertEqual(len(self.e.box.history('cards','s')),2)
    def test_changed_sense_invalidates_edge(self):
        cid=sense_id('dog',0);c=self.e.box.get('cards',cid)
        self.e.box.put_card(cid,c['title'],dict(c['body'],definition='changed'),expected_revision=1)
        with self.assertRaises(ValueError):self.e.transform('s','s:0',sense_id('animal',0),mode='generalize',expected_revision=1)
    def test_read_only(self):
        self.e.writable=False
        with self.assertRaises(PermissionError):self.e.frame('x',self.slots)
    def test_unsupported_conjugation(self):
        self.slots[1]['sense']=sense_id('sleep',0);self.e.frame('u',self.slots)
        self.assertEqual(self.e.render('u')['decision'],'ABSTAIN')
    def test_irregular_has(self):
        self.slots[1]['sense']=sense_id('have',0);self.e.frame('h',self.slots)
        self.assertEqual(self.e.render('h')['sentence'],'Some poodle has some parcel.')
    def test_bad_archive(self):
        p=Path(self.tmp.name)/'bad.zip';p.write_bytes(b'bad')
        with self.assertRaises(ValueError):lexicon_from_zip(p)
