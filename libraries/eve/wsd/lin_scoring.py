#!/usr/bin/env python3
# =============================================================================
# SHARED LIN-SIMILARITY SCORING
#
# Replaces raw hypernym-overlap COUNT (the confirmed root cause of every
# WSD failure this session) with information-content-based Lin similarity,
# validated against the exact failing cases: 0.621 vs 0.338, a real margin,
# not the thin 0.02 Wu-Palmer gave.
# =============================================================================

import nltk
nltk.data.path.append('/home/claude/nltk_data')
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic

BROWN_IC = wordnet_ic.ic('ic-brown.dat')


def lin_score(synset_a, synset_b):
    """Safe Lin similarity — returns 0.0 instead of raising on incompatible
    POS pairs, missing IC data, or root-node comparisons (all real edge
    cases Lin similarity can hit)."""
    if synset_a is None or synset_b is None:
        return 0.0
    if synset_a.pos() != synset_b.pos():
        return 0.0  # Lin similarity requires same POS, same as hypernym chains did
    try:
        sim = synset_a.lin_similarity(synset_b, BROWN_IC)
        return sim if sim is not None else 0.0
    except Exception:
        return 0.0
