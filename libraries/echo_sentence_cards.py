"""Experimental sense/position cards. Inert data; trusted calls, no autonomous dispatcher.
Generalization is licensed only for positive existential frames under supplied subtype assumptions.
"""
import copy
import hashlib
import json
import zipfile
from collections import deque
from pathlib import Path
from .catalog_box import CatalogBox
LEXICON_BLOB = '370e23a301badb6362eac29682afc5bba9e8d5a4'
def lexicon_from_zip(path):
    raw=Path(path).read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=LEXICON_BLOB:
        raise ValueError('Lexicon differs from pinned source')
    with zipfile.ZipFile(path) as z:return json.loads(z.read('core-lexicon/words.json'))
def sense_id(word,index):return 'lex:'+hashlib.sha256(word.encode()).hexdigest()[:24]+':'+str(index)
class SentenceCards:
    def __init__(self,database=':memory:',*,writable=True):
        self.box=CatalogBox(database);self.writable=writable
    def close(self):self.box.close()
    def _write(self):
        if not self.writable:raise PermissionError('Card writes disabled')
    def ingest(self,dictionary,*,source):
        self._write();prepared=[]
        for word,entry in dictionary.items():
            if not isinstance(word,str) or not word or not entry.get('senses'):raise ValueError('Word and senses required')
            for i,s in enumerate(entry['senses']):
                if not all(isinstance(s.get(k),str) and s[k] for k in ('pos','def')):raise ValueError('Role and definition required')
                body={'kind':'lexical-sense','word':word,'sense_index':i,'pos':s['pos'],'definition':s['def'],
                      'example':s.get('ex'),'frequency':entry.get('z'),'status':'source-record-not-verified-semantics'}
                prepared.append((sense_id(word,i),word,body))
        for cid,word,body in prepared:
            try:
                old=self.box.get('cards',cid)
                if old['body']!=body or old['provenance']!=source:raise ValueError('Source card collision')
            except KeyError:pass
        for cid,word,body in prepared:
            try:self.box.get('cards',cid)
            except KeyError:self.box.put_card(cid,word,body,provenance=source)
        return len(prepared)
    def _sense(self,cid,revision=None):
        c=self.box.get('cards',cid,revision)
        if c['body'].get('kind')!='lexical-sense':raise ValueError('Expected lexical sense')
        return c
    def subtype(self,cid,child,parent,*,evidence):
        self._write();a,b=self._sense(child),self._sense(parent)
        if a['id']==b['id'] or a['body']['pos']!='noun' or b['body']['pos']!='noun' or not evidence:
            raise ValueError('Distinct noun senses and explicit evidence required')
        return self.box.put_card(cid,'subtype',{'kind':'subtype','child':{'id':a['id'],'revision':a['revision']},
            'parent':{'id':b['id'],'revision':b['revision']},'evidence':evidence,'status':'supplied-assumption-not-independent-proof'})
    def _path(self,child,parent):
        q=deque([(child,[])]);seen=set();edges=self.box.list('cards')
        while q:
            cid,path=q.popleft()
            if cid==parent:return path
            if cid in seen:continue
            seen.add(cid)
            for c in edges:
                b=c['body']
                if b.get('kind')=='subtype' and b['child']['id']==cid:
                    if any(self.box.get('cards',b[k]['id'])['revision']!=b[k]['revision'] for k in ('child','parent')):continue
                    q.append((b['parent']['id'],path+[c['id']]))
        return None
    def frame(self,cid,slots,*,scope='positive-existential'):
        self._write()
        if scope!='positive-existential':raise ValueError('Only positive existential frames supported')
        if [s.get('role') for s in slots]!=['agent','predicate','patient']:raise ValueError('Explicit agent/predicate/patient required')
        body={'kind':'sentence-frame','scope':scope,'slots':[],'history':[],'claim_status':'input-assumption-not-world-verification'}
        for i,(slot,pos) in enumerate(zip(slots,['noun','verb','noun'])):
            c=self._sense(slot['sense'])
            if c['body']['pos']!=pos:raise ValueError('Role/POS mismatch')
            body['slots'].append({'position_id':cid+':'+str(i),'role':slot['role'],
                'selected':{'id':c['id'],'revision':c['revision']},'alternatives':[c['id']]})
        return self.box.put_card(cid,'sentence frame',body)
    def transform(self,cid,position_id,target,*,mode,expected_revision):
        self._write()
        if mode not in ('generalize','specialize'):raise ValueError('Unknown transformation')
        old=self.box.get('cards',cid)
        if old['body'].get('kind')!='sentence-frame':raise ValueError('Expected frame')
        body=copy.deepcopy(old['body']);slot=next((s for s in body['slots'] if s['position_id']==position_id),None)
        if slot is None or slot['role']=='predicate':raise ValueError('Noun position required')
        source=slot['selected']['id'];target_card=self._sense(target)
        if target_card['body']['pos']!='noun' or source==target:raise ValueError('Distinct noun candidate required')
        if self.box.get('cards',source)['revision']!=slot['selected']['revision']:raise ValueError('Source sense changed; explicit rebase required')
        path=self._path(source,target) if mode=='generalize' else self._path(target,source)
        if path is None:raise ValueError('No supplied subtype path')
        slot['selected']={'id':target,'revision':target_card['revision']}
        if target not in slot['alternatives']:slot['alternatives'].append(target)
        body['history'].append({'operation':mode,'position_id':position_id,'from':source,'to':target,'evidence':path})
        if mode=='specialize':body['claim_status']='candidate-needs-instance-evidence'
        return self.box.put_card(cid,old['title'],body,expected_revision=expected_revision)
    def reorder(self,cid,positions,*,expected_revision):
        self._write();old=self.box.get('cards',cid);body=copy.deepcopy(old['body'])
        if body.get('kind')!='sentence-frame':raise ValueError('Expected frame')
        by_id={s['position_id']:s for s in body['slots']}
        if len(positions)!=len(by_id) or set(positions)!=set(by_id):raise ValueError('Permutation required')
        body['slots']=[by_id[p] for p in positions];body['history'].append({'operation':'reorder','positions':positions})
        body['claim_status']='candidate-needs-grammar-audit'
        return self.box.put_card(cid,old['title'],body,expected_revision=expected_revision)
    def render(self,cid):
        body=self.box.get('cards',cid)['body']
        if body.get('kind')!='sentence-frame':raise ValueError('Expected frame')
        if [s['role'] for s in body['slots']]!=['agent','predicate','patient']:return {'decision':'ABSTAIN','reason':'Outside supported SVO order'}
        a,v,b=[self._sense(s['selected']['id'],s['selected']['revision'])['body']['word'] for s in body['slots']]
        forms={'have':'has','give':'gives','move':'moves','carry':'carries','see':'sees','make':'makes'}
        if v not in forms:return {'decision':'ABSTAIN','reason':'No tested inflection for predicate'}
        return {'decision':'CANDIDATE','sentence':f'Some {a} {forms[v]} some {b}.','claim_status':body['claim_status'],
                'execution':False,'scope':'Singular positive existential SVO only; countability not audited.'}
