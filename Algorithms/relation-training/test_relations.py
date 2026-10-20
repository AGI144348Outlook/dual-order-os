import unittest
from train_relations import articulate,inverse,CONTRACTS,choose,AlgorithmMatrix
class Tests(unittest.TestCase):
 def test_all_frames(self):
  for _,r,_ in CONTRACTS:self.assertEqual(articulate(r,'A','B',['fixture'],condition='C',criterion='D')['status'],'expressed')
 def test_no_evidence(self):self.assertEqual(articulate('is_a','A','B')['status'],'unresolved')
 def test_causal_conditions(self):self.assertEqual(articulate('causes','A','B',['x'])['status'],'unresolved')
 def test_comparison_scope(self):self.assertEqual(articulate('equivalent','A','B',['x'])['status'],'unresolved')
 def test_possible_not_actual(self):self.assertIn('can be used',articulate('can_be_used_for','A','B',['x'],condition='C')['sentence'])
 def test_no_cause_inverse(self):self.assertIsNone(inverse('causes'))
 def test_part_inverse(self):self.assertEqual(inverse('part_of'),'has_part')
 def test_unknown_task(self):self.assertIsNone(choose(AlgorithmMatrix(),'unseen task wording'))
 def test_collapse_guard(self):
  m=AlgorithmMatrix();m.history[('is_a','fixture')]=(10,10)
  for _ in range(3):m.record_outcome('is_a','fixture',False)
  r=m.checkpoint_generation();self.assertEqual(r['decision'],'DISCARDED');self.assertEqual(m.history[('is_a','fixture')],(10,10))
 def test_unknown_relation(self):self.assertEqual(articulate('invented','A','B',['x'])['status'],'unsupported')
if __name__=='__main__':unittest.main()
