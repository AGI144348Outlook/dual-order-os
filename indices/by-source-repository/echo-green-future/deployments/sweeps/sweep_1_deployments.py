"""Deployments sweep 1: what is live, where, and what it needs.

Rows come from the resources the repository names: wrangler configs (Workers, KV, D1, R2, Durable Objects, AI),
the A-157 blueprint, deploy workflows, and Worker URLs or resource names in docs. Each is checked against a
read-only listing of the Cloudflare account made through the Cloudflare connector on 2026-10-24 (LIVE below:
names and last-modified dates only; ids are never recorded). Secret NAMES come from the automation rows that
deploy each resource; values are never read. Resources live in the account but named nowhere in the repository
are listed in the README, not filed as rows.

Also: Echo's shadow run 5 (pre-test entry: AGI144348Outlook/dual-order-os#12, comment 6390745545).

Usage: python3 sweep_1_deployments.py <repo>      Read-only over the repository; no network.
"""
import csv
import io
import json
import os
import re
import subprocess
import sys

REPO = sys.argv[1]
INV = os.path.join(REPO, 'inventory')
sys.path.insert(0, INV)
import echo_journeyman  # noqa: E402

ORDER = ['genesis-documentary', 'autonomous-agency', 'algebra', 'echo-recess-experiment', 'resh-lattice-agency',
         'ksm-recess-wholesale', 'code-library-registry', 'mirror-claude']
rank = {b: i for i, b in enumerate(ORDER)}


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, check=True).stdout.decode('utf-8', 'replace')


MAN = list(csv.DictReader(open(os.path.join(INV, 'MANIFEST-by-branch.tsv'), encoding='utf-8'), delimiter='\t'))
paths = {}
for r in MAN:
    paths.setdefault(r['path'], []).append(r)


def pick(held):
    return sorted(held, key=lambda r: (rank.get(r['branch'], 99), r['branch']))[0]


