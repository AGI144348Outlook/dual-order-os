"""Algorithms sweep: one row per algorithm, pointing at where it is implemented.

Sources (read-only):
  1. Echo's own registries: echo_algorithm_matrix.json (newest on autonomous-agency, older on
     genesis-documentary) and dev-suite genesis_structure.json  -> name, type, status, description
  2. Every .py / .js / .jsx / .mjs / .cjs file on every branch -> class/def definitions and A-number markers
  3. glyph_algorithm_index.json -> glyph ties
  4. code_library_registry/modules/MOD-* -> non-numbered algorithm modules
"""
import csv
import json
import re
import subprocess
import sys
from collections import defaultdict

REPO, OUT = sys.argv[1], sys.argv[2]
INV = json.load(open(sys.argv[3]))['summary']


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, check=True).stdout.decode('utf-8', 'replace')


def show(branch, path):
    try:
        return git('show', f'origin/{branch}:{path}')
    except subprocess.CalledProcessError:
        return None


# 1. registries -------------------------------------------------------------
reg = {}
for branch, path in [('genesis-documentary', 'matrices/echo_algorithm_matrix.json'),
                     ('autonomous-agency', 'ECHO_AutonomousAgency/matrices/echo_algorithm_matrix.json')]:
    for k, v in json.loads(show(branch, path)).items():
        reg[k] = dict(v, registry=f'{branch}:{path}')          # newer file overwrites older
struct = json.loads(show('dev-suite-algorithms', 'dev-suite/suite/src/data/genesis_structure.json'))['algs']
for a in struct:
    reg.setdefault(a['id'], dict(name=a['name'], status=a['status'], description=a['desc'], type='',
                                 registry='dev-suite-algorithms:dev-suite/suite/src/data/genesis_structure.json'))

# 3. glyph ties ---------------------------------------------------------------
glyph_of = defaultdict(list)
gi = json.loads(show('autonomous-agency', 'ECHO_AutonomousAgency/matrices/glyph_algorithm_index.json'))
for block in gi['blocks'].values():
    for t in block['algorithm_ties']:
        glyph_of[t['algorithm_id']].append(block['glyph'])

# 2. code definitions across all branches, deduped by blob -------------------------------
branches = sorted(INV)
pref = ['genesis-documentary', 'autonomous-agency', 'algebra', 'echo-recess-experiment', 'resh-lattice-agency']
order = pref + [b for b in branches if b not in pref]
CODE = re.compile(r'\.(py|js|jsx|mjs|cjs)$')
blob_seen = {}
defs = defaultdict(list)       # class/def name -> [(branch, path, line, blob)]
marks = defaultdict(list)      # A-id -> [(branch, path, line, enclosing_class, blob, kind)]
AID = re.compile(r'\bA-(\d{3})(-[A-Z]+)?\b')
for b in order:
    for line in git('ls-tree', '-r', f'origin/{b}').splitlines():
        meta, path = line.split('\t', 1)
        sha = meta.split()[2]
        if not CODE.search(path) or path.startswith('Datasets/') or 'pyodide' in path:
            continue
        if sha in blob_seen:
            blob_seen[sha]['branches'].add(b)
            continue
        blob_seen[sha] = dict(branch=b, path=path, branches={b})
        text = git('cat-file', 'blob', sha)
        cls, meth, last_def_line, last_def_name = None, None, -99, None
        pending = []   # (line, aid) header comments waiting for the next definition
        DEFN = re.compile(r'A-\d{3}(?:-[A-Z]+)?\s*[:—]')     # "A-158:" defines; "(A-101)" only refers
        for n, src in enumerate(text.splitlines(), 1):
            new_def = None
            m = re.match(r'\s*(?:export\s+)?class\s+([A-Za-z_]\w*)', src)
            if m:
                cls, meth = m.group(1), None
                new_def = cls
            m2 = re.match(r'(\s*)(?:async\s+)?(?:def|function)\s+([A-Za-z_]\w*)', src)
            if m2:
                if not m2.group(1):
                    cls, meth = None, m2.group(2)
                    new_def = m2.group(2)
                else:
                    meth = m2.group(2)
                    new_def = f'{cls}.{meth}' if cls else meth
            if new_def:
                defs[new_def].append((b, path, n, sha))
                last_def_line, last_def_name = n, new_def
                for (pn, paid) in pending:
                    if n - pn <= 3:
                        marks[paid].append(dict(b=b, path=path, n=n, sha=sha, header=new_def,
                                                named=None, near=None, inside=None))
                pending = []
            is_comment = src.lstrip().startswith(('#', '//'))
            for am in AID.finditer(src):
                aid = 'A-' + am.group(1) + (am.group(2) or '')
                cm = re.match(r'\s*#\s*A-\d{3}(?:-[A-Z]+)?\s*[:—-]\s*([A-Za-z_]\w*)', src)
                if is_comment and DEFN.search(src):
                    pending.append((n, aid))
                near = last_def_name if (0 < n - last_def_line <= 4 and DEFN.search(src)) else None
                marks[aid].append(dict(b=b, path=path, n=n, sha=sha, named=cm.group(1) if cm else None,
                                       near=near, header=None,
                                       inside=(f'{cls}.{meth}' if cls and meth else (cls or meth))))

