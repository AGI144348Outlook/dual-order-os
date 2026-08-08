#!/usr/bin/env python3
# =============================================================================
# ENGLISH LEXICONAL EVE
#
# EVE = Enveloping Virtual Environment. Under the Dual-Order OS, EVE is the
# Index-of-Matrices layer: given a direction (angle) from the shared (0,0,0)
# anchor, resolve which NVE occupies it. Each NVE (a word) is itself a
# Matrix-of-Indices — its own internal content (definition, category, etc.)
#
# NVEs are placed via a golden-angle Fibonacci sphere, same technique eve3
# already uses for the 22 Hebrew letters — generalized here to open-ended
# vocabulary size instead of a fixed 22.
#
# Built as a CONTROLLED TEST, not just a demo: the same word set is inserted
# two ways — grouped by semantic category, and alphabetically (meaningless
# baseline) — to check whether angular clustering reflects anything beyond
# insertion order.
# =============================================================================

import math
from dataclasses import dataclass, field


GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # ~2.39996 rad, ~137.5 degrees


@dataclass
class NVE:
    """A Nested Virtual Environment — one word. A Matrix of Indices in its
    own right (its internal fields), reachable via EVE's angle-lookup."""
    word: str
    category: str
    index: int
    total: int
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    theta: float = 0.0  # azimuthal angle, radians

    def place(self):
        """Golden-angle Fibonacci sphere placement, anchored at (0,0,0)."""
        i, n = self.index, self.total
        self.y = 1 - (i / (n - 1)) * 2 if n > 1 else 0.0
        radius_at_y = math.sqrt(max(0.0, 1 - self.y * self.y))
        self.theta = GOLDEN_ANGLE * i
        self.x = math.cos(self.theta) * radius_at_y
        self.z = math.sin(self.theta) * radius_at_y

    def __repr__(self):
        return f"<NVE '{self.word}' [{self.category}] @ ({self.x:.3f},{self.y:.3f},{self.z:.3f})>"


@dataclass
class LexiconalEVE:
    """The Index-of-Matrices layer. Anchored at (0,0,0). Holds NVEs and
    resolves angle -> word."""
    name: str
    nves: list = field(default_factory=list)
    anchor: tuple = (0.0, 0.0, 0.0)

    def populate(self, ordered_words: list):
        """ordered_words: list of (word, category) tuples, in the exact
        insertion order that determines their angular position."""
        n = len(ordered_words)
        for i, (word, category) in enumerate(ordered_words):
            nve = NVE(word=word, category=category, index=i, total=n)
            nve.place()
            self.nves.append(nve)

    def nearest(self, x, y, z, k=1):
        """EVE's core job: given a direction, resolve which NVE(s) occupy
        it. This IS the Index-of-Matrices lookup."""
        def dist(nve):
            return math.sqrt((nve.x - x) ** 2 + (nve.y - y) ** 2 + (nve.z - z) ** 2)
        return sorted(self.nves, key=dist)[:k]

    def angular_distance(self, a: NVE, b: NVE):
        """Great-circle distance between two NVEs on the unit sphere."""
        dot = a.x * b.x + a.y * b.y + a.z * b.z
        dot = max(-1.0, min(1.0, dot))
        return math.acos(dot)

    def category_tightness(self):
        """For each category, average pairwise angular distance between
        its words. Lower = tighter cluster. This is the actual test."""
        cats = {}
        for nve in self.nves:
            cats.setdefault(nve.category, []).append(nve)

        results = {}
        for cat, members in cats.items():
            if len(members) < 2:
                continue
            dists = []
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    dists.append(self.angular_distance(members[i], members[j]))
            results[cat] = sum(dists) / len(dists)
        return results


# ── A modest, honest test set: 6 categories, 8 words each ──────────────────
CATEGORIZED_WORDS = {
    "animal":  ["wolf", "otter", "hawk", "salmon", "bear", "heron", "fox", "elk"],
    "emotion": ["joy", "grief", "anger", "awe", "shame", "hope", "dread", "calm"],
    "motion":  ["run", "drift", "leap", "crawl", "spin", "fall", "surge", "glide"],
    "water":   ["river", "tide", "rain", "wave", "spring", "flood", "mist", "brine"],
    "fire":    ["flame", "ember", "blaze", "spark", "ash", "kindle", "smoke", "pyre"],
    "time":    ["dawn", "dusk", "epoch", "moment", "season", "cycle", "eve", "eon"],
}


def build_grouped_order():
    """Semantic order: all of one category together, then the next."""
    ordered = []
    for cat, words in CATEGORIZED_WORDS.items():
        for w in words:
            ordered.append((w, cat))
    return ordered


def build_alphabetical_order():
    """Meaningless baseline: same words, sorted alphabetically — insertion
    order has nothing to do with category."""
    flat = []
    for cat, words in CATEGORIZED_WORDS.items():
        for w in words:
            flat.append((w, cat))
    flat.sort(key=lambda pair: pair[0])
    return flat


def run_test():
    print("=" * 70)
    print(" ENGLISH LEXICONAL EVE — grouped-order vs. alphabetical-order test")
    print("=" * 70)
    print()

    grouped_eve = LexiconalEVE(name="lexicon-grouped")
    grouped_eve.populate(build_grouped_order())

    alpha_eve = LexiconalEVE(name="lexicon-alphabetical")
    alpha_eve.populate(build_alphabetical_order())

    print(f"Total NVEs per EVE: {len(grouped_eve.nves)}")
    print()

    grouped_tightness = grouped_eve.category_tightness()
    alpha_tightness = alpha_eve.category_tightness()

    print(f"{'category':10s}  {'grouped (rad)':>14s}  {'alphabetical (rad)':>19s}  {'tighter?':>10s}")
    print("-" * 62)
    grouped_wins = 0
    for cat in CATEGORIZED_WORDS:
        g = grouped_tightness[cat]
        a = alpha_tightness[cat]
        tighter = "grouped" if g < a else "alpha"
        if g < a:
            grouped_wins += 1
        print(f"{cat:10s}  {g:14.4f}  {a:19.4f}  {tighter:>10s}")

    print()
    print(f"Grouped ordering was tighter in {grouped_wins}/{len(CATEGORIZED_WORDS)} categories.")
    print()
    print("-- What this test actually shows --")
    print("If grouped consistently beats alphabetical (expected: yes, all 6/6),")
    print("that CONFIRMS the mechanism works as designed — insertion order maps")
    print("to angular proximity. It does NOT by itself show the lattice discovered")
    print("meaning; it shows the golden-angle math faithfully encodes whatever")
    print("order you feed it. The open question from before — whether meaningful")
    print("clusters emerge beyond what deliberate ordering already guarantees —")
    print("would need a THIRD condition: insertion order derived independently")
    print("of category (e.g. by real semantic embedding distance, or by usage")
    print("frequency) and checking if categories cluster anyway, without being")
    print("told to.")
    print()

    # Example EVE lookup — the actual Index-of-Matrices operation.
    sample = grouped_eve.nves[0]
    print(f"Example EVE resolve(): nearest neighbors of '{sample.word}' "
          f"[{sample.category}] in grouped EVE:")
    for nve in grouped_eve.nearest(sample.x, sample.y, sample.z, k=4):
        print(f"    {nve}")

    return grouped_eve, alpha_eve


if __name__ == "__main__":
    run_test()
