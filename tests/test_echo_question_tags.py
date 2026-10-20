import unittest
from libraries.echo_question_tags import candidate_tags,definition_hints,save_tags,tags_current,answer_role
from libraries.echo_sentence_cards import SentenceCards,sense_id
class Tests(unittest.TestCase):
    def sense(self,word='morning',pos='noun',definition='the early part of a day'):
        return {'kind':'lexical-sense','word':word,'pos':pos,'definition':definition}
    def fact(self,**kw):return dict(id='f1',event='e1',role='agent',value='Julian',polarity='positive',category='person',**kw)
    def test_temporal_multirole(self):
        t=candidate_tags(self.sense(),[{'category':'time-interval','source':'lesson:1'}])
        self.assertEqual(t['possible_questions'],['what','when'])
    def test_no_adverb_manner_assumption(self):
        self.assertEqual(candidate_tags(self.sense('tomorrow','adv'))['possible_questions'],[])
    def test_no_every_noun_is_person(self):self.assertEqual(candidate_tags(self.sense('box'))['possible_questions'],['what'])
    def test_category_needs_provenance(self):
        with self.assertRaises(ValueError):candidate_tags(self.sense(),[{'category':'person'}])
    def test_definition_hint_is_candidate(self):
        h=definition_hints(self.sense('clock',definition='an object measuring time'))
        self.assertEqual(h[0]['status'],'definition-keyword-candidate-not-proof')
        self.assertNotIn('when',candidate_tags(self.sense('clock'))['possible_questions'])
    def test_tag_history_pins_source(self):
        e=SentenceCards();e.ingest({'morning':{'senses':[{'pos':'noun','def':'part of a day'}]}},source={})
        cid=sense_id('morning',0);tag=save_tags(e.box,cid);self.assertTrue(tags_current(e.box,tag))
        n=len(e.box.events());save_tags(e.box,cid);self.assertEqual(len(e.box.events()),n)
        c=e.box.get('cards',cid);e.box.put_card(cid,c['title'],dict(c['body'],definition='revised'),expected_revision=1)
        self.assertFalse(tags_current(e.box,tag));new=save_tags(e.box,cid);self.assertEqual(new['revision'],2);e.close()
    def test_who_from_fact(self):
        r=answer_role([self.fact()],event='e1',role='agent',question='who')
        self.assertEqual(r['answers'],['Julian']);self.assertEqual(r['evidence'],['f1'])
    def test_other_event_does_not_leak(self):self.assertEqual(answer_role([self.fact()],event='e2',role='agent',question='who')['decision'],'UNKNOWN')
    def test_missing_owner_unknown(self):self.assertEqual(answer_role([self.fact()],event='e1',role='owner',question='whose')['decision'],'UNKNOWN')
    def test_negative_not_answer(self):
        f=self.fact();f['polarity']='negative'
        self.assertEqual(answer_role([f],event='e1',role='agent',question='who')['decision'],'UNKNOWN')
    def test_contradiction_withheld(self):
        a=self.fact();b=dict(a,id='f2',polarity='negative')
        self.assertEqual(answer_role([a,b],event='e1',role='agent',question='who')['decision'],'WITHHOLD')
    def test_who_requires_person(self):
        a=self.fact();a['category']='object'
        self.assertEqual(answer_role([a],event='e1',role='agent',question='who')['decision'],'WITHHOLD')
    def test_patient_is_not_agent(self):
        a=self.fact();a['role']='patient'
        self.assertEqual(answer_role([a],event='e1',role='agent',question='who')['decision'],'UNKNOWN')
    def test_why_does_not_invent_cause(self):self.assertEqual(answer_role([self.fact()],event='e1',role='cause',question='why')['decision'],'UNKNOWN')
    def test_which_needs_alternatives(self):self.assertEqual(answer_role([self.fact()],event='e1',role='agent',question='which')['decision'],'ABSTAIN')
    def test_transfer_names(self):
        for name in ['Nexus','a newly named learner']:
            a=self.fact();a['value']=name
            self.assertEqual(answer_role([a],event='e1',role='agent',question='who')['answers'],[name])
    def test_malformed_fact_abstains(self):
        a=self.fact();a.pop('id')
        self.assertEqual(answer_role([a],event='e1',role='agent',question='who')['decision'],'ABSTAIN')
