"""Explicit integration adapter: unchanged Genesis + persistent catalog + typed links.

Capabilities are trusted-caller configuration, not authentication. No LLM or DSL inversion.
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

from .catalog_box import CatalogBox, Conflict

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'vendor/echo-genesis/src/echo_governor_skeleton.py'
SOURCE_BLOB = '63eb982989b4f3478d649430b555c8f4ba755c27'


def genesis():
    data = SOURCE.read_bytes()
    if hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() != SOURCE_BLOB:
        raise ValueError('Genesis source differs from the preserved baseline')
    name = '_dual_order_preserved_genesis'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, SOURCE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


class EchoWorkspace:
    ALL_CAPABILITIES = frozenset({'read', 'cards:write', 'relations:write', 'tags:write', 'templates:write'})

    def __init__(self, database=':memory:', *, capabilities=('read',)):
        self.capabilities = frozenset(capabilities)
        if not self.capabilities <= self.ALL_CAPABILITIES:
            raise ValueError('Unknown capability')
        self.core = genesis()
        self.box = CatalogBox(database)
        self.matrix = self.core.AlgorithmMatrix()
        self.identity = self.core.ReshIdentity(self.matrix)
        self.identity.anchor()
        self.lobby = None
        self._rebuild()

    def close(self):
        self.box.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _gate(self, capability):
        if capability not in self.capabilities:
            raise PermissionError('Capability required: ' + capability)
        if not self.identity.validate() or self.matrix.known.get('A-000', {}).get('status') != 'ACTIVE':
            raise PermissionError('Genesis identity is not active')

    @staticmethod
    def _tokens(text):
        return set(re.findall(r'[a-z]+', text.lower()))

    def _rebuild(self):
        # Reconstruct from current persisted cards, not accumulated stale definitions.
        matrix = self.core.AlgorithmMatrix()
        self.matrix = matrix
        self.identity = self.core.ReshIdentity(matrix)
        self.identity.anchor()
        for card in self.box.list('cards'):
            body = card['body']
            if body.get('kind') != 'vocabulary':
                continue
            matrix.index_dictionary_entry(body['word'], body['definition'], body['department'])
        self.lobby = self.core.Lobby(matrix)
        self.lobby.populate()
        if self.lobby.agents:
            self.lobby.run_orientation()
            self.lobby.run_typed_study_groups()

    def seed_profiles(self):
        self._gate('cards:write')
        result = []
        for name, profile in self.core.HEBREW_LETTER_INDEX.items():
            card_id = 'glyph:' + name
            try:
                result.append(self.box.get('cards', card_id))
                continue
            except KeyError:
                pass
            body = {'kind': 'glyph-profile', 'name': name, 'source_profile': profile,
                    'keywords': [], 'status': 'source-description-not-execution'}
            if name == 'tsadi':
                body.update(role='paperclip', keywords=['attach', 'attachment', 'paperclip', 'paperclipping'],
                            status='user-directed-association')
            if name == 'tav':
                body.update(role='associative-stamp', keywords=['stamp', 'tag', 'mark'],
                            status='user-directed-association')
            result.append(self.box.put_card(card_id, name, body, glyph=profile['glyph'],
                          provenance={'source_blob': SOURCE_BLOB, 'override_source':
                                      'Timothy user direction' if name in ('tsadi', 'tav') else None}))
        return result

    def put_word(self, card_id, word, definition, *, department='unclassified', source=None,
                 expected_revision=0):
        self._gate('cards:write')
        if not all(isinstance(x, str) and x.strip() for x in (word, definition, department)):
            raise ValueError('Word, definition and department are required')
        word = word.lower().strip()
        for card in self.box.list('cards'):
            if card['id'] != card_id and card['body'].get('kind') == 'vocabulary' and card['body']['word'] == word:
                raise Conflict('Word already has a catalog identity')
        result = self.box.put_card(card_id, word, {'kind': 'vocabulary', 'word': word,
                                  'definition': definition, 'department': department},
                                  provenance=source, expected_revision=expected_revision)
        self._rebuild()
        return result

    def revise_profile(self, card_id, keywords, *, expected_revision):
        self._gate('cards:write')
        old = self.box.get('cards', card_id)
        if old['body'].get('kind') != 'glyph-profile':
            raise ValueError('Not a glyph profile')
        if not isinstance(keywords, list) or any(not isinstance(k, str) or not k.strip() for k in keywords):
            raise ValueError('Keywords must be nonblank strings')
        body = dict(old['body'], keywords=keywords, status='user-revised-association')
        return self.box.put_card(card_id, old['title'], body, glyph=old['glyph'],
                                 provenance=old['provenance'], expected_revision=expected_revision)

    def _relation(self, relation_id, relation_type, source_id, target_id, evidence):
        source = self.box.get('cards', source_id)
        target = self.box.get('cards', target_id)
        body = {'kind': 'relation', 'relation_type': relation_type,
                'source': {'id': source_id, 'revision': source['revision']},
                'target': {'id': target_id, 'revision': target['revision']},
                'evidence': evidence, 'status': 'association-not-verified-theorem'}
        try:
            old = self.box.get('cards', relation_id)
            if old['body'] == body:
                return old
            raise Conflict('Relation identity already refers to different endpoints or evidence')
        except KeyError:
            return self.box.put_card(relation_id, relation_type, body,
                                     provenance={'component': 'echo-workspace'})

    def paperclip(self, relation_id, source_id, target_id):
        self._gate('relations:write')
        if source_id == target_id:
            raise ValueError('Paperclip requires two distinct card identities')
        return self._relation(relation_id, 'paperclip', source_id, target_id,
                              {'requested_operation': 'צ paperclipping'})

    def assert_is_a(self, relation_id, source_id, target_id):
        self._gate('relations:write')
        for card_id in (source_id, target_id):
            if self.box.get('cards', card_id)['body'].get('kind') != 'vocabulary':
                raise ValueError('An asserted is-a relation needs vocabulary residents')
        return self._relation(relation_id, 'asserted-is-a', source_id, target_id,
                              {'source': 'explicit caller assertion',
                               'status': 'assumption-not-independent-verification'})

    def stamp(self, relation_id, word_id, profile_id, *, profile_revision=None):
        self._gate('tags:write')
        word = self.box.get('cards', word_id)
        profile = self.box.get('cards', profile_id, profile_revision)
        if word['body'].get('kind') != 'vocabulary' or profile['body'].get('kind') != 'glyph-profile':
            raise ValueError('Stamp needs a vocabulary card and a glyph profile')
        tokens = self._tokens(word['body']['word'] + ' ' + word['body']['definition'])
        matches = sorted(k for k in profile['body']['keywords'] if self._tokens(k) and self._tokens(k) <= tokens)
        if not matches:
            raise ValueError('No defined lexical evidence for this stamp')
        if profile['revision'] != self.box.get('cards', profile_id)['revision']:
            # Historical association is explicit, but never silently retarget to latest.
            raise ValueError('Use the current profile when creating a new stamp; old stamps retain history')
        return self._relation(relation_id, 'associative-stamp', word_id, profile_id,
                              {'matched_keywords': matches, 'method': 'explicit-token-match',
                               'operation_glyph': 'ת', 'profile_revision': profile['revision']})

    def save_template(self, template_id, title, configuration, card_ids):
        self._gate('templates:write')
        return self.box.put_template(template_id, title, configuration,
                                     [{'id': x} for x in card_ids])

    def stamp_matches(self, word_id):
        """Deterministic associations, not theorem verification or subjective judgment."""
        self._gate('tags:write')
        word = self.box.get('cards', word_id)
        if word['body'].get('kind') != 'vocabulary':
            raise ValueError('Not a vocabulary card')
        tokens = self._tokens(word['body']['word'] + ' ' + word['body']['definition'])
        result = []
        for profile in self.box.list('cards'):
            body = profile['body']
            if body.get('kind') != 'glyph-profile':
                continue
            if any(self._tokens(k) and self._tokens(k) <= tokens for k in body['keywords']):
                identity = json.dumps([word_id, word['revision'], profile['id'], profile['revision']])
                relation_id = 'stamp:' + hashlib.sha256(identity.encode()).hexdigest()
                result.append(self.stamp(relation_id, word_id, profile['id']))
        return result

    def restore(self, template_id, instance_id):
        self._gate('templates:write')
        return self.box.instantiate(template_id, instance_id)

    def configuration_graph(self, instance_id):
        """Describe saved references; this is not the undefined §DSL§ inversion."""
        self._gate('read')
        cards = self.box.resolve_cards('configurations', instance_id)
        edges = []
        for card in cards:
            if card['body'].get('kind') == 'relation':
                edges.append({'id': card['id'], **card['body']})
        return {'nodes': [{'id': c['id'], 'revision': c['revision'],
                           'kind': c['body'].get('kind')} for c in cards],
                'relations': edges, 'inversion': 'unresolved-not-executed'}

    def query(self, request):
        self._gate('read')
        if not isinstance(request, dict):
            raise ValueError('Query must be an object')
        operation = request.get('operation')
        if operation == 'language':
            from .echo_language import inspect_language
            return inspect_language(self, request.get('text'), surface=request.get('surface', 'emel'),
                                    records=request.get('records'))
        if operation == 'articulate':
            from .echo_language import articulate_roles
            return articulate_roles(request.get('nodes'), request.get('edges'))
        if operation == 'cards':
            return self.box.list('cards', glyph=request.get('glyph'))
        if operation == 'neighbors':
            word = request.get('word', '').lower()
            a = self.lobby.agents.get(word)
            return {'word': word, 'neighbors': sorted(a.ties) if a else [],
                    'classification': self.core.AlgorithmicCommunicator(lobby=self.lobby)._ayin_classify(word)}
        if operation == 'record':
            return self.box.get(request['section'], request['id'], request.get('revision'))
        if operation == 'relations':
            return [x for x in self.box.list('cards') if x['body'].get('kind') == 'relation'
                    and (request.get('card_id') is None or request['card_id'] in
                         (x['body']['source']['id'], x['body']['target']['id']))]
        raise ValueError('Unknown query operation; queries cannot execute mutations')
