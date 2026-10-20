import sys, json, math, random, copy, re, pathlib, contextlib, io
ROOT=pathlib.Path('/tmp/echo-genesis-exact');sys.path.insert(0,str(ROOT/'src'))
import echo_governor_skeleton as e
random.seed(42)
results=[];observations={}
def assert_true(v):assert v

def test(group,name,fn):
 try:
  details=fn();results.append({'group':group,'name':name,'status':'PASS','details':details})
 except AssertionError as ex:results.append({'group':group,'name':name,'status':'FAIL','details':str(ex)})
 except Exception as ex:results.append({'group':group,'name':name,'status':'ERROR','details':type(ex).__name__+': '+str(ex)})
def eq(a,b):assert a==b, f'observed={a!r}; expected={b!r}'
def raises(typ,fn):
 try:fn()
 except typ:return
 raise AssertionError('expected '+typ.__name__+' was not raised')
def dump(v):return json.dumps(v,sort_keys=True,default=lambda x:sorted(x) if isinstance(x,set) else str(x))
def fixture(reverse=False):
 m=e.AlgorithmMatrix();entries=[('entity','existence state change','noun'),('state','entity condition change','noun'),('change','state entity transform','verb'),('condition','state entity','noun')]
 for word,definition,pos in reversed(entries) if reverse else entries:m.index_dictionary_entry(word,definition,pos=pos)
 l=e.Lobby(m);l.populate();return m,l
# Identity/order boundaries
m=e.AlgorithmMatrix();r=e.ReshIdentity(m)
test('identity','Resh requires anchoring',lambda:eq(r.validate(),False))
test('identity','Resh anchor identifies A-000',lambda:(r.anchor(),eq(r.validate(),True),eq(m.known['A-000']['identity_glyph'],'ר')))
def damaged_anchor():
 del m.known['A-000-RESH'];eq(r.validate(),False)
test('identity','Removed anchor is detected',damaged_anchor)
test('governance','Missing A-000 blocks deployment',lambda:(m.known.pop('A-000'),eq(e.governor_validate_and_deploy(m)['status'],'FAILED')))
def inactive():
 m=e.AlgorithmMatrix();m.known['A-000']['status']='INACTIVE';eq(e.governor_validate_and_deploy(m)['status'],'FAILED')
test('governance','Inactive A-000 blocks deployment',inactive)
test('governance','Wrong operation order detected',lambda:assert_true(bool(e.OperationOrderValidator().validate_sequence(['compute_generality_scores','run_orientation']))))
def assert_true(v):assert v
# rerun the deferred lambda now assert_true is defined
if results[-1]['status']=='ERROR' and 'assert_true' in results[-1]['details']:results.pop();test('governance','Wrong operation order detected',lambda:assert_true(bool(e.OperationOrderValidator().validate_sequence(['compute_generality_scores','run_orientation']))))
test('governance','Correct operation order accepted',lambda:eq(e.OperationOrderValidator().validate_sequence(['index_dictionary_entry','run_orientation','compute_generality_scores','populate_generality_matrix']),[]))
def prereqs():
 v=e.OperationOrderValidator();eq(v.check_prereqs('compute_generality_scores')['ok'],False);v.mark_complete('run_orientation');eq(v.check_prereqs('compute_generality_scores')['ok'],True)
test('governance','Prerequisite completion changes gate',prereqs)
# Small controlled input fixtures, original implementations
m,l=fixture();test('indexing','Dictionary ingestion populates typed agents',lambda:(eq(set(l.agents),{'entity','state','change','condition'}),eq(l.agents['change'].department,'verb')))
def unconfirmed():
 _,x=fixture();x.agents['entity'].identity_confirmed=False;raises(RuntimeError,x.run_orientation)
test('orientation','Unconfirmed agent blocks orientation',unconfirmed)
l.run_orientation()
test('orientation','Discovered relationships are bidirectional',lambda:assert_true(all(a in l.agents[b].ties for a,agent in l.agents.items() for b in agent.ties)))
def reverse_order():
 _,rev=fixture(True);rev.run_orientation();eq(l.ties,rev.ties)
