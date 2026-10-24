"""Schemas sweep 1: the blank forms. What fields a kind of record must have.

Three kinds of row (`form` column):
  written   the schema exists as a document or a column header someone wrote down
  declared  a data file names its own schema id ("schema": "echo.x.v0.1"); fields are read from the file
  implied   no written form; fields are read from the code (dataclasses, returned dicts) or the data

Read-only over the repository. Field lists are extracted by the script, not typed by hand.
Writes inventory/schemas/INDEX.tsv, merges glossary and registries rows, and runs Echo's shadow
(continuing from his state after the logics sweep).

Usage: python3 sweep_1_schemas.py <repo>
"""
import ast
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


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, check=True).stdout.decode('utf-8', 'replace')


MAN = list(csv.DictReader(open(os.path.join(INV, 'MANIFEST-by-branch.tsv'), encoding='utf-8'), delimiter='\t'))


def locate(path, branch=None, find=None):
    held = [r for r in MAN if r['path'] == path]
    if branch == 'integration/echo-whole':        # the inventory's own files are not in the census
        sha = git('rev-parse', f'origin/{branch}:{path}').strip()
        held = [dict(branch=branch, path=path, blob_sha=sha)]
    if not held:
        raise SystemExit(f'not in census: {path}')
    if branch is None:
        rank = {b: i for i, b in enumerate(ORDER)}
        branch = sorted(held, key=lambda r: (rank.get(r['branch'], 99), r['branch']))[0]['branch']
    row = next(r for r in held if r['branch'] == branch)
    text = git('cat-file', 'blob', row['blob_sha'])
    line = ''
    if find:
        for n, src in enumerate(text.splitlines(), 1):
            if re.search(find, src):
                line = n
                break
        if not line:
            raise SystemExit(f'{find!r} not found in {path}')
    return dict(branch=branch, path=path, blob_sha=row['blob_sha'], commit=git('rev-parse', f'origin/{branch}').strip(),
                same=sum(1 for r in held if r['blob_sha'] == row['blob_sha']) - 1, line=line, text=text)


def short(fields, n=14):
    fields = list(dict.fromkeys(fields))
    return ', '.join(fields[:n]) + (f' (+{len(fields) - n} more)' if len(fields) > n else '')


rows, located = [], {}


def add(iid, name, form, describes, notation, fields, path, branch=None, find=None, glyph='', notes='', kind='home'):
    loc = locate(path, branch, find)
    located[iid] = loc
    n = notes + (f'; line {loc["line"]}' if loc['line'] else '') + (f'; same file in {loc["same"]} other branches' if loc['same'] else '')
    rows.append(dict(id=iid, name=name, form=form, describes=describes, notation=notation,
                     fields=fields(loc['text']) if callable(fields) else fields,
                     branch=loc['branch'], path=path, blob_sha=loc['blob_sha'], commit=loc['commit'], made_by='unknown',
                     status='INERT', home_or_ref=kind, glyph=glyph, notes=n.strip('; ')))


def md_table_fields(text):
    return [m.group(1) for m in re.finditer(r'^\|\s*`([^`]+)`\s*\|', text, re.M)]


def sql_columns(table):
    def f(text):
        m = re.search(r'CREATE TABLE IF NOT EXISTS ' + table + r' \((.*?)\);', json.loads(text)['migration_sql'], re.S)
        return [c.strip().split()[0] for c in m.group(1).split(',\n') if c.strip()]
    return f


def tsv_header(text):
    for line in text.splitlines():
        if line.startswith('# columns:'):
            return [c.strip().split()[0] for c in line.split(':', 1)[1].split('<TAB>')]
        if not line.startswith('#'):
            return line.split('\t')
    return []


# ---- written ---------------------------------------------------------------------------------------------
add('SCH-0001', 'Contract 000 manifest row', 'written', 'one file of a mirrored branch (Contract 000 Inert rule)', 'TSV',
    lambda t: tsv_header(t), 'L1-main/MANIFEST.tsv', 'mirror-claude', r'^# columns:', '',
    'rule stated in research-registry/contracts/CONTRACT-000.md: "every file of every branch is listed in a manifest (path, git blob fingerprint, size)", status INERT, KEPT, PRUNED or DEFERRED')
