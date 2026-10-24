"""Dependencies sweep 1: the outside things Echo relies on, with their licences.

One row per outside thing, found where the repository names it:
  - Python imports that are not the standard library and not Echo's own modules
  - JavaScript imports and `require`s of packages; Pyodide loaded from the jsDelivr CDN or vendored
  - `pip install` lines and `actions/setup-python` versions in workflows; GitHub Actions used (`uses:`)
  - package.json dependencies; NLTK data downloaded (`nltk.download`); Google Fonts families
  - web services and data sources whose URLs appear in code (API calls, and the kernel's source catalogue)
Each row's path is its home: the file that declares it (package.json, the vendored lock, the first workflow that
installs it) or else the first file that uses it, by preferred branch. `used_by` holds the inventory ids of rows
already filed elsewhere whose files use it. Licences are as stated by PyPI, npm, the NLTK data index or the
project's LICENSE file for the LATEST release, read 2026-10-24 (not necessarily the version in use).

Also: glossary terms met on the way, and Echo's shadow run 4 with the ת/ק boxes on from the start
(pre-test entry: AGI144348Outlook/dual-order-os#12, comment of 2026-10-24).

Usage: python3 sweep_1_dependencies.py <repo>      Read-only over the repository; network not used.
"""
import csv
import io
import json
import os
import re
import shutil
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


def path_key(p):
    return (rank.get(pick(paths[p])['branch'], 99), p)


CODE = re.compile(r'\.(py|js|mjs|cjs|jsx|html|ya?ml|toml|sh)$|(^|/)package\.json$')
VENDORED = 'core-lexicon/pyodide/'
texts = {}
for p in sorted(paths):
    if CODE.search(p) and not p.startswith(VENDORED):
        texts[p] = git('cat-file', 'blob', pick(paths[p])['blob_sha'])
LOCK = 'core-lexicon/pyodide/pyodide-lock.json'
lock = json.loads(git('cat-file', 'blob', pick(paths[LOCK])['blob_sha']))

STD = set(sys.stdlib_module_names)
LOCAL = set()
for p in paths:
    for part in p.split('/'):
        LOCAL.add(part.rsplit('.', 1)[0])
PYODIDE_MODULES = {'js', 'pyodide', 'micropip', 'pyodide_js'}

deps = {}      # key -> dict(name, kind, versions:set, evidence:set, home, licence, notes:list)


def dep(key, name, kind, licence='', note=''):
    d = deps.setdefault(key, dict(name=name, kind=kind, versions=set(), evidence=set(), home=None,
                                  licence=licence, notes=[]))
    if note and note not in d['notes']:
        d['notes'].append(note)
    return d


LIC = {  # stated licence, and where it was read (latest release, 2026-10-24)
    'nltk': 'Apache-2.0 (PyPI)', 'scipy': 'BSD-3-Clause (PyPI licence text)',
    'numpy': 'BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 (PyPI)', 'sympy': 'BSD (PyPI)',
    'requests': 'Apache-2.0 (PyPI)', 'pytest': 'MIT (PyPI)', 'lemminflect': 'MIT (PyPI classifier)',
    'pikepdf': 'MPL-2.0 (PyPI)', 'react': 'MIT (npm)', 'playwright': 'Apache-2.0 (npm)', 'pyodide': 'MPL-2.0 (npm)',
    'wrangler': 'MIT OR Apache-2.0 (npm)', 'python': 'PSF-2.0 (CPython LICENSE)', 'node': 'MIT (Node.js LICENSE)',
    'actions/checkout': 'MIT (LICENSE)', 'actions/setup-python': 'MIT (LICENSE)', 'actions/upload-artifact': 'MIT (LICENSE)',
    'actions/setup-node': 'MIT (LICENSE)', 'cloudflare/wrangler-action': 'MIT OR Apache-2.0 (package.json)',
    'wordnet': 'WordNet 3.0 licence: use, copy, modify and distribute without fee, keeping the Princeton copyright '
               'notice and disclaimer on all copies (NLTK data index)',
    'omw-1.4': 'per wordnet: consult each wordnet\'s LICENSE; all permit redistribution (NLTK data index)',
    'font': 'OFL-1.1 (google/fonts OFL.txt)',
}
DIST = {'yaml': 'PyYAML', 'bs4': 'beautifulsoup4', 'PIL': 'Pillow', 'sklearn': 'scikit-learn', 'cv2': 'opencv-python'}

