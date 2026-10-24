"""Run Echo's talk course on a seed until graduation (G1–G3) or a stop rule, then the G2 held-out check.

Usage: python run_course.py SEED [SEED ...] [--out results] [--max-units N]
"""
import argparse
import json
import os
import random
import shutil
import time

from echo_talk import Talker
from teacher_talk import FRAMES, Teacher
from world_repo import CONTENT_WORDS, NUMBERS, YESNO

HERE = os.path.dirname(os.path.abspath(__file__))
G1_WORDS = 150
STALL_UNITS = 3


def curriculum(T):
    tw = lambda ch: [w for w in CONTENT_WORDS[ch] if w in T.testable]
    names = tw('name')
    formats = tw('format')
    places = tw('place')
    units = [
        dict(name='numbers', words=NUMBERS, tasks=[]),
        dict(name='kinds and sizes', words=tw('kind') + tw('size'), tasks=['count', 'show']),
        dict(name='formats 1 and spread', words=formats[:len(formats) // 2] + tw('spread'), tasks=['count', 'show', 'yesno'],
             truth=True),
        dict(name='formats 2', words=formats[len(formats) // 2:], tasks=['count', 'show', 'yesno', 'kind', 'format', 'size'],
             truth=True),
        dict(name='places 1', words=places[:len(places) // 2], tasks=list(FRAMES)),
        dict(name='places 2', words=places[len(places) // 2:], tasks=list(FRAMES)),
    ]
    for i in range(0, len(names), 12):
        units.append(dict(name=f'names {i // 12 + 1}', words=names[i:i + 12], tasks=list(FRAMES)))
    return units


def teach_mixed(T, words):
    T.teach_words([w for w in words if w not in NUMBERS and w not in YESNO])
    if any(w in NUMBERS for w in words):
        T.teach_numbers(reps=1)
    if any(w in YESNO for w in words):
        T.teach_truth(12)


def run_unit(T, u, log):
    t0 = time.time()
    rec = dict(unit=u['name'], new_words=len(u['words']))
    if u['name'] == 'numbers':
        T.teach_numbers()
    else:
        teach_mixed(T, u['words'])
    T.rest()
    rec['practice'] = T.practice(u['words'])
    T.rest()
    if u.get('truth'):
        rec['truth_lessons'] = T.teach_truth()
    # review: words still yellow after a test get taught again
    review = [w for w, d in T.dict.items() if d['color'] == 'yellow' and d['tests'] and w not in u['words']]
    T.rng.shuffle(review)
    review = review[:15]
    if review:
        teach_mixed(T, review)
        T.rest()
        T.practice(review)
    rec['review'] = len(review)
    if u['tasks']:
        d = T.dialogue(60, u['tasks'])
        rec['dialogue'] = dict(n=len(d), ok=sum(1 for x in d if x['ok']), asked=sum(1 for x in d if x['asked']))
        log.extend(d[-5:])
    T.rest()
    T.rest()                                  # recess before the ת check
    rec['changed'] = T.green_tests()
    # ת re-check: green words whose last test is oldest are checked again; forgotten ones turn yellow
    greens = sorted(T.green(), key=lambda w: T.dict[w]['tests'][-1][0])[:20]
    rec['rechecked'] = len(greens)
    rec['changed'] += T.green_tests(greens)
    rec['green'] = len(T.green())
    rec['seconds'] = round(time.time() - t0, 1)
    return rec


def g2(T, seed):
    spec = json.load(open(os.path.join(HERE, 'heldout_g2.json')))
    rng = random.Random(5000 + seed)
    T.rng = rng
    out = []
    for it in spec['items']:
        frames = {it['task']: [it['frame']]}
        q = None
        for _ in range(20):
            q = T.make_question(it['task'], T.w.test_pool, frames=frames, n_cons=it['constraints'])
            if q and all(w in T.dict for w in q['text'].split() if w in T.testable):
                break
        if q is None:
            out.append(dict(frame=it['frame'], skipped=True))
            continue
        r = T.converse(q, learn=False)
        green = set(T.green())
        content = [w for w in q['text'].split() if w in T.testable]
        r.update(frame=it['frame'], unmet=it.get('unmet'), all_green=all(w in green for w in content))
        out.append(r)
    return out


def score_g2(rows):
    ans = [r for r in rows if not r.get('skipped') and not r.get('unmet')]
    un = [r for r in rows if not r.get('skipped') and r.get('unmet')]
    ans_green = [r for r in ans if r['all_green']]
    return dict(answerable=len(ans), answerable_correct=sum(1 for r in ans if r['ok']),
                answerable_all_green=len(ans_green), answerable_all_green_correct=sum(1 for r in ans_green if r['ok']),
                unmet=len(un), unmet_asked=sum(1 for r in un if 'ask' in r['reply']),
                unmet_asked_right_word=sum(1 for r in un if r['reply'].get('ask') == r['unmet']),
                skipped=sum(1 for r in rows if r.get('skipped')))


def run(seed, out, max_units):
    folder = os.path.join(out, f'seed_{seed}')
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    talker = Talker(seed=seed, boxes_dir=os.path.join(folder, 'boxes'))
    T = Teacher(talker, seed)
    units = curriculum(T)
    log, recs = [], []
    best, stall, i = 0, 0, 0
    while True:
        if i < len(units):
            u = units[i]
        else:
            yellow = [w for w, d in T.dict.items() if d['color'] == 'yellow']
            untaught = [w for w in T.testable if w not in T.dict]
            if not yellow and not untaught:
                break
            u = dict(name=f'review {i - len(units) + 1}', words=(untaught + yellow)[:15], tasks=list(FRAMES))
        rec = run_unit(T, u, log)
        recs.append(rec)
        print(seed, rec['unit'], 'green', rec['green'], rec.get('dialogue'), rec['seconds'], 's', flush=True)
        i += 1
        if i >= len(units):
            if rec['green'] > best:
                best, stall = rec['green'], 0
            else:
                stall += 1
            if stall >= STALL_UNITS or i >= max_units:
                break
    rows = g2(T, seed)
    res = dict(seed=seed, units=recs, green=T.green(), n_green=len(T.green()), testable=len(T.testable),
               g2=score_g2(rows), speech=T.speech, talker=talker.snapshot(),
               dictionary={w: d for w, d in sorted(T.dict.items())})
    talker.boxes.close()
    json.dump(res, open(os.path.join(folder, 'result.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(dict(dialogue_samples=log, g2=rows), open(os.path.join(folder, 'transcript.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(seed, 'G1 green', res['n_green'], 'G2', res['g2'], 'speech', T.speech, flush=True)
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('seeds', type=int, nargs='+')
    ap.add_argument('--out', default=os.path.join(HERE, 'results'))
    ap.add_argument('--max-units', type=int, default=40)
    a = ap.parse_args()
    for s in a.seeds:
        run(s, a.out, a.max_units)
