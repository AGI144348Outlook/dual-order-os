"""Renderers: one syntax tree, several surfaces (English, EMEL notation).

English is produced by grammar rules over the tree (noun phrases with articles,
negation, coordination, pronouns for a subject already in focus), not by filling a
fixed sentence. A small discourse state carries the thread between sentences.
"""
from .ast import Term, Relation, Property, Proportion, Continued, Apply, Not, Join
from .lexicon import GLYPHS

VOWEL_SOUND_EXCEPT_A = ("uni", "use", "usu", "uti", "one", "eu", "ur")   # "a unit", "a one"
VOWEL_SOUND_EXCEPT_AN = ("hour", "honest", "honor", "heir")               # "an hour"


def article(word):
    w = word.lower()
    if w.startswith(VOWEL_SOUND_EXCEPT_AN): return "an"
    if w.startswith(VOWEL_SOUND_EXCEPT_A): return "a"
    return "an" if w[:1] in "aeiou" else "a"


def words(t: Term):
    return t.surface.replace("_", " ")


def np(t: Term, det=True):
    """Noun phrase for a term."""
    if t.kind == "GlyphOperator" and t.surface in GLYPHS:
        return f"{t.surface} ({GLYPHS[t.surface]['operation']})"
    if t.kind == "GlyphString":
        return f"the glyph string {t.surface}"
    if t.substrate in ("record", "number", "text") or not det:
        return words(t)
    w = words(t).lower()
    return f"{article(w)} {w}"


class Discourse:
    """Remembers the entity in focus so the next sentence can say 'its' instead of repeating it."""
    def __init__(self):
        self.focus = None


def clause(n, ds, neg=False):
    no = " not" if neg else ""
    if isinstance(n, Not):
        return clause(n.clause, ds, not neg)
    if isinstance(n, Relation):
        ds.focus = None
        if n.op == "is_a": return f"{np(n.source)} is{no} {np(n.target)}"
        if n.op == "includes": return f"{np(n.source)}{' does not include' if neg else ' includes'} {np(n.target)}"
        if n.op == "antonym_of": return f"{np(n.source, False)} is{no} the opposite of {np(n.target, False)}"
    if isinstance(n, Property):
        attr = n.attribute.replace("_", " ")
        if ds.focus == n.subject.canonical:
            subj = f"its {attr}"
        else:
            subj = f"the {attr} of {np(n.subject)}"
            ds.focus = n.subject.canonical
        return f"{subj} is{no} {words(n.value)}"
    if isinstance(n, Proportion):
        ds.focus = None
        return (f"{np(n.a, False)} is{no} to {np(n.b, False)} as {np(n.c, False)} is to {np(n.d, False)}")
    if isinstance(n, Continued):
        ds.focus = None
        q = lambda p: f"{words(p.a).lower()} : {words(p.b).lower()} :: {words(p.c).lower()} : {words(p.d).lower()}"
        if isinstance(n.x, Term):
            x = words(n.x).lower()
            if n.reading == "pivot":
                return f"{x} is{no} the level between the analogy {q(n.p1)} and the analogy {q(n.p2)}"
            if n.reading == "common":
                return f"the analogy {q(n.p1)} and the analogy {q(n.p2)} {'do not both' if neg else 'both'} fall under {x}"
            if n.reading == "hinge":
                return f"the analogy {q(n.p1)} and the analogy {q(n.p2)} {'do not turn' if neg else 'turn'} on {x} in the same sense"
            return f"{x} is{no} between the analogy {q(n.p1)} and the analogy {q(n.p2)}"
        return f"as the analogy {q(n.p1)} is{no} to the analogy {q(n.x)}, so that analogy is to {q(n.p2)}"
    if isinstance(n, Apply):
        ds.focus = None
        op = n.operator
        name = "the inversion" if op.surface == "%" else (np(op) if op.kind == "GlyphOperator" else op.surface)
        return f"{'it is not the case that ' if neg else ''}{name} is applied to {', '.join(np(a) for a in n.args)}"
    if isinstance(n, Join):
        if neg:
            return "it is not the case that " + clause(n, ds)
        left = clause(n.left, ds)
        right = clause(n.right, ds)
        return f"{left}, {n.conj} {right}"
    raise ValueError(f"cannot realize {type(n).__name__}")


def english(n, ds=None):
    ds = ds or Discourse()
    s = clause(n, ds)
    return s[0].upper() + s[1:] + "."


def emel(n):
    """Canonical EMEL notation for the same tree."""
    t = lambda x: x.surface if x.substrate != "lexical" else x.surface.lower()
    if isinstance(n, Relation): return f"{t(n.source)} {n.op} {t(n.target)}"
    if isinstance(n, Property): return f"{t(n.subject)}.{n.attribute} = {n.value.surface}"
    if isinstance(n, Proportion): return f"{t(n.a)}:{t(n.b)}::{t(n.c)}:{t(n.d)}"
    if isinstance(n, Continued):
        mid = t(n.x) if isinstance(n.x, Term) else emel(n.x)
        return f"|{emel(n.p1)}| ::|{mid}|:: |{emel(n.p2)}|"
    if isinstance(n, Apply): return f"{n.operator.surface}({', '.join(t(a) for a in n.args)})"
    if isinstance(n, Not): return f"not {emel(n.clause)}"
    if isinstance(n, Join): return f"{emel(n.left)} {n.conj} {emel(n.right)}"