# mentioned anywhere (docs, json, jsx) for ids that are only mentioned
mentions = defaultdict(set)
for line in open(sys.argv[4], encoding='utf-8', errors='replace'):
    try:
        b, rest = line.split('\t', 1)
    except ValueError:
        continue
    path = rest.split(':', 1)[0]
    for am in AID.finditer(rest):
        mentions['A-' + am.group(1) + (am.group(2) or '')].add((b, path))


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def locate(aid, name):
    """Best evidence first: name match, then a naming comment, then a docstring right under a
    definition; a mere mention inside a class or method is returned as weak."""
    rank = {b: i for i, b in enumerate(order)}
    tiers = []
    if aid in ('A-000', 'A-000-RESH'):
        h = sorted(defs['ReshIdentity'], key=lambda x: (rank[x[0]], x[1]))[0]
        where = 'ReshIdentity' if aid == 'A-000-RESH' else 'ReshIdentity (the Governor is the whole system; its identity check runs here)'
        return h[0], h[1], h[2], where, h[3], 'manual check'
    tiers.append(([(h, mk['named']) for mk in marks.get(aid, []) if mk['named'] in defs
                   for h in defs[mk['named']] if h[3] == mk['sha']], 'A-number comment naming it'))
    tiers.append(([((mk['b'], mk['path'], mk['n'], mk['sha']), mk['header']) for mk in marks.get(aid, []) if mk.get('header')],
                  'header comment above the definition'))
    hits = []
    if name:
        key = norm(name.split('—')[0].split('(')[0].split('+')[0])
        hits = [(h, dn) for dn, hs in defs.items() if norm(dn.split('.')[-1]) == key for h in hs]
    marked_files = {mk['sha'] for mk in marks.get(aid, [])}
    tiers.append(([(h, dn) for h, dn in hits if h[3] in marked_files], 'name match, A-number in the same file'))
    tiers.append(([(h, mk['near']) for mk in marks.get(aid, []) if mk['near']
                   for h in defs[mk['near']] if h[3] == mk['sha'] and h[2] <= mk['n']], 'docstring under the definition'))
    tiers.append(([(h, dn) for h, dn in hits], 'WEAK: name match only'))
    tiers.append(([((mk['b'], mk['path'], mk['n'], mk['sha']), f"mentioned inside {mk['inside']}") for mk in marks.get(aid, []) if mk['inside']],
                  'WEAK: only mentioned inside'))
    for cands, how in tiers:
        if cands:
            cands.sort(key=lambda c: (rank[c[0][0]], c[0][1], c[0][2]))
            (b, path, n, sha), where = cands[0]
            if how.startswith('header'):
                # first definition under a section header may belong to another A-number
                # (its own docstring says so); then take the next definition in the file
                owners = {other for other, mks in marks.items() if other != aid
                          for mk in mks if mk.get('near') == where and mk['sha'] == sha}
                mine = any(mk.get('near') == where and mk['sha'] == sha for mk in marks.get(aid, []))
                if owners and not mine:
                    later = sorted((h[2], dn) for dn, hs in defs.items() for h in hs if h[3] == sha and h[2] > n)
                    if later:
                        n, where = later[0]
                        how = 'header comment above the section (first definition belongs to ' + ', '.join(sorted(owners)) + ')'
            return b, path, n, where, sha, how
    return None