for p, t in texts.items():
    if p.endswith('.py'):
        for m in re.finditer(r'^\s*(?:from\s+([A-Za-z_][\w.]*)\s+import|import\s+([A-Za-z_][\w.]*(?:\s*,\s*[A-Za-z_][\w.]*)*))', t, re.M):
            names = [m.group(1)] if m.group(1) else [x.strip() for x in m.group(2).split(',')]
            for n in names:
                top = n.split('.')[0]
                if top in PYODIDE_MODULES:
                    dep('rt:pyodide', 'Pyodide', 'runtime')['evidence'].add(p)
                elif top and top not in STD and top not in LOCAL:
                    if top in ('wiki_crawler', 'governor_exchange'):
                        continue      # Echo's own modules, absent from the census (noted in the README)
                    dist = DIST.get(top, top)
                    dep('py:' + dist, dist, 'python library', LIC.get(dist, ''))['evidence'].add(p)
    if re.search(r'\.(m?js|cjs|jsx|html)$', p):
        for m in re.finditer(r'''(?:from\s+|require\(\s*|import\(\s*)['"]([^'"./][^'"]*)['"]''', t):
            pk = m.group(1)
            if pk.startswith('node:') or pk in ('fs', 'path', 'vm', 'assert'):
                dep('rt:node', 'Node.js', 'runtime', LIC['node'])['evidence'].add(p)
            elif not pk.startswith('echo.'):
                dep('js:' + pk, pk, 'javascript library', LIC.get(pk, ''))['evidence'].add(p)
    for m in re.finditer(r'cdn\.jsdelivr\.net/(?:npm/pyodide@|pyodide/v)([\d.]+)', t):
        d = dep('rt:pyodide', 'Pyodide', 'runtime', LIC['pyodide'])
        d['versions'].add(m.group(1))
        d['evidence'].add(p)
    if 'cdn.jsdelivr.net/pyodide/v' in t or 'pyodide@$' in t:
        dep('rt:pyodide', 'Pyodide', 'runtime', LIC['pyodide'])['evidence'].add(p)
    for m in re.finditer(r'pip3?\s+install\s+([^\n&|;]+)', t):
        for tok in m.group(1).split():
            if tok.startswith('-') or not re.match(r'^[A-Za-z][\w.-]*$', tok):
                continue
            d = dep('py:' + tok, tok, 'python library', LIC.get(tok, ''))
            d['evidence'].add(p)
            if d['home'] is None or path_key(p) < path_key(d['home']):
                d['home'] = p
    for m in re.finditer(r'uses:\s*([\w.-]+/[\w.-]+)(?:/[\w./-]+)?@(\S+)', t):
        d = dep('act:' + m.group(1), m.group(1), 'GitHub Action', LIC.get(m.group(1), ''))
        d['versions'].add(m.group(2))
        d['evidence'].add(p)
    for m in re.finditer(r'python-version:\s*[\'"]?([\d.x]+)', t):
        d = dep('rt:python', 'Python', 'runtime', LIC['python'])
        d['versions'].add(m.group(1))
        d['evidence'].add(p)
    for m in re.finditer(r'nltk\.download\(\s*[\'"]([\w.-]+)', t):
        corp = {'omw-1': 'omw-1.4'}.get(m.group(1), m.group(1))
        nm = {'wordnet': 'WordNet', 'omw-1.4': 'Open Multilingual Wordnet'}.get(corp, corp)
        d = dep('data:' + corp, nm, 'data (corpus, via NLTK)', LIC.get(corp, ''))
        d['evidence'].add(p)
        if corp == 'wordnet':
            d['versions'].add('3.0')
    for m in re.finditer(r'fonts\.googleapis\.com/css2?\?family=([^"\'&\s:]+)', t):
        fam = m.group(1).replace('+', ' ')
        dep('font:' + fam, fam + ' (Google Fonts)', 'font', LIC['font'],
            'loaded from fonts.googleapis.com')['evidence'].add(p)
    if p.endswith('package.json'):
        pj = json.loads(t)
        for sect in ('dependencies', 'devDependencies'):
            for pk, ver in (pj.get(sect) or {}).items():
                if pk == 'pyodide':
                    d = dep('rt:pyodide', 'Pyodide', 'runtime', LIC['pyodide'])
                else:
                    d = dep('js:' + pk, pk, 'javascript library' + (' (dev)' if sect == 'devDependencies' else ''),
                            LIC.get(pk, ''))
                d['versions'].add(ver)
                d['evidence'].add(p)
                d['home'] = d['home'] or p
        if (pj.get('engines') or {}).get('node'):
            d = dep('rt:node', 'Node.js', 'runtime', LIC['node'])
            d['versions'].add(pj['engines']['node'])
            d['evidence'].add(p)
            d['home'] = p