test('orientation','Reversed ingestion preserves orientation ties',reverse_order)
def repeated():
 _,x=fixture();x.run_orientation();old=dict(x.ties);before=len(x.agents);x.run_orientation();eq(len(x.agents),before);eq(x.ties,{k:2*v for k,v in old.items()})
test('orientation','Repeated orientation preserves nodes and adds tie strength',repeated)
test('indexing','Indexed graph supports semantic traversal',lambda:assert_true(len(m.semantic_chain('entity',length=3))>1))
test('learning','Document frequencies count once per document',lambda:doc_frequency())
def doc_frequency():
 x=e.AlgorithmMatrix();x.index_content('entity entity state');eq(x.content_units['entity'],1);x.index_content('entity');eq(x.content_units['entity'],2)
if results[-1]['status']=='ERROR' and 'doc_frequency' in results[-1]['details']:results.pop();test('learning','Document frequencies count once per document',doc_frequency)
def bandit():
 x=e.AlgorithmMatrix();x.record_outcome('op','bucket',True);x.record_outcome('op','bucket',False);eq(x.current_generation[('op','bucket')],(1,2));eq(x.history,{});x.record_outcome('op','bucket',True);eq(x.checkpoint_generation()['decision'],'ANCHORED');eq(x.history[('op','bucket')],(2,3))
test('learning','Success and failure both enter bandit history',bandit)
# Generalization and statements
lexicon={'stone':{'desc':'an object'},'object':{'desc':'an entity'},'entity':{'desc':'existence'}}
test('generalization','Specific-to-general path retains every level',lambda:eq(e.GeneralizationStack(lexicon).build('stone'),['stone','object','entity']))
test('generalization','Cycles terminate without duplicate levels',lambda:eq(e.GeneralizationStack({'alpha':{'desc':'beta'},'beta':{'desc':'alpha'}}).build('alpha'),['alpha','beta']))
test('generalization','Unknown word remains an explicit singleton',lambda:eq(e.GeneralizationStack(lexicon).build('unknown'),['unknown']))
vgm=json.loads((ROOT/'matrices/echo_vgm.json').read_text())
test('generalization','Saved VGM can be queried with stack provenance',lambda:assert_true(all('stack_level' in x and 'stmt_id' in x for x in e.VGMQuery(vgm).query(['entity'])) and len(e.VGMQuery(vgm).query(['entity']))>0))
test('generalization','Invalid grammatical sequence rejected',lambda:eq(e.SyntacticalValidator().validate([('change','verb'),('entity','noun')],{})['valid'],False))
test('generalization','Low-generality term rejected',lambda:eq(e.SyntacticalValidator().validate([('entity','noun'),('changes','verb')],{'entity':{'generality':0.1}})['reason'],'SPECIFICITY_BREACH'))
# Existing hypothesis handling; no new sandbox implementation
l.run_typed_study_groups();g=e.LobbyEvolutionGovernor([l]);h=e.HypothesisSandbox(l,m,g)
l.neighborhoods={'N-TEST':{'members':['entity','state','condition'],'size':3}}
for a in l.agents.values():a.neighborhood='N-TEST' if a.word in l.neighborhoods['N-TEST']['members'] else None
hyp={'id':'A-9000','name':'probe','origin':'test fixture','strategy':'THRESHOLD_TUNE','description':'test fixture','test_fn':'hub_quarantine','parameters':{'hub_words':['entity']},'target_deficiency':'test','target_metric':'precision'}
def isolation():
 before=dump({'n':l.neighborhoods,'ties':l.ties if False else sorted((list(k),v) for k,v in l.ties.items()),'assign':{w:a.neighborhood for w,a in l.agents.items()},'agents':{w:sorted(a.ties) for w,a in l.agents.items()}})
 outcome=h.sandbox_test(hyp)
 after=dump({'n':l.neighborhoods,'ties':sorted((list(k),v) for k,v in l.ties.items()),'assign':{w:a.neighborhood for w,a in l.agents.items()},'agents':{w:sorted(a.ties) for w,a in l.agents.items()}})
 eq(before,after);return outcome
