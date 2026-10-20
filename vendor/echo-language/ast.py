"""Typed, substrate-neutral syntax tree for ECHO's expression language (EMEL, working name).

English, EMEL notation and Canvas are renderers of these nodes; none of them is the meaning.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union


@dataclass(frozen=True)
class Term:
    surface: str            # what was written
    substrate: str          # lexical | record | glyph | glyph_string | number | text
    canonical: str          # canonical id after resolution, e.g. word:dog, glyph:ל
    kind: str = "Resident"  # Resident | Record | GlyphOperator | GlyphString | Quantity | Gap


@dataclass(frozen=True)
class Relation:
    op: str                 # is_a | includes | antonym_of
    source: Term
    target: Term


@dataclass(frozen=True)
class Property:
    subject: Term
    attribute: str
    value: Term


@dataclass(frozen=True)
class Proportion:
    a: Term
    b: Term
    c: Term
    d: Term


@dataclass(frozen=True)
class Continued:
    """|P1| ::|x|:: |P2|. x is an analogy (mean proportional) or a single word.

    For a single word the reading says what the word does between them:
      pivot   the level P1 rises to and P2 rises from, evenly stepped
      common  the nearest category every term of both analogies falls under
      hinge   a word both analogies contain, in the same sense
    """
    p1: Proportion
    x: object
    p2: Proportion
    reading: str = ""


@dataclass(frozen=True)
class Apply:
    operator: Term
    args: tuple


@dataclass(frozen=True)
class Not:
    clause: object


@dataclass(frozen=True)
class Join:
    conj: str               # and | but
    left: object
    right: object


Node = Union[Relation, Property, Proportion, Continued, Apply, Not, Join]


def to_dict(node):
    d = asdict(node)
    d["node"] = type(node).__name__
    return d
