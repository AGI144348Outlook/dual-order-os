"""Independent challenge cases for the new bounded branch-derived interfaces."""
import json
import sys
import tempfile
import time
import tracemalloc
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from libraries.echo_workspace import EchoWorkspace


def run():
    rows=[]
    def check(group,name,expected,fn):
        try:
            observed=fn();record={'observed':observed};status='PASS' if observed==expected else 'FAIL'
        except Exception as exc:
            status='FAIL';record={'exception':type(exc).__name__,'detail':str(exc)}
        rows.append({'group':group,'name':name,'expected':expected,'status':status,**record})
    with tempfile.TemporaryDirectory() as tmp:
        with EchoWorkspace(Path(tmp)/'language.sqlite',capabilities=EchoWorkspace.ALL_CAPABILITIES) as w:
            for word in ('sparrow','bird','animal','stone'):
                w.put_word(word,word,'a kind of entity',department='noun')
            w.assert_is_a('r1','sparrow','bird');w.assert_is_a('r2','bird','animal')
            def q(text,**kw):return w.query({'operation':'language','text':text,**kw})
            check('typed_inference','held-out transitive conclusion','SUPPORTED',lambda:q('sparrow is_a animal')['semantic'])
            check('typed_inference','negation contradicted by explicit path','CONTRADICTED',lambda:q('not sparrow is_a animal')['semantic'])
            check('typed_inference','no path remains unknown','UNKNOWN',lambda:q('stone is_a animal')['semantic'])
            check('typed_inference','no path does not prove negative','UNKNOWN',lambda:q('not stone is_a animal')['semantic'])
            check('typed_inference','contradictory conjunction withheld','WITHHOLD',lambda:q('sparrow is_a animal and not sparrow is_a animal')['decision'])
            check('typed_inference','unsupported glyph operation is not executed',False,lambda:q('%(sparrow)')['execution'])
            check('grammar_roundtrip','English accepted in bounded grammar','SUPPORTED',lambda:q('A sparrow is an animal.',surface='english')['semantic'])
            check('grammar_roundtrip','wrong copula outside supported grammar','ABSTAIN',lambda:q('A sparrow are an animal.',surface='english')['decision'])
            check('grammar_roundtrip','render parses back','PASS',lambda:q('sparrow is_a animal')['grammar']['status'])
            check('provenance','transitive conclusion cites both edges',['r1','r2'],lambda:q('sparrow is_a animal')['evidence'])
            def articulate(agent,verb,patient,edges=None):
                return w.query({'operation':'articulate','nodes':[agent,verb,patient],
                                'edges':edges if edges is not None else [[agent,'agent_of',verb],[patient,'patient_of',verb]]})
            check('role_articulation','held-out transitive sentence','A fox chases a hen.',lambda:articulate('fox','chase','hen')['sentence'])
            check('role_articulation','role reversal preserved','A hen chases a fox.',lambda:articulate('hen','chase','fox')['sentence'])
            check('role_articulation','no role invention','ABSTAIN',lambda:articulate('fox','chase','hen',[])['decision'])
            check('role_articulation','missing patient abstains','ABSTAIN',lambda:articulate('fox','chase','hen',[['fox','agent_of','chase']])['decision'])
            check('role_articulation','ambiguous agent abstains','ABSTAIN',lambda:articulate('fox','chase','hen',[['fox','agent_of','chase'],['hen','agent_of','chase'],['hen','patient_of','chase']])['decision'])
            # Deliberate broader English challenges expose limitations of the recovered inflector.
            check('english_limits','mass noun determiner','A person drinks water.',lambda:articulate('person','drink','water')['sentence'])
            check('english_limits','irregular verb','A person has a book.',lambda:articulate('person','have','book')['sentence'])
            check('english_limits','phonetic article','An hour changes a plan.',lambda:articulate('hour','change','plan')['sentence'])
    measurements=[]
    for size in (10,100):
        with tempfile.TemporaryDirectory() as tmp:
            tracemalloc.start();start=time.perf_counter()
            with EchoWorkspace(Path(tmp)/'perf.sqlite',capabilities=EchoWorkspace.ALL_CAPABILITIES) as w:
                for i in range(size):w.put_word('w'+str(i),'term'+str(i),'a kind of entity',department='noun')
            elapsed=time.perf_counter()-start;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            measurements.append({'vocabulary_cards':size,'seconds':round(elapsed,4),'python_traced_peak_bytes':peak,
                                 'note':'Synthetic desktop/CI measurement, not Android or browser performance; no target budget defined.'})
    return {'battery':'branch-components-diagnostics/1','cases':rows,'summary':dict(Counter(r['status'] for r in rows)),
            'performance_smoke':measurements,'scope':'Small held-out synthetic cases relative to unit fixtures; all rules and lexical realization are authored, not learned. Not standardized benchmark scores.'}


if __name__=='__main__':
    target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'reports/echo-benchmarks/branch-components.json'
    r=run();target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'summary':r['summary'],'performance_smoke':r['performance_smoke']},indent=2))
