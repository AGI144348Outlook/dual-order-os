"""Resolution: every token's meaning comes from a registry, never from its surface.

- Hebrew glyphs: the authoritative Hebrew Glyph Registry (algebra branch), loaded from data/.
- Words: ECHO's Registry; optionally WordNet when it is installed (CPython), not in offline Pyodide.
- Records: experiment results (e.g. C-05, A-177) supplied as data.
"""
import json, os

_here = os.path.dirname(__file__)
with open(os.path.join(_here, "data", "hebrew_glyph_registry.json"), encoding="utf-8") as f:
    _g = json.load(f)
GLYPHS = {r["glyph"]: r for r in _g["records"]}                  # ל -> {ordinal, glyph, operation}
OPERATION_TO_GLYPH = {r["operation"]: r["glyph"] for r in _g["records"]}

try:
    from nltk.corpus import wordnet as _wn
    _wn.synsets("dog")
    WORDNET = _wn
except Exception:
    WORDNET = None

# Operator signatures (argument kinds -> result kind). Glyph operators take anything and yield an Operation.
SIGNATURES = {
    "GENERALIZE": (("Resident", "Quantity"), "ResidentSet"),
    "SPECIFY": (("Resident", "Quantity"), "ResidentSet"),
    "PRESENTIATE": (("Resident",), "Manifestation"),
    "%": (("Any",), "Same"),                                    # inversion returns the kind it was given
}
for op in OPERATION_TO_GLYPH:
    SIGNATURES.setdefault(op, (("Any",), "Operation"))
RELATION_SIGNATURES = {"is_a": ("Resident", "Resident"), "includes": ("Resident", "Resident"),
                       "antonym_of": ("Resident", "Resident")}


class Lexicon:
    def __init__(self, registry=None, records=None):
        self.registry = registry
        self.records = records or {}

    def word_known(self, w):
        w = w.replace("_", " ").lower()
        if self.registry is not None and self.registry.has(w):
            return True
        return bool(WORDNET and WORDNET.synsets(w.replace(" ", "_")))

    def word_pos(self, w):
        if not WORDNET:
            return {"n"} if self.registry is not None and self.registry.has(w) else set()
        return {s.pos().replace("s", "a") for s in WORDNET.synsets(w.replace(" ", "_"))}