ids = set(reg) | set(marks) | set(mentions)
def sortkey(a):
    m = re.match(r'A-(\d{3})(.*)', a)
    return (int(m.group(1)), m.group(2)) if m else (9999, a)

cols = open(f'{OUT}/INDEX.tsv').readline().rstrip('\n').split('\t')
rows = []
for aid in sorted(ids, key=sortkey):
    r = reg.get(aid, {})
    name = r.get('name', '')
    loc = locate(aid, name)
    glyphs = glyph_of.get(aid, [])
    num = re.match(r'A-(\d{3})(.*)', aid)
    row = dict(id=f'ALG-{int(num.group(1)):04d}{num.group(2)}', name=name or '(unnamed in registries)',
               algorithm_id=aid, state_in_code=r.get('status', ''), status='INERT', home_or_ref='home',
               made_by='unknown', glyph=';'.join(glyphs), depends_on='', introduced_in='')
    notes = []
    if r.get('type'):
        notes.append(f"type {r['type']}")
    if loc:
        b, path, n, where, sha, how = loc
        row.update(branch=b, path=path, blob_sha=sha, commit=git('rev-parse', f'origin/{b}').strip(),
                   location=f'{where} (line {n})')
        if how.startswith('WEAK'):
            notes.append('implementation not pinned down')
        others = len(blob_seen[sha]['branches']) - 1
        notes.append(f'located by {how}')
        if others:
            notes.append(f'same file in {others} other branches')
    else:
        where = sorted(mentions.get(aid, set()))
        if where:
            row.update(branch=where[0][0], path=where[0][1], commit=git('rev-parse', f'origin/{where[0][0]}').strip())
        row['location'] = 'not found in code'
        notes.append(f'mentioned in {len(where)} files' + (', registry only' if r and not where else ''))
    if not r:
        notes.append('absent from the algorithm registries')
    if r.get('description'):
        notes.append('registry: ' + re.sub(r'\s+', ' ', r['description'])[:160])
    row['notes'] = '; '.join(notes)
    rows.append(row)

# 4. MOD modules ---------------------------------------------------------------
for line in git('ls-tree', '-d', '--name-only', 'origin/code-library-registry', 'code_library_registry/modules/').splitlines():
    mod = line.rsplit('/', 1)[-1]
    num = re.match(r'MOD-(\d{4})(?:-(.*))?', mod)
    rows.append(dict(id=f'ALG-MOD-{num.group(1)}', name=(num.group(2) or mod).replace('-', ' '), algorithm_id=mod,
                     location='module folder', state_in_code='', branch='code-library-registry', path=line + '/',
                     commit=git('rev-parse', 'origin/code-library-registry').strip(), status='INERT',
                     home_or_ref='home', made_by='unknown', notes='code library module; contents to be read'))

with open(f'{OUT}/INDEX.tsv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(c, '') for c in cols])

found = sum(1 for r in rows if r.get('location') not in ('not found in code', 'module folder'))
print(len(rows), 'rows;', found, 'located in code;',
      sum(1 for r in rows if r.get('location') == 'not found in code'), 'not found in code;',
      sum(1 for r in rows if r['id'].startswith('ALG-MOD')), 'modules')