add('SCH-0002', 'L2 Library register row', 'written', 'one file placed in a Library sub-library (L2-library/*/REGISTER.tsv)', 'TSV',
    tsv_header, 'L2-library/Algorithms/REGISTER.tsv', 'mirror-claude', None, '', 'the earlier librarian\'s register; same header in all seven REGISTER.tsv files')
add('SCH-0003', 'Inventory index row', 'written', 'one row of any inventory/*/INDEX.tsv', 'Markdown table',
    lambda t: ['id', 'name', '(folder columns)'] + [f for f in md_table_fields(t.split('Shared columns', 1)[1].split('\n## ', 1)[0])
                                                    if f not in ('id', 'name')],
    'inventory/README.md', 'integration/echo-whole', r'^### Shared columns|^## Shared columns', '',
    'this inventory\'s own form; each folder README adds its own columns', kind='home')
rows[-1]['made_by'] = 'claude'
add('SCH-0004', 'Business ledger row', 'written', 'one transaction (stored privately; only the schema is public)', 'Markdown table',
    md_table_fields, 'Business/ledger/SCHEMA.md', None, None, '',
    'rules: amounts never estimated; a missing figure is recorded as missing; corrections are new reversing rows, never edits')
add('SCH-0005', 'Code library assessment template', 'written', 'one assessment of a code library artifact (CLR-XXXX)', 'Markdown headings',
    lambda t: [m.group(1) for m in re.finditer(r'^## (.+)$', t, re.M)], 'code_library_registry/ASSESSMENT_TEMPLATE.md', None, None, '',
    'a template: a schema with blanks to fill')
add('SCH-0006', 'ECHO output format', 'written', "ECHO's own responses: ## sections, [N] footnotes, timestamps", 'JSON example',
    lambda t: re.findall(r'"(## [^"]+)"', t), 'docs/ECHO_OUTPUT_FORMAT.md', None, None, '',
    'applies the Dual-Order structure to responses: sections read content-first, footnotes lookup-first')
for k, (table, describes) in enumerate([('agents', 'one word agent'), ('ties', 'one tie between two words'),
                                         ('formulas', 'one formula'), ('wordnet_chains', 'one WordNet chain'),
                                         ('etymology', 'one word\'s etymology'), ('geosensory_endpoints', 'one feed endpoint')], 7):
    add(f'SCH-{k:04d}', f'D1 table {table}', 'written', describes, 'SQL (D1)', sql_columns(table),
        'infrastructure/cloudflare_blueprint.json', None, None, '',
        'migration_sql in the blueprint A-157 DeploymentTranslator generates; not deployed (L2 register: deploy DEFERRED)')

# ---- declared schema ids -----------------------------------------------------------------------------------
DECLARED = {}
for r in MAN:
    if r['path'].endswith('.json') and not r['path'].startswith(('Datasets/', 'L2-library/')):
        DECLARED.setdefault(r['path'], r)


def json_fields(text):
    d = json.loads(text)
    top = [k for k in d if k != 'schema'] if isinstance(d, dict) else []
    best = None
    for k, v in (d.items() if isinstance(d, dict) else []):
        if isinstance(v, list) and v and isinstance(v[0], dict):
            if best is None or len(v) > len(best[1]):
                best = (k, v)
    if best:
        keys = list(dict.fromkeys(k for e in best[1] for k in e))
        return [f'{x}' for x in top if x != best[0]] + [f'{best[0]}[]: ' + short(keys, 10)]
    return top


seen_ids = {}
for path in sorted(DECLARED):
    try:
        d = json.loads(git('cat-file', 'blob', DECLARED[path]['blob_sha']))
    except (json.JSONDecodeError, subprocess.CalledProcessError):
        continue
    if isinstance(d, dict) and isinstance(d.get('schema'), str) and re.match(r'echo\.', d['schema']):
        seen_ids[d['schema']] = path
