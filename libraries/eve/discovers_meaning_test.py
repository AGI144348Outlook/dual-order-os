#!/usr/bin/env python3
# =============================================================================
# THE DISCOVERS-MEANING TEST
#
# Condition 1 (from before): grouped-by-category insertion order (meaningful,
#   but by fiat — I hand-picked the categories).
# Condition 2 (from before): alphabetical insertion order (meaningless
#   baseline).
# Condition 3 (NEW, this file): insertion order derived from WordNet's own
#   taxonomic structure — built by lexicographers with zero knowledge of
#   my category labels. If category clusters show up tightly under THIS
#   ordering too, that's real evidence the lattice is tracking something
#   about meaning, not just replaying an order I imposed.
#
# Method for condition 3: pairwise WordNet path_similarity between all 48
# words, then a greedy nearest-neighbor chain (start anywhere, repeatedly
# walk to the most similar not-yet-visited word). This produces a sequence
# where semantic neighbors tend to sit close in the ORDER — but critically,
# the ordering algorithm never sees my category labels at all.
# =============================================================================

import sys
sys.path.insert(0, '/home/claude/lexicon_eve')
import nltk
nltk.data.path.append('/home/claude/nltk_data')
from nltk.corpus import wordnet as wn

from lexicon_eve import LexiconalEVE, CATEGORIZED_WORDS, build_grouped_order, build_alphabetical_order


def get_synset(word):
    synsets = wn.synsets(word)
    return synsets[0] if synsets else None


def build_wordnet_order():
    """Greedy nearest-neighbor chain through WordNet path_similarity.
    Never references CATEGORIZED_WORDS' category labels — only the words
    themselves and WordNet's independent taxonomy."""
    flat_words = []
    for cat, words in CATEGORIZED_WORDS.items():
        for w in words:
            flat_words.append((w, cat))  # category kept ONLY for later scoring, not for ordering

    synsets = {}
    for word, cat in flat_words:
        syn = get_synset(word)
        synsets[word] = syn

    missing = [w for w, s in synsets.items() if s is None]
    if missing:
        print(f"[WARN] No WordNet synset found for: {missing} — excluding from this test.")
    flat_words = [(w, c) for w, c in flat_words if synsets[w] is not None]

    remaining = list(flat_words)
    chain = [remaining.pop(0)]  # arbitrary start — first word alphabetically encountered in dict
    while remaining:
        current_word = chain[-1][0]
        current_syn = synsets[current_word]

        def sim(pair):
            w, c = pair
            s = current_syn.path_similarity(synsets[w])
            return s if s is not None else 0.0

        remaining.sort(key=sim, reverse=True)
        chain.append(remaining.pop(0))

    return chain


def run_discovers_meaning_test():
    print("=" * 74)
    print(" THE DISCOVERS-MEANING TEST")
    print(" Condition 3: WordNet-derived order (independent of my category labels)")
    print("=" * 74)
    print()

    wn_order = build_wordnet_order()
    print("WordNet-derived insertion order (first 12 of {}):".format(len(wn_order)))
    print("  " + ", ".join(f"{w}[{c}]" for w, c in wn_order[:12]) + " ...")
    print()

    wn_eve = LexiconalEVE(name="lexicon-wordnet-derived")
    wn_eve.populate(wn_order)

    grouped_eve = LexiconalEVE(name="lexicon-grouped")
    grouped_eve.populate(build_grouped_order())

    alpha_eve = LexiconalEVE(name="lexicon-alphabetical")
    alpha_eve.populate(build_alphabetical_order())

    wn_tight = wn_eve.category_tightness()
    grouped_tight = grouped_eve.category_tightness()
    alpha_tight = alpha_eve.category_tightness()

    print(f"{'category':10s}  {'grouped':>10s}  {'alpha':>10s}  {'wordnet':>10s}  {'verdict':>28s}")
    print("-" * 78)

    wn_beats_alpha = 0
    wn_near_grouped = 0
    for cat in CATEGORIZED_WORDS:
        g = grouped_tight.get(cat, float('nan'))
        a = alpha_tight.get(cat, float('nan'))
        w = wn_tight.get(cat, float('nan'))

        if w < a:
            wn_beats_alpha += 1
        # "near grouped" = within 15% of the hand-grouped tightness
        if g > 0 and abs(w - g) / g < 0.15:
            wn_near_grouped += 1

        verdict = "WordNet tighter than alpha" if w < a else "no better than random"
        print(f"{cat:10s}  {g:10.4f}  {a:10.4f}  {w:10.4f}  {verdict:>28s}")

    print()
    print(f"WordNet-derived order beat the meaningless alphabetical baseline in "
          f"{wn_beats_alpha}/{len(CATEGORIZED_WORDS)} categories.")
    print(f"WordNet-derived order came within 15% of hand-grouped tightness in "
          f"{wn_near_grouped}/{len(CATEGORIZED_WORDS)} categories.")
    print()
    print("-- Honest read --")
    if wn_beats_alpha >= 4:
        print("This is real evidence: an ordering built from WordNet's independent")
        print("taxonomy — which never saw my category labels — still produces tighter")
        print("angular clustering than chance, in most categories. That's closer to")
        print("'the lattice tracks something about meaning' than 'geometric inevitability.'")
    else:
        print("WordNet path_similarity for this word set didn't reliably beat the")
        print("meaningless baseline. That's a real negative result, not a failure of")
        print("the test — it suggests either the word set is too small/ambiguous for")
        print("WordNet's path metric, or the golden-angle scattering effect (seen in")
        print("the first test) is strong enough to wash out a modest semantic signal.")
    print()
    print("What this does NOT yet test: whether the clustering DOES anything —")
    print("supports retrieval, analogy, or any downstream task. Geometric proximity")
    print("existing is a precondition for usefulness, not proof of it.")

    return wn_eve, grouped_eve, alpha_eve


if __name__ == "__main__":
    run_discovers_meaning_test()
