import hashlib
import unittest
from tools.read_consent_paradox import checked_text,reading,BLOB
class Tests(unittest.TestCase):
 def test_source_copy_identity(self):
  b=checked_text().encode();self.assertEqual(len(b),5039);self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),BLOB)
 def test_repetition_is_not_new_word_identity(self):
  r=reading({'person':{'desc':'a human entity','pos':'noun'}},passes=3)
  self.assertEqual(len(r['passes']),3)
  self.assertTrue(all(s['known_source_tokens']==r['baseline']['known_source_tokens'] for s in r['passes']))
  self.assertEqual([s['source_token_document_counts']['consent'] for s in r['passes']],[1,2,3])
  self.assertTrue(all(not s['new_word_agents'] for s in r['passes']))
  self.assertTrue(all(s['vgm_statements_supplied']==0 for s in r['passes']))
 def test_budget(self):
  for budget in [0,6,True]:
   with self.assertRaises(ValueError):reading({},passes=budget)
