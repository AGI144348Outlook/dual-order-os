"""EMEL lexer and recursive-descent parser. A custom grammar, not Python's.

  statement := clause (('and' | 'but') clause)*
  clause    := 'not' clause | core
  core      := bounded '::' bounded '::' bounded          continued proportion |P1| ::|x|:: |P2|
             | term ':' term '::' term ':' term           proportion
             | term RELATION term                         is_a | includes | antonym_of
             | term '.' ATTRIBUTE '=' value               property
             | call                                       operator application
  call      := (NAME | GLYPH | '%') '(' term (',' term)* ')'
  term      := call | QUALIFIED | NAME | GLYPH | GLYPH_STRING | NUMBER | STRING

Qualified names (word:dog, glyph:ל, result:C-05) make the substrate explicit; bare
names are resolved. A token's canonical id comes from resolution, never its spelling.
"""
import re
from .ast import Term, Relation, Property, Proportion, Continued, Apply, Not, Join
from .lexicon import GLYPHS, OPERATION_TO_GLYPH, SIGNATURES

QUALIFIERS = ("word", "glyph", "result", "math", "formula", "relation", "resident", "echo")
TOKEN = re.compile(r"""
  (?P<ws>\s+)
 |(?P<qual>(?:%s):[^\s():,=]+)
 |(?P<hebrew>[\u05D0-\u05EA]+)
 |(?P<number>\d+(?:\.\d+)?%%?)
 |(?P<string>"[^"]*")
 |(?P<sym>::|:|%%|\(|\)|,|\.|=|\|)
 |(?P<name>[A-Za-z][A-Za-z0-9_\-]*)
""" % "|".join(QUALIFIERS), re.X)
RELATIONS = {"is_a", "includes", "antonym_of"}
KEYWORDS = RELATIONS | {"not", "and", "but"}


class ParseError(Exception):
    pass


def lex(text):
    out, i = [], 0
    while i < len(text):
        m = TOKEN.match(text, i)
        if not m:
            raise ParseError(f"unrecognised symbol {text[i]!r} at {i}")
        kind = m.lastgroup
        if kind != "ws":
            out.append((kind, m.group(kind), i))
        i = m.end()
    return out


class Parser:
    def __init__(self, tokens, lexicon):
        self.t, self.i, self.lex = tokens, 0, lexicon

    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else (None, None, None)

    def take(self, value=None, kind=None):
        tk = self.peek()
        if tk[0] is None or (value and tk[1] != value) or (kind and tk[0] != kind):
            raise ParseError(f"expected {value or kind}, found {tk[1]!r}")
        self.i += 1
        return tk

    def statement(self):
        node = self.clause()
        while self.peek()[1] in ("and", "but"):
            conj = self.take()[1]
            node = Join(conj, node, self.clause())
        if self.peek()[0] is not None:
            raise ParseError(f"unexpected {self.peek()[1]!r}")
        return node

    def clause(self):
        if self.peek()[1] == "not":
            self.take()
            return Not(self.clause())
        return self.core()

    def bounded(self):
        """|a:b::c:d| : a proportion used as a single operand (an auxiliary tree)."""
        self.take("|")
        a = self.term(); self.take(":"); b = self.term(); self.take("::"); c = self.term(); self.take(":"); d = self.term()
        self.take("|")
        return Proportion(a, b, c, d)

    def core(self):
        if self.peek()[1] == "|":
            p1 = self.bounded(); self.take("::")
            if self.peek(2)[1] == "|":                     # |word| : a single-word middle
                self.take("|"); x = self.term(); self.take("|")
            else:
                x = self.bounded()
            self.take("::"); p2 = self.bounded()
            return Continued(p1, x, p2)
        if self.is_call_start():
            call = self.call()
            return call
        a = self.term()
        nxt = self.peek()[1]
        if nxt == ":":
            self.take(":"); b = self.term(); self.take("::"); c = self.term(); self.take(":"); d = self.term()
            return Proportion(a, b, c, d)
        if nxt in RELATIONS:
            op = self.take()[1]
            return Relation(op, a, self.term())
        if nxt == ".":
            self.take("."); attr = self.take(kind="name")[1]; self.take("=")
            return Property(a, attr, self.value())
        raise ParseError(f"expected ':', a relation or '.' after {a.surface!r}")

    def is_call_start(self):
        k, v, _ = self.peek()
        return (k in ("name", "hebrew") or v == "%") and self.peek(1)[1] == "("

    def call(self):
        k, v, _ = self.take()
        self.take("(")
        args = [self.term()]
        while self.peek()[1] == ",":
            self.take(","); args.append(self.term())
        self.take(")")
        if k == "hebrew":
            if v not in GLYPHS:
                raise ParseError(f"operator {v} is a glyph string; only registered single glyphs are operators")
            op = Term(v, "glyph", "glyph:" + v, "GlyphOperator")
        elif v == "%":
            op = Term("%", "symbol", "symbol:%", "Operator")
        else:
            op = Term(v, "operator", "op:" + v.upper(), "Operator")
        return Apply(op, tuple(args))

    def value(self):
        """A property value is a literal (VALID, 81.25, 0%, "text"), not a resident to resolve."""
        kind, v, _ = self.peek()
        if kind is None:
            raise ParseError("expected a value, found end of input")
        self.take()
        return Term(v.strip('"'), "number" if kind == "number" else "text", "value:" + v.strip('"'), "Quantity")

    def term(self):
        if self.peek()[0] is None:
            raise ParseError("expected a term, found end of input")
        if self.is_call_start():
            return self.call()
        kind, v, pos = self.take()
        if kind is None or v in KEYWORDS or kind == "sym":
            raise ParseError(f"expected a term, found {v!r}")
        if kind == "qual":
            q, name = v.split(":", 1)
            return self.resolve(name, forced=q)
        if kind == "hebrew":
            if len(v) == 1:
                return Term(v, "glyph", "glyph:" + v, "GlyphOperator")
            # composite: a new candidate identity whose constituents keep their own meanings
            return Term(v, "glyph_string", "glyph_string:" + v, "GlyphString")
        if kind == "number":
            return Term(v, "number", "num:" + v, "Quantity")
        if kind == "string":
            return Term(v.strip('"'), "text", "text:" + v.strip('"'), "Quantity")
        return self.resolve(v)

    def resolve(self, name, forced=None):
        if forced == "result" or (forced is None and name in self.lex.records):
            return Term(name, "record", "result:" + name, "Record" if name in self.lex.records else "Gap")
        if forced == "glyph":
            return Term(name, "glyph", "glyph:" + name, "GlyphOperator" if name in GLYPHS else "Gap")
        w = name.replace("_", " ").lower()
        return Term(name, "lexical", "word:" + w, "Resident" if self.lex.word_known(w) else "Gap")


def parse(text, lexicon):
    return Parser(lex(text), lexicon).statement()
