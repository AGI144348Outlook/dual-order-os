#!/usr/bin/env python3
# =============================================================================
# TWO-STAGE GRAMMAR-PRINCIPLED SENTENCE MATRIX
#
# Stage 1 — NOUN DESIGNATION (R-loci): all ambiguous nouns are collapsed
#   jointly, isolated from verbs/adjectives entirely, the same way ASL
#   signers assign referents to fixed points in signing space before any
#   verb movement between them is articulated.
#
# Stage 2 — VERB RESOLUTION VIA THE NOW-FIXED NOUNS: verb candidates
#   cannot be compared directly against noun chains (separate WordNet
#   hierarchies, proven broken with "kindle" earlier). Instead, each verb
#   candidate is followed to its OWN derivationally-related noun form(s)
#   via WordNet's real morphological bridge, and THAT noun-form's chain is
#   compared against the now-fixed Stage 1 nouns. This is the affix-relation
#   idea in concrete form: the verb's resolved sense is determined by its
#   relationship to the already-designated nouns, not chosen independently.
# =============================================================================

import sys
sys.path.insert(0, '/home/claude/lexicon_eve')
import nltk
nltk.data.path.append('/home/claude/nltk_data')
from nltk.corpus import wordnet as wn
from itertools import product
from lin_scoring import lin_score
from lin_scoring import lin_score
import re

TAG_MAP = {
    "NN": wn.NOUN, "NNS": wn.NOUN, "NNP": wn.NOUN, "NNPS": wn.NOUN,
    "VB": wn.VERB, "VBD": wn.VERB, "VBG": wn.VERB, "VBN": wn.VERB,
    "VBP": wn.VERB, "VBZ": wn.VERB,
}
STOPWORDS = {"the", "a", "an", "and", "or", "but", "is", "was", "were", "of",
             "in", "on", "at", "to", "for", "with", "near", "past", "it", "its"}


def wn_pos(tag):
    return TAG_MAP.get(tag)


def chain(synset):
    try:
        return set(s.name() for s in synset.hypernym_paths()[0])
    except Exception:
        return set()


def verb_bridge_synsets(verb_synset):
    """Follow a verb sense to its derivationally-related noun synset(s).
    Empty if no bridge exists for this sense."""
    synsets = []
    for lemma in verb_synset.lemmas():
        for related in lemma.derivationally_related_forms():
            if related.synset().pos() == 'n':
                synsets.append(related.synset())
    return synsets


def stage1_designate_nouns(tagged):
    """R-loci: resolve all ambiguous nouns jointly, isolated from verbs."""
    noun_matrices = {}
    fixed_noun_synsets = []

    for w, t in tagged:
        if w.lower() in STOPWORDS or wn_pos(t) != wn.NOUN:
            continue
        candidates = wn.synsets(w, pos=wn.NOUN)
        if len(candidates) > 1:
            noun_matrices[w] = candidates
        elif candidates:
            fixed_noun_synsets.append(candidates[0])

    if not noun_matrices:
        return {}, fixed_noun_synsets

    words = list(noun_matrices.keys())
    candidate_lists = [noun_matrices[w] for w in words]

    best_assignment, best_score = None, -1
    for combo in product(*candidate_lists):
        score = 0
        for i in range(len(combo)):
            for j in range(i + 1, len(combo)):
                score += lin_score(combo[i], combo[j])
        for c_syn in combo:
            for fixed_syn in fixed_noun_synsets:
                score += lin_score(c_syn, fixed_syn)
        if score > best_score:
            best_score = score
            best_assignment = combo

    resolved = dict(zip(words, best_assignment))
    all_noun_synsets = fixed_noun_synsets + list(resolved.values())
    return resolved, all_noun_synsets


def stage2_resolve_verbs(tagged, fixed_noun_chains):
    """Verbs resolved via the derivational bridge against the NOW-FIXED
    noun chains from Stage 1 — relationship to already-designated nouns,
    not independent resolution."""
    results = {}
    for w, t in tagged:
        if w.lower() in STOPWORDS or wn_pos(t) != wn.VERB:
            continue
        candidates = wn.synsets(w, pos=wn.VERB)
        if len(candidates) <= 1:
            continue

        best_syn, best_score = None, -1
        for syn in candidates:
            bridge_synsets = verb_bridge_synsets(syn)
            score = 0
            for bs in bridge_synsets:
                for ns in fixed_noun_chains:
                    score += lin_score(bs, ns)
            if score > best_score:
                best_score = score
                best_syn = syn
        results[w] = (best_syn, best_score)
    return results


def run(sentence):
    print(f"\nSentence: \"{sentence}\"")
    tokens = re.findall(r"[a-zA-Z']+", sentence)
    tagged = nltk.pos_tag(tokens)
    print(f"POS tags: {tagged}")

    print("\n-- STAGE 1: Noun designation (R-loci) --")
    resolved_nouns, all_noun_chains = stage1_designate_nouns(tagged)
    for w, syn in resolved_nouns.items():
        print(f"  {w:10s} -> {syn.name():15s} \"{syn.definition()}\"  [DESIGNATED]")

    print("\n-- STAGE 2: Verb resolution via now-fixed nouns --")
    resolved_verbs = stage2_resolve_verbs(tagged, all_noun_chains)
    for w, (syn, score) in resolved_verbs.items():
        if syn:
            print(f"  {w:10s} -> {syn.name():15s} \"{syn.definition()}\"  (bridge score={score})")
        else:
            print(f"  {w:10s} -> no bridge found, unresolved")


if __name__ == "__main__":
    print("=" * 78)
    print(" TWO-STAGE GRAMMAR-PRINCIPLED RESOLUTION — nouns first, verbs via relation")
    print("=" * 78)
    run("The water at the spring flowed past the steep bank.")
