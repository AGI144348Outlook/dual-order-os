"""UI adapter over original modules. No user text is evaluated as Python."""
import json
from libraries.echo_sentence_cards import SentenceCards,sense_id
from libraries.echo_question_tags import candidate_tags,definition_hints,answer_role
_demo=None
_words={'poodle':('noun','a kind of dog'),'dog':('noun','a kind of animal'),'animal':('noun','a living entity'),'parcel':('noun','a kind of object'),'object':('noun','a thing'),'carry':('verb','transport'),'have':('verb','possess'),'sleep':('verb','rest')}
def _state():
    c=_demo.box.get('cards','s');b=c['body']
    slots=[{'position_id':s['position_id'],'role':s['role'],'word':_demo._sense(s['selected']['id'])['body']['word'],
        'alternatives':[_demo._sense(a)['body']['word'] for a in s['alternatives']]} for s in b['slots']]
    return {'revision':c['revision'],'slots':slots,'history':b['history'],'claim':b['claim_status'],
            'output':_demo.render('s'),'revision_count':len(_demo.box.history('cards','s'))}
def dispatch(payload):
    global _demo
    op=payload['operation']
    if op=='init':
        if _demo:_demo.close()
        _demo=SentenceCards()
        _demo.ingest({w:{'senses':[{'pos':p,'def':d}]} for w,(p,d) in _words.items()},source={'fixture':'demo assumptions'})
        for cid,a,b in [('pd','poodle','dog'),('da','dog','animal'),('po','parcel','object')]:
            _demo.subtype(cid,sense_id(a,0),sense_id(b,0),evidence={'source':'demo assumption'})
        verb=payload.get('predicate','carry')
        _demo.frame('s',[{'role':r,'sense':sense_id(w,0)} for r,w in [('agent','poodle'),('predicate',verb),('patient','parcel')]])
        return _state()
    if op=='transform':
        _demo.transform('s',payload['position'],sense_id(payload['target'],0),mode=payload['mode'],expected_revision=_demo.box.get('cards','s')['revision'])
        return _state()
    if op=='reorder':
        _demo.reorder('s',payload['positions'],expected_revision=_demo.box.get('cards','s')['revision']);return _state()
    if op=='tags':
        sense={'kind':'lexical-sense','word':payload['word'],'pos':payload['pos'],'definition':payload['definition']}
        categories=[{'category':payload['category'],'source':'explicit demo assumption'}] if payload['category'] else []
        return dict(candidate_tags(sense,categories),definition_hints=definition_hints(sense))
    if op=='answer':return answer_role(payload['facts'],event=payload['event'],role=payload['role'],question=payload['question'])
    raise ValueError('Unsupported demo command')
def dispatch_json(payload):return json.dumps(dispatch(json.loads(payload)))