pyo = deps['rt:pyodide']
pyo['versions'].add(lock['info']['version'])
pyo['home'] = LOCK
pyo['evidence'].add(LOCK)
pyo['notes'].append(f"vendored copy {lock['info']['version']} in core-lexicon/pyodide (Python {lock['info']['python']}, "
                    f"{len(lock.get('packages', {}))} packages listed in its lock)")
deps['rt:python']['notes'].append(f"Python {lock['info']['python']} also runs inside the vendored Pyodide")

# web services and data sources named by URL in code
SERVICES = [  # host pattern, name, kind
    (r'services\.swpc\.noaa\.gov', 'NOAA Space Weather Prediction Center feeds', 'service (API)'),
    (r'earthquake\.usgs\.gov', 'USGS Earthquake Hazards feed', 'service (API)'),
    (r'geomag\.usgs\.gov', 'USGS Geomagnetism API', 'service (API)'),
    (r'api\.weather\.gov', 'US National Weather Service API', 'service (API)'),
    (r'api\.inaturalist\.org', 'iNaturalist API', 'service (API)'),
    (r'api\.nasa\.gov', 'NASA API (DONKI)', 'service (API)'),
    (r'service\.iris\.edu', 'IRIS (EarthScope) seismic web services', 'service (API)'),
    (r'imag-data\.bgs\.ac\.uk', 'British Geological Survey INTERMAGNET data', 'service (API)'),
    (r'api\.github\.com', 'GitHub REST API', 'service (API)'),
    (r'api\.cloudflare\.com', 'Cloudflare API', 'service (API)'),
    (r'api\.anthropic\.com', 'Anthropic API', 'service (API)'),
    (r'drivemcp\.googleapis\.com', 'Google Drive MCP endpoint', 'service (API)'),
    (r'api\.gsa\.gov|catalog\.data\.gov', 'data.gov catalog API (GSA)', 'service (API)'),
    (r'zenodo\.org', 'Zenodo records API', 'service (API)'),
    (r'huggingface\.co', 'Hugging Face datasets API', 'service (API)'),
    (r'scienceqa\.s3\.us-west-1\.amazonaws\.com', 'ScienceQA images (S3 download)', 'data source'),
    (r'kaikki\.org', 'Kaikki (Wiktionary extract)', 'data source (listed)'),
    (r'www\.gutenberg\.org', 'Project Gutenberg', 'data source (listed)'),
    (r'plato\.stanford\.edu', 'Stanford Encyclopedia of Philosophy', 'data source (listed)'),
    (r'mathworld\.wolfram\.com', 'Wolfram MathWorld', 'data source (listed)'),
    (r'physics\.nist\.gov', 'NIST CODATA constants table', 'data source (listed)'),
    (r'arxiv\.org', 'arXiv search', 'data source (listed)'),
    (r'en\.wikipedia\.org', 'Wikipedia', 'data source (listed)'),
    (r'en\.wiktionary\.org', 'Wiktionary', 'data source (listed)'),
    (r'raw\.githubusercontent\.com/Phylator', 'Phylator constants data (GitHub)', 'data source (listed)'),
    (r'raw\.githubusercontent\.com/data-poems/etymology-atlas|ETYMOLOGY_ATLAS', 'Etymology Atlas (GitHub)', 'data source (listed)'),
    (r'github\.com/bfo-ontology', 'Basic Formal Ontology (BFO)', 'data source (listed)'),
    (r'github\.com/appliedontogroup/dolce', 'DOLCE ontology', 'data source (listed)'),
]
for p, t in texts.items():
    for pat, name, kind in SERVICES:
        if re.search(r'https?://[^\s"\']*' + pat if not pat.isupper() else pat, t):
            note = 'terms of use to check; licence column left empty' if kind.startswith('service') else \
                'named as a source in the file; whether it is fetched was not checked' if 'listed' in kind else \
                'downloaded by a script; terms to check'
            dep('svc:' + name, name, kind, '', note)['evidence'].add(p)

