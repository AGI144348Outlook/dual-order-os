"""Independent audits. They inform ECHO; they never write his sentences.

lexical    every term resolves (gaps reported, glyph strings split into their registered glyphs)
syntax     the EMEL parse succeeded (checked by the caller)
type       operands match operator and relation signatures
semantic   the claim is SUPPORTED / CONTRADICTED / UNKNOWN against the Registry, WordNet or result records
provenance which source supports a supported claim
grammar    English(tree) parses back to the same tree, and every word is a known word
"""
import re
from .ast import Term, Relation, Property, Proportion, Continued, Apply, Not, Join, to_dict
from .lexicon import GLYPHS, SIGNATURES, RELATION_SIGNATURES, WORDNET

FUNCTION_WORDS = set("a an the is are not of to as and but its it applied case that does include includes opposite glyph string".split())


def terms(n):
    if isinstance(n, Term): yield n
    elif isinstance(n, (Relation,)): yield n.source; yield n.target
    elif isinstance(n, Property): yield n.subject
    elif isinstance(n, Proportion): yield from (n.a, n.b, n.c, n.d)
    elif isinstance(n, Continued):
        for p in (n.p1, n.x, n.p2): yield from terms(p)
    elif isinstance(n, Apply):
        yield n.operator
        for a in n.args: yield from terms(a)
    elif isinstance(n, Not): yield from terms(n.clause)
    elif isinstance(n, Join): yield from terms(n.left); yield from terms(n.right)


