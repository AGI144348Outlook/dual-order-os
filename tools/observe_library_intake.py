"""Bounded source reception; no lexical authority or executable operations inferred.

Writes source-bearing records only to the caller's local output directory.
Public reporting must use summary.json rather than copying the catalog or responses.
"""
import argparse
import bisect
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from libraries.echo_workspace import genesis
from libraries.echo_sentence_cards import lexicon_from_zip
from libraries.catalog_box import CatalogBox

SOURCE_SHA='4566617ba5f2931343967e29f2c6ccbbbb583b159a9386ee9b7f3512460bdc15'
def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def candidates(text):
    headings=list(re.finditer(r'(?m)(?:^|[\n\f])(###\s+(\d+)\.\s*([^\n\f]+))',text))
    sections=list(re.finditer(r'(?m)(?:^|[\n\f])(## Mashet E-Dictionary:[^\n\f]+)',text))
    breaks=[m.start() for m in re.finditer('\f',text)]
    bounds=[m.start(1) for m in sections]
    offset=0
    for page in text.split('\f'):
        visible=''.join(c for c in page.strip() if unicodedata.category(c)!='Cf')
        if re.fullmatch(r'[\u05d0-\u05ea]',visible):bounds.append(offset)
        offset+=len(page)+1
    records=[]
    for i,h in enumerate(headings):
        start=h.start(1);end=headings[i+1].start(1) if i+1<len(headings) else len(text)
        end=min([end]+[b for b in bounds if start<b<end])
        prior=[s for s in sections if s.start(1)<start]
        section=prior[-1].group(1) if prior else ''
        family=next((x for x in ('Aleph','Bet','Gimel','Dalet','He','Vav','Zayin') if re.search(r'\b'+x+r'\b',section)),'unresolved')
        records.append({'kind':'library-entry-candidate','status':'source-description-not-executable-or-verified',
            'source_sha256':SOURCE_SHA,'ordinal':int(h.group(2)),'family':family,
            'heading':h.group(3),'start_codepoint':start,'end_codepoint':end,
            'first_page':bisect.bisect_left(breaks,start)+1,
            'last_page':bisect.bisect_left(breaks,max(start,end-1))+1,'raw_text':text[start:end]})
    return records

