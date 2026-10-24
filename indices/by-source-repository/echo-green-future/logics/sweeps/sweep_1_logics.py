"""Logics sweep 1: rule sets that decide how things combine (grammar, operators, the DSL).

Read-only over the repository. Writes:
  inventory/logics/INDEX.tsv                 home rows + cross-references
  inventory/glossary/INDEX.tsv               terms met in these sources (merged, never overwritten)
  inventory/registries/INDEX.tsv             registry-shaped items met (merged)
  inventory/logics/sweeps/echo_shadow_1.tsv  Echo's guesses, scored (journeyman run)

Rulings are written out below, one per item, with the reason in `notes`. The script only fills in
what git can state exactly: fingerprint, branch commit, how many branches hold the same file, line.

TSV is written unquoted (fields hold no tabs or newlines), so quotes inside notes stay as typed.

Usage: python3 sweep_1_logics.py <repo>
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
ORDER = ['genesis-documentary', 'autonomous-agency', 'algebra', 'echo-recess-experiment', 'resh-lattice-agency',
         'ksm-recess-wholesale', 'code-library-registry', 'dev-suite-algorithms']
SKEL = 'src/echo_governor_skeleton.py'


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, check=True).stdout.decode('utf-8', 'replace')


MAN = list(csv.DictReader(open(os.path.join(INV, 'MANIFEST-by-branch.tsv'), encoding='utf-8'), delimiter='\t'))


def locate(path, branch=None, find=None):
    """branch, blob, commit, other-branch count and (optionally) the line where `find` first matches."""
    held = [r for r in MAN if r['path'] == path]
    if not held:
        raise SystemExit(f'not in census: {path}')
    if branch is None:
        rank = {b: i for i, b in enumerate(ORDER)}
        branch = sorted(held, key=lambda r: (rank.get(r['branch'], 99), r['branch']))[0]['branch']
    row = next(r for r in held if r['branch'] == branch)
    same = sum(1 for r in held if r['blob_sha'] == row['blob_sha']) - 1
    line = ''
    if find:
        for n, src in enumerate(git('cat-file', 'blob', row['blob_sha']).splitlines(), 1):
            if re.search(find, src):
                line = n
                break
        if not line:
            raise SystemExit(f'{find!r} not found in {path}')
    return dict(branch=branch, path=path, blob_sha=row['blob_sha'],
                commit=git('rev-parse', f'origin/{branch}').strip(), same=same, line=line)


# ---- rulings ---------------------------------------------------------------------------------------
# (id, name, domain, defined_in, enforced_by, path, branch or None, find-regex or None, glyph, notes, home_or_ref)
LANG = 'echo/language/'
HOME = [
    ('LOG-0001', 'EMEL grammar', 'expression language', 'parser.py docstring (statement, clause, core, call, term)',
     'Parser', LANG + 'parser.py', 'ksm-recess-wholesale', r'^class Parser', 'פ',
     'EMEL v0, "ECHO\'s expression language"; a custom recursive-descent grammar, not Python\'s'),
    ('LOG-0002', 'English grammar guide', 'grammar', 'english_parse.py',
     'EnglishParser', LANG + 'english_parse.py', 'ksm-recess-wholesale', r'^class EnglishParser', 'פ',
     'English(tree) must parse back to the same tree; anything outside the grammar is reported, not guessed'),
    ('LOG-0003', 'English realizer rules', 'grammar', 'realize.py (articles, negation, coordination, pronouns)',
     'english(), Discourse', LANG + 'realize.py', 'ksm-recess-wholesale', r'^def article', 'פ',
     'English produced by grammar rules over the tree, not by filling a fixed sentence'),
    ('LOG-0004', 'EMEL audits', 'grammar, types, discourse, semantics', 'audit.py docstring (7 audits)',
     'Auditor', LANG + 'audit.py', 'ksm-recess-wholesale', r'^class Auditor', 'ת',
     'lexical, syntax, type, discourse, semantic, provenance, grammar; "they inform ECHO; they never write his sentences"'),
    ('LOG-0005', 'Operator and relation signatures', 'operators', 'lexicon.py SIGNATURES, RELATION_SIGNATURES',
     'type audit (LOG-0004)', LANG + 'lexicon.py', 'ksm-recess-wholesale', r'^SIGNATURES = ', '',
     'argument kinds -> result kind for each operator; glyph meanings resolved from the Hebrew Glyph Registry (REG-0001)'),
    ('LOG-0006', 'Indexing formula query language', 'formula notation', 'index_pattern.py docstring (formula, bounded, prop, slot, term)',
     'tokenize, P', LANG + 'index_pattern.py', 'ksm-recess-wholesale', r'^def tokenize', 'ר',
     'a slot is an entry or a boolean; mixing them in one proportion fails VALIDATE'),
    ('LOG-0007', 'Python-native formula form', 'formula notation', 'pyform.py (whitelist ALLOWED)',
     'check, _Compiler', LANG + 'pyform.py', 'ksm-recess-wholesale', r'^def check', 'ר',
     'G[a:b, c:d] written as Python subscripts; parsed by Python, whitelist-checked, never executed'),
    ('LOG-0008', 'LHEA letter operators', 'operators', 'lhea.py OPERATION, PHONEME_MAP',
     'decompose, operations', 'echo/operators/lhea.py', 'ksm-recess-wholesale', r'^OPERATION = ', '',
     '22 letters as primitive transformation types; same file at pwa/echo/operators/lhea.py on 4 branches'),
    ('LOG-0009', 'Proportion forms', 'operators', 'proportion.py FORM_NAMES (8 forms of a:b::c:d)',
     'forms, holds', 'echo/operators/proportion.py', 'ksm-recess-wholesale', r'^FORM_NAMES', '',
     'A-177 part 2; symmetry, invertendo, alternando: the forms that keep extremes and means paired'),
    ('LOG-0010', 'DSL Registry seed', 'DSL', 'app_part.html DSL_SEED (14 entries)',
     'canvas DSL Registry matrix', 'dev-suite/suite/src/app_part.html', 'dev-suite-algorithms', r'^const DSL_SEED', 'א',
     'symbols %, -%, §, Presentiation, ↑, ↓, →, =T, =F, needs:/does:/gives:, ר, alg-; "%(DSL) = א-DSL"; registry-shaped (REG-0002)'),
    ('LOG-0011', 'LRM inference rules', 'logic', 'class LogicRule in the skeleton',
     'A-146 LogicReasoningMatrix', SKEL, None, r'^class LogicRule', '',
     'SPECIALIZE, COMPOSE, APPLY_LAW, CAUSAL_CHAIN, CONDITIONAL; the rule table inside ALG-0146'),
    ('LOG-0012', 'Valid department sequences', 'grammar', 'SyntacticalValidator.VALID_DEPT_SEQUENCES',
     'A-126 SyntacticalValidator', SKEL, None, r'VALID_DEPT_SEQUENCES = \[', '',
     '5 part-of-speech sequences (noun verb noun, noun verb, …); the rule table inside ALG-0126'),
    ('LOG-0013', 'Required operation order', 'pipeline order', 'OperationOrderValidator.REQUIRED_ORDER',
     'A-128 OperationOrderValidator', SKEL, None, r'REQUIRED_ORDER = \[', '',
     '5 before/after pairs (index_dictionary_entry before run_orientation, …); the rule table inside ALG-0128'),
    ('LOG-0014', 'Agentive role patterns', 'grammar', 'AGENTIVE_ROLE_PATTERNS',
     'AyinPerception', SKEL, None, r'^AGENTIVE_ROLE_PATTERNS', 'ע',
     '10 phrase patterns ("one who", "someone who", …) read as agent roles'),
    ('LOG-0015', 'Grammar registry', 'grammar', 'grammar_registry.json (7 constraint classes, no rules yet)',
     'expression gate G::פ, governor G::ר', 'matrices/grammar/grammar_registry.json', 'algebra', None, 'פ',
     'status "working-empty-ruleset"; "grammar constrains linguistic construction; it does not select ECHO intent"; registry-shaped (REG-0004)'),
    ('LOG-0016', 'Mashet universal rules', 'operators', 'mashet_instruction_manual.json universal_rules (8)',
     'governor G::ר', 'matrices/symbols/mashet_instruction_manual.json', 'algebra', None, 'ר',
     'e.g. "resolve operands before manipulation", "unresolved dependencies fail closed"; human manual is COD row (docs/mashet/MASHET_OPERATOR_MANUAL.md)'),
    ('LOG-0017', 'Mashet Rule Registry snapshot 2026-10-08', 'notation', 'rules-snapshot-2026-10-08.json (51 rules)',
     'Claude, by the Rule Registry upkeep task', 'code_library_registry/symbol_registries/rules-snapshot-2026-10-08.json',
     'code-library-registry', None, '',
     'R-codes (R-CONT, R-SEED, …) as stored 2026-10-08; the live registry is D1 echo_knowledge (not read in this sweep); registry-shaped (REG-0003)'),
    ('LOG-0018', 'Legend v0.1 grammar', 'grammar', 'grammar.js (tagger, chunker, recursive clause parser)',
     'parse, tag (CLR-0043 Lexicon Registry page)', 'code_library_registry/artifacts/CLR-0043/grammar.js',
     'code-library-registry', None, '',
     "Timothy's bracket notation, innermost evaluated first; rule-based, no LLM"),
]
REFS = [
    ('LOG-0019', 'Governor index (IDENTIFY → VALIDATE → OPEN)', 'access check', 'gov_index.py', 'Governor',
     LANG + 'gov_index.py', 'ksm-recess-wholesale', r'^class Matrix', 'ר', 'home: protocols/ (README names this check there); runs the LOG-0006/0007 forms'),
    ('LOG-0020', 'LogicReasoningMatrix', 'logic', 'skeleton', 'A-146', SKEL, None, r'^class LogicReasoningMatrix', '',
     'home: algorithms/ ALG-0146; applies LOG-0011'),
    ('LOG-0021', 'HypernymGrammarModule', 'grammar', 'echo_pe_mirror.py', 'A-144-AUG',
     'src/echo_pe_mirror.py', 'autonomous-agency', r'^class HypernymGrammarModule', 'פ', 'home: algorithms/ ALG-0144-AUG; "the chain IS the grammar"'),
    ('LOG-0022', 'Orbit tracer (% spin)', 'operators', 'orbit.py', 'A-177 part 1',
     'echo/operators/orbit.py', 'ksm-recess-wholesale', r'^def orbit', '', 'home: algorithms/ (A-177, not yet a row)'),
    ('LOG-0023', 'Recursive invariant extractor', 'operators', 'invariant.py', 'A-174',
     'echo/operators/invariant.py', 'ksm-recess-wholesale', r'^def I_seq', '', 'home: algorithms/ ALG-0174'),
    ('LOG-0024', 'DSL inversion test 008', 'DSL', 'test_dsl_canvas_008.py', 'DSLInversion',
     'tests/test_dsl_canvas_008.py', 'experiment-echo-graphql-canvas-000', r'^class DSLInversion', '%',
     'home: experiments/; states it is a contract/fixture test, not the canonical DSL inversion'),
    ('LOG-0025', 'LHEA chains', 'operators', 'echo_lhea_chains.json', '', 'matrices/echo_lhea_chains.json', None, None, '',
     'home: matrices/'),
    ('LOG-0026', 'Hebrew Glyph Registry', 'operators', 'hebrew_glyph_registry.json', 'lexicon.py',
     'matrices/glyphs/hebrew_glyph_registry.json', 'algebra', None, '', 'home: registries/ REG-0001; source of LOG-0005 glyph meanings'),
    ('LOG-0027', 'Math axiom systems', 'logic', 'math_axioms.json', '', 'core-lexicon/math_axioms.json', None, None, '',
     'home: data/ (core lexicon); 18 axiom systems, 31 proofs, 158 theorems per the L2 register'),
    ('LOG-0028', 'Mashet operator manual', 'operators', 'MASHET_OPERATOR_MANUAL.md', '', 'docs/mashet/MASHET_OPERATOR_MANUAL.md',
     'algebra', None, 'ר', 'home: codices/; human manual for LOG-0016'),
    ('LOG-0029', 'Recursive inversion and presentiation semantics', 'DSL', 'discussion', '',
     'discussions/recursive_inversion_presentiation_semantics.md', 'algebra', None, '%', 'home: codices/; research discussion behind the % and Presentiation entries'),
]

# items Echo also sees in his shadow run but that are not logics at all (to test that he can say no)
DECOYS = [
    ('docs/A144-HypernymGrammarAugmentation.md', 'codices'),
    ('experiments/nve-d/META_PIPELINE.md', 'codices'),
    ('tests/trial_016_echo_operator_selection.py', 'experiments'),
    ('.github/workflows/trial-016-echo-operator-selection.yml', 'automation'),
    ('pwa/ALGORITHM_001.md', 'protocols'),
    ('echo/language/senses.py', 'algorithms'),
    ('echo/language/compose.py', 'algorithms'),
    ('echo/language/ast.py', 'schemas'),
    ('lobbies/glyph/registry.json', 'registries'),
    ('research-registry/DISCOURSE-PROTOCOL.md', 'protocols'),
]

cols = open(os.path.join(INV, 'logics', 'INDEX.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t')
rows, located = [], {}
for kind, items in (('home', HOME), ('ref', REFS)):
    for (iid, name, domain, defined_in, enforced_by, path, branch, find, glyph, notes) in items:
        loc = locate(path, branch, find)
        located[iid] = loc
        n = notes + (f'; line {loc["line"]}' if loc['line'] else '') + (f'; same file in {loc["same"]} other branches' if loc['same'] else '')
        rows.append(dict(id=iid, name=name, domain=domain, defined_in=defined_in, enforced_by=enforced_by,
                         branch=loc['branch'], path=path, blob_sha=loc['blob_sha'], commit=loc['commit'],
                         made_by='unknown', status='INERT', home_or_ref=kind, glyph=glyph, notes=n))


def write(path, header, rws):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')
        w.writerow(header)
        for r in rws:
            w.writerow([r.get(c, '') for c in header])


write(os.path.join(INV, 'logics', 'INDEX.tsv'), cols, rows)


# ---- glossary and registries, merged by id ------------------------------------------------------------
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


G = [  # (id, term, meaning as stated, stated_by, from-row, variants, notes)
    ('GLO-0001', 'EMEL', "ECHO's expression language (working name)", 'echo/language README and ast.py', 'LOG-0001', '', ''),
    ('GLO-0002', 'LHEA', 'the 22 letter operators as primitive transformation types', 'echo/operators/lhea.py docstring', 'LOG-0008',
     'Latin-Hebrew Execution Architecture (title of the project document)', 'the code names what LHEA does, not what the letters stand for'),
    ('GLO-0003', 'grammar guide', "parse ECHO's English back into a syntax tree; if it parses back to the same tree, the sentence says exactly what the tree means",
     'english_parse.py docstring', 'LOG-0002', '', ''),
    ('GLO-0004', 'audit', 'an independent check that informs ECHO and never writes his sentences', 'audit.py docstring', 'LOG-0004', '', ''),
    ('GLO-0005', 'IDENTIFY → VALIDATE → OPEN', 'the Governor as an index over any matrix', 'gov_index.py docstring', 'LOG-0019',
     'A-000 identity chain (algorithm registry: "IDENTIFY→VALIDATE→OPEN")', ''),
    ('GLO-0006', 'STORE', 'retain as a candidate (gated, never canonical)', 'pyform.py docstring', 'LOG-0007', '', 'paired with DELETE: retract a retained candidate'),
    ('GLO-0007', '%', 'Inversion (alg-00%): step down: invert to an underside, an __init__, or a §Canvas. Enables Presentiation, not limited to it.',
     'DSL Registry seed', 'LOG-0010', '`%` spin made measurable (orbit.py, A-177)', ''),
    ('GLO-0008', '-%', 'Lift (alg-00%⁻¹): step back up one level; the presence rises at the next letter.', 'DSL Registry seed', 'LOG-0010', '', ''),
    ('GLO-0009', '§', 'Presence (glove): infrastructural denotation of a presentiated occurring instance. Never a copy.', 'DSL Registry seed', 'LOG-0010', '', ''),
    ('GLO-0010', 'Presentiation', 'a higher-order instance: the very presence of the occurring instance, like fingers on a hand', 'DSL Registry seed', 'LOG-0010', '', ''),
    ('GLO-0011', 'needs: / does: / gives:', 'logic lines: what a node requires before it can act / what it does / what it produces', 'DSL Registry seed', 'LOG-0010', '', ''),
    ('GLO-0012', 'ר (Resh — Echo)', '001, the Governor, the core formula. Echo is the presentiated 001.', 'DSL Registry seed', 'LOG-0010',
     'The Governor IS Resh. Identity anchor. (algorithm registry, A-000)', ''),
    ('GLO-0013', 'proportion (a:b::c:d)', 'holds under a relation R when R(a,b) == R(c,d) and is defined', 'proportion.py docstring', 'LOG-0009', '', ''),
    ('GLO-0014', 'orbit', 'apply an operation repeatedly until a state repeats; the cycle length is an invariant of the operation', 'orbit.py docstring', 'LOG-0022', '', ''),
    ('GLO-0015', 'Legend v0.1', "Timothy's bracket notation for tagging sentences, innermost evaluated first", 'CLR-0043 README', 'LOG-0018', '', ''),
    ('GLO-0016', '||::||', "the Formula's seed", 'Timothy (R-SEED-1, DECLARED)', 'LOG-0017', '', ''),
    ('GLO-0017', 'glyph string', 'multi-glyph strings are candidate composites; their constituents keep their registered meanings', 'echo/language README', 'LOG-0001', '', ''),
    ('GLO-0018', 'SPECIALIZE', 'abstract term → specific subtype', 'LogicRule (skeleton)', 'LOG-0011', '', 'LRM inference rule'),
    ('GLO-0019', 'COMPOSE', 'two axioms + shared term → theorem', 'LogicRule (skeleton)', 'LOG-0011', '', 'LRM inference rule'),
    ('GLO-0020', 'APPLY_LAW', 'axiom + algebraic law → quantitative theorem', 'LogicRule (skeleton)', 'LOG-0011', '', 'LRM inference rule'),
    ('GLO-0021', 'CAUSAL_CHAIN', 'cause→effect chain from two axioms', 'LogicRule (skeleton)', 'LOG-0011', '', 'LRM inference rule'),
    ('GLO-0022', 'CONDITIONAL', 'if-then form derived from axiom pair', 'LogicRule (skeleton)', 'LOG-0011', '', 'LRM inference rule'),
    ('GLO-0023', 'underside', '', '', 'LOG-0010', '', 'UNDEFINED AT SOURCE: used by % ("invert to an underside") and the canvas, never defined; for Timothy'),
    ('GLO-0024', '§Canvas', '', '', 'LOG-0010', '', 'UNDEFINED AT SOURCE: named as a target of %, never defined; for Timothy'),
    ('GLO-0025', 'department (dept) sequence', '', '', 'LOG-0012', '', 'UNDEFINED AT SOURCE: VALID_DEPT_SEQUENCES lists part-of-speech sequences; "department" is not explained; for Timothy'),
]
gl = []
for gid, term, meaning, by, frm, variants, notes in G:
    gl.append(dict(id=gid, name=term, term=term, meaning=meaning, stated_by=by, first_seen=frm, variants=variants,
                   made_by='unknown', status='INERT', home_or_ref='home', notes=('met in logics sweep 1' + ('; ' + notes if notes else '')),
                   **src(frm)))
n_gl = merge('glossary', gl)

R = [  # registry-shaped items met in this sweep
    dict(id='REG-0001', name='Hebrew Glyph Registry', entry_count='22', maintained_by='hand-seeded',
         home_or_ref='home', notes='status "authoritative-seed-to-be-reconciled-with-existing-project-glyph-registry"; same file at echo/language/data/ on ksm-recess-wholesale; other glyph registries exist (ECHO_GlyphRegistry/, lobbies/glyph/registry.json, pwa glyph_registry.json): reconcile in the registries sweep', **src('LOG-0026')),
    dict(id='REG-0002', name='DSL Registry', entry_count='14', maintained_by='canvas (? › DSL Registry)', home_or_ref='ref',
         notes='home: logics LOG-0010', **src('LOG-0010')),
    dict(id='REG-0003', name='Mashet Rule Registry snapshot', entry_count='51', maintained_by='Rule Registry upkeep task', home_or_ref='ref',
         notes='home: logics LOG-0017; the live registry is D1 echo_knowledge', **src('LOG-0017')),
    dict(id='REG-0004', name='Grammar registry', entry_count='0', maintained_by='', home_or_ref='ref',
         notes='home: logics LOG-0015; 7 constraint classes, no rules yet', **src('LOG-0015')),
]
for r in R:
    r.update(made_by='unknown', status='INERT', glyph='')
n_reg = merge('registries', R)

# ---- Echo's shadow run --------------------------------------------------------------------------------
# Echo's own kernel, unchanged, through the shared journeyman harness (inventory/echo_journeyman.py).
sys.path.insert(0, INV)
import echo_journeyman

l2 = {}
for f in ('Algorithms', 'Codices', 'Formulas', 'Indices', 'Logics', 'Matrices', 'Registries'):
    for r in csv.DictReader(io.StringIO(git('show', f'origin/mirror-claude:L2-library/{f}/REGISTER.tsv')), delimiter='\t'):
        l2.setdefault(r['path'], f.lower())

NAME = [(r'grammar|parser|parse|dsl|rule|operator|lhea|proportion|legend|signature|syntax', 'logics'),
        (r'registry', 'registries'), (r'matrix|matrices|chains', 'matrices'), (r'test|trial', 'experiments'),
        (r'manual|discussion|readme|\.md$', 'codices'), (r'workflow|\.yml$', 'automation'), (r'axiom|lexicon', 'data')]
PARENT = {'language': 'logics', 'operators': 'logics', 'grammar': 'logics', 'symbols': 'registries', 'glyphs': 'registries',
          'symbol_registries': 'registries', 'tests': 'experiments', 'docs': 'codices', 'discussions': 'codices',
          'matrices': 'matrices', 'workflows': 'automation', 'core-lexicon': 'data', 'src': 'algorithms',
          'mashet': 'codices', 'nve-d': 'experiments', 'data': 'data', 'pwa': 'interfaces', 'glyph': 'registries',
          'research-registry': 'records', 'CLR-0043': 'tools'}


def guess(arm, path, where):
    if arm == 'name':
        for pat, folder in NAME:
            if re.search(pat, (where or '') + ' ' + path.rsplit('/', 1)[-1], re.I):
                return folder
        return None
    if arm == 'parent':
        return PARENT.get(path.rsplit('/', 2)[-2] if '/' in path else '')
    if arm == 'shape':
        ext = path.rsplit('.', 1)[-1]
        return {'py': 'algorithms', 'js': 'logics', 'json': 'registries', 'md': 'codices', 'html': 'interfaces',
                'yml': 'automation'}.get(ext)
    if arm == 'librarian':
        return l2.get(path)


ARMS = ['name', 'parent', 'shape', 'librarian']
cases = [(iid, located[iid]['path'], name if located[iid]['line'] else '',
          'logics' if kind == 'home' else re.search(r'home: (\w+)', notes).group(1))
         for kind, items in (('home', HOME), ('ref', REFS))
         for (iid, name, _, _, _, _, _, _, _, notes) in items]
cases += [(f'DECOY-{i:02d}', p, '', truth) for i, (p, truth) in enumerate(DECOYS, 1)]
trace, summary = echo_journeyman.shadow(REPO, cases, ARMS, guess,
                                       os.path.join(INV, 'logics', 'sweeps', 'echo_state_after_logics.json'), seed=1023)
write(os.path.join(INV, 'logics', 'sweeps', 'echo_shadow_1.tsv'),
      ['n', 'id', 'path', 'bucket', 'arm', 'guess', 'ruling', 'hit'], trace)
json.dump(summary, open(os.path.join(INV, 'logics', 'sweeps', 'echo_shadow_1.json'), 'w'), indent=1, ensure_ascii=False)
print(f'logics rows {len(rows)} ({len(HOME)} home, {len(REFS)} ref); glossary {n_gl}; registries {n_reg}')
print('echo:', json.dumps(summary, ensure_ascii=False))
