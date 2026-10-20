"""Supervised relation-operation routing using Echo's existing UCB/anchor methods.
Closed synthetic curriculum: not unrestricted language understanding.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,'Algorithms/training')
from engine import AlgorithmMatrix
# cue, relation, sentence frame. Frames are supplied, not learned.
CONTRACTS=[('classify','is_a','{s} is a kind of {o}.'),('component membership','part_of','{s} is part of {o}.'),('list components','has_part','{s} has {o} as a part.'),('material composition','made_of','{s} is made of {o}.'),('attribute lookup','has_property','{s} has the property {o}.'),('actor action','performs','{s} performs {o}.'),('state change','undergoes','{s} undergoes {o}.'),('established purpose','used_for','{s} is used for {o}.'),('possible application','can_be_used_for','{s} can be used for {o}.'),('find position','located_in','{s} is located in {o}.'),('causal consequence','causes','{s} causes {o}.'),('prerequisite support','enables','{s} enables {o}.'),('earlier event','before','{s} occurs before {o}.'),('later event','after','{s} occurs after {o}.'),('same under criterion','equivalent','{s} is equivalent to {o}.'),('contrast under criterion','opposite','{s} contrasts with {o}.')]
ARMS=[r for _,r,_ in CONTRACTS];FRAMES={r:f for _,r,f in CONTRACTS};CUES={c:r for c,r,_ in CONTRACTS}
def choose(matrix,cue):
 if cue not in CUES:return None
 stats=[(matrix.history.get((r,cue),(0,0)),r) for r in ARMS]
 observed=[(s/n,r) for (s,n),r in stats if n]
 return max(observed)[1] if observed else ARMS[0]
def articulate(relation,subject,obj,evidence=None,condition=None,criterion=None):
 if relation not in FRAMES:return {'status':'unsupported','sentence':None}
 if not evidence:return {'status':'unresolved','sentence':None,'reason':'missing evidence'}
 if relation in {'causes','enables','can_be_used_for'} and not condition:return {'status':'unresolved','sentence':None,'reason':'conditions required'}
 if relation in {'equivalent','opposite'} and not criterion:return {'status':'unresolved','sentence':None,'reason':'criterion required'}
 text=FRAMES[relation].format(s=subject,o=obj)
 if condition:text=text[:-1]+' under the condition: '+condition+'.'
 if criterion:text=text[:-1]+' with respect to '+criterion+'.'
 return {'status':'expressed','sentence':text,'relation':relation,'evidence':evidence,'condition':condition,'criterion':criterion}
def inverse(relation):return {'part_of':'has_part','has_part':'part_of','before':'after','after':'before'}.get(relation)
def train():
 m=AlgorithmMatrix();before={c:choose(m,c) for c in CUES};corrections=[];epochs=[]
 for epoch in range(120):
  for cue,target in CUES.items():
   selected=m.bandit_select(cue,ARMS);ok=selected==target;m.record_outcome(selected,cue,ok)
   if not ok:corrections.append({'epoch':epoch,'task':cue,'selected':selected,'expected':target,'correction':'external curriculum label'})
  epochs.append(m.checkpoint_generation())
 after={c:choose(m,c) for c in CUES}
 # New subjects/objects; same task cues. Does not test novel paraphrases.
 evaluation=[]
 for i,(cue,target,_) in enumerate(CONTRACTS):
  actual=choose(m,cue);r=articulate(actual,'Held-out subject '+str(i),'held-out object '+str(i),['synthetic-test-fact-'+str(i)],condition='supplied fixture conditions',criterion='supplied fixture criterion')
  evaluation.append({'cue':cue,'expected':target,'selected':actual,'correct':actual==target,'output':r})
 checkpoint={'history':[{'relation':r,'task':c,'successes':s,'attempts':n} for (r,c),(s,n) in m.history.items()]}
 out=Path('Algorithms/relation-training');(out/'learned-routing.json').write_text(json.dumps(checkpoint,indent=2))
 report={'training_trials':120*len(CUES),'initial_correct':sum(before[c]==r for c,r in CUES.items()),'final_correct':sum(after[c]==r for c,r in CUES.items()),'tasks':len(CUES),'corrections':len(corrections),'evaluation':evaluation,'anchoring':epochs,'limits':'learned selection among 16 supplied relation operations for familiar task cues; new test entities only; manually supplied grammar frames and facts; not novel phrase interpretation, autonomous discovery or demonstrated full understanding'}
 (out/'corrections.json').write_text(json.dumps(corrections,indent=2));(out/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['training_trials','initial_correct','final_correct','tasks','corrections','limits']},indent=2))
if __name__=='__main__':train()
