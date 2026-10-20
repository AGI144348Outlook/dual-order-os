import unittest
from types import SimpleNamespace
from .runtime import GrammarGuide,RecursiveSentencePipeline
from .legacy import MirrorStep
class Syn:
 def __init__(self,w,parent=None):self.w=w;self.parent=parent
 def lemma_names(self):return [self.w]
 def definition(self):return 'definition of '+self.w+' with complete contextual detail'
 def name(self):return self.w+'.n.01'
 def hypernym_paths(self):return [[self.parent,self]] if self.parent else [[self]]
class Provider:
 def synsets(self,w,pos='n'):
  return [Syn('heron',Syn('bird'))] if w=='heron' else []
class Tests(unittest.TestCase):
 def setUp(self):self.g=GrammarGuide(Provider())
 def test_direction(self):s=self.g.speak_chain('heron');self.assertIn('Heron is a kind of bird.',s);self.assertNotIn('Bird is a kind of heron.',s)
 def test_ambiguity(self):
  provider=type('Ambiguous',(),{'synsets':lambda self,w,pos='n':[Syn('heron'),Syn('hero')]})()
  self.assertEqual(GrammarGuide(provider).speak_chain('heron'),[])
 def test_explicit_sense(self):
  provider=type('Ambiguous',(),{'synsets':lambda self,w,pos='n':[Syn('heron'),Syn('hero')]})()
  self.assertTrue(GrammarGuide(provider,sense='heron.n.01').speak_chain('heron'))
 def test_unknown(self):self.assertEqual(self.g.speak_chain('unseen'),[])
 def test_depth(self):self.assertEqual(len(self.g.speak_chain('heron',1)),1)
 def test_invalid_depth(self):
  with self.assertRaises(ValueError):self.g.speak_chain('heron',0)
 def mirror(self):
  comm=SimpleNamespace(_ayin_classify=lambda w:'GAP');inward=SimpleNamespace(search=lambda w:SimpleNamespace(found=False));lobby=SimpleNamespace(agents={})
  return MirrorStep(comm,inward,{},lobby,{},self.g)
 def test_existing_mirror(self):
  m=self.mirror();r=m.reflect(['Heron is a bird.'],'heron');self.assertIn('heron',r['new_homework']);self.assertIn('bird',r['new_homework'])
 def test_recursive_integration(self):
  r=RecursiveSentencePipeline(self.g,self.mirror()).run('heron',2);self.assertEqual(r['status'],'stable');self.assertEqual(len(r['rounds']),1)
 def test_budget(self):
  with self.assertRaises(ValueError):RecursiveSentencePipeline(self.g,self.mirror()).run('heron',100)
 def test_unresolved_pipeline(self):self.assertEqual(RecursiveSentencePipeline(self.g,self.mirror()).run('unseen')['status'],'unresolved')
if __name__=='__main__':unittest.main()
