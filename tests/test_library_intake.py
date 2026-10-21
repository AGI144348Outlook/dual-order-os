"""Synthetic extraction-parser checks; no private PDF text in fixtures."""
import unittest
from tools.observe_library_intake import candidates

class LibraryCandidateTests(unittest.TestCase):
    def test_page_break_heading_and_literal_glyphs_are_preserved(self):
        text='## Mashet E-Dictionary: Aleph Family\n\f### 1. \u202bא\u202c (Fixture)\nDescription.\n'
        row=candidates(text)[0]
        self.assertEqual(row['family'],'Aleph')
        self.assertEqual(row['first_page'],2)
        self.assertIn('\u202bא\u202c',row['heading'])
        self.assertEqual(text[row['start_codepoint']:row['end_codepoint']],row['raw_text'])

    def test_repeated_titles_keep_distinct_source_positions(self):
        text='## Mashet E-Dictionary: Bet Family\n### 1. Same title\nFirst.\n### 2. Same title\nSecond.'
        rows=candidates(text)
        self.assertEqual(len(rows),2)
        self.assertNotEqual(rows[0]['start_codepoint'],rows[1]['start_codepoint'])
        self.assertEqual([r['ordinal'] for r in rows],[1,2])

    def test_new_family_and_standalone_glyph_do_not_join_previous_entry(self):
        text='## Mashet E-Dictionary: Aleph Family\n### 30. Fixture\nBody.\n\f\u202bב\u202c\n\f## Mashet E-Dictionary: Bet Family\n### 1. Next\nNext body.'
        rows=candidates(text)
        self.assertNotIn('Bet Family',rows[0]['raw_text'])
        self.assertNotIn('ב',rows[0]['raw_text'])
        self.assertEqual(rows[1]['family'],'Bet')

    def test_missing_family_is_unresolved_not_invented(self):
        row=candidates('### 1. Unfinished heading\nUnfinished [')[0]
        self.assertEqual(row['family'],'unresolved')
        self.assertTrue(row['raw_text'].endswith('['))
        self.assertEqual(row['status'],'source-description-not-executable-or-verified')
