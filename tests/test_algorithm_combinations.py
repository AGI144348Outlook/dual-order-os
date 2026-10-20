import ast
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
    def test_catalog_references_existing_code_or_explicit_external_branch(self):
        entries=json.loads((ROOT/'libraries/algorithms/mapped-combinations/catalog.json').read_text())['combinations']
        ids=[e['id'] for e in entries];self.assertEqual(len(ids),len(set(ids)))
        for entry in entries:
            self.assertFalse(entry['auto_dispatch'])
            for ref in entry['code']:
                if entry.get('source_branch'):continue
                source=ROOT/ref['path'];self.assertTrue(source.is_file(),ref['path'])
                node=ast.parse(source.read_text())
                for part in ref['callable'].split('.'):
                    choices=[n for n in node.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==part]
                    self.assertTrue(choices,ref);node=choices[0]