test('hypotheses','Existing hypothesis test leaves live neighborhood state unchanged',isolation)
test('hypotheses','Unknown hypothesis operation returns rejected error',lambda:eq(h.sandbox_test({**hyp,'test_fn':'not_defined'})['accepted'],False))
# Contract probes expose limits without correcting them

def invariant_gate():eq(e.validate({'theta':{'invalid':True}},[lambda *args:False])[0],False)
test('contract','Invariant validator rejects a deliberately failing invariant',invariant_gate)
test('contract','Governor rejects an over-budget candidate',lambda:eq(e.govern({'complexity':100},{'C_max':0},{}),False))
def untested():
 a=e.GeneratedAlgorithm('untested','probe','fixture','TEST',lambda:1,[]);eq(a.run_tests(),False)
test('contract','Generated operation without tests remains unverified',untested)
def rejected_registration():
 x=e.AlgorithmMatrix();_,y=fixture();z=e.HypothesisSandbox(y,x,e.LobbyEvolutionGovernor([y]));z.register(hyp,{'accepted':False,'baseline_C':1,'sandbox_C':0,'delta_C':-1});assert x.known.get('A-9000',{}).get('status')!='ACTIVE','Direct register() activated rejected hypothesis'
test('contract','Direct hypothesis registration refuses rejected results',rejected_registration)
def rejected_vgm():
 x=e.ValidatedGeneralizationMatrix();x.commit(['entity','changes'],['noun','verb'],{'valid':False,'score':0},origin='test');eq(len(x.statements),0)
test('contract','Direct VGM commit refuses failed validation',rejected_vgm)
test('contract','VGM word lookup excludes substring-only matches',lambda:eq(e.VGMQuery({'s':{'words':['parts'],'text':'Contains parts'}}).query(['art']),[]))
# Mathematics: independent expected values, original code only
x=e.AlgebraicExpression.variable(e.Variable('x'))
test('mathematics','Expression evaluation matches known arithmetic',lambda:eq((x*x+2*x+1).evaluate({'x':3}),16))
def numerical():
 a=e.NumericalIntegrator(0,1,1000).integrate(lambda x:x*x)['result'];assert abs(a-1/3)<1e-5,a
 b=e.NumericalIntegrator(0,1,10).integrate(lambda x:x*x)['result'];assert abs(a-1/3)<abs(b-1/3)
test('mathematics','Numerical integration converges toward known integral',numerical)
def wrong_algorithm():
 a=e.GeneratedAlgorithm('wrong','test','fixture','TEST',lambda x:x+1,[{'inputs':{'x':1},'expected':10}]);eq(a.run_tests(),False)
test('mathematics','Generated algorithm with incorrect expected result fails',wrong_algorithm)
# Saved branch data, not external thesaurus or generated corpus
saved=json.loads((ROOT/'matrices/echo_lobby_agents.json').read_text());actual=e.AlgorithmMatrix()
for word,record in saved.items():actual.index_dictionary_entry(word,record['definition'],pos=record['department'])
actual_lobby=e.Lobby(actual);actual_lobby.populate();actual_lobby.run_orientation();actual_lobby.run_typed_study_groups()
observations['saved_data']={'source_records':len(saved),'rebuilt_agents':len(actual_lobby.agents),'ties':len(actual_lobby.ties),'vgm_statements':len(vgm),'algorithm_entries':len(json.loads((ROOT/'matrices/echo_algorithm_matrix.json').read_text())),'note':'Fresh ingestion of preserved definitions, not restoration of original runtime state'}
test('saved-data','Preserved vocabulary can be ingested and oriented',lambda:assert_true(len(actual_lobby.agents)>1000 and len(actual_lobby.ties)>0))
test('saved-data','Real-data orientation ties are bidirectional',lambda:assert_true(all(w in actual_lobby.agents[t].ties for w,a in actual_lobby.agents.items() for t in a.ties)))
comm=e.AlgorithmicCommunicator(actual_lobby,vgm=vgm,alg_matrix=json.loads((ROOT/'matrices/echo_algorithm_matrix.json').read_text()))
test('communication','Unknown English input is reported as a gap',lambda:assert_true('GAP' in comm.communicate('zzqvunknownword')))
test('communication','Known saved vocabulary produces algorithmic output',lambda:assert_true('Ayin' in comm.communicate('entity change') and 'Pe' in comm.communicate('entity change')))
observations['communication_examples']={t:comm.communicate(t) for t in ['entity change','echo','zzqvunknownword','רעי','|{•}{•}|','123 3.14']}
for label,text in [('Hebrew glyph input','רעי'),('Bracket-symbol input','|{•}{•}|'),('Numeric input','123 3.14')]:
 tokens=comm._tokenize(text);results.append({'group':'capability','name':label,'status':'UNSUPPORTED' if not tokens else 'PASS','details':{'tokens':tokens,'response':comm.communicate(text)}})
