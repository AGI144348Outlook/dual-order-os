import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from libraries.echo_workspace import EchoWorkspace


class LanguageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.w=EchoWorkspace(Path(self.tmp.name)/'language.sqlite',capabilities=EchoWorkspace.ALL_CAPABILITIES)
        for word in ('dog','mammal','animal','cat','hour','unit'):
            self.w.put_word(word,word,'a kind of entity',department='noun')
        self.w.assert_is_a('r:dog-mammal','dog','mammal')
        self.w.assert_is_a('r:mammal-animal','mammal','animal')

    def tearDown(self):
        self.w.close();self.tmp.cleanup()

    def q(self,text,**kwargs):
        return self.w.query({'operation':'language','text':text,**kwargs})

    def test_transitive_path_has_evidence_and_roundtrip(self):
        r=self.q('dog is_a animal')
        self.assertEqual(r['english'],'A dog is an animal.')
        self.assertEqual(r['evidence'],['r:dog-mammal','r:mammal-animal'])
        self.assertEqual(r['grammar']['status'],'PASS')

    def test_negation_of_supported_relation_withheld(self):
        r=self.q('not dog is_a animal')
        self.assertEqual(r['semantic'],'CONTRADICTED');self.assertIsNone(r['english'])

    def test_unproved_relation_and_its_negation_stay_unknown(self):
        for text in ('dog is_a cat','not dog is_a cat'):
            r=self.q(text);self.assertEqual(r['semantic'],'UNKNOWN')
            self.assertEqual(r['decision'],'WITHHOLD')

    def test_contradictory_join_does_not_become_asserted_sentence(self):
        r=self.q('dog is_a animal and not dog is_a animal')
        self.assertEqual(r['decision'],'WITHHOLD');self.assertIsNone(r['english'])

    def test_inverse_relation(self):
        self.assertEqual(self.q('animal includes dog')['semantic'],'SUPPORTED')
        self.assertEqual(self.q('dog includes animal')['semantic'],'UNKNOWN')

    def test_unknown_word_is_not_adopted_from_ambient_wordnet(self):
        r=self.q('dog is_a unicorn')
        self.assertEqual(r['lexical']['status'],'FLAG')
        self.assertEqual(r['decision'],'WITHHOLD')

    def test_bounded_english_input_and_malformed_input(self):
        r=self.q('A dog is an animal.',surface='english')
        self.assertEqual(r['semantic'],'SUPPORTED')
        for text in ('A dog are an animal.','A dog is an animal',''):
            if not text:
                with self.assertRaises(ValueError):self.q(text,surface='english')
            else:self.assertEqual(self.q(text,surface='english')['decision'],'ABSTAIN')

    def test_operator_parse_does_not_execute(self):
        r=self.q('%(dog)')
        self.assertFalse(r['execution'])
        self.assertEqual(r['semantic'],'NOT_A_CLAIM')
        self.assertEqual(r['decision'],'WITHHOLD')

    def test_arity_audit(self):
        r=self.q('GENERALIZE(dog)')
        self.assertEqual(r['type']['status'],'FAIL')

    def test_result_record_property_truth(self):
        records={'C-05':{'verdict':'VALID'}}
        self.assertEqual(self.q('C-05.verdict = VALID',records=records)['semantic'],'SUPPORTED')
        self.assertEqual(self.q('C-05.verdict = VALID',records=records)['decision'],'ARTICULATE')
        self.assertEqual(self.q('C-05.verdict = INVALID',records=records)['semantic'],'CONTRADICTED')

    def test_cycle_terminates(self):
        self.w.assert_is_a('cycle','animal','dog')
        self.assertEqual(self.q('dog is_a cat')['semantic'],'UNKNOWN')

    def test_renamed_endpoint_does_not_retarget_old_assertion(self):
        self.w.put_word('dog','hound','a kind of entity',department='noun',expected_revision=1)
        self.assertEqual(self.q('hound is_a mammal')['semantic'],'UNKNOWN')

    def test_paperclip_is_not_subtype_evidence(self):
        self.w.paperclip('clip','dog','cat')
        self.assertEqual(self.q('dog is_a cat')['semantic'],'UNKNOWN')

    def test_source_role_realizer_preserves_roles_and_reversal(self):
        def render(edges):
            return self.w.query({'operation':'articulate','nodes':['dog','chase','cat'],'edges':edges})
        self.assertEqual(render([['dog','agent_of','chase'],['cat','patient_of','chase']])['sentence'],'A dog chases a cat.')
        self.assertEqual(render([['cat','agent_of','chase'],['dog','patient_of','chase']])['sentence'],'A cat chases a dog.')

    def test_incomplete_or_ambiguous_roles_abstain(self):
        for edges in ([],[['dog','agent_of','chase']],
                      [['dog','agent_of','chase'],['cat','agent_of','chase'],['cat','patient_of','chase']]):
            r=self.w.query({'operation':'articulate','nodes':['dog','chase','cat'],'edges':edges})
            self.assertEqual(r['decision'],'ABSTAIN')

    def test_role_generator_rejects_unregistered_nodes(self):
        r=self.w.query({'operation':'articulate','nodes':['dog','chase','cat'],
                        'edges':[['wolf','agent_of','chase'],['cat','patient_of','chase']]})
        self.assertEqual(r['decision'],'ABSTAIN')


if __name__=='__main__':unittest.main()
