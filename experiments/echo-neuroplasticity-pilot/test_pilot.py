"""Guards for the pilot: no hard-coded vocabulary, no answer leakage, frozen quizzes."""
import io
import json
import keyword
import re
import sys
import tokenize
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from echo_np import Echo                      # noqa: E402
from teacher import Classroom                 # noqa: E402
from world import DICTIONARY, PLURAL, World   # noqa: E402

VOCAB = set(DICTIONARY) | set(PLURAL.values())
ALLOWED_ITEM_KEYS = {'type', 'cards', 'options', 'query_words', 'multi', 'words', 'n', 'label', 'example'}


class NoHardCodedVocabulary(unittest.TestCase):
    def test_learner_source_has_no_classroom_words(self):
        src = (HERE / 'echo_np.py').read_text(encoding='utf-8')
        found = set()
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.NAME and keyword.iskeyword(tok.string):
                continue                       # Python's own keywords (e.g. 'not') are syntax
            if tok.type in (tokenize.NAME, tokenize.STRING, tokenize.COMMENT):
                for word in re.findall(r'[A-Za-z]+', tok.string):
                    if word.lower() in VOCAB:
                        found.add(word.lower())
        self.assertEqual(found, set(), f'learner mentions classroom words: {sorted(found)}')

    def test_learner_never_imports_teacher_side(self):
        src = (HERE / 'echo_np.py').read_text(encoding='utf-8')
        self.assertNotRegex(src, r'^\s*(from|import)\s+(world|teacher)\b')


class NoAnswerLeakage(unittest.TestCase):
    def test_items_carry_only_task_fields(self):
        seen = []
        e = Echo(seed=7)
        real = e.attempt

        def spy(item, practice=False):
            seen.append(set(item))
            return real(item, practice)
        e.attempt = spy
        Classroom(e, 7).course()
        self.assertTrue(seen)
        for keys in seen:
            self.assertTrue(keys <= ALLOWED_ITEM_KEYS, f'unexpected fields reached Echo: {keys - ALLOWED_ITEM_KEYS}')

    def test_feedback_only_after_attempt(self):
        order = []
        e = Echo(seed=8)
        ra, rf = e.attempt, e.feedback
        e.attempt = lambda item, practice=False: (order.append('a'), ra(item, practice))[1]
        e.feedback = lambda *a, **k: (order.append('f'), rf(*a, **k))[1]
        Classroom(e, 8).course()
        for i, x in enumerate(order):
            if x == 'f':
                self.assertEqual(order[i - 1], 'a', 'feedback arrived without a preceding attempt')

    def test_percept_codes_change_per_seed(self):
        a, b = World(1), World(2)
        self.assertNotEqual(a.chan, b.chan)
        self.assertTrue(set(a.val.values()).isdisjoint(set(b.val.values())) or a.val != b.val)


class QuizzesAreFrozen(unittest.TestCase):
    def test_quiz_does_not_change_state(self):
        e = Echo(seed=9)
        c = Classroom(e, 9)
        c.board_encounter('ע-1')
        c.recess()
        before = json.dumps(e.snapshot(), sort_keys=True, default=str), e.memory_size(), e.N
        c.run('quiz', c.naming_items(10, heldout=True), 'quiz')
        after = json.dumps(e.snapshot(), sort_keys=True, default=str), e.memory_size(), e.N
        self.assertEqual(before, after)


class Reproducible(unittest.TestCase):
    def test_same_seed_same_results(self):
        r1 = Classroom(Echo(seed=11), 11).course()
        r2 = Classroom(Echo(seed=11), 11).course()
        self.assertEqual(json.dumps(r1, sort_keys=True), json.dumps(r2, sort_keys=True))

    def test_zero_learning_control_runs(self):
        c = Classroom(Echo(seed=12, learn=False), 12)
        c.course()
        self.assertLessEqual(len(c.green), 6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