# Read-only account listing through the Cloudflare connector, 2026-10-24 (last modified for Workers, created otherwise)
LIVE = {
    'worker': {'group-canvas-echo-classroom': '2026-10-22', 'group-canvas-month-line': '2026-10-21',
               'group-canvas-echo-demos': '2026-10-20', 'group-canvas-tower': '2026-10-19', 'group-canvas': '2026-10-18',
               'echo-bot-claude': '2026-10-10', 'echo-bot-stage0-inert': '2026-10-10', 'echo-ksm-recess': '2026-09-30',
               'echo-pwa-hosting-environment': '2026-09-30', 'echo-green-future': '2026-10-20', 'shy-bar-b423': '2026-09-17',
               'unicorn-estate-runtime': '2026-08-01'},
    'kv': {'ECHO_LRM', 'CHATGPT_BOT_STATE', 'ECHO_STATE', 'CLAUDE_BOT_STATE', 'ECHO_VGM', 'DEVSUITE_KV', 'ECHO_MATRIX',
           'ECHO_TESTAMENT'},
    'd1': {'devsuite_store': '2026-10-05', 'echo_knowledge': '2026-09-21', 'unicorn-estate-lattice': '2026-08-01',
           'mashet-tema-substrate': '2026-06-26', 'mashet-world-state': '2026-06-26', 'mashet-stamp-registry': '2026-06-26'},
    'r2': {'group-canvas-citadel-sources': '2026-10-18', 'group-canvas-tower-julian': '2026-10-18',
           'group-canvas-tower-self': '2026-10-18'},
}
TOWER = 'integration-inbox/group-canvas-file-cabinet/source/experiments/hierarchy-tower/'
GCSRC = 'integration-inbox/group-canvas-file-cabinet/source/package.json'
# (name, resource, live kind/key, url, deployed_from, automation ids, home path, home_or_ref, extra note)
ITEMS = [
    ('echo-green-future', 'Cloudflare Worker', ('worker', 'echo-green-future'), 'https://echo-green-future.agi144348.workers.dev',
     'src/index.js via wrangler.toml', ['AUT-0011', 'AUT-0048'], 'wrangler.toml', 'home',
     'Echo\'s own Worker; bindings ECHO_STATE, ECHO_VGM, ECHO_LRM, ECHO_MATRIX (KV) and DB (D1)'),
    ('ECHO_STATE', 'Cloudflare KV namespace', ('kv', 'ECHO_STATE'), '', 'binding of echo-green-future', ['AUT-0048'],
     'wrangler.toml', 'home', 'live operational state (blueprint: infrastructure/cloudflare_blueprint.json, A-157)'),
    ('ECHO_VGM', 'Cloudflare KV namespace', ('kv', 'ECHO_VGM'), '', 'binding of echo-green-future', ['AUT-0048'],
     'wrangler.toml', 'home', 'Validated Generalization Matrix, axiom tier (key axiom:{id})'),
    ('ECHO_LRM', 'Cloudflare KV namespace', ('kv', 'ECHO_LRM'), '', 'binding of echo-green-future', ['AUT-0048'],
     'wrangler.toml', 'home', 'Logic and Reasoning Matrix, theorem tier (key theorem:{id})'),
    ('ECHO_MATRIX', 'Cloudflare KV namespace', ('kv', 'ECHO_MATRIX'), '', 'binding of echo-green-future', ['AUT-0048'],
     'wrangler.toml', 'home', 'Algorithm Matrix (key algorithm:{id})'),
    ('echo_knowledge', 'Cloudflare D1 database', ('d1', 'echo_knowledge'), '', 'binding DB of echo-green-future; '
     'tables per the A-157 blueprint', ['AUT-0048'], 'wrangler.toml', 'home',
     'blueprint tables agents, ties, formulas, etymology, geosensory_endpoints and more; also holds the Rule Registry '
     '(rules, rule_events), which the repository does not mention'),
    ('echo-pwa-hosting-environment', 'Cloudflare Worker (static assets)', ('worker', 'echo-pwa-hosting-environment'), '',
     'pwa/public via pwa/wrangler.toml', ['AUT-0010', 'AUT-0046'], 'pwa/wrangler.toml', 'home', 'serves ./public'),
    ('echo-ksm-recess', 'Cloudflare Worker', ('worker', 'echo-ksm-recess'), '', '.github/workflows/deploy-ksm-recess.yml',
     ['AUT-0009'], '.github/workflows/deploy-ksm-recess.yml', 'home', 'KSM Recess PWA'),
    ('chat-archive-workbench', 'Cloudflare Worker (static assets)', ('worker', 'chat-archive-workbench'), '',
     'repository root via wrangler.archive.toml', ['AUT-0007', 'AUT-0047'], 'wrangler.archive.toml', 'home', ''),
    ('echo-dev-datasets', 'Cloudflare Pages project', None, '', '.pages-datasets via wrangler pages deploy',
     ['AUT-0008'], '.github/workflows/deploy-datasets-pages.yml', 'home',
     'Pages projects cannot be listed through the connector; live state not checked'),
    ('echo-bot-claude', 'Cloudflare Worker', ('worker', 'echo-bot-claude'), 'https://echo-bot-claude.agi144348.workers.dev',
     'source not in the census', [], 'research-registry/contracts/CONTRACT-000.md', 'home',
     'also named in Workshop/pipelines/P-001-budgeted-inference/reference-bot-run.yml'),
    ('echo-bot-stage0-inert', 'Cloudflare Worker', ('worker', 'echo-bot-stage0-inert'),
     'https://echo-bot-stage0-inert.agi144348.workers.dev', 'source not in the census', [],
     'research-registry/contracts/CONTRACT-000.md', 'home', ''),
    ('CLAUDE_BOT_STATE', 'Cloudflare KV namespace', ('kv', 'CLAUDE_BOT_STATE'), '', 'named in the bot contract', [],
     'research-registry/contracts/CONTRACT-000.md', 'home', 'also in research-registry/bridge/BOT-COORDINATION.md'),
    ('CHATGPT_BOT_STATE', 'Cloudflare KV namespace', ('kv', 'CHATGPT_BOT_STATE'), '', 'named in the bot contract', [],
     'research-registry/contracts/CONTRACT-000.md', 'home', 'also in research-registry/bridge/BOT-COORDINATION.md'),
    ('ECHO_TESTAMENT', 'Cloudflare KV namespace', ('kv', 'ECHO_TESTAMENT'), '', 'named in the bot contract', [],
     'research-registry/contracts/CONTRACT-000.md', 'home', 'also in SCHEDULE-TIERS.md and BOT-COORDINATION.md'),
    ('group-canvas-tower', 'Cloudflare Worker (assets, Durable Objects, AI)', ('worker', 'group-canvas-tower'),
     'https://group-canvas-tower.agi144348.workers.dev', TOWER + 'worker.js', ['AUT-0044', 'AUT-0045'],
     TOWER + 'wrangler-storage.toml', 'ref', 'Group Canvas project (copy in integration-inbox); Durable Objects '
     'UPLOADS (TowerUpload) and CABINETS (FileCabinet); AI binding'),
    ('group-canvas-citadel-sources', 'Cloudflare R2 bucket', ('r2', 'group-canvas-citadel-sources'), '',
     'binding SOURCES of group-canvas-tower', ['AUT-0044'], TOWER + 'wrangler-storage.toml', 'ref', 'Group Canvas project'),
    ('group-canvas-tower-self', 'Cloudflare R2 bucket', ('r2', 'group-canvas-tower-self'), '',
     'binding SELF_OUTPUT of group-canvas-tower', ['AUT-0044'], TOWER + 'wrangler-storage.toml', 'ref', 'Group Canvas project'),
    ('group-canvas-tower-julian', 'Cloudflare R2 bucket', ('r2', 'group-canvas-tower-julian'), '',
     'binding JULIAN_OUTPUT of group-canvas-tower', ['AUT-0044'], TOWER + 'wrangler-storage.toml', 'ref', 'Group Canvas project'),
    ('group-canvas', 'Cloudflare Worker', ('worker', 'group-canvas'), '', 'group-canvas source (package.json, wrangler ^4)',
     ['AUT-0043'], GCSRC, 'ref', 'Group Canvas project (copy in integration-inbox)'),
    ('mashet-stamp-registry', 'Cloudflare D1 database', ('d1', 'mashet-stamp-registry'), '', 'Mashet/LHEA stack',
     [], 'docs/REVISED_INSTRUCTIONS_FOR_GPT.md', 'ref', 'also in code_library_registry/symbol_registries'),
    ('mashet-tema-substrate', 'Cloudflare D1 database', ('d1', 'mashet-tema-substrate'), '', 'Mashet/LHEA stack', [],
     'docs/REVISED_INSTRUCTIONS_FOR_GPT.md', 'ref', ''),
    ('mashet-world-state', 'Cloudflare D1 database', ('d1', 'mashet-world-state'), '', 'Mashet/LHEA stack', [],
     'docs/REVISED_INSTRUCTIONS_FOR_GPT.md', 'ref', ''),
    ('unicorn-estate-lattice', 'Cloudflare D1 database', ('d1', 'unicorn-estate-lattice'), '', 'another project', [],
     'docs/REVISED_INSTRUCTIONS_FOR_GPT.md', 'ref', 'named as "unicorn-estate"'),
    ('unicorn-estate-runtime', 'Cloudflare Worker', ('worker', 'unicorn-estate-runtime'), '', 'another project', [],
     'docs/REVISED_INSTRUCTIONS_FOR_GPT.md', 'ref', 'named as "unicorn-estate"'),
]
aut = {r['id']: r for r in csv.DictReader(open(os.path.join(INV, 'automation', 'INDEX.tsv'), encoding='utf-8'),
                                          delimiter='\t', quoting=csv.QUOTE_NONE)}