class Auditor:
    def __init__(self, registry, records):
        self.registry, self.records = registry, records

    # ---- lexical ---------------------------------------------------------------
    def lexical(self, n):
        gaps, strings = [], []
        for t in terms(n):
            if t.kind == "Gap": gaps.append(t.surface)
            if t.kind == "GlyphString":
                strings.append({"string": t.surface, "status": "candidate composite, meaning unassigned",
                                "constituents": [(g, GLYPHS[g]["operation"] if g in GLYPHS else "UNREGISTERED") for g in t.surface]})
        return {"status": "FLAG" if gaps else "PASS", "gaps": gaps, "glyph_strings": strings}

    # ---- type ------------------------------------------------------------------
    def type(self, n):
        errs = []
        def walk(x):
            if isinstance(x, Relation):
                for side in (x.source, x.target):
                    if side.kind not in ("Resident", "Gap"):
                        errs.append(f"{x.op} needs residents, got {side.kind} '{side.surface}'")
            elif isinstance(x, Apply):
                key = x.operator.surface if x.operator.surface == "%" else (
                    GLYPHS[x.operator.surface]["operation"] if x.operator.kind == "GlyphOperator" else x.operator.surface.upper())
                sig = SIGNATURES.get(key)
                if not sig: errs.append(f"unknown operator {x.operator.surface}")
                else:
                    want = sig[0]
                    if want != ("Any",) and len(want) != len(x.args):
                        errs.append(f"{key} takes {len(want)} argument(s) {want}, got {len(x.args)}")
                    elif want != ("Any",):
                        for w, a in zip(want, x.args):
                            if getattr(a, "kind", None) not in (w, "Gap"):
                                errs.append(f"{key} expects {w}, got {getattr(a, 'kind', type(a).__name__)}")
                for a in x.args:
                    if not isinstance(a, Term): walk(a)
            elif isinstance(x, Proportion):
                subs = {t.substrate for t in (x.a, x.b, x.c, x.d)}
                if len(subs) > 1: errs.append(f"proportion mixes substrates {sorted(subs)}")
            elif isinstance(x, Not): walk(x.clause)
            elif isinstance(x, Join): walk(x.left); walk(x.right)
        walk(n)
        return {"status": "FAIL" if errs else "PASS", "errors": errs}

    # ---- semantic + provenance -------------------------------------------------------
    def _isa(self, a, b):
        """Spectrum depth from a up to b, with the source that supports it."""
        ra, rb = a.canonical.split(":", 1)[1], b.canonical.split(":", 1)[1]
        if self.registry.has(ra) and self.registry.has(rb):
            d = self.registry.ancestors(ra).get(rb)
            return (d, f"registry: {ra} -> {' -> '.join(self.registry.chain(ra)[:d])}") if d else (None, "registry")
        if WORDNET:
            sa, sb = WORDNET.synsets(ra.replace(" ", "_"), "n"), WORDNET.synsets(rb.replace(" ", "_"), "n")
            if sa and sb:
                for x in sa:
                    for p in x.hypernym_paths():
                        for y in sb:
                            if y in p: return len(p) - 1 - p.index(y), f"wordnet: {x.name()} -> {y.name()}"
                return None, "wordnet"
        return None, None

    def _rel(self, a, b):
        d, src = self._isa(a, b)
        if d: return ("is_a", d), src
        d, src2 = self._isa(b, a)
        if d: return ("includes", d), src2
        return None, src or src2

    def truth(self, n):
        if isinstance(n, Relation):
            if n.op in ("is_a", "includes"):
                a, b = (n.source, n.target) if n.op == "is_a" else (n.target, n.source)
                d, src = self._isa(a, b)
                if d: return "SUPPORTED", f"{src} (spectrum depth {d})"
                return ("CONTRADICTED", f"{src}: no is-a path") if src else ("UNKNOWN", "a term is not indexed")
            if n.op == "antonym_of" and WORDNET:
                a, b = (x.canonical.split(":", 1)[1] for x in (n.source, n.target))
                ok = any(l2.name() == b for s in WORDNET.synsets(a) for l in s.lemmas() for l2 in l.antonyms())
                return ("SUPPORTED", "wordnet antonym") if ok else ("CONTRADICTED", "wordnet: not antonyms")
            return "UNKNOWN", "no source for this relation"
        if isinstance(n, Property):
            rec = self.records.get(n.subject.surface)
            if rec is None: return "UNKNOWN", f"no record {n.subject.surface}"
            if n.attribute not in rec: return "UNKNOWN", f"{n.subject.surface} has no field {n.attribute}"
            ok = str(rec[n.attribute]) == n.value.surface
            return ("SUPPORTED" if ok else "CONTRADICTED"), f"record {n.subject.surface}.{n.attribute} = {rec[n.attribute]}"
        if isinstance(n, Proportion):
            r1, s1 = self._rel(n.a, n.b); r2, s2 = self._rel(n.c, n.d)
            if r1 and r1 == r2: return "SUPPORTED", f"both pairs are {r1[0]} at spectrum depth {r1[1]}"
            if r1 and r2: return "CONTRADICTED", f"{r1} vs {r2}"
            return ("CONTRADICTED", f"{r1} vs {r2}") if (r1 or r2) and (s1 and s2) else ("UNKNOWN", "pair relation unknown")
        if isinstance(n, Continued):
            sig = []
            for p in (n.p1, n.x, n.p2):
                v, why = self.truth(p)
                if v != "SUPPORTED": return v, f"inner analogy {p.a.surface}:{p.b.surface}::{p.c.surface}:{p.d.surface} is {v}"
                sig.append(self._rel(p.a, p.b)[0])
            (t1, d1), (tx, dx), (t2, d2) = sig
            words_of = lambda p: {p.a.canonical, p.b.canonical, p.c.canonical, p.d.canonical}
            bridge = bool(words_of(n.x) & words_of(n.p1)) and bool(words_of(n.x) & words_of(n.p2))
            if not (t1 == tx == t2): return "CONTRADICTED", f"relation types differ: {t1}, {tx}, {t2}"
            if dx - d1 != d2 - dx: return "CONTRADICTED", f"spectrum depths {d1}, {dx}, {d2} are not evenly stepped"
            if dx == d1: return "UNKNOWN", f"flat: all three at spectrum depth {d1}"
            if not bridge: return "UNKNOWN", "x shares no term with P1 or P2, so it bridges nothing"
            return "SUPPORTED", f"{t1} at spectrum depths {d1} -> {dx} -> {d2}, and x shares terms with both"
        if isinstance(n, Apply):
            return "NOT_A_CLAIM", "an operation, not an assertion"
        if isinstance(n, Not):
            v, src = self.truth(n.clause)
            return {"SUPPORTED": "CONTRADICTED", "CONTRADICTED": "SUPPORTED"}.get(v, v), src
        if isinstance(n, Join):
            (v1, s1), (v2, s2) = self.truth(n.left), self.truth(n.right)
            v = "CONTRADICTED" if "CONTRADICTED" in (v1, v2) else ("SUPPORTED" if v1 == v2 == "SUPPORTED" else "UNKNOWN")
            return v, f"{s1}; {s2}"

    # ---- discourse: connectives must be earned -------------------------------------
    def discourse(self, n):
        issues = []
        def walk(x):
            if isinstance(x, Join):
                if x.conj == "but" and isinstance(x.left, Property) and isinstance(x.right, Property) \
                        and x.left.value.surface == x.right.value.surface:
                    issues.append(f"'but' joins two equal values ({x.left.value.surface}); there is no contrast")
                walk(x.left); walk(x.right)
        walk(n)
        return {"status": "FAIL" if issues else "PASS", "issues": issues}

    # ---- grammar: English must parse back to the same tree -------------------------------
    def grammar(self, n, text, english_parser, known_word):
        issues = []
        try:
            back = english_parser.sentence(text)
            if to_dict(back) != to_dict(n):
                issues.append("round trip changed the meaning")
        except Exception as e:
            issues.append(f"does not parse back: {e}")
        for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]*", text):
            lw = w.lower()
            if w in self.records or re.match(r"^[A-Z]{1,2}-?\d+$", w):
                continue
            if lw not in FUNCTION_WORDS and not known_word(lw):
                issues.append(f"unknown word '{w}'")
        return {"status": "FAIL" if issues else "PASS", "issues": issues}