n = 13
for sid, path in sorted(seen_ids.items()):
    add(f'SCH-{n:04d}', sid, 'declared', path.rsplit('/', 1)[-1], 'JSON', json_fields, path, None, None, '',
        'the file names its schema id; no written definition of the id was found, so fields are read from the file')
    n += 1


# ---- implied from code ----------------------------------------------------------------------------------------
def dataclass_fields(classes):
    def f(text):
        tree = ast.parse(text)
        out = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name in classes:
                fs = [s.target.id for s in node.body if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]
                out.append(f'{node.name}({", ".join(fs)})')
        return out
    return f


CODE = [
    ('EMEL syntax tree', 'one EMEL statement as a typed tree', 'echo/language/ast.py', 'ksm-recess-wholesale',
     ['Term', 'Relation', 'Property', 'Proportion', 'Continued', 'Apply', 'Not', 'Join'], r'^class Term', 'פ',
     '"English, EMEL notation and Canvas are renderers of these nodes; none of them is the meaning"'),
    ('Governor request and state', "the Governor's State, Request and Context", 'src/echo_governor_skeleton.py', None,
     ['State', 'Request', 'Context'], r'^class State', 'ר', 'top of the kernel'),
    ('Plastic link', 'one neuroplastic link in the overlay', 'echo_neuroplasticity_overlay.py', None,
     ['PlasticLink'], r'^class PlasticLink', '', 'the overlay that wraps AlgorithmMatrix (neuroplasticity gate precedent)'),
    ('Matrix dictionary cells', 'custom matrices and their cells', 'ECHO_AutonomousAgency/src/echo_matrix_dictionary.py', None,
     ['CustomMatrix', 'MatrixCell'], r'^class CustomMatrix|^class MatrixCell', '', ''),
    ('Classroom exam item', 'one exam item', 'src/echo_classroom.py', None, ['ExamItem'], r'^class ExamItem', '', ''),
    ('Comprehension record', 'one comprehension audit record', 'src/echo_comprehension_audit.py', None, ['ComprehensionRecord'],
     r'^class ComprehensionRecord', '', ''),
    ('Homework event', 'one homework audit event', 'src/echo_homework_audit.py', None, ['HomeworkEvent'], r'^class HomeworkEvent', '', ''),
    ('Lexical entry (WordNet)', 'one lexical entry', 'src/echo_gf_wordnet.py', None, ['LexicalEntry'], r'^class LexicalEntry', '', ''),
    ('Sub-governor finding', 'one finding a sub-governor reports', 'src/echo_sub_governor.py', None, ['Finding'], r'^class Finding', 'ר', ''),
    ('EVE classroom lobby', 'a classroom lobby and its vocabulary neighbours', 'pwa/public/eve/classroom/lobby.py', None,
     ['EchoLobby', 'VocabularyNeighbor'], r'^class EchoLobby|^class VocabularyNeighbor', '', ''),
    ('Inert EVE', 'an inert EVE instance', 'pwa/public/eve/inert_eve.py', None, ['InertEVE'], r'^class InertEVE', '', ''),
    ('NVE-D configuration lab', 'nodes, links, budget and clock of an NVE-D configuration', 'experiments/nve-d/configuration_lab.py', None,
     ['Node', 'Link', 'Budget', 'Clock'], r'^class (Node|Link|Budget|Clock)\b', '', 'also writes schema ids nve-d-arm-v1 and nve-d-tested-set-v1'),
]
for name, describes, path, branch, classes, find, glyph, notes in CODE:
    add(f'SCH-{n:04d}', name, 'implied', describes, 'Python dataclasses', dataclass_fields(classes), path, branch, find, glyph, notes)
    n += 1
