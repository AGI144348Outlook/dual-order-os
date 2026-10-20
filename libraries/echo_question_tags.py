"""Provisional question affordances, separate from evidence-backed event roles.
No free-text comprehension, hidden answer extraction, or semantic learning is claimed.
"""
import hashlib
import re

# Explicit research rules; category membership must come from a supplied source.
CATEGORY_QUESTIONS = {
    'person': ['who','what'], 'place': ['where','what'],
    'time-interval': ['when','what'], 'event': ['what'],
    'object': ['what'], 'substance': ['what'], 'concept': ['what'],
    'manner': ['how'], 'method': ['how'], 'cause': ['why'],
    'purpose': ['why'], 'quantity': ['how-many-or-much'],
}
ROLE_QUESTIONS = {'agent':['who','what'], 'patient':['who','what'],
    'location':['where'], 'time':['when'], 'manner':['how'], 'method':['how'],
    'cause':['why'], 'purpose':['why'], 'owner':['whose'],
    'quantity':['how-many-or-much']}

def candidate_tags(sense, categories=()):
    """Possible answer roles, never sufficient evidence for an actual answer."""
    if sense.get('kind')!='lexical-sense':raise ValueError('A sense-specific card is required')
    tags={}
    def add(q,reason):tags.setdefault(q,[]).append(reason)
    if sense['pos']=='noun':add('what','noun-role candidate; context and sense still required')
    for item in categories:
        if not isinstance(item,dict) or item.get('category') not in CATEGORY_QUESTIONS or not item.get('source'):
            raise ValueError('Known category and source required')
        for q in CATEGORY_QUESTIONS[item['category']]:
            add(q,{'category':item['category'],'source':item['source']})
    # No catch-all adverb -> how, noun -> who, or arbitrary why tag.
    return {'kind':'question-affordances','possible_questions':sorted(tags),
            'reasons':tags,'status':'candidate-not-contextual-answer','rule_version':'question-tags-v1'}

def definition_hints(sense):
    """Small audited-text shortlist. Suggestions only; never converted to category facts."""
    text=sense['definition'].lower();hints=[]
    patterns={'person':r'\b(person|someone|somebody)\b',
              'place':r'\b(place|location|region)\b',
              'time-interval':r'\b(time|period|interval|duration)\b'}
    for category,pattern in patterns.items():
        matches=sorted(set(re.findall(pattern,text)))
        if matches:hints.append({'category':category,'matched_text':matches,
                                'status':'definition-keyword-candidate-not-proof'})
    return hints

def save_tags(box,sense_id,*,categories=()):
    source=box.get('cards',sense_id)
    body=candidate_tags(source['body'],categories)
    body['source_sense']={'id':source['id'],'revision':source['revision']}
    body['definition_hints']=definition_hints(source['body'])
    cid='qtag:'+hashlib.sha256(sense_id.encode()).hexdigest()[:32]
    try:
        old=box.get('cards',cid)
        if old['body']==body:return old
        revision=old['revision']
    except KeyError:revision=0
    return box.put_card(cid,'Question affordances: '+source['title'],body,
                        provenance={'method':'explicit provisional rules'},expected_revision=revision)

def tags_current(box,annotation):
    ref=annotation['body']['source_sense']
    return box.get('cards',ref['id'])['revision']==ref['revision']

def answer_role(facts,*,event,role,question):
    """Answer from supplied event-role facts, not from vocabulary affordances.
    Unknown/negative/conflicting facts are never completed by guessing.
    """
    if not isinstance(event,str) or not event:raise ValueError('An explicit event is required')
    if role not in ROLE_QUESTIONS or question not in ROLE_QUESTIONS[role]:
        return {'decision':'ABSTAIN','reason':'Unsupported question/role combination'}
    selected=[f for f in facts if f.get('event')==event and f.get('role')==role]
    if not selected:return {'decision':'UNKNOWN','answers':[],'evidence':[]}
    if any(not f.get('id') or not isinstance(f.get('value'),str) or not f['value'] or
           f.get('polarity') not in ('positive','negative') for f in selected):
        return {'decision':'ABSTAIN','reason':'Malformed or unsupported evidence'}
    yes={f['value'] for f in selected if f['polarity']=='positive'}
    no={f['value'] for f in selected if f['polarity']=='negative'}
    if yes & no:return {'decision':'WITHHOLD','reason':'Contradictory supplied facts',
                        'evidence':[f['id'] for f in selected]}
    if not yes:return {'decision':'UNKNOWN','answers':[],'evidence':[f['id'] for f in selected]}
    positive=[f for f in selected if f['polarity']=='positive']
    if question=='who' and any(f.get('category')!='person' for f in positive):
        return {'decision':'WITHHOLD','reason':'Person typing not established for all answers'}
    return {'decision':'SUPPORTED','answers':sorted(yes),'evidence':[f['id'] for f in positive],
            'scope':'Relative to supplied typed facts, not independently extracted from text'}
