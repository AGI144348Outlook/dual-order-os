import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from libraries.echo_workspace import EchoWorkspace, genesis
from libraries.catalog_box import Conflict


class IntegratedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'workspace.sqlite'
        self.w = EchoWorkspace(self.db, capabilities=EchoWorkspace.ALL_CAPABILITIES)
        self.w.seed_profiles()
        self.w.put_word('word:clip', 'paperclip', 'attach card to index', department='verb')
        self.w.put_word('word:index', 'index', 'card collection', department='noun')

    def tearDown(self):
        self.w.close(); self.tmp.cleanup()

    def test_genesis_identity_and_original_index_are_live(self):
        self.assertTrue(self.w.identity.validate())
        result = self.w.query({'operation': 'neighbors', 'word': 'paperclip'})
        self.assertIn('index', result['neighbors'])
        self.assertEqual(result['classification'], 'PROCESS_VERB')

    def test_raw_glyph_query_uses_catalog_without_changing_tokenizer(self):
        self.assertEqual(self.w.query({'operation': 'cards', 'glyph': 'צ'})[0]['id'], 'glyph:tsadi')
        self.assertEqual(self.w.query({'operation': 'cards', 'glyph': 'ץ'})[0]['id'], 'glyph:tsadi-sofit')
        self.assertEqual(self.w.core.AlgorithmicCommunicator()._tokenize('צ'), [])

    def test_profile_seeding_does_not_overwrite_revisions(self):
        self.w.revise_profile('glyph:tsadi', ['connect'], expected_revision=1)
        self.w.seed_profiles()
        self.assertEqual(self.w.box.get('cards', 'glyph:tsadi')['revision'], 2)
        self.assertEqual(self.w.box.get('cards', 'glyph:tsadi')['body']['keywords'], ['connect'])

    def test_paperclip_is_typed_identity_preserving_and_idempotent(self):
        before = self.w.box.get('cards', 'word:clip')
        first = self.w.paperclip('clip:1', 'word:clip', 'word:index')
        self.assertEqual(self.w.paperclip('clip:1', 'word:clip', 'word:index'), first)
        self.assertEqual(self.w.box.get('cards', 'word:clip'), before)
        with self.assertRaises(Conflict):
            self.w.paperclip('clip:1', 'word:index', 'word:clip')

    def test_paperclip_rejects_unknown_or_self_target_without_partial_record(self):
        with self.assertRaises(KeyError):
            self.w.paperclip('clip:bad', 'word:clip', 'missing')
        with self.assertRaises(ValueError):
            self.w.paperclip('clip:bad', 'word:clip', 'word:clip')
        with self.assertRaises(KeyError):
            self.w.box.get('cards', 'clip:bad')

    def test_stamp_evidence_pins_profile_and_remains_association(self):
        r = self.w.stamp('tag:1', 'word:clip', 'glyph:tsadi')
        self.assertEqual(r['body']['target'], {'id': 'glyph:tsadi', 'revision': 1})
        self.assertIn('attach', r['body']['evidence']['matched_keywords'])
        self.assertEqual(r['body']['status'], 'association-not-verified-theorem')
        self.assertFalse(any(k.startswith('VGM') for k in self.w.matrix.known))

    def test_unrelated_stamp_is_rejected(self):
        with self.assertRaises(ValueError):
            self.w.stamp('tag:bad', 'word:index', 'glyph:tav')
        with self.assertRaises(KeyError):
            self.w.box.get('cards', 'tag:bad')

    def test_batch_stamps_are_idempotent_and_profile_changes_do_not_rewrite_history(self):
        first = self.w.stamp_matches('word:clip')
        self.assertEqual(len(first), 1)
        self.assertEqual(self.w.stamp_matches('word:clip'), first)
        self.w.revise_profile('glyph:tsadi', ['unrelated'], expected_revision=1)
        self.assertEqual(self.w.stamp_matches('word:clip'), [])
        old = self.w.box.get('cards', first[0]['id'])
        self.assertEqual(old['body']['target']['revision'], 1)

    def test_reopen_rebuilds_genesis_and_preserves_relations(self):
        self.w.paperclip('clip:1', 'word:clip', 'word:index')
        self.w.close(); self.w = EchoWorkspace(self.db)
        self.assertIn('index', self.w.query({'operation': 'neighbors', 'word': 'paperclip'})['neighbors'])
        self.assertEqual(len(self.w.query({'operation': 'relations', 'card_id': 'word:clip'})), 1)

    def test_catalog_template_restores_versions_and_graph(self):
        self.w.paperclip('clip:1', 'word:clip', 'word:index')
        self.w.save_template('layout', 'Layout', {'columns': ['word']}, ['word:clip', 'word:index', 'clip:1'])
        self.w.restore('layout', 'instance')
        self.w.put_word('word:clip', 'paperclip', 'revised definition', department='noun', expected_revision=1)
        graph = self.w.configuration_graph('instance')
        self.assertEqual(next(n for n in graph['nodes'] if n['id'] == 'word:clip')['revision'], 1)
        self.assertEqual(graph['relations'][0]['relation_type'], 'paperclip')
        self.assertEqual(graph['inversion'], 'unresolved-not-executed')

    def test_read_only_caller_cannot_mutate(self):
        with EchoWorkspace(self.db) as readonly:
            self.assertTrue(readonly.query({'operation': 'cards'}))
            for f in [lambda: readonly.seed_profiles(),
                      lambda: readonly.paperclip('bad', 'word:clip', 'word:index'),
                      lambda: readonly.stamp_matches('word:clip'),
                      lambda: readonly.restore('anything', 'new')]:
                with self.assertRaises(PermissionError): f()

    def test_inactive_governor_blocks_adapter(self):
        self.w.matrix.known['A-000']['status'] = 'INACTIVE'
        with self.assertRaises(PermissionError):
            self.w.paperclip('blocked', 'word:clip', 'word:index')
        with self.assertRaises(PermissionError):
            self.w.query({'operation': 'cards'})

    def test_query_does_not_dispatch_arbitrary_code(self):
        with self.assertRaises(ValueError):
            self.w.query({'operation': '__import__', 'code': 'raise Exception()'})

    def test_duplicate_word_identity_rejected(self):
        with self.assertRaises(Conflict):
            self.w.put_word('different-id', 'paperclip', 'other definition')


if __name__ == '__main__':
    unittest.main()