def main():
    p=argparse.ArgumentParser();p.add_argument('--pdf',required=True);p.add_argument('--archive',required=True)
    p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output)
    if out.exists():raise ValueError('Use a fresh output directory')
    raw=Path(a.pdf).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Different attachment: review a new source plan')
    out.mkdir(parents=True)
    (out/'source.pdf').write_bytes(raw)
    extraction=out/'extracted-layout.txt'
    subprocess.run(['pdftotext','-layout',str(Path(a.pdf).resolve()),str(extraction)],check=True)
    text=extraction.read_text();entries=candidates(text);e=genesis();matrix=e.AlgorithmMatrix()
    identity=e.ReshIdentity(matrix);identity.anchor()
    dictionary=lexicon_from_zip(a.archive)
    lexicon={w:{'desc':v['senses'][0]['def'],'pos':v['senses'][0]['pos']} for w,v in dictionary.items()}
    for w,v in lexicon.items():matrix.index_dictionary_entry(w,v['desc'],v['pos'])
    tokens=sorted(set(e.AlgorithmicCommunicator()._tokenize(text)))
    # Source-derived spelling and explanatory-text probes; no desired answer supplied.
    first=entries[0]['heading']
    hebrew=''.join(c for c in first if '\u0590'<=c<='\u05ff')
    probes={'hebrew_heading':hebrew,'transliteration':'Alamnish',
            'functional_phrase':'Loom of Connectivity Recursive Integration',
            'state_terms':'Potential Directed Matrix Active Synapse',
            'known_words':'matrix flow word name'}
    def view():
        lobby=e.Lobby(matrix);lobby.populate();lobby.run_orientation();lobby.run_typed_study_groups();lobby.compute_generality_scores()
        return lobby
    def stats(lobby):
        return {'documents_seen':matrix.documents_seen,'indexed_units':len(matrix.content_units),
            'word_agents':len(lobby.agents),'ties':len(lobby.ties),
            'known_unique_english_content_tokens':sum(t in lobby.agents for t in tokens),
            'gap_unique_english_content_tokens':sum(t not in lobby.agents for t in tokens),
            'identity_valid':identity.validate()}
    def responses(lobby):
        c=e.AlgorithmicCommunicator(lobby=lobby,vgm={},lexicon=lexicon,alg_matrix=matrix.known)
        return {k:{'tokens':c._tokenize(v),'response':c.communicate(v)} for k,v in probes.items()}
    lobby=view();baseline=stats(lobby);original_agents=set(lobby.agents)
    base_responses=responses(lobby)
    (out/'baseline-probes.json').write_text(json.dumps(base_responses,ensure_ascii=False,indent=2)+'\n')
    observations=[];previous=base_responses
    for n in range(1,3):
        matrix.index_content(text,category='reading:mashet-library:'+SOURCE_SHA)
        lobby=view();current=responses(lobby)
        (out/f'pass-{n}-probes.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n')
        observations.append({'pass':n,**stats(lobby),'new_word_agents':sorted(set(lobby.agents)-original_agents),
            'probe_responses_equal_to_previous':current==previous,
            'changed_probes':[k for k in current if current[k]!=previous[k]],
            'source_documents_per_token':sorted(set(matrix.content_units[t] for t in set(text.lower().split()))),
            'vgm_claims_admitted':0})
        previous=current
    database=out/'reception.sqlite';box=CatalogBox(database)
    box.put_card('source:'+SOURCE_SHA,'Attached Mashet Library',{'kind':'source-document','sha256':SOURCE_SHA,
        'extraction_sha256':hashlib.sha256(extraction.read_bytes()).hexdigest(),'extracted_text':text,
        'extraction':'pdftotext -layout; no normalization or OCR'},provenance={'origin':'Timothy attachment'})
    for entry in entries:
        box.put_card('entry:'+SOURCE_SHA[:20]+':'+str(entry['start_codepoint']),entry['heading'],entry,
            provenance={'recorded_by':'explicit intake adapter','source_sha256':SOURCE_SHA})
    for step in observations:
        box.put_card('reading:'+str(step['pass']),'Document exposure',{'kind':'reading-observation',**step})
    before=box.list('cards');before_hash=digest(before);box.close()
    box=CatalogBox(database);restored=digest(box.list('cards'))==before_hash;box.close()
    # Public-safe aggregates only. Detailed records remain in the local output directory.
    summary={'source_sha256':SOURCE_SHA,'source_bytes':len(raw),'pages':text.count('\f'),
        'extracted_characters':len(text),'extraction_sha256':hashlib.sha256(extraction.read_bytes()).hexdigest(),
        'candidate_entries':len(entries),'entries_per_family':dict(Counter(x['family'] for x in entries)),
        'directional_controls':dict(Counter(unicodedata.name(c) for c in text if unicodedata.category(c)=='Cf')),
        'unique_english_content_tokens':len(tokens),'baseline':baseline,'exposures':observations,
        'hebrew_heading_probe_token_count':len(base_responses['hebrew_heading']['tokens']),
        'transliteration_is_word_agent_after': 'alamnish' in lobby.agents,
        'persistent_cards':len(before),'catalog_restored':restored,
        'source_pdf_unchanged':Path(a.pdf).read_bytes()==raw,
        'candidate_entries_created_by':'explicit adapter, not self-initiated Echo action',
        'dictionary_projection':'first listed source sense per spelling',
        'executable_algorithms_installed':0,'neural_training':False,
        'limits':['Source descriptions are not independently verified meanings or executable operations.',
                  'PDF text extraction may alter visual Hebrew ordering and spacing; raw PDF is retained.',
                  'Document indexing records co-occurrence, not directional glyph composition or causal understanding.',
                  'Existing Lobby reconstructs definition links from shared transitions; prose can contaminate lexical associations.',
                  'Pe output stating AcquisitionPlanner queued is text; this run does not invoke an acquisition worker.',
                  'New candidate cards are not automatically imported into spelling-keyed legacy WordAgents.',
                  'SQLite records persist; this run does not serialize/restore the in-memory AlgorithmMatrix.']}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
