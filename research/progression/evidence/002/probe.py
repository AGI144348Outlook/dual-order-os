import sys,json,hashlib
from pathlib import Path
src=Path('/tmp/echo-genesis-exact/src/echo_governor_skeleton.py');b=src.read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='63eb982989b4f3478d649430b555c8f4ba755c27'
sys.path.insert(0,str(src.parent))
import echo_governor_skeleton as e
pairs=[('ר','resh'),('צ','tsadi'),('פ','pe'),('ע','ayin'),('ק','qof'),('ש','shin'),('ת','tav')]
results=[]
for glyph,name in pairs:
 m=e.AlgorithmMatrix();a=e.InformationAlgorithmizer(alg_matrix=m)
 ids=a.algorithmize(glyph)
 row={'glyph':glyph,'name':name,'raw_tokens':e.AlgorithmicCommunicator()._tokenize(glyph),'direct_lookup_found':e.InwardSearchEngine().search(glyph).found,'name_lookup':e.InwardSearchEngine().search(name).letter,'raw_generated_types':[x.operation_type for x in a.generated],'raw_registered':len(ids),'raw_empty_record_classification':next(x for x in a.generated if x.operation_type=='CLASSIFY').execute(d={})}
 record={'glyph':glyph,'name':name}
 aa=e.InformationAlgorithmizer(alg_matrix=e.AlgorithmMatrix());aa.algorithmize(record)
 q=next(x for x in aa.generated if x.operation_type=='QUERY')
 row['record_query']=q.execute(dataset=[record,{'glyph':'?','name':'control'}],field='glyph',value=glyph)
 assert row['raw_tokens']==[]
 assert row['direct_lookup_found']==False
 assert row['name_lookup']['glyph']==glyph
 assert row['raw_generated_types']==['CLASSIFY','INFER','QUERY']
 assert row['raw_empty_record_classification']=='UNKNOWN_ENTITY'
 assert row['record_query']==[record]
 results.append(row)
out={'date':'2026-10-20','source_blob':'63eb982989b4f3478d649430b555c8f4ba755c27','method':'Fresh in-memory matrix per input. Metadata records have glyph/name only; no semantic meanings assigned. No persisted registrations, repository modifications, network calls or LLM use.','results':results}
Path('/tmp/echo-seven-glyphs/results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
