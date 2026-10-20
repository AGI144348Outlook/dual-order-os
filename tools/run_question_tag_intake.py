"""Reproduce provisional lexical annotations; no category learning or private data."""
import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from libraries.echo_sentence_cards import SentenceCards,lexicon_from_zip,LEXICON_BLOB
from libraries.echo_question_tags import save_tags,candidate_tags

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output',required=True);args=p.parse_args()
    counts=Counter();hints=Counter();total=0
    with tempfile.TemporaryDirectory() as d:
        db=Path(d)/'cards.sqlite';e=SentenceCards(db)
        e.ingest(lexicon_from_zip(args.archive),source={'archive':LEXICON_BLOB})
        for c in e.box.list('cards'):
            if c['body'].get('kind')!='lexical-sense':continue
            a=save_tags(e.box,c['id']);total+=1
            counts.update(a['body']['possible_questions']);hints.update(h['category'] for h in a['body']['definition_hints'])
        e.close();e=SentenceCards(db,writable=False)
        restored=sum(c['body'].get('kind')=='question-affordances' for c in e.box.list('cards'));e.close()
    report={'source_archive_git_blob':LEXICON_BLOB,'sense_cards':total,'annotation_cards':restored,
      'provisional_affordance_counts':dict(counts),'unapproved_definition_hint_counts':dict(hints),
      'automatic_category_promotions':0,'persistence_verified':restored==total,'training':False,
      'scope':'Explicit noun->What candidates only without curated categories; keywords are review hints, not answers.',
      'manual_category_example':candidate_tags({'kind':'lexical-sense','word':'morning','pos':'noun','definition':'early part of day'},[{'category':'time-interval','source':'illustrative lesson assumption'}])}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('sense_cards','annotation_cards','persistence_verified')}))
if __name__=='__main__':main()