# Matrices are readable but no claim that all source labels are true.
formula=json.loads((ROOT/'matrices/echo_formula_matrix.json').read_text());engine=e.InformationAlgorithmizer(e.AlgorithmMatrix())
for rec in list(formula.values())[:16]:
 agent=e.FormulaAgent(rec['name'],rec['expression'],rec.get('variables',{}),rec['domain'],rec.get('law',''));engine.algorithmize(agent)
observations['formula_generation']={'formulas_exercised':16,'generated':len(engine.generated),'registered':len(engine.registered),'failed':sum(not a.passed for a in engine.generated),'untested_accepted':sum(a.passed and not a.test_cases for a in engine.generated),'failed_details':[{'name':a.name,'reason':a.failure_reason} for a in engine.generated if not a.passed]}
test('formulas','Formula derivation produces callable operations',lambda:assert_true(len(engine.generated)>0 and all(callable(a.execute) for a in engine.generated)))
test('formulas','Failed generated candidates are absent from registered IDs',lambda:assert_true(all(a.alg_id not in engine.registered for a in engine.generated if not a.passed)))
def collapsed_generation():
 x=e.AlgorithmMatrix()
 for _ in range(3):x.record_outcome('op','bucket',True)
 x.checkpoint_generation();before=dict(x.history)
 for _ in range(3):x.record_outcome('op','bucket',False)
 eq(x.checkpoint_generation()['decision'],'DISCARDED');eq(x.history,before)
test('learning','Collapsed generation does not overwrite anchored history',collapsed_generation)
def balance():
 lex={**lexicon,'wood':{'desc':'an object'}};scale=e.BalancingScale(e.EquilibriumGeneralityMeasure(lexicon=lex));a=scale.weigh('stone','wood');b=scale.weigh('wood','stone');eq(a['status'],'CONVERGED');eq(a['equilibrium'],'object');eq(a['equilibrium'],b['equilibrium'])
test('balancing','Two known branches converge at shared genus in either order',balance)
test('balancing','Unrelated unknown inputs report no convergence',lambda:eq(e.BalancingScale(e.EquilibriumGeneralityMeasure()).weigh('unknownalpha','unknownbeta')['status'],'NO_CONVERGENCE'))
def invalid_number():
 a=e.GeneratedAlgorithm('nonfinite','test','fixture','TEST',lambda:float('nan'),[{'inputs':{},'expected':1.0}]);eq(a.run_tests(),False)
test('contract','Non-finite generated result fails numerical verification',invalid_number)
report={'branch':'genesis-documentary','commit':'f888091f6d81c60a61e5ca9bbba14d8d28a18093','method':'unchanged source, temporary external test harness, controlled fixtures and preserved branch data, no network calls or model use','tests':results,'observations':observations}
pathlib.Path('/tmp/echo-genesis-results/probe-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
from collections import Counter
print('TOTALS',dict(Counter(x['status'] for x in results)))
for x in results:print(x['status'],x['group'],x['name'], str(x['details'])[:200] if x['status']!='PASS' else '')
print('SAVED DATA',observations['saved_data']);print('FORMULA GENERATION',observations['formula_generation'])
