#!/usr/bin/env python3
# =============================================================================
# SEQUENTIAL WSD v2 — rebuilt on Lin similarity
# =============================================================================

import sys
sys.path.insert(0, '/home/claude/lexicon_eve')
import nltk
nltk.data.path.append('/home/claude/nltk_data')
from nltk.corpus import wordnet as wn
import re
from lin_scoring import lin_score

EVO = {"eta": 1.0, "m_hard": 3.5}  # recalibrated: Lin scores are 0-1, not integer counts

STOPWORDS = {"the", "a", "an", "and", "or", "but", "is", "was", "were", "of",
             "in", "on", "at", "to", "for", "with", "down", "up", "it", "its",
             "near", "past"}

TAG_MAP = {
    "NN": wn.NOUN, "NNS": wn.NOUN, "NNP": wn.NOUN, "NNPS": wn.NOUN,
    "VB": wn.VERB, "VBD": wn.VERB, "VBG": wn.VERB, "VBN": wn.VERB,
    "VBP": wn.VERB, "VBZ": wn.VERB,
    "JJ": wn.ADJ, "JJR": wn.ADJ, "JJS": wn.ADJ,
}


def wn_pos(tag):
    return TAG_MAP.get(tag)


class SenseAccumulator:
    def __init__(self, synset):
        self.synset = synset
        self.myelin_accum = 0.0
        self.trace = []

    def receive(self, context_word, cw_pos, position):
        cw_synsets = wn.synsets(context_word, pos=cw_pos)
        if not cw_synsets:
            return 0.0
        sim = lin_score(self.synset, cw_synsets[0])
        if sim == 0.0:
            return 0.0
        delta = EVO["eta"] * sim
        self.myelin_accum += delta
        self.trace.append((position, context_word, round(sim, 3), round(self.myelin_accum, 3)))
        return delta


def resolve(sentence: str, target: str):
    print(f"\nSentence: \"{sentence}\"")
    print(f"Target word: '{target}'")

    tokens = re.findall(r"[a-zA-Z']+", sentence)
    tagged = nltk.pos_tag(tokens)
    target_idx = next((i for i, (w, t) in enumerate(tagged) if w.lower() == target.lower()), None)
    if target_idx is None:
        print("  Target not found.")
        return None

    target_tag = tagged[target_idx][1]
    target_pos = wn_pos(target_tag)
    print(f"Target tagged {target_tag} -> {target_pos}")

    candidates = wn.synsets(target, pos=target_pos)
    accumulators = [SenseAccumulator(s) for s in candidates]

    context = [(w, t) for i, (w, t) in enumerate(tagged)
               if i != target_idx and w.lower() not in STOPWORDS]

    winner = None
    for i, (cw, ctag) in enumerate(context):
        cw_pos = wn_pos(ctag)
        if cw_pos != target_pos:
            continue
        for acc in accumulators:
            acc.receive(cw, cw_pos, i)
        crossed = [a for a in accumulators if a.myelin_accum >= EVO["m_hard"]]
        if crossed:
            winner = max(crossed, key=lambda a: a.myelin_accum)
            break

    print(f"{'sense':30s}  {'accum':>8s}")
    for acc in accumulators:
        marker = " <-- WINNER" if acc is winner else ""
        print(f"{acc.synset.name():30s}  {acc.myelin_accum:8.3f}{marker}")

    if not winner:
        winner = max(accumulators, key=lambda a: a.myelin_accum)
        print(f"(never crossed m_hard={EVO['m_hard']} — best available)")

    print(f"RESOLVED: {winner.synset.name()} — \"{winner.synset.definition()}\"")
    return winner


if __name__ == "__main__":
    print("=" * 74)
    print(" SEQUENTIAL WSD v2 — Lin similarity")
    print("=" * 74)
    resolve("The spring flowed cold and clear down the mountain into the river.", "spring")
    resolve("Every spring the flowers bloom again after the long winter season.", "spring")
    resolve("The cat will spring from the shelf without warning.", "spring")
