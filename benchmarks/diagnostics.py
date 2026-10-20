"""Transparent diagnostic battery, not a standardized IQ/LLM benchmark.

Golden grammar labels are supplied by the evaluator; original Echo receives POS pairs.
Failures are recorded, not concealed to obtain a green CI result.
"""
import json
import math
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from libraries.echo_workspace import EchoWorkspace, genesis


def run():
    e = genesis(); cases = []
    def check(group, name, expected, fn):
        start = time.perf_counter()
        try:
            observed = fn()
            status = 'PASS' if observed == expected else 'FAIL'
            record = {'expected': expected, 'observed': observed}
        except Exception as exc:
            status = 'FAIL'; record = {'expected': expected, 'exception': type(exc).__name__, 'detail': str(exc)}
        cases.append({'group': group, 'name': name, 'status': status,
                      'milliseconds': round((time.perf_counter()-start)*1000, 3), **record})
    def unsupported(group, name, why):
        cases.append({'group': group, 'name': name, 'status': 'UNSUPPORTED', 'reason': why})

    grammar = [
        ('complete subject verb object', [('entity','noun'),('changes','verb'),('state','noun')], True),
        ('complete intransitive', [('bird','noun'),('flies','verb')], True),
        ('reject bare noun', [('bird','noun')], False),
        ('reject verb noun ordering', [('flies','verb'),('bird','noun')], False),
        ('reject two nouns', [('bird','noun'),('sky','noun')], False),
        ('reject missing copula in ordinary English', [('bird','noun'),('blue','adjective')], False),
        ('reject singular subject plural verb', [('bird','noun'),('fly','verb')], False),
        ('reject plural subject singular verb', [('birds','noun'),('flies','verb')], False),
        ('accept plural agreement', [('birds','noun'),('fly','verb')], True),
        ('reject intransitive verb with arbitrary object', [('bird','noun'),('sleeps','verb'),('stone','noun')], False),
        ('reject unknown gibberish despite supplied POS', [('zzqv','noun'),('xxrr','verb')], False),
    ]
    for name, statement, expected in grammar:
        check('sentence_structure', name, expected, lambda s=statement: e.SyntacticalValidator().validate(s,{})['valid'])
    unsupported('sentence_structure','raw sentence POS parsing','SyntacticalValidator requires caller-supplied POS pairs; this is not a raw-language grammar parser.')
    unsupported('sentence_structure','Hebrew morphological agreement','No integrated Hebrew morphological grammar evaluator is exposed.')

    def lrm_pair(a,b,method,structure=None):
        vgm={'a':{'text':a,'words':a.lower().split(),'structure':structure or []},
             'b':{'text':b,'words':b.lower().split()}}
        lrm=e.LogicReasoningMatrix(vgm,e.Lobby(e.AlgorithmMatrix()))
        return getattr(lrm,method)('a','b')
    check('inference','reject explicit contradiction',True,
          lambda:lrm_pair('entity is connected','entity is not connected','derive_compose') is None)
    check('inference','reject unrelated causal conclusion',True,
          lambda:lrm_pair('bird flies','stone is heavy','derive_causal',['verb']) is None)
    check('inference','reject unrelated conditional implication',True,
          lambda:lrm_pair('bird flies','stone is heavy','derive_conditional') is None)
    check('inference','reject composition without shared pivot',True,
          lambda:lrm_pair('bird flies','stone is heavy','derive_compose') is None)
    check('inference','reject absent causal action',True,
          lambda:lrm_pair('stone is heavy','bird is blue','derive_causal') is None)
    check('inference','derive transitive subtype conclusion',True,
          lambda:'dogs are animals' in str(lrm_pair('dogs are mammals','mammals are animals','derive_compose')))
    unsupported('inference','formal modus ponens and quantifier reasoning','No typed predicate/rule proof API is integrated. String templates are not a substitute.')
    unsupported('inference','counterfactual causal intervention','No causal-model intervention API is integrated.')

    vgm={'a':{'text':'cat chases mouse','words':['cat','chases','mouse']},
         'b':{'text':'mouse avoids cat','words':['mouse','avoids','cat']}}
    matrix=e.AlgorithmMatrix(); lobby=e.Lobby(matrix)
    for word,definition,pos in [('cat','animal mouse','noun'),('mouse','animal cat','noun'),
                                ('chases','cat mouse','verb'),('avoids','mouse cat','verb')]:
        matrix.index_dictionary_entry(word,definition,pos)
    lobby.populate();lobby.run_orientation();lobby.run_typed_study_groups()
    c=e.AlgorithmicCommunicator(lobby=lobby,vgm=vgm)
    check('comprehension','retrieve indexed fact',True,lambda:'cat chases mouse' in c.communicate('cat'))
    check('comprehension','unknown-word gap disclosure',True,lambda:'GAP' in c.communicate('zzqvunknown'))
    check('comprehension','role-sensitive answer excludes unrelated inverse relation',True,
          lambda:'mouse avoids cat' not in c.communicate('Who chases mouse?'))
    check('comprehension','word queries avoid substring false match',[],
          lambda:e.VGMQuery({'x':{'text':'Contains parts','words':['parts']}}).query(['art']))
    check('comprehension','raw glyph preserved as indexable content',True,lambda:bool(c._tokenize('ר')))
    check('comprehension','two-letter word pe retained',True,lambda:'pe' in c._tokenize('pe'))
    unsupported('comprehension','pronoun reference resolution','No integrated coreference resolver.')
    unsupported('comprehension','paraphrase equivalence','No validated paraphrase equivalence mechanism; lexical overlap is weaker.')
    unsupported('comprehension','standardized broad benchmarks','MMLU, GLUE, bAbI and similar full datasets were not loaded; these scores cannot be compared to published model results.')

    E=e.AlgebraicExpression
    for op,a,b,expected in [('add',2,3,5),('sub',7,3,4),('mul',4,3,12),('div',8,2,4),('pow',2,3,8)]:
        check('mathematics',op,expected,lambda op=op,a=a,b=b:E(op,E.const(a),E.const(b)).evaluate())
    check('mathematics','polynomial substitution',16.0,
          lambda:E('add',E('pow',E.variable(e.Variable('x')),E.const(2)),E.const(7)).evaluate({'x':3}))
    check('mathematics','unary negation',-3.0,lambda:E('neg',E.const(3)).evaluate())
    def division_is_safe():
        try:
            return math.isfinite(E('div',E.const(3),E.const(0)).evaluate())
        except (ZeroDivisionError, ValueError):
            return True
    check('mathematics','reject nonfinite division result',True,division_is_safe)
    check('verification','reject untested generated operation',False,
          lambda:e.GeneratedAlgorithm('empty','test','fixture','TEST',lambda:1,[]).run_tests())
    check('verification','reject NaN generated operation',False,
          lambda:e.GeneratedAlgorithm('nan','test','fixture','TEST',lambda:float('nan'),[{'inputs':{},'expected':1.0}]).run_tests())
    check('verification','generic false invariant rejected',False,lambda:e.validate({},[lambda:False])[0])
    order=e.OperationOrderValidator()
    check('governance','orientation prerequisites rejected',False,lambda:order.check_prereqs('run_orientation')['ok'])
    order.mark_complete('index_dictionary_entry')
    check('governance','satisfied orientation prerequisites accepted',True,lambda:order.check_prereqs('run_orientation')['ok'])

    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'bench.sqlite'
        with EchoWorkspace(db,capabilities=EchoWorkspace.ALL_CAPABILITIES) as w:
            w.seed_profiles()
            w.put_word('w:clip','paperclip','attach card to index',department='verb')
            w.put_word('w:index','index','card collection',department='noun')
            check('integration','raw glyph catalog lookup','glyph:tsadi',lambda:w.query({'operation':'cards','glyph':'צ'})[0]['id'])
            check('integration','final form remains distinct','glyph:tsadi-sofit',lambda:w.query({'operation':'cards','glyph':'ץ'})[0]['id'])
            r=w.paperclip('r:clip','w:clip','w:index')
            check('integration','paperclip idempotent',r,lambda:w.paperclip('r:clip','w:clip','w:index'))
            stamps=w.stamp_matches('w:clip')
            check('integration','evidenced stamp created',1,lambda:len(stamps))
            check('integration','stamp remains association','association-not-verified-theorem',lambda:stamps[0]['body']['status'])
        with EchoWorkspace(db) as w:
            check('integration','restart retains original index relation',True,lambda:'index' in w.query({'operation':'neighbors','word':'paperclip'})['neighbors'])
            check('integration','restart retains typed links',2,lambda:len(w.query({'operation':'relations'})))

    groups=defaultdict(Counter)
    for case in cases:groups[case['group']][case['status']]+=1
    return {'battery':'echo-transparent-diagnostics/1','comparison_commit':'768e5b744224732e42f128db887287108093611f',
            'method':'Small fixed synthetic diagnostic cases, no model calls or training; not standardized intelligence scores. POS labels supplied by evaluator. Grammar expectations describe ordinary English, broader than original generalization-validator contract.',
            'summary':dict(Counter(c['status'] for c in cases)),
            'by_group':{g:dict(v) for g,v in groups.items()},'cases':cases}


if __name__=='__main__':
    report=run()
    target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'reports/echo-benchmarks/baseline.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'summary':report['summary'],'by_group':report['by_group']},indent=2))
