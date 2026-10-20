"""Bounded observations, not training. No sentence prompt, no invented autonomous scheduler."""
import argparse
import contextlib
import hashlib
import io
import json
import os
import random
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from libraries.echo_workspace import genesis
from libraries.echo_sentence_cards import SentenceCards,lexicon_from_zip,LEXICON_BLOB

def digest(cards):return hashlib.sha256(json.dumps(cards,sort_keys=True).encode()).hexdigest()
class BudgetStop(Exception):pass

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    if (out/'cards.sqlite').exists():raise ValueError('Use a fresh output directory')
    random.seed(42);started=time.monotonic();dictionary=lexicon_from_zip(args.archive);e=genesis()
    cards=SentenceCards(out/'cards.sqlite')
    senses=cards.ingest(dictionary,source={'archive_git_blob':LEXICON_BLOB,'member':'core-lexicon/words.json'})
    catalog=json.loads((ROOT/'libraries/algorithms/mapped-combinations/catalog.json').read_text())
    for block in catalog['combinations']:
        cards.box.put_card('block:'+block['id'],block['id'],{'kind':'algorithm-block',**block})
    # Availability is not dispatch. Inspect state without calling any work runner.
    before=cards.box.list('cards');events=len(cards.box.events())
    after=cards.box.list('cards')
    idle={'autonomous_dispatcher':False,'before_hash':digest(before),'after_hash':digest(after),
          'new_card_events':len(cards.box.events())-events,'sentence_prompt':None,
          'observation':'No actions occur simply from making cards and blocks available.'}
    # Explicit bootstrap adapter: one legacy sense per spelling; all senses retained in cards.
    projection={w:{'desc':v['senses'][0]['def'],'pos':v['senses'][0]['pos']} for w,v in dictionary.items()}
    matrix=e.AlgorithmMatrix();identity=e.ReshIdentity(matrix);identity.anchor()
    for word,entry in projection.items():matrix.index_dictionary_entry(word,entry['desc'],entry['pos'])
    lobby=e.Lobby(matrix);lobby.label='core-lexicon-1000'
    with contextlib.redirect_stdout(io.StringIO()):
        lobby.populate();lobby.run_orientation();lobby.run_typed_study_groups()
    # Complete the documented Genesis ordering, without inventing word/sentence targets.
    lobby.compute_generality_scores()
    proposals=lobby.propose_neighborhoods()
    approved=lobby.scrutinize(proposals)
    initial_neighborhoods=lobby.commit(approved)
    if not identity.validate():raise RuntimeError('Genesis identity check failed')
    operations=[]
    class ObservedGovernor(e.LobbyEvolutionGovernor):
        pass
    def wrap(name):
        base=getattr(e.LobbyEvolutionGovernor,name)
        def record(self,*values,**kwargs):
            if len(operations)>=8:raise BudgetStop()
            result=base(self,*values,**kwargs)
            record={'operation':name,'arguments':[v for v in values if isinstance(v,(str,int,float,list,dict))],
                    'result':result if isinstance(result,(str,int,float,list,dict,type(None))) else type(result).__name__}
            operations.append(record)
            # Recorder mirrors actual committed operations; core does not itself call CatalogBox.
            cards.box.put_card('observed:'+str(len(operations)),name,{'kind':'observed-operation',**record},
                               provenance={'selected_by':'existing A-120 policy','persisted_by':'observation adapter'})
            return result
        return record
    for method in ('commit_recruit','commit_refine','commit_split','commit_merge'):setattr(ObservedGovernor,method,wrap(method))
    governor=ObservedGovernor([lobby],label='bounded-no-language-goal')
    pre=governor.lobby_health(governor.measure_lobby(lobby));stopped=False
    with contextlib.redirect_stdout(io.StringIO()):
        try:logs=governor.evolve(max_generations=2,budget_per_iter=8,verbose=False)
        except BudgetStop:logs=governor.evolution_log;stopped=True
    post=governor.lobby_health(governor.measure_lobby(lobby))
    pool=e.GeneralityMatrix([lobby]);pool.populate();vgm=e.ValidatedGeneralizationMatrix()
    # A separate explicitly started existing runner; order and pattern choices are its code's.
    generator=e.UnderstandingGenerator(pool,e.SyntacticalValidator(),vgm)
    with contextlib.redirect_stdout(io.StringIO()):accepted=generator.generate_combinatorial(max_candidates=40)
    for cid,statement in vgm.statements.items():
        cards.box.put_card('candidate:'+cid,statement['text'],{'kind':'statement-candidate','source':statement,
            'claim_status':'heuristic-acceptance-not-proof'},provenance={'selected_by':'existing UnderstandingGenerator',
            'persisted_by':'observation adapter'})
    end=cards.box.list('cards');logical_hash=digest(end);cards.close()
    reopened=SentenceCards(out/'cards.sqlite',writable=False)
    restored=digest(reopened.box.list('cards'))==logical_hash;reopened.close()
    report={'archive_git_blob':LEXICON_BLOB,'dictionary_words':len(dictionary),'sense_cards':senses,
        'legacy_projection':'first listed sense per spelling only','algorithm_blocks':len(catalog['combinations']),
        'python_hash_seed':os.environ.get('PYTHONHASHSEED'),'random_seed':42,'idle_availability':idle,
        'explicit_starts':['bootstrap orientation, study groups, generality scoring and scrutinized neighborhood commits','A-120 evolve: 2 generations / 8 commit calls maximum',
                           'UnderstandingGenerator combinatorial: 40 candidate attempts maximum'],
        'bootstrap':{'agents':len(lobby.agents),'ties':len(lobby.ties),'proposed_neighborhoods':len(proposals),'committed_neighborhoods':len(initial_neighborhoods)},
        'evolution':{'before':pre,'after':post,'operations':operations,'log':logs,'hard_commit_cap_reached':stopped},
        'candidate_generation':{'pool_size':len(pool.pool),'accepted':accepted,'rejected':vgm.rejected,
                                'candidates':list(vgm.statements.values()),'status':'not-verified-logics'},
        'persistence_verified':restored,'final_cards':len(end),'logical_card_hash':logical_hash,
        'duration_seconds':round(time.monotonic()-started,3),
        'limits':['No autonomous dispatcher connects the available blocks.',
                  'No independently chosen sentence goal, invented algorithm, or self-initiated sentence-card use observed.',
                  'Recorded cards mirror legacy activity; their recorder is new adapter code.',
                  'No subtype edges inferred from definition overlap; no mixed-POS hierarchy imported.',
                  'No external models, training, network access or Python from the ZIP executed.']}
    (out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('dictionary_words','sense_cards','final_cards','persistence_verified','duration_seconds')}))
if __name__=='__main__':main()
