"""Pulse-check pilot: full mechanism set vs one-mechanism-off variants.

Seeds 100-109 were not used while the code was being debugged (seeds 0-3 were).
Writes results/ : results.json, summary.md, transcript-seed100.jsonl, handover-seed100.json
"""
import json
import statistics as st
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
import echo_np                              # noqa: E402
from echo_np import Echo                    # noqa: E402
from teacher import Classroom               # noqa: E402

SEEDS = list(range(100, 110))
CONFIGS = {
    'full': {},
    'B1-a counts only (no outcome weighting)': dict(b1='a'),
    'no F1 tag-and-capture': dict(f1=False),
    'no A6 downscaling': dict(a6=False),
    'E2 delete instead of E1 dormant': dict(e1=False),
    'no G3 spaced review': dict(g3=False),
    'D1 greedy (no exploration)': dict(d1='greedy'),
    'D1-a epsilon-greedy': dict(d1='eps'),
    'no F2 pattern tokens': dict(f2=False),
    'no צ questions': dict(q=False),
    'no mutual exclusivity (new)': dict(me=False),
    'zero-learning control': dict(learn=False),
}
DOWNSCALE_SWEEP = [0.8, 0.9, 0.95]
LESSONS = ['ע', 'פ', 'צ', 'ר', 'ץ', 'ש', 'ק', 'ת']


def identity_anchor():
    """Echo's preserved Genesis A-000 identity check (read-only use)."""
    try:
        from libraries.echo_workspace import genesis
        core = genesis()
        a = core.ReshIdentity(core.AlgorithmMatrix()).anchor()
        return {'glyph': a.get('glyph'), 'status': a.get('status'), 'aliases': a.get('aliases')}
    except Exception as exc:                # report, never fake
        return {'status': 'unavailable', 'error': type(exc).__name__}


def one_run(flags, seed, transcript=False):
    e = Echo(seed=seed, identity=None, **flags)
    c = Classroom(e, seed, transcript=transcript)
    t0 = time.time()
    res = c.course()
    row = {'seed': seed, 'seconds': round(time.time() - t0, 2)}
    for g in LESSONS:
        quizzes = [a for a in res[g] if a['mode'] == 'quiz']
        if quizzes:
            row[g + ' first quiz'] = quizzes[0]['score']
            row[g + ' final quiz'] = quizzes[-1]['score']
        row[g + ' assignments'] = len(res[g])
    row['retention (ת)'] = row.pop('ת first quiz')
    row.pop('ת final quiz')
    row['green words'] = len(c.green - {'who'})
    row['questions asked'] = c.questions
    row['claims accepted'] = sum(1 for v in c.claims_checked.values() if v == 'accepted')
    row['claims rejected'] = sum(1 for v in c.claims_checked.values() if v.startswith('rejected'))
    row.update(e.memory_size())
    return row, c, e


def summarise(rows, keys):
    out = {}
    for k in keys:
        vals = [r[k] for r in rows if r.get(k) is not None]
        if vals:
            out[k] = (round(st.mean(vals), 3), round(st.pstdev(vals), 3))
    return out


def main():
    outdir = HERE / 'results'
    outdir.mkdir(exist_ok=True)
    report = {'identity': identity_anchor(), 'seeds': SEEDS, 'configs': {}, 'downscale_sweep': {}}
    keys = None
    for name, flags in CONFIGS.items():
        rows = []
        for seed in SEEDS:
            row, c, e = one_run(flags, seed, transcript=(name == 'full' and seed == SEEDS[0]))
            rows.append(row)
            if name == 'full' and seed == SEEDS[0]:
                with open(outdir / 'transcript-seed100.jsonl', 'w', encoding='utf-8') as f:
                    for line in c.transcript:
                        f.write(json.dumps(line, ensure_ascii=False) + '\n')
                (outdir / 'handover-seed100.json').write_text(json.dumps(
                    {'report': c.handover_report, 'claims': c.claims_checked, 'green': sorted(c.green),
                     'lessons': c.results, 'echo_state': e.snapshot()}, ensure_ascii=False, indent=1, default=str),
                    encoding='utf-8')
        keys = keys or [k for k in rows[0] if k != 'seed']
        report['configs'][name] = {'flags': flags, 'runs': rows, 'mean_sd': summarise(rows, keys)}
        print(f'{name:45s} green {report["configs"][name]["mean_sd"]["green words"]}  '
              f'retention {report["configs"][name]["mean_sd"]["retention (ת)"]}')
    original = echo_np.DOWNSCALE
    for s in DOWNSCALE_SWEEP:
        echo_np.DOWNSCALE = s
        rows = [one_run({}, seed)[0] for seed in SEEDS]
        report['downscale_sweep'][str(s)] = summarise(rows, keys)
        print('downscale', s, report['downscale_sweep'][str(s)]['green words'],
              report['downscale_sweep'][str(s)]['retention (ת)'])
    echo_np.DOWNSCALE = original
    (outdir / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    write_summary(report, keys, outdir / 'summary.md')


def write_summary(report, keys, path):
    full = {r['seed']: r for r in report['configs']['full']['runs']}
    cols = [k for k in keys if k.endswith('first quiz')] + ['retention (ת)', 'green words', 'active_links']
    lines = ['# Pilot summary (seeds %d-%d)\n' % (SEEDS[0], SEEDS[-1]),
             'Mean over 10 seeds. Δ = paired difference from `full` on the same seeds; '
             '"worse/better" counts seeds.\n',
             '| config | ' + ' | '.join(cols) + ' |', '|' + '---|' * (len(cols) + 1)]
    for name, data in report['configs'].items():
        cells = []
        for k in cols:
            m = data['mean_sd'].get(k, (None, None))[0]
            if name == 'full' or m is None:
                cells.append('' if m is None else f'{m:g}')
                continue
            d = [r[k] - full[r['seed']][k] for r in data['runs'] if r.get(k) is not None]
            worse = sum(1 for x in d if (x > 0 if k == 'active_links' else x < 0))
            better = sum(1 for x in d if (x < 0 if k == 'active_links' else x > 0))
            cells.append(f'{m:g} (Δ{st.mean(d):+.2f}; {worse}w/{better}b)')
        lines.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    lines += ['', '## Forgetting-rate sweep (A6-b factor s, full config)', '',
              '| s | retention | green words | active links |', '|---|---|---|---|']
    for s, m in report['downscale_sweep'].items():
        lines.append(f"| {s} | {m['retention (ת)'][0]:g} | {m['green words'][0]:g} | {m['active_links'][0]:g} |")
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
