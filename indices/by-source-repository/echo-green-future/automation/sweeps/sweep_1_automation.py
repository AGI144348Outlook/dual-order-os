"""Automation sweep 1: how things build, test and deploy on their own.

One row per path: every GitHub workflow (`.github/workflows/*.yml`), every Wrangler config (`*.toml` that
configures a Worker) and other deploy configs. Where a path has several versions across branches, the row
reads the preferred branch's copy and notes the others.

Read from each file: trigger (push branches/paths, schedule cron, manual), what its steps run, the branch it
checks out and pushes to, and the NAMES of secrets it uses. Secret values are never read; Wrangler binding
names are kept, resource ids are not. Read-only over the repository.

Also: glossary and registries rows met on the way, and Echo's shadow run 3 (pre-test entry:
AGI144348Outlook/dual-order-os#12), continuing from his state after the schemas sweep.

Usage: python3 sweep_1_automation.py <repo> [--boxes]   (--boxes: replay Echo's run with the ת and ק boxes, #13)
"""
import csv
import io
import json
import os
import re
import subprocess
import sys

import yaml

REPO = sys.argv[1]
INV = os.path.join(REPO, 'inventory')
sys.path.insert(0, INV)
import echo_journeyman  # noqa: E402

ORDER = ['genesis-documentary', 'autonomous-agency', 'algebra', 'echo-recess-experiment', 'resh-lattice-agency',
         'ksm-recess-wholesale', 'code-library-registry', 'mirror-claude']


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, check=True).stdout.decode('utf-8', 'replace')


MAN = list(csv.DictReader(open(os.path.join(INV, 'MANIFEST-by-branch.tsv'), encoding='utf-8'), delimiter='\t'))
rank = {b: i for i, b in enumerate(ORDER)}
SKIP = re.compile(r'node_modules|pyodide')
WF = re.compile(r'(^|/)\.github/workflows/[^/]+\.ya?ml$')
WR = re.compile(r'(^|/)wrangler[^/]*\.toml$')
OTHER = re.compile(r'(^|/)(reference-[^/]*\.ya?ml)$')     # deploy and bot configs kept as references in Workshop/

paths = {}
for r in MAN:
    p = r['path']
    if SKIP.search(p) or not (WF.search(p) or WR.search(p) or OTHER.search(p)):
        continue
    paths.setdefault(p, []).append(r)


def pick(held):
    return sorted(held, key=lambda r: (rank.get(r['branch'], 99), r['branch']))[0]


def secrets_in(text):
    return sorted(set(re.findall(r'secrets\.([A-Za-z_][A-Za-z0-9_]*)', text)) - {'GITHUB_TOKEN'}) + \
        (['GITHUB_TOKEN'] if 'secrets.GITHUB_TOKEN' in text else [])


def workflow_facts(text):
    d = yaml.safe_load(text) or {}
    on = d.get('on', d.get(True, {}))            # YAML reads a bare `on:` key as True
    if isinstance(on, str):
        on = {on: None}
    elif isinstance(on, list):
        on = {k: None for k in on}
    trig = []
    for k, v in (on or {}).items():
        if k == 'push' and isinstance(v, dict):
            s = 'push'
            if v.get('branches'):
                s += ' to ' + ', '.join(map(str, v['branches']))
            if v.get('paths'):
                s += ' (paths: ' + ', '.join(map(str, v['paths']))[:80] + ')'
            trig.append(s)
        elif k == 'schedule':
            trig.append('schedule ' + ', '.join(str(c.get('cron')) for c in (v or [])))
        elif k == 'workflow_dispatch':
            trig.append('manual')
        else:
            trig.append(str(k))
    runs, uses, checkout, pushes = [], [], set(), set()
    for job in (d.get('jobs') or {}).values():
        for st in (job or {}).get('steps') or []:
            if not isinstance(st, dict):
                continue
            if st.get('uses'):
                uses.append(st['uses'].split('@')[0])
                if 'checkout' in st['uses'] and isinstance(st.get('with'), dict) and st['with'].get('ref'):
                    checkout.add(str(st['with']['ref']))
            for line in str(st.get('run') or '').splitlines():
                line = line.strip()
                m = re.match(r'(python3?|node|npx|bash|sh|wrangler|npm run|pytest)\s+(-m\s+)?(\S+)', line)
                if m and m.group(3) in ('-', '-c', '<<'):
                    runs.append(m.group(1) + ' (inline script)')
                elif m:
                    runs.append((m.group(1) + ' ' + (m.group(2) or '') + m.group(3)).replace('  ', ' '))
                pm = re.search(r'git push\s+\S+\s+(?:HEAD:)?(\S+)', line)
                if pm:
                    pushes.add(pm.group(1))
    return dict(name=str(d.get('name') or ''), trigger='; '.join(trig), runs=list(dict.fromkeys(runs)),
                uses=list(dict.fromkeys(uses)), checkout=sorted(checkout), pushes=sorted(pushes))