add(f'SCH-{n:04d}', 'Geosensory reading', 'implied', 'one feed reading turned into map points (schema_version 1)', 'Python dict',
    lambda t: ['schema_version', 'view', 'generated_at_ms', 'freshness', 'feed_age_ms', 'coverage', 'points[]: id, coordinates, value, quantity, unit, observed_at_ms, information_kind, value_status, source, lineage, label, review_status', 'rejected', 'source_url', 'persistence'],
    'src/geosensory_model.py', 'geosensory-crawler-experiment', r"'schema_version':1", '',
    'USGS GeoJSON to points; feed freshness kept separate from event age; "absence is not absence of earthquakes"')
n += 1
MODS = [('MOD-0001 verified resource gate', 'code_library_registry/modules/MOD-0001-verified-resource-gate/generalized/verified_resource_gate.py', ['ResourceSpec']),
        ('MOD-0002 bounded composition search', 'code_library_registry/modules/MOD-0002-bounded-composition-search/generalized/bounded_composition_search.py', ['SearchEvent', 'SearchResult']),
        ('MOD-0003 structured workspace', 'code_library_registry/modules/MOD-0003-structured-workspace-registry/generalized/structured_workspace.py', ['Collection', 'Item', 'Relation', 'IndexBinding']),
        ('MOD-0005 bounded affinity admission', 'code_library_registry/modules/MOD-0005-bounded-affinity-admission/generalized/bounded_affinity_admission.py', ['AdmissionDecision', 'CycleResult']),
        ('MOD-0006 static python flow outline', 'code_library_registry/modules/MOD-0006-static-python-flow-outline/generalized/static_python_flow_outline.py', ['FlowOutline', 'OutlineNode', 'OutlineEdge']),
        ('MOD-0008 schedule gate', 'code_library_registry/modules/MOD-0008/generalized/schedule_gate.py', ['Schedule', 'Decision'])]
for name, path, classes in MODS:
    add(f'SCH-{n:04d}', name + ' records', 'implied', 'the records this module passes around', 'Python dataclasses',
        dataclass_fields(classes), path, 'code-library-registry', r'^class ' + classes[0] + r'\b', '', 'algorithm row: ALG-' + name.split()[0])
    n += 1

# ---- implied from data: Echo's matrices --------------------------------------------------------------------------
def entry_fields(text):
    d = json.loads(text)
    entries = list(d.values()) if isinstance(d, dict) else d
    objs = [e for e in entries if isinstance(e, dict)]
    if not objs:
        return ['(entries are not objects)']
    counts = {}
    for e in objs:
        for k in e:
            counts[k] = counts.get(k, 0) + 1
    keys = sorted(counts, key=lambda k: -counts[k])
    keyed = 'keyed by id; ' if isinstance(d, dict) else 'list; '
    return [keyed + f'{len(objs)} entries'] + [k + ('' if counts[k] == len(objs) else f' ({counts[k]}/{len(objs)})') for k in keys]


MATRICES = [('echo_algorithm_matrix.json', 'one algorithm'), ('echo_lobby_agents.json', 'one word agent'),
            ('echo_vgm.json', 'one validated generalization'), ('echo_wordnet_chains.json', 'one WordNet chain'),
            ('echo_number_matrix.json', 'one number'), ('echo_equilibria.json', 'one equilibrium'),
            ('echo_formula_matrix.json', 'one formula'), ('echo_lhea_chains.json', 'one LHEA chain'),
            ('echo_geosensory_registry.json', 'one feed endpoint')]
for fname, describes in MATRICES:
    add(f'SCH-{n:04d}', f'{fname} entry', 'implied', describes, 'JSON', entry_fields, 'matrices/' + fname, None, None, '',
        'home: matrices/ for the store itself; this row is the shape of one entry')
    n += 1
add(f'SCH-{n:04d}', 'Rule Registry rule', 'implied', 'one notation or framework rule (R-codes)', 'JSON',
    lambda t: list(json.loads(t)[0]), 'code_library_registry/symbol_registries/rules-snapshot-2026-10-08.json', None, None, '',
    'fields read from the 2026-10-08 snapshot; the written form (D1 tables rules and rule_events) is in the CloudFlare project doc claude/rule-registry-upkeep.md, not in this repository')
