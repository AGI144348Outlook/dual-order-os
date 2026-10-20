#!/usr/bin/env python3
# =============================================================================
# BIDIRECTIONAL by-glyph INDEX
#
# The dual-order principle applied to the index itself, not just the repo
# structure: glyph -> roots/senses (Matrix-of-Indices direction) and
# root+sense -> glyph (Index-of-Matrices direction) are BOTH first-class,
# not one primary with a bolted-on reverse lookup.
#
# A root is not enough to resolve a glyph on its own — "spring" needs its
# SENSE specified too, same as WordNet needed spring.n.03 vs spring.n.01
# pinned explicitly. So the real key on both sides is (root, sense), not
# just root.
# =============================================================================

from dataclasses import dataclass, field


@dataclass
class GlyphRootEntry:
    root: str
    sense: str          # human-readable sense gloss, disambiguating like a synset
    glyph: str
    opcode: str
    note: str = ""


class BidirectionalGlyphRootIndex:
    def __init__(self):
        self.entries = []
        self._by_glyph = {}          # glyph -> [entries]
        self._by_root_sense = {}     # (root, sense) -> entry

    def add(self, entry: GlyphRootEntry):
        self.entries.append(entry)
        self._by_glyph.setdefault(entry.glyph, []).append(entry)
        self._by_root_sense[(entry.root, entry.sense)] = entry

    # Matrix-of-Indices direction: given the glyph, what does it govern?
    def roots_for_glyph(self, glyph: str):
        return self._by_glyph.get(glyph, [])

    # Index-of-Matrices direction: given a specific sense, which glyph applies?
    def glyph_for_root_sense(self, root: str, sense: str):
        entry = self._by_root_sense.get((root, sense))
        return entry.glyph if entry else None

    # What senses exist for an ambiguous root, so a caller can pick correctly.
    def senses_for_root(self, root: str):
        return [e for e in self.entries if e.root == root]


def build_index():
    idx = BidirectionalGlyphRootIndex()

    # "spring" — the exact word that broke the WordNet test earlier.
    # Two senses, two DIFFERENT glyphs, same root text.
    idx.add(GlyphRootEntry(
        root="spring", sense="natural flow of ground water",
        glyph="מ", opcode="Mem — Flow/Transition",
        note="matches spring.n.03 — the water-source sense"
    ))
    idx.add(GlyphRootEntry(
        root="spring", sense="the season of growth",
        glyph="ק", opcode="Qof — Order/Alignment (cyclical)",
        note="matches spring.n.01 — the season sense; Qof chosen for its "
             "cyclical/time-alignment role, distinct from spring's water sense"
    ))

    # A few more roots already established this session, for context —
    # each with only one sense so far, to show the structure handles both
    # ambiguous and unambiguous roots without special-casing.
    idx.add(GlyphRootEntry(
        root="colleg-", sense="to gather", glyph="מ", opcode="Mem — Flow/Transition",
        note="Genesis-1 gathering phase"
    ))
    idx.add(GlyphRootEntry(
        root="sec-", sense="to cut", glyph="ג", opcode="Gimel — Motion/Transfer",
        note="Genesis-1 structural phase"
    ))

    return idx


def demo():
    idx = build_index()

    print("=" * 70)
    print(" BIDIRECTIONAL by-glyph INDEX — spring as the worked example")
    print("=" * 70)
    print()

    print("-- Index-of-Matrices direction: root+sense -> glyph --")
    water_glyph = idx.glyph_for_root_sense("spring", "natural flow of ground water")
    season_glyph = idx.glyph_for_root_sense("spring", "the season of growth")
    print(f"  spring [water-source sense] -> {water_glyph} (Mem, Flow/Transition)")
    print(f"  spring [season sense]       -> {season_glyph} (Qof, cyclical Order/Alignment)")
    print(f"  Same root text, two different glyphs — resolved by SENSE, not root alone.")
    print()

    print("-- Ambiguity check: what senses exist for 'spring'? --")
    for e in idx.senses_for_root("spring"):
        print(f"  '{e.sense}' -> {e.glyph} ({e.opcode})")
    print()

    print("-- Matrix-of-Indices direction: glyph -> roots/senses it governs --")
    for glyph in ["מ", "ק", "ג"]:
        entries = idx.roots_for_glyph(glyph)
        names = [f"{e.root} [{e.sense}]" for e in entries]
        print(f"  {glyph}: {', '.join(names)}")
    print()

    print("-- Why this matters --")
    print("A one-directional (root -> glyph) table would have forced 'spring' to pick")
    print("ONE glyph, silently wrong half the time — the exact bug WordNet's default-sense")
    print("lookup had. Making both directions first-class, keyed on (root, sense) rather")
    print("than root alone, is what actually fixes it at the architecture level instead")
    print("of patching it case by case.")


if __name__ == "__main__":
    demo()