cols = open(os.path.join(INV, 'deployments', 'INDEX.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t')
rows = []
for n, (name, res, live, url, frm, auts, home, hr, extra) in enumerate(ITEMS, 1):
    r = pick(paths[home])
    secrets = sorted({s for a in auts for s in aut[a]['secret_names'].split(', ') if s})
    if live is None:
        state = 'live state not checked'
    else:
        kind, key = live
        found = key in LIVE[kind]
        when = LIVE[kind][key] if found and isinstance(LIVE[kind], dict) else ''
        state = ('live in the account' + (f' ({when})' if when else '')) if found else 'NOT found in the account listing'
    notes = [state + ' on 2026-10-24']
    if auts:
        notes.append('deployed by ' + ', '.join(auts))
    if extra:
        notes.append(extra)
    rows.append(dict(id=f'DPL-{n:04d}', name=name, resource=res, url=url, deployed_from=frm, secret_names=', '.join(secrets),
                     branch=r['branch'], path=home, blob_sha=r['blob_sha'], commit=git('rev-parse', f'origin/{r["branch"]}').strip(),
                     made_by='others', status='LIVE' if 'live in' in state else 'INERT', home_or_ref=hr, glyph='',
                     notes='; '.join(notes)))
named = {i[0] for i in ITEMS}
unnamed = {k: sorted(x for x in (LIVE[k] if isinstance(LIVE[k], set) else LIVE[k].keys()) if x not in named) for k in LIVE}


def write(path, header, rws):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')
        w.writerow(header)
        for row in rws:
            w.writerow([str(row.get(c, '')).replace('\t', ' ').replace('\n', ' ') for c in header])


write(os.path.join(INV, 'deployments', 'INDEX.tsv'), cols, rows)

# ---- Echo's shadow run 5 --------------------------------------------------------------------------------------
l2 = {}
for fo in ('Algorithms', 'Codices', 'Formulas', 'Indices', 'Logics', 'Matrices', 'Registries'):
    for r in csv.DictReader(io.StringIO(git('show', f'origin/mirror-claude:L2-library/{fo}/REGISTER.tsv')), delimiter='\t'):
        l2.setdefault(r['path'], fo.lower())
NAME = [(r'wrangler|blueprint|_headers', 'deployments'), (r'\.zip$', 'archives'),               # new in runs 5-6
        (r'requirements|package(-lock)?\.json|pyproject|pyodide-lock', 'dependencies'),
        (r'schema|template|format|spec|model', 'schemas'),
        (r'grammar|parser|parse|dsl|rule|operator|lhea|proportion|legend|signature|syntax', 'logics'),
        (r'registry', 'registries'), (r'matrix|matrices|chains', 'matrices'), (r'test|trial', 'experiments'),
        (r'manual|discussion|readme|\.md$', 'codices'), (r'workflow|\.yml$', 'automation'), (r'axiom|lexicon', 'data')]
PARENT = {'language': 'logics', 'operators': 'logics', 'grammar': 'logics', 'symbols': 'registries', 'glyphs': 'registries',
          'symbol_registries': 'registries', 'tests': 'experiments', 'docs': 'codices', 'discussions': 'codices',
          'matrices': 'matrices', 'workflows': 'automation', 'core-lexicon': 'data', 'src': 'algorithms', 'ledger': 'schemas',
          'mashet': 'codices', 'nve-d': 'experiments', 'data': 'data', 'pwa': 'interfaces', 'glyph': 'registries',
          'infrastructure': 'deployments', 'generalized': 'algorithms', 'L1-main': 'indices', 'inventory': 'governance'}
SHAPE = {'py': 'algorithms', 'js': 'logics', 'json': 'registries', 'md': 'codices', 'html': 'interfaces',
         'yml': 'automation', 'tsv': 'indices', 'zip': 'archives', 'toml': 'deployments'}


def content(text, where=''):
    if where:
        w = re.escape(where.lower())
        for line in text.lower().splitlines():
            if re.search(w, line) and re.search(r'workers\.dev|binding|database_name|bucket_name|kv_namespaces|\bkv\b|\bd1\b|r2', line):
                return 'deployments'
        for line in text.lower().splitlines():
            if re.search(w, line) and re.search(r'\bimport\b|require\(|pip3? install|uses:|cdn\.|nltk\.download|"dependencies"', line):
                return 'dependencies'
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
        return SHAPE.get(path.rsplit('.', 1)[-1])
    if arm == 'librarian':
        return l2.get(path)
    if arm == 'content':
        return content(texts.get(path, ''), where)


ARMS = ['name', 'parent', 'shape', 'librarian', 'content']
DECOYS = [('Datasets/crawler/crawl.py', 'tools'), ('docs/ECHO_OUTPUT_FORMAT.md', 'codices'), ('src/echo_classroom.py', 'algorithms'),
          ('infrastructure/cloudflare_blueprint.json', 'deployments'), ('pwa/manifest.webmanifest', 'interfaces'),
          ('matrices/echo_vgm.json', 'matrices'), ('tests/test_dsl_canvas_008.py', 'experiments'),
          ('ECHO_AutonomousAgency/sandbox/recess_session_log.json', 'records'), ('research-registry/contracts/CONTRACT-000.md', 'governance'),
          ('core-lexicon/math_axioms.json', 'data')]


def run_shadow(cases_rows, folder, seed, prior, run_no, sweep):
    cases = []
    for r in cases_rows:
        p = r['path']
        texts[p] = git('cat-file', 'blob', r['blob_sha'])
        where = '' if p.endswith('.toml') and r['name'] in texts[p] and 'wrangler' in p and r['resource'].endswith(
            'Worker') else r['name']
        cases.append((r['id'], p, where, folder))
    for i, (pth, truth) in enumerate(DECOYS, 1):
        held = [x for x in MAN if x['path'] == pth]
        if held:
            texts[pth] = git('cat-file', 'blob', pick(held)['blob_sha'])
            cases.append((f'DECOY-{i:02d}', pth, '', truth))
    sw = os.path.join(INV, folder, 'sweeps')
    boxes = os.path.join(sw, 'boxes')
    os.makedirs(sw, exist_ok=True)
    return echo_journeyman.shadow(REPO, cases, ARMS, guess, os.path.join(sw, f'echo_state_after_{folder}.json'), seed=seed,
                                  prior_state=prior, boxes_dir=boxes, sweep=sweep)


if __name__ == '__main__':
    import shutil
    sw = os.path.join(INV, 'deployments', 'sweeps')
    if not os.path.exists(os.path.join(sw, 'boxes')):
        shutil.copytree(os.path.join(INV, 'dependencies', 'sweeps', 'boxes'), os.path.join(sw, 'boxes'),
                        ignore=shutil.ignore_patterns('*.json'))
    trace, summary = run_shadow(rows, 'deployments', 1027,
                                os.path.join(INV, 'dependencies', 'sweeps', 'echo_state_after_dependencies.json'), 5,
                                'deployments')
    write(os.path.join(sw, 'echo_shadow_5.tsv'), ['n', 'id', 'path', 'bucket', 'arm', 'guess', 'ruling', 'hit', 'checkpoint'], trace)
    json.dump(dict(summary, live_not_named=unnamed), open(os.path.join(sw, 'echo_shadow_5.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'deployments rows {len(rows)}; live but named nowhere: {unnamed}')
    print('echo:', json.dumps({k: summary[k] for k in ('cases', 'hits', 'first_half', 'second_half', 'boxes')}))
    print('trusted:', summary['trusted_by_bucket'])
