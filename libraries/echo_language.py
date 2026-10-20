"""Bounded language interfaces adapted around preserved branch components.

No free-form LLM, world-knowledge completion, or executable inversion is provided.
"""
import ast as py_ast
import importlib
import importlib.util
import json
import re
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def backend():
    name = '_echo_recovered_language'
    if name not in sys.modules:
        path = ROOT / 'vendor/echo-language'
        spec = importlib.util.spec_from_file_location(name, path / '__init__.py',
                                                    submodule_search_locations=[str(path)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return {part: importlib.import_module(name + '.' + part)
            for part in ('ast', 'lexicon', 'parser', 'realize', 'english_parse', 'audit')}


class RegistryView:
    def __init__(self, workspace):
        self.words = set()
        self.edges = {}
        for card in workspace.box.list('cards'):
            if card['body'].get('kind') == 'vocabulary':
                self.words.add(card['body']['word'])
        for relation in workspace.box.list('cards'):
            body = relation['body']
            if body.get('kind') != 'relation' or body.get('relation_type') != 'asserted-is-a':
                continue
            source = workspace.box.get('cards', body['source']['id'], body['source']['revision'])
            target = workspace.box.get('cards', body['target']['id'], body['target']['revision'])
            current_s = workspace.box.get('cards', source['id'])
            current_t = workspace.box.get('cards', target['id'])
            # Do not silently reinterpret an old edge after a resident was renamed.
            a, b = source['body']['word'], target['body']['word']
            if current_s['body']['word'] == a and current_t['body']['word'] == b:
                self.edges.setdefault(a, []).append((b, relation['id']))

    def has(self, word):
        return word in self.words

    def path(self, source, target):
        if not self.has(source) or not self.has(target):
            return None
        queue = deque([(source, [])]); seen = set()
        while queue:
            word, path = queue.popleft()
            if word == target:
                return path
            if word in seen:
                continue
            seen.add(word)
            for parent, relation_id in self.edges.get(word, []):
                queue.append((parent, path + [relation_id]))
        return None


def inspect_language(workspace, text, *, surface='emel', records=None):
    if not isinstance(text, str) or not text.strip() or len(text) > 10000:
        raise ValueError('A nonblank bounded expression is required')
    if surface not in ('emel', 'english'):
        raise ValueError('Unknown language surface')
    if records is not None and not isinstance(records, dict):
        raise ValueError('Result records must be an object')
    parts = backend(); registry = RegistryView(workspace)
    # Avoid ambient WordNet corpora changing lexical membership between machines.
    class LocalLexicon(parts['lexicon'].Lexicon):
        def word_known(self, word):
            return registry.has(word.replace('_', ' ').lower())
    lx = LocalLexicon(registry, records)
    parser = parts['parser']
    english_parser = parts['english_parse'].EnglishParser(lambda: parser.Parser([], lx))
    try:
        node = parser.parse(text, lx) if surface == 'emel' else english_parser.sentence(text)
    except (parser.ParseError, parts['english_parse'].EnglishParseError, IndexError) as exc:
        return {'decision': 'ABSTAIN', 'syntax': 'OUTSIDE_SUPPORTED_GRAMMAR',
                'reason': str(exc), 'execution': False}
    audit = parts['audit'].Auditor(registry, records or {})
    lexical, typed, discourse = audit.lexical(node), audit.type(node), audit.discourse(node)
    A = parts['ast']
    def truth(n):
        if isinstance(n, A.Relation):
            if n.op not in ('is_a', 'includes'):
                return 'UNKNOWN', []
            source, target = (n.source, n.target) if n.op == 'is_a' else (n.target, n.source)
            a = source.canonical.removeprefix('word:'); b = target.canonical.removeprefix('word:')
            path = registry.path(a, b)
            return ('SUPPORTED', path) if path is not None else ('UNKNOWN', [])
        if isinstance(n, A.Property):
            verdict, source = audit.truth(n)
            return verdict, [source]
        if isinstance(n, A.Not):
            verdict, evidence = truth(n.clause)
            return {'SUPPORTED': 'CONTRADICTED', 'CONTRADICTED': 'SUPPORTED'}.get(verdict, verdict), evidence
        if isinstance(n, A.Join):
            v1, e1 = truth(n.left); v2, e2 = truth(n.right)
            return ('CONTRADICTED' if 'CONTRADICTED' in (v1, v2) else
                    'SUPPORTED' if v1 == v2 == 'SUPPORTED' else 'UNKNOWN'), e1 + e2
        if isinstance(n, A.Apply):
            return 'NOT_A_CLAIM', []
        return 'UNKNOWN', []
    verdict, evidence = truth(node)
    rendered = parts['realize'].english(node)
    record_words = set()
    for record in (records or {}).values():
        if isinstance(record, dict):
            for key, value in record.items():
                record_words.update(re.findall('[a-z]+', str(key).replace('_', ' ').lower()))
                record_words.update(re.findall('[a-z]+', str(value).lower()))
    grammar = audit.grammar(node, rendered,
                            parts['english_parse'].EnglishParser(lambda: parser.Parser([], lx)),
                            lambda word: lx.word_known(word) or word.lower() in record_words)
    supported = (verdict == 'SUPPORTED' and lexical['status'] == 'PASS'
                 and typed['status'] == 'PASS' and discourse['status'] == 'PASS'
                 and grammar['status'] == 'PASS')
    return {'decision': 'ARTICULATE' if supported else 'WITHHOLD',
            'syntax': 'PARSED', 'tree': A.to_dict(node),
            'english': rendered if supported else None, 'rendered_candidate': rendered,
            'lexical': lexical, 'type': typed, 'discourse': discourse, 'grammar': grammar,
            'semantic': verdict, 'evidence': evidence, 'execution': False,
            'scope': 'Supported relative to explicitly supplied records/assumed relations; not independent world verification.'}


def articulate_roles(nodes, edges):
    """Use recovered trial-011 decision functions without running its top-level experiment."""
    if not isinstance(nodes, list) or any(not isinstance(n, str) or not re.fullmatch('[a-z]+', n) for n in nodes):
        raise ValueError('This bounded realizer accepts lower-case single-word terms only')
    if not isinstance(edges, list):
        raise ValueError('Edges must be a list')
    roles = {}
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 3:
            raise ValueError('Each edge needs entity, role and action')
        entity, role, action = edge
        if entity not in nodes or action not in nodes or role not in ('agent_of', 'patient_of'):
            return {'decision': 'ABSTAIN', 'reason': 'Unresolved term or unsupported role', 'sentence': None}
        roles.setdefault((role, action), set()).add(entity)
    if any(len(values) != 1 for values in roles.values()) or len({key[1] for key in roles}) > 1:
        return {'decision': 'ABSTAIN', 'reason': 'Ambiguous or multiple action roles', 'sentence': None}
    source = ROOT / 'vendor/echo-articulation/evidence_bound_articulation_011.py'
    tree = py_ast.parse(source.read_text())
    functions = [n for n in tree.body if isinstance(n, py_ast.FunctionDef)
                 and n.name in ('article', 'inflect', 'echo_decide')]
    namespace = {}
    # Only trusted pinned source functions; input data is never compiled or evaluated.
    exec(compile(py_ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), namespace)
    result = namespace['echo_decide']({'nodes': nodes, 'edges': edges})
    result['scope'] = 'Programmed singular transitive-clause grammar; irregular verbs and mass nouns are not resolved.'
    return result
