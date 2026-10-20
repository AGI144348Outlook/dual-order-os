import unittest
from tools.test_glyph_vocabulary import SELECTIONS
from libraries.echo_workspace import EchoWorkspace
from libraries.echo_sentence_cards import SentenceCards, sense_id
import tempfile
from pathlib import Path

class VocabularyClippingTests(unittest.TestCase):
    def test_sense_specific_clips_survive_reopen_without_profile_changes(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / 'cards.sqlite'
            cards = SentenceCards(db)
            cards.ingest({'match': {'senses': [
                {'pos': 'verb', 'def': 'Test fixture: compare characteristics'},
                {'pos': 'noun', 'def': 'Test fixture: fire-lighting object'}]}}, source={'kind': 'test-fixture'})
            cards.close()
            w = EchoWorkspace(db, capabilities=EchoWorkspace.ALL_CAPABILITIES)
            w.seed_profiles()
            profile = w.box.get('cards', 'glyph:resh')
            relation = w.paperclip('test:match', sense_id('match', 0), 'glyph:resh')
            self.assertEqual(w.paperclip('test:match', sense_id('match', 0), 'glyph:resh'), relation)
            self.assertEqual(w.box.get('cards', 'glyph:resh'), profile)
            self.assertEqual(relation['body']['source']['id'], sense_id('match', 0))
            w.close()
            w = EchoWorkspace(db)
            self.assertEqual(w.box.get('cards', 'test:match'), relation)
            with self.assertRaises(PermissionError):
                w.paperclip('test:blocked', sense_id('match', 1), 'glyph:resh')
            w.close()

    def test_perception_and_identification_are_separate_sets(self):
        self.assertEqual(set(SELECTIONS), {'ayin', 'resh'})
        self.assertNotIn(('match', 1), SELECTIONS['resh'])
        self.assertNotIn(('name', 1), SELECTIONS['resh'])