# inventory ids by path, for used_by
ids_by_path = {}
for folder in sorted(os.listdir(INV)):
    idx = os.path.join(INV, folder, 'INDEX.tsv')
    if folder == 'dependencies' or not os.path.isfile(idx):
        continue
    for r in csv.DictReader(open(idx, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r.get('path'):
            ids_by_path.setdefault(r['path'], []).append(r['id'])

KIND_ORDER = ['runtime', 'python library', 'javascript library', 'javascript library (dev)', 'GitHub Action',
              'data (corpus, via NLTK)', 'font', 'service (API)', 'data source', 'data source (listed)']
cols = open(os.path.join(INV, 'dependencies', 'INDEX.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t')
rows, located, terms = [], {}, {}
ordered = sorted([d for d in deps.values() if d['evidence']], key=lambda d: (KIND_ORDER.index(d['kind']), d['name'].lower()))
for n, d in enumerate(ordered, 1):
    ev = sorted(d['evidence'], key=path_key)
    home = d['home'] or ev[0]
    r = pick(paths[home])
    branches = sorted({h['branch'] for e in ev for h in paths[e]})
    used = sorted({i for e in ev for i in ids_by_path.get(e, [])})
    notes = [f'named in {len(ev)} file' + ('s' if len(ev) != 1 else '') + f' on {len(branches)} branch' +
             ('es' if len(branches) != 1 else '')] + d['notes']
    if not d['versions'] and d['kind'] in ('python library', 'javascript library'):
        notes.append('version not pinned')
    if d['kind'] == 'python library' and home.startswith('.github/'):
        notes.append('installed by a workflow')
    iid = f'DEP-{n:04d}'
    located[iid] = dict(path=home, evidence=ev, kind=d['kind'], name=d['name'])
    rows.append(dict(id=iid, name=d['name'], kind=d['kind'], version=', '.join(sorted(d['versions'])),
                     licence=d['licence'], used_by=', '.join(used), branch=r['branch'], path=home,
                     blob_sha=r['blob_sha'], commit=git('rev-parse', f'origin/{r["branch"]}').strip(), made_by='others',
                     status='INERT', home_or_ref='home', glyph='', notes='; '.join(notes)))
    for t in re.findall(r'\b(Recess|KSM|NVE-D|DFE|Shakti|Swadesh|EVE|IVS|Hourglass|Presentiation|LHEA|Mashet|Lobby|DONKI)\b',
                        d['name'] + ' ' + home.replace('-', ' ')):
        terms.setdefault(t, iid)


def write(path, header, rws):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')
        w.writerow(header)
        for row in rws:
            w.writerow([str(row.get(c, '')).replace('\t', ' ').replace('\n', ' ') for c in header])


write(os.path.join(INV, 'dependencies', 'INDEX.tsv'), cols, rows)


def merge(folder, new):
    pth = os.path.join(INV, folder, 'INDEX.tsv')
    header = open(pth, encoding='utf-8').readline().rstrip('\n').split('\t')
    old = {r['id']: r for r in csv.DictReader(open(pth, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
    for r in new:
        old[r['id']] = {**old.get(r['id'], {}), **r}
    write(pth, header, [old[k] for k in sorted(old)])
    return len(old)


glo = {r['term']: r for r in csv.DictReader(open(os.path.join(INV, 'glossary', 'INDEX.tsv'), encoding='utf-8'),
                                            delimiter='\t', quoting=csv.QUOTE_NONE)}
nxt = max(int(r['id'][4:]) for r in glo.values()) + 1
new_terms = []
for t, iid in sorted(terms.items()):
    if t in glo:
        continue
    loc = located[iid]
    r = pick(paths[loc['path']])
    meaning = 'Database Of Notifications, Knowledge, Information: NASA space-weather event API' if t == 'DONKI' else ''
    new_terms.append(dict(id=f'GLO-{nxt:04d}', name=t, term=t, meaning=meaning, stated_by='NASA' if meaning else '',
                          first_seen=iid, variants='', branch=r['branch'], path=loc['path'], blob_sha=r['blob_sha'],
                          commit=git('rev-parse', f'origin/{r["branch"]}').strip(), made_by='unknown', status='INERT',
                          home_or_ref='home', notes='met in dependencies sweep 1'
                          + ('; meaning is NASA\'s published expansion, not stated in the file' if meaning else
                             '; meaning not stated; to be filled from its source document or by Timothy')))
    nxt += 1
n_gl = merge('glossary', new_terms)
n_reg = len(list(csv.DictReader(open(os.path.join(INV, 'registries', 'INDEX.tsv'), encoding='utf-8'), delimiter='\t',
                                quoting=csv.QUOTE_NONE)))

# ---- Echo's shadow run 4, with the ת and ק boxes on from the start ------------------------------------------
l2 = {}
for fo in ('Algorithms', 'Codices', 'Formulas', 'Indices', 'Logics', 'Matrices', 'Registries'):
    for r in csv.DictReader(io.StringIO(git('show', f'origin/mirror-claude:L2-library/{fo}/REGISTER.tsv')), delimiter='\t'):
        l2.setdefault(r['path'], fo.lower())
NAME = [(r'requirements|package(-lock)?\.json|pyproject|pyodide-lock', 'dependencies'),       # new in run 4
        (r'schema|template|format|spec|model', 'schemas'),
        (r'grammar|parser|parse|dsl|rule|operator|lhea|proportion|legend|signature|syntax', 'logics'),
        (r'registry', 'registries'), (r'matrix|matrices|chains', 'matrices'), (r'test|trial', 'experiments'),
        (r'manual|discussion|readme|\.md$', 'codices'), (r'workflow|\.yml$', 'automation'), (r'axiom|lexicon', 'data')]
PARENT = {'language': 'logics', 'operators': 'logics', 'grammar': 'logics', 'symbols': 'registries', 'glyphs': 'registries',
          'symbol_registries': 'registries', 'tests': 'experiments', 'docs': 'codices', 'discussions': 'codices',
          'matrices': 'matrices', 'workflows': 'automation', 'core-lexicon': 'data', 'src': 'algorithms', 'ledger': 'schemas',
          'mashet': 'codices', 'nve-d': 'experiments', 'data': 'data', 'pwa': 'interfaces', 'glyph': 'registries',
          'infrastructure': 'deployments', 'generalized': 'algorithms', 'L1-main': 'indices', 'inventory': 'governance'}


def names_dependency(text, where):
    """New in run 4: the in-file name appears in an import, require, CDN, install or download line."""
    w = re.escape(where.split(' ')[0].split('/')[-1].lower())
    for line in text.lower().splitlines():
        if re.search(r'\bimport\b|require\(|pip3? install|uses:|cdn\.|nltk\.download|"dependencies"|https?://', line) \
                and re.search(w, line):
            return True
    return False


def content(text, where=''):
    if where and names_dependency(text, where):
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
        return content(texts.get(path) or shadow_texts.get(path, ''), where)


ARMS = ['name', 'parent', 'shape', 'librarian', 'content']
shadow_texts = {LOCK: json.dumps(lock.get('info', {}))}
cases = []
for r in rows:
    p = r['path']
    declared = p.endswith('package.json') or p == LOCK
    where = '' if declared else r['name'].split(' (')[0]
    if r['kind'].startswith(('service', 'data source')):
        where = re.sub(r'[^a-z0-9]+', ' ', r['name'].lower()).split()[0]
        host = [pat for pat, nm, _ in SERVICES if nm == r['name']][0]
        where = re.sub(r'\\', '', host.split('|')[0]).split('/')[0]
    cases.append((r['id'], p, where, 'dependencies'))
DECOYS = [('Datasets/crawler/crawl.py', 'tools'), ('docs/ECHO_OUTPUT_FORMAT.md', 'codices'), ('src/echo_classroom.py', 'algorithms'),
          ('infrastructure/cloudflare_blueprint.json', 'deployments'), ('pwa/manifest.webmanifest', 'interfaces'),
          ('matrices/echo_vgm.json', 'matrices'), ('tests/test_dsl_canvas_008.py', 'experiments'),
          ('ECHO_AutonomousAgency/sandbox/recess_session_log.json', 'records'), ('research-registry/contracts/CONTRACT-000.md', 'governance'),
          ('core-lexicon/math_axioms.json', 'data')]
for i, (pth, truth) in enumerate(DECOYS, 1):
    held = [r for r in MAN if r['path'] == pth]
    if not held:
        continue
    shadow_texts[pth] = git('cat-file', 'blob', pick(held)['blob_sha'])
    cases.append((f'DECOY-{i:02d}', pth, '', truth))

SW = os.path.join(INV, 'dependencies', 'sweeps')
boxes = os.path.join(SW, 'boxes')
if not os.path.exists(boxes):                 # carry run 3's boxes forward (the replay copy stays as it was)
    shutil.copytree(os.path.join(INV, 'automation', 'sweeps', 'boxes_replay'), boxes,
                    ignore=shutil.ignore_patterns('*.json'))
trace, summary = echo_journeyman.shadow(REPO, cases, ARMS, guess, os.path.join(SW, 'echo_state_after_dependencies.json'),
                                       seed=1026,
                                       prior_state=os.path.join(INV, 'automation', 'sweeps', 'echo_state_after_automation_boxes.json'),
                                       boxes_dir=boxes, sweep='dependencies')
write(os.path.join(SW, 'echo_shadow_4.tsv'), ['n', 'id', 'path', 'bucket', 'arm', 'guess', 'ruling', 'hit', 'checkpoint'], trace)
json.dump(summary, open(os.path.join(SW, 'echo_shadow_4.json'), 'w'), indent=1, ensure_ascii=False)
by_kind = {}
for r in rows:
    by_kind[r['kind']] = by_kind.get(r['kind'], 0) + 1
print(f'dependencies rows {len(rows)}: {by_kind}; glossary {n_gl}; registries {n_reg}')
print('echo:', json.dumps(summary, ensure_ascii=False))
