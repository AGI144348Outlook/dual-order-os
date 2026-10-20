import sys,json,re,hashlib,copy
from pathlib import Path
src=Path('/tmp/echo-genesis-exact/src/echo_governor_skeleton.py');b=src.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='63eb982989b4f3478d649430b555c8f4ba755c27'
sys.path.insert(0,str(src.parent));import echo_governor_skeleton as e
saved=json.load(open('/tmp/echo-genesis-exact/matrices/echo_lobby_agents.json'))
pairs=[('ר','resh'),('צ','tsadi'),('פ','pe'),('ע','ayin'),('ק','qof'),('ש','shin'),('ת','tav')]
def make(mode):
 m=e.AlgorithmMatrix();l=e.Lobby(m);added=[]
 for w,r in saved.items():
  a=e.WordAgent(w,r.get('definition','').split(),r.get('entry_class',''),r.get('department',''),m,raw_definition=r.get('definition',''));a.confirm_identity();a.generality_score=r.get('generality_score',0);l.agents[w]=a
 for glyph,name in pairs:
  if name not in l.agents:
   text=e.HEBREW_LETTER_INDEX[name]['lhea'];a=e.WordAgent(name,re.findall('[a-z]+',text.lower()),'ABSTRACT','letter',m,raw_definition=text);a.confirm_identity();l.agents[name]=a;added.append(name)
 if mode!='baseline':
  text={'literal':'paperclipping','explained':'paperclipping attach index card module','control':'zzqvcontrol'}[mode]
  a=l.agents['tsadi'];a.definition_words=text.split();a.raw_definition=text
 l.run_orientation();l.run_typed_study_groups()
 comm=e.AlgorithmicCommunicator(lobby=l,vgm=json.load(open('/tmp/echo-genesis-exact/matrices/echo_vgm.json')))
 return l,comm,added
out={'method':'Controlled temporary re-profiling, not autonomous learning. Original 1861 definitions reconstructed; missing four letter-name agents supplied from existing static profiles. Three treatments replace tsadi definition only; other definitions remain fixed. No new glyph interpreter, actions, registry persistence, or external model.','arms':{}}
for mode in ['baseline','literal','explained','control']:
 l,c,added=make(mode)
 overlap={name:l.cross_communicate('tsadi',name)['shared_vocabulary'] for _,name in pairs if name!='tsadi'}
 candidates=[]
 for word,a in l.agents.items():
  if word=='tsadi':continue
  shared=sorted(set(a.definition_words)&set(l.agents['tsadi'].definition_words))
  if shared:candidates.append({'word':word,'shared':shared})
 candidates.sort(key=lambda r:(-len(r['shared']),r['word']))
 out['arms'][mode]={'added_profile_agents':added,'tsadi_definition':l.agents['tsadi'].raw_definition,'tsadi_ties':sorted(l.agents['tsadi'].ties),'pairwise_shared_vocabulary':overlap,'overlap_candidates':candidates[:12],'definitions':{name:l.agents[name].raw_definition for _,name in pairs},'neighbors':{name:sorted(l.agents[name].ties) for _,name in pairs},'direct_classifications':{name:c._ayin_classify(name) for _,name in pairs},'tsadi_communication':c.communicate('tsadi'),'raw_glyph_communication':c.communicate('ר צ פ ע ק ש ת')}
base=out['arms']['baseline'];out['changes']={}
for mode in ['literal','explained','control']:
 arm=out['arms'][mode];out['changes'][mode]={name:{'definition_changed':arm['definitions'][name]!=base['definitions'][name],'added_neighbors':sorted(set(arm['neighbors'][name])-set(base['neighbors'][name])),'removed_neighbors':sorted(set(base['neighbors'][name])-set(arm['neighbors'][name]))} for _,name in pairs if name!='tsadi'}
 assert all(not r['definition_changed'] for r in out['changes'][mode].values())
Path('/tmp/echo-paperclip/results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for mode,arm in out['arms'].items():print(mode,json.dumps({k:arm[k] for k in ['tsadi_ties','pairwise_shared_vocabulary','overlap_candidates']},ensure_ascii=False))
print('changes',json.dumps(out['changes'],ensure_ascii=False))