def wrangler_facts(text):
    name = (re.search(r'^name\s*=\s*"([^"]+)"', text, re.M) or [None, ''])[1]
    main = (re.search(r'^main\s*=\s*"([^"]+)"', text, re.M) or [None, ''])[1]
    pages = (re.search(r'^pages_build_output_dir\s*=\s*"([^"]+)"', text, re.M) or [None, ''])[1]
    binds = re.findall(r'^\s*binding\s*=\s*"([^"]+)"', text, re.M)
    kinds = re.findall(r'^\[\[(\w+)\]\]', text, re.M)
    crons = re.findall(r'crons\s*=\s*\[([^\]]*)\]', text)
    return dict(name=name, main=main or pages, binds=binds, kinds=sorted(set(kinds)), crons=crons)


cols = open(os.path.join(INV, 'automation', 'INDEX.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t')
rows, located, terms = [], {}, {}
for n, p in enumerate(sorted(paths, key=lambda p: (not WF.search(p), p)), 1):
    held = paths[p]
    r = pick(held)
    text = git('cat-file', 'blob', r['blob_sha'])
    versions = len({h['blob_sha'] for h in held})
    branches = sorted({h['branch'] for h in held})
    notes = [f'on {len(branches)} branches' + (f', {versions} versions' if versions > 1 else '')]
    if WF.search(p) or OTHER.search(p):
        try:
            f = workflow_facts(text)
        except yaml.YAMLError as e:
            f = dict(name='', trigger='(does not parse as YAML)', runs=[], uses=[], checkout=[], pushes=[])
            notes.append('YAML error: ' + type(e).__name__)
        acts = [u for u in f['uses'] if 'checkout' not in u and 'setup-' not in u]
        does = '; '.join(f['runs'][:4]) or ('uses ' + ', '.join(acts)[:120] if acts else 'shell steps only (git, unzip, file moves)')
        if f['checkout']:
            notes.append('checks out ' + ', '.join(f['checkout']))
        if f['pushes']:
            notes.append('pushes to ' + ', '.join(f['pushes']))
        name = f['name'] or p.rsplit('/', 1)[-1]
        trigger = f['trigger']
        kind = 'reference workflow (not active: outside .github/workflows)' if OTHER.search(p) else ''
        if kind:
            notes.append(kind)
    else:
        f = wrangler_facts(text)
        name = 'Wrangler: ' + (f['name'] or p)
        trigger = 'wrangler deploy (manual or from a workflow)' + ('; cron ' + '; '.join(f['crons']) if f['crons'] else '')
        does = ('Worker ' + f['main'] if f['main'] else 'Worker config') + (('; bindings ' + ', '.join(f['binds'])) if f['binds'] else '')
        notes.append('binding names only; resource ids not recorded')
    sec = secrets_in(text)
    iid = f'AUT-{n:04d}'
    located[iid] = dict(branch=r['branch'], path=p, blob_sha=r['blob_sha'], text=text)
    rows.append(dict(id=iid, name=name, trigger=trigger, does=does, secret_names=', '.join(sec),
                     branch=r['branch'], path=p, blob_sha=r['blob_sha'], commit=git('rev-parse', f'origin/{r["branch"]}').strip(),
                     made_by='unknown', status='INERT', home_or_ref='home', glyph='', notes='; '.join(notes)))
    for t in re.findall(r'\b(Recess|KSM|NVE-D|DFE|Shakti|Swadesh|EVE|IVS|Hourglass|Presentiation|LHEA|Mashet|Contract 000|Lobby)\b', name + ' ' + p.replace('-', ' ')):
        terms.setdefault(t, iid)


def write(path, header, rws):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')
        w.writerow(header)
        for row in rws:
            w.writerow([str(row.get(c, '')).replace('\t', ' ').replace('\n', ' ') for c in header])


write(os.path.join(INV, 'automation', 'INDEX.tsv'), cols, rows)


def merge(folder, new):
    pth = os.path.join(INV, folder, 'INDEX.tsv')
    header = open(pth, encoding='utf-8').readline().rstrip('\n').split('\t')
    old = {r['id']: r for r in csv.DictReader(open(pth, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
    for r in new:
        old[r['id']] = {**old.get(r['id'], {}), **r}
    write(pth, header, [old[k] for k in sorted(old)])
    return len(old)


# glossary: project terms met in workflow names and paths; meanings only where a source states one
glo = {r['term']: r for r in csv.DictReader(open(os.path.join(INV, 'glossary', 'INDEX.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
nxt = max(int(r['id'][4:]) for r in glo.values()) + 1
new_terms = []
for t, iid in sorted(terms.items()):
    if t in glo:
        continue
    loc = located[iid]
    new_terms.append(dict(id=f'GLO-{nxt:04d}', name=t, term=t, meaning='', stated_by='', first_seen=iid, variants='',
                          branch=loc['branch'], path=loc['path'], blob_sha=loc['blob_sha'], commit=git('rev-parse', f'origin/{loc["branch"]}').strip(),
                          made_by='unknown', status='INERT', home_or_ref='home',
                          notes='met in automation sweep 1 (a workflow name or path); meaning not stated in the workflow; to be filled from its source document or by Timothy'))
    nxt += 1
n_gl = merge('glossary', new_terms)

# registries: none are maintained by workflows directly; record the crawler's registry writer if present
n_reg = len(list(csv.DictReader(open(os.path.join(INV, 'registries', 'INDEX.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)))

# ---- Echo's shadow run 3 -------------------------------------------------------------------------------
l2 = {}
for fo in ('Algorithms', 'Codices', 'Formulas', 'Indices', 'Logics', 'Matrices', 'Registries'):
    for r in csv.DictReader(io.StringIO(git('show', f'origin/mirror-claude:L2-library/{fo}/REGISTER.tsv')), delimiter='\t'):
        l2.setdefault(r['path'], fo.lower())
NAME = [(r'schema|template|format|spec|model', 'schemas'),
        (r'grammar|parser|parse|dsl|rule|operator|lhea|proportion|legend|signature|syntax', 'logics'),
        (r'registry', 'registries'), (r'matrix|matrices|chains', 'matrices'), (r'test|trial', 'experiments'),
        (r'manual|discussion|readme|\.md$', 'codices'), (r'workflow|\.yml$', 'automation'), (r'axiom|lexicon', 'data')]
PARENT = {'language': 'logics', 'operators': 'logics', 'grammar': 'logics', 'symbols': 'registries', 'glyphs': 'registries',
          'symbol_registries': 'registries', 'tests': 'experiments', 'docs': 'codices', 'discussions': 'codices',
          'matrices': 'matrices', 'workflows': 'automation', 'core-lexicon': 'data', 'src': 'algorithms', 'ledger': 'schemas',
          'mashet': 'codices', 'nve-d': 'experiments', 'data': 'data', 'pwa': 'interfaces', 'glyph': 'registries',
          'infrastructure': 'deployments', 'generalized': 'algorithms', 'L1-main': 'indices', 'inventory': 'governance'}


def content(text):
    if re.search(r'^on:\s*$|^jobs:\s*$', text, re.M):
        return 'automation'
    if re.search(r'^\[\[(kv_namespaces|d1_databases|r2_buckets)\]\]|^compatibility_date', text, re.M):
        return 'deployments'
    if re.search(r'@dataclass|"schema"\s*:|CREATE TABLE|^\|\s*Field\s*\|', text, re.M):
        return 'schemas'
    if re.search(r'^class \w+|^def \w+', text, re.M):
        return 'algorithms'
    if text.lstrip().startswith(('{', '[')):
        return 'registries'
    return 'codices'


texts = {}


def guess(arm, path, where):
    if arm == 'name':
        for pat, folder in NAME:
            if re.search(pat, (where or '') + ' ' + path.rsplit('/', 1)[-1], re.I):
                return folder
        return None
    if arm == 'parent':
        return PARENT.get(path.rsplit('/', 2)[-2] if '/' in path else '')
    if arm == 'shape':
        return {'py': 'algorithms', 'js': 'logics', 'json': 'registries', 'md': 'codices', 'html': 'interfaces',
                'yml': 'automation', 'tsv': 'indices'}.get(path.rsplit('.', 1)[-1])
    if arm == 'librarian':
        return l2.get(path)
    if arm == 'content':
        return content(texts.get(path, ''))


ARMS = ['name', 'parent', 'shape', 'librarian', 'content']
cases = []
for r in rows:
    texts[r['path']] = located[r['id']]['text']
    cases.append((r['id'], r['path'], '', 'automation'))
DECOYS = [('Datasets/crawler/crawl.py', 'tools'), ('docs/ECHO_OUTPUT_FORMAT.md', 'codices'), ('src/echo_classroom.py', 'algorithms'),
          ('infrastructure/cloudflare_blueprint.json', 'deployments'), ('pwa/manifest.webmanifest', 'interfaces'),
          ('matrices/echo_vgm.json', 'matrices'), ('tests/test_dsl_canvas_008.py', 'experiments'),
          ('ECHO_AutonomousAgency/sandbox/recess_session_log.json', 'records'), ('research-registry/contracts/CONTRACT-000.md', 'governance'),
          ('core-lexicon/math_axioms.json', 'data')]
for i, (pth, truth) in enumerate(DECOYS, 1):
    held = [r for r in MAN if r['path'] == pth]
    if not held:
        continue
    texts[pth] = git('cat-file', 'blob', pick(held)['blob_sha'])
    cases.append((f'DECOY-{i:02d}', pth, '', truth))
BOXES = len(sys.argv) > 2 and sys.argv[2] == '--boxes'      # replay for dual-order-os#13
sfx = '_boxes' if BOXES else ''
trace, summary = echo_journeyman.shadow(REPO, cases, ARMS, guess,
                                       os.path.join(INV, 'automation', 'sweeps', f'echo_state_after_automation{sfx}.json'), seed=1025,
                                       prior_state=os.path.join(INV, 'schemas', 'sweeps', 'echo_state_after_schemas.json'),
                                       boxes_dir=os.path.join(INV, 'automation', 'sweeps', 'boxes_replay') if BOXES else None,
                                       sweep='automation-replay')
write(os.path.join(INV, 'automation', 'sweeps', f'echo_shadow_3{sfx}.tsv'), ['n', 'id', 'path', 'bucket', 'arm', 'guess', 'ruling', 'hit', 'checkpoint'], trace)
json.dump(summary, open(os.path.join(INV, 'automation', 'sweeps', f'echo_shadow_3{sfx}.json'), 'w'), indent=1, ensure_ascii=False)
wf = sum(1 for r in rows if WF.search(r['path']))
print(f'automation rows {len(rows)} ({wf} workflows); glossary {n_gl}; registries {n_reg}')
print('secrets named:', sorted({s for r in rows for s in r['secret_names'].split(', ') if s}))
print('echo:', json.dumps(summary, ensure_ascii=False))
