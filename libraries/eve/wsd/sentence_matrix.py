#!/usr/bin/env python3
# =============================================================================
# SENTENCE-MATRIX: unresolved word-matrices, collapsed jointly
#
# Instead of resolving each word left-to-right (sequential_wsd.py /
# grammar_gated_wsd.py), every ambiguous word's full candidate list stays
# UNRESOLVED — a "word matrix" — and multiple word-matrices sit together,
# unresolved, inside a "sentence matrix." Only then does a single joint
# collapse operation pick one sense per word, maximizing total coherence
# ACROSS all ambiguous words at once, not one at a time.
#
# This is the literal collapse operation the earlier "superposition" claim
# needed and didn't have: a word held as a genuine set of possibilities
# until interaction with the rest of the sentence resolves it.
#
# Test case: TWO ambiguous words in one sentence that should disambiguate
# EACH OTHER — something sequential, one-word-at-a-time resolution cannot
# exploit, since it never considers another ambiguous word's candidates
# as part of the evidence.
# =============================================================================

import sys
sys.path.insert(0, '/home/claude/lexicon_eve')
import nltk
nltk.data.path.append('/home/claude/nltk_data')
from nltk.corpus import wordnet as wn
from itertools import product
from lin_scoring import lin_score
import re

TAG_MAP = {
    "NN": wn.NOUN, "NNS": wn.NOUN, "NNP": wn.NOUN, "NNPS": wn.NOUN,
    "VB": wn.VERB, "VBD": wn.VERB, "VBG": wn.VERB, "VBN": wn.VERB,
    "VBP": wn.VERB, "VBZ": wn.VERB,
    "JJ": wn.ADJ, "JJR": wn.ADJ, "JJS": wn.ADJ,
    "RB": wn.ADV, "RBR": wn.ADV, "RBS": wn.ADV,
}
STOPWORDS = {"the", "a", "an", "and", "or", "but", "is", "was", "were", "of",
             "in", "on", "at", "to", "for", "with", "near", "it", "its"}


def wn_pos(tag):
    return TAG_MAP.get(tag)


def chain(synset):
    try:
        return set(s.name() for s in synset.hypernym_paths()[0])
    except Exception:
        return set()


class WordMatrix:
    """One ambiguous word, held UNRESOLVED — the full set of candidate
    senses, none chosen yet."""
    def __init__(self, word, pos):
        self.word = word
        self.pos = pos
        self.candidates = wn.synsets(word, pos=pos) if pos else []
        self.chains = {c.name(): chain(c) for c in self.candidates}

    def is_ambiguous(self):
        return len(self.candidates) > 1


class SentenceMatrix:
    """Multiple word-matrices held together, unresolved, until collapse()
    runs. This IS the sentence-level structure — not a list of independent
    resolutions, one object holding everyone's possibilities at once."""

    def __init__(self, sentence):
        self.sentence = sentence
        tokens = re.findall(r"[a-zA-Z']+", sentence)
        self.tagged = nltk.pos_tag(tokens)
        self.word_matrices = {}
        self.fixed_context_synsets = []  # unambiguous words' chains, fixed evidence

        for w, t in self.tagged:
            if w.lower() in STOPWORDS:
                continue
            pos = wn_pos(t)
            if pos is None:
                continue
            wm = WordMatrix(w, pos)
            if wm.is_ambiguous():
                self.word_matrices[w] = wm
            elif wm.candidates:
                self.fixed_context_synsets.append(wm.candidates[0])

    def collapse(self):
        """The actual collapse operation. Try every joint combination of
        senses across ALL ambiguous words simultaneously, score each
        combination by total coherence (mutual overlap between the chosen
        senses of DIFFERENT ambiguous words, PLUS overlap with fixed
        unambiguous context), and pick the single best joint assignment."""
        if not self.word_matrices:
            return {}

        words = list(self.word_matrices.keys())
        candidate_lists = [self.word_matrices[w].candidates for w in words]

        best_assignment = None
        best_score = -1
        all_scores = []

        for combo in product(*candidate_lists):
            score = 0
            combo_chains = [chain(c) for c in combo]

            # Mutual coherence BETWEEN the ambiguous words' chosen senses —
            # the part sequential resolution structurally cannot see, since
            # it only ever looks at ONE target word against fixed context.
            for i in range(len(combo)):
                for j in range(i + 1, len(combo)):
                    score += lin_score(combo[i], combo[j])

            # Plus coherence with fixed unambiguous context words.
            for c_syn in combo:
                for fixed_syn in self.fixed_context_synsets:
                    score += lin_score(c_syn, fixed_syn)

            all_scores.append((combo, score))
            if score > best_score:
                best_score = score
                best_assignment = combo

        result = dict(zip(words, best_assignment))
        return result, best_score, sorted(all_scores, key=lambda x: -x[1])


def run(sentence):
    print(f"\nSentence: \"{sentence}\"")
    sm = SentenceMatrix(sentence)

    print(f"Ambiguous word-matrices (held UNRESOLVED): "
          f"{[(w, len(wm.candidates)) for w, wm in sm.word_matrices.items()]}")
    print(f"Fixed context chains (unambiguous words): {len(sm.fixed_context_synsets)}")

    if not sm.word_matrices:
        print("  No ambiguous words to jointly resolve.")
        return

    result, best_score, all_scores = sm.collapse()

    print(f"\nJOINT COLLAPSE — best combined assignment (score={best_score}):")
    for w, syn in result.items():
        print(f"  {w:10s} -> {syn.name():15s} \"{syn.definition()}\"")

    print(f"\nTop 3 combinations considered, for comparison:")
    for combo, score in all_scores[:3]:
        desc = ", ".join(f"{c.name()}" for c in combo)
        print(f"  score={score:.3f}  [{desc}]")


if __name__ == "__main__":
    print("=" * 78)
    print(" SENTENCE-MATRIX — words held unresolved, collapsed jointly")
    print("=" * 78)

    # bank and spring should mutually disambiguate: geographic/water senses
    # of BOTH words score higher together than any other pairing — something
    # sequential, one-word-at-a-time resolution structurally cannot exploit.
    run("The steep bank near the spring was covered in moss.")
