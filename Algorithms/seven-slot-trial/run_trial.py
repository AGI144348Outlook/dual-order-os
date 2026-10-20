"""Bounded autonomous selection among supplied context operations.
Glyph labels have no predefined semantics; task generator and operations are supplied.
"""
import sys,json,itertools,random
from pathlib import Path
sys.path.insert(0,'Algorithms/training')
from engine import AlgorithmMatrix
GLYPHS=['ע','פ','צ','ק','ר','ש','ת']
# Available reusable operations. Each is a real filter over evidence records.
OPS={
 'subject_match':lambda r,q:r['subject']==q['subject'],
 'relation_match':lambda r,q:r['relation']==q['relation'],
 'context_match':lambda r,q:r['context']==q['context'],
 'condition_match':lambda r,q:r['condition']==q['condition'],
 'evidence_check':lambda r,q:bool(r['evidence']),
 'polarity_match':lambda r,q:r['polarity']==q['polarity'],
 'time_match':lambda r,q:r['time']==q['time'],
 'object_nonempty':lambda r,q:bool(r['object']),
 'id_present':lambda r,q:bool(r['id']),
 'record_is_dict':lambda r,q:isinstance(r,dict),
}
def dataset(prefix,count):
 cases=[]
 for i in range(count):
  q={'subject':prefix+' subject '+str(i),'relation':['is_a','part_of','located_in','made_of','has_property','used_for','can_be_used_for'][i%7],'context':prefix+' context','condition':'condition '+str(i%3),'polarity':True,'time':i}
  good={**q,'id':prefix+str(i)+'-good','object':prefix+' object '+str(i),'evidence':'fixture assertion '+str(i)}
  rows=[good]
  for field in ['subject','relation','context','condition','polarity','time','evidence']:
   wrong=dict(good);wrong['id']=prefix+str(i)+'-wrong-'+field
   wrong[field]=False if field=='polarity' else '' if field=='evidence' else -1 if field=='time' else 'different-'+field
   rows.append(wrong)
  random.Random(i).shuffle(rows);cases.append({'query':q,'records':rows,'expected':[good['id']]})
 return cases

def resolve(mapping,case):
 rows=case['records']
 for glyph in GLYPHS:
  operation=mapping.get(glyph)
  if operation is not None:rows=[r for r in rows if OPS[operation](r,case['query'])]
 return sorted(r['id'] for r in rows)
def score(mapping,cases):return sum(resolve(mapping,c)==c['expected'] for c in cases)/len(cases)
def run():
 train=dataset('train',28);test=dataset('unseen',21)
 # Each candidate proposes seven distinct functions; glyph placement is arbitrary.
 names=list(OPS);candidates={}
 for i,combo in enumerate(itertools.combinations(names,7)):
  shuffled=list(combo);random.Random(i+19).shuffle(shuffled);candidates['candidate-'+str(i)]=dict(zip(GLYPHS,shuffled))
 arms=list(reversed(candidates));m=AlgorithmMatrix();trace=[]
 for step in range(600):
  arm=m.bandit_select('context_assembly',arms);quality=score(candidates[arm],train)
  # Existing Echo monitor/anchor stores success against explicit task correctness.
  for c in train:m.record_outcome(arm,'context_assembly',resolve(candidates[arm],c)==c['expected'])
  decision=m.checkpoint_generation();trace.append({'step':step,'candidate':arm,'training_accuracy':quality,'anchor':decision['decision']})
 evaluated={arm:(s/n if n else 0) for (arm,bucket),(s,n) in m.history.items()};best=max(evaluated,key=lambda a:(evaluated[a],a));mapping=candidates[best]
 baseline=dict(zip(GLYPHS,['object_nonempty','id_present','record_is_dict','subject_match','relation_match','context_match','evidence_check']))
 shuffled=dict(zip(GLYPHS,reversed(list(mapping.values()))))
 tests={
 'seven_identities_preserved':list(mapping)==GLYPHS,
 'trained_context_exact_on_holdout':score(mapping,test)==1,
 'untrained_context_worse':score(mapping,test)>score(baseline,test),
 'no_slot_context_worse':score(mapping,test)>score({},test),
 'renaming_slot_assignments_keeps_score':score(shuffled,test)==score(mapping,test),
 'source_records_preserved':all(len(c['records'])==8 for c in test),
 }
 # Ablate each selected operation independently to see whether the curriculum needs it.
 ablations={g:score({k:v for k,v in mapping.items() if k!=g},test) for g in GLYPHS}
 tests['each_selected_function_needed_in_fixture']=all(v<1 for v in ablations.values())
 # Unknown operation rejected; no silently invented implementation.
 try:resolve({'ע':'invented'},test[0]);tests['unknown_operation_rejected']=False
 except KeyError:tests['unknown_operation_rejected']=True
 report={'training_cases':len(train),'heldout_cases':len(test),'candidate_configurations':len(candidates),'selection_trials':len(trace),'feedback_observations':len(trace)*len(train),'candidate_slot_assignment':mapping,'trained_exact_accuracy':score(mapping,test),'untrained_exact_accuracy':score(baseline,test),'no_slots_exact_accuracy':score({},test),'ablations':ablations,'checks':tests,'history':[{'candidate':a,'bucket':b,'successes':s,'attempts':n} for (a,b),(s,n) in m.history.items()],'limits':['Synthetic closed curriculum constructed to need seven filtering dimensions.','Operations supplied by developer; Echo selected combinations, did not invent them.','Holdout changes entities/contexts, not schema or relation language.','Filters commute; data cannot identify unique glyph meanings or optimal ordering.','No invariant slot semantics promoted; no native glyph execution or free-language understanding established.']}
 out=Path('Algorithms/seven-slot-trial');(out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(out/'training-trace.json').write_text(json.dumps(trace,indent=2));(out/'heldout.json').write_text(json.dumps(test,indent=2))
 print(json.dumps({k:report[k] for k in ['candidate_configurations','selection_trials','candidate_slot_assignment','trained_exact_accuracy','untrained_exact_accuracy','no_slots_exact_accuracy','checks','limits']},ensure_ascii=False,indent=2));assert all(tests.values())
if __name__=='__main__':run()
