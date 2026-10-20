"""Integration over source-extracted grammar and mirror definitions."""
from .legacy import HypernymGrammarModule,MirrorStep,PeComposer,article
class GrammarGuide(HypernymGrammarModule):
 """Migration adapter: provider injection and corrected taxonomy direction.
 Keeps inherited get_chain data shape; legacy behavior remains in legacy.py.
 """
 def __init__(self,provider,lobby=None,lexicon=None,sense=None):
  super().__init__(lobby,lexicon);self.provider=provider;self.selected_sense=sense
 def get_chain(self,word,pos='n'):
  key=(word,pos,self.selected_sense)
  if key in self._chain_cache:return self._chain_cache[key]
  synsets=self.provider.synsets(word,pos=pos)
  if self.selected_sense:synsets=[s for s in synsets if s.name()==self.selected_sense]
  if len(synsets)!=1:return []
  paths=synsets[0].hypernym_paths()
  chain=[{'word':s.lemma_names()[0].replace('_',' ').lower(),'definition':s.definition(),'synset':s.name()} for s in paths[0]] if paths else []
  self._chain_cache[key]=chain;return chain
 def speak_chain(self,word,depth=4):
  if not isinstance(depth,int) or depth<1:raise ValueError('depth must be a positive integer')
  chain=self.get_chain(word)
  if not chain:return []
  tail=chain[-depth:];sentences=[]
  for node in reversed(tail):
   # Preserve complete definition; avoid source's arbitrary 70-character truncation.
   sentences.append(f"{node['word'].capitalize()} means: {node['definition'].rstrip('.')}.")
  for parent,child in reversed(list(zip(tail,tail[1:]))):
   sentences.append(f"{child['word'].capitalize()} is a kind of {parent['word']}.")
  return sentences
class RecursiveSentencePipeline:
 """Grammar expression -> existing MirrorStep reflection, bounded return.
 Does not equate mirror familiarity checks with grammatical or factual proof.
 """
 def __init__(self,grammar,mirror):self.grammar=grammar;self.mirror=mirror
 def run(self,word,max_rounds=2,depth=4):
  if not isinstance(max_rounds,int) or not 1<=max_rounds<=10:raise ValueError('round budget must be 1..10')
  rounds=[];seen=set()
  for i in range(max_rounds):
   sentences=self.grammar.speak_chain(word,depth=depth)
   if not sentences:return {'status':'unresolved','rounds':rounds,'sentences':[]}
   signature=tuple(sentences)
   if signature in seen:return {'status':'stable','rounds':rounds,'sentences':sentences}
   seen.add(signature);reflection=self.mirror.reflect(sentences,word)
   rounds.append({'round':i+1,'sentences':sentences,'reflection':reflection})
  return {'status':'budget_reached','rounds':rounds,'sentences':rounds[-1]['sentences']}
