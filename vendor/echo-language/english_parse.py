"""The grammar guide: parse ECHO's English back into a syntax tree.

If English(tree) parses back to the same tree, the sentence says exactly what the
tree means. If it does not, the realizer produced something ambiguous or wrong, and
ECHO gets that as feedback. This parser covers the English that the grammar can
produce, so anything outside that grammar is reported, not guessed.
"""
import re
from .ast import Term, Relation, Property, Proportion, Continued, Apply, Not, Join
from .lexicon import OPERATION_TO_GLYPH

ART = r"(?:an?\s+)?"
NP = r"(.+?)"


class EnglishParseError(Exception):
    pass


class EnglishParser:
    def __init__(self, parser_factory):
        self.pf = parser_factory          # gives a Parser whose resolve() maps words to terms
        self.focus = None

    def term(self, text):
        text = text.strip()
        m = re.match(r"^(.) \(([A-Z_]+)\)$", text)                      # "ל (DIRECT)"
        if m:
            return Term(m.group(1), "glyph", "glyph:" + m.group(1), "GlyphOperator")
        m = re.match(r"^the glyph string (\S+)$", text)
        if m:
            return Term(m.group(1), "glyph_string", "glyph_string:" + m.group(1), "GlyphString")
        text = re.sub(r"^(?:a|an)\s+", "", text, flags=re.I)
        return self.pf().resolve(text.replace(" ", "_") if " " in text else text)

    def value(self, text):
        text = text.strip()
        return Term(text, "number" if re.match(r"^\d", text) else "text", "value:" + text, "Quantity")

    def sentence(self, s):
        s = s.strip()
        if not s.endswith("."):
            raise EnglishParseError("a sentence must end with a period")
        s = s[:-1]
        return self.clause(s[0].lower() + s[1:])

    def clause(self, s):
        for conj in ("but", "and"):
            parts = s.split(f", {conj} ", 1)
            if len(parts) == 2:
                return Join(conj, self.clause(parts[0]), self.clause(parts[1]))
        if s.startswith("it is not the case that "):
            return Not(self.clause(s[len("it is not the case that "):]))
        m = re.match(r"^(?:the (.+?) of (.+?)|its (.+?)) is( not)? (.+)$", s)
        if m and (m.group(1) or m.group(3)):
            if m.group(3):
                if not self.focus: raise EnglishParseError("'its' has nothing to refer to")
                subj, attr = self.focus, m.group(3)
            else:
                subj, attr = self.term(m.group(2)), m.group(1)
                self.focus = subj
            node = Property(subj, attr.replace(" ", "_"), self.value(m.group(5)))
            return Not(node) if m.group(4) else node
        self.focus = None
        m = re.match(r"^as the analogy (.+?) is( not)? to the analogy (.+?), so that analogy is to (.+)$", s)
        if m:
            def prop(t):
                p = re.match(r"^(.+?) : (.+?) :: (.+?) : (.+)$", t)
                if not p: raise EnglishParseError(f"not an analogy: {t!r}")
                return Proportion(*(self.term(p.group(i)) for i in range(1, 5)))
            node = Continued(prop(m.group(1)), prop(m.group(3)), prop(m.group(4)))
            return Not(node) if m.group(2) else node
        def prop2(t):
            p = re.match(r"^(.+?) : (.+?) :: (.+?) : (.+)$", t)
            if not p: raise EnglishParseError(f"not an analogy: {t!r}")
            return Proportion(*(self.term(p.group(i)) for i in range(1, 5)))
        for pat, reading in ((r"^(.+?) is( not)? the level between the analogy (.+?) and the analogy (.+)$", "pivot"),
                             (r"^(.+?) is( not)? between the analogy (.+?) and the analogy (.+)$", "")):
            m = re.match(pat, s)
            if m:
                node = Continued(prop2(m.group(3)), self.term(m.group(1)), prop2(m.group(4)), reading)
                return Not(node) if m.group(2) else node
        for pat, reading in ((r"^the analogy (.+?) and the analogy (.+?) (both|do not both) fall under (.+)$", "common"),
                             (r"^the analogy (.+?) and the analogy (.+?) (turn|do not turn) on (.+) in the same sense$", "hinge")):
            m = re.match(pat, s)
            if m:
                node = Continued(prop2(m.group(1)), self.term(m.group(4)), prop2(m.group(2)), reading)
                return Not(node) if m.group(3).startswith("do not") else node
        m = re.match(r"^(.+?) is( not)? to (.+?) as (.+?) is to (.+)$", s)
        if m:
            node = Proportion(self.term(m.group(1)), self.term(m.group(3)), self.term(m.group(4)), self.term(m.group(5)))
            return Not(node) if m.group(2) else node
        m = re.match(r"^(.+?) is( not)? the opposite of (.+)$", s)
        if m:
            node = Relation("antonym_of", self.term(m.group(1)), self.term(m.group(3)))
            return Not(node) if m.group(2) else node
        m = re.match(r"^(.+?) (includes|does not include) (.+)$", s)
        if m:
            node = Relation("includes", self.term(m.group(1)), self.term(m.group(3)))
            return Not(node) if m.group(2).startswith("does not") else node
        m = re.match(r"^(.+?) is applied to (.+)$", s)
        if m:
            name = m.group(1)
            if name == "the inversion": op = Term("%", "symbol", "symbol:%", "Operator")
            else:
                g = self.term(name)
                op = g if g.kind == "GlyphOperator" else Term(name, "operator", "op:" + name.upper(), "Operator")
            return Apply(op, tuple(self.term(a) for a in m.group(2).split(", ")))
        m = re.match(r"^(.+?) is( not)? (an? .+)$", s)
        if m:
            node = Relation("is_a", self.term(m.group(1)), self.term(m.group(3)))
            return Not(node) if m.group(2) else node
        raise EnglishParseError(f"outside ECHO's grammar: {s!r}")
