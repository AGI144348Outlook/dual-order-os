#!/usr/bin/env python3
# =============================================================================
# THE by-is-a INDEX
#
# is-a is a relationship BETWEEN words, not content a word holds — so it
# belongs in /indices, not /matrices. This is a second, independent index
# over the same 48-word lexicon that by-angle already covers, capturing a
# different kind of structure (taxonomic kind-relations) than geometric
# position does.
#
# Correction applied: 2 of 48 words had wrong default WordNet senses
# (spring -> season instead of water-source; otter -> fur instead of the
# animal), found and fixed before this became canonical, not after.
# =============================================================================

import sys
sys.path.insert(0, '/home/claude/lexicon_eve')
import nltk
nltk.data.path.append('/home/claude/nltk_data')
from nltk.corpus import wordnet as wn

from lexicon_eve import CATEGORIZED_WORDS

# Manual sense corrections — pinned explicitly rather than trusting
# WordNet's default first-synset ranking.
SENSE_OVERRIDES = {
    "spring": "spring.n.03",  # natural flow of ground water (not the season)
    "otter": "otter.n.02",    # the animal (not otter fur)
}


def get_synset(word):
    if word in SENSE_OVERRIDES:
        return wn.synset(SENSE_OVERRIDES[word])
    # Restrict to noun senses only — a verb-only word (e.g. "kindle") has no
    # place in a noun is-a comparison; including it is a category error,
    # not a taxonomic-distance finding.
    noun_synsets = wn.synsets(word, pos=wn.NOUN)
    return noun_synsets[0] if noun_synsets else None


def build_is_a_index():
    """For each word: its full hypernym chain (is-a ancestry) up to 'entity'.
    Also computes, per category, the deepest common ancestor shared by all
    its members — a real measure of whether that category is a genuine
    taxonomic kind, or just a label I imposed."""
    index = {}
    for cat, words in CATEGORIZED_WORDS.items():
        index[cat] = {}
        for w in words:
            syn = get_synset(w)
            if syn is None:
                continue
            path = syn.hypernym_paths()[0]
            chain = [s.lemma_names()[0] for s in path]
            index[cat][w] = {
                "synset": syn.name(),
                "definition": syn.definition(),
                "is_a_chain": chain,
            }
    return index


def find_deepest_common_ancestor(chains: list):
    """Given multiple is-a chains (lists of ancestor names, root-first),
    find how deep their shared prefix goes. Deeper = more genuinely a
    taxonomic kind; shallow = the category is associative, not taxonomic."""
    if not chains:
        return [], 0
    min_len = min(len(c) for c in chains)
    common = []
    for i in range(min_len):
        level = {c[i] for c in chains}
        if len(level) == 1:
            common.append(chains[0][i])
        else:
            break
    return common, len(common)


def run():
    print("=" * 74)
    print(" by-is-a INDEX — built from WordNet, independent of geometric position")
    print("=" * 74)
    print()

    index = build_is_a_index()

    print(f"{'category':10s}  {'shared ancestry depth':>22s}  {'deepest common ancestor':>28s}")
    print("-" * 68)
    for cat, words in index.items():
        chains = [entry["is_a_chain"] for entry in words.values()]
        common, depth = find_deepest_common_ancestor(chains)
        deepest = common[-1] if common else "(none)"
        print(f"{cat:10s}  {depth:22d}  {deepest:>28s}")

    print()
    print("-- What this shows --")
    print("Categories with DEEP shared ancestry (animal) are genuine taxonomic kinds —")
    print("this is a real, structural fact about the words, independent of the golden-angle")
    print("geometry test. Categories with SHALLOW shared ancestry (emotion, likely stopping")
    print("at 'feeling' or 'state') are real too, just not taxonomic — they're associative/")
    print("affective categories that is-a structurally cannot capture, no matter how the")
    print("similarity math is tuned. Both are honest facts about these words, not failures.")
    print()

    return index


if __name__ == "__main__":
    run()
