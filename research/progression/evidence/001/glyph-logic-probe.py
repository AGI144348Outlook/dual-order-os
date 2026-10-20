import sys,json,hashlib
from pathlib import Path
src=Path('/tmp/echo-genesis-exact/src/echo_governor_skeleton.py'); b=src.read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='63eb982989b4f3478d649430b555c8f4ba755c27'
sys.path.insert(0,str(src.parent))
import echo_governor_skeleton as e
out={'source_blob':'63eb982989b4f3478d649430b555c8f4ba755c27','scope':'unchanged Genesis, isolated memory only; controlled fixtures are not approved axioms','raw_glyph_generation':[]}
for text in ['א','ארת','עפ','פע','|{•}{•}|']:
 m=e.AlgorithmMatrix();a=e.InformationAlgorithmizer(alg_matrix=m)
 ids=a.algorithmize(text)
 out['raw_glyph_generation'].append({'input':text,'tokenized':e.AlgorithmicCommunicator()._tokenize(text),'generated':len(a.generated),'operations':[x.operation_type for x in a.generated],'classified':a.generated[0].execute(d={}) if a.generated else None,'registered':len(ids)})
records=[{'glyph':'א','operation':'INITIALIZE'},{'glyph':'ר','operation':'GOVERN'},{'glyph':'ת','operation':'SEAL'}]
m=e.AlgorithmMatrix();a=e.InformationAlgorithmizer(alg_matrix=m);ids=a.algorithmize(records[0],info_type='STRUCTURED_DATA')
q=next(x for x in a.generated if x.operation_type=='QUERY')
actual=q.execute(dataset=records,field='glyph',value='ר');assert actual==[records[1]]
out['glyph_record_tools']={'generated':len(a.generated),'registered':len(ids),'query_result':actual,'classification':a.generated[0].execute(d=records[0]),'infer':a.generated[1].execute(d=records[0])}
axiom={'id':'TEST-ONLY','text':'entity passes threshold','words':['entity','threshold']}
a2=e.InformationAlgorithmizer(alg_matrix=e.AlgorithmMatrix());a2.algorithmize(axiom)
d=next(x for x in a2.generated if x.operation_type=='DERIVE');text=d.execute(entity='ד');assert text=='[DERIVED from TEST-ONLY] ד passes threshold'
out['glyph_substitution']={'result':text,'registered':len(a2.registered),'expected_checks':[c.get('expected') for x in a2.generated for c in x.test_cases],'note':'Threshold meaning supplied by test author, not discovered from glyph.'}
search=e.InwardSearchEngine();out['letter_lookup']={s:{'found':search.search(s).found,'letter':search.search(s).letter} for s in ['א','aleph','ר','resh']}
# Adversarial inputs are untrusted fixtures, not additions to the real VGM.
vgm={'X':{'text':'entity is connected','words':['entity','connected']},'Y':{'text':'entity is not connected','words':['entity','connected']}}
lrm=e.LogicReasoningMatrix(vgm,e.Lobby(e.AlgorithmMatrix()));r=lrm.derive_compose('X','Y')
out['contradiction_challenge']={'candidate':r,'accepted_as_theorem':r is not None}
vgm2={'X':{'text':'ד opens','words':['ד','opens']},'Y':{'text':'ד closes','words':['ד','closes']}}
out['single_glyph_pivot']=e.LogicReasoningMatrix(vgm2,e.Lobby(e.AlgorithmMatrix())).derive_compose('X','Y')
vgm3={'X':{'text':'ד opens','words':['ד','opens'],'structure':['verb']},'Y':{'text':'א vanishes','words':['א','vanishes']}}
out['unrelated_causal_challenge']=e.LogicReasoningMatrix(vgm3,e.Lobby(e.AlgorithmMatrix())).derive_causal('X','Y')
Path('/tmp/echo-glyph-logic/results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