n += 1

# ---- cross-references ----------------------------------------------------------------------------------------------
add(f'SCH-{n:04d}', 'Lexicon registry page template', 'written', 'the CLR-0043 page with /*STARTER*/ and /*GRAMMAR*/ placeholders', 'HTML template',
    '', 'code_library_registry/artifacts/CLR-0043/lexicon_registry.template.html', None, None, '', 'home: interfaces/; a page template, not a record form', kind='ref')
n += 1

cols = open(os.path.join(INV, 'schemas', 'INDEX.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t')


def write(path, header, rws):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')
        w.writerow(header)
        for r in rws:
            w.writerow([(r.get(c, '') if not isinstance(r.get(c), list) else '; '.join(r[c])) for c in header])


write(os.path.join(INV, 'schemas', 'INDEX.tsv'), cols, rows)


def merge(folder, new):
    p = os.path.join(INV, folder, 'INDEX.tsv')
    header = open(p, encoding='utf-8').readline().rstrip('\n').split('\t')
    old = {r['id']: r for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
    for r in new:
        old[r['id']] = {**old.get(r['id'], {}), **r}
    write(p, header, [old[k] for k in sorted(old)])
    return len(old)


def src(iid):
    loc = located[iid]
    return dict(branch=loc['branch'], path=loc['path'], blob_sha=loc['blob_sha'], commit=loc['commit'])


by_name = {r['name']: r['id'] for r in rows}
G = [
    ('GLO-0026', 'schema', 'the blank form: what fields a kind of record must have, their types and rules', 'inventory/schemas README (Claude, for this inventory)', 'SCH-0003', '', ''),
    ('GLO-0027', 'Inert (manifest)', 'every file of every branch is listed in a manifest (path, git blob fingerprint, size) with no content copied', 'CONTRACT-000.md', 'SCH-0001', '', ''),
    ('GLO-0028', 'Dual-Order', 'every elemental part reachable both ways: content-first (Matrix) and lookup-first (Index)', 'docs/ECHO_OUTPUT_FORMAT.md (citing the Dual-Order OS RFC)', 'SCH-0006', '', ''),
    ('GLO-0029', 'SOURCE-OBSERVED / INFERRED (evidence)', 'from a processor record / not', 'Business/ledger/SCHEMA.md', 'SCH-0004', 'Rule Registry provenance uses DECLARED / INFERRED / OBSERVED', ''),
    ('GLO-0030', 'freshness', 'whether a feed is missing, future, stale or fresh; kept separate from event age', 'src/geosensory_model.py', by_name['Geosensory reading'], '', ''),
    ('GLO-0031', 'department', '', '', 'SCH-0007', '', 'UNDEFINED AT SOURCE: also a column of the D1 agents table; see GLO-0025'),
    ('GLO-0032', 'reuse disposition', '', '', 'SCH-0005', '', 'UNDEFINED AT SOURCE: a heading of the assessment template; its allowed values are not listed there'),
]
gl = [dict(id=g, name=t, term=t, meaning=m, stated_by=b, first_seen=f, variants=v, made_by='unknown', status='INERT',
           home_or_ref='home', notes='met in schemas sweep 1' + ('; ' + nt if nt else ''), **src(f)) for g, t, m, b, f, v, nt in G]
n_gl = merge('glossary', gl)

REG = [dict(id='REG-0005', name='Geosensory endpoint registry', entry_count=str(len(json.loads(located[by_name['echo_geosensory_registry.json entry']]['text']))),
            maintained_by='A-155/A-158 GeosensoryCrawler', home_or_ref='home', entry_schema=by_name['echo_geosensory_registry.json entry'],
            notes='met in schemas sweep 1; also a D1 table (SCH-0012)', **src(by_name['echo_geosensory_registry.json entry'])),
       dict(id='REG-0006', name='Algorithm registry (echo_algorithm_matrix.json)',
            entry_count=str(len(json.loads(located[by_name['echo_algorithm_matrix.json entry']]['text']))), maintained_by='hand and A-150',
            home_or_ref='ref', entry_schema=by_name['echo_algorithm_matrix.json entry'],
            notes='home: matrices/ (its README lists it there); registry-shaped: A-numbers to name, status, purpose; newer copy on autonomous-agency', **src(by_name['echo_algorithm_matrix.json entry']))]
for r in REG:
    r.update(made_by='unknown', status='INERT', glyph='')
DECL_REG = sorted(sid for sid in seen_ids if ('registry' in sid or 'catalog' in sid)
                  and sid not in ('echo.hebrew-glyph-registry.v0.1', 'echo.grammar-registry.v0.1'))   # already REG-0001, REG-0004
for k, sid in enumerate(DECL_REG, 7):
    loc = located[by_name[sid]]
    d = json.loads(loc['text'])
    big = max((v for v in d.values() if isinstance(v, list)), key=len, default=[])
    REG.append(dict(id=f'REG-{k:04d}', name=sid, entry_count=str(len(big)), entry_schema=by_name[sid], maintained_by='', home_or_ref='home',
                    made_by='unknown', status='INERT', glyph='', notes='met in schemas sweep 1; declares its own schema id', **src(by_name[sid])))
REG.append(dict(id='REG-0001', entry_schema=by_name['echo.hebrew-glyph-registry.v0.1']))
REG.append(dict(id='REG-0004', entry_schema=by_name['echo.grammar-registry.v0.1']))
n_reg = merge('registries', REG)

# ---- Echo's shadow run, continuing from the logics sweep ------------------------------------------------------------
l2 = {}
for f in ('Algorithms', 'Codices', 'Formulas', 'Indices', 'Logics', 'Matrices', 'Registries'):
    for r in csv.DictReader(io.StringIO(git('show', f'origin/mirror-claude:L2-library/{f}/REGISTER.tsv')), delimiter='\t'):
        l2.setdefault(r['path'], f.lower())
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
    cases.append((r['id'], r['path'], r['name'] if located[r['id']]['line'] else '',
                  'schemas' if r['home_or_ref'] == 'home' else 'interfaces'))
DECOYS = [('src/echo_classroom.py', 'algorithms'), ('docs/ECHO_Polymath_Unified_Spec.md', 'codices'),
          ('notebook/query_workspace/specs.md', 'codices'), ('pwa/manifest.webmanifest', 'interfaces'),
          ('tests/test_geosensory_model.py', 'experiments'), ('GEOSENSORY_VISUAL_MODELS.md', 'codices'),
          ('matrices/symbols/mashet_instruction_manual.json', 'logics'), ('matrices/grammar/grammar_registry.json', 'logics')]
for i, (p, truth) in enumerate(DECOYS, 1):
    texts[p] = locate(p)['text']
    cases.append((f'DECOY-{i:02d}', p, '', truth))
# a file can be both a schema row and a decoy elsewhere: keep the first ruling for each path+id pair only
trace, summary = echo_journeyman.shadow(REPO, cases, ARMS, guess,
                                       os.path.join(INV, 'schemas', 'sweeps', 'echo_state_after_schemas.json'), seed=1024,
                                       prior_state=os.path.join(INV, 'logics', 'sweeps', 'echo_state_after_logics.json'))
write(os.path.join(INV, 'schemas', 'sweeps', 'echo_shadow_2.tsv'), ['n', 'id', 'path', 'bucket', 'arm', 'guess', 'ruling', 'hit'], trace)
json.dump(summary, open(os.path.join(INV, 'schemas', 'sweeps', 'echo_shadow_2.json'), 'w'), indent=1, ensure_ascii=False)
forms = {}
for r in rows:
    forms[r['form']] = forms.get(r['form'], 0) + 1
print(f'schemas rows {len(rows)} {forms}; glossary {n_gl}; registries {n_reg}')
print('echo:', json.dumps(summary, ensure_ascii=False))
