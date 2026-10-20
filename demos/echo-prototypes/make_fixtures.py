"""Expected results from original Python, kept separate from interactive runtime data."""
import json
import runpy
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from libraries.echo_question_tags import candidate_tags,definition_hints,answer_role
bridge=runpy.run_path(str(HERE/'python_bridge.py'));dispatch=bridge['dispatch']
rows=[]
for word,pos,definition,category in [('morning','noun','early part of day','time-interval'),('clock','noun','an object measuring time',''),('tomorrow','adv','on the next day',''),('teacher','noun','a person teaching','person'),('school','noun','a place of learning','place')]:
 s={'kind':'lexical-sense','word':word,'pos':pos,'definition':definition};cats=[{'category':category,'source':'fixture'}] if category else []
 r=candidate_tags(s,cats);rows.append({'word':word,'pos':pos,'definition':definition,'category':category,'expected':{'possible_questions':r['possible_questions'],'status':r['status'],'definition_hints':definition_hints(s)}})
facts=[{'id':'s1','event':'placement','role':'agent','value':'Julian','category':'person','polarity':'positive'},{'id':'s2','event':'placement','role':'patient','value':'card','category':'object','polarity':'positive'},{'id':'s3','event':'placement','role':'time','value':'morning','category':'time-interval','polarity':'positive'}]
answers=[]
for event,role,q in [('placement','agent','who'),('placement','patient','what'),('placement','time','when'),('placement','owner','whose'),('placement','cause','why'),('other','agent','who'),('placement','agent','which')]:
 answers.append({'facts':facts,'event':event,'role':role,'question':q,'expected':answer_role(facts,event=event,role=role,question=q)})
for condition in ['negative','contradictory','untyped']:
 fs=[dict(facts[0])]
 if condition=='negative':fs[0]['polarity']='negative'
 if condition=='contradictory':fs.append(dict(fs[0],id='n1',polarity='negative'))
 if condition=='untyped':fs[0].pop('category')
 answers.append({'facts':fs,'event':'placement','role':'agent','question':'who','expected':answer_role(fs,event='placement',role='agent',question='who')})
seq=[{'operation':'init','predicate':'carry'},{'operation':'transform','position':'s:0','target':'animal','mode':'generalize'},{'operation':'transform','position':'s:0','target':'poodle','mode':'specialize'},{'operation':'reorder','positions':['s:2','s:1','s:0']},{'operation':'reorder','positions':['s:0','s:1','s:2']},{'operation':'init','predicate':'have'},{'operation':'init','predicate':'sleep'}]
cards=[]
for command in seq:
 r=dispatch(command);cards.append({'command':command,'expected':{'revision':r['revision'],'slots':r['slots'],'output':{k:v for k,v in r['output'].items() if k!='scope'}}})
(HERE/'fixtures.json').write_text(json.dumps({'tags':rows,'answers':answers,'cards':cards},indent=2)+'\n')
print('Generated Python parity fixtures: 5 tag cases, 10 answer cases, 7 card states')
