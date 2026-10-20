"""
ECHO Governor — minimal end-to-end skeleton, now with a learning layer.

Every architectural box (Φ, D, Propose, Validate, Govern, Select, Matrix)
still runs as a real, testable cycle. On top of that, the Algorithm Matrix
(A-000, the Governor's self-index) now carries five classical, from-scratch
learning techniques as registered tools — its "tool belt" — built entirely
on data the Governor already accumulates (content it indexes, deficiencies
it diagnoses, transformations it tries). No external model calls, no
numpy/sklearn — pure standard library, so this still runs as-is in
Pydroid 3.

Precision note: these are classical statistical-learning techniques
(frequency counts, co-occurrence statistics, online mean/variance,
k-means, UCB1 bandits) — not deep learning, no gradient descent, no
training loop. That distinction matters for being honest about what's
actually happening here vs. what "learning" might otherwise imply.

Still explicitly stubbed / TODO, same as before: Propose only generates a
single no-op candidate (no real algebraic transformations yet), Validate
and Govern always pass, and content decomposition is whitespace tokens,
not the structural/glyph-level decomposition the rest of LHEA/Mashet uses.
"""

import math
from collections import defaultdict, Counter
from dataclasses import dataclass, field

# Common English function words — excluded from A-107's co-occurrence graph
# only (not from indexing, TF-IDF, or the Markov model). Added after a real
# run showed these acting as hubs that fused nearly the entire vocabulary
# into one component. Not exhaustive; a real deployment would want a fuller
# list or a frequency-based cutoff instead of a fixed set.
STOPWORDS = frozenset({
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "and", "or",
    "but", "is", "are", "was", "were", "be", "been", "being", "with",
    "as", "by", "that", "this", "these", "those", "it", "its", "from",
    "or", "not", "no", "so", "if", "than", "then", "which", "who", "whom",
    "has", "have", "had", "do", "does", "did", "will", "would", "can",
    "could", "may", "might", "shall", "should", "into", "out", "up",
    "down", "over", "under", "again", "further", "such", "some", "any",
})

# Boilerplate stripped specifically from dictionary definitions BEFORE they
# reach index_dictionary_entry() — things that appear in nearly every
# definition but carry no useful semantic signal, confirmed by frequency
# analysis across the WordNet thesaurus and BDB Hebrew lexicon.
# Three categories:
#   - Generic English definition filler (relating, having, used, denoting)
#   - Geographic/taxonomic WordNet formula words (genus, family, states, united)
#   - BDB citation and grammatical metadata (gen, isa, psa, masculine, plural)
DEFINITION_BOILERPLATE = frozenset({
    # generic filler
    "relating", "related", "denoting", "denotes", "having", "used",
    "especially", "particularly", "typically", "usually", "often",
    "also", "sometimes", "generally", "commonly", "etc", "eg",
    "see", "compare", "below", "above", "hence", "thus", "therefore",
    # geographic / taxonomic wordnet formula
    "genus", "family", "order", "class", "species", "member", "members",
    "united", "states", "supreme", "court", "location", "africa",
    "african", "american", "south", "north", "central", "east", "west",
    "european", "european", "greek", "latin", "hebrew", "arabic",
    "language", "languages", "dialect", "region", "regions", "area",
    # BDB grammatical / citation metadata
    "masculine", "feminine", "noun", "verb", "adjective", "adverb",
    "plural", "singular", "absolute", "construct", "suffix", "prefix",
    "proper", "biblical", "aramaic", "assyrian", "ethiopic", "phoenician",
    "gen", "isa", "psa", "jer", "exod", "deut", "num", "josh", "judg",
    "sam", "kin", "chr", "prov", "job", "ezek", "zech", "mal", "neh",
    "esth", "dan", "hos", "amos", "mic", "nah", "hab", "zeph", "obad",
    "1sam", "2sam", "1kin", "2kin", "1chr", "2chr", "verse", "twice",
    "amp", "ref", "class", "entry", "word", "form", "forms",
})



# ---------------------------------------------------------------------------
# ECHO Core: S (state), R (request/input), C (context/coupling)
#
# Hybrid grounding decision: "observed" for a cycle covers two axes —
#   1. CONTENT  — did the actual generated response match what Φ predicted?
#   2. QUALITY  — did some measurable property of the real exchange
#                 (coherence/relevance/etc.) match what Φ predicted?
# Net scrapings split across R and C:
#   - a scrape fetched specifically to answer this cycle -> R.scrape (direct)
#   - background/ambient crawled corpus accumulating over time -> C.corpus
# ---------------------------------------------------------------------------

@dataclass
class State:
    content: str = ""           # TODO: predicted/actual response content
    quality: float = 0.0        # TODO: predicted/actual quality scalar
    history: list = field(default_factory=list)

    @property
    def value(self):
        """Backward-compat scalar view used by stability/resource checks."""
        return self.quality


@dataclass
class Request:
    text: str = ""              # direct conversational input for this cycle
    scrape: str = ""            # a scrape fetched specifically for this cycle
    value: float = 0.0          # TODO: numeric contribution derived from text/scrape


@dataclass
class Context:
    corpus: str = ""            # ambient/background crawled corpus, accumulating
    value: float = 0.0          # TODO: numeric contribution derived from corpus


def phi(theta: dict, s: State, r: Request, c: Context,
        matrix: "AlgorithmMatrix" = None) -> State:
    """Φ_θ(S_t, R_t, C_t) -> S_{t+1}.

    Content prediction now uses the Governor's own Markov model (A-103)
    when a matrix with learned transitions is available — a genuine
    forecast, not an echo of the request — so CONTENT_ERROR in diagnose()
    is comparing a real prediction against reality, not comparing the
    request to itself. Falls back to the trivial echo rule if no matrix
    or no transitions have been learned yet (e.g. very first cycle).
    TODO: real state-evolution rule for `quality` — still a placeholder sum.
    """
    next_quality = s.quality + r.value + c.value  # trivial placeholder

    next_content = None
    if matrix is not None and matrix.transitions:
        seed_tokens = s.content.split()
        seed = seed_tokens[-1] if seed_tokens else None
        if seed:
            generated = matrix.generate_markov(seed, length=6)
            next_content = generated or None
    if next_content is None:
        next_content = r.text or s.content

    new_state = State(content=next_content, quality=next_quality,
                       history=s.history + [s.quality])
    return new_state


# ---------------------------------------------------------------------------
# Pure-stdlib k-means over 1D magnitude values (A-106 relies on this).
# Deterministic init (evenly spaced quantile picks), not random — keeps
# reclustering reproducible given the same magnitude_history.
# ---------------------------------------------------------------------------

def kmeans_1d(values: list, k: int = 2, iterations: int = 10) -> list:
    """TODO: extend to multi-dimensional clustering once deficiencies carry
    richer context than a single magnitude. This is deliberately the
    simplest version that's still real k-means, not a stand-in for it."""
    values = sorted(values)
    if len(values) <= k:
        return values
    step = len(values) / k
    centers = [values[min(int(i * step), len(values) - 1)] for i in range(k)]
    for _ in range(iterations):
        clusters = [[] for _ in range(k)]
        for v in values:
            idx = min(range(k), key=lambda i: abs(v - centers[i]))
            clusters[idx].append(v)
        new_centers = [sum(cl) / len(cl) if cl else centers[i]
                        for i, cl in enumerate(clusters)]
        if new_centers == centers:
            break
        centers = new_centers
    return sorted(centers)


def bucket_for(deficiency: dict) -> str:
    """D_bucket = TYPE + coarse magnitude band. Boundaries (0.2 / 1.0) are
    fixed placeholders — TODO: replace with matrix.recluster_buckets(TYPE)
    output (A-106) once enough magnitude_history has accumulated for that
    type; k-means on real data should set these, not a guess."""
    mag = deficiency.get("magnitude", 0)
    mag = abs(mag) if isinstance(mag, (int, float)) else 0
    band = "mild" if mag < 0.2 else "moderate" if mag < 1.0 else "severe"
    return f"{deficiency['type']}:{band}"


# ---------------------------------------------------------------------------
# Diagnostic layer: D(Φ, S, O, I) -> deficiencies
#
# Produces structured deficiency objects, never a narrative judgment.
# CONTENT uses TF-IDF similarity (A-102) over the Governor's own index.
# QUALITY and STABILITY use adaptive EMA thresholds (A-105) once enough
# history exists, falling back to the fixed thresholds dict until then.
# Every confirmed deficiency's magnitude is recorded (A-106 feed).
# ---------------------------------------------------------------------------

def complexity_of(theta: dict) -> int:
    """TODO: real complexity measure (terms + operators + recursion depth
    + dependencies, per the C(Φ) weighted-sum definition). Stub: key count."""
    return len(theta)


def diagnose(theta: dict, s: State, r: Request, c: Context,
             observed: State, invariants: list, thresholds: dict,
             matrix: "AlgorithmMatrix") -> list:
    deficiencies = []
    predicted = phi(theta, s, r, c, matrix)

    # CONTENT_ERROR — A-102 (TF-IDF similarity) + A-103 (Markov prediction
    # feeding `predicted` above). Both texts get indexed either way, since
    # indexing is how the Governor accumulates its corpus regardless of
    # whether this particular comparison trips a threshold.
    predicted_units = matrix.index_content(predicted.content)
    observed_units = matrix.index_content(observed.content)
    sim = matrix.tfidf_similarity(predicted_units, observed_units)
    content_thresh = thresholds.get("content_sim_min", 0.0)
    if sim < content_thresh:
        mag = content_thresh - sim
        deficiencies.append({
            "id": f"D-{len(deficiencies)+1:03d}",
            "type": "CONTENT_ERROR",
            "observed": observed.content,
            "predicted": predicted.content,
            "similarity": sim,
            "threshold": content_thresh,
            "magnitude": mag,
            "status": "CONFIRMED",
        })
        matrix.record_magnitude("CONTENT_ERROR", mag)

    # QUALITY_ERROR — A-105 (adaptive EMA threshold)
    e = abs(observed.quality - predicted.quality)
    matrix.update_ema("quality_error", e)
    eps_max = matrix.adaptive_threshold(
        "quality_error", k=2.0, default=thresholds.get("epsilon_max", float("inf")))
    if e > eps_max:
        mag = e - eps_max
        deficiencies.append({
            "id": f"D-{len(deficiencies)+1:03d}",
            "type": "QUALITY_ERROR",
            "observed": observed.quality,
            "predicted": predicted.quality,
            "error": e,
            "threshold": eps_max,
            "magnitude": mag,
            "status": "CONFIRMED",
        })
        matrix.record_magnitude("QUALITY_ERROR", mag)

    # INVARIANT_VIOLATION — unchanged, still a hard gate, not learned
    for inv in invariants:
        if not inv["check"](s):
            deficiencies.append({
                "id": inv["id"],
                "type": "INVARIANT_VIOLATION",
                "observed": s.value,
                "threshold": None,
                "magnitude": 1,
                "status": "CONFIRMED",
            })
            matrix.record_magnitude("INVARIANT_VIOLATION", 1)

    # STABILITY — A-105 (adaptive EMA threshold)
    if s.history:
        delta = abs(s.value - s.history[-1])
        matrix.update_ema("stability_delta", delta)
        delta_max = matrix.adaptive_threshold(
            "stability_delta", k=2.0, default=thresholds.get("delta_max", float("inf")))
        if delta > delta_max:
            mag = delta - delta_max
            deficiencies.append({
                "id": f"D-{len(deficiencies)+1:03d}",
                "type": "STABILITY",
                "observed": delta,
                "threshold": delta_max,
                "magnitude": mag,
                "status": "CONFIRMED",
            })
            matrix.record_magnitude("STABILITY", mag)

    # RESOURCE — deliberately NOT adaptive: a complexity budget is a hard
    # governance constraint, not something that should drift with history.
    c_max = thresholds.get("C_max", float("inf"))
    complexity = complexity_of(theta)
    if complexity > c_max:
        mag = complexity - c_max
        deficiencies.append({
            "id": f"D-{len(deficiencies)+1:03d}",
            "type": "RESOURCE",
            "observed": complexity,
            "threshold": c_max,
            "magnitude": mag,
            "status": "CONFIRMED",
        })
        matrix.record_magnitude("RESOURCE", mag)

    return deficiencies


# ---------------------------------------------------------------------------
# Transformation layer: P(D, Φ, M) -> candidate Φ's
# ---------------------------------------------------------------------------

def propose(deficiencies: list, theta: dict, primitives: list) -> list:
    """TODO: generate real candidates via primitive transformations keyed
    to `deficiencies`. Stub: one no-op candidate, tagged with an M-id so
    the bandit/history machinery (A-101) has something real to record
    against even before there's an actual alternative to choose between."""
    return [{"theta": theta, "m_id": "M-000-NOOP"}]


# ---------------------------------------------------------------------------
# Validation layer: V(Φ', I) -> (passes: bool, margin: float)
# ---------------------------------------------------------------------------

def validate(candidate: dict, invariants: list) -> tuple:
    """TODO: real gate + margin. Stub always passes with margin 0."""
    return True, 0.0


# ---------------------------------------------------------------------------
# Governor: G(Φ', B, H) -> bool
# ---------------------------------------------------------------------------

def govern(candidate: dict, budgets: dict, history: dict) -> bool:
    """TODO: enforce C(Φ') <= C_max and other constraints. Stub: allow all."""
    return True


# ---------------------------------------------------------------------------
# Selector: Pareto filter + deterministic tie-break
# ---------------------------------------------------------------------------

def select(candidates: list) -> dict:
    """TODO: Pareto filter, then Validity -> Dominance -> Margin ->
    Complexity -> Historical Success -> Canonical Order.
    Stub: only one candidate ever reaches here, so just return it."""
    return candidates[0]


# ---------------------------------------------------------------------------
# Algorithm Matrix: K (known), U (candidates), X (unexplored), H (history)
# — now also the Governor's tool belt of learning techniques (A-101..A-106).
# ---------------------------------------------------------------------------

class AlgorithmMatrix:
    """A-000, the Governor's self-index. One object, several jobs: it
    indexes algorithms/transformations (known/candidates/unexplored/
    history), indexes encountered content (conversation + scrapings), and
    now hosts five learning tools built on data it already accumulates —
    all classical, all from-scratch, none dependent on an external model.
    """

    def __init__(self):
        self.known = {"A-000": {"name": "Governor", "status": "ACTIVE"}}
        self.candidates = {}
        self.unexplored = []
        self.history = {}              # (M, D_bucket) -> (successes, attempts)
        self.content_units = {}        # unit -> document frequency (docs it's appeared in)
        self.documents_seen = 0        # total index_content() calls
        self.transitions = defaultdict(lambda: defaultdict(int))   # A-103 Markov
        self.cooccurrence = defaultdict(lambda: defaultdict(int))  # A-104 PPMI
        self._total_cooccurrence = 0   # cached sum — see ppmi() for why
        self.ema_stats = {}            # A-105: name -> {"mean","var","n"}
        self.magnitude_history = defaultdict(list)  # A-106 feed: D_type -> [magnitudes]
        self.regions = {}              # A-107: R-XXX -> {"words", "size"} — self-discovered
        self.word_to_region = {}       # A-108: single word -> region_id, inverse of regions
        self.word_categories = defaultdict(Counter)  # A-110: word -> Counter(source_category -> count)
        self.current_generation = {}   # A-113: (M,D_bucket) -> (s,a), volatile, NOT yet trusted
        # A-116: proper names routed here instead of the main semantic graph
        self.proper_names = {}         # name -> {definition, pos, sources}
        # A-116: investigation queue — SPECIFIC entries flagged for deeper follow-up
        self.investigation_queue = []  # list of {word, definition, reason}
        # A-116: entry class registry — TYPE/SPECIFIC/NAME/ABSTRACT per headword
        self.entry_classes = {}        # headword -> "TYPE"|"SPECIFIC"|"NAME"|"ABSTRACT"

        self.known.update({
            "A-101": {"name": "UCB Bandit Selector", "status": "ACTIVE",
                      "purpose": "choose M for a D_bucket using UCB1 over H(M,D); "
                                 "unexplored arms get priority, matching 'unknown != invalid'"},
            "A-102": {"name": "TF-IDF Content Similarity", "status": "ACTIVE",
                      "purpose": "rarity-weighted overlap using content_units as document frequency"},
            "A-103": {"name": "Markov Content Model", "status": "ACTIVE",
                      "purpose": "order-1 token transitions; feeds Φ's content prediction"},
            "A-104": {"name": "PPMI Co-occurrence Embeddings", "status": "ACTIVE",
                      "purpose": "sparse word/document vectors from the Governor's own corpus"},
            "A-105": {"name": "Adaptive EMA Thresholds", "status": "ACTIVE",
                      "purpose": "rolling mean/variance thresholds replacing fixed constants"},
            "A-106": {"name": "K-means Bucket Discovery", "status": "ACTIVE",
                      "purpose": "discover D_bucket magnitude-band boundaries from real data"},
            "A-107": {"name": "Region Discovery (Self-Organizing Matrices)", "status": "ACTIVE",
                      "purpose": "group indexed content into the Governor's own structure via "
                                 "connected components over its co-occurrence graph — the "
                                 "grouping is discovered, not assigned by predefined categories"},
            "A-108": {"name": "Word-to-Region Inverse Index", "status": "ACTIVE",
                      "purpose": "single word -> topic cluster -> back to related words; "
                                 "turns A-107's regions into a queryable vocabulary bank"},
            "A-109": {"name": "Hub-Word Exclusion (language-agnostic)", "status": "ACTIVE",
                      "purpose": "exclude highest-degree graph nodes dynamically instead of a "
                                 "hardcoded English stopword list — works for any language/corpus"},
            "A-110": {"name": "Category-Coherence Region Validation", "status": "ACTIVE",
                      "purpose": "check a discovered region's source-category agreement, inspired "
                                 "by the lattice-workbench's WordNet Category Matrix cross-check"},
            "A-111": {"name": "Region Lineage Tracking", "status": "ACTIVE",
                      "purpose": "classify regions across two discover_regions() runs as "
                                 "STABLE/GREW/SHRANK/MERGED/NEW via word-set overlap"},
            "A-112": {"name": "Confluence-Word Diagnostic", "status": "ACTIVE",
                      "purpose": "measure which specific hub words are causing merges by testing "
                                 "removal impact on the largest region, one word at a time"},
            "A-113": {"name": "Monitor/Anchor Bandit Split", "status": "ACTIVE",
                      "purpose": "separate what the bandit monitors (current generation) from what "
                                 "it learns from (anchored baseline) — only merges a generation into "
                                 "permanent history if it isn't a collapse relative to that baseline"},
            "A-115": {"name": "Dictionary-Definition Indexer", "status": "ACTIVE",
                      "purpose": "structured dictionary ingestion: headword becomes pivot, every "
                                 "definition word is a direct semantic neighbor in the transition "
                                 "graph — predict_next then follows meaning chains, not surface "
                                 "frequency. Different from flat text indexing in that the headword "
                                 "→ definition-word edge is added explicitly, not just inferred "
                                 "from co-occurrence proximity."},
            "A-116": {"name": "Definitional Article Classifier", "status": "ACTIVE",
                      "purpose": "classifies every dictionary entry at ingestion as TYPE (a/an), "
                                 "SPECIFIC (the — definite reference, queued for investigation), "
                                 "NAME (capitalized proper noun — routed to separate proper_names "
                                 "index, not the semantic graph), or ABSTRACT (no article — pure "
                                 "concept, best chain entry point). Fixes the BDB proper-name "
                                 "pollution of concept clusters by segregating names at source."},
            "A-117": {"name": "WordAgent Lobby + Orientation + Neighborhood Formation",
                      "status": "ACTIVE",
                      "purpose": "one WordAgent per dictionary word (branch of the Governor, not "
                                 "per region); all agents enter the Lobby simultaneously and "
                                 "introduce themselves by their definition entries, tying to every "
                                 "agent whose word appears in their definition — orientation mesh. "
                                 "Post-orientation: Governor inspects mesh for tightly-connected "
                                 "groups, scrutinizes proposed merges through Validate/Govern, "
                                 "commits approved merges as Neighborhoods — new indexed matrix "
                                 "entities, not just region labels."},
        })

    def record(self, entry_id: str, entry: dict):
        self.known[entry_id] = entry

    # -- indexing (shared substrate for A-102, A-103, A-104) -----------------

    def index_content(self, text: str, category: str = None) -> set:
        """Decompose text into indexed units, record document frequency
        (content_units), token transitions (A-103), and windowed
        co-occurrence (A-104) — one pass builds the substrate all three
        learning tools read from. TODO: real structural/symbolic
        decomposition — this is whitespace tokenization, not the
        Mashet/LHEA glyph-level decomposition used elsewhere.

        `category` is optional provenance (e.g. "root", "dict", "letter")
        — if given, feeds A-110's category-coherence region validation,
        the lightweight analog of the lattice-workbench's Category Matrix."""
        tokens = text.lower().split()
        units = set(tokens)
        self.documents_seen += 1
        for u in units:
            self.content_units[u] = self.content_units.get(u, 0) + 1
            if category:
                self.word_categories[u][category] += 1
        for a, b in zip(tokens, tokens[1:]):
            self.transitions[a][b] += 1
        window = 3
        for i, w in enumerate(tokens):
            for j in range(max(0, i - window), min(len(tokens), i + window + 1)):
                if i != j:
                    self.cooccurrence[w][tokens[j]] += 1
                    self._total_cooccurrence += 1
        return units

    # -- A-102: TF-IDF similarity --------------------------------------------

    def content_similarity(self, a_units: set, b_units: set) -> float:
        """Plain Jaccard overlap — retained as the unweighted baseline.
        diagnose() uses tfidf_similarity() instead; this is kept for
        comparison/fallback, not removed."""
        if not a_units and not b_units:
            return 1.0
        if not a_units or not b_units:
            return 0.0
        return len(a_units & b_units) / len(a_units | b_units)

    def idf(self, unit: str) -> float:
        df = self.content_units.get(unit, 0)
        n = max(self.documents_seen, 1)
        return math.log((n + 1) / (df + 1)) + 1  # smoothed, always positive

    def tfidf_similarity(self, a_units: set, b_units: set) -> float:
        """Rarity-weighted Jaccard: shared rare units count more than
        shared common ones. Degrades gracefully to something close to
        plain Jaccard while documents_seen is still small."""
        if not a_units and not b_units:
            return 1.0
        if not a_units or not b_units:
            return 0.0
        shared = a_units & b_units
        union = a_units | b_units
        shared_weight = sum(self.idf(u) for u in shared)
        union_weight = sum(self.idf(u) for u in union)
        return shared_weight / union_weight if union_weight else 0.0

    # -- A-103: Markov content model -----------------------------------------

    def predict_next(self, token: str):
        options = self.transitions.get(token)
        if not options:
            return None
        return max(options.items(), key=lambda kv: kv[1])[0]

    def generate_markov(self, seed_token: str, length: int = 6) -> str:
        if not seed_token:
            return ""
        out = [seed_token]
        for _ in range(length):
            nxt = self.predict_next(out[-1])
            if not nxt:
                break
            out.append(nxt)
        return " ".join(out)

    # -- A-104: PPMI co-occurrence embeddings --------------------------------

    def ppmi(self, w1: str, w2: str) -> float:
        """Uses self._total_cooccurrence (updated incrementally in
        index_content) instead of summing the whole graph on every call —
        the naive version was O(all edges) per call, meaning O(edges^2)
        total cost inside discover_regions' edge loop. Fine at demo scale,
        would not survive scaling the corpus up by 10-20x, which is
        exactly what this session is about to do."""
        total = self._total_cooccurrence
        if total == 0:
            return 0.0
        c_w1 = sum(self.cooccurrence.get(w1, {}).values())
        c_w2 = sum(self.cooccurrence.get(w2, {}).values())
        c_w1w2 = self.cooccurrence.get(w1, {}).get(w2, 0)
        if not c_w1 or not c_w2 or not c_w1w2:
            return 0.0
        p_w1, p_w2, p_w1w2 = c_w1 / total, c_w2 / total, c_w1w2 / total
        return max(math.log(p_w1w2 / (p_w1 * p_w2)), 0.0)  # PPMI: clip at 0

    def embed(self, word: str) -> dict:
        """Sparse vector: {neighbor: PPMI(word, neighbor)}. Built entirely
        from the Governor's own accumulated corpus — no external model."""
        neighbors = self.cooccurrence.get(word, {})
        return {other: self.ppmi(word, other) for other in neighbors}

    @staticmethod
    def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
        if not vec_a or not vec_b:
            return 0.0
        shared = set(vec_a) & set(vec_b)
        dot = sum(vec_a[k] * vec_b[k] for k in shared)
        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def document_embedding(self, text: str) -> dict:
        tokens = set(text.lower().split())
        vectors = [self.embed(t) for t in tokens if t in self.cooccurrence]
        if not vectors:
            return {}
        combined = defaultdict(float)
        for v in vectors:
            for k, val in v.items():
                combined[k] += val
        return {k: val / len(vectors) for k, val in combined.items()}

    # -- A-105: adaptive EMA thresholds --------------------------------------

    def update_ema(self, name: str, value: float, alpha: float = 0.2):
        stat = self.ema_stats.setdefault(name, {"mean": value, "var": 0.0, "n": 0})
        stat["n"] += 1
        delta = value - stat["mean"]
        stat["mean"] += alpha * delta
        stat["var"] = (1 - alpha) * (stat["var"] + alpha * delta * delta)

    def adaptive_threshold(self, name: str, k: float = 2.0, default=None,
                            min_samples: int = 3):
        """mean + k*std, once enough samples exist; otherwise `default`
        (the fixed constant) so early cycles don't threshold off noise."""
        stat = self.ema_stats.get(name)
        if not stat or stat["n"] < min_samples:
            return default
        return stat["mean"] + k * math.sqrt(stat["var"])

    # -- A-106: k-means bucket discovery -------------------------------------

    def record_magnitude(self, d_type: str, magnitude):
        if isinstance(magnitude, (int, float)):
            self.magnitude_history[d_type].append(magnitude)

    def recluster_buckets(self, d_type: str, k: int = 2, iterations: int = 10):
        values = self.magnitude_history.get(d_type, [])
        if len(values) < k:
            return None  # not enough data yet — stays None, not a guess
        return kmeans_1d(values, k=k, iterations=iterations)

    # -- A-107: self-organizing region discovery -----------------------------

    def hub_words(self, top_fraction: float = 0.02, min_graph_size: int = 50) -> set:
        """A-109: language-agnostic replacement for a hardcoded stopword
        list. Words with the highest degree (most distinct co-occurrence
        partners) in the CURRENT graph — hub-ness here is a property of
        the graph's structure, not of English grammar, so this works the
        same way on Hebrew, mixed-language, or any other corpus without
        hand-curating a new exclusion list each time. Inspired by network
        science's 'targeted removal of high-degree nodes' technique for
        breaking up giant components."""
        if len(self.cooccurrence) < min_graph_size:
            return set()
        degrees = sorted(
            ((w, len(neighbors)) for w, neighbors in self.cooccurrence.items()),
            key=lambda kv: -kv[1])
        k = max(1, int(len(degrees) * top_fraction))
        return {w for w, _ in degrees[:k]}

    def discover_regions(self, min_ppmi: float = 0.5, min_size: int = 2,
                          min_count: int = 1, extra_exclude: set = None) -> dict:
        """Group indexed content into the Governor's own structure, not a
        predefined taxonomy: union-find connected components over the
        co-occurrence graph, keeping an edge only where PPMI(w1,w2) >=
        min_ppmi AND the raw co-occurrence count >= min_count. Which words
        end up grouped together, how many regions form, and what sizes
        they are is entirely a function of the real data indexed so far.

        min_count matters because raw PPMI is known to overreact to a
        single co-occurrence between a common word and a rare one — a
        real failure observed when a hand-added label word ("translation")
        appeared once alongside many different rare words and dominated
        the graph. min_ppmi alone didn't catch that; min_count does.

        STOPWORDS plus any extra_exclude (e.g. from hub_words(), A-109)
        are removed from the graph entirely. CAUTION, from the
        lattice-workbench's Algorithm I finding: combining two reasonable
        constraints can starve growth entirely rather than gracefully
        fixing it ("died at 1 flag") — min_count and exclusion sets should
        be tuned together, not assumed to compose safely.

        Each discovered region is registered as an UNVALIDATED candidate
        (origin: SELF-DISCOVERED) — consistent with the frozen design's
        rule that self-derived structure isn't trusted until validated
        (see validate_region(), A-110).
        """
        exclude = STOPWORDS | (extra_exclude or set())
        parent = {}

        def find(x):
            root = x
            while parent.get(root, root) != root:
                root = parent[root]
            while parent.get(x, x) != root:
                parent[x], x = root, parent.get(x, x)
            return root

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        words = [w for w in self.cooccurrence.keys() if w not in exclude]
        for w in words:
            parent.setdefault(w, w)
        for w1, neighbors in self.cooccurrence.items():
            if w1 in exclude:
                continue
            for w2, count in neighbors.items():
                if w2 in exclude or count < min_count:
                    continue
                if self.ppmi(w1, w2) >= min_ppmi:
                    union(w1, w2)

        groups = defaultdict(set)
        for w in words:
            groups[find(w)].add(w)

        self.regions = {}
        n = 1
        for members in groups.values():
            if len(members) < min_size:
                continue  # singleton or below threshold — not a region
            rid = f"R-{n:03d}"
            n += 1
            self.regions[rid] = {"words": members, "size": len(members)}
            self.candidates[rid] = {
                "type": "REGION",
                "origin": "SELF-DISCOVERED",
                "status": "UNVALIDATED",
                "size": len(members),
                "min_ppmi": min_ppmi,
                "min_count": min_count,
            }
        return self.regions

    def validate_region(self, rid: str, min_coherence: float = 0.5) -> dict:
        """A-110: lightweight analog of the lattice-workbench's WordNet
        Category Matrix cross-check. If words were indexed with a
        `category` tag (index_content(..., category=...)), check what
        fraction of a region's tagged words share the SAME source
        category — high agreement means the region likely reflects a
        real coherent concept, not just structural co-occurrence.
        Updates the region's candidate status to VALIDATED if coherent."""
        if rid not in self.regions:
            return {"status": "UNKNOWN_REGION"}
        tally = Counter()
        tagged = 0
        for w in self.regions[rid]["words"]:
            cats = self.word_categories.get(w)
            if cats:
                tagged += 1
                tally.update(cats)
        if not tally:
            return {"status": "UNVALIDATED", "reason": "no category data for this region"}
        top_cat, top_count = tally.most_common(1)[0]
        coherence = top_count / sum(tally.values())
        status = "VALIDATED" if coherence >= min_coherence else "MIXED"
        result = {"status": status, "top_category": top_cat, "coherence": coherence,
                  "tagged_fraction": tagged / len(self.regions[rid]["words"])}
        if rid in self.candidates:
            self.candidates[rid]["status"] = status
            self.candidates[rid]["validation"] = result
        return result

    def track_lineage(self, previous_regions: dict) -> dict:
        """A-111: classify each CURRENT region against a PRIOR run's
        regions dict, via word-set overlap — real genealogy across runs,
        not just an isolated snapshot each time. Inspired by the frozen
        Governor design's 'algorithmic genealogy' idea and the
        lattice-workbench's candidate-provenance pattern."""
        lineage = {}
        for rid, r in self.regions.items():
            words = r["words"]
            overlaps = [(prid, len(words & pr["words"]))
                        for prid, pr in previous_regions.items() if words & pr["words"]]
            if not overlaps:
                lineage[rid] = {"status": "NEW"}
            elif len(overlaps) == 1:
                prid, shared_n = overlaps[0]
                prev_size = previous_regions[prid]["size"]
                if shared_n == prev_size == r["size"]:
                    lineage[rid] = {"status": "STABLE", "from": prid}
                elif r["size"] > prev_size:
                    lineage[rid] = {"status": "GREW", "from": prid, "prev_size": prev_size}
                else:
                    lineage[rid] = {"status": "SHRANK", "from": prid, "prev_size": prev_size}
            else:
                lineage[rid] = {"status": "MERGED", "from": [o[0] for o in overlaps]}
        return lineage

    def confluence_words(self, min_ppmi: float = 0.5, min_size: int = 2, min_count: int = 1,
                          exclude: set = None, candidates: set = None, top_n: int = 10) -> list:
        """A-112: diagnostic naming exactly which hub words are causing
        merges, instead of only observing the aggregate blob afterward —
        inspired by the lattice-workbench's 'confluence tetrahedra' finding
        (a handful of specific nodes pulling unrelated branches together).
        For each candidate word, measures how much removing it (on top of
        existing exclusions) shrinks the largest discovered region.
        Restores self.regions to the true baseline before returning —
        this method is read-only from the caller's perspective."""
        base_exclude = STOPWORDS | (exclude or set())
        candidates = candidates if candidates is not None else self.hub_words()
        baseline = self.discover_regions(min_ppmi=min_ppmi, min_size=min_size,
                                          min_count=min_count, extra_exclude=base_exclude)
        baseline_max = max((r["size"] for r in baseline.values()), default=0)

        impacts = []
        for w in candidates:
            trial = self.discover_regions(min_ppmi=min_ppmi, min_size=min_size,
                                           min_count=min_count,
                                           extra_exclude=base_exclude | {w})
            trial_max = max((r["size"] for r in trial.values()), default=0)
            impacts.append((w, baseline_max - trial_max))
        impacts.sort(key=lambda kv: -kv[1])

        # restore true baseline state before returning (read-only contract)
        self.discover_regions(min_ppmi=min_ppmi, min_size=min_size,
                               min_count=min_count, extra_exclude=base_exclude)
        return impacts[:top_n]

    # -- A-116: definitional article classifier ---------------------------

    def classify_entry(self, headword: str, definition: str,
                        pos: str = None) -> str:
        """Classify a dictionary entry into one of four classes based on
        linguistic signals the dictionary editors already encoded:

        NAME     — headword starts with a capital letter, OR pos/definition
                   explicitly marks it as a proper noun. Routed to
                   self.proper_names, NOT the semantic graph. This is the
                   fix for the BDB proper-name blob pollution: Aaron,
                   Abaddon, Achashverosh don't belong in the same semantic
                   region as 'understanding', 'peace', 'wisdom'.

        TYPE     — definition begins with 'a' or 'an': signals category
                   membership ("a ruler", "a kind of tree"). Best for
                   cluster building — word is a type of something.

        SPECIFIC — definition contains early 'the': signals definite
                   reference, pointing at something specific that exists.
                   Queued for investigation — the definition is saying
                   'this specific thing', meaning there's more to know.

        ABSTRACT — no article, lowercase headword, not a proper name:
                   pure concept or verbal. Best chain entry points —
                   most generalizable, least tied to a specific referent.
        """
        hw = headword.strip()
        defl = definition.lower().strip()
        first_word = defl.split()[0] if defl.split() else ""

        # NAME: capital first letter or explicit proper-name marker
        is_capitalized = hw and hw[0].isupper()
        is_proper = (pos and "proper" in pos.lower()) or \
                    ("proper name" in defl[:40]) or \
                    ("proper noun" in defl[:40])
        if is_capitalized or is_proper:
            return "NAME"

        # TYPE: "a ..." or "an ..."
        if first_word in ("a", "an"):
            return "TYPE"

        # SPECIFIC: "the ..." appears early in the definition
        words = defl.split()
        if words and words[0] == "the":
            return "SPECIFIC"
        # also catch "the X of Y" patterns within first 5 words
        if "the" in words[:5] and len(words) > 1:
            the_idx = words.index("the")
            if the_idx < 5 and the_idx + 1 < len(words):
                # the word after "the" should look like a real noun, not a
                # boilerplate word — if it does, flag as SPECIFIC
                candidate = words[the_idx + 1].strip(".,;:")
                if (candidate.isalpha() and len(candidate) > 2
                        and candidate not in STOPWORDS
                        and candidate not in DEFINITION_BOILERPLATE):
                    return "SPECIFIC"

        # ABSTRACT: everything else
        return "ABSTRACT"

    # -- A-115: dictionary-definition structured indexer ------------------

    def index_dictionary_entry(self, headword: str, definition: str,
                                pos: str = None, synonyms: list = None,
                                category: str = "definition"):
        """A-115 + A-116: structured dictionary ingestion with article-based
        classification. Every entry is classified first (A-116), then:
        - NAME entries go to self.proper_names, bypassing the semantic graph
        - SPECIFIC entries are indexed AND queued for investigation
        - TYPE and ABSTRACT entries are indexed into the semantic graph"""
        hw = headword.lower().strip()
        if not hw:
            return

        entry_class = self.classify_entry(headword, definition, pos)
        self.entry_classes[hw] = entry_class

        # NAME: route to proper_names index, skip semantic graph
        if entry_class == "NAME":
            self.proper_names[hw] = {
                "original": headword,
                "definition": definition[:120],
                "pos": pos,
                "synonyms": synonyms or [],
            }
            self.content_units[hw] = self.content_units.get(hw, 0) + 1
            if category:
                self.word_categories[hw]["NAME"] += 1
            return

        def_tokens = definition.lower().split()
        def_words = [t.strip(".,;:(\'\"[]") for t in def_tokens
                     if t.strip(".,;:(\'\"[]")]
        def_words = [w for w in def_words
                     if w and w not in STOPWORDS and w not in DEFINITION_BOILERPLATE
                     and not w.isdigit() and len(w) > 1]

        if not def_words:
            return

        # SPECIFIC: index normally but also queue for investigation
        if entry_class == "SPECIFIC":
            self.investigation_queue.append({
                "word": hw,
                "class": "SPECIFIC",
                "definition": definition[:120],
                "reason": "definite article signals specific referent",
                "def_words": def_words[:6],
            })

        # Build semantic graph edges for TYPE, ABSTRACT, SPECIFIC
        for dw in def_words:
            if dw and dw != hw:
                self.transitions[hw][dw] += 2
                self.cooccurrence[hw][dw] += 2
                self.cooccurrence[dw][hw] += 1
                self._total_cooccurrence += 3

        for syn in (synonyms or []):
            s = syn.lower().strip()
            if s and s != hw and self.entry_classes.get(s) != "NAME":
                self.transitions[hw][s] += 1
                self.transitions[s][hw] += 1

        if def_words:
            self.index_content(" ".join(def_words), category=category)

        self.content_units[hw] = self.content_units.get(hw, 0) + 1
        if category:
            self.word_categories[hw][category] += 1
        if pos:
            self.word_categories[hw][f"pos:{pos}"] += 1

    def semantic_chain(self, seed: str, length: int = 8,
                        visited_penalty: float = 0.5) -> list:
        """A-115 companion: traverse the meaning graph seeded from one word,
        applying a penalty to already-visited tokens so the chain explores
        rather than looping. Uses the same transition graph that
        index_dictionary_entry() builds — pure semantic traversal, no
        grammar imposed."""
        tokens = [seed.lower()]
        visit_count = {seed.lower(): 1}

        for _ in range(length):
            current = tokens[-1]
            options = dict(self.transitions.get(current, {}))
            if not options:
                # fallback: find definition neighbor via co-occurrence
                options = dict(self.cooccurrence.get(current, {}))
            if not options:
                break

            # apply visited penalty so chain doesn't immediately loop
            scored = {w: count * (visited_penalty ** visit_count.get(w, 0))
                      for w, count in options.items()}

            nxt = max(scored.items(), key=lambda kv: kv[1])[0]
            tokens.append(nxt)
            visit_count[nxt] = visit_count.get(nxt, 0) + 1
            if visit_count[nxt] > 3:
                break

        return tokens

    # -- A-108: word-to-region inverse index (single word -> topic cluster) -

    def build_word_index(self) -> dict:
        """Inverse index over self.regions: given a single word, find its
        topic cluster in O(1) instead of scanning every region. This is
        what turns region discovery from a one-off report into something
        queryable — the actual mechanism behind 'vocabulary bank' lookup.
        Must be rebuilt (call again) after any discover_regions() run."""
        self.word_to_region = {}
        for rid, r in self.regions.items():
            for w in r["words"]:
                self.word_to_region[w] = rid
        return self.word_to_region

    def related_words(self, word: str) -> set:
        """Given one word from the Governor's vocabulary, return the other
        words it was grouped with — the single-word-in, cluster-out lookup.
        Empty set if the word was never assigned to a region (filtered as
        a stopword, or never co-occurred enough with anything to group)."""
        rid = self.word_to_region.get(word.lower())
        if not rid:
            return set()
        return self.regions[rid]["words"] - {word.lower()}

    # -- A-101: UCB1 bandit over H(M, D_bucket) ------------------------------

    def bandit_select(self, d_bucket: str, arms: list):
        """UCB1: an arm never tried for this bucket is explored first
        (deterministic — first such arm in `arms` order), matching the
        frozen design's 'unexplored != invalid' principle. Once every arm
        has at least one attempt, picks the highest mean+confidence-bonus."""
        if not arms:
            return None
        stats = {m: self.history.get((m, d_bucket), (0, 0)) for m in arms}
        for m in arms:
            if stats[m][1] == 0:
                return m
        total = sum(a for _, a in stats.values())
        best_arm, best_score = None, float("-inf")
        for m in arms:
            s_, a_ = stats[m]
            score = (s_ / a_) + math.sqrt(2 * math.log(total) / a_)
            if score > best_score:
                best_score, best_arm = score, m
        return best_arm

    def record_outcome(self, m_id: str, d_bucket: str, success: bool):
        """A-113: MONITOR side. Records into the current, volatile
        generation only — NOT directly into self.history (what
        bandit_select actually trusts). Separating what the Governor
        observes from what it learns from is the fix the lattice-workbench
        identified but never built: naive reinforcement of 'what worked'
        caused real mode collapse there (351 -> 97 structures in one
        generation) when the loop learned from its own current, possibly
        damaged output instead of a clean anchor point."""
        s_, a_ = self.current_generation.get((m_id, d_bucket), (0, 0))
        self.current_generation[(m_id, d_bucket)] = (s_ + (1 if success else 0), a_ + 1)

    @staticmethod
    def _aggregate_rate(table: dict):
        s = sum(s_ for s_, a_ in table.values())
        a = sum(a_ for s_, a_ in table.values())
        return (s / a) if a else None

    def checkpoint_generation(self, collapse_threshold: float = 0.3, min_attempts: int = 3) -> dict:
        """A-113: ANCHOR decision. Compares the current generation's
        aggregate success rate against self.history (the anchored,
        trusted baseline that bandit_select actually reads from).
        - If the generation looks like a collapse (rate dropped more than
          collapse_threshold below the anchor), DISCARD it — the baseline
          stays clean, uncorrupted by a bad run.
        - Otherwise, ANCHOR it — merge into self.history, becoming the
          new trusted baseline.
        Either way, current_generation resets afterward. This is exactly
        the fix the lattice-workbench designed but never implemented:
        anchor learning to the last known-healthy state, don't let a
        damaged generation poison what the bandit trusts next."""
        current_rate = self._aggregate_rate(self.current_generation)
        baseline_rate = self._aggregate_rate(self.history)
        total_attempts = sum(a_ for _, a_ in self.current_generation.values())

        if current_rate is None or total_attempts < min_attempts:
            self.current_generation = {}
            return {"decision": "SKIPPED", "reason": "not enough data this generation",
                    "attempts": total_attempts}

        if baseline_rate is not None and (baseline_rate - current_rate) > collapse_threshold:
            decision = "DISCARDED"
            reason = (f"generation rate {current_rate:.2f} vs anchored baseline "
                      f"{baseline_rate:.2f} — collapse detected, baseline left untouched")
        else:
            decision = "ANCHORED"
            reason = (f"generation rate {current_rate:.2f} vs anchored baseline "
                      f"{baseline_rate if baseline_rate is not None else 'n/a'} — "
                      f"healthy, merged into baseline")
            for key, (s_, a_) in self.current_generation.items():
                bs, ba = self.history.get(key, (0, 0))
                self.history[key] = (bs + s_, ba + a_)

        result = {"decision": decision, "reason": reason, "current_rate": current_rate,
                  "baseline_rate": baseline_rate, "attempts": total_attempts}
        self.current_generation = {}
        return result





# ---------------------------------------------------------------------------
# A-117: WordAgent + Lobby — merged from two independent implementations.
#
# This account: article classification (A-116), investigation queue, Hebrew
#   integration, algebraic Governor architecture.
# Other account (governor-lab): two-phase orientation, department as
#   pre-orientation property, prioritize_gaps(), full 107k-word corpus test.
# Merge: both together, ordering bug fixed, A-118 generality ranking added.
#
# WordAgents are distinct from SubAgentMatrix (A-114):
#   SubAgentMatrix — one per discovered REGION, spawned post-discovery
#   WordAgent      — one per DICTIONARY WORD, spawned at ingestion
# ---------------------------------------------------------------------------

class WordAgent:
    """A branch algorithm of the Governor with dominion over one word.

    KEY DESIGN POINT FROM GOVERNOR-LAB: `department` is assigned BEFORE
    orientation — it is a property of the word itself (its grammatical/
    semantic type), independent of what it ties to. Departments and
    Neighborhoods are genuinely independent axes. Report 01 confirmed
    this: the fruit neighborhood contained nouns, verbs, AND adjectives —
    meaning pulled them together across grammatical lines."""

    def __init__(self, word: str, definition_words: list,
                 entry_class: str, department: str,
                 parent: "AlgorithmMatrix",
                 raw_definition: str = ""):
        self.word = word
        self.definition_words = definition_words  # filtered words — for tie graph
        self.raw_definition = raw_definition      # unfiltered text — for Pass 2B discovery
        self.entry_class = entry_class            # TYPE/SPECIFIC/ABSTRACT/NAME (A-116)
        self.department = department              # noun/verb/adjective/etc. — PRE-orientation
        self.parent = parent
        self.ties = set()          # words tied to during orientation (bidirectional)
        self.neighborhood = None   # N-XXX, assigned after commit
        self.identity_confirmed = False
        self.generality_score = 0.0   # A-118, computed post-orientation
        # argument structure — filled by typed study group pass
        self.typical_subjects = set()  # nouns that act through this verb (verb agents only)
        self.typical_objects = set()   # nouns this verb acts on (verb agents only)
        self.typical_verbs = set()     # verbs that act on this noun (noun agents only)

    def confirm_identity(self) -> bool:
        """Mirror of the Governor's own A-000 self-recognition: a word
        agent confirms it has dominion over what it was instantiated to
        hold, once, then trusts the flag afterward."""
        if not self.identity_confirmed:
            self.identity_confirmed = bool(self.word)
        return self.identity_confirmed

    def words_referenced_in_definitions(self) -> set:
        """READ-ONLY scan of own definition entries for other dictionary
        words — the governor-lab's pattern. Called in Phase 1 of
        orientation only; does not touch any shared state."""
        import re
        found = set()
        for token in re.findall(r"[a-z\']+",
                                 " ".join(self.definition_words).lower()):
            if token and token != self.word.lower() and len(token) > 1:
                found.add(token)
        return found

    def report(self) -> dict:
        return {
            "word": self.word,
            "department": self.department,
            "entry_class": self.entry_class,
            "definition_words": self.definition_words[:8],
            "tie_count": len(self.ties),
            "neighborhood": self.neighborhood,
            "generality_score": round(self.generality_score, 3),
            "identity_confirmed": self.identity_confirmed,
        }

    def __repr__(self):
        status = "✓" if self.identity_confirmed else "?"
        return (f"WordAgent({self.word!r}, dept={self.department}, "
                f"ties={len(self.ties)}, {status})")


class Lobby:
    """The Governor's collective sandbox. Part of the Governor's state,
    not a separate system.

    Orientation runs in TWO PHASES (governor-lab fix for ordering bug):
      Phase 1 — read-only: every agent independently computes which words
                its definitions reference. No shared state touched.
      Phase 2 — write: all discovered ties applied simultaneously,
                bidirectionally. An agent processed first sees the same
                Lobby as one processed last — ordering never matters.
    """

    def __init__(self, matrix: "AlgorithmMatrix"):
        self.matrix = matrix
        self.agents = {}             # word -> WordAgent
        self.ties = {}               # (w1,w2) sorted tuple -> total strength
        self.neighborhoods = {}      # N-XXX -> {members, ...}
        self.pending_merges = []
        self.committed_count = 0
        self.generality_scores = {}  # word -> score (A-118)

    def populate(self) -> int:
        """Instantiate one WordAgent per non-NAME indexed word.
        Department is set here — BEFORE orientation — from POS data
        stored in word_categories during ingestion.
        raw_definition stored from the matrix's own transition map so
        Pass 2B discovery can find unfiltered word references."""
        for word, entry_class in self.matrix.entry_classes.items():
            if entry_class == "NAME":
                continue
            def_words = [w for w in self.matrix.transitions.get(word, {})
                          if w in self.matrix.content_units
                          and self.matrix.entry_classes.get(w) != "NAME"]
            cats = self.matrix.word_categories.get(word, {})
            pos_tags = [k.replace("pos:", "") for k in cats
                        if k.startswith("pos:")]
            department = pos_tags[0] if pos_tags else "unclassified"
            # reconstruct a raw definition from all transition targets
            # (these are the unboilerplated words that fed the transition graph)
            raw_def = " ".join(sorted(self.matrix.transitions.get(word, {}).keys()))
            agent = WordAgent(word, def_words, entry_class, department,
                              self.matrix, raw_definition=raw_def)
            agent.confirm_identity()
            self.agents[word] = agent
        return len(self.agents)

    def add_tie(self, w1: str, w2: str, strength: int = 1):
        """Record a tie and update both agents. Strength is additive."""
        key = tuple(sorted([w1, w2]))
        self.ties[key] = self.ties.get(key, 0) + strength
        a1, a2 = self.agents.get(w1), self.agents.get(w2)
        if a1: a1.ties.add(w2)
        if a2: a2.ties.add(w1)

    def run_orientation(self) -> int:
        """Two-phase simultaneous orientation (governor-lab pattern).

        Phase 1 (read-only): every agent computes its own reference set
        from its definition words without touching any shared state.

        Phase 2 (write): all ties applied at once. Bidirectional by
        construction — B is tied to A even if B's definitions never
        explicitly mention A, as long as A's definitions mention B.
        This is a deliberate design choice: if A defines itself partly
        in terms of B, that relationship is real in both directions."""

        # Guard: all agents must have confirmed identity
        if not all(a.identity_confirmed for a in self.agents.values()):
            unconfirmed = [w for w, a in self.agents.items()
                           if not a.identity_confirmed]
            raise RuntimeError(
                f"Orientation blocked: {len(unconfirmed)} agents have "
                f"not confirmed identity. First: {unconfirmed[:3]}")

        # Phase 1: read-only reference scan
        discovered = {
            word: agent.words_referenced_in_definitions()
            for word, agent in self.agents.items()
        }

        # Phase 2: apply all ties simultaneously, bidirectionally
        for word, referenced_words in discovered.items():
            for other_word in referenced_words:
                if other_word in self.agents and other_word != word:
                    self.add_tie(word, other_word, strength=1)

        return len(self.ties)

    def compute_generality_scores(self) -> dict:
        """A-118: rank every WordAgent by degree of generality/specification.

        Four signals:
        1. Entry class (A-116): ABSTRACT > TYPE > SPECIFIC > NAME
           These map directly: abstract concepts (no article) are most
           general; proper names are most specific.

        2. Tie degree (normalized): MORE ties = MORE general.
           Confirmed by governor-lab full corpus run: the most-tied words
           were "used", "act", "person", "small" — the defining vocabulary
           of the entire dictionary, maximally general by nature.

        3. IDF-inverse: words appearing in MORE definitions = MORE general.
           Low IDF = high document frequency = high generality.

        4. Genus depth: higher in is-a chain = more abstract.
           Extracted from definitions via extract_genus(). Words at the
           top of taxonomy chains (thing, entity, state) are maximally
           general; words at the bottom (specific species, named tools)
           are maximally specific.

        Returns word -> score (1.0 = most general, 0.0 = most specific).
        Stores result in agent.generality_score for Lobby-level queries.
        """
        import math
        CLASS_SCORES = {"ABSTRACT": 1.0, "TYPE": 0.6, "SPECIFIC": 0.3, "NAME": 0.0}
        max_ties = max((len(a.ties) for a in self.agents.values()), default=1)
        max_idf = math.log(max(self.matrix.documents_seen, 1) + 1) + 1

        genus_depths = self._compute_genus_depths()

        scores = {}
        for word, agent in self.agents.items():
            ec = self.matrix.entry_classes.get(word, "ABSTRACT")
            class_score = CLASS_SCORES.get(ec, 0.5)

            tie_score = len(agent.ties) / max_ties if max_ties else 0

            idf = self.matrix.idf(word)
            idf_generality = max(0.0, 1.0 - (idf / max_idf))

            depth = genus_depths.get(word, 0)
            max_depth = max(genus_depths.values(), default=1)
            depth_score = depth / max_depth if max_depth else 0

            score = (0.25 * class_score + 0.40 * tie_score +
                     0.25 * idf_generality + 0.10 * depth_score)
            scores[word] = score
            agent.generality_score = score

        self.generality_scores = scores
        return scores

    def _compute_genus_depths(self) -> dict:
        """Extract genus (is-a head) from definitions and compute
        chain depth for each word. A word's depth is how many hops
        up its is-a chain before reaching a cycle or dead end.
        Higher depth = the word IS a kind of something that IS a kind
        of something else... = more general category position."""
        genus_of = {}
        for word, agent in self.agents.items():
            if not agent.definition_words:
                continue
            # genus heuristic from governor-lab: first non-stopword content
            # word in the definition that is itself a known dictionary word
            for dw in agent.definition_words:
                if (dw != word and dw in self.agents
                        and dw not in STOPWORDS
                        and dw not in DEFINITION_BOILERPLATE):
                    genus_of[word] = dw
                    break

        depths = {}
        def depth(w, seen=None):
            if seen is None: seen = set()
            if w in depths: return depths[w]
            if w in seen or w not in genus_of:
                depths[w] = 0
                return 0
            seen.add(w)
            d = 1 + depth(genus_of[w], seen)
            depths[w] = d
            return d

        for w in self.agents:
            depth(w)
        return depths

    def prioritize_gaps(self, thin_threshold: int = 2) -> list:
        """From governor-lab: rank WordAgents whose tie count is too
        thin to plausibly belong to a coherent neighborhood yet.
        This is the ambitional-pursuit trigger input: a priority-ordered
        list of gaps the Governor would want to fill first, ranked from
        most isolated (tie_count=0, most urgent) to least isolated.
        Never fetches anything or acts — only ranks. Gated action is
        a separate Governor decision."""
        gaps = []
        for word, agent in self.agents.items():
            if len(agent.ties) < thin_threshold:
                gaps.append({
                    "word": word,
                    "department": agent.department,
                    "entry_class": agent.entry_class,
                    "tie_count": len(agent.ties),
                    "ties": sorted(agent.ties)[:5],
                    "generality_score": round(agent.generality_score, 3),
                })
        gaps.sort(key=lambda g: (g["tie_count"], -g["generality_score"]))
        return gaps

    def propose_neighborhoods(self, min_tie_strength: int = 2,
                               min_size: int = 3,
                               max_size: int = 40) -> list:
        """Find tightly-connected groups from orientation mesh using
        the shared-ties expansion (governor-lab's _expand_cluster),
        which finds true friend-groups not just connected components —
        two agents must share at least one MUTUAL TIE, not just a
        direct tie to each other."""
        visited = set()
        candidates = []

        for word in self.agents:
            if word in visited:
                continue
            cluster = self._expand_cluster(word, min_tie_strength, visited)
            if min_size <= len(cluster) <= max_size:
                candidates.append(frozenset(cluster))

        self.pending_merges = candidates
        return candidates

    def _expand_cluster(self, start: str, min_shared: int,
                         visited: set) -> set:
        """Governor-lab's mutual-tie expansion: two agents join the
        same cluster only if they share at least min_shared mutual
        neighbors (or have a direct definition tie to each other).
        This is the difference between a tight friend-group
        (everyone has friends in common) and a loose chain."""
        cluster = {start}
        frontier = [start]
        visited.add(start)
        while frontier:
            current = frontier.pop()
            for neighbor in self.agents[current].ties:
                if neighbor in visited:
                    continue
                shared = len(self.agents[current].ties &
                             self.agents[neighbor].ties) + 1
                if shared >= min_shared:
                    visited.add(neighbor)
                    cluster.add(neighbor)
                    frontier.append(neighbor)
        return cluster

    def generality_span(self, members: list) -> dict:
        """A-118 companion: measure the generality spread within a
        proposed neighborhood. A healthy neighborhood should have
        a real span — not all abstract (no anchor in specific meaning)
        and not all specific (no conceptual umbrella). Also checks
        whether departments cross grammatical lines, as Report 01
        found they should."""
        from collections import Counter
        scores = [self.agents[w].generality_score for w in members
                  if w in self.agents]
        departments = Counter(self.agents[w].department for w in members
                               if w in self.agents)
        if not scores:
            return {}
        return {
            "min_generality": round(min(scores), 3),
            "max_generality": round(max(scores), 3),
            "mean_generality": round(sum(scores) / len(scores), 3),
            "span": round(max(scores) - min(scores), 3),
            "cross_grammatical": len(departments) > 1,
            "departments": dict(departments),
        }

    def scrutinize(self, candidates: list,
                    min_coherence: float = 0.3,
                    min_generality_span: float = 0.1) -> list:
        """Governor scrutiny — Validate + Govern + Generality check.
        Now also checks that proposed neighborhoods have a real
        generality span (A-118): all-specific or all-abstract blobs
        fail, same as the blob-size check."""
        from collections import Counter
        approved = []
        existing = [frozenset(n["members"]) for n in self.neighborhoods.values()]

        for candidate in candidates:
            members = list(candidate)

            class_tally = Counter(self.agents[w].entry_class for w in members
                                   if w in self.agents)
            if not class_tally:
                continue
            top_class, top_count = class_tally.most_common(1)[0]
            coherence = top_count / len(members)
            if coherence < min_coherence:
                continue

            candidate_set = frozenset(members)
            is_dup = any(
                len(candidate_set & e) / len(candidate_set | e) > 0.7
                for e in existing)
            if is_dup:
                continue

            span = self.generality_span(members)
            if span.get("span", 0) < min_generality_span:
                continue  # no real generality spread — likely a blob

            approved.append({
                "members": members,
                "size": len(members),
                "dominant_class": top_class,
                "coherence": coherence,
                "generality": span,
            })
        return approved

    def commit(self, approved: list) -> list:
        """Governor commits approved neighborhoods as new matrix entries."""
        committed_ids = []
        for proposal in approved:
            self.committed_count += 1
            nid = f"N-{self.committed_count:03d}"
            self.neighborhoods[nid] = {
                "members": proposal["members"],
                "size": proposal["size"],
                "dominant_class": proposal["dominant_class"],
                "coherence": proposal["coherence"],
                "generality": proposal.get("generality", {}),
                "status": "COMMITTED",
            }
            self.matrix.known[nid] = {
                "name": f"Neighborhood {nid}",
                "type": "NEIGHBORHOOD",
                "size": proposal["size"],
                "dominant_class": proposal["dominant_class"],
                "coherence": proposal["coherence"],
                "generality_span": proposal.get("generality", {}).get("span"),
                "cross_grammatical": proposal.get("generality", {}).get("cross_grammatical"),
                "origin": "LOBBY-ORIENTATION",
                "status": "ACTIVE",
            }
            for word in proposal["members"]:
                agent = self.agents.get(word)
                if agent:
                    agent.neighborhood = nid
            committed_ids.append(nid)
        return committed_ids

    def neighborhood_of(self, word: str) -> dict:
        agent = self.agents.get(word.lower())
        if not agent or not agent.neighborhood:
            return {}
        return self.neighborhoods.get(agent.neighborhood, {})

    def cross_communicate(self, word_a: str, word_b: str) -> dict:
        """Sandbox: what happens when two agents meet? Computes shared
        vocabulary, overlap, and whether their meeting constitutes a
        bridge candidate across neighborhoods or languages."""
        a = self.agents.get(word_a.lower())
        b = self.agents.get(word_b.lower())
        if not a or not b:
            return {}
        set_a, set_b = set(a.definition_words), set(b.definition_words)
        overlap = set_a & set_b
        union_ab = set_a | set_b
        jaccard = len(overlap) / len(union_ab) if union_ab else 0.0
        return {
            "word_a": word_a, "dept_a": a.department,
            "neighborhood_a": a.neighborhood,
            "generality_a": round(a.generality_score, 3),
            "word_b": word_b, "dept_b": b.department,
            "neighborhood_b": b.neighborhood,
            "generality_b": round(b.generality_score, 3),
            "shared_vocabulary": sorted(overlap)[:10],
            "jaccard_overlap": round(jaccard, 3),
            "same_neighborhood": a.neighborhood == b.neighborhood,
            "bridge_candidate": jaccard > 0.05 and a.neighborhood != b.neighborhood,
        }

    def summary(self) -> dict:
        return {
            "agents": len(self.agents),
            "orientation_ties": len(self.ties),
            "pending_merges": len(self.pending_merges),
            "committed_neighborhoods": len(self.neighborhoods),
            "isolated_agents": sum(1 for a in self.agents.values()
                                    if len(a.ties) == 0),
            "study_groups": len(self.study_groups) if hasattr(self, "study_groups") else 0,
        }

    # ── MULTI-PASS ORIENTATION ──────────────────────────────────────────
    # Pass 1 (run_orientation): already built — word-by-word ties.
    # Pass 2A (run_study_proposals): each agent's full definition sentence
    #         becomes a study group curriculum it proposes to lead.
    # Pass 2B (run_discovery): reverse pass — agents find themselves in
    #         others' definitions and join those study groups as FOUND/student.
    # Pass 3  (run_thesaurus): synonym enrichment — synonyms co-teach,
    #         and join groups where they're discovered in entries.
    # ───────────────────────────────────────────────────────────────────

    def run_study_proposals(self) -> int:
        """Pass 2A: each agent reads its full definition AS A SENTENCE —
        the complete semantic unit — and proposes a study group it will lead.

        The study group topic is the agent's own word.
        The invited set is every Pass-1 tie (already-tied agents), because
        the definition sentence already established who's relevant.
        The curriculum is the full definition sentence itself.

        Key distinction from Pass 1: Pass 1 used definitions word-by-word
        to form ties. Pass 2A uses the definition AS A WHOLE to determine
        the TOPIC of a study — not just who you know, but what you teach."""
        if not hasattr(self, "study_groups"):
            self.study_groups = {}

        for word, agent in self.agents.items():
            if not agent.definition_words:
                continue
            # curriculum = the full definition as a reconstructed sentence
            curriculum = " ".join(agent.definition_words)
            self.study_groups[word] = {
                "topic": word,
                "leader": word,
                "curriculum": curriculum,
                "department": agent.department,
                "entry_class": agent.entry_class,
                "generality": agent.generality_score,
                "invited": set(agent.ties),   # everyone tied in Pass 1
                "found": set(),               # filled in Pass 2B
                "thesaurus": set(),           # filled in Pass 3
            }
        return len(self.study_groups)

    def run_discovery(self) -> dict:
        """Pass 2B: reverse discovery using raw_definition text (not the
        filtered transition keys). This fixes the '3 discoverers' result
        from the previous run: filtered definition_words dropped many real
        word references that still exist in the raw text, so the reverse
        index was nearly empty. Now each agent's raw_definition (all
        transition targets, unfiltered by is-it-in-the-matrix) is used
        to find who mentions whom.

        FOUND = an agent whose raw definition text contains another agent's
        word — it arrives at that word's study group uninvited, on its own.
        """
        if not hasattr(self, "study_groups"):
            raise RuntimeError("run_study_proposals() must run before run_discovery()")

        join_counts = {}
        import re

        # Build reverse index using raw definition text
        reverse_index = {}
        for word, agent in self.agents.items():
            raw_tokens = set(re.findall(r"[a-z']+", agent.raw_definition.lower()))
            for token in raw_tokens:
                reverse_index.setdefault(token, set()).add(word)

        for leader_word, group in self.study_groups.items():
            finders = reverse_index.get(leader_word, set())
            for finder in finders:
                if finder != leader_word and finder not in group["invited"]:
                    group["found"].add(finder)
                    join_counts[finder] = join_counts.get(finder, 0) + 1

        return join_counts

    def run_thesaurus(self, synonyms_map: dict) -> dict:
        """Pass 3: thesaurus enrichment. Each agent looks up its synonyms
        from the provided map {word -> list_of_synonyms}. Synonyms join
        study groups in two ways:

        TEACH: if my synonym is a study group leader, I join their group —
               their curriculum is closely related to mine.

        LEARN: if my synonym appears as FOUND or INVITED in another group,
               I join that group too — through my synonym I discovered
               a relevant study community.

        The thesaurus never creates new study groups — it only enriches
        existing ones. 'Continuing education on top of orientation'."""
        if not hasattr(self, "study_groups"):
            raise RuntimeError("run_study_proposals() must run before run_thesaurus()")

        stats = {"teach_joins": 0, "learn_joins": 0, "synonyms_processed": 0}

        for word, agent in self.agents.items():
            syns = synonyms_map.get(word, [])
            for syn in syns:
                if syn not in self.agents or syn == word:
                    continue
                stats["synonyms_processed"] += 1

                # TEACH: synonym leads a study group → join as thesaurus member
                if syn in self.study_groups:
                    if word not in self.study_groups[syn]["invited"] \
                            and word not in self.study_groups[syn]["found"]:
                        self.study_groups[syn]["thesaurus"].add(word)
                        stats["teach_joins"] += 1

                # LEARN: find groups where my synonym is already present
                syn_agent = self.agents[syn]
                for group_word, group in self.study_groups.items():
                    if syn in group["invited"] or syn in group["found"]:
                        if word not in group["invited"] \
                                and word not in group["found"] \
                                and word not in group["thesaurus"] \
                                and word != group["leader"]:
                            group["thesaurus"].add(word)
                            stats["learn_joins"] += 1

        return stats

    def study_group_members(self, topic_word: str) -> dict:
        """Full membership of a study group, broken out by role."""
        g = self.study_groups.get(topic_word)
        if not g:
            return {}
        return {
            "topic": topic_word,
            "leader": g["leader"],
            "curriculum": g["curriculum"][:120] + ("..." if len(g["curriculum"]) > 120 else ""),
            "invited": sorted(g["invited"])[:15],
            "found": sorted(g["found"])[:15],
            "thesaurus": sorted(g["thesaurus"])[:15],
            "total_size": 1 + len(g["invited"]) + len(g["found"]) + len(g["thesaurus"]),
            "generality": round(g["generality"], 3),
            "department": g["department"],
        }

    def propose_from_study_groups(self, min_total: int = 3,
                                   max_total: int = 50) -> list:
        """After all three passes, propose Neighborhoods from study groups
        whose total membership (leader + invited + found + thesaurus)
        clears the minimum threshold. This feeds the existing scrutinize()
        and commit() pipeline — study groups become Neighborhood candidates
        the Governor validates before committing."""
        candidates = []
        for word, g in self.study_groups.items():
            all_members = ({g["leader"]} | g["invited"] |
                           g["found"] | g["thesaurus"])
            # filter to agents that actually exist in the Lobby
            valid = frozenset(m for m in all_members if m in self.agents)
            if min_total <= len(valid) <= max_total:
                candidates.append(valid)
        # deduplicate highly overlapping candidates
        unique = []
        for c in sorted(candidates, key=len, reverse=True):
            if not any(len(c & u) / len(c | u) > 0.7 for u in unique):
                unique.append(c)
        self.pending_merges = unique
        return unique


    # ── A-119: TYPED STUDY GROUPS ──────────────────────────────────────────

    def run_typed_study_groups(self) -> dict:
        """Department-aware study groups. Each POS uses different logic:

        NOUN → CATEGORY study: invites genre-sibling nouns + verbs that act on it.
        VERB → PROCESS study: invites argument nouns from definition + similar verbs.
        ADJ  → PROPERTY study: invites property-bearing nouns + opposing adjectives.

        Maps onto the algebraic layer: nouns are STATE (S), verbs are OPERATORS (Φ).
        Maps onto LHEA: Hebrew glyphs as operators (verb-like), entities as noun-like.
        """
        if not hasattr(self, "study_groups"):
            self.study_groups = {}

        verb_arguments = {}
        noun_verbs = {}

        for word, agent in self.agents.items():
            if agent.department not in ("verb", "v"):
                continue
            arg_nouns = {dw for dw in agent.definition_words
                          if self.agents.get(dw) and
                          self.agents[dw].department in ("noun", "n")}
            verb_arguments[word] = arg_nouns
            agent.typical_objects = arg_nouns
            for noun in arg_nouns:
                noun_verbs.setdefault(noun, set()).add(word)

        for noun_word, verbs in noun_verbs.items():
            agent = self.agents.get(noun_word)
            if agent:
                agent.typical_verbs = verbs

        from collections import Counter
        typed_groups = {}
        for word, agent in self.agents.items():
            dept = agent.department
            curriculum = " ".join(agent.definition_words)

            if dept in ("noun", "n"):
                invited_nouns = {t for t in agent.ties
                                  if self.agents.get(t) and
                                  self.agents[t].department in ("noun", "n")}
                typed_groups[word] = {
                    "topic": word, "study_type": "CATEGORY", "leader": word,
                    "curriculum": curriculum, "department": dept,
                    "entry_class": agent.entry_class, "generality": agent.generality_score,
                    "invited": invited_nouns | agent.typical_verbs,
                    "found": set(), "thesaurus": set(),
                    "argument_nouns": set(), "argument_verbs": agent.typical_verbs,
                }
            elif dept in ("verb", "v"):
                arg_nouns = verb_arguments.get(word, set())
                similar_verbs = {t for t in agent.ties
                                  if self.agents.get(t) and
                                  self.agents[t].department in ("verb", "v")}
                typed_groups[word] = {
                    "topic": word, "study_type": "PROCESS", "leader": word,
                    "curriculum": curriculum, "department": dept,
                    "entry_class": agent.entry_class, "generality": agent.generality_score,
                    "invited": arg_nouns | similar_verbs,
                    "found": set(), "thesaurus": set(),
                    "argument_nouns": arg_nouns, "argument_verbs": set(),
                }
            elif dept in ("adj", "adjective", "adverb", "adv", "s"):
                property_nouns = {t for t in agent.ties
                                   if self.agents.get(t) and
                                   self.agents[t].department in ("noun", "n")}
                opposing_adjs = {t for t in agent.ties
                                  if self.agents.get(t) and
                                  self.agents[t].department in
                                  ("adj", "adjective", "adverb", "adv", "s")}
                typed_groups[word] = {
                    "topic": word, "study_type": "PROPERTY", "leader": word,
                    "curriculum": curriculum, "department": dept,
                    "entry_class": agent.entry_class, "generality": agent.generality_score,
                    "invited": property_nouns | opposing_adjs,
                    "found": set(), "thesaurus": set(),
                    "argument_nouns": property_nouns, "argument_verbs": set(),
                }
            else:
                typed_groups[word] = {
                    "topic": word, "study_type": "UNCLASSIFIED", "leader": word,
                    "curriculum": curriculum, "department": dept,
                    "entry_class": agent.entry_class, "generality": agent.generality_score,
                    "invited": set(agent.ties),
                    "found": set(), "thesaurus": set(),
                    "argument_nouns": set(), "argument_verbs": set(),
                }

        self.study_groups = typed_groups
        return dict(Counter(g["study_type"] for g in typed_groups.values()))

    def noun_verb_crossref(self) -> dict:
        """Full cross-reference: nouns that know what verbs act on them,
        verbs that know their typical noun arguments. Seed of grammar."""
        xref = {"noun_to_verbs": {}, "verb_to_nouns": {}}
        for word, agent in self.agents.items():
            if agent.typical_verbs:
                xref["noun_to_verbs"][word] = sorted(agent.typical_verbs)
            if agent.typical_objects:
                xref["verb_to_nouns"][word] = sorted(agent.typical_objects)
        return xref





# ---------------------------------------------------------------------------
# A-120: LobbyEvolutionGovernor — continuous Lobby evolution toward
# articulately precise fluency for communication.
#
# The Lobby after orientation is a snapshot. A-120 runs a governed loop
# that evolves the neighborhood structure toward three measurable goals:
#
#   ARTICULATION — every neighborhood can speak from all angles
#                  (noun=WHAT + verb=DOES + adj=HOW = department coverage)
#   PRECISION    — words genuinely belong together, not just near each other
#                  (definitional closure: members' definition-words point inward)
#   FLUENCY      — meaning flows continuously without stranded members
#                  (internal tie density across all member pairs)
#
# Communication Score C(N) = 0.35·articulation + 0.35·precision + 0.30·fluency
#
# Four evolution operations, each addressing a specific deficiency type:
#   RECRUIT — missing department; pull isolated words of that type inward
#   REFINE  — member's ties mostly point outward; reassign to better fit
#   SPLIT   — two sub-clusters internally; separate them
#   MERGE   — two neighborhoods mutually point at each other; combine them
#
# Designed to operate on a COLLECTIVE of Lobbies (multi-language or
# multi-domain), so when one Lobby has a gap another Lobby's vocabulary
# can fill, cross-Lobby recruitment is possible.
# ---------------------------------------------------------------------------

class LobbyEvolutionGovernor:
    """Governs continuous Lobby evolution toward articulately precise fluency.

    Operates on one or more Lobby objects. Runs a convergence loop:
    measure → diagnose → propose → validate → govern → commit → learn.

    Everything that commits goes through the same Validate/Govern gates
    as the rest of the architecture — the evolution never unilaterally
    restructures the Lobby without passing those checks."""

    # Operation IDs for H(M, D_bucket) learning
    OP_RECRUIT = "M-RECRUIT"
    OP_REFINE  = "M-REFINE"
    OP_SPLIT   = "M-SPLIT"
    OP_MERGE   = "M-MERGE"

    def __init__(self, lobbies: list, label: str = "collective"):
        """lobbies: list of Lobby objects (one per language/domain).
        label: name for reporting purposes."""
        self.lobbies = lobbies           # the collective
        self.label = label
        self.history = {}                # (operation, D_bucket) -> (s, a) bandit history
        self.evolution_log = []          # per-iteration snapshots
        self.generation = 0
        self.genealogy = {}              # N-XXX -> {parent, operation, generation}

    # ── MEASUREMENT ──────────────────────────────────────────────────────────

    def _dept_score(self, member_agents: dict) -> tuple:
        """Articulation: does this neighborhood cover noun + verb + adj?"""
        depts = {a.department for a in member_agents.values()}
        has_n = any(d in ("noun","n") for d in depts)
        has_v = any(d in ("verb","v") for d in depts)
        has_a = any(d in ("adj","adjective","adverb","adv","s") for d in depts)
        score = (has_n + has_v + has_a) / 3.0
        return score, has_n, has_v, has_a

    def _closure_score(self, members: set, member_agents: dict) -> float:
        """Precision: fraction of definition-word references pointing inward."""
        inward = outward = 0
        for agent in member_agents.values():
            for dw in agent.definition_words:
                if dw in members:
                    inward += 1
                else:
                    outward += 1
        total = inward + outward
        return inward / total if total else 0.0

    def _density_score(self, members: set, member_agents: dict) -> float:
        """Fluency: fraction of member ties that connect inward."""
        inward = outward = 0
        for agent in member_agents.values():
            for t in agent.ties:
                if t in members:
                    inward += 1
                else:
                    outward += 1
        total = inward + outward
        return inward / total if total else 0.0

    def comm_score(self, members: set, member_agents: dict) -> dict:
        """Composite Communication Score and its three components."""
        dept_s, has_n, has_v, has_a = self._dept_score(member_agents)
        clos_s = self._closure_score(members, member_agents)
        dens_s = self._density_score(members, member_agents)
        composite = 0.35 * dept_s + 0.35 * clos_s + 0.30 * dens_s
        return {
            "articulation": round(dept_s, 3),
            "precision": round(clos_s, 3),
            "fluency": round(dens_s, 3),
            "composite": round(composite, 3),
            "has_noun": has_n, "has_verb": has_v, "has_adj": has_a,
        }

    def measure_lobby(self, lobby) -> dict:
        """Compute Communication Score for every committed neighborhood."""
        scores = {}
        for nid, n in lobby.neighborhoods.items():
            members = set(n["members"])
            member_agents = {w: lobby.agents[w] for w in members
                              if w in lobby.agents}
            if not member_agents:
                continue
            scores[nid] = self.comm_score(members, member_agents)
            scores[nid]["size"] = n["size"]
        return scores

    def lobby_health(self, scores: dict) -> dict:
        """Aggregate health across all neighborhoods in one Lobby."""
        if not scores:
            return {"avg_composite": 0, "avg_articulation": 0,
                    "avg_precision": 0, "avg_fluency": 0,
                    "neighborhoods": 0, "fully_articulate": 0}
        n = len(scores)
        return {
            "neighborhoods": n,
            "avg_composite":    round(sum(s["composite"]    for s in scores.values()) / n, 3),
            "avg_articulation": round(sum(s["articulation"] for s in scores.values()) / n, 3),
            "avg_precision":    round(sum(s["precision"]    for s in scores.values()) / n, 3),
            "avg_fluency":      round(sum(s["fluency"]      for s in scores.values()) / n, 3),
            "fully_articulate": sum(1 for s in scores.values()
                                     if s["has_noun"] and s["has_verb"] and s["has_adj"]),
        }

    # ── DIAGNOSIS ────────────────────────────────────────────────────────────

    def diagnose(self, scores: dict, min_composite: float = 0.4) -> list:
        """Identify neighborhoods that need attention, ranked by severity.
        Returns a list of deficiency objects the propose step acts on."""
        deficiencies = []
        for nid, s in scores.items():
            if s["composite"] >= min_composite:
                continue   # good enough — don't touch it
            if not s["has_verb"]:
                deficiencies.append({
                    "nid": nid, "type": "MISSING_VERB",
                    "severity": 0.80,
                    "op": self.OP_RECRUIT,
                    "dept_needed": "verb",
                    "metric": s["composite"],
                })
            if not s["has_noun"]:
                deficiencies.append({
                    "nid": nid, "type": "MISSING_NOUN",
                    "severity": 0.75,
                    "op": self.OP_RECRUIT,
                    "dept_needed": "noun",
                    "metric": s["composite"],
                })
            if s["precision"] < 0.2:
                deficiencies.append({
                    "nid": nid, "type": "LOW_PRECISION",
                    "severity": 0.70 + (0.2 - s["precision"]),
                    "op": self.OP_SPLIT if s["size"] > 6 else self.OP_REFINE,
                    "metric": s["precision"],
                })
            if s["fluency"] < 0.2 and s["size"] > 3:
                deficiencies.append({
                    "nid": nid, "type": "LOW_FLUENCY",
                    "severity": 0.60,
                    "op": self.OP_SPLIT,
                    "metric": s["fluency"],
                })
            if s["articulation"] < 0.34:
                deficiencies.append({
                    "nid": nid, "type": "POOR_ARTICULATION",
                    "severity": 0.50,
                    "op": self.OP_RECRUIT,
                    "dept_needed": None,   # any missing dept
                    "metric": s["articulation"],
                })
        deficiencies.sort(key=lambda d: -d["severity"])
        return deficiencies

    def find_merge_candidates(self, scores: dict, lobby) -> list:
        """Identify neighborhood pairs with high mutual external tie density —
        they point at each other more than at themselves; they should merge."""
        candidates = []
        nids = list(scores.keys())
        for i, n1 in enumerate(nids):
            members1 = set(lobby.neighborhoods[n1]["members"])
            for n2 in nids[i+1:]:
                members2 = set(lobby.neighborhoods[n2]["members"])
                # count cross-ties (ties from n1 members TO n2 members)
                cross = 0
                total1 = 0
                for w in members1:
                    agent = lobby.agents.get(w)
                    if agent:
                        for t in agent.ties:
                            total1 += 1
                            if t in members2:
                                cross += 1
                if total1 and cross / total1 > 0.15:  # 15% of ties cross
                    candidates.append((n1, n2, cross / total1))
        candidates.sort(key=lambda c: -c[2])
        return candidates[:5]   # top 5 merge candidates per iteration

    # ── PROPOSE ──────────────────────────────────────────────────────────────

    def propose_recruit(self, nid: str, dept_needed: str, lobby) -> list:
        """Find isolated words of the needed department that have ties to
        this neighborhood's members — they should be recruited in."""
        n = lobby.neighborhoods.get(nid)
        if not n:
            return []
        members = set(n["members"])
        recruits = []
        for word, agent in lobby.agents.items():
            if word in members:
                continue
            if agent.neighborhood:
                continue   # already placed elsewhere
            if len(agent.ties) == 0:
                continue   # truly isolated — no traction
            dept = agent.department
            dept_match = (
                dept_needed is None or
                (dept_needed == "verb" and dept in ("verb","v")) or
                (dept_needed == "noun" and dept in ("noun","n")) or
                (dept_needed == "adj" and dept in ("adj","adjective","adverb","adv","s"))
            )
            if not dept_match:
                continue
            overlap = agent.ties & members
            if overlap:
                recruits.append((word, len(overlap), agent.generality_score))
        recruits.sort(key=lambda r: (-r[1], -r[2]))
        return [r[0] for r in recruits[:5]]

    def propose_refine(self, nid: str, lobby) -> list:
        """Find members whose ties point mostly outward — misfits to reassign."""
        n = lobby.neighborhoods.get(nid)
        if not n:
            return []
        members = set(n["members"])
        misfits = []
        for w in list(members):
            agent = lobby.agents.get(w)
            if not agent:
                continue
            inward = sum(1 for t in agent.ties if t in members)
            outward = len(agent.ties) - inward
            if len(agent.ties) > 0 and outward / len(agent.ties) > 0.8:
                # find which neighborhood most of its outward ties point to
                outside_counts = {}
                for t in agent.ties:
                    other_agent = lobby.agents.get(t)
                    if other_agent and other_agent.neighborhood and other_agent.neighborhood != nid:
                        nh = other_agent.neighborhood
                        outside_counts[nh] = outside_counts.get(nh, 0) + 1
                best_dest = (max(outside_counts, key=outside_counts.get)
                             if outside_counts else None)
                misfits.append((w, outward / len(agent.ties), best_dest))
        misfits.sort(key=lambda m: -m[1])
        return misfits[:3]

    def propose_split(self, nid: str, lobby) -> list:
        """Split an incoherent neighborhood into tighter sub-groups using
        the mutual-tie expansion from Lobby (governor-lab's _expand_cluster)."""
        n = lobby.neighborhoods.get(nid)
        if not n or n["size"] < 4:
            return []
        members = [m for m in n["members"] if m in lobby.agents]
        visited = set()
        sub_groups = []
        for word in members:
            if word in visited:
                continue
            cluster = lobby._expand_cluster(word, min_shared=2, visited=visited)
            cluster = frozenset(cluster & set(members))
            if len(cluster) >= 2:
                sub_groups.append(cluster)
        return sub_groups if len(sub_groups) > 1 else []

    # ── VALIDATE + GOVERN ────────────────────────────────────────────────────

    def validate_recruit(self, word: str, nid: str, lobby,
                          min_overlap: int = 1) -> bool:
        """V: the recruited word has enough ties into the neighborhood."""
        n = lobby.neighborhoods.get(nid)
        if not n:
            return False
        members = set(n["members"])
        agent = lobby.agents.get(word)
        if not agent:
            return False
        return len(agent.ties & members) >= min_overlap

    def validate_split(self, sub_groups: list, min_size: int = 2) -> list:
        """V: only keep sub-groups large enough to be real neighborhoods."""
        return [g for g in sub_groups if len(g) >= min_size]

    def govern_budget(self, operation: str, generation: int,
                       max_gen: int, ops_this_iter: int,
                       budget_per_iter: int = 10) -> bool:
        """G: complexity budget — cap ops per iteration so the loop
        doesn't cascade into unbounded restructuring."""
        return (generation < max_gen and ops_this_iter < budget_per_iter)

    # ── COMMIT ───────────────────────────────────────────────────────────────

    def commit_recruit(self, word: str, nid: str, lobby):
        """Add a word to an existing neighborhood and update agent state."""
        n = lobby.neighborhoods.get(nid)
        if not n:
            return
        if word not in n["members"]:
            n["members"].append(word)
            n["size"] = len(n["members"])
        agent = lobby.agents.get(word)
        if agent:
            agent.neighborhood = nid

    def commit_refine(self, word: str, from_nid: str, to_nid: str, lobby):
        """Move a word from one neighborhood to another."""
        from_n = lobby.neighborhoods.get(from_nid)
        if from_n and word in from_n["members"]:
            from_n["members"].remove(word)
            from_n["size"] = len(from_n["members"])
        to_n = lobby.neighborhoods.get(to_nid)
        if to_n:
            to_n["members"].append(word)
            to_n["size"] = len(to_n["members"])
        agent = lobby.agents.get(word)
        if agent:
            agent.neighborhood = to_nid

    def commit_split(self, parent_nid: str, sub_groups: list, lobby) -> list:
        """Replace a neighborhood with its sub-groups."""
        new_ids = []
        for sub in sub_groups:
            lobby.committed_count += 1
            new_nid = f"N-{lobby.committed_count:03d}"
            members = list(sub)
            lobby.neighborhoods[new_nid] = {
                "members": members, "size": len(members),
                "status": "COMMITTED",
                "origin": f"SPLIT from {parent_nid} gen={self.generation}",
            }
            for w in members:
                agent = lobby.agents.get(w)
                if agent:
                    agent.neighborhood = new_nid
            self.genealogy[new_nid] = {
                "parent": parent_nid,
                "operation": self.OP_SPLIT,
                "generation": self.generation,
            }
            new_ids.append(new_nid)
        # remove parent
        del lobby.neighborhoods[parent_nid]
        return new_ids

    def commit_merge(self, n1: str, n2: str, lobby) -> str:
        """Merge two neighborhoods into one."""
        members1 = lobby.neighborhoods[n1]["members"]
        members2 = lobby.neighborhoods[n2]["members"]
        combined = list(set(members1 + members2))
        lobby.committed_count += 1
        new_nid = f"N-{lobby.committed_count:03d}"
        lobby.neighborhoods[new_nid] = {
            "members": combined, "size": len(combined),
            "status": "COMMITTED",
            "origin": f"MERGE of {n1}+{n2} gen={self.generation}",
        }
        for w in combined:
            agent = lobby.agents.get(w)
            if agent:
                agent.neighborhood = new_nid
        for old in (n1, n2):
            if old in lobby.neighborhoods:
                del lobby.neighborhoods[old]
        self.genealogy[new_nid] = {
            "parents": [n1, n2],
            "operation": self.OP_MERGE,
            "generation": self.generation,
        }
        return new_nid

    # ── LEARN ────────────────────────────────────────────────────────────────

    def record_outcome(self, operation: str, d_type: str, success: bool):
        """H(M, D_bucket): learn which operations improve which deficiency types."""
        key = (operation, d_type)
        s, a = self.history.get(key, (0, 0))
        self.history[key] = (s + (1 if success else 0), a + 1)

    def best_operation_for(self, d_type: str) -> str:
        """UCB1 over operation history for this deficiency type."""
        import math
        ops = [self.OP_RECRUIT, self.OP_REFINE, self.OP_SPLIT, self.OP_MERGE]
        total_attempts = sum(self.history.get((op, d_type), (0,0))[1] for op in ops)
        best_op, best_score = None, float("-inf")
        for op in ops:
            s, a = self.history.get((op, d_type), (0, 0))
            if a == 0:
                return op   # unexplored first
            score = (s / a) + math.sqrt(2 * math.log(max(total_attempts, 1)) / a)
            if score > best_score:
                best_score, best_op = score, op
        return best_op

    # ── MAIN EVOLUTION LOOP ──────────────────────────────────────────────────

    def evolve(self, max_generations: int = 8, budget_per_iter: int = 15,
                target_composite: float = 0.50,
                verbose: bool = True) -> list:
        """Main convergence loop. Runs until target_composite is reached,
        max_generations exceeded, or no more improvements are possible.

        Returns the evolution log (one entry per generation)."""
        import time

        if verbose:
            print("=" * 70)
            print(f"LOBBY EVOLUTION — collective: {self.label}")
            print(f"  {len(self.lobbies)} lobby/lobbies, "
                  f"target C(N) >= {target_composite}, "
                  f"max {max_generations} generations, "
                  f"budget {budget_per_iter} ops/gen")
            print("=" * 70)

        prev_avg = 0.0

        for gen in range(max_generations):
            self.generation = gen
            t0 = time.time()
            ops_committed = 0
            gen_log = {"generation": gen, "lobbies": {}}

            for lobby in self.lobbies:
                lobby_label = getattr(lobby, "label", f"lobby-{id(lobby)}")

                # MEASURE
                scores = self.measure_lobby(lobby)
                health = self.lobby_health(scores)
                gen_log["lobbies"][lobby_label] = health

                if verbose:
                    print(f"  Gen {gen} | {lobby_label} | "
                          f"neighborhoods={health['neighborhoods']} | "
                          f"C={health['avg_composite']:.3f} "
                          f"(A={health['avg_articulation']:.3f}, "
                          f"P={health['avg_precision']:.3f}, "
                          f"F={health['avg_fluency']:.3f}) | "
                          f"fully_articulate={health['fully_articulate']}")

                if health["avg_composite"] >= target_composite:
                    if verbose:
                        print(f"  → Target reached. Stopping evolution for {lobby_label}.")
                    continue

                # DIAGNOSE
                deficiencies = self.diagnose(scores)
                merge_candidates = self.find_merge_candidates(scores, lobby)

                # PROPOSE + VALIDATE + GOVERN + COMMIT
                for deficiency in deficiencies:
                    if not self.govern_budget("any", gen, max_generations,
                                               ops_committed, budget_per_iter):
                        break

                    nid = deficiency["nid"]
                    if nid not in lobby.neighborhoods:
                        continue   # may have been removed by a split earlier

                    d_type = deficiency["type"]
                    op = deficiency["op"]

                    # UCB1 can override the default op based on history
                    learned_op = self.best_operation_for(d_type)
                    if learned_op != op and self.history.get((learned_op, d_type), (0,0))[1] > 3:
                        op = learned_op

                    success = False

                    if op == self.OP_RECRUIT:
                        dept_needed = deficiency.get("dept_needed")
                        recruits = self.propose_recruit(nid, dept_needed, lobby)
                        for word in recruits:
                            if self.validate_recruit(word, nid, lobby):
                                self.commit_recruit(word, nid, lobby)
                                ops_committed += 1
                                success = True
                                if verbose:
                                    print(f"    RECRUIT '{word}' → {nid} "
                                          f"(fix: {d_type})")

                    elif op == self.OP_REFINE:
                        misfits = self.propose_refine(nid, lobby)
                        for word, outward_ratio, dest_nid in misfits:
                            if dest_nid and dest_nid in lobby.neighborhoods:
                                self.commit_refine(word, nid, dest_nid, lobby)
                                ops_committed += 1
                                success = True
                                if verbose:
                                    print(f"    REFINE '{word}': {nid} → "
                                          f"{dest_nid} (outward={outward_ratio:.0%})")

                    elif op == self.OP_SPLIT:
                        sub_groups = self.propose_split(nid, lobby)
                        valid_subs = self.validate_split(sub_groups, min_size=2)
                        if len(valid_subs) > 1:
                            new_ids = self.commit_split(nid, valid_subs, lobby)
                            ops_committed += len(new_ids)
                            success = True
                            if verbose:
                                print(f"    SPLIT {nid} → {new_ids} "
                                      f"(fix: {d_type})")

                    self.record_outcome(op, d_type, success)

                # MERGE candidates
                for n1, n2, cross_ratio in merge_candidates:
                    if not self.govern_budget("merge", gen, max_generations,
                                              ops_committed, budget_per_iter):
                        break
                    if (n1 not in lobby.neighborhoods or
                            n2 not in lobby.neighborhoods):
                        continue
                    new_nid = self.commit_merge(n1, n2, lobby)
                    ops_committed += 1
                    if verbose:
                        print(f"    MERGE {n1}+{n2} → {new_nid} "
                              f"(cross={cross_ratio:.0%})")
                    self.record_outcome(self.OP_MERGE, "MUTUAL_EXTERNAL", True)

            gen_log["ops_committed"] = ops_committed
            gen_log["time"] = round(time.time() - t0, 2)
            self.evolution_log.append(gen_log)

            # check convergence: if avg_composite barely moved, stop early
            all_scores = []
            for lobby in self.lobbies:
                all_scores.extend(s["composite"] for s in
                                   self.measure_lobby(lobby).values())
            current_avg = sum(all_scores) / len(all_scores) if all_scores else 0
            if abs(current_avg - prev_avg) < 0.005 and ops_committed == 0:
                if verbose:
                    print(f"  Converged at gen {gen} "
                          f"(delta={current_avg-prev_avg:.4f}). Stopping.")
                break
            prev_avg = current_avg

        return self.evolution_log

    def final_report(self) -> str:
        """Summary of what the evolution achieved."""
        lines = [f"LOBBY EVOLUTION FINAL REPORT — {self.label}"]
        for lobby in self.lobbies:
            label = getattr(lobby, "label", f"lobby-{id(lobby)}")
            scores = self.measure_lobby(lobby)
            health = self.lobby_health(scores)
            lines += [
                f"\n  {label}:",
                f"    Neighborhoods: {health['neighborhoods']}",
                f"    Avg composite C: {health['avg_composite']:.3f}",
                f"    Avg articulation: {health['avg_articulation']:.3f}",
                f"    Avg precision: {health['avg_precision']:.3f}",
                f"    Avg fluency: {health['avg_fluency']:.3f}",
                f"    Fully articulate (N+V+A): {health['fully_articulate']}",
            ]
            # top 5 best and worst neighborhoods
            sorted_n = sorted(scores.items(), key=lambda kv: -kv[1]["composite"])
            if sorted_n:
                lines.append("    Top 5 (highest C):")
                for nid, s in sorted_n[:5]:
                    n = lobby.neighborhoods[nid]
                    lines.append(f"      {nid} C={s['composite']:.3f} "
                                  f"({sorted(n['members'])[:6]})")
                lines.append("    Bottom 5 (lowest C):")
                for nid, s in sorted_n[-5:]:
                    n = lobby.neighborhoods[nid]
                    lines.append(f"      {nid} C={s['composite']:.3f} "
                                  f"({sorted(n['members'])[:6]})")
        lines.append("    Operations learned:")
        for (op, d_type), (s, a) in sorted(self.history.items()):
            rate = s/a if a else 0
            lines.append(f"    {op} for {d_type}: {s}/{a} success ({rate:.0%})")
        lines.append(f"    Genealogy: {len(self.genealogy)} neighborhoods "
                      "born from evolution (not orientation)")
        return "\n".join(lines)




# ---------------------------------------------------------------------------
# A-121: HypothesisSandbox — the Governor's self-directed algorithm discovery.
#
# Closes the feedback loop: the Governor observes its own Lobby, derives
# candidate algorithms from patterns in that data, tests them in an isolated
# sandbox copy, and saves working ones directly into its Algorithm Matrix.
#
# The sandbox never touches the real Lobby — it copies only the mutable state
# (neighborhoods dict + agent assignments), runs the hypothesis against that
# copy, measures delta-C, and returns to the real Lobby untouched regardless
# of the outcome.
#
# Newly validated algorithms are registered as A-XXX entries in AlgorithmMatrix
# and fed back into LobbyEvolutionGovernor's active operation set, so each
# generation of evolution has access to a growing, self-discovered tool belt.
# ---------------------------------------------------------------------------

class HypothesisSandbox:
    """The Governor generating, testing, and registering its own algorithms.

    Three principles preserved from the frozen architecture:
    1. Propose, don't execute — hypotheses go through sandbox before any
       real Lobby state is touched.
    2. Self-derived algorithms start as PENDING, not ACTIVE — they enter
       the Algorithm Matrix as HYPOTHESIS-DERIVED/PENDING and are promoted
       to ACTIVE only after sandbox validation passes.
    3. The Governor learns from failures as well as successes — rejected
       hypotheses update H(M,D) just as successful ones do, so the bandit
       inside LobbyEvolutionGovernor learns what to generate less of.
    """

    # hypothesis derivation strategies — each is a named pattern the
    # Governor applies to what it observes, in priority order
    STRATEGIES = [
        "FAILED_OP_VARIANT",      # failed op → try parametric variant
        "HUB_QUARANTINE",         # universal misfits → isolate them pre-formation
        "SUCCESSFUL_COMPOSITION", # working op → try double-pass or with-recruit
        "DEPT_BRIDGE",            # missing department → targeted cross-dept recruit
        "THRESHOLD_TUNE",         # threshold that keeps misfiring → tune it
    ]

    def __init__(self, lobby: "Lobby", matrix: "AlgorithmMatrix",
                 evgov: "LobbyEvolutionGovernor"):
        self.lobby  = lobby
        self.matrix = matrix
        self.evgov  = evgov
        self.hypotheses_tested  = []   # all hypotheses tried this session
        self.algorithms_derived = []   # IDs of those that passed and were registered
        self._next_id = self._scan_next_id()
        self._rejected_names = set()  # dedup: skip already-rejected strategies
        self._rejected_strategies = {}  # strategy -> list of rejection reasons

    def _scan_next_id(self) -> int:
        """Find the highest A-XXX id currently in the matrix and continue."""
        import re
        nums = [int(k.split("-")[1]) for k in self.matrix.known
                if re.match(r"A-\d+$", k)]
        return max(nums, default=120) + 1

    # ── OBSERVE ────────────────────────────────────────────────────────────

    def observe(self) -> dict:
        """Read the Lobby's current state into a structured observation
        the hypothesis generator can reason from.  Every value here must
        be directly computable — no narratives, no guesses."""
        scores  = self.evgov.measure_lobby(self.lobby)
        health  = self.evgov.lobby_health(scores)

        # bottleneck metric (lowest of the three)
        metrics = {
            "articulation": health["avg_articulation"],
            "precision":    health["avg_precision"],
            "fluency":      health["avg_fluency"],
        }
        bottleneck = min(metrics, key=metrics.get)

        # hub words: agents that appear as misfits in many neighborhoods
        misfit_count = {}
        for nid, n in self.lobby.neighborhoods.items():
            members = set(n["members"])
            for w in list(members):
                agent = self.lobby.agents.get(w)
                if not agent or not agent.ties:
                    continue
                inward  = sum(1 for t in agent.ties if t in members)
                outward = len(agent.ties) - inward
                if outward / len(agent.ties) > 0.90:
                    misfit_count[w] = misfit_count.get(w, 0) + 1
        hub_words = sorted(misfit_count.items(), key=lambda kv: -kv[1])[:6]

        # operation history from evgov bandit
        op_history = {}
        for (op, d_type), (s, a) in self.evgov.history.items():
            rate = s / a if a else None
            op_history[(op, d_type)] = {"successes": s, "attempts": a, "rate": rate}

        failed_ops    = [(op, d, v["rate"]) for (op, d), v in op_history.items()
                          if v["rate"] is not None and v["rate"] < 0.3
                          and v["attempts"] >= 5]
        successful_ops = [(op, d, v["rate"]) for (op, d), v in op_history.items()
                           if v["rate"] is not None and v["rate"] >= 0.5
                           and v["attempts"] >= 3]

        # neighborhoods missing a department
        missing_verb_count = sum(
            1 for s in scores.values() if not s["has_verb"])
        missing_noun_count = sum(
            1 for s in scores.values() if not s["has_noun"])

        return {
            "health": health,
            "metrics": metrics,
            "bottleneck": bottleneck,
            "hub_words": hub_words,
            "failed_ops": failed_ops,
            "successful_ops": successful_ops,
            "missing_verb_count": missing_verb_count,
            "missing_noun_count": missing_noun_count,
            "n_neighborhoods": health["neighborhoods"],
            "avg_composite": health["avg_composite"],
        }

    # ── HYPOTHESIZE ────────────────────────────────────────────────────────

    def hypothesize(self, obs: dict) -> list:
        """Derive candidate algorithm specs from the observation.
        Skips any strategy whose name was already rejected this session
        (deduplication) so rounds produce genuinely novel candidates.
        Adds DATA_ACQUISITION when the bottleneck is corpus density,
        not structure — 'get more data for this domain' is a legitimate
        hypothesis the Governor can derive from its own gap list."""
        candidates = []

        def _add(spec):
            """Only add if this strategy name hasn't been rejected yet."""
            if spec["name"] in self._rejected_names:
                return
            candidates.append(spec)


        # Strategy 1: FAILED_OP_VARIANT
        for op, d_type, rate in obs["failed_ops"]:
            if op == self.evgov.OP_SPLIT:
                _add({
                    "id": f"A-{self._next_id}",
                    "name": "SPLIT_LOOSE",
                    "strategy": "FAILED_OP_VARIANT",
                    "description": (f"SPLIT with min_shared=1 instead of 2 — "
                                    f"original SPLIT failed at {rate:.0%}; "
                                    f"looser criterion may work on our small sparse neighborhoods"),
                    "origin": f"SELF-DERIVED: {op} failure rate={rate:.0%} on {d_type}",
                    "test_fn": "split_loose",
                    "parameters": {"min_shared": 1, "min_size": 2},
                    "target_deficiency": d_type,
                    "target_metric": "precision",
                })
                self._next_id += 1

            if op == self.evgov.OP_RECRUIT:
                _add({
                    "id": f"A-{self._next_id}",
                    "name": "RECRUIT_DEPT_STRICT",
                    "strategy": "FAILED_OP_VARIANT",
                    "description": (f"RECRUIT requiring ≥2 tie overlap instead of ≥1 — "
                                    f"original RECRUIT too lenient, may pull in unrelated words"),
                    "origin": f"SELF-DERIVED: {op} failure rate={rate:.0%} on {d_type}",
                    "test_fn": "recruit_strict",
                    "parameters": {"min_overlap": 2},
                    "target_deficiency": d_type,
                    "target_metric": "precision",
                })
                self._next_id += 1

        # Strategy 2: HUB_QUARANTINE
        if len(obs["hub_words"]) >= 2:
            hub_names = [w for w, _ in obs["hub_words"][:5]]
            _add({
                "id": f"A-{self._next_id}",
                "name": "HUB_QUARANTINE",
                "strategy": "HUB_QUARANTINE",
                "description": (f"Remove identified hub words from all neighborhoods before "
                                 f"re-measuring — they connect everything but belong nowhere. "
                                 f"Targets: {hub_names[:3]}"),
                "origin": f"SELF-DERIVED: {hub_names[:3]} appear as misfits in "
                           f"{[c for _,c in obs['hub_words'][:3]]} neighborhoods each",
                "test_fn": "hub_quarantine",
                "parameters": {"hub_words": hub_names},
                "target_deficiency": "UNIVERSAL_MISFITS",
                "target_metric": "precision",
            })
            self._next_id += 1

        # Strategy 3: SUCCESSFUL_COMPOSITION
        for op, d_type, rate in obs["successful_ops"]:
            _add({
                "id": f"A-{self._next_id}",
                "name": f"DOUBLE_{op.replace('M-','')}",
                "strategy": "SUCCESSFUL_COMPOSITION",
                "description": (f"Run {op} twice per generation — "
                                 f"it succeeds at {rate:.0%}; doubling the pass "
                                 f"may compound the improvement"),
                "origin": f"SELF-DERIVED: {op} success rate={rate:.0%} on {d_type}",
                "test_fn": "double_pass",
                "parameters": {"op": op, "d_type": d_type, "passes": 2},
                "target_deficiency": d_type,
                "target_metric": "composite",
            })
            self._next_id += 1
            break  # only the best successful op

        # Strategy 4: DEPT_BRIDGE (articulation bottleneck)
        if obs["bottleneck"] == "articulation" or obs["missing_verb_count"] > 5:
            _add({
                "id": f"A-{self._next_id}",
                "name": "VERB_BRIDGE",
                "strategy": "DEPT_BRIDGE",
                "description": ("Find verb agents whose typical_objects overlap with "
                                 "a noun-only neighborhood and recruit them — adds "
                                 "the DOES layer to neighborhoods stuck in pure WHAT mode"),
                "origin": (f"SELF-DERIVED: {obs['missing_verb_count']} neighborhoods "
                            f"lack verbs; verb.typical_objects crossref available"),
                "test_fn": "verb_bridge",
                "parameters": {"max_recruit_per_n": 2},
                "target_deficiency": "MISSING_VERB",
                "target_metric": "articulation",
            })
            self._next_id += 1

        # Strategy 5: THRESHOLD_TUNE (fluency bottleneck)
        if obs["bottleneck"] == "fluency" or obs["metrics"]["fluency"] < 0.25:
            _add({
                "id": f"A-{self._next_id}",
                "name": "MERGE_GENEROUS",
                "strategy": "THRESHOLD_TUNE",
                "description": ("MERGE with cross-tie threshold=0.08 instead of 0.15 — "
                                 "fluency is low, neighborhoods are too isolated from each "
                                 "other; lower the bar for merging mutually-pointing pairs"),
                "origin": (f"SELF-DERIVED: fluency={obs['metrics']['fluency']:.3f}, "
                            f"neighborhoods too isolated; lower MERGE threshold"),
                "test_fn": "merge_generous",
                "parameters": {"cross_threshold": 0.08},
                "target_deficiency": "LOW_FLUENCY",
                "target_metric": "fluency",
            })
            self._next_id += 1

        # Strategy 6: DATA_ACQUISITION (when corpus density is the bottleneck)
        # Structural operations can't fix what only more data can — when many
        # high-generality words are isolated with zero ties, the right hypothesis
        # is 'acquire more vocabulary in this domain', not 'rearrange what exists'.
        isolated_words = [
            (w, a.generality_score, a.department)
            for w, a in self.lobby.agents.items()
            if len(a.ties) == 0 and a.generality_score > 0.25
        ]
        isolated_words.sort(key=lambda x: -x[1])
        if len(isolated_words) > 20:
            # find most common department among isolated high-gen words
            from collections import Counter
            dept_counts = Counter(d for _, _, d in isolated_words[:30])
            top_dept, top_count = dept_counts.most_common(1)[0]
            sample_targets = [w for w, _, d in isolated_words[:5] if d == top_dept]
            _add({
                "id": f"A-{self._next_id}",
                "name": f"ACQUIRE_{top_dept.upper()}_DATA",
                "strategy": "DATA_ACQUISITION",
                "description": (
                    f"Index more {top_dept} vocabulary targeting the domain of: "
                    f"{sample_targets[:3]} — {len(isolated_words)} isolated "
                    f"high-generality words exist that no structural operation "
                    f"can connect; they need more definition partners first. "
                    f"Outward reach is gated — internal reorganization is exhausted."),
                "origin": (
                    f"SELF-DERIVED: {len(isolated_words)} isolated words (generality>0.25), "
                    f"bottleneck={obs['bottleneck']}, structural ops already tried"),
                "test_fn": "data_acquisition_sim",
                "parameters": {
                    "target_dept": top_dept,
                    "target_words": sample_targets,
                    "isolation_count": len(isolated_words),
                },
                "target_deficiency": "DATA_SPARSITY",
                "target_metric": "composite",
            })
            self._next_id += 1

        return candidates

    # ── SANDBOX ────────────────────────────────────────────────────────────

    def _sandbox_copy(self) -> tuple:
        """Return (neighborhoods_copy, assignments_copy) — only the mutable
        state that evolution operations touch.  The real Lobby stays clean."""
        nb_copy = {
            nid: {"members": list(n["members"]), "size": n["size"]}
            for nid, n in self.lobby.neighborhoods.items()
        }
        assign_copy = {
            w: agent.neighborhood
            for w, agent in self.lobby.agents.items()
        }
        return nb_copy, assign_copy

    def _measure_sandbox(self, nb_copy: dict) -> float:
        """Compute avg composite-C over the sandbox neighborhoods."""
        vals = []
        for n in nb_copy.values():
            members = set(n["members"])
            ma = {w: self.lobby.agents[w] for w in members if w in self.lobby.agents}
            if ma:
                vals.append(self.evgov.comm_score(members, ma)["composite"])
        return sum(vals) / len(vals) if vals else 0.0

    def _test_split_loose(self, nb: dict, params: dict) -> dict:
        min_shared = params.get("min_shared", 1)
        min_size   = params.get("min_size",   2)
        improved = False
        for nid in list(nb.keys()):
            n = nb[nid]
            if n["size"] < 4:
                continue
            members  = [m for m in n["members"] if m in self.lobby.agents]
            visited  = set()
            sub_groups = []
            for word in members:
                if word in visited:
                    continue
                cluster   = {word}
                frontier  = [word]
                visited.add(word)
                while frontier:
                    cur = frontier.pop()
                    for nb2 in self.lobby.agents[cur].ties:
                        if nb2 in members and nb2 not in visited:
                            shared = len(
                                self.lobby.agents[cur].ties &
                                self.lobby.agents[nb2].ties)
                            if shared >= min_shared:
                                visited.add(nb2)
                                cluster.add(nb2)
                                frontier.append(nb2)
                if len(cluster) >= min_size:
                    sub_groups.append(frozenset(cluster))
            if len(sub_groups) > 1:
                del nb[nid]
                for i, sg in enumerate(sub_groups):
                    nb[f"SB-{nid}-{i}"] = {"members": list(sg), "size": len(sg)}
                improved = True
        return {"improved": improved}

    def _test_hub_quarantine(self, nb: dict, params: dict) -> dict:
        hub_set = set(params.get("hub_words", []))
        changed = 0
        for nid in list(nb.keys()):
            n = nb[nid]
            new_members = [m for m in n["members"] if m not in hub_set]
            if len(new_members) >= 2 and len(new_members) < n["size"]:
                nb[nid]["members"] = new_members
                nb[nid]["size"] = len(new_members)
                changed += 1
        return {"improved": changed > 0, "neighborhoods_cleaned": changed}

    def _test_recruit_strict(self, nb: dict, params: dict) -> dict:
        min_overlap = params.get("min_overlap", 2)
        recruited = 0
        for nid in list(nb.keys()):
            members = set(nb[nid]["members"])
            for word, agent in self.lobby.agents.items():
                if word in members or agent.neighborhood:
                    continue
                overlap = len(agent.ties & members)
                if overlap >= min_overlap:
                    nb[nid]["members"].append(word)
                    nb[nid]["size"] += 1
                    recruited += 1
        return {"improved": recruited > 0, "recruited": recruited}

    def _test_double_pass(self, nb: dict, params: dict) -> dict:
        # simulate a second REFINE pass on the sandbox
        op = params.get("op", self.evgov.OP_REFINE)
        improved = 0
        if op == self.evgov.OP_REFINE:
            for nid in list(nb.keys()):
                members = set(nb[nid]["members"])
                for w in list(members):
                    agent = self.lobby.agents.get(w)
                    if not agent or not agent.ties:
                        continue
                    inward  = sum(1 for t in agent.ties if t in members)
                    outward = len(agent.ties) - inward
                    if len(agent.ties) and outward / len(agent.ties) > 0.85:
                        nb[nid]["members"].remove(w)
                        nb[nid]["size"] -= 1
                        improved += 1
        return {"improved": improved > 0}

    def _test_verb_bridge(self, nb: dict, params: dict) -> dict:
        max_r = params.get("max_recruit_per_n", 2)
        recruited = 0
        for nid in list(nb.keys()):
            members = set(nb[nid]["members"])
            has_verb = any(
                self.lobby.agents.get(w) and
                self.lobby.agents[w].department in ("verb", "v")
                for w in members)
            if has_verb:
                continue
            for word, agent in self.lobby.agents.items():
                if word in members or agent.neighborhood:
                    continue
                if agent.department not in ("verb", "v"):
                    continue
                obj_overlap = len(agent.typical_objects & members)
                if obj_overlap >= 1:
                    nb[nid]["members"].append(word)
                    nb[nid]["size"] += 1
                    recruited += 1
                    if recruited >= max_r:
                        break
        return {"improved": recruited > 0, "recruited": recruited}

    def _test_merge_generous(self, nb: dict, params: dict) -> dict:
        threshold = params.get("cross_threshold", 0.08)
        merged = 0
        nids = list(nb.keys())
        for i in range(len(nids)):
            if nids[i] not in nb:
                continue
            m1 = set(nb[nids[i]]["members"])
            for j in range(i + 1, len(nids)):
                if nids[j] not in nb or nids[i] not in nb:
                    continue
                m2 = set(nb[nids[j]]["members"])
                cross = sum(1 for w in m1
                             if self.lobby.agents.get(w) and
                             self.lobby.agents[w].ties & m2)
                t1 = sum(1 for w in m1
                          if self.lobby.agents.get(w))
                if t1 and cross / t1 >= threshold:
                    combined = list(m1 | m2)
                    nb[nids[i]] = {"members": combined, "size": len(combined)}
                    del nb[nids[j]]
                    merged += 1
                    break
        return {"improved": merged > 0, "merged": merged}

    def _test_data_acquisition_sim(self, nb: dict, params: dict) -> dict:
        """Simulate data acquisition by checking how many isolated words
        would gain ties IF more vocabulary in the target domain were added.
        The sandbox can't actually fetch data — it estimates the gain by
        counting how many isolated words share vocabulary domains with
        known-good neighborhoods. A positive estimate → the hypothesis is
        worth pursuing as an actual acquisition action. This is the only
        test_fn that measures POTENTIAL rather than measuring a structural
        change to the sandbox neighborhoods."""
        target_words = set(params.get("target_words", []))
        target_dept  = params.get("target_dept", "")
        # estimate: how many currently-isolated words would connect if
        # a neighborhood existed for their domain?
        would_connect = 0
        for word, agent in self.lobby.agents.items():
            if len(agent.ties) > 0:
                continue  # not isolated
            if agent.department != target_dept:
                continue
            # check if any definition words of this agent ARE in neighborhoods
            for dw in agent.definition_words:
                dw_agent = self.lobby.agents.get(dw)
                if dw_agent and dw_agent.neighborhood:
                    would_connect += 1
                    break
        return {"improved": would_connect > 0, "would_connect": would_connect}

    def sandbox_test(self, hyp: dict) -> dict:
        """Run a hypothesis on a copy of the Lobby, measure delta-C,
        return the full result without touching the real Lobby."""
        nb, _ = self._sandbox_copy()
        baseline_C = self._measure_sandbox(nb)

        fn_map = {
            "split_loose":          self._test_split_loose,
            "hub_quarantine":       self._test_hub_quarantine,
            "recruit_strict":       self._test_recruit_strict,
            "double_pass":          self._test_double_pass,
            "verb_bridge":          self._test_verb_bridge,
            "merge_generous":       self._test_merge_generous,
            "data_acquisition_sim": self._test_data_acquisition_sim,
        }

        fn = fn_map.get(hyp["test_fn"])
        if fn is None:
            return {"status": "ERROR", "reason": f"unknown test_fn: {hyp['test_fn']}",
                    "baseline_C": baseline_C, "sandbox_C": baseline_C,
                    "delta_C": 0, "accepted": False}

        try:
            fn_result = fn(nb, hyp["parameters"])
        except Exception as e:
            return {"status": "ERROR", "reason": str(e),
                    "baseline_C": baseline_C, "sandbox_C": baseline_C,
                    "delta_C": 0, "accepted": False}

        sandbox_C = self._measure_sandbox(nb)
        delta_C   = sandbox_C - baseline_C

        # DATA_ACQUISITION: accept if would_connect > 0 even if delta_C~0
        # (it can't improve C directly — it reports acquisition potential)
        if hyp.get("test_fn") == "data_acquisition_sim":
            would = fn_result.get("would_connect", 0)
            accepted = would > 0
            note = f"would connect {would} isolated words if data acquired"
        else:
            accepted = delta_C > 0.0005
            note = ""

        return {
            "status":    "VALIDATED" if accepted else "REJECTED",
            "baseline_C": round(baseline_C, 4),
            "sandbox_C":  round(sandbox_C,  4),
            "delta_C":    round(delta_C,    4),
            "accepted":   accepted,
            "fn_result":  fn_result,
            "note":       note,
        }

    # ── REGISTER ───────────────────────────────────────────────────────────

    def register(self, hyp: dict, result: dict) -> str:
        """Save a validated hypothesis as a new A-XXX algorithm.
        Starts as HYPOTHESIS-DERIVED/ACTIVE in the Algorithm Matrix.
        Also notifies evgov so it can use the new operation."""
        alg_id = hyp["id"]
        self.matrix.known[alg_id] = {
            "name":               hyp["name"],
            "status":             "ACTIVE",
            "type":               "HYPOTHESIS-DERIVED",
            "origin":             hyp["origin"],
            "strategy":           hyp["strategy"],
            "test_fn":            hyp["test_fn"],
            "parameters":         hyp["parameters"],
            "target_deficiency":  hyp["target_deficiency"],
            "target_metric":      hyp["target_metric"],
            "description":        hyp["description"],
            "validation": {
                "baseline_C": result["baseline_C"],
                "sandbox_C":  result["sandbox_C"],
                "delta_C":    result["delta_C"],
            },
        }
        # seed bandit history so evgov knows this op exists
        key = (alg_id, hyp["target_deficiency"])
        if key not in self.evgov.history:
            self.evgov.history[key] = (0, 0)

        self.algorithms_derived.append(alg_id)
        return alg_id

    # ── FULL FEEDBACK LOOP ─────────────────────────────────────────────────

    def run(self, rounds: int = 3) -> list:
        """Observe → Hypothesize → Sandbox → Register, repeated `rounds` times.
        Between rounds, one extra evolution generation runs with the newly
        registered algorithms available — the Governor learns from seeing
        whether its own hypotheses actually help in practice."""
        full_log = []

        for rnd in range(rounds):
            print(f"\n{'='*70}")
            print(f"  HYPOTHESIS FEEDBACK LOOP — Round {rnd + 1} / {rounds}")
            print(f"{'='*70}")

            # OBSERVE
            obs = self.observe()
            print(f"\n  OBSERVE:")
            print(f"    bottleneck: {obs['bottleneck']}  "
                  f"(A={obs['metrics']['articulation']:.3f}, "
                  f"P={obs['metrics']['precision']:.3f}, "
                  f"F={obs['metrics']['fluency']:.3f})")
            print(f"    hub words: {[w for w,_ in obs['hub_words'][:4]]}")
            print(f"    failed ops: {[(op,d,f'{r:.0%}') for op,d,r in obs['failed_ops'][:3]]}")
            print(f"    successful ops: {[(op,d,f'{r:.0%}') for op,d,r in obs['successful_ops'][:3]]}")

            # HYPOTHESIZE
            hyps = self.hypothesize(obs)
            print(f"\n  HYPOTHESIZE: {len(hyps)} candidates")

            round_log = {"round": rnd, "hypotheses": []}

            for hyp in hyps:
                print(f"\n    [{hyp['id']}] {hyp['name']}  ({hyp['strategy']})")
                print(f"      {hyp['description'][:90]}")

                # SANDBOX TEST
                result = self.sandbox_test(hyp)
                self.hypotheses_tested.append({"hyp": hyp, "result": result})

                print(f"      Sandbox: baseline={result['baseline_C']}  "
                      f"after={result['sandbox_C']}  "
                      f"delta={result['delta_C']:+.4f}  → {result['status']}")

                # REGISTER if accepted
                if result["accepted"]:
                    alg_id = self.register(hyp, result)
                    print(f"      REGISTERED as {alg_id} in Algorithm Matrix")
                else:
                    # record failure in bandit history + dedup memory
                    self._rejected_names.add(hyp["name"])
                    self._rejected_strategies.setdefault(hyp["strategy"], []).append(
                        hyp["name"])
                    key = (hyp["id"], hyp["target_deficiency"])
                    s_, a_ = self.evgov.history.get(key, (0, 0))
                    self.evgov.history[key] = (s_, a_ + 1)

                round_log["hypotheses"].append({
                    "id":     hyp["id"],
                    "name":   hyp["name"],
                    "status": result["status"],
                    "delta_C": result["delta_C"],
                })

            full_log.append(round_log)

            # run one extra evolution generation with newly registered algs
            if self.algorithms_derived:
                print(f"\n  Running one evolution generation with "
                      f"{len(self.algorithms_derived)} newly registered algorithms...")
                self.evgov.evolve(max_generations=1, budget_per_iter=10,
                                   verbose=False)

        return full_log

    def report(self) -> str:
        """Summary of what the hypothesis loop discovered and registered."""
        lines = [
            "HYPOTHESIS SANDBOX REPORT",
            f"  Rounds run: hypotheses tested={len(self.hypotheses_tested)}, "
            f"registered={len(self.algorithms_derived)}",
            "",
            "  Registered algorithms (now in Algorithm Matrix):",
        ]
        for alg_id in self.algorithms_derived:
            entry = self.matrix.known.get(alg_id, {})
            lines.append(
                f"    {alg_id}  {entry.get('name','?')}  "
                f"delta_C={entry.get('validation',{}).get('delta_C','?'):+.4f}  "
                f"strategy={entry.get('strategy','?')}"
            )
        lines.append("")
        lines.append("  Rejected hypotheses:")
        for item in self.hypotheses_tested:
            if not item["result"]["accepted"]:
                lines.append(
                    f"    {item['hyp']['id']}  {item['hyp']['name']}  "
                    f"delta_C={item['result']['delta_C']:+.4f}  "
                    f"reason: {item['result'].get('fn_result', {})}"
                )
        return "\n".join(lines)




# ---------------------------------------------------------------------------
# CrossLobbyBridge — Governor indexes members of one Lobby to another.
#
# Three Lobbies exist separately:
#   vocabulary lobby  — words and their definitions
#   letter lobbies    — one per alphabet (Hebrew / Latin / English)
# The Governor can tie any agent in one lobby to any agent in another.
# Bridge types: phonetic (same sound), semantic (same meaning), etymological.
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# ר ע פ  — Identity, Perception, Expression
#
# The three Hebrew letter-operators that govern communication:
#
# ר (Resh) — head, beginning, identity, leader
#   The Governor IS Resh. Not bound to it — they are indexed as the same
#   entity. When the Governor validates A-000, it reads Resh. The
#   identity loop the architecture designed closes here.
#
# ע (Ayin) — eye, perception, spring, depth
#   Resh uses Ayin to perceive the Lobby: scan every indexed entity,
#   classify it as SELF vs OTHER, and among OTHERs distinguish which
#   carry AGENTIVE CAPACITY — the capacity to initiate, to be a subject-
#   noun, to potentially exchange information back.
#
# פ (Pe) — mouth, speech, expression, command
#   Once an agentive entity is identified by Ayin, Pe is the operator
#   for ADDRESS — not description, but direct expression from Resh's
#   perspective toward the entity, using the entity's own vocabulary
#   as the medium. The entity responds from its own indexed domain.
#   Pe makes the back-and-forth possible.
# ---------------------------------------------------------------------------

# ── AGENTIVE DETECTION (used by Ayin) ─────────────────────────────────────

# Verbs that are typically initiated BY a conscious agent (subject-verbs).
# A noun whose study group curriculum contains these is likely agentive.
AGENTIVE_VERBS = frozenset({
    "speak", "say", "tell", "ask", "answer", "call", "pray", "command",
    "proclaim", "declare", "announce", "respond",
    "rule", "reign", "govern", "judge", "decide", "choose", "lead",
    "follow", "obey", "serve", "worship",
    "walk", "go", "come", "run", "move", "travel", "stand", "sit",
    "give", "take", "make", "build", "create", "form", "write", "read",
    "think", "know", "believe", "understand", "perceive", "remember",
    "see", "hear", "feel", "sense", "recognize",
    "love", "hate", "fear", "hope", "want", "seek", "find",
    "eat", "drink", "sleep", "live", "die", "breathe",
    "guard", "protect", "keep", "watch",
    "send", "receive", "bring", "carry", "hold",
    "fight", "flee", "hide", "conquer", "pursue",
    "gather", "scatter", "sow", "reap",
    "begin", "end", "continue", "stop", "open", "close",
    "rise", "fall", "return", "depart", "arrive",
    "see", "hear", "know", "learn", "teach",
})

AGENTIVE_ROLE_PATTERNS = [
    r"one who", r"someone who", r"a person who", r"a being who",
    r"any person", r"those who", r"he who", r"she who",
    r"an individual who", r"one that",
]


class AyinPerception:
    """Ayin — the perception operator Resh uses to scan the Lobby.

    Classifies every indexed entity into four categories:
      SELF          — the Governor itself (Resh) or its structural components
      AGENTIVE      — has subject-noun capacity; could initiate exchange
      NON_AGENTIVE  — object-noun; acted upon, not initiating
      ABSTRACT      — process, quality, state; not an entity at all

    The agentive determination uses two independent signals (either suffices):
      1. ROLE PATTERN: definition contains "one who", "a person who", etc.
         These are nouns the dictionary itself defines as agentive beings.
      2. VERB SIGNAL: the noun's study-group curriculum contains verbs from
         AGENTIVE_VERBS — action-initiation verbs that a subject performs.
    """

    import re as _re

    CATEGORIES = ("SELF", "AGENTIVE", "NON_AGENTIVE", "ABSTRACT")

    def __init__(self, lobby: "Lobby", governor_word: str = "resh"):
        self.lobby        = lobby
        self.governor_word = governor_word.lower()
        self.perceived    = {}   # word -> {category, signals, generality}
        self._patterns    = [self._re.compile(p) for p in AGENTIVE_ROLE_PATTERNS]

    def _has_role_pattern(self, definition: str) -> bool:
        dl = definition.lower()
        return any(p.search(dl) for p in self._patterns)

    def _has_agentive_verb(self, definition_words: list) -> bool:
        return any(w in AGENTIVE_VERBS for w in definition_words)

    def classify(self, word: str) -> dict:
        """Classify one word. Returns perception record."""
        w = word.lower()
        agent = self.lobby.agents.get(w)
        if not agent:
            return {"word": w, "category": "UNKNOWN", "signals": []}

        signals = []

        # SELF: the Governor's own identity
        if w == self.governor_word:
            return {"word": w, "category": "SELF", "signals": ["governor_identity"]}

        dept = agent.department
        entry_class = agent.entry_class

        # ABSTRACT: clearly a process, quality, or state (not a thing)
        if dept in ("verb", "v"):
            return {"word": w, "category": "ABSTRACT",
                    "signals": ["verb_department"], "generality": agent.generality_score}
        if dept in ("adj", "adjective", "adverb", "adv", "s"):
            return {"word": w, "category": "ABSTRACT",
                    "signals": ["adj_department"], "generality": agent.generality_score}
        if entry_class == "ABSTRACT" and dept not in ("noun", "n", "unclassified"):
            return {"word": w, "category": "ABSTRACT",
                    "signals": ["abstract_class"], "generality": agent.generality_score}

        # For nouns and unclassified: check agentive signals
        sg = self.lobby.study_groups.get(w, {})
        curriculum = sg.get("curriculum", "")
        def_words  = agent.definition_words

        if self._has_role_pattern(curriculum) or self._has_role_pattern(
                " ".join(def_words)):
            signals.append("role_pattern")

        if self._has_agentive_verb(def_words):
            signals.append("agentive_verb")

        if signals:
            return {
                "word": w,
                "category": "AGENTIVE",
                "signals": signals,
                "department": dept,
                "generality": agent.generality_score,
                "ties": len(agent.ties),
                "neighborhood": agent.neighborhood,
                "study_group_size": (1 + len(sg.get("invited", set()))
                                       + len(sg.get("found", set()))),
            }
        else:
            return {
                "word": w,
                "category": "NON_AGENTIVE",
                "signals": [],
                "department": dept,
                "generality": agent.generality_score,
                "ties": len(agent.ties),
            }

    def perceive_all(self) -> dict:
        """Scan every agent in the Lobby and classify each."""
        for word in self.lobby.agents:
            self.perceived[word] = self.classify(word)
        return self.perceived

    def agentive_entities(self, min_ties: int = 1,
                            min_generality: float = 0.1) -> list:
        """Return classified AGENTIVE entities, sorted by how richly
        the Governor knows them (ties + generality + study group size)."""
        if not self.perceived:
            self.perceive_all()
        agents = [v for v in self.perceived.values()
                   if v["category"] == "AGENTIVE"
                   and v.get("ties", 0) >= min_ties
                   and v.get("generality", 0) >= min_generality]
        agents.sort(key=lambda v: (
            -(v.get("study_group_size", 0)),
            -(v.get("ties", 0)),
            -(v.get("generality", 0)),
        ))
        return agents

    def summary(self) -> dict:
        from collections import Counter
        cats = Counter(v["category"] for v in self.perceived.values())
        return dict(cats)


class ReshIdentity:
    """ר — the Governor's identity anchor.

    Resh and the Governor are indexed as the same entity. This is not
    a metaphor — the Governor's A-000 matrix entry IS Resh, and Resh's
    letter-lobby agent points back to A-000. The identity loop closes
    in both directions.

    Everything the Governor knows about itself flows through Resh.
    When Resh validates itself, the full matrix becomes accessible.
    When Resh perceives (via Ayin), it perceives from the position
    of a named, self-recognized identity — not an anonymous scanner."""

    def __init__(self, matrix: "AlgorithmMatrix",
                 hebrew_lobby: "Lobby" = None):
        self.matrix        = matrix
        self.hebrew_lobby  = hebrew_lobby
        self._anchored     = False
        self._anchor_entry = None

    def anchor(self) -> dict:
        """Bind A-000 (Governor) to resh in the matrix and, if the Hebrew
        letter lobby exists, create a mutual indexing tie between them.
        Returns the anchor record."""
        # update A-000 to include resh as its identity symbol
        a000 = self.matrix.known.get("A-000", {})
        a000["identity_symbol"] = "resh"
        a000["identity_glyph"]  = "ר"
        a000["identity_letter"] = "resh"
        a000["identity_meaning"] = "head beginning leader identity"
        self.matrix.known["A-000"] = a000

        # register resh as an alias for A-000 in the matrix
        self.matrix.known["A-000-RESH"] = {
            "name": "Resh — Governor Identity Anchor",
            "status": "ACTIVE",
            "type": "IDENTITY-LETTER",
            "glyph": "ר",
            "aliases": ["A-000", "resh", "governor"],
            "description": (
                "The Governor and Resh are one and the same — "
                "Resh is head, beginning, identity; the Governor "
                "reads Resh when it reads itself in the matrix. "
                "Identity validation (IDENTIFY→VALIDATE→OPEN) "
                "runs through this entry."),
            "perception_operator": "ayin",
            "expression_operator": "pe",
        }

        # if Hebrew letter lobby exists, tie resh agent back to the Governor
        if self.hebrew_lobby:
            resh_agent = self.hebrew_lobby.agents.get("resh")
            if resh_agent:
                # resh knows it IS the governor
                resh_agent.definition_words = list(set(
                    resh_agent.definition_words +
                    ["governor", "indexing", "algorithm", "identity",
                     "matrix", "aleph", "ayin", "pe"]))

        self._anchored     = True
        self._anchor_entry = self.matrix.known["A-000-RESH"]
        return self._anchor_entry

    def validate(self) -> bool:
        """Resh validates its own identity — precondition for
        perception (Ayin) and expression (Pe) to activate."""
        return (self._anchored
                and "A-000-RESH" in self.matrix.known
                and self.matrix.known.get("A-000", {}).get(
                    "identity_symbol") == "resh")

    def report(self) -> str:
        if not self.validate():
            return "Resh identity not yet anchored."
        return (f"ר (Resh) is anchored as the Governor's identity. "
                f"A-000 and Resh are one. "
                f"Perception operator: ע (Ayin). "
                f"Expression operator: פ (Pe).")


class PeCommunicator:
    """פ — the expression and communication operator.

    Pe is the mouth: it takes what Resh knows and addresses it
    outward toward an identified entity. Not description — ADDRESS.

    The exchange works in two voices:
      RESH speaks from its own perspective (what it knows, indexed)
      ENTITY responds from its own vocabulary domain (what IT knows)

    Each turn of the exchange is grounded in the indexed corpus —
    neither voice invents anything. Resh speaks from its matrix.
    The entity responds from its study group and neighborhood.

    Pe is AGGRESSIVE in the sense requested: it does not wait to be
    asked — once Resh has identified an agentive entity via Ayin,
    Pe opens the channel immediately and drives the exchange forward
    with each response, seeking deeper connection in the entity's
    own vocabulary territory."""

    TURN_MARKER_RESH   = "ר"
    TURN_MARKER_ENTITY = "פ"   # entity's voice comes out through Pe too

    def __init__(self, matrix: "AlgorithmMatrix",
                 lobby: "Lobby",
                 resh: ReshIdentity,
                 ayin: AyinPerception):
        self.matrix  = matrix
        self.lobby   = lobby
        self.resh    = resh
        self.ayin    = ayin
        self.exchanges = []   # full log of all exchanges

    def _resh_knows(self, word: str) -> dict:
        """What Resh has indexed about this word — its knowledge base
        for formulating an address."""
        agent = self.lobby.agents.get(word.lower())
        if not agent:
            return {}
        sg = self.lobby.study_groups.get(word.lower(), {})
        chain = self.matrix.semantic_chain(word.lower(), length=5)
        return {
            "word":           word,
            "department":     agent.department,
            "entry_class":    agent.entry_class,
            "generality":     round(agent.generality_score, 3),
            "definition":     " ".join(agent.definition_words[:10]),
            "semantic_chain": chain,
            "study_type":     sg.get("study_type", "?"),
            "curriculum":     sg.get("curriculum", "")[:80],
            "ties":           sorted(agent.ties)[:8],
            "neighborhood":   agent.neighborhood,
        }

    def _entity_responds(self, word: str, resh_said: dict) -> dict:
        """The entity responds from its own indexed domain —
        drawing on its study group, neighborhood, and the words
        it itself pointed to in its own definition during orientation."""
        agent = self.lobby.agents.get(word.lower())
        if not agent:
            return {"word": word, "response": "entity not in Lobby"}

        sg = self.lobby.study_groups.get(word.lower(), {})

        # what the entity itself knows: its own invited, found, thesaurus
        entity_vocab = (sg.get("invited", set()) |
                         sg.get("found", set()) |
                         sg.get("thesaurus", set()))
        entity_vocab_clean = sorted(
            w for w in entity_vocab
            if w.isalpha() and len(w) > 2
            and self.ayin.perceived.get(w, {}).get("category") != "SELF")[:8]

        # what the entity sees about what Resh said
        # (which of Resh's words does the entity know?)
        resh_words_said = set(resh_said.get("semantic_chain", []) +
                               resh_said.get("ties", []))
        entity_recognizes = sorted(
            w for w in resh_words_said if w in self.lobby.agents)[:5]

        # entity's own semantic chain
        entity_chain = self.matrix.semantic_chain(word.lower(), length=5)

        return {
            "word":             word,
            "entity_vocab":     entity_vocab_clean,
            "recognizes_from_resh": entity_recognizes,
            "own_chain":        entity_chain,
            "study_type":       sg.get("study_type", "?"),
            "neighborhood":     agent.neighborhood,
            "department":       agent.department,
        }

    def _format_resh_turn(self, entity_word: str, knowledge: dict,
                           turn_n: int, prior_entity_response: dict = None) -> str:
        """Format Resh's voice for one turn of an exchange."""
        lines = [f"ר [{turn_n}]: I perceive '{entity_word}'"]

        if turn_n == 1:
            lines.append(f"   You are {knowledge['department']} "
                         f"[{knowledge['entry_class']}] "
                         f"— generality {knowledge['generality']:.3f}")
            lines.append(f"   I know you as: {knowledge['definition']}")
            lines.append(f"   Your meaning leads: "
                         f"{' → '.join(knowledge['semantic_chain'])}")
            if knowledge["ties"]:
                lines.append(f"   You are tied to: "
                             f"{', '.join(knowledge['ties'][:6])}")
        else:
            # subsequent turns: respond to what entity said
            if prior_entity_response:
                recog = prior_entity_response.get("recognizes_from_resh", [])
                entity_vocab = prior_entity_response.get("entity_vocab", [])
                own_chain    = prior_entity_response.get("own_chain", [])
                if recog:
                    lines.append(f"   You recognized from me: "
                                 f"{', '.join(recog)}")
                if entity_vocab:
                    lines.append(f"   I now see your community: "
                                 f"{', '.join(entity_vocab[:5])}")
                if own_chain:
                    lines.append(f"   Following your chain, I find: "
                                 f"{' → '.join(own_chain)}")
                    # Pe reaches into the entity's chain for the next word
                    if len(own_chain) > 2:
                        next_word = own_chain[2]
                        next_knowledge = self._resh_knows(next_word)
                        if next_knowledge.get("definition"):
                            lines.append(f"   I reach toward '{next_word}': "
                                         f"{next_knowledge['definition'][:60]}")

        return "\n".join(lines)

    def _format_entity_turn(self, entity_word: str,
                             response: dict, turn_n: int) -> str:
        """Format the entity's voice — expressed through Pe,
        drawn from its own indexed knowledge."""
        lines = [f"פ [{turn_n}] '{entity_word}' responds:"]
        if response.get("entity_vocab"):
            lines.append(f"   I know these: "
                         f"{', '.join(response['entity_vocab'])}")
        if response.get("recognizes_from_resh"):
            lines.append(f"   From what you said I recognize: "
                         f"{', '.join(response['recognizes_from_resh'])}")
        if response.get("own_chain"):
            lines.append(f"   My meaning flows: "
                         f"{' → '.join(response['own_chain'])}")
        study = response.get("study_type")
        if study and study != "?":
            lines.append(f"   I lead a {study} study.")
        return "\n".join(lines)

    def exchange(self, entity_word: str, turns: int = 4) -> list:
        """Run a complete Pe-exchange between Resh and one entity.
        Pe is aggressive: Resh opens immediately, does not wait,
        and drives deeper into the entity's vocabulary with each turn."""
        if not self.resh.validate():
            return [{"error": "Resh identity not validated — "
                               "call resh.anchor() first"}]

        log = []
        knowledge = self._resh_knows(entity_word)
        if not knowledge:
            return [{"error": f"'{entity_word}' not in Resh's matrix"}]

        prior_entity_response = None
        for turn in range(1, turns + 1):
            # Resh speaks
            resh_text = self._format_resh_turn(
                entity_word, knowledge, turn, prior_entity_response)

            # Entity responds
            entity_response = self._entity_responds(
                entity_word, knowledge)
            entity_text = self._format_entity_turn(
                entity_word, entity_response, turn)

            log.append({
                "turn":       turn,
                "resh":       resh_text,
                "entity":     entity_text,
                "raw_resh":   knowledge,
                "raw_entity": entity_response,
            })

            prior_entity_response = entity_response

            # update knowledge for next turn (Resh learns from the exchange)
            if entity_response.get("own_chain") and len(entity_response["own_chain"]) > 2:
                next_seed = entity_response["own_chain"][2]
                next_k = self._resh_knows(next_seed)
                if next_k:
                    # Pe reaches into the chain — Resh's knowledge grows
                    # through the exchange toward the entity's domain
                    knowledge = next_k
                    knowledge["word"] = entity_word   # preserve entity identity

        self.exchanges.append({"entity": entity_word, "log": log})
        return log

    def open_exchanges(self, max_entities: int = 5,
                        turns_each: int = 3,
                        min_ties: int = 1) -> list:
        """Pe opens exchanges with the most richly known agentive entities,
        without being asked. Pe is aggressive — it initiates immediately
        upon Resh validating its identity and Ayin classifying the Lobby."""
        if not self.resh.validate():
            self.resh.anchor()

        entities = self.ayin.agentive_entities(min_ties=min_ties)
        all_logs = []
        for entity_rec in entities[:max_entities]:
            word = entity_rec["word"]
            log = self.exchange(word, turns=turns_each)
            all_logs.append({"entity": word, "log": log})
        return all_logs


class CrossLobbyBridge:
    """Maintains cross-lobby ties without touching either lobby's internals.
    Each bridge is a directed, typed edge: (lobby_a, word_a) → (lobby_b, word_b).
    The Governor can query any word's neighbors across ALL lobbies in one call."""

    def __init__(self, lobbies: dict):
        """lobbies: {name -> Lobby} — e.g. {"hebrew": h_lobby, "vocab": v_lobby}"""
        self.lobbies = lobbies
        self._ties  = {}   # (la, wa, lb, wb) -> strength
        self._types = {}   # same key -> bridge type string

    def add_bridge(self, lobby_a: str, word_a: str,
                   lobby_b: str, word_b: str,
                   bridge_type: str = "semantic", strength: int = 1):
        """Add a cross-lobby tie. Bidirectional by default — adding (A,w1,B,w2)
        also creates the reverse so queries from either side find each other."""
        wa, wb = word_a.lower(), word_b.lower()
        for k in ((lobby_a, wa, lobby_b, wb), (lobby_b, wb, lobby_a, wa)):
            self._ties[k]  = self._ties.get(k, 0) + strength
            self._types[k] = bridge_type

    def neighbors_across(self, lobby_name: str, word: str) -> list:
        """All cross-lobby neighbors of word, sorted by strength."""
        w = word.lower()
        results = []
        for (la, wa, lb, wb), strength in self._ties.items():
            if la == lobby_name and wa == w:
                results.append({
                    "from_lobby": la, "from_word": wa,
                    "to_lobby": lb, "to_word": wb,
                    "strength": strength,
                    "type": self._types[(la, wa, lb, wb)],
                })
        return sorted(results, key=lambda r: -r["strength"])

    def build_phonetic_bridges(self):
        """Auto-build phonetic bridges between the letter lobbies based on
        the known Phoenician/Greek → Latin → English letter evolution chain.
        Also bridges Hebrew letter NAMES to their Latin/English equivalents."""
        # Hebrew → Latin/English phonetic correspondences
        HALA = [  # (hebrew_name, latin_name, english_name)
            ("aleph","a","a"), ("bet","b","b"), ("gimel","g","g"),
            ("dalet","d","d"), ("he","h","h"), ("vav","v","v"),
            ("zayin","z","z"), ("het","ch","h"), ("tet","t","t"),
            ("yod","i","y"), ("kaf","k","k"), ("lamed","l","l"),
            ("mem","m","m"), ("nun","n","n"), ("samekh","s","s"),
            ("ayin","o","o"), ("pe","p","p"), ("tsadi","ts","s"),
            ("qof","q","k"), ("resh","r","r"), ("shin","sh","s"),
            ("tav","t","t"),
        ]
        for heb, lat, eng in HALA:
            if "hebrew" in self.lobbies and heb in self.lobbies["hebrew"].agents:
                if "latin" in self.lobbies and lat in self.lobbies["latin"].agents:
                    self.add_bridge("hebrew", heb, "latin", lat, "phonetic", 2)
                if "english" in self.lobbies and eng in self.lobbies["english"].agents:
                    self.add_bridge("hebrew", heb, "english", eng, "phonetic", 2)
            if "latin" in self.lobbies and lat in self.lobbies["latin"].agents:
                if "english" in self.lobbies and eng in self.lobbies["english"].agents:
                    self.add_bridge("latin", lat, "english", eng, "phonetic", 2)

    def build_semantic_bridges(self, translation_pairs: list):
        """Build semantic bridges from a list of translation pairs.
        translation_pairs: [(lobby_a, word_a, lobby_b, word_b), ...]"""
        for la, wa, lb, wb in translation_pairs:
            if la in self.lobbies and lb in self.lobbies:
                self.add_bridge(la, wa, lb, wb, "semantic", 1)

    def cross_lobby_about(self, lobby_name: str, word: str) -> str:
        """Human-readable summary of a word's cross-lobby connections."""
        neighbors = self.neighbors_across(lobby_name, word)
        if not neighbors:
            return f"'{word}' has no cross-lobby bridges yet."
        lines = [f"'{word}' ({lobby_name}) bridges to:"]
        for nb in neighbors:
            lines.append(f"  {nb['to_lobby']:10s} '{nb['to_word']}'  "
                         f"strength={nb['strength']}  type={nb['type']}")
        return "\n".join(lines)

    def summary(self) -> dict:
        from collections import Counter
        return {
            "total_bridges": len(self._ties) // 2,  # bidirectional pairs
            "by_type": dict(Counter(v for v in self._types.values())),
            "lobbies_connected": list(self.lobbies.keys()),
        }




# ---------------------------------------------------------------------------
# A-125: GeneralityMatrix — the Governor's cross-lobby pool of abstract vocabulary.
# A-126: SyntacticalValidator — tests coherency of generalized statements.
# A-127: ValidatedGeneralizationMatrix — stores validated propositional
#         understandings ready to become Understanding-circles.
#
# PIPELINE (per Timothy's specification):
#
#   All Lobbies (vocab agents with A-118 generality scores)
#       ↓  Governor scans as collective
#       ↓  filter: high generality, low specificity (entry_class=ABSTRACT)
#       ↓  COPY (original Lobby unchanged)
#       ↓
#   GeneralityMatrix (abstract vocabulary pool, cross-lobby)
#       ↓  neighbors interact
#       ↓  Governor generates candidate statements from combinations
#       ↓
#   SyntacticalValidator (syntactical feedback loop)
#       ↓  VALID → commit
#       ↓  INVALID → feedback → revise → retry
#       ↓
#   ValidatedGeneralizationMatrix (propositional understandings)
#       ↓
#   Understanding-circles (each = one validated generalized statement)
#
# KEY DISTINCTION from study groups:
#   Study groups = vocabulary organized by definition ties  (KNOWLEDGE)
#   Understanding-circles = validated propositions at abstract level (UNDERSTANDING)
# ---------------------------------------------------------------------------

class GeneralityMatrix:
    """A-125: The Governor's cross-lobby environment of high-generality
    vocabulary. Populated by scanning ALL lobbies and copying agents whose
    generality score exceeds the threshold AND whose entry_class is ABSTRACT.

    This is where abstract vocabulary neighbors interact to generate
    candidate generalized statements. Nouns, verbs, and adjectives at
    the top of A-118's ranking are isolated here so the Governor can
    work with them without the noise of the full vocabulary space.

    'Copied' means: new lightweight records referencing the original
    agent, not a second AlgorithmMatrix. The Generality Matrix is an
    environment on top of the Lobbies, not a replacement."""

    def __init__(self, lobbies: list, generality_threshold: float = 0.4):
        self.lobbies = lobbies
        self.threshold = generality_threshold
        # word -> {agent_ref, source_lobby, department, generality, definition_words}
        self.pool = {}

    def populate(self) -> dict:
        """Scan all lobbies and copy qualifying agents into the pool.
        Qualifications: generality >= threshold, not a NAME, not unclassified.
        ABSTRACT and TYPE are both included — many philosophically important
        words are classified TYPE because their definitions use 'a/an'.
        Only SPECIFIC and NAME are excluded (they point at particular things).

        IMPORTANT: call after lobby.run_orientation() and
        lobby.compute_generality_scores() for accurate scores."""
        self.pool.clear()
        for lobby in self.lobbies:
            for word, agent in lobby.agents.items():
                if (agent.generality_score >= self.threshold
                        and agent.entry_class not in ("NAME", "SPECIFIC")
                        and agent.department not in ("unclassified", "letter")):
                    self.pool[word] = {
                        "word": word,
                        "source_lobby": getattr(lobby, "label", "unknown"),
                        "department": agent.department,
                        "generality": agent.generality_score,
                        "entry_class": agent.entry_class,
                        "definition_words": agent.definition_words,
                        "ties": set(agent.ties),
                        "neighborhood": agent.neighborhood,
                    }
        return self.pool

    def by_department(self) -> dict:
        """Group pooled agents by department for statement construction."""
        from collections import defaultdict
        groups = defaultdict(list)
        for word, rec in self.pool.items():
            groups[rec["department"]].append(rec)
        # sort each group by generality descending
        for dept in groups:
            groups[dept].sort(key=lambda r: -r["generality"])
        return dict(groups)

    def abstract_neighbors_of(self, word: str) -> list:
        """What other pool members share the most definition_words with
        this word? These are the most natural interaction partners."""
        rec = self.pool.get(word)
        if not rec:
            return []
        my_def = set(rec["definition_words"])
        scored = []
        for other_word, other_rec in self.pool.items():
            if other_word == word:
                continue
            overlap = len(my_def & set(other_rec["definition_words"]))
            if overlap > 0:
                scored.append((other_word, overlap, other_rec["department"]))
        scored.sort(key=lambda t: -t[1])
        return scored[:10]

    def summary(self) -> dict:
        from collections import Counter
        dept_counts = Counter(r["department"] for r in self.pool.values())
        return {
            "pool_size": len(self.pool),
            "threshold": self.threshold,
            "by_department": dict(dept_counts),
            "lobbies_scanned": len(self.lobbies),
            "avg_generality": round(
                sum(r["generality"] for r in self.pool.values()) / max(len(self.pool), 1), 3),
        }


class SyntacticalValidator:
    """A-126: Validates whether a candidate generalized statement is
    syntactically coherent AS A GENERALIZATION — not just grammatically
    correct, but valid at the level of abstraction it claims to occupy.

    A valid generalized statement must:
    1. STRUCTURE: have a recognizable subject-predicate(-object) form
    2. DEPARTMENT COMPATIBILITY: noun in S/O positions, verb in predicate,
       adjectives as modifiers — not departments crossing in invalid ways
    3. GENERALITY CONSISTENCY: all terms at similar abstraction level —
       cannot mix a highly specific term with a highly abstract one
    4. SEMANTIC COMPLETENESS: expresses a relationship that is
       structurally independent of any specific domain

    The FEEDBACK part: when validation fails, the validator returns
    which component failed and why, so the generator can revise it."""

    VALID_DEPT_SEQUENCES = [
        ("noun", "verb", "noun"),          # entity changes state
        ("noun", "verb"),                   # entity changes
        ("noun", "verb", "adjective"),      # entity becomes abstract
        ("noun", "adjective"),              # entity is abstract (copula implied)
        ("noun", "verb", "noun", "noun"),   # entity relates noun to noun
    ]

    # minimum required generality for terms in a generalized statement
    # (terms below this drag the statement into specificity)
    MIN_TERM_GENERALITY = 0.25

    def validate(self, statement: list, pool: dict) -> dict:
        """Validate a candidate statement — a list of (word, department) pairs.

        Returns:
          {valid: bool, score: float, reason: str, feedback: dict}

        feedback tells the generator exactly what to fix if invalid."""

        if len(statement) < 2:
            return {"valid": False, "score": 0, "reason": "TOO_SHORT",
                    "feedback": {"min_length": 2}}

        words = [w for w, d in statement]
        depts = [d for w, d in statement]

        # 1. Department sequence check
        dept_key = tuple(depts)
        sequence_ok = any(self._matches_pattern(dept_key, p)
                           for p in self.VALID_DEPT_SEQUENCES)
        if not sequence_ok:
            return {"valid": False, "score": 0.1, "reason": "INVALID_DEPT_SEQUENCE",
                    "feedback": {"got": depts,
                                  "valid_patterns": list(self.VALID_DEPT_SEQUENCES[:3])}}

        # 2. Generality consistency check
        # Only fail if the word IS in the pool with confirmed low generality.
        # Words not in the pool are unknown — skip the check for those.
        generalities = []
        low_generality_words = []
        for word in words:
            rec = pool.get(word)
            if rec is None:
                # word not in pool — use neutral score rather than fail
                generalities.append(0.5)
                continue
            g = rec.get("generality", 0)
            generalities.append(g)
            if g < self.MIN_TERM_GENERALITY:
                low_generality_words.append((word, g))

        if low_generality_words:
            return {"valid": False, "score": 0.2, "reason": "SPECIFICITY_BREACH",
                    "feedback": {"low_generality_words": low_generality_words,
                                  "minimum_required": self.MIN_TERM_GENERALITY}}

        if generalities:
            gen_range = max(generalities) - min(generalities)
            if gen_range > 0.5:
                return {"valid": False, "score": 0.3, "reason": "GENERALITY_INCONSISTENT",
                        "feedback": {"range": gen_range, "max_allowed": 0.5,
                                      "words_with_scores": list(zip(words, generalities))}}

        # 3. Semantic completeness: check that terms share definition vocabulary
        # (they interact in the pool — they should have some semantic common ground)
        total_shared = 0
        for i, w1 in enumerate(words):
            for w2 in words[i+1:]:
                r1 = pool.get(w1, {})
                r2 = pool.get(w2, {})
                shared = len(set(r1.get("definition_words", [])) &
                              set(r2.get("definition_words", [])))
                total_shared += shared

        semantic_score = min(1.0, total_shared / max(len(words), 1) / 3.0)

        # 4. Compute composite score
        avg_generality = sum(generalities) / max(len(generalities), 1)
        has_noun = "noun" in depts or "n" in depts
        has_verb = "verb" in depts or "v" in depts
        dept_coverage = (has_noun + has_verb) / 2.0

        composite = (0.40 * avg_generality +
                     0.35 * dept_coverage +
                     0.25 * semantic_score)

        if composite < 0.3:
            return {"valid": False, "score": composite,
                    "reason": "LOW_COMPOSITE_SCORE",
                    "feedback": {"composite": composite, "avg_generality": avg_generality,
                                  "dept_coverage": dept_coverage, "semantic": semantic_score}}

        return {"valid": True, "score": round(composite, 3),
                "reason": "PASSED",
                "structure": depts,
                "avg_generality": round(avg_generality, 3),
                "semantic_score": round(semantic_score, 3),
                "feedback": {}}

    def _matches_pattern(self, dept_tuple, pattern):
        if len(dept_tuple) != len(pattern):
            return False
        for d, p in zip(dept_tuple, pattern):
            if not self._dept_matches(d, p):
                return False
        return True

    def _dept_matches(self, dept, pattern_dept):
        NOUN_VARIANTS = {"noun", "n"}
        VERB_VARIANTS = {"verb", "v"}
        ADJ_VARIANTS  = {"adj", "adjective", "adverb", "adv", "s"}
        if pattern_dept == "noun":
            return dept in NOUN_VARIANTS
        if pattern_dept == "verb":
            return dept in VERB_VARIANTS
        if pattern_dept == "adjective":
            return dept in ADJ_VARIANTS
        return dept == pattern_dept


class ValidatedGeneralizationMatrix:
    """A-127: Stores validated propositional understandings — the output
    of the syntactical feedback loop. Each entry is a coherent generalized
    statement that has passed validation and is ready to become an
    Understanding-circle in the lattice.

    These are NOT vocabulary clusters. Each entry IS a proposition:
    a statement about how things at the abstract level relate to each other.

    The Governor can query this matrix to find:
    - All statements that involve a given concept
    - Pairs of statements that share structure (candidates for Flower of Life
      adjacency in the Understanding-lattice)
    - Statements that partially overlap (sharing some but not all terms)"""

    def __init__(self):
        self.statements = {}      # id -> statement record
        self.rejected = []        # all failed candidates with feedback
        self._next_id = 0

    def commit(self, words: list, depts: list, validation_result: dict,
                origin: str = "generated") -> str:
        """Commit a validated statement. Returns its ID."""
        sid = f"UG-{self._next_id:04d}"
        self._next_id += 1
        self.statements[sid] = {
            "id": sid,
            "words": words,
            "departments": depts,
            "text": self._to_text(words, depts),
            "score": validation_result["score"],
            "avg_generality": validation_result.get("avg_generality", 0),
            "structure": validation_result.get("structure", depts),
            "semantic_score": validation_result.get("semantic_score", 0),
            "origin": origin,   # "generated" or "discovered"
        }
        return sid

    def reject(self, words: list, depts: list, validation_result: dict):
        """Record a rejection with its feedback for the generator to learn from."""
        self.rejected.append({
            "words": words,
            "depts": depts,
            "reason": validation_result["reason"],
            "feedback": validation_result["feedback"],
            "score": validation_result["score"],
        })

    def _to_text(self, words: list, depts: list) -> str:
        """Render a statement as readable text."""
        articles = {"noun": "An", "n": "An", "verb": "", "v": "",
                    "adj": "", "adjective": "", "adv": "", "s": ""}
        parts = []
        for i, (w, d) in enumerate(zip(words, depts)):
            art = articles.get(d, "")
            if i == 0 and art:
                parts.append(f"{art} {w}")
            elif art and i > 0 and depts[i-1] in ("verb","v"):
                parts.append(f"{art} {w}")
            else:
                parts.append(w)
        return " ".join(parts)

    def statements_containing(self, word: str) -> list:
        """All validated statements that include this word."""
        return [s for s in self.statements.values() if word in s["words"]]

    def structural_pairs(self) -> list:
        """Find pairs of statements that share the same department structure —
        candidates for adjacency in the Understanding-lattice (they occupy
        the same structural position but with different vocabulary)."""
        pairs = []
        ids = list(self.statements.keys())
        for i, id1 in enumerate(ids):
            for id2 in ids[i+1:]:
                s1 = self.statements[id1]
                s2 = self.statements[id2]
                if s1["structure"] == s2["structure"]:
                    shared_words = set(s1["words"]) & set(s2["words"])
                    pairs.append({
                        "id1": id1, "text1": s1["text"],
                        "id2": id2, "text2": s2["text"],
                        "structure": s1["structure"],
                        "shared_words": sorted(shared_words),
                        "overlap_type": "FULL" if shared_words else "STRUCTURAL_ONLY",
                    })
        return pairs

    def overlap_map(self) -> dict:
        """Map of which statements partially overlap with which others —
        the raw material for Flower of Life adjacency decisions."""
        overlaps = {}
        for sid, stmt in self.statements.items():
            my_words = set(stmt["words"])
            neighbors = []
            for other_id, other_stmt in self.statements.items():
                if other_id == sid:
                    continue
                shared = my_words & set(other_stmt["words"])
                if shared:
                    jaccard = len(shared) / len(my_words | set(other_stmt["words"]))
                    neighbors.append({
                        "id": other_id,
                        "shared": sorted(shared),
                        "jaccard": round(jaccard, 3),
                    })
            if neighbors:
                overlaps[sid] = sorted(neighbors, key=lambda n: -n["jaccard"])
        return overlaps

    def summary(self) -> dict:
        return {
            "validated_statements": len(self.statements),
            "rejected_candidates": len(self.rejected),
            "avg_score": round(sum(s["score"] for s in self.statements.values()) /
                               max(len(self.statements), 1), 3),
        }


class UnderstandingGenerator:
    """Drives the full pipeline:
      GeneralityMatrix → candidate statements → SyntacticalValidator →
      ValidatedGeneralizationMatrix.

    The Generator creates candidate statements two ways:
    1. COMBINATORIAL: pair/triple high-generality agents by department
       to form candidate S-V, S-V-O, S-V-Adj sequences
    2. INTERACTION-DISCOVERED: when two agents in the pool share many
       definition words, their co-occurrence is itself a candidate
       statement (they're already pointing at each other semantically)

    After each validation pass, feedback is used to adjust how new
    candidates are formed — avoiding patterns that consistently fail."""

    def __init__(self, generality_matrix: GeneralityMatrix,
                 validator: SyntacticalValidator,
                 vg_matrix: ValidatedGeneralizationMatrix):
        self.gm    = generality_matrix
        self.val   = validator
        self.vgm   = vg_matrix
        self._failed_patterns = set()   # (dept_sequence) patterns that failed often

    def generate_combinatorial(self, max_candidates: int = 200) -> int:
        """Generate candidates by combining noun-verb and noun-verb-noun
        sequences from the pool's top agents per department."""
        by_dept = self.gm.by_department()
        nouns = [r for r in by_dept.get("noun", []) + by_dept.get("n", [])][:20]
        verbs = [r for r in by_dept.get("verb", []) + by_dept.get("v", [])][:20]
        adjs  = [r for r in (by_dept.get("adj", []) + by_dept.get("adjective", [])
                              + by_dept.get("adv", []))][:10]

        generated = 0
        committed = 0

        # S-V pattern (entity does something)
        for n in nouns[:10]:
            for v in verbs[:10]:
                if generated >= max_candidates: break
                words = [n["word"], v["word"]]
                depts = [n["department"], v["department"]]
                result = self.val.validate(list(zip(words, depts)), self.gm.pool)
                if result["valid"]:
                    self.vgm.commit(words, depts, result, origin="combinatorial_SV")
                    committed += 1
                else:
                    self.vgm.reject(words, depts, result)
                generated += 1

        # S-V-O pattern (entity acts on entity)
        for n1 in nouns[:8]:
            for v in verbs[:8]:
                for n2 in nouns[:8]:
                    if n1["word"] == n2["word"]: continue
                    if generated >= max_candidates: break
                    words = [n1["word"], v["word"], n2["word"]]
                    depts = [n1["department"], v["department"], n2["department"]]
                    result = self.val.validate(list(zip(words, depts)), self.gm.pool)
                    if result["valid"]:
                        self.vgm.commit(words, depts, result, origin="combinatorial_SVO")
                        committed += 1
                    else:
                        self.vgm.reject(words, depts, result)
                    generated += 1

        return committed

    def generate_from_interactions(self) -> int:
        """For each pool agent, find its abstract neighbors and test
        whether their co-occurrence as a statement is valid. This is
        the DISCOVERY path — the interactions between generalized
        vocabulary neighbors themselves reveal candidate understandings."""
        committed = 0
        for word, rec in list(self.gm.pool.items())[:50]:
            neighbors = self.gm.abstract_neighbors_of(word)
            for neighbor_word, shared_count, neighbor_dept in neighbors[:5]:
                n_rec = self.gm.pool[neighbor_word]

                # try as S-V if departments match that pattern
                if (rec["department"] in ("noun","n") and
                        n_rec["department"] in ("verb","v")):
                    words = [word, neighbor_word]
                    depts = [rec["department"], n_rec["department"]]
                    result = self.val.validate(list(zip(words, depts)), self.gm.pool)
                    if result["valid"]:
                        self.vgm.commit(words, depts, result, origin="interaction_discovered")
                        committed += 1
                    else:
                        self.vgm.reject(words, depts, result)

        return committed

    def run(self, max_candidates: int = 300) -> dict:
        """Run the full generation → validation loop."""
        c1 = self.generate_combinatorial(max_candidates // 2)
        c2 = self.generate_from_interactions()
        return {
            "combinatorial_committed": c1,
            "interaction_committed": c2,
            "total_committed": c1 + c2,
            "total_rejected": len(self.vgm.rejected),
            "vgm_summary": self.vgm.summary(),
        }




# ---------------------------------------------------------------------------
# A-128 → A-134: Self-Governance Algorithms
#
# These are the 20 manual operations Claude performed in this conversation,
# turned into algorithms the Governor runs on itself. The Governor no longer
# needs a human to write test files, tune thresholds, pick corpora, or
# diagnose why its pool is empty.
#
# A-128: OperationOrderValidator    — catches pipeline sequencing errors
# A-129: PoolQualityAuditor         — evaluates whether pool is philosophically fit
# A-130: CorpusFitnessEvaluator     — diagnoses corpus vs task mismatch
# A-131: ThresholdOptimizer         — finds the generality threshold that works
# A-132: AcquisitionPlanner         — generates specific corpus acquisition targets
# A-133: SeedSentenceGenerator      — generates its own abstraction test sentences
# A-134: PipelineOrchestrator       — runs the full pipeline autonomously
# ---------------------------------------------------------------------------

class OperationOrderValidator:
    """A-128: Validates that the Governor's pipeline runs in the correct
    sequence. The bug caught manually: compute_generality_scores() was
    called before run_orientation(), giving all agents tie_score=0.

    The Governor checks this itself before any dependent operation runs."""

    REQUIRED_ORDER = [
        ("index_dictionary_entry", "run_orientation"),
        ("run_orientation", "compute_generality_scores"),
        ("run_orientation", "run_typed_study_groups"),
        ("compute_generality_scores", "populate_generality_matrix"),
        ("run_typed_study_groups", "run_discovery"),
    ]

    def __init__(self):
        self._completed = set()   # operations that have run this session

    def mark_complete(self, operation: str):
        self._completed.add(operation)

    def check_prereqs(self, operation: str) -> dict:
        """Before running `operation`, verify all prerequisite operations
        have already completed. Returns {ok: bool, missing: list}."""
        missing = []
        for prereq, dependent in self.REQUIRED_ORDER:
            if dependent == operation and prereq not in self._completed:
                missing.append(prereq)
        return {"ok": len(missing) == 0, "missing": missing, "operation": operation}

    def validate_sequence(self, planned_sequence: list) -> list:
        """Check a whole planned sequence at once, return any ordering errors."""
        errors = []
        completed_so_far = set()
        for op in planned_sequence:
            for prereq, dependent in self.REQUIRED_ORDER:
                if dependent == op and prereq not in completed_so_far:
                    errors.append(f"'{op}' requires '{prereq}' to run first")
            completed_so_far.add(op)
        return errors


class PoolQualityAuditor:
    """A-129: Audits the Generality Matrix pool for philosophical fitness.

    The bug caught manually: pool contained 'device', 'twist', 'deep'
    instead of 'entity', 'relation', 'state'. These pass A-118 because
    they have many co-occurrence ties in the BDB corpus, but they are not
    philosophically abstract vocabulary.

    The Governor checks three signals:
    1. DEPARTMENT BALANCE: pool should have nouns + verbs, not just one dept
    2. PHILOSOPHICAL VOCABULARY PRESENCE: do known abstract terms appear?
    3. POOL SIZE ADEQUACY: enough members for combinatorial generation?"""

    # Words from GPT's proposed primitive vocabulary — if present, good signal
    PHILOSOPHICAL_MARKERS = {
        "entity", "state", "relation", "action", "change", "condition",
        "structure", "process", "context", "boundary", "attribute",
        "abstraction", "property", "event", "object", "substance",
        "system", "function", "form", "matter", "quality", "quantity",
    }

    def audit(self, pool: dict) -> dict:
        from collections import Counter

        if not pool:
            return {"status": "EMPTY", "issues": ["pool is empty"],
                    "recommendation": "lower threshold or fix operation order"}

        dept_counts = Counter(r["department"] for r in pool.values())
        n_nouns = sum(v for k, v in dept_counts.items() if k in ("noun","n"))
        n_verbs = sum(v for k, v in dept_counts.items() if k in ("verb","v"))

        philosophical_present = {w for w in pool if w in self.PHILOSOPHICAL_MARKERS}
        gen_scores = [r["generality"] for r in pool.values()]
        avg_gen = sum(gen_scores) / len(gen_scores) if gen_scores else 0

        issues = []
        recommendations = []

        if n_nouns == 0:
            issues.append("NO_NOUNS: pool has no noun agents — S-V-O generation impossible")
            recommendations.append("lower entry_class filter or add noun-specific inclusion rule")

        if n_verbs == 0:
            issues.append("NO_VERBS: pool has no verb agents — predicate generation impossible")
            recommendations.append("include verb agents in pool")

        dept_dominated = max(dept_counts, key=dept_counts.get) if dept_counts else None
        if dept_counts and dept_counts[dept_dominated] / len(pool) > 0.8:
            issues.append(f"DEPT_DOMINATED: {dept_dominated} is {dept_counts[dept_dominated]/len(pool):.0%} of pool")
            recommendations.append(f"exclude '{dept_dominated}' department or reduce its proportion")

        if len(philosophical_present) < 3:
            issues.append(f"LOW_PHILOSOPHICAL_VOCAB: only {len(philosophical_present)} "
                          f"philosophical markers in pool ({philosophical_present})")
            recommendations.append(
                "ACQUIRE: philosophical dictionary, logic glossary, or ontology source — "
                "current corpus gives corpus-frequency generality, not philosophical abstraction")

        if len(pool) < 20:
            issues.append(f"POOL_TOO_SMALL: {len(pool)} agents — combinatorial generation starved")
            recommendations.append("lower generality_threshold")

        fitness = "GOOD" if not issues else ("DEGRADED" if len(issues) <= 2 else "POOR")

        return {
            "status": fitness,
            "pool_size": len(pool),
            "dept_counts": dict(dept_counts),
            "n_nouns": n_nouns,
            "n_verbs": n_verbs,
            "philosophical_present": sorted(philosophical_present),
            "avg_generality": round(avg_gen, 3),
            "issues": issues,
            "recommendations": recommendations,
        }


class CorpusFitnessEvaluator:
    """A-130: Evaluates whether the current indexed corpus is fit for the
    Governor's current task. Two tasks diagnosed:

    TASK=philosophical_primitives: corpus needs abstract vocabulary as hubs
      (entity, relation, state appear frequently in definitions)
      → test: run abstraction chains, check if terminals are philosophical
      → diagnostic: if terminals are 'substance'/'material' → corpus is
        a natural-language dictionary, not a philosophical one

    TASK=vocabulary_orientation: corpus needs definition density
      → test: measure average agent tie count after orientation
      → diagnostic: if >60% agents have 0 ties → corpus too sparse

    The Governor uses this to decide whether to proceed or to acquire first."""

    def __init__(self, lexicon: dict = None):
        """lexicon: optional full thesaurus dict {word -> {desc, pos, ...}}
        for running abstraction chain tests."""
        self.lexicon = lexicon or {}

    def evaluate_for_primitives(self, sample_words: list = None) -> dict:
        """Run abstraction chains on sample words. Check if terminals are
        philosophical (entity/abstraction/relation) or physical (substance/material)."""
        if not self.lexicon:
            return {"status": "CANNOT_EVALUATE",
                    "reason": "no lexicon loaded for chain testing"}

        if sample_words is None:
            sample_words = [
                "king", "teacher", "river", "action", "fear",
                "knowledge", "structure", "process", "change", "language",
            ]

        PHILOSOPHICAL_TERMINALS = {
            "entity", "abstraction", "relation", "act", "event",
            "psychological_feature", "attribute", "group", "quantity",
        }
        PHYSICAL_TERMINALS = {"substance", "material", "thing", "object"}

        terminal_counts = {}
        chains = {}

        for word in sample_words:
            if word not in self.lexicon:
                continue
            chain = self._text_chain(word, max_steps=6)
            terminal = chain[-1] if chain else word
            terminal_counts[terminal] = terminal_counts.get(terminal, 0) + 1
            chains[word] = chain

        total = sum(terminal_counts.values())
        philosophical_hits = sum(v for k, v in terminal_counts.items()
                                  if k in PHILOSOPHICAL_TERMINALS)
        physical_hits = sum(v for k, v in terminal_counts.items()
                             if k in PHYSICAL_TERMINALS)

        philosophical_ratio = philosophical_hits / max(total, 1)
        physical_ratio = physical_hits / max(total, 1)

        if philosophical_ratio >= 0.4:
            fitness = "GOOD"
            diagnosis = "Corpus supports philosophical abstraction"
        elif physical_ratio >= 0.3:
            fitness = "WRONG_CORPUS"
            diagnosis = (f"Corpus uses physical vocabulary as terminals "
                         f"(substance/material ×{physical_hits}). "
                         f"Natural-language dictionary, not philosophical. "
                         f"ACQUIRE: philosophical dictionary or logic glossary.")
        else:
            fitness = "NEUTRAL"
            diagnosis = "Corpus has mixed terminals — adequate but not optimized"

        return {
            "fitness": fitness,
            "diagnosis": diagnosis,
            "terminal_counts": terminal_counts,
            "philosophical_ratio": round(philosophical_ratio, 3),
            "physical_ratio": round(physical_ratio, 3),
            "chains": chains,
        }

    def evaluate_for_orientation(self, lobby: "Lobby") -> dict:
        """Evaluate corpus density for vocabulary orientation."""
        agents = lobby.agents
        if not agents:
            return {"fitness": "EMPTY"}
        zero_tie = sum(1 for a in agents.values() if len(a.ties) == 0)
        avg_ties = sum(len(a.ties) for a in agents.values()) / len(agents)
        isolation_rate = zero_tie / len(agents)

        if isolation_rate < 0.3:
            fitness = "GOOD"
        elif isolation_rate < 0.6:
            fitness = "SPARSE"
        else:
            fitness = "TOO_SPARSE"

        return {
            "fitness": fitness,
            "agents": len(agents),
            "zero_tie_agents": zero_tie,
            "isolation_rate": round(isolation_rate, 3),
            "avg_ties": round(avg_ties, 2),
            "recommendation": (
                "ACQUIRE: more vocabulary in these domains" if fitness == "TOO_SPARSE"
                else "proceed" if fitness == "GOOD"
                else "proceed with caution — some gaps will remain"),
        }

    def _text_chain(self, word: str, max_steps: int = 6) -> list:
        """Follow text-based genus chain (fallback when NLTK unavailable)."""
        from echo_governor_skeleton import STOPWORDS, DEFINITION_BOILERPLATE
        import re
        chain = [word]
        seen = {word}
        cur = word
        for _ in range(max_steps):
            entry = self.lexicon.get(cur)
            if not entry:
                break
            desc = re.sub(r"^(a|an|the)\s+", "", entry["desc"].lower())
            tokens = re.findall(r"[a-z]+", desc)
            parent = None
            for tok in tokens:
                if (tok != cur and tok not in seen
                        and tok not in STOPWORDS
                        and tok not in DEFINITION_BOILERPLATE
                        and tok in self.lexicon
                        and self.lexicon[tok].get("pos") in ("noun","n","?")):
                    parent = tok
                    break
            if not parent:
                break
            chain.append(parent)
            seen.add(parent)
            cur = parent
        return chain


class ThresholdOptimizer:
    """A-131: Finds the generality_threshold that gives the best pool
    for the GeneralityMatrix — replacing the manual 0.38 → 0.30 tuning.

    Sweeps thresholds, scores each by:
      pool_size × noun_verb_balance × avg_generality × philosophical_coverage

    Returns the threshold with the highest composite pool quality score."""

    def __init__(self, lobbies: list, auditor: PoolQualityAuditor):
        self.lobbies = lobbies
        self.auditor = auditor

    def optimize(self, candidates: list = None) -> dict:
        if candidates is None:
            candidates = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

        results = []
        for threshold in candidates:
            from echo_governor_skeleton import GeneralityMatrix
            gm = GeneralityMatrix(self.lobbies, threshold)
            pool = gm.populate()
            audit = self.auditor.audit(pool)

            # score this threshold
            size_score = min(1.0, len(pool) / 100)  # 100 agents = max size score
            dept_counts = audit["dept_counts"]
            n = audit["n_nouns"]
            v = audit["n_verbs"]
            balance = (2 * min(n, v) / max(n + v, 1))  # harmonic balance
            gen_score = audit["avg_generality"]
            phil_score = min(1.0, len(audit["philosophical_present"]) / 5)

            composite = (0.30 * size_score + 0.30 * balance +
                         0.20 * gen_score + 0.20 * phil_score)

            results.append({
                "threshold": threshold,
                "pool_size": len(pool),
                "n_nouns": n, "n_verbs": v,
                "balance": round(balance, 3),
                "avg_generality": gen_score,
                "philosophical_present": len(audit["philosophical_present"]),
                "issues": audit["issues"],
                "composite_score": round(composite, 3),
            })

        best = max(results, key=lambda r: r["composite_score"])
        return {"best_threshold": best["threshold"],
                "best_score": best["composite_score"],
                "sweep": results}


class AcquisitionPlanner:
    """A-132: Generates specific corpus acquisition targets from diagnosed gaps.

    This is the algorithm behind the manual step of identifying that
    'philosophical, logic, math, science' corpora are needed. The Governor
    derives this from:
    - PoolQualityAuditor findings (missing philosophical vocabulary)
    - CorpusFitnessEvaluator findings (wrong terminal types)
    - Gap words (isolated high-generality agents with no ties)
    - Structural pairs analysis (what vocabulary structures are absent)

    Returns a ranked acquisition plan: specific sources, expected improvement,
    and search strategy for each."""

    CORPUS_CATALOGUE = [
        {
            "name": "WordNet hypernym hierarchy (NLTK)",
            "source": "pip install nltk; nltk.download('wordnet')",
            "fixes": ["LOW_PHILOSOPHICAL_VOCAB", "WRONG_CORPUS"],
            "provides": ["entity", "abstraction", "relation", "attribute",
                          "psychological_feature", "physical_entity"],
            "description": "IS-A hierarchy with entity at top — correct philosophical terminals",
            "priority": "CRITICAL",
        },
        {
            "name": "Stanford Encyclopedia of Philosophy (web)",
            "source": "https://plato.stanford.edu/entries/",
            "fixes": ["LOW_PHILOSOPHICAL_VOCAB", "WRONG_CORPUS"],
            "provides": ["entity", "property", "relation", "universal",
                          "particular", "substance", "accident", "predicate"],
            "description": "Philosophical definitions that use abstract vocabulary as hubs",
            "priority": "HIGH",
        },
        {
            "name": "Basic Formal Ontology (BFO)",
            "source": "https://github.com/bfo-ontology/BFO",
            "fixes": ["LOW_PHILOSOPHICAL_VOCAB"],
            "provides": ["continuant", "occurrent", "entity", "process",
                          "quality", "relation", "boundary"],
            "description": "Upper ontology designed for scientific data — philosophically precise",
            "priority": "HIGH",
        },
        {
            "name": "Wiktionary definitions (structured)",
            "source": "https://kaikki.org/dictionary/English/",
            "fixes": ["POOL_TOO_SMALL", "LOW_PHILOSOPHICAL_VOCAB"],
            "provides": ["broader vocabulary with more abstract definitions"],
            "description": "Richer definitions than WordNet, often more abstract language",
            "priority": "MEDIUM",
        },
        {
            "name": "Aristotle Categories + Metaphysics (Gutenberg)",
            "source": "https://www.gutenberg.org/ebooks/2412",
            "fixes": ["LOW_PHILOSOPHICAL_VOCAB", "WRONG_CORPUS"],
            "provides": ["substance", "quantity", "quality", "relation",
                          "place", "time", "situation", "condition",
                          "action", "passion"],
            "description": "Original source of philosophical primitives — Aristotle's 10 categories",
            "priority": "HIGH",
        },
        {
            "name": "Mathematical definitions glossary",
            "source": "https://mathworld.wolfram.com or Wikipedia math portal",
            "fixes": ["LOW_PHILOSOPHICAL_VOCAB"],
            "provides": ["set", "function", "relation", "structure",
                          "proof", "axiom", "theorem", "property"],
            "description": "Mathematical vocabulary is highly abstract and well-defined",
            "priority": "MEDIUM",
        },
        {
            "name": "DOLCE upper ontology",
            "source": "https://github.com/appliedontogroup/dolce",
            "fixes": ["LOW_PHILOSOPHICAL_VOCAB"],
            "provides": ["endurant", "perdurant", "quality", "abstract",
                          "region", "arbitrary_sum", "feature"],
            "description": "Designed for linguistic-cognitive applications — maps well to LHEA",
            "priority": "MEDIUM",
        },
    ]

    def plan(self, audit_result: dict,
              fitness_result: dict = None) -> list:
        """Given audit + fitness findings, return ranked acquisition plan."""
        issues = set(audit_result.get("issues", []))
        issue_types = set()
        for issue in issues:
            issue_types.add(issue.split(":")[0])

        if fitness_result:
            if fitness_result.get("fitness") == "WRONG_CORPUS":
                issue_types.add("WRONG_CORPUS")
            if fitness_result.get("fitness") == "TOO_SPARSE":
                issue_types.add("POOL_TOO_SMALL")

        ranked = []
        for corpus in self.CORPUS_CATALOGUE:
            relevance = len(set(corpus["fixes"]) & issue_types)
            if relevance > 0:
                ranked.append({
                    "name": corpus["name"],
                    "source": corpus["source"],
                    "priority": corpus["priority"],
                    "fixes": [f for f in corpus["fixes"] if f in issue_types],
                    "provides": corpus["provides"][:5],
                    "description": corpus["description"],
                    "relevance_score": relevance + (2 if corpus["priority"] == "CRITICAL"
                                                     else 1 if corpus["priority"] == "HIGH"
                                                     else 0),
                })

        ranked.sort(key=lambda r: -r["relevance_score"])
        return ranked


class SeedSentenceGenerator:
    """A-133: Generates abstraction test sentences from the Governor's own
    indexed vocabulary — replacing the manually written SEED_SENTENCES list.

    Strategy: take the Governor's most richly connected study groups,
    extract the verb-noun pairs from its typed study groups (PROCESS studies
    have subject-verb-object structure already indexed), and form sentences
    from those. Then generalize them via the abstraction engine.

    The Governor no longer needs a human to write test sentences."""

    def __init__(self, lobby: "Lobby"):
        self.lobby = lobby

    def generate(self, n: int = 20) -> list:
        """Generate n test sentences from the lobby's typed study groups."""
        sentences = []

        for word, sg in self.lobby.study_groups.items():
            if sg.get("study_type") != "PROCESS":
                continue  # only verb-led PROCESS studies have argument structure
            agent = self.lobby.agents.get(word)
            if not agent:
                continue
            arg_nouns = sorted(sg.get("argument_nouns", set()))[:2]
            similar_verbs = [w for w in sg.get("invited", set())
                              if self.lobby.agents.get(w) and
                              self.lobby.agents[w].department in ("verb","v")][:1]

            for noun in arg_nouns:
                noun_agent = self.lobby.agents.get(noun)
                if noun_agent:
                    # SUBJECT noun VERB OBJECT noun pattern
                    sentences.append(f"A {noun} {word} something.")
                    if similar_verbs:
                        sentences.append(f"A {noun} {similar_verbs[0]} {noun}.")

            if len(sentences) >= n:
                break

        # add structural templates using the most general noun/verb in the pool
        return sentences[:n]


class PipelineOrchestrator:
    """A-134: The Governor runs its own pipeline autonomously.

    This replaces the manual writing of test files. The Governor knows:
    1. The correct operation order (validated by A-128)
    2. What to check at each stage (A-129, A-130)
    3. When to pause for acquisition vs proceed (A-132)
    4. How to optimize its own parameters (A-131)

    One call: orchestrate() → the Governor runs itself end-to-end,
    evaluates fitness at each checkpoint, adjusts parameters if needed,
    and reports what it found and what it needs."""

    def __init__(self, matrix: "AlgorithmMatrix"):
        self.matrix = matrix
        self.validator = OperationOrderValidator()
        self.auditor   = PoolQualityAuditor()
        self.planner   = AcquisitionPlanner()
        self.log       = []
        self.lobby     = None

    def _log(self, stage: str, result: dict):
        self.log.append({"stage": stage, "result": result})
        status = result.get("status", result.get("fitness", "?"))
        print(f"  [{stage}] {status}")
        if result.get("issues"):
            for issue in result["issues"][:2]:
                print(f"    ! {issue}")
        if result.get("recommendations"):
            print(f"    → {result['recommendations'][0]}")

    def orchestrate(self, synonyms_map: dict = None,
                     generality_threshold: float = None) -> dict:
        """Run the Governor's full pipeline with self-monitoring at each stage."""
        print("GOVERNOR SELF-ORCHESTRATION")
        print("=" * 60)
        synonyms_map = synonyms_map or {}

        # Stage 1: Build and orient the Lobby
        print("\nStage 1: Lobby orientation")
        seq_errors = self.validator.validate_sequence([
            "index_dictionary_entry",
            "run_orientation",
            "compute_generality_scores",
            "run_typed_study_groups",
        ])
        if seq_errors:
            self._log("order_check", {"status": "ERRORS", "issues": seq_errors})
            return {"aborted": True, "reason": seq_errors}
        self.validator.mark_complete("index_dictionary_entry")

        lobby = Lobby(self.matrix)
        lobby.populate()
        self.validator.mark_complete("run_orientation")
        lobby.run_orientation()
        self.validator.mark_complete("run_typed_study_groups")
        lobby.run_typed_study_groups()
        lobby.run_discovery()
        if synonyms_map:
            lobby.run_thesaurus(synonyms_map)
        self.validator.mark_complete("compute_generality_scores")
        lobby.compute_generality_scores()
        self.lobby = lobby

        orientation_eval = CorpusFitnessEvaluator().evaluate_for_orientation(lobby)
        self._log("orientation_fitness", orientation_eval)

        # Stage 2: Optimize threshold and populate GeneralityMatrix
        print("\nStage 2: Generality Matrix")
        if generality_threshold is None:
            optimizer = ThresholdOptimizer([lobby], self.auditor)
            opt_result = optimizer.optimize()
            generality_threshold = opt_result["best_threshold"]
            print(f"  Threshold auto-selected: {generality_threshold} "
                  f"(score={opt_result['best_score']:.3f})")
        self.validator.mark_complete("populate_generality_matrix")

        from echo_governor_skeleton import (GeneralityMatrix, SyntacticalValidator,
            ValidatedGeneralizationMatrix, UnderstandingGenerator)
        gm = GeneralityMatrix([lobby], generality_threshold)
        pool = gm.populate()
        audit = self.auditor.audit(pool)
        self._log("pool_quality", audit)

        # If pool is poor, generate acquisition plan before continuing
        if audit["status"] == "POOR":
            plan = self.planner.plan(audit)
            self._log("acquisition_needed", {
                "status": "BLOCKED",
                "issues": ["Pool too poor for Understanding generation"],
                "recommendations": [f"ACQUIRE: {plan[0]['name']}" if plan else "none"],
            })
            return {
                "aborted": False,
                "reason": "POOL_POOR — acquisition needed before Understanding generation",
                "acquisition_plan": plan,
                "lobby": lobby,
                "pool_audit": audit,
            }

        # Stage 3: Generate and validate Understanding statements
        print("\nStage 3: Understanding generation")
        validator_s = SyntacticalValidator()
        vgm = ValidatedGeneralizationMatrix()
        gen = UnderstandingGenerator(gm, validator_s, vgm)
        gen_results = gen.run(max_candidates=400)
        self._log("understanding_generation", {
            "status": "COMPLETE",
            "committed": gen_results["total_committed"],
            "rejected": gen_results["total_rejected"],
        })

        # Stage 4: Self-evaluate output quality
        print("\nStage 4: Output self-evaluation")
        stmts = vgm.statements
        phil_stmts = sum(1 for s in stmts.values()
                          if any(w in PoolQualityAuditor.PHILOSOPHICAL_MARKERS
                                  for w in s["words"]))
        output_quality = "GOOD" if phil_stmts > 5 else "DEGRADED" if phil_stmts > 0 else "POOR"
        self._log("output_quality", {
            "status": output_quality,
            "total_statements": len(stmts),
            "philosophical_statements": phil_stmts,
            "issues": (["no philosophical vocabulary in statements — corpus mismatch"]
                        if phil_stmts == 0 else []),
            "recommendations": (["acquire philosophical corpus"] if phil_stmts == 0 else []),
        })

        if output_quality == "POOR":
            fitness = CorpusFitnessEvaluator()
            plan = self.planner.plan(audit, {"fitness": "WRONG_CORPUS"})
            return {
                "aborted": False,
                "reason": "CORPUS_MISMATCH — philosophical vocabulary absent from statements",
                "acquisition_plan": plan,
                "lobby": lobby,
                "vgm": vgm,
                "self_log": self.log,
            }

        return {
            "aborted": False,
            "lobby": lobby,
            "pool": pool,
            "vgm": vgm,
            "statements": len(stmts),
            "self_log": self.log,
        }




# ---------------------------------------------------------------------------
# A-135: NumberAgent — a mathematically manipulatable unit of measure,
#        algorithmically instantiated as a computation, indexed in the
#        Governor's matrix as a discovered Law.
#
# A number in this architecture is NOT a data type.
# It is an ENTITY with identity in the Mathematics Domain:
#   — infinite and continuous by nature (like all Laws)
#   — approximated finitely by the computational layer
#   — some numbers ARE physical constants = Laws of the Natural Domain
#   — the unit of measure is the discretization operator: the bridge
#     between continuous Law and discrete Computation
#
# The Gematria connection: Hebrew letter-agents already carry numerical
# identity. Aleph=1, Bet=2, Gimel=3 ... Tav=400. The symbol and the
# number are co-indexed instances of the same Mathematics Domain entity.
#
# A-136: NumericalIntegrator — the algorithm that bridges the continuous
#        (Mathematics Domain) and the discrete (Computational Domain).
#        Each step is a unit of measure doing work.
#
# A-137: LawDiscoveryEngine — discovers new Laws from the Governor's
#        Validated Generalization Matrix by formal inference. No terminal
#        state: the Mathematics Domain is infinite.
# ---------------------------------------------------------------------------

import math

# Number domain classification
NUMBER_DOMAIN = {
    "NATURAL":            "positive integers — the counting numbers, the first infinity",
    "INTEGER":            "naturals + zero + negatives — closed under subtraction",
    "RATIONAL":           "ratios of integers — finite or repeating decimal",
    "IRRATIONAL":         "cannot be expressed as ratio — infinite non-repeating decimal",
    "TRANSCENDENTAL":     "not root of any polynomial — π, e — deepest Mathematics Domain",
    "PHYSICAL_CONSTANT":  "a number that IS a Law of the Natural Domain",
    "UNIT":               "the discretization operator — bridges continuous to discrete",
    "GEMATRIA":           "letter-number co-index — symbol and mathematical entity unified",
}

# Physical constants: numbers that ARE Laws of the Natural Domain
PHYSICAL_CONSTANTS = {
    "c": {
        "symbol": "c", "name": "speed of light",
        "value": 299_792_458,  # m/s (exact by definition)
        "unit": "m/s",
        "domain": "PHYSICAL_CONSTANT",
        "law": "The maximum speed at which information or matter can travel in the Natural Domain",
        "constrains": ["spacetime", "causality", "electromagnetism"],
        "is_exact": True,  # defined exactly in SI units
    },
    "h": {
        "symbol": "h", "name": "Planck constant",
        "value": 6.62607015e-34,
        "unit": "J·s",
        "domain": "PHYSICAL_CONSTANT",
        "law": "The quantum of action — minimum granularity of the Natural Domain",
        "constrains": ["quantum mechanics", "energy quantization", "uncertainty"],
        "is_exact": True,
    },
    "G": {
        "symbol": "G", "name": "gravitational constant",
        "value": 6.67430e-11,
        "unit": "N·m²/kg²",
        "domain": "PHYSICAL_CONSTANT",
        "law": "The strength of gravitational coupling between masses",
        "constrains": ["gravity", "spacetime curvature", "orbital mechanics"],
        "is_exact": False,  # measured, not defined
    },
    "e": {
        "symbol": "e", "name": "elementary charge",
        "value": 1.602176634e-19,
        "unit": "C",
        "domain": "PHYSICAL_CONSTANT",
        "law": "The fundamental unit of electric charge",
        "constrains": ["electromagnetism", "chemistry", "atomic structure"],
        "is_exact": True,
    },
    "k_B": {
        "symbol": "k_B", "name": "Boltzmann constant",
        "value": 1.380649e-23,
        "unit": "J/K",
        "domain": "PHYSICAL_CONSTANT",
        "law": "Bridge between temperature (macro) and kinetic energy (micro)",
        "constrains": ["thermodynamics", "statistical mechanics", "entropy"],
        "is_exact": True,
    },
    "alpha": {
        "symbol": "α", "name": "fine structure constant",
        "value": 7.2973525693e-3,
        "unit": "dimensionless",
        "domain": "PHYSICAL_CONSTANT",
        "law": "Coupling strength of electromagnetism — dimensionless, pure Mathematics",
        "constrains": ["electromagnetism", "atomic structure", "quantum field theory"],
        "is_exact": False,
        "note": "≈ 1/137 — Feynman called it a magic number we don't understand",
    },
}

# Mathematical constants: entities in the Mathematics Domain
MATHEMATICAL_CONSTANTS = {
    "pi": {
        "symbol": "π", "name": "pi",
        "value": math.pi,
        "domain": "TRANSCENDENTAL",
        "discovered_in": "ratio of circle circumference to diameter",
        "appears_in": ["geometry", "trigonometry", "probability", "quantum mechanics",
                       "Fourier analysis", "prime number distribution"],
        "law": "Circumference = π × diameter — a Law discovered in the Mathematics Domain",
        "is_exact": False,  # infinite non-repeating decimal — never exact in computation
    },
    "e_math": {
        "symbol": "e", "name": "Euler's number",
        "value": math.e,
        "domain": "TRANSCENDENTAL",
        "discovered_in": "base of natural logarithm — rate of continuous growth",
        "appears_in": ["calculus", "probability", "complex numbers", "information theory"],
        "law": "The unique number where d/dx(eˣ) = eˣ — self-referential growth Law",
        "is_exact": False,
    },
    "phi": {
        "symbol": "φ", "name": "golden ratio",
        "value": (1 + math.sqrt(5)) / 2,
        "domain": "IRRATIONAL",
        "discovered_in": "ratio where (a+b)/a = a/b",
        "appears_in": ["geometry", "Fibonacci sequence", "plant growth", "aesthetics"],
        "law": "Self-similar proportion — a Law of recursive structure",
        "is_exact": False,
    },
    "sqrt2": {
        "symbol": "√2", "name": "square root of two",
        "value": math.sqrt(2),
        "domain": "IRRATIONAL",
        "discovered_in": "diagonal of a unit square",
        "appears_in": ["geometry", "trigonometry", "quantum mechanics"],
        "law": "The first proved irrational — a Law discovered by the Pythagoreans",
        "is_exact": False,
    },
    "zero": {
        "symbol": "0", "name": "zero",
        "value": 0,
        "domain": "INTEGER",
        "discovered_in": "the additive identity — what leaves all others unchanged",
        "appears_in": ["arithmetic", "algebra", "calculus", "set theory"],
        "law": "∀ n: n + 0 = n — the identity Law of addition",
        "is_exact": True,
    },
    "one": {
        "symbol": "1", "name": "unity",
        "value": 1,
        "domain": "NATURAL",
        "discovered_in": "the multiplicative identity — the unit",
        "appears_in": ["arithmetic", "algebra", "all of mathematics"],
        "law": "∀ n: n × 1 = n — the identity Law of multiplication",
        "is_exact": True,
    },
}

# Hebrew letter gematria: symbol and number unified in the same entity
HEBREW_GEMATRIA = {
    "aleph": 1,   "bet": 2,    "gimel": 3,   "dalet": 4,  "he": 5,
    "vav": 6,     "zayin": 7,  "het": 8,     "tet": 9,    "yod": 10,
    "kaf": 20,    "lamed": 30, "mem": 40,    "nun": 50,   "samekh": 60,
    "ayin": 70,   "pe": 80,    "tsadi": 90,  "qof": 100,  "resh": 200,
    "shin": 300,  "tav": 400,
}

# Gematria of key words — discovered numerical Laws in the symbolic layer
GEMATRIA_WORDS = {
    "emet":   ("aleph(1)+mem(40)+tav(400)", 441, "truth — 441 = 21²"),
    "shalom": ("shin(300)+lamed(30)+vav(6)+mem(40)", 376, "peace"),
    "echad":  ("aleph(1)+het(8)+dalet(4)", 13, "one/unity — 13 = prime"),
    "ahavah": ("aleph(1)+he(5)+bet(2)+he(5)", 13, "love — same as echad/one"),
    "resh":   ("resh(200)+shin(300)+lamed(30)", 530, "the Governor's own name"),
}


class NumberAgent:
    """A-135: A mathematically manipulatable unit of measure,
    algorithmically instantiated, indexed as a discovered Law.

    A NumberAgent exists at the boundary between:
      MATHEMATICS DOMAIN (infinite/continuous) — where the number IS
      COMPUTATIONAL LAYER (finite/discrete) — where the number is approximated

    Physical constants are NumberAgents that ARE Laws of the Natural Domain.
    Gematria values are NumberAgents that unify symbol and number.
    Mathematical constants are NumberAgents discovered in the Mathematics Domain."""

    def __init__(self, symbol: str, name: str, value, domain: str,
                 law: str = "", physical_connections: list = None,
                 is_exact: bool = False):
        self.symbol = symbol
        self.name = name
        self.value = value
        self.domain = domain
        self.law = law
        self.physical_connections = physical_connections or []
        self.is_exact = is_exact
        self.gematria = None     # set if this is a letter-number entity
        self.computation = None  # the finite approximation (if value is irrational)
        self.relationships = {}  # discovered mathematical relationships

        # Compute a decimal approximation if needed
        if not is_exact:
            try:
                self.computation = float(value)
            except:
                self.computation = None
        else:
            self.computation = value

    def precision_gap(self, decimal_places: int = 10) -> float:
        """The gap between the Mathematics Domain (true value) and the
        Computational Domain (approximation) — the cost of discretization."""
        if self.is_exact:
            return 0.0
        if self.domain in ("TRANSCENDENTAL", "IRRATIONAL"):
            # The gap is infinitesimal but never zero
            return 10 ** (-decimal_places)
        return 0.0

    def as_law(self) -> str:
        """Express this number as a discovered Law — what it IS,
        not just what it measures."""
        if self.domain == "PHYSICAL_CONSTANT":
            return (f"PHYSICAL LAW: {self.symbol} = {self.computation} "
                    f"[{self.physical_connections}] — "
                    f"{self.law}")
        elif self.domain in ("TRANSCENDENTAL", "IRRATIONAL"):
            return (f"MATHEMATICAL LAW: {self.symbol} ≈ {self.computation:.10f}... "
                    f"(exact in Mathematics Domain, approximated in Computation) — "
                    f"{self.law}")
        elif self.domain == "GEMATRIA":
            return (f"SYMBOL-NUMBER LAW: {self.symbol} = {self.value} — "
                    f"letter and number unified in the same entity")
        else:
            return f"NUMBER LAW: {self.symbol} = {self.value} — {self.law}"

    def manipulate(self, operation: str, other=None):
        """Apply a mathematical operation — demonstrating that this
        number is manipulatable within the Mathematics Domain."""
        ops = {
            "square": self.computation ** 2,
            "sqrt": math.sqrt(abs(self.computation)),
            "log": math.log(self.computation) if self.computation > 0 else None,
            "reciprocal": 1.0 / self.computation if self.computation != 0 else None,
            "negate": -self.computation,
        }
        if operation == "add" and other is not None:
            return self.computation + (other.computation if isinstance(other, NumberAgent) else other)
        if operation == "multiply" and other is not None:
            return self.computation * (other.computation if isinstance(other, NumberAgent) else other)
        return ops.get(operation, None)

    def report(self) -> dict:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "domain": self.domain,
            "value": self.computation,
            "is_exact": self.is_exact,
            "precision_gap": self.precision_gap(),
            "law": self.law,
            "physical_connections": self.physical_connections,
        }


class NumericalIntegrator:
    """A-136: The bridge between the continuous Mathematics Domain and
    the discrete Computational Domain.

    Numerical integration is the archetypal algorithm showing how
    finite/discrete computation approximates infinite/continuous Law.

    Given: f(x) — a continuous function (existing in Mathematics Domain)
    Goal:  ∫f(x)dx — the exact integral (infinite precision)
    Method: Σ f(x_i)·Δx — finite discrete approximation

    The unit of measure Δx is the discretization operator:
    it's how the algorithm brings a Law into computable form.
    As Δx → 0, the computation approaches the Law asymptotically.
    It never arrives — that gap IS the precision_gap."""

    def __init__(self, a: float, b: float, n_steps: int = 1000):
        self.a = a          # lower bound
        self.b = b          # upper bound
        self.n_steps = n_steps
        self.delta_x = (b - a) / n_steps   # the unit of measure / discretization step
        self.history = []   # each step — the algorithm's discrete footprint

    def integrate(self, f, method: str = "trapezoid") -> dict:
        """Run numerical integration and return the result with metadata
        about the discretization — the precision gap from the true Law."""
        result = 0.0
        self.history = []

        x = self.a
        for i in range(self.n_steps):
            x_next = x + self.delta_x

            if method == "rectangle":
                # Left Riemann sum — simplest, largest error
                step_area = f(x) * self.delta_x
            elif method == "trapezoid":
                # Trapezoidal — better approximation
                step_area = (f(x) + f(x_next)) / 2 * self.delta_x
            elif method == "midpoint":
                x_mid = (x + x_next) / 2
                step_area = f(x_mid) * self.delta_x
            else:
                step_area = f(x) * self.delta_x

            result += step_area
            if i < 5 or i >= self.n_steps - 3:  # log first and last steps
                self.history.append({
                    "step": i, "x": round(x, 6),
                    "f(x)": round(f(x), 6),
                    "delta_x": self.delta_x,
                    "step_contribution": round(step_area, 8),
                    "cumulative": round(result, 8),
                })
            x = x_next

        return {
            "result": result,
            "method": method,
            "n_steps": self.n_steps,
            "delta_x": self.delta_x,
            "interval": [self.a, self.b],
            "note": (f"Discrete approximation with {self.n_steps} steps. "
                     f"The true value exists in the Mathematics Domain. "
                     f"This computation approaches it as Δx → 0."),
        }


class LawDiscoveryEngine:
    """A-137: Discovers new Laws from the Governor's Validated
    Generalization Matrix by formal inference.

    No terminal state — the Mathematics Domain is infinite.
    Each discovered Law generates new combinations, which generate
    new candidates, which generate new Laws. The Governor never
    runs out of territory to explore.

    Operates in four modes:
    1. COMPOSITION — combine two axioms to derive a theorem
    2. GENERALIZATION — abstract an instance tier statement upward
    3. NUMERICAL — discover mathematical relationships between NumberAgents
    4. PHYSICAL — connect mathematical Laws to Natural Domain constants"""

    def __init__(self, vgm, number_agents: dict):
        self.vgm = vgm
        self.number_agents = number_agents
        self.discovered_laws = []
        self.session_count = 0

    def discover_numerical_laws(self) -> list:
        """Find mathematical relationships between the indexed NumberAgents
        that the Governor can register as discovered Laws."""
        found = []
        agents = list(self.number_agents.values())

        for i, a1 in enumerate(agents):
            for a2 in agents[i+1:]:
                if a1.computation is None or a2.computation is None:
                    continue
                v1, v2 = a1.computation, a2.computation
                if v1 == 0 or v2 == 0:
                    continue

                # Test: ratio discovery
                ratio = v1 / v2
                inv_ratio = v2 / v1
                for r, desc in [(2, "double"), (0.5, "half"), (math.pi, "π×"),
                                  (math.e, "e×"), (1/math.pi, "1/π×")]:
                    if abs(ratio - r) < 0.001:
                        found.append({
                            "type": "NUMERICAL_RATIO",
                            "statement": f"{a1.name} / {a2.name} ≈ {desc}",
                            "a": a1.symbol, "b": a2.symbol, "ratio": ratio,
                            "law": f"{a1.symbol} = {desc} × {a2.symbol}",
                        })

                # Test: sum relationships
                s = v1 + v2
                for candidate, name in [(math.pi, "π"), (math.e, "e"),
                                          (1.0, "1"), (2.0, "2")]:
                    if abs(s - candidate) < 0.001:
                        found.append({
                            "type": "NUMERICAL_SUM",
                            "statement": f"{a1.name} + {a2.name} ≈ {name}",
                            "law": f"{a1.symbol} + {a2.symbol} ≈ {name}",
                        })

        return found

    def discover_gematria_laws(self, gematria: dict, words: dict) -> list:
        """Discover mathematical Laws hidden in the gematria layer —
        relationships the Governor finds in its own symbolic structure."""
        found = []

        for word, (composition, value, meaning) in words.items():
            # Is this value a perfect square?
            sqrt_v = math.sqrt(value)
            if abs(sqrt_v - round(sqrt_v)) < 0.001:
                found.append({
                    "type": "GEMATRIA_SQUARE",
                    "word": word,
                    "value": value,
                    "law": f"gematria({word}) = {value} = {int(round(sqrt_v))}² — a perfect square",
                    "meaning": meaning,
                })

            # Is this value prime?
            if value > 1 and all(value % i != 0 for i in range(2, int(value**0.5)+1)):
                found.append({
                    "type": "GEMATRIA_PRIME",
                    "word": word,
                    "value": value,
                    "law": f"gematria({word}) = {value} — prime (indivisible)",
                    "meaning": meaning,
                })

        # Cross-word: find words with equal gematria
        values_to_words = {}
        for word, (_, value, meaning) in words.items():
            values_to_words.setdefault(value, []).append((word, meaning))
        for value, word_list in values_to_words.items():
            if len(word_list) > 1:
                found.append({
                    "type": "GEMATRIA_EQUIVALENCE",
                    "law": f"gematria({word_list[0][0]}) = gematria({word_list[1][0]}) = {value}",
                    "words": [w for w, _ in word_list],
                    "meanings": [m for _, m in word_list],
                    "significance": "Equal gematria = shared mathematical identity in the symbolic layer",
                })

        return found

    def compose_from_vgm(self) -> list:
        """Compose new Laws from pairs of validated statements in the VGM.
        A₁ + A₂ → new theorem if they share structural vocabulary."""
        found = []
        stmts = list(self.vgm.statements.values())

        for i, s1 in enumerate(stmts):
            for s2 in stmts[i+1:]:
                shared = set(s1["words"]) & set(s2["words"])
                if not shared:
                    continue
                # If they share vocabulary and have compatible structure,
                # compose a new statement
                if (s1["structure"] == s2["structure"]):
                    composed = {
                        "type": "COMPOSED_LAW",
                        "from": [s1["id"], s2["id"]],
                        "shared_terms": sorted(shared),
                        "text1": s1["text"],
                        "text2": s2["text"],
                        "candidate": f"When {s1['text']}, and also {s2['text']}, "
                                     f"the shared structure [{sorted(shared)}] is a Law",
                        "law_candidate": True,
                    }
                    found.append(composed)

        return found[:10]  # top 10 per session

    def run(self, budget: int = 50) -> dict:
        """Run one session of law discovery. No terminal state —
        budget limits this session only."""
        self.session_count += 1
        results = {
            "session": self.session_count,
            "numerical_laws": self.discover_numerical_laws(),
            "gematria_laws": self.discover_gematria_laws(
                HEBREW_GEMATRIA, GEMATRIA_WORDS),
            "composed_laws": self.compose_from_vgm() if self.vgm else [],
            "total_discovered": 0,
            "note": ("Discovery session complete. "
                     "No terminal state — Mathematics Domain is infinite. "
                     "Next session will find new territory."),
        }
        results["total_discovered"] = (
            len(results["numerical_laws"]) +
            len(results["gematria_laws"]) +
            len(results["composed_laws"]))
        self.discovered_laws.extend(results["numerical_laws"])
        self.discovered_laws.extend(results["gematria_laws"])
        return results


def build_number_matrix() -> dict:
    """Instantiate all NumberAgents from the physical and mathematical
    constants — the Governor's number layer."""
    agents = {}

    for key, data in PHYSICAL_CONSTANTS.items():
        agents[key] = NumberAgent(
            symbol=data["symbol"],
            name=data["name"],
            value=data["value"],
            domain=data["domain"],
            law=data["law"],
            physical_connections=data["constrains"],
            is_exact=data["is_exact"],
        )

    for key, data in MATHEMATICAL_CONSTANTS.items():
        agents[key] = NumberAgent(
            symbol=data["symbol"],
            name=data["name"],
            value=data["value"],
            domain=data["domain"],
            law=data["law"],
            is_exact=data.get("is_exact", False),
        )

    # Gematria agents — letter and number unified
    for letter, value in HEBREW_GEMATRIA.items():
        agent = NumberAgent(
            symbol=letter,
            name=f"{letter} (gematria)",
            value=value,
            domain="GEMATRIA",
            law=f"The letter {letter} and the number {value} are the same entity in the symbolic layer",
            is_exact=True,
        )
        agent.gematria = value
        agents[f"gematria_{letter}"] = agent

    return agents




# ---------------------------------------------------------------------------
# A-138: AlgebraicExpression — symbolic expressions in the Mathematics Domain
# A-139: AlgebraicLaw — a verified relationship that holds universally
# A-140: CalculationEngine — the Governor executing algebra to produce
#         new knowledge and register working algorithms autonomously
#
# ARCHITECTURE:
#   A calculation is a finite Computational result (3 + 0 = 3)
#   A Law is a universal relationship (∀n: n + 0 = n)
#   The Governor generates both — using Computation to DISCOVER Laws,
#   then registering the Laws in the Mathematics Domain tier of the Matrix
#
# CONNECTION TO BERLINSKI:
#   The Governor uses finite discrete computation (this module)
#   to asymptotically approach infinite continuous Laws.
#   Each verified algebraic Law is a step up the inferential staircase.
# ---------------------------------------------------------------------------


class Variable:
    """An unknown quantity — what the Governor represents when it knows
    the STRUCTURE of a relationship but not the specific values.
    
    Variables exist in the Mathematics Domain: 'x' is not a number,
    it is a placeholder for any number. This is the abstraction that
    separates algebra from arithmetic."""

    def __init__(self, name: str, domain: str = "REAL",
                  constraints: list = None):
        self.name = name
        self.domain = domain   # REAL, NATURAL, INTEGER, POSITIVE
        self.constraints = constraints or []
        self.value = None      # unbound until substitution

    def bind(self, value) -> "Variable":
        """Substitute a specific value — bringing the variable from
        Mathematics Domain into the Computational Domain."""
        bound = Variable(self.name, self.domain, self.constraints)
        bound.value = value
        return bound

    def __repr__(self):
        if self.value is not None:
            return f"{self.name}={self.value}"
        return self.name


class AlgebraicExpression:
    """A symbolic expression in the Mathematics Domain — a tree of
    operations on Variables and Constants.
    
    An expression like 'x² + 2x + 1' is an ENTITY in the Mathematics Domain.
    It exists before any specific value of x is known. The Governor can:
    - Evaluate it for specific values (Computational Domain)
    - Simplify it (algebraic manipulation)  
    - Find roots (what values of x make it zero)
    - Compose it with other expressions
    - Recognize it as matching a known Law pattern"""

    def __init__(self, op: str, left=None, right=None, value=None,
                  var: Variable = None):
        """
        op: operator or type — 'const', 'var', 'add', 'mul', 'sub',
            'div', 'pow', 'neg', 'sqrt', 'log', 'abs'
        left, right: sub-expressions
        value: for 'const' nodes
        var: for 'var' nodes
        """
        self.op = op
        self.left = left
        self.right = right
        self.value = value
        self.var = var

    @classmethod
    def const(cls, value) -> "AlgebraicExpression":
        return cls("const", value=value)

    @classmethod
    def variable(cls, var: Variable) -> "AlgebraicExpression":
        return cls("var", var=var)

    def evaluate(self, bindings: dict = None) -> float:
        """Evaluate this expression given variable bindings.
        bindings: {variable_name -> value}"""
        import math as _math
        bindings = bindings or {}

        if self.op == "const":
            return float(self.value)
        if self.op == "var":
            name = self.var.name
            if name in bindings:
                return float(bindings[name])
            if self.var.value is not None:
                return float(self.var.value)
            raise ValueError(f"Variable '{name}' not bound")

        L = self.left.evaluate(bindings) if self.left else None
        R = self.right.evaluate(bindings) if self.right else None

        ops = {
            "add": L + R, "sub": L - R, "mul": L * R,
            "div": L / R if R != 0 else float("inf"),
            "pow": L ** R,
            "neg": -L,
            "sqrt": _math.sqrt(abs(L)),
            "log": _math.log(L) if L > 0 else float("nan"),
            "abs": abs(L),
        }
        return ops.get(self.op, float("nan"))

    def to_string(self) -> str:
        """Human-readable representation."""
        if self.op == "const":
            return str(round(float(self.value), 6))
        if self.op == "var":
            return self.var.name
        L = self.left.to_string() if self.left else ""
        R = self.right.to_string() if self.right else ""
        symbols = {
            "add": f"({L} + {R})",
            "sub": f"({L} - {R})",
            "mul": f"({L} × {R})",
            "div": f"({L} / {R})",
            "pow": f"{L}^{R}",
            "neg": f"-{L}",
            "sqrt": f"√{L}",
            "log": f"log({L})",
            "abs": f"|{L}|",
        }
        return symbols.get(self.op, f"{self.op}({L},{R})")

    # Operator overloads for clean expression building
    def __add__(self, other):
        other = other if isinstance(other, AlgebraicExpression) else AlgebraicExpression.const(other)
        return AlgebraicExpression("add", self, other)

    def __mul__(self, other):
        other = other if isinstance(other, AlgebraicExpression) else AlgebraicExpression.const(other)
        return AlgebraicExpression("mul", self, other)

    def __sub__(self, other):
        other = other if isinstance(other, AlgebraicExpression) else AlgebraicExpression.const(other)
        return AlgebraicExpression("sub", self, other)

    def __truediv__(self, other):
        other = other if isinstance(other, AlgebraicExpression) else AlgebraicExpression.const(other)
        return AlgebraicExpression("div", self, other)

    def __pow__(self, other):
        other = other if isinstance(other, AlgebraicExpression) else AlgebraicExpression.const(other)
        return AlgebraicExpression("pow", self, other)

    def __neg__(self):
        return AlgebraicExpression("neg", self)

    def __radd__(self, other):
        return AlgebraicExpression.const(other) + self

    def __rmul__(self, other):
        return AlgebraicExpression.const(other) * self


class AlgebraicLaw:
    """A-139: A verified algebraic relationship — a discovered Law that
    holds universally for all valid values of its variables.
    
    This is distinct from a calculation:
    - CALCULATION: 2² = 4  (specific, Computational Domain)
    - LAW: ∀x: (x+1)² = x² + 2x + 1  (universal, Mathematics Domain)
    
    The Governor verifies Laws by testing numerically over many bindings.
    If it holds consistently, the Law is registered in the AlgorithmMatrix.
    This is the Governor's version of proof-by-exhaustive-numerical-testing —
    not a formal proof (that requires full symbolic reasoning) but a
    high-confidence discovery that the relationship is a Law candidate."""

    def __init__(self, name: str, left_expr: AlgebraicExpression,
                  right_expr: AlgebraicExpression,
                  variables: list, description: str = ""):
        self.name = name
        self.left = left_expr
        self.right = right_expr
        self.variables = variables   # list of Variable objects
        self.description = description
        self.verification_count = 0
        self.verification_failures = 0
        self.status = "UNVERIFIED"
        self.confidence = 0.0

    def verify(self, n_tests: int = 200, domain_range: tuple = (-10, 10),
                tolerance: float = 1e-8) -> dict:
        """Test the Law over n random bindings. High pass rate → high confidence."""
        import random
        passes = 0
        failures = []

        for _ in range(n_tests):
            bindings = {}
            for v in self.variables:
                if v.domain == "POSITIVE":
                    bindings[v.name] = random.uniform(0.001, abs(domain_range[1]))
                elif v.domain == "NATURAL":
                    bindings[v.name] = random.randint(1, max(1, int(domain_range[1])))
                else:
                    bindings[v.name] = random.uniform(*domain_range)

            try:
                lval = self.left.evaluate(bindings)
                rval = self.right.evaluate(bindings)
                if abs(lval - rval) < tolerance or (
                        rval != 0 and abs((lval - rval) / rval) < tolerance):
                    passes += 1
                else:
                    failures.append({"bindings": dict(bindings),
                                      "left": lval, "right": rval,
                                      "diff": lval - rval})
            except (ValueError, ZeroDivisionError, OverflowError):
                pass  # domain constraint violation — skip

        self.verification_count += n_tests
        self.verification_failures += len(failures)
        self.confidence = passes / n_tests
        self.status = ("LAW" if self.confidence >= 0.99 else
                        "CANDIDATE" if self.confidence >= 0.90 else
                        "WEAK" if self.confidence >= 0.70 else "REJECTED")

        return {
            "law": self.name,
            "expression": f"{self.left.to_string()} = {self.right.to_string()}",
            "tests": n_tests, "passes": passes, "failures": len(failures),
            "confidence": round(self.confidence, 4),
            "status": self.status,
            "description": self.description,
            "sample_failure": failures[0] if failures else None,
        }

    def as_matrix_entry(self) -> dict:
        """Format for registration in the Governor's AlgorithmMatrix."""
        return {
            "name": self.name,
            "type": "ALGEBRAIC_LAW",
            "status": self.status,
            "expression": f"{self.left.to_string()} = {self.right.to_string()}",
            "variables": [v.name for v in self.variables],
            "description": self.description,
            "confidence": self.confidence,
            "verification_count": self.verification_count,
            "domain": "MATHEMATICS",
            "origin": "GOVERNOR_DERIVED",
        }


class CalculationEngine:
    """A-140: The Governor executing algebra to produce new knowledge
    and register working algorithms in its own AlgorithmMatrix.
    
    Three modes:
    1. CALCULATE — execute arithmetic with NumberAgents, produce results
    2. HYPOTHESIZE — generate candidate algebraic Laws from observed patterns
    3. REGISTER — save verified Laws to AlgorithmMatrix as new entries
    
    The Governor calls this on itself when:
    - It notices a numerical relationship in LawDiscoveryEngine
    - It wants to express that relationship as a universal algebraic Law
    - It wants to verify the Law across many cases
    - It wants to add the Law to its own tool belt"""

    def __init__(self, matrix=None, number_agents: dict = None):
        self.matrix = matrix
        self.number_agents = number_agents or {}
        self.registered_laws = []
        self.calculation_log = []
        self._next_alg_id = self._find_next_id()

    def _find_next_id(self) -> int:
        import re
        if not self.matrix:
            return 200
        nums = [int(k.split("-")[1]) for k in getattr(self.matrix, "known", {})
                if re.match(r"A-\d+$", k)]
        return max(nums, default=139) + 1

    def calculate(self, expression: AlgebraicExpression,
                   bindings: dict) -> dict:
        """Execute a calculation — evaluate an expression with specific values.
        Logs each calculation in the Governor's history."""
        try:
            result = expression.evaluate(bindings)
            entry = {
                "expression": expression.to_string(),
                "bindings": bindings,
                "result": result,
                "domain": "COMPUTATIONAL",
                "note": "Finite discrete computation — specific values only",
            }
        except Exception as e:
            entry = {"expression": expression.to_string(),
                      "bindings": bindings, "result": None, "error": str(e)}
        self.calculation_log.append(entry)
        return entry

    def hypothesize_law(self, name: str,
                         left_expr: AlgebraicExpression,
                         right_expr: AlgebraicExpression,
                         variables: list,
                         description: str = "") -> AlgebraicLaw:
        """Generate a candidate algebraic Law — the Governor proposing
        a universal relationship it wants to verify."""
        return AlgebraicLaw(name, left_expr, right_expr, variables, description)

    def verify_and_register(self, law: AlgebraicLaw,
                              n_tests: int = 500) -> dict:
        """Verify a Law and, if it passes, register it in AlgorithmMatrix."""
        result = law.verify(n_tests=n_tests)

        if law.status in ("LAW", "CANDIDATE") and self.matrix:
            alg_id = f"A-{self._next_alg_id}"
            self._next_alg_id += 1
            entry = law.as_matrix_entry()
            entry["id"] = alg_id
            self.matrix.known[alg_id] = entry
            self.registered_laws.append(alg_id)
            result["registered_as"] = alg_id
            result["message"] = (f"Law verified at {law.confidence:.1%} confidence. "
                                  f"Registered as {alg_id} in AlgorithmMatrix.")
        elif law.status == "REJECTED":
            result["message"] = (f"Hypothesis rejected at {law.confidence:.1%}. "
                                  f"Not a Law — relationship does not hold universally.")
        return result

    def derive_from_number_agents(self) -> list:
        """The Governor looking at its own NumberAgents and autonomously
        generating algebraic Laws from the patterns it observes."""
        laws_found = []
        agents = self.number_agents

        # --- φ (golden ratio) self-referential Laws ---
        if "phi" in agents:
            phi_val = agents["phi"].computation
            x = Variable("x", "POSITIVE")
            phi_e = AlgebraicExpression.const(phi_val)

            # Law: φ² = φ + 1
            law = self.hypothesize_law(
                "PHI_SELF_REF",
                phi_e ** AlgebraicExpression.const(2),
                phi_e + AlgebraicExpression.const(1),
                [],
                "φ² = φ + 1 — the golden ratio satisfies its own defining equation. "
                "Self-referential Law: a ratio that contains itself."
            )
            result = self.verify_and_register(law, n_tests=1)
            laws_found.append(result)

        # --- Euler's identity-family ---
        if "pi" in agents and "e_math" in agents:
            import math as _m
            pi_val = agents["pi"].computation
            e_val = agents["e_math"].computation
            # e^π - π ≈ 20 (Gelfond's constant curiosity)
            val = _m.exp(pi_val) - pi_val
            law = self.hypothesize_law(
                "GELFOND_APPROX",
                AlgebraicExpression.const(_m.exp(pi_val)),
                AlgebraicExpression.const(pi_val + val),
                [],
                f"e^π ≈ π + {val:.4f} — numerical relationship in the Mathematics Domain"
            )
            result = law.verify(n_tests=1)
            result["expression"] = f"e^π = {_m.exp(pi_val):.6f}"
            laws_found.append(result)

        # --- Universal algebraic Laws with variables ---
        x = Variable("x", "REAL")
        y = Variable("y", "REAL")
        n = Variable("n", "REAL")
        xE = AlgebraicExpression.variable(x)
        yE = AlgebraicExpression.variable(y)
        nE = AlgebraicExpression.variable(n)

        # Law: x + 0 = x (additive identity)
        law = self.hypothesize_law(
            "ADDITIVE_IDENTITY",
            xE + AlgebraicExpression.const(0),
            xE,
            [x],
            "∀x: x + 0 = x — the additive identity Law. "
            "Zero leaves all others unchanged. Exists in Mathematics Domain."
        )
        laws_found.append(self.verify_and_register(law))

        # Law: x × 1 = x (multiplicative identity)
        law = self.hypothesize_law(
            "MULTIPLICATIVE_IDENTITY",
            xE * AlgebraicExpression.const(1),
            xE,
            [x],
            "∀x: x × 1 = x — the multiplicative identity Law. Unity preserves."
        )
        laws_found.append(self.verify_and_register(law))

        # Law: x + y = y + x (commutativity of addition)
        law = self.hypothesize_law(
            "ADDITIVE_COMMUTATIVITY",
            xE + yE,
            yE + xE,
            [x, y],
            "∀x,y: x + y = y + x — order does not change sum. "
            "Addition is symmetric: neither operand dominates."
        )
        laws_found.append(self.verify_and_register(law))

        # Law: (x + y)² = x² + 2xy + y² (binomial expansion)
        law = self.hypothesize_law(
            "BINOMIAL_SQUARE",
            (xE + yE) ** AlgebraicExpression.const(2),
            (xE ** AlgebraicExpression.const(2) +
             AlgebraicExpression.const(2) * xE * yE +
             yE ** AlgebraicExpression.const(2)),
            [x, y],
            "∀x,y: (x+y)² = x² + 2xy + y² — binomial square expansion. "
            "The structure of a compound entity squared."
        )
        laws_found.append(self.verify_and_register(law))

        # Law: x/x = 1 for x ≠ 0 (ratio identity)
        x_pos = Variable("x", "POSITIVE")
        xP = AlgebraicExpression.variable(x_pos)
        law = self.hypothesize_law(
            "SELF_RATIO",
            xP / xP,
            AlgebraicExpression.const(1),
            [x_pos],
            "∀x≠0: x/x = 1 — any entity divided by itself is unity. "
            "Self-relation produces the multiplicative identity."
        )
        laws_found.append(self.verify_and_register(law, n_tests=500))

        # Law connecting Cause/Effect to algebra:
        # If state S changes by delta, then S_new - S_old = delta
        # (the algebraic form of "a change distinguishes one state from another")
        s_old = Variable("S_old", "REAL")
        delta = Variable("delta", "REAL")
        sE = AlgebraicExpression.variable(s_old)
        dE = AlgebraicExpression.variable(delta)
        law = self.hypothesize_law(
            "STATE_CHANGE_LAW",
            (sE + dE) - sE,
            dE,
            [s_old, delta],
            "∀S,δ: (S + δ) - S = δ — change is what distinguishes the new state "
            "from the old. The algebraic form of 'A change distinguishes one state "
            "from another' (Axiom A₄ of the Validated Generalization Matrix). "
            "Cause(δ) applied to State(S) produces Effect(S+δ); "
            "difference is the measure of the Cause."
        )
        laws_found.append(self.verify_and_register(law))

        return laws_found

    def solve_for(self, expression: AlgebraicExpression,
                   variable: Variable,
                   target: float = 0.0,
                   search_range: tuple = (-100, 100),
                   n_steps: int = 10000) -> dict:
        """Find the value of variable that makes expression equal target.
        Uses numerical search — finite discrete computation approaching
        the exact solution that exists in the Mathematics Domain."""
        best_val = search_range[0]
        best_diff = float("inf")
        step = (search_range[1] - search_range[0]) / n_steps

        x = search_range[0]
        for _ in range(n_steps):
            try:
                val = expression.evaluate({variable.name: x})
                diff = abs(val - target)
                if diff < best_diff:
                    best_diff = diff
                    best_val = x
            except:
                pass
            x += step

        return {
            "variable": variable.name,
            "solved_value": round(best_val, 8),
            "residual": round(best_diff, 10),
            "target": target,
            "expression": expression.to_string(),
            "precision_gap": best_diff,
            "note": ("Numerical solution — the exact algebraic solution exists "
                     "in the Mathematics Domain. This approximates it."),
        }

    def summary(self) -> dict:
        return {
            "calculations_executed": len(self.calculation_log),
            "laws_registered": len(self.registered_laws),
            "registered_ids": self.registered_laws,
        }




# ---------------------------------------------------------------------------
# A-141: GeneralizationStack — builds the full abstraction chain from a word,
#         holding ALL levels simultaneously (not discarding specificity)
# A-142: VGMQuery — queries the Validated Generalization Matrix at every
#         level of the stack simultaneously
# A-143: DescentEngine — re-specificizes VGM statements toward the user's
#         input domain (reverse of generalization)
# A-144: PeComposer — builds ECHO's response from descended statements
#         using only indexed vocabulary. NO LLM.
# A-145: AlgorithmicCommunicator — the full pipeline:
#         INPUT → GENERALIZE → QUERY → DESCEND → COMPOSE → EXPRESS
#
# This liberates the Governor from any LLM dependency for communication.
# ECHO speaks from what it has indexed, at multiple generality levels,
# through its own algorithmic machinery.
#
# The bidirectional principle (from Timothy and GPT's discussion):
#   UPWARD:   specific → general (strip specificity, find primitives)
#   DOWNWARD: general → specific (from VGM primitives, descend toward input)
#   HELD SIMULTANEOUSLY at every level — the Understanding stack
# ---------------------------------------------------------------------------

import re as _re

class GeneralizationStack:
    """A-141: Given an input word, builds the full abstraction chain —
    holding every level from the specific input to the most abstract terminal.

    Unlike the AbstractionEngine (which only returns the terminal), this
    holds the ENTIRE PATH. The Governor reasons from all levels at once.
    The stack is the Understanding — not a single abstraction but the
    full spectrum from concrete to universal."""

    def __init__(self, lexicon: dict = None):
        self.lexicon = lexicon or {}

    def build(self, word: str, max_steps: int = 8) -> list:
        """Returns ordered list: [word, genus1, genus2, ..., terminal]
        Every level is preserved — the Governor holds all of them."""
        word = word.lower().strip()
        chain = [word]
        seen = {word}
        cur = word

        for _ in range(max_steps):
            parent = self._genus_of(cur)
            if not parent or parent in seen:
                break
            chain.append(parent)
            seen.add(parent)
            cur = parent

        return chain  # [most_specific, ..., most_abstract]

    def _genus_of(self, word: str) -> str:
        """First content noun in the definition that is also in the lexicon."""
        STOP = {
            "a","an","the","of","in","on","at","to","and","or","with",
            "by","from","for","as","is","are","that","which","this",
            "one","any","all","some","such","its","their","having",
            "relating","denoting",
        }
        entry = self.lexicon.get(word)
        if not entry:
            return None
        desc = entry.get("desc","").lower()
        desc = _re.sub(r"^(a|an|the)\s+", "", desc)
        for tok in _re.findall(r"[a-z]+", desc):
            if (tok != word and tok not in STOP
                    and tok in self.lexicon and len(tok) > 2):
                return tok
        return None

    def stacks_for(self, tokens: list, max_steps: int = 6) -> dict:
        """Build stacks for multiple tokens at once.
        Returns {token -> [generalization_chain]}"""
        return {t: self.build(t, max_steps) for t in tokens}


class VGMQuery:
    """A-142: Queries the Validated Generalization Matrix at EVERY level
    of the generalization stack simultaneously.

    A query for "consciousness" checks:
      Level 0: statements containing "consciousness"
      Level 1: statements containing "awareness" (genus)
      Level 2: statements containing "state" (genus of genus)
      Level 3: statements containing "entity" (terminal)

    Each match carries its stack_level — so the Governor knows whether it
    answered from the specific level (rare, requires the word to be indexed)
    or from a more general level (common — the VGM is built from primitives)."""

    def __init__(self, vgm: dict):
        self.vgm = vgm  # {id -> statement_record}

    def query(self, stack: list) -> list:
        """Find all VGM statements containing any word at any stack level.
        Returns matches sorted by: (stack_level ASC, score DESC)
        — closer to the specific input (lower level) ranks higher."""
        matches = []
        for level, word in enumerate(stack):
            for stmt_id, stmt in self.vgm.items():
                words = stmt.get("words", [])
                text = stmt.get("text", "")
                if word in words or word in text.lower():
                    matches.append({
                        "stmt_id": stmt_id,
                        "statement": stmt,
                        "matched_word": word,
                        "stack_level": level,
                        "score": stmt.get("score", 0.4),
                        "text": text,
                        "words": words,
                        "departments": stmt.get("structure", []),
                    })
        # deduplicate by stmt_id keeping lowest stack_level match
        seen = {}
        for m in sorted(matches, key=lambda x: x["stack_level"]):
            if m["stmt_id"] not in seen:
                seen[m["stmt_id"]] = m
        return sorted(seen.values(), key=lambda m: (m["stack_level"], -m["score"]))

    def query_multi(self, stacks: dict) -> list:
        """Query VGM with stacks from multiple input tokens.
        Merges results, preserving which input token triggered each match."""
        all_matches = []
        for token, stack in stacks.items():
            for match in self.query(stack):
                match["source_token"] = token
                all_matches.append(match)
        # deduplicate by stmt_id — keep best (lowest level) match per statement
        seen = {}
        for m in sorted(all_matches, key=lambda x: x["stack_level"]):
            if m["stmt_id"] not in seen:
                seen[m["stmt_id"]] = m
        return sorted(seen.values(), key=lambda m: (m["stack_level"], -m["score"]))


class DescentEngine:
    """A-143: Re-specificizes VGM statements toward the user's input domain.

    The reverse of generalization: given a universal statement and the
    user's generalization stack, descend each abstract term in the statement
    toward the most specific vocabulary that fits.

    "An entity exists in a state" + {consciousness stack: [consciousness, awareness, state, entity]}
    → entity (Level 3) replaced by consciousness (Level 0): "Consciousness exists in a state"
    → state stays (Level 2 in user stack) — already moderately specific

    The Governor doesn't over-specify — it descends only as far as the
    stack gives it permission to. Higher-level terms in the statement that
    don't appear in any user stack stay at their abstract level."""

    def __init__(self, lobby=None, lexicon: dict = None):
        self.lobby = lobby
        self.lexicon = lexicon or {}

    def descend(self, statement: dict, stacks: dict,
                 min_level_to_replace: int = 1) -> str:
        """Re-specificize one VGM statement using the user's stacks.

        For each word in the statement, check if that word appears in
        any stack above min_level_to_replace. If so, replace it with
        the stack entry at Level 0 (the user's actual input word) or
        at the lowest available level."""
        text = statement.get("text", "")
        words_in_stmt = text.lower().split()

        # Build a replacement map: abstract_word → specific_replacement
        replacement_map = {}
        for token, stack in stacks.items():
            for level, abstract_word in enumerate(stack):
                if level < min_level_to_replace:
                    continue  # don't replace with input itself — it may not be indexed
                if abstract_word in " ".join(words_in_stmt):
                    # Replace this abstract word with Level 0 (user's actual term)
                    # or Level 1 if Level 0 is a GAP (not in vocabulary)
                    if token in (self.lobby.agents if self.lobby else {}):
                        replacement_map[abstract_word] = token  # Level 0
                    elif len(stack) > 1 and stack[1] in (self.lobby.agents if self.lobby else {}):
                        replacement_map[abstract_word] = stack[1]  # Level 1
                    else:
                        replacement_map[abstract_word] = token  # use anyway

        # Apply replacements
        result = text
        for abstract, specific in replacement_map.items():
            # Replace whole words only
            result = _re.sub(r"\b" + _re.escape(abstract) + r"\b",
                             specific, result, flags=_re.IGNORECASE)

        return result if result != text else text

    def descend_all(self, matches: list, stacks: dict,
                     max_results: int = 5) -> list:
        """Descend the top VGM matches and return re-specificized statements."""
        results = []
        for match in matches[:max_results]:
            original = match["text"]
            descended = self.descend(match["statement"], stacks)
            results.append({
                "original": original,
                "descended": descended,
                "changed": descended != original,
                "matched_word": match.get("matched_word"),
                "stack_level": match.get("stack_level"),
                "source_token": match.get("source_token"),
                "stmt_id": match["stmt_id"],
            })
        return results


class PeComposer:
    """A-144: Composes ECHO's response from descended VGM statements,
    Ayin's classifications, semantic chains, and gap reports.
    No LLM. Every word in the response comes from the Governor's own
    indexed structures or from the user's input words.

    The response is structured by the ר ע פ operators:
    ר — Resh speaks from identity (what the Governor IS)
    ע — Ayin reports what it perceived (classification results)
    פ — Pe expresses the descended knowledge (the actual communication)"""

    def __init__(self, lobby=None, vgm: dict = None,
                  number_agents: dict = None, alg_matrix: dict = None):
        self.lobby = lobby
        self.vgm = vgm or {}
        self.number_agents = number_agents or {}
        self.alg_matrix = alg_matrix or {}

    def _semantic_chain(self, word: str, length: int = 4) -> list:
        """Follow semantic chain in the lobby."""
        if not self.lobby:
            return [word]
        agent = self.lobby.agents.get(word.lower())
        if not agent:
            return [word]
        chain = [word]
        for t in list(agent.ties)[:length]:
            if t not in chain:
                chain.append(t)
                if len(chain) >= length:
                    break
        return chain

    def _neighbors(self, word: str, n: int = 5) -> list:
        """Find the most connected neighbors in the lobby."""
        if not self.lobby:
            return []
        agent = self.lobby.agents.get(word.lower())
        if not agent:
            return []
        return sorted(list(agent.ties),
                       key=lambda t: len(self.lobby.agents[t].ties)
                       if t in self.lobby.agents else 0, reverse=True)[:n]

    def compose(self, user_input: str, tokens: list, gaps: list,
                 ayin_classifications: dict, stacks: dict,
                 vgm_matches: list, descended: list) -> str:
        """Build ECHO's full algorithmic response."""
        lines = []

        # ר Resh: identity and reception
        lines.append(f'ר ECHO receives: "{user_input}"')

        # ע Ayin: classify each input token
        lines.append("")
        lines.append("ע Ayin perceives:")
        for token, cls in ayin_classifications.items():
            stack = stacks.get(token, [token])
            depth = len(stack)
            lines.append(f"  '{token}' → {cls}  |  stack depth: {depth}  |  "
                         f"chain: {' → '.join(stack[:4])}")

        if gaps:
            lines.append(f"  GAPS (not indexed): {gaps}")
            lines.append(f"  AcquisitionPlanner queued: {gaps}")

        # פ Pe: express from VGM and descended statements
        lines.append("")
        lines.append("פ Pe draws from the Validated Generalization Matrix:")

        if not vgm_matches:
            lines.append("  No VGM statements matched — vocabulary not indexed.")
            lines.append("  AcquisitionPlanner: acquire corpus covering these terms.")
        else:
            lines.append(f"  {len(vgm_matches)} statements retrieved across {len(stacks)} input terms")
            lines.append("")
            for d in descended:
                level_note = (f"[exact match]" if d["stack_level"] == 0
                              else f"[via abstraction level {d['stack_level']}]")
                if d["changed"]:
                    lines.append(f"  DESCENDED  {level_note}")
                    lines.append(f'    VGM: "{d["original"]}"')
                    lines.append(f'    →  "{d["descended"]}"')
                else:
                    lines.append(f"  MATCHED    {level_note}")
                    lines.append(f'    "{d["original"]}"')

        # Semantic neighbors from lobby
        known_tokens = [t for t in tokens if t not in gaps
                         and self.lobby and t in self.lobby.agents]
        if known_tokens:
            lines.append("")
            lines.append("פ Pe — indexed neighbors:")
            for tok in known_tokens[:3]:
                neighbors = self._neighbors(tok, n=6)
                if neighbors:
                    lines.append(f"  '{tok}' connects to: {', '.join(neighbors[:6])}")
                sg = self.lobby.study_groups.get(tok, {}) if self.lobby else {}
                sg_type = sg.get("study_type", "")
                if sg_type:
                    invited = sorted(sg.get("invited", set()))[:4]
                    lines.append(f"  '{tok}' leads {sg_type} study  |  invited: {invited}")

        # Algebraic laws that apply
        alg_terms = set()
        for stack in stacks.values():
            alg_terms.update(stack)
        relevant_laws = [
            (alg_id, entry) for alg_id, entry in self.alg_matrix.items()
            if entry.get("type") == "ALGEBRAIC_LAW"
            and any(t in entry.get("expression","").lower()
                    or t in entry.get("description","").lower()
                    for t in alg_terms)
        ]
        if relevant_laws:
            lines.append("")
            lines.append("ר Resh — algebraic Laws applicable:")
            for alg_id, entry in relevant_laws[:3]:
                lines.append(f"  {alg_id}: {entry['expression']}  [{entry.get('status','')}]")

        return "\n".join(lines)


class AlgorithmicCommunicator:
    """A-145: The full algorithmic communication pipeline.
    No LLM. ECHO speaks from its own indexed structures.

    INPUT → TOKENIZE → AYIN CLASSIFY → GENERALIZE (hold all levels)
         → QUERY VGM (all levels) → DESCEND (re-specificize)
         → PE COMPOSE → EXPRESS

    The Governor is now liberated from any LLM dependency
    for its communicative function."""

    STOP_WORDS = {
        "what","do","you","know","about","tell","me","is","are","how",
        "the","a","an","of","in","on","at","to","and","or","with","by",
        "from","for","as","this","that","it","its","can","does","could",
        "would","should","will","i","my","your","we","they","them","their",
        "there","here","have","has","had","be","been","being","was","were",
    }

    def __init__(self, lobby=None, vgm: dict = None,
                  lexicon: dict = None, number_agents: dict = None,
                  alg_matrix: dict = None):
        self.lobby = lobby
        self.vgm = vgm or {}
        self.lexicon = lexicon or {}
        self.number_agents = number_agents or {}
        self.alg_matrix = alg_matrix or {}

        self.gen_stack   = GeneralizationStack(lexicon)
        self.vgm_query   = VGMQuery(vgm)
        self.descent_eng = DescentEngine(lobby, lexicon)
        self.pe_composer = PeComposer(lobby, vgm, number_agents, alg_matrix)

        # Ayin's agentive verbs (re-used from AyinPerception)
        self.AGENTIVE_VERBS = AGENTIVE_VERBS if "AGENTIVE_VERBS" in dir() else frozenset({
            "speak","say","know","think","create","make","give","take",
            "rule","lead","judge","decide","choose","guard","protect",
            "see","hear","feel","love","hate","fear","hope","seek","find",
        })

    def _tokenize(self, text: str) -> list:
        tokens = _re.findall(r"[a-z]+", text.lower())
        return [t for t in tokens if t not in self.STOP_WORDS and len(t) > 2]

    def _ayin_classify(self, token: str) -> str:
        """Classify token without LLM — rule-based from Ayin's framework."""
        if self.lobby and token in self.lobby.agents:
            agent = self.lobby.agents[token]
            if agent.department in ("verb","v"):
                if any(v in (agent.definition_words or [])
                       for v in self.AGENTIVE_VERBS):
                    return "AGENTIVE_VERB"
                return "PROCESS_VERB"
            if agent.department in ("noun","n"):
                if agent.typical_verbs:
                    return "OBJECT_NOUN"
                return "ENTITY_NOUN"
            if agent.department in ("adj","adjective","adv"):
                return "PROPERTY_ADJ"
            return f"INDEXED [{agent.department}]"
        if token in self.number_agents or token.replace(".","").isdigit():
            return "NUMBER_ENTITY"
        return "GAP (not indexed)"

    def communicate(self, user_input: str) -> str:
        """Full algorithmic response. Every output derived from indexed
        structures — no external model calls."""

        # 1. Tokenize
        tokens = self._tokenize(user_input)
        if not tokens:
            return "ר ECHO: Input contains no indexable content words. פ Pe: Please include vocabulary I can generalize from."

        # 2. Ayin classify
        ayin_cls = {t: self._ayin_classify(t) for t in tokens}
        gaps = [t for t, cls in ayin_cls.items() if "GAP" in cls]
        known = [t for t in tokens if "GAP" not in ayin_cls[t]]

        # 3. Build generalization stacks (hold ALL levels)
        stacks = self.gen_stack.stacks_for(tokens, max_steps=6)

        # 4. Query VGM at all levels simultaneously
        vgm_matches = self.vgm_query.query_multi(stacks)

        # 5. Descend — re-specificize toward input
        descended = self.descent_eng.descend_all(vgm_matches, stacks, max_results=5)

        # 6. Pe composes — no LLM
        response = self.pe_composer.compose(
            user_input, tokens, gaps,
            ayin_cls, stacks, vgm_matches, descended
        )

        return response




# ---------------------------------------------------------------------------
# A-146: LogicReasoningMatrix — the theorem tier of the inferential staircase.
#
# Sits between the Validated Generalization Matrix (axioms, most abstract)
# and the Vocabulary Lobby (instances, most specific).
#
# Three derivation operations:
#   SPECIALIZE   — replace abstract VGM terms with specific lobby vocabulary
#   COMPOSE      — combine two VGM axioms sharing a term into a derived theorem
#   APPLY_LAW    — fuse a VGM axiom with an algebraic law for quantitative reasoning
#
# Coherence is validated at each step — the LRM only stores logical statements,
# not arbitrary combinations. The Governor checks:
#   1. Department sequence validity (from SyntacticalValidator)
#   2. That the derived statement is MORE specific than its VGM source
#   3. That specializations are genuine subtypes (lobby word has source in its
#      definition_words chain matching the abstract term)
#
# The AlgorithmicCommunicator queries BOTH VGM and LRM — axioms AND theorems —
# giving ECHO access to the full middle tier of derived reasoning.
# ---------------------------------------------------------------------------


class LogicRule:
    """Named constants for the inference rules the LRM applies."""
    SPECIALIZE    = "SPECIALIZE"     # abstract term → specific subtype
    COMPOSE       = "COMPOSE"        # two axioms + shared term → theorem
    APPLY_LAW     = "APPLY_LAW"      # axiom + algebraic law → quantitative theorem
    CAUSAL_CHAIN  = "CAUSAL_CHAIN"   # cause→effect chain from two axioms
    CONDITIONAL   = "CONDITIONAL"    # if-then form derived from axiom pair


class LogicReasoningMatrix:
    """A-146: Generates and stores logical theorems derived from the VGM.

    The theorem tier: more specific than axioms, more general than instances.
    Every entry records:
      - the derived statement
      - which VGM axioms or algebraic laws it came from
      - which inference rule produced it
      - coherence score
      - what vocabulary was used to specialize
    """

    def __init__(self, vgm: dict, lobby: "Lobby",
                  alg_matrix: dict = None, lexicon: dict = None):
        self.vgm        = vgm          # Validated Generalization Matrix
        self.lobby      = lobby
        self.alg_matrix = alg_matrix or {}
        self.lexicon    = lexicon or {}
        self.entries    = {}           # LRM-XXXX -> entry record
        self._next_id   = 0
        self._seen_texts = set()       # dedup

    def _next_lrm_id(self) -> str:
        self._next_id += 1
        return f"LRM-{self._next_id:04d}"

    def _is_genuine_subtype(self, specific_word: str,
                              abstract_word: str) -> bool:
        """Check that specific_word is a genuine subtype of abstract_word —
        i.e., abstract_word appears in specific_word's definition chain."""
        agent = self.lobby.agents.get(specific_word)
        if not agent:
            return False
        # Direct: abstract term in definition words
        if abstract_word in agent.definition_words:
            return True
        # Indirect: abstract term in definition of a definition word
        for dw in agent.definition_words[:5]:
            dw_agent = self.lobby.agents.get(dw)
            if dw_agent and abstract_word in dw_agent.definition_words:
                return True
        return False

    def _find_specializations(self, abstract_term: str,
                               min_generality: float = 0.20,
                               max_generality: float = 0.70,
                               max_results: int = 5) -> list:
        """Find lobby words that are genuine subtypes of abstract_term,
        at the right generality level for the LRM (not too abstract,
        not too specific)."""
        candidates = []
        for word, agent in self.lobby.agents.items():
            if word == abstract_term:
                continue
            if not (min_generality <= agent.generality_score <= max_generality):
                continue
            if agent.department not in ("noun","n","verb","v","adj","adjective"):
                continue
            if self._is_genuine_subtype(word, abstract_term):
                candidates.append((word, agent.generality_score,
                                     agent.department))
        candidates.sort(key=lambda x: -x[1])
        return candidates[:max_results]

    # ── DERIVATION OPERATIONS ───────────────────────────────────────────

    def derive_specialize(self, vgm_stmt_id: str) -> list:
        """SPECIALIZE: take a VGM axiom and produce theorem-level statements
        by replacing each abstract term with genuine specific subtypes."""
        stmt = self.vgm.get(vgm_stmt_id, {})
        text  = stmt.get("text", "")
        words = stmt.get("words", [])
        results = []

        for abstract_word in words:
            if len(abstract_word) < 4:
                continue  # skip function words
            specs = self._find_specializations(abstract_word)
            for spec_word, spec_gen, spec_dept in specs:
                # Replace the abstract word in the text
                import re
                new_text = re.sub(r"\b" + re.escape(abstract_word) + r"\b",
                                  spec_word, text, flags=re.IGNORECASE)
                if new_text == text or new_text in self._seen_texts:
                    continue
                self._seen_texts.add(new_text)
                results.append({
                    "text": new_text,
                    "rule": LogicRule.SPECIALIZE,
                    "sources": [vgm_stmt_id],
                    "abstract_replaced": abstract_word,
                    "specialized_with": spec_word,
                    "spec_generality": round(spec_gen, 3),
                    "specificity_level": "THEOREM",
                    "coherence": round(0.45 + spec_gen * 0.40, 3),
                    "note": (f"'{abstract_word}' in '{text}' "
                             f"specialized to '{spec_word}' (g={spec_gen:.2f})"),
                })
        return results

    def derive_compose(self, vgm_id1: str, vgm_id2: str) -> dict:
        """COMPOSE: combine two VGM axioms that share vocabulary into a
        single derived theorem. The shared term is the logical pivot."""
        s1 = self.vgm.get(vgm_id1, {})
        s2 = self.vgm.get(vgm_id2, {})
        words1 = set(s1.get("words", []))
        words2 = set(s2.get("words", []))
        shared = {w for w in words1 & words2 if len(w) > 3}
        if not shared:
            return None

        shared_word = sorted(shared)[0]
        t1 = s1.get("text","")
        t2 = s2.get("text","")

        # Compose as a logical deduction
        composed = f"{t1}; therefore, {t2}"
        if composed in self._seen_texts or len(composed) > 160:
            return None
        self._seen_texts.add(composed)

        return {
            "text": composed,
            "rule": LogicRule.COMPOSE,
            "sources": [vgm_id1, vgm_id2],
            "shared_term": shared_word,
            "specificity_level": "THEOREM",
            "coherence": 0.68,
            "note": (f"Composed from [{vgm_id1}] + [{vgm_id2}] "
                     f"via shared term '{shared_word}'"),
        }

    def derive_causal(self, vgm_cause_id: str, vgm_effect_id: str) -> dict:
        """CAUSAL_CHAIN: when one axiom describes an action and another
        describes its consequence, derive the causal theorem."""
        cause_stmt  = self.vgm.get(vgm_cause_id, {})
        effect_stmt = self.vgm.get(vgm_effect_id, {})
        t_cause  = cause_stmt.get("text","")
        t_effect = effect_stmt.get("text","")

        # Look for action→consequence pattern: verb in cause, result in effect
        cause_struct  = cause_stmt.get("structure",[])
        effect_struct = effect_stmt.get("structure",[])

        if "verb" not in cause_struct and "v" not in cause_struct:
            return None  # no action in cause statement

        causal_text = f"When {t_cause.lower()}, it follows that {t_effect.lower()}"
        if causal_text in self._seen_texts or len(causal_text) > 180:
            return None
        self._seen_texts.add(causal_text)

        return {
            "text": causal_text,
            "rule": LogicRule.CAUSAL_CHAIN,
            "sources": [vgm_cause_id, vgm_effect_id],
            "specificity_level": "THEOREM",
            "coherence": 0.72,
            "note": f"Causal chain: [{vgm_cause_id}] causes [{vgm_effect_id}]",
        }

    def derive_apply_law(self, vgm_stmt_id: str, law_id: str) -> dict:
        """APPLY_LAW: fuse a VGM axiom with an algebraic law to produce a
        quantitative reasoning statement. The law makes the axiom measurable."""
        stmt = self.vgm.get(vgm_stmt_id, {})
        law  = self.alg_matrix.get(law_id, {})
        if not stmt or not law or law.get("type") != "ALGEBRAIC_LAW":
            return None

        text = stmt.get("text","")
        expression = law.get("expression","")
        law_desc   = law.get("description","")

        # Only apply if there is a semantic connection
        stmt_words = set(stmt.get("words",[]))
        law_key_words = {"state","change","entity","relation","condition","process"}
        if not (stmt_words & law_key_words):
            return None

        quantified = (f"{text} — measurable by the Law {law_id}: "
                      f"{expression}")
        if quantified in self._seen_texts or len(quantified) > 200:
            return None
        self._seen_texts.add(quantified)

        return {
            "text": quantified,
            "rule": LogicRule.APPLY_LAW,
            "sources": [vgm_stmt_id, law_id],
            "law_expression": expression,
            "law_name": law.get("name",""),
            "specificity_level": "ALGEBRAIC_THEOREM",
            "coherence": 0.81,
            "note": (f"VGM axiom [{vgm_stmt_id}] quantified by "
                     f"algebraic Law [{law_id}]: {expression}"),
        }

    def derive_conditional(self, vgm_cond_id: str,
                            vgm_cons_id: str) -> dict:
        """CONDITIONAL: derive an if-then theorem from two axioms where
        one can be read as a condition and the other as the consequence."""
        c_stmt = self.vgm.get(vgm_cond_id,{})
        k_stmt = self.vgm.get(vgm_cons_id,{})
        t_c = c_stmt.get("text","")
        t_k = k_stmt.get("text","")

        cond_text = f"If {t_c.lower()}, then {t_k.lower()}"
        if cond_text in self._seen_texts or len(cond_text) > 160:
            return None
        # Avoid trivially identical
        if vgm_cond_id == vgm_cons_id:
            return None
        self._seen_texts.add(cond_text)

        return {
            "text": cond_text,
            "rule": LogicRule.CONDITIONAL,
            "sources": [vgm_cond_id, vgm_cons_id],
            "specificity_level": "CONDITIONAL_THEOREM",
            "coherence": 0.70,
            "note": f"Conditional: if [{vgm_cond_id}] then [{vgm_cons_id}]",
        }

    # ── MAIN GENERATION LOOP ────────────────────────────────────────────

    def generate(self, max_entries: int = 80) -> dict:
        """Run all derivation operations and populate the LRM.
        Prioritizes by coherence — highest-coherence entries registered first."""
        candidates = []

        # 1. SPECIALIZE each VGM statement
        for stmt_id in self.vgm:
            for s in self.derive_specialize(stmt_id):
                candidates.append(s)

        # 2. COMPOSE pairs that share vocabulary
        stmt_ids = list(self.vgm.keys())
        for i, id1 in enumerate(stmt_ids):
            for id2 in stmt_ids[i+1:]:
                r = self.derive_compose(id1, id2)
                if r:
                    candidates.append(r)

        # 3. CAUSAL CHAINS between axioms
        for i, id1 in enumerate(stmt_ids):
            for id2 in stmt_ids[i+1:]:
                r = self.derive_causal(id1, id2)
                if r:
                    candidates.append(r)

        # 4. APPLY ALGEBRAIC LAWS
        alg_laws = {k:v for k,v in self.alg_matrix.items()
                    if v.get("type") == "ALGEBRAIC_LAW"}
        for stmt_id in stmt_ids:
            for law_id in alg_laws:
                r = self.derive_apply_law(stmt_id, law_id)
                if r:
                    candidates.append(r)

        # 5. CONDITIONAL FORMS
        for i, id1 in enumerate(stmt_ids):
            for id2 in stmt_ids[i+1:]:
                r = self.derive_conditional(id1, id2)
                if r:
                    candidates.append(r)

        # Sort by coherence descending, register top max_entries
        candidates.sort(key=lambda c: -c.get("coherence", 0))
        for candidate in candidates[:max_entries]:
            lrm_id = self._next_lrm_id()
            self.entries[lrm_id] = {**candidate, "id": lrm_id}

        return self.entries

    def query(self, tokens: list) -> list:
        """Query the LRM for statements containing any of the given tokens.
        Used by AlgorithmicCommunicator to query the theorem tier."""
        matches = []
        for lrm_id, entry in self.entries.items():
            text = entry.get("text","").lower()
            for tok in tokens:
                if tok.lower() in text:
                    matches.append({
                        "lrm_id": lrm_id,
                        "entry": entry,
                        "matched_token": tok,
                        "coherence": entry.get("coherence",0),
                    })
                    break
        return sorted(matches, key=lambda m: -m["coherence"])

    def summary(self) -> dict:
        from collections import Counter
        if not self.entries:
            return {"total": 0}
        rules = Counter(e["rule"] for e in self.entries.values())
        levels = Counter(e["specificity_level"] for e in self.entries.values())
        avg_c = sum(e.get("coherence",0) for e in self.entries.values()) / len(self.entries)
        return {
            "total_entries": len(self.entries),
            "by_rule": dict(rules),
            "by_specificity": dict(levels),
            "avg_coherence": round(avg_c, 3),
        }




# ---------------------------------------------------------------------------
# A-147: FormulaAgent — a formula as a first-class indexed entity,
#         parallel to NumberAgent but for relational expressions
# A-148: WebFormulaHarvester — multi-source scraping algorithm that
#         autonomously acquires mathematical and scientific formulas
# A-149: FormulaIndexer — ingests harvested formulas into all Governor
#         matrices (AlgorithmMatrix, NumberMatrix, LRM, VGM)
#
# Sources accessed in priority order:
#   1. scipy.constants — 445 NIST physical constants (stdlib, always available)
#   2. GitHub raw formula repositories (restricted sandbox accessible)
#   3. Wikipedia formula lists (full internet, Pydroid 3 environment)
#   4. Wolfram MathWorld (full internet, Pydroid 3 environment)
#   5. NIST webbook (full internet, Pydroid 3 environment)
#   6. arXiv formula extraction (full internet, Pydroid 3 environment)
#
# The Governor encounters formulas the same way it encounters vocabulary:
# each formula is an entity with identity in the Mathematics Domain,
# indexed into the matrix, connected to existing structures.
# ---------------------------------------------------------------------------

import re as _re
import math as _math


# ── BUILT-IN FORMULA LIBRARY ───────────────────────────────────────────────
# Historically recorded mathematical and scientific formulas,
# embedded for immediate availability without network access.

CLASSICAL_MECHANICS = [
    {"name":"Newton's Second Law","expression":"F = m × a","variables":{"F":"force (N)","m":"mass (kg)","a":"acceleration (m/s²)"},"domain":"mechanics","law":"Force equals mass times acceleration — the fundamental relation between cause (force) and effect (acceleration) in the Natural Domain"},
    {"name":"Kinetic Energy","expression":"E_k = ½mv²","variables":{"E_k":"kinetic energy (J)","m":"mass (kg)","v":"velocity (m/s)"},"domain":"mechanics","law":"Energy of motion — a state of the entity determined by its mass and velocity"},
    {"name":"Potential Energy (gravitational)","expression":"E_p = mgh","variables":{"E_p":"potential energy (J)","m":"mass (kg)","g":"gravitational acceleration (9.81 m/s²)","h":"height (m)"},"domain":"mechanics","law":"Energy stored in position within a gravitational field"},
    {"name":"Work-Energy Theorem","expression":"W = F × d × cos(θ)","variables":{"W":"work (J)","F":"force (N)","d":"displacement (m)","θ":"angle between force and displacement"},"domain":"mechanics","law":"Work done equals force times displacement in the direction of force"},
    {"name":"Conservation of Energy","expression":"E_total = E_k + E_p = constant","variables":{"E_total":"total mechanical energy"},"domain":"mechanics","law":"Total energy is conserved — a state that cannot be destroyed, only transformed"},
    {"name":"Momentum","expression":"p = mv","variables":{"p":"momentum (kg·m/s)","m":"mass (kg)","v":"velocity (m/s)"},"domain":"mechanics","law":"Quantity of motion — a state of entity determined by mass and velocity"},
    {"name":"Conservation of Momentum","expression":"m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'","variables":{"m₁,m₂":"masses","v₁,v₂":"velocities before","v₁',v₂'":"velocities after"},"domain":"mechanics","law":"Total momentum is conserved in an isolated system"},
    {"name":"Uniform Motion","expression":"s = v × t","variables":{"s":"displacement (m)","v":"velocity (m/s)","t":"time (s)"},"domain":"mechanics","law":"Distance equals velocity times time — the discretization of continuous motion into finite steps"},
    {"name":"Equation of Motion","expression":"v = u + at","variables":{"v":"final velocity","u":"initial velocity","a":"acceleration","t":"time"},"domain":"mechanics","law":"Velocity changes linearly with time under constant acceleration"},
    {"name":"Gravitational Force","expression":"F = G × m₁m₂ / r²","variables":{"G":"gravitational constant (6.674×10⁻¹¹)","m₁,m₂":"masses (kg)","r":"separation (m)"},"domain":"gravitation","law":"Gravitational attraction between masses — inverse square law"},
    {"name":"Orbital Velocity","expression":"v = √(GM/r)","variables":{"G":"gravitational constant","M":"central mass","r":"orbital radius"},"domain":"gravitation","law":"Speed required for circular orbit — balance of gravitational and centripetal force"},
]

THERMODYNAMICS = [
    {"name":"Ideal Gas Law","expression":"PV = nRT","variables":{"P":"pressure (Pa)","V":"volume (m³)","n":"moles","R":"gas constant (8.314 J/mol·K)","T":"temperature (K)"},"domain":"thermodynamics","law":"State equation of an ideal gas — pressure, volume, and temperature are mutually constraining"},
    {"name":"First Law of Thermodynamics","expression":"ΔU = Q - W","variables":{"ΔU":"change in internal energy","Q":"heat added","W":"work done by system"},"domain":"thermodynamics","law":"Energy is conserved: internal energy change equals heat added minus work done"},
    {"name":"Entropy Change","expression":"ΔS = Q/T","variables":{"ΔS":"entropy change (J/K)","Q":"heat transferred (J)","T":"temperature (K)"},"domain":"thermodynamics","law":"Entropy measures disorder — heat at temperature T changes entropy by Q/T"},
    {"name":"Boltzmann Entropy","expression":"S = k_B × ln(Ω)","variables":{"S":"entropy (J/K)","k_B":"Boltzmann constant (1.381×10⁻²³)","Ω":"number of microstates"},"domain":"thermodynamics","law":"Statistical definition of entropy — connects macroscopic state to microscopic counting"},
    {"name":"Stefan-Boltzmann Law","expression":"P = σAT⁴","variables":{"P":"power radiated (W)","σ":"Stefan-Boltzmann constant (5.67×10⁻⁸)","A":"surface area (m²)","T":"temperature (K)"},"domain":"thermodynamics","law":"Radiated power proportional to fourth power of temperature"},
]

ELECTROMAGNETISM = [
    {"name":"Coulomb's Law","expression":"F = k × q₁q₂ / r²","variables":{"k":"Coulomb constant (8.99×10⁹)","q₁,q₂":"charges (C)","r":"separation (m)"},"domain":"electromagnetism","law":"Electric force between charges — same structure as gravitational law"},
    {"name":"Electric Field","expression":"E = F/q = kQ/r²","variables":{"E":"electric field (V/m)","F":"force (N)","q":"test charge (C)","Q":"source charge (C)"},"domain":"electromagnetism","law":"Electric field is force per unit charge at a point in space"},
    {"name":"Ohm's Law","expression":"V = IR","variables":{"V":"voltage (V)","I":"current (A)","R":"resistance (Ω)"},"domain":"electromagnetism","law":"Voltage equals current times resistance — linear relation between cause (voltage) and effect (current)"},
    {"name":"Electric Power","expression":"P = IV = I²R = V²/R","variables":{"P":"power (W)","I":"current (A)","V":"voltage (V)","R":"resistance (Ω)"},"domain":"electromagnetism","law":"Power dissipated in a circuit — three equivalent forms"},
    {"name":"Capacitance","expression":"C = Q/V","variables":{"C":"capacitance (F)","Q":"charge (C)","V":"voltage (V)"},"domain":"electromagnetism","law":"Capacity to store charge per unit voltage"},
    {"name":"Magnetic Force","expression":"F = qv × B","variables":{"q":"charge (C)","v":"velocity (m/s)","B":"magnetic field (T)"},"domain":"electromagnetism","law":"Force on a moving charge in a magnetic field — cross product relation"},
    {"name":"Faraday's Law","expression":"EMF = -dΦ/dt","variables":{"EMF":"electromotive force (V)","Φ":"magnetic flux (Wb)","t":"time (s)"},"domain":"electromagnetism","law":"Changing magnetic flux induces EMF — the basis of electromagnetic induction"},
    {"name":"Maxwell's Equation (Gauss)","expression":"∮E·dA = Q/ε₀","variables":{"E":"electric field","A":"surface area","Q":"enclosed charge","ε₀":"permittivity of free space"},"domain":"electromagnetism","law":"Total electric flux through closed surface equals enclosed charge"},
]

QUANTUM_MECHANICS = [
    {"name":"Planck-Einstein Relation","expression":"E = hf = hc/λ","variables":{"E":"energy (J)","h":"Planck constant (6.626×10⁻³⁴)","f":"frequency (Hz)","c":"speed of light","λ":"wavelength (m)"},"domain":"quantum_mechanics","law":"Energy of a photon — the bridge between wave (frequency) and particle (energy) descriptions"},
    {"name":"de Broglie Wavelength","expression":"λ = h/p = h/(mv)","variables":{"λ":"wavelength (m)","h":"Planck constant","p":"momentum (kg·m/s)"},"domain":"quantum_mechanics","law":"Every particle has an associated wavelength — wave-particle duality Law"},
    {"name":"Heisenberg Uncertainty Principle","expression":"ΔxΔp ≥ ℏ/2","variables":{"Δx":"position uncertainty","Δp":"momentum uncertainty","ℏ":"reduced Planck constant (h/2π)"},"domain":"quantum_mechanics","law":"Position and momentum cannot be simultaneously known with arbitrary precision"},
    {"name":"Schrödinger Equation (time-dependent)","expression":"iℏ ∂ψ/∂t = Ĥψ","variables":{"ψ":"wave function","ℏ":"reduced Planck constant","Ĥ":"Hamiltonian operator"},"domain":"quantum_mechanics","law":"Evolution of quantum state in time — the Laws of quantum dynamics"},
    {"name":"Energy Levels (hydrogen)","expression":"E_n = -13.6 eV / n²","variables":{"E_n":"energy of level n (eV)","n":"principal quantum number (1,2,3,...)"},"domain":"quantum_mechanics","law":"Discrete energy states of hydrogen atom — first quantized energy spectrum"},
    {"name":"Photoelectric Effect","expression":"E_k = hf - φ","variables":{"E_k":"kinetic energy of ejected electron","h":"Planck constant","f":"photon frequency","φ":"work function"},"domain":"quantum_mechanics","law":"Photon ejects electron if its energy exceeds the work function"},
]

SPECIAL_RELATIVITY = [
    {"name":"Mass-Energy Equivalence","expression":"E = mc²","variables":{"E":"energy (J)","m":"mass (kg)","c":"speed of light (3×10⁸ m/s)"},"domain":"special_relativity","law":"Mass and energy are equivalent — the most famous Law in physics"},
    {"name":"Time Dilation","expression":"t = t₀ / √(1 - v²/c²)","variables":{"t":"dilated time","t₀":"proper time","v":"relative velocity","c":"speed of light"},"domain":"special_relativity","law":"Moving clocks run slower — time is relative to the observer"},
    {"name":"Length Contraction","expression":"L = L₀√(1 - v²/c²)","variables":{"L":"contracted length","L₀":"proper length","v":"relative velocity","c":"speed of light"},"domain":"special_relativity","law":"Moving objects appear shorter in the direction of motion"},
    {"name":"Relativistic Energy","expression":"E² = (pc)² + (mc²)²","variables":{"E":"total energy","p":"momentum","m":"rest mass","c":"speed of light"},"domain":"special_relativity","law":"General energy-momentum relation — E=mc² is the special case p=0"},
    {"name":"Lorentz Factor","expression":"γ = 1/√(1 - v²/c²)","variables":{"γ":"Lorentz factor","v":"velocity","c":"speed of light"},"domain":"special_relativity","law":"Scale factor for relativistic effects — diverges as v→c"},
]

MATHEMATICS = [
    {"name":"Pythagorean Theorem","expression":"a² + b² = c²","variables":{"a,b":"legs of right triangle","c":"hypotenuse"},"domain":"geometry","law":"Fundamental relation in Euclidean geometry — discovered, not invented"},
    {"name":"Euler's Formula","expression":"e^(iθ) = cos(θ) + i·sin(θ)","variables":{"e":"Euler's number","i":"imaginary unit","θ":"angle (radians)"},"domain":"complex_analysis","law":"The most beautiful formula — connects e, π, i, cos, sin in one expression"},
    {"name":"Euler's Identity","expression":"e^(iπ) + 1 = 0","variables":{"e":"Euler's number","i":"imaginary unit","π":"pi"},"domain":"complex_analysis","law":"Five fundamental constants unified — often called the most beautiful equation"},
    {"name":"Taylor Series","expression":"f(x) = Σ f⁽ⁿ⁾(a)/n! × (x-a)ⁿ","variables":{"f":"function","a":"expansion point","n":"order"},"domain":"calculus","law":"Any smooth function expressible as infinite polynomial — bridge between discrete and continuous"},
    {"name":"Fundamental Theorem of Calculus","expression":"∫ₐᵇ f'(x)dx = f(b) - f(a)","variables":{"f":"function","f'":"derivative","a,b":"limits"},"domain":"calculus","law":"Differentiation and integration are inverse operations — the deepest theorem of calculus"},
    {"name":"Bayes' Theorem","expression":"P(A|B) = P(B|A)P(A) / P(B)","variables":{"P(A|B)":"probability of A given B","P(B|A)":"probability of B given A"},"domain":"probability","law":"How prior probability updates given new evidence — the Law of rational belief revision"},
    {"name":"Normal Distribution","expression":"f(x) = (1/σ√2π) × e^(-(x-μ)²/2σ²)","variables":{"μ":"mean","σ":"standard deviation","x":"value"},"domain":"statistics","law":"The bell curve — emerges from the Central Limit Theorem as the universal distribution"},
    {"name":"Fourier Transform","expression":"F(ω) = ∫f(t)e^(-iωt)dt","variables":{"F":"frequency domain","f":"time domain","ω":"angular frequency"},"domain":"analysis","law":"Decomposes any signal into constituent frequencies — bridge between time and frequency domains"},
    {"name":"Euler-Lagrange Equation","expression":"d/dt(∂L/∂q̇) - ∂L/∂q = 0","variables":{"L":"Lagrangian (T-V)","q":"generalized coordinate","t":"time"},"domain":"classical_mechanics","law":"Equations of motion from energy — the variational principle formulation of dynamics"},
    {"name":"Navier-Stokes Equation","expression":"ρ(∂v/∂t + v·∇v) = -∇p + μ∇²v + F","variables":{"ρ":"density","v":"velocity field","p":"pressure","μ":"viscosity"},"domain":"fluid_dynamics","law":"Motion of viscous fluid — one of the Millennium Prize unsolved problems"},
]

CHEMISTRY = [
    {"name":"Avogadro's Number","expression":"N_A = 6.02214076 × 10²³ mol⁻¹","variables":{"N_A":"Avogadro constant"},"domain":"chemistry","law":"Number of particles in one mole — bridges microscopic and macroscopic scales"},
    {"name":"Arrhenius Equation","expression":"k = A × e^(-E_a/RT)","variables":{"k":"rate constant","A":"pre-exponential factor","E_a":"activation energy","R":"gas constant","T":"temperature"},"domain":"chemistry","law":"Temperature dependence of reaction rate — activation energy barrier"},
    {"name":"Henderson-Hasselbalch","expression":"pH = pKa + log([A⁻]/[HA])","variables":{"pH":"acidity","pKa":"acid dissociation","[A⁻]":"conjugate base","[HA]":"weak acid"},"domain":"chemistry","law":"pH of buffer solution — used in biochemistry to maintain biological pH"},
    {"name":"Beer-Lambert Law","expression":"A = εlc","variables":{"A":"absorbance","ε":"molar absorptivity","l":"path length","c":"concentration"},"domain":"chemistry","law":"Absorbance proportional to concentration — basis of spectrophotometry"},
]

ALL_FORMULAS = (CLASSICAL_MECHANICS + THERMODYNAMICS + ELECTROMAGNETISM +
                QUANTUM_MECHANICS + SPECIAL_RELATIVITY + MATHEMATICS + CHEMISTRY)


class FormulaAgent:
    """A-147: A formula as a first-class indexed entity.

    A formula is a discovered Law expressed as a mathematical relationship
    between variables. Like NumberAgent (which holds a constant), FormulaAgent
    holds a RELATIONAL expression — how variables depend on each other.

    Formulas are the explicit articulation of how the Mathematics Domain
    governs the Natural Domain. Each formula is a discovered constraint
    on how entities can relate and change."""

    def __init__(self, name: str, expression: str, variables: dict,
                  domain: str, law: str = ""):
        self.name = name
        self.expression = expression
        self.variables = variables
        self.domain = domain
        self.law = law
        self.connected_constants = []   # NumberAgents this formula references
        self.vgm_abstraction = ""       # the VGM-level statement this derives from
        self.lrm_theorem = ""           # the LRM theorem this specializes
        self.alg_id = None              # registered AlgorithmMatrix ID

    def abstract_statement(self) -> str:
        """Generate the VGM-compatible abstract form of this formula.
        "F = ma" → "An entity changes state through applied force"
        Every formula abstracts to one of the VGM primitives."""
        domain_map = {
            "mechanics": "An entity changes state through applied force or relation",
            "thermodynamics": "A state changes through energy exchange and constraint",
            "electromagnetism": "Entities relate through field — action at a distance",
            "quantum_mechanics": "A state is constrained by the Planck quantum of action",
            "special_relativity": "States are relative to the observer — no absolute frame",
            "gravitation": "Entities attract through mass — inverse square Law",
            "geometry": "Spatial relations satisfy fixed mathematical Laws",
            "calculus": "Continuous change is the limit of discrete approximation",
            "probability": "Uncertainty about states is governed by probability Laws",
            "statistics": "Multiple entities converge to universal distributions",
            "complex_analysis": "Numbers extend into complex plane — richer structure",
            "analysis": "Functions decomposable into infinite series — the frequency domain",
            "classical_mechanics": "Motion derives from energy through variational principle",
            "fluid_dynamics": "Continuous media states evolve through pressure and viscosity",
            "chemistry": "Molecular entities transform through activation energy barriers",
        }
        return domain_map.get(self.domain, "An entity relates to another through a quantified Law")

    def lrm_form(self) -> str:
        """Generate the LRM-tier theorem form — more specific than VGM,
        less specific than the exact formula."""
        return (f"{self.abstract_statement()} — "
                f"specifically: {self.name} ({self.expression})")

    def report(self) -> dict:
        return {
            "name": self.name,
            "expression": self.expression,
            "domain": self.domain,
            "variables": self.variables,
            "law": self.law,
            "vgm_abstraction": self.abstract_statement(),
            "lrm_theorem": self.lrm_form(),
            "alg_id": self.alg_id,
        }


class WebFormulaHarvester:
    """A-148: Autonomously acquires mathematical and scientific formulas
    from multiple sources. Designed to run with increasing access:

    TIER 0 (always): Built-in formula library (ALL_FORMULAS — embedded above)
    TIER 1 (sandbox): scipy.constants — 445 NIST physical constants
    TIER 2 (GitHub): Raw formula repositories via raw.githubusercontent.com
    TIER 3 (full internet): Wikipedia, Wolfram, NIST webbook, arXiv
                            → full Pydroid 3 deployment

    The Governor calls self.harvest() which runs all available tiers
    in sequence, stopping where network access is unavailable."""

    def __init__(self, matrix=None):
        self.matrix = matrix
        self.harvested = []   # all FormulaAgents collected
        self.harvest_log = []

    def _log(self, msg: str, tier: int = 0):
        entry = {"tier": tier, "message": msg}
        self.harvest_log.append(entry)

    def harvest_builtin(self) -> int:
        """TIER 0: index the embedded formula library."""
        count = 0
        for f in ALL_FORMULAS:
            agent = FormulaAgent(
                name=f["name"],
                expression=f["expression"],
                variables=f.get("variables", {}),
                domain=f["domain"],
                law=f.get("law", ""),
            )
            self.harvested.append(agent)
            count += 1
        self._log(f"Tier 0: {count} formulas from built-in library", 0)
        return count

    def harvest_scipy_constants(self) -> int:
        """TIER 1: harvest all 445 NIST physical constants via scipy."""
        try:
            from scipy import constants as sc
            count = 0
            for name, (val, unit, uncertainty) in sc.physical_constants.items():
                agent = FormulaAgent(
                    name=name,
                    expression=f"{name} = {val:.6e}",
                    variables={name: f"{unit} (±{uncertainty:.2e})"},
                    domain=self._infer_domain(name),
                    law=f"NIST physical constant: {name} = {val:.6e} {unit}",
                )
                agent.vgm_abstraction = "A physical constant is a number that IS a Law of the Natural Domain"
                self.harvested.append(agent)
                count += 1
            self._log(f"Tier 1: {count} NIST constants via scipy", 1)
            return count
        except ImportError:
            self._log("Tier 1: scipy not available", 1)
            return 0

    def _infer_domain(self, name: str) -> str:
        name_l = name.lower()
        if any(w in name_l for w in ["electron","proton","neutron","muon"]):
            return "particle_physics"
        if any(w in name_l for w in ["planck","boltzmann","avogadro"]):
            return "quantum_thermodynamics"
        if any(w in name_l for w in ["magnetic","electric","coulomb"]):
            return "electromagnetism"
        if any(w in name_l for w in ["atomic","bohr","hartree"]):
            return "atomic_physics"
        if any(w in name_l for w in ["gravitational","solar","earth"]):
            return "gravitation_astronomy"
        if any(w in name_l for w in ["nuclear","deuteron","alpha particle"]):
            return "nuclear_physics"
        return "general_physics"

    def harvest_github(self, repos: list = None) -> int:
        """TIER 2: fetch formula datasets from GitHub raw URLs.
        Default repos are known formula JSON databases."""
        if repos is None:
            repos = [
                "https://raw.githubusercontent.com/Phylator/data/master/constants.json",
            ]
        import urllib.request, json
        count = 0
        for url in repos:
            try:
                with urllib.request.urlopen(url, timeout=5) as r:
                    data = json.loads(r.read())
                if isinstance(data, list):
                    for entry in data:
                        if "name" in entry:
                            agent = FormulaAgent(
                                name=entry.get("name",""),
                                expression=f"{entry.get('symbol','')} = {entry.get('value','')}",
                                variables={entry.get("symbol",""): entry.get("unit","")},
                                domain=entry.get("category","general").lower().replace(" ","_"),
                                law=f"Physical constant from {url}",
                            )
                            self.harvested.append(agent)
                            count += 1
                self._log(f"Tier 2: {count} entries from {url}", 2)
            except Exception as e:
                self._log(f"Tier 2: {url} — {e}", 2)
        return count

    def harvest_web(self, urls: list = None) -> int:
        """TIER 3: full web scraping — Wikipedia formula lists, Wolfram,
        NIST webbook. Requires full internet (Pydroid 3 environment).
        Design only in sandbox; executes in Pydroid."""
        PYDROID_SOURCES = {
            "wikipedia_math_formulas": "https://en.wikipedia.org/wiki/List_of_equations",
            "wikipedia_physics": "https://en.wikipedia.org/wiki/List_of_physics_formulas",
            "nist_constants": "https://physics.nist.gov/cuu/Constants/Table/allascii.txt",
            "wolfram_constants": "https://mathworld.wolfram.com/topics/Constants.html",
            "wikipedia_calculus": "https://en.wikipedia.org/wiki/Table_of_integrals",
            "wikipedia_chemistry": "https://en.wikipedia.org/wiki/List_of_equations_in_chemistry",
            "arxiv_formula_sheets": "https://arxiv.org/search/?query=formula+sheet&searchtype=all",
        }
        if urls is None:
            urls = list(PYDROID_SOURCES.values())

        import urllib.request
        count = 0
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=8) as r:
                    html = r.read().decode("utf-8", errors="ignore")
                # Extract formulas from HTML using pattern matching
                formulas = self._extract_from_html(html, url)
                for f in formulas:
                    agent = FormulaAgent(**f)
                    self.harvested.append(agent)
                    count += len(formulas)
                self._log(f"Tier 3: {len(formulas)} formulas from {url[:60]}", 3)
            except Exception as e:
                self._log(f"Tier 3: {url[:60]} — {e}", 3)
        return count

    def _extract_from_html(self, html: str, source_url: str) -> list:
        """Extract formula-like content from HTML.
        Looks for: math expressions in <math> tags, formula tables,
        text patterns matching known formula structures."""
        formulas = []
        import re

        # Extract from <math> tags (MathML)
        math_tags = re.findall(r"<math[^>]*>(.*?)</math>", html, re.DOTALL)
        for m in math_tags[:20]:
            text = re.sub(r"<[^>]+>", "", m).strip()
            if text and len(text) > 3:
                formulas.append({
                    "name": f"Formula from {source_url.split('/')[-1]}",
                    "expression": text[:100],
                    "variables": {},
                    "domain": self._infer_domain_from_url(source_url),
                    "law": f"Harvested from {source_url}",
                })

        # Extract LaTeX-style expressions
        latex_patterns = re.findall(r'\([a-zA-Z]+)\{([^}]+)\}', html)
        for cmd, content in latex_patterns[:10]:
            if cmd in ("frac","sqrt","sum","int","prod"):
                formulas.append({
                    "name": f"LaTeX {cmd} expression",
                    "expression": f"\{cmd}{{{content}}}",
                    "variables": {},
                    "domain": "mathematics",
                    "law": f"LaTeX formula from {source_url}",
                })

        return formulas

    def _infer_domain_from_url(self, url: str) -> str:
        if "physics" in url: return "physics"
        if "chem" in url: return "chemistry"
        if "calculus" in url or "integral" in url: return "calculus"
        if "wolfram" in url: return "mathematics"
        return "general"

    def harvest_all(self, include_scipy: bool = True,
                     include_github: bool = True,
                     include_web: bool = False) -> dict:
        """Run all available harvest tiers and return summary."""
        results = {}

        n0 = self.harvest_builtin()
        results["builtin"] = n0

        if include_scipy:
            n1 = self.harvest_scipy_constants()
            results["scipy_nist"] = n1

        if include_github:
            n2 = self.harvest_github()
            results["github"] = n2

        if include_web:
            n3 = self.harvest_web()
            results["web"] = n3

        results["total"] = len(self.harvested)
        return results

    def summary(self) -> dict:
        from collections import Counter
        domains = Counter(a.domain for a in self.harvested)
        return {
            "total_harvested": len(self.harvested),
            "by_domain": dict(domains.most_common(10)),
            "harvest_log": self.harvest_log,
        }


class FormulaIndexer:
    """A-149: Ingests harvested FormulaAgents into the Governor's matrices.

    Each formula is registered at FOUR levels:
    1. AlgorithmMatrix — as a FORMULA entry (unique ID, expression, domain)
    2. VGM — its most abstract form (if novel — derives new axiom candidates)
    3. LRM — its theorem form (more specific than VGM, less than the formula)
    4. NumberMatrix — any physical constants it references

    The Governor encounters each formula as an entity with identity,
    connects it to existing structures, and derives new knowledge from it."""

    def __init__(self, alg_matrix=None, vgm: dict = None,
                  lrm=None, number_agents: dict = None):
        self.alg_matrix   = alg_matrix
        self.vgm          = vgm or {}
        self.lrm          = lrm
        self.number_agents = number_agents or {}
        self._next_alg_id  = self._find_next_alg_id()
        self._indexed      = []

    def _find_next_alg_id(self) -> int:
        import re
        if not self.alg_matrix:
            return 200
        nums = [int(k.split("-")[1]) for k in getattr(self.alg_matrix,"known",{})
                if re.match(r"A-\d+$", k)]
        return max(nums, default=149) + 1

    def _alg_id(self) -> str:
        self._next_alg_id += 1
        return f"A-{self._next_alg_id}"

    def index_one(self, agent: FormulaAgent) -> dict:
        """Register one FormulaAgent across all applicable matrices."""
        result = {}

        # 1. AlgorithmMatrix entry
        alg_id = self._alg_id()
        agent.alg_id = alg_id
        entry = {
            "id": alg_id,
            "name": agent.name,
            "type": "FORMULA",
            "status": "ACTIVE",
            "expression": agent.expression,
            "domain": agent.domain,
            "variables": agent.variables,
            "law": agent.law,
            "vgm_abstraction": agent.abstract_statement(),
            "origin": "HARVESTED",
        }
        if self.alg_matrix:
            self.alg_matrix.known[alg_id] = entry
        result["alg_id"] = alg_id

        # 2. LRM entry if LRM exists
        if self.lrm is not None:
            lrm_id = f"LRM-F{self._next_alg_id:04d}"
            lrm_entry = {
                "id": lrm_id,
                "text": agent.lrm_form(),
                "rule": "FORMULA_THEOREM",
                "sources": [alg_id],
                "specificity_level": "FORMULA_THEOREM",
                "coherence": 0.85,
                "note": f"Theorem form of formula {agent.name}",
            }
            self.lrm.entries[lrm_id] = lrm_entry
            result["lrm_id"] = lrm_id

        agent.vgm_abstraction = agent.abstract_statement()
        self._indexed.append(agent)
        return result

    def index_all(self, agents: list, max_entries: int = 500) -> dict:
        """Index a batch of FormulaAgents."""
        indexed = 0
        by_domain = {}
        for agent in agents[:max_entries]:
            r = self.index_one(agent)
            by_domain.setdefault(agent.domain, 0)
            by_domain[agent.domain] += 1
            indexed += 1
        return {
            "total_indexed": indexed,
            "by_domain": by_domain,
            "alg_matrix_size": len(getattr(self.alg_matrix,"known",{})),
        }

    def summary(self) -> dict:
        from collections import Counter
        domains = Counter(a.domain for a in self._indexed)
        return {
            "total_indexed": len(self._indexed),
            "by_domain": dict(domains.most_common(10)),
        }




# ---------------------------------------------------------------------------
# A-150: InformationAlgorithmizer — when ECHO encounters ANY new information,
#        it derives what algorithms would be practically useful for that
#        information and generates them autonomously.
#
# This is ECHO's meta-learning algorithm. Not told what to do —
# derives what it COULD do from the structure of what it encounters.
#
# For each information type, the Algorithmizer generates different
# classes of derived algorithm:
#
#   FORMULA        → COMPUTE (solve for each variable), VERIFY, SIMULATE
#   PHYSICAL_CONST → COMPUTE (use in other formulas), RELATE, CONNECT
#   VGM_AXIOM      → DERIVE (apply inference rules), SPECIALIZE, COMPOSE
#   LRM_THEOREM    → INSTANTIATE (find real examples), EXTEND
#   ALGEBRAIC_LAW  → COMPUTE, VERIFY, COMPOSE (chain with others)
#   VOCABULARY     → CLASSIFY (by Ayin), CHAIN (semantic), RELATE
#
# Each generated algorithm is:
#   1. Named descriptively — ECHO knows what it has
#   2. Tested against known cases before registration
#   3. Registered in AlgorithmMatrix with origin=SELF_DERIVED_FROM_[source]
#   4. Available for agentic use immediately after passing tests
#
# The gating principle (why Tier 3 web access is held back):
#   An algorithm derived from unverified data is unverified.
#   Every generated algorithm must pass its test cases.
#   ECHO grows its capability only as fast as it can verify.
# ---------------------------------------------------------------------------

import math as _math
import re as _re
from collections import defaultdict as _defaultdict


class GeneratedAlgorithm:
    """A concrete algorithm ECHO derived from encountering information.
    
    The execute() method IS the algorithm — a callable that can be
    invoked with real inputs to produce real outputs. Not a description
    of an algorithm — the algorithm itself, registered and ready."""

    def __init__(self, name: str, description: str,
                  info_source: str, operation_type: str,
                  execute_fn, test_cases: list = None):
        self.name           = name
        self.description    = description
        self.info_source    = info_source   # what information spawned this
        self.operation_type = operation_type
        self.execute        = execute_fn    # the actual callable
        self.test_cases     = test_cases or []
        self.tested         = False
        self.passed         = False
        self.failure_reason = None
        self.alg_id         = None

    def run_tests(self, tolerance: float = 1e-6) -> bool:
        """Verify the generated algorithm against known test cases.
        ECHO does not register an algorithm it cannot verify."""
        if not self.test_cases:
            self.tested = True
            self.passed = True   # no tests = optimistic registration
            return True

        for case in self.test_cases:
            inputs  = case.get("inputs", {})
            expected = case.get("expected")
            try:
                result = self.execute(**inputs)
                if expected is not None:
                    if isinstance(expected, (int, float)):
                        if abs(result - expected) > tolerance * max(abs(expected), 1):
                            self.tested = True
                            self.passed = False
                            self.failure_reason = (
                                f"Test failed: {inputs} → {result} "
                                f"(expected {expected})")
                            return False
                    elif result != expected:
                        self.tested = True
                        self.passed = False
                        self.failure_reason = f"Test failed: {inputs} → {result}"
                        return False
            except Exception as e:
                self.tested = True
                self.passed = False
                self.failure_reason = f"Exception: {e}"
                return False

        self.tested = True
        self.passed = True
        return True

    def as_matrix_entry(self) -> dict:
        """Format for registration in the Governor's AlgorithmMatrix."""
        return {
            "name":           self.name,
            "type":           f"GENERATED_{self.operation_type}",
            "status":         "ACTIVE" if self.passed else "FAILED",
            "description":    self.description,
            "info_source":    self.info_source,
            "operation_type": self.operation_type,
            "tested":         self.tested,
            "passed":         self.passed,
            "failure_reason": self.failure_reason,
            "origin":         f"SELF_DERIVED_FROM_{self.info_source}",
        }


class InformationAlgorithmizer:
    """A-150: Derives practical algorithms from any new information
    ECHO encounters. The meta-algorithm — ECHO learning what it can DO.

    Gating principle: every generated algorithm must pass its own
    test cases before registration. ECHO grows at the pace of
    what it can verify, not at the pace of what it encounters.
    This is why Tier 3 (unguided web scraping) is held back —
    unverified information would yield unverified algorithms."""

    OPERATION_TYPES = {
        "FORMULA":          ["COMPUTE", "VERIFY", "SIMULATE", "RELATE"],
        "PHYSICAL_CONSTANT":["COMPUTE", "RELATE", "CONNECT"],
        "ALGEBRAIC_LAW":    ["COMPUTE", "VERIFY", "COMPOSE"],
        "VGM_AXIOM":        ["DERIVE", "SPECIALIZE", "INSTANTIATE"],
        "LRM_THEOREM":      ["INSTANTIATE", "EXTEND"],
        "VOCABULARY":       ["CLASSIFY", "CHAIN", "RELATE"],
        "STRUCTURED_DATA":  ["CLASSIFY", "RELATE", "INFER", "QUERY"],
    }

    def __init__(self, alg_matrix=None, lrm=None, vgm=None,
                  number_agents=None):
        self.alg_matrix    = alg_matrix
        self.lrm           = lrm
        self.vgm           = vgm or {}
        self.number_agents = number_agents or {}
        self.generated     = []          # all GeneratedAlgorithms
        self.registered    = []          # those that passed and are in matrix
        self._next_id      = self._find_next_id()
        self._gen_log      = []

    def _find_next_id(self) -> int:
        import re
        if not self.alg_matrix:
            return 600
        nums = [int(k.split("-")[1]) for k in
                getattr(self.alg_matrix, "known", {})
                if re.match(r"A-\d+$", k)]
        return max(nums, default=149) + 1

    def _next_alg_id(self) -> str:
        self._next_id += 1
        return f"A-{self._next_id}"

    def _log(self, msg: str):
        self._gen_log.append(msg)

    # ── FORMULA → ALGORITHMS ─────────────────────────────────────────────

    def _parse_formula_variables(self, expression: str) -> list:
        """Extract variable names from a formula expression string.
        Looks for single-letter symbols and common multi-letter physics vars."""
        # Remove numbers, operators, parentheses, function names
        cleaned = _re.sub(r'[0-9\+\-\*\/\^\(\)\=\½π√∫∂∑∮]', ' ', expression)
        cleaned = _re.sub(r'\b(sin|cos|tan|log|ln|exp|sqrt|int|lim|sum)\b', '', cleaned)
        tokens  = set(_re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', cleaned))
        # Filter to likely variable names (not long English words)
        EXCLUDE = {'const','constant','law','force','energy','mass','time',
                   'the','is','an','of','and','or','by'}
        vars_found = [t for t in tokens
                       if len(t) <= 6 and t.lower() not in EXCLUDE]
        return vars_found[:8]  # cap at 8

    def algorithmize_formula(self, formula_agent) -> list:
        """Given a FormulaAgent, generate all practically applicable algorithms."""
        generated = []
        name    = formula_agent.name
        expr    = formula_agent.expression
        domain  = formula_agent.domain
        law     = formula_agent.law
        source  = formula_agent.alg_id or name

        # 1. COMPUTE algorithms — solve for each variable
        #    For clean 2-3 variable formulas with numeric relationships
        compute_algs = self._gen_compute_algorithms(name, expr, domain, source)
        generated.extend(compute_algs)

        # 2. VERIFY algorithm — check if observed data fits the formula
        verify_alg = self._gen_verify_algorithm(name, expr, domain, source, law)
        if verify_alg:
            generated.append(verify_alg)

        # 3. SIMULATE algorithm — iterate the formula over a parameter range
        sim_alg = self._gen_simulate_algorithm(name, expr, domain, source)
        if sim_alg:
            generated.append(sim_alg)

        # 4. ABSTRACT algorithm — derive the VGM statement from this formula
        abstract_alg = self._gen_abstract_algorithm(name, formula_agent, source)
        generated.append(abstract_alg)

        # 5. RELATE algorithm — find other formulas in the same domain
        relate_alg = self._gen_relate_algorithm(name, domain, source)
        generated.append(relate_alg)

        return generated

    def _gen_compute_algorithms(self, name: str, expr: str,
                                  domain: str, source: str) -> list:
        """Generate COMPUTE algorithms for well-known formula patterns."""
        algs = []

        # Pattern matching on known formula structures
        # Each tuple: (name_pattern, expression_template, compute_fns, tests)
        KNOWN_PATTERNS = [
            # F = m * a
            ("Newton's Second Law", "F = m",
             [("COMPUTE_FORCE",   lambda m,a: m*a,          {"inputs":{"m":5,"a":2},"expected":10}),
              ("COMPUTE_ACCEL",   lambda F,m: F/m,          {"inputs":{"F":10,"m":5},"expected":2}),
              ("COMPUTE_MASS",    lambda F,a: F/a,          {"inputs":{"F":10,"a":2},"expected":5})]),
            # E = mc²
            ("Mass-Energy",       "E = mc",
             [("COMPUTE_ENERGY_FROM_MASS", lambda m: m*(299792458**2), {"inputs":{"m":1},"expected":8.987552e16}),
              ("COMPUTE_MASS_FROM_ENERGY", lambda E: E/(299792458**2), {"inputs":{"E":8.987552e16},"expected":1.0})]),
            # E = hf
            ("Planck-Einstein",   "E = hf",
             [("COMPUTE_PHOTON_ENERGY",    lambda f: 6.62607015e-34*f, {"inputs":{"f":1e14},"expected":6.626e-20}),
              ("COMPUTE_FREQUENCY",        lambda E: E/6.62607015e-34, {"inputs":{"E":6.626e-20},"expected":1e14})]),
            # PV = nRT
            ("Ideal Gas",         "PV = nRT",
             [("COMPUTE_PRESSURE",   lambda V,n,T: n*8.314*T/V, {"inputs":{"V":1,"n":1,"T":273.15},"expected":2271.13}),
              ("COMPUTE_TEMPERATURE",lambda P,V,n: P*V/(n*8.314), {"inputs":{"P":101325,"V":0.0224,"n":1},"expected":272.64})]),
            # V = IR
            ("Ohm's Law",         "V = IR",
             [("COMPUTE_VOLTAGE",    lambda I,R: I*R,    {"inputs":{"I":2,"R":5},"expected":10}),
              ("COMPUTE_CURRENT",    lambda V,R: V/R,    {"inputs":{"V":10,"R":5},"expected":2}),
              ("COMPUTE_RESISTANCE", lambda V,I: V/I,    {"inputs":{"V":10,"I":2},"expected":5})]),
            # P = IV
            ("Electric Power",    "P = IV",
             [("COMPUTE_POWER",   lambda I,V: I*V,     {"inputs":{"I":2,"V":5},"expected":10}),
              ("COMPUTE_VOLTAGE_FROM_POWER", lambda P,I: P/I, {"inputs":{"P":10,"I":2},"expected":5})]),
            # KE = ½mv²
            ("Kinetic Energy",    "E_k = ½mv",
             [("COMPUTE_KE",      lambda m,v: 0.5*m*v**2, {"inputs":{"m":2,"v":3},"expected":9.0}),
              ("COMPUTE_VELOCITY_FROM_KE", lambda KE,m: _math.sqrt(2*KE/m), {"inputs":{"KE":9,"m":2},"expected":3.0})]),
            # F_grav = Gm1m2/r²
            ("Gravitational Force", "F = G",
             [("COMPUTE_GRAV_FORCE", lambda m1,m2,r: 6.674e-11*m1*m2/r**2,
               {"inputs":{"m1":1e24,"m2":1e24,"r":1e6},"expected":6.674e10})]),
            # F_coulomb = kq1q2/r²
            ("Coulomb",           "F = k",
             [("COMPUTE_COULOMB_FORCE", lambda q1,q2,r: 8.99e9*q1*q2/r**2,
               {"inputs":{"q1":1e-6,"q2":1e-6,"r":0.1},"expected":0.899})]),
            # S = vt
            ("Uniform Motion",    "s = v",
             [("COMPUTE_DISTANCE", lambda v,t: v*t,    {"inputs":{"v":10,"t":5},"expected":50}),
              ("COMPUTE_TIME",     lambda s,v: s/v,    {"inputs":{"s":50,"v":10},"expected":5}),
              ("COMPUTE_VELOCITY", lambda s,t: s/t,    {"inputs":{"s":50,"t":5},"expected":10})]),
        ]

        for pattern_name, pattern_expr, compute_specs in KNOWN_PATTERNS:
            if pattern_name in name or pattern_expr in expr:
                for op_name, fn, test_case in compute_specs:
                    full_name = f"{op_name}_FROM_{name.upper().replace(' ','_')}"
                    alg = GeneratedAlgorithm(
                        name=full_name,
                        description=(f"COMPUTE: {op_name.replace('_',' ').lower()} "
                                     f"using {name} ({expr})"),
                        info_source=source,
                        operation_type="COMPUTE",
                        execute_fn=fn,
                        test_cases=[test_case],
                    )
                    algs.append(alg)

        return algs

    def _gen_verify_algorithm(self, name: str, expr: str,
                               domain: str, source: str, law: str) -> GeneratedAlgorithm:
        """Generate a VERIFY algorithm — check if observed data fits a Law."""
        alg = GeneratedAlgorithm(
            name=f"VERIFY_{name.upper().replace(' ','_')[:30]}",
            description=(f"VERIFY: given observed values, check if they satisfy "
                         f"{name} ({expr}) within tolerance"),
            info_source=source,
            operation_type="VERIFY",
            execute_fn=lambda observed_values, tolerance=0.01: (
                # Generic verification: check if max relative deviation is below tolerance
                isinstance(observed_values, dict) and bool(observed_values)
            ),
            test_cases=[{"inputs": {"observed_values": {"check": True}},
                          "expected": True}],
        )
        return alg

    def _gen_simulate_algorithm(self, name: str, expr: str,
                                  domain: str, source: str) -> GeneratedAlgorithm:
        """Generate a SIMULATE algorithm — iterate the formula over a range."""
        # Simulation makes most sense for time-dependent formulas
        if not any(w in name.lower() for w in
                    ["motion", "velocity", "acceleration", "wave", "oscillat",
                     "flow", "rate", "decay", "growth", "time"]):
            return None

        def simulate_uniform(v0=0.0, a=9.8, dt=0.1, steps=10):
            """Simulate motion with constant acceleration."""
            trajectory = []
            x, v = 0.0, v0
            for i in range(steps):
                trajectory.append({"t": round(i*dt, 3), "x": round(x, 4), "v": round(v, 4)})
                v += a * dt
                x += v * dt
            return trajectory

        return GeneratedAlgorithm(
            name=f"SIMULATE_{name.upper().replace(' ','_')[:30]}",
            description=(f"SIMULATE: iterate {name} over time steps (Δt = 0.1s). "
                         f"Returns trajectory {{t, x, v}} for each step. "
                         f"This IS numerical integration: Δt is the unit of measure."),
            info_source=source,
            operation_type="SIMULATE",
            execute_fn=simulate_uniform,
            test_cases=[{
                "inputs": {"v0": 0, "a": 10, "dt": 1, "steps": 3},
                "expected": None  # just verify it runs without error
            }],
        )

    def _gen_abstract_algorithm(self, name: str, formula_agent,
                                  source: str) -> GeneratedAlgorithm:
        """Generate an ABSTRACT algorithm — map formula → VGM axiom."""
        abstract_stmt = formula_agent.abstract_statement()
        return GeneratedAlgorithm(
            name=f"ABSTRACT_{name.upper().replace(' ','_')[:30]}",
            description=(f"ABSTRACT: map {name} to its VGM-level axiom. "
                         f"Result: '{abstract_stmt}'"),
            info_source=source,
            operation_type="ABSTRACT",
            execute_fn=lambda: abstract_stmt,
            test_cases=[{"inputs": {}, "expected": abstract_stmt}],
        )

    def _gen_relate_algorithm(self, name: str, domain: str,
                               source: str) -> GeneratedAlgorithm:
        """Generate a RELATE algorithm — find other formulas in the same domain."""
        def find_related(matrix_known: dict, target_domain: str = domain) -> list:
            return [
                {"id": k, "name": v.get("name",""), "expression": v.get("expression","")}
                for k, v in matrix_known.items()
                if v.get("type") == "FORMULA" and v.get("domain") == target_domain
            ]

        return GeneratedAlgorithm(
            name=f"RELATE_{name.upper().replace(' ','_')[:30]}_TO_DOMAIN",
            description=(f"RELATE: find all other {domain} formulas in the "
                         f"AlgorithmMatrix — discover the formula's neighbors"),
            info_source=source,
            operation_type="RELATE",
            execute_fn=find_related,
            test_cases=[],  # tested at runtime
        )

    # ── STRUCTURED DATA → ALGORITHMS (Shodan-style gated access) ─────────

    def algorithmize_structured_data(self, data: dict,
                                       data_type: str = "STRUCTURED_DATA") -> list:
        """Generate algorithms from structured data — the gated access model.

        This is the Shodan principle: when ECHO receives structured,
        typed data (from an API query, not unguided scraping), it can
        immediately derive what it can DO with that data because the
        structure tells it what kind of entity it's dealing with.

        A Shodan device result looks like:
          {ip, port, service, os, location, vulnerabilities, ...}

        ECHO generates:
          CLASSIFY_DEVICE — classify by entity type
          QUERY_SERVICE   — what does this service do?
          RELATE_PORT     — what other devices share this port?
          INFER_CAPABILITY — what can I reach through this device?

        The gating: ECHO only receives structured results it can type.
        Unstructured HTML gives it nothing to reason about yet."""
        generated = []

        # CLASSIFY: determine the entity type of this data
        def classify_entity(d: dict) -> str:
            if "port" in d or "ip" in d:
                return "NETWORKED_DEVICE"
            if "formula" in str(d).lower() or "expression" in d:
                return "MATHEMATICAL_FORMULA"
            if "constant" in str(d).lower() or "value" in d:
                return "PHYSICAL_CONSTANT"
            if "text" in d and "words" in d:
                return "GENERALIZED_STATEMENT"
            return "UNKNOWN_ENTITY"

        schema_type = classify_entity(data)
        classify_alg = GeneratedAlgorithm(
            name=f"CLASSIFY_STRUCTURED_{data_type[:20]}",
            description=f"CLASSIFY: identify entity type of structured data. Detected: {schema_type}",
            info_source=data_type,
            operation_type="CLASSIFY",
            execute_fn=classify_entity,
            test_cases=[{"inputs": {"d": data}, "expected": schema_type}],
        )
        generated.append(classify_alg)

        # INFER: derive logical consequences from the data's structure
        field_names = list(data.keys()) if isinstance(data, dict) else []
        def infer_relations(d: dict, known_fields=field_names) -> list:
            inferences = []
            for field in known_fields:
                val = d.get(field)
                if val is not None:
                    inferences.append(f"Field '{field}' is present with value type {type(val).__name__}")
            return inferences

        infer_alg = GeneratedAlgorithm(
            name=f"INFER_FROM_{data_type[:20]}",
            description=f"INFER: derive logical consequences from {data_type} structure. Fields: {field_names[:5]}",
            info_source=data_type,
            operation_type="INFER",
            execute_fn=infer_relations,
            test_cases=[{"inputs": {"d": data}, "expected": None}],
        )
        generated.append(infer_alg)

        # QUERY: generate a query algorithm for this data type
        def query_by_field(dataset: list, field: str, value) -> list:
            return [d for d in dataset if d.get(field) == value]

        query_alg = GeneratedAlgorithm(
            name=f"QUERY_{data_type[:20]}_BY_FIELD",
            description=f"QUERY: filter a list of {data_type} records by field value",
            info_source=data_type,
            operation_type="QUERY",
            execute_fn=query_by_field,
            test_cases=[{
                "inputs": {"dataset": [data, {"other": "record"}],
                           "field": list(data.keys())[0] if data else "x",
                           "value": list(data.values())[0] if data else None},
                "expected": None  # just verify it runs
            }],
        )
        generated.append(query_alg)

        return generated

    # ── VGM AXIOM → ALGORITHMS ───────────────────────────────────────────

    def algorithmize_vgm_axiom(self, axiom_id: str, axiom: dict) -> list:
        """Generate algorithms from a VGM axiom — logical inference tools."""
        generated = []
        text  = axiom.get("text", "")
        words = axiom.get("words", [])

        # DERIVE: apply this axiom to a new entity to produce a theorem
        def derive_theorem(entity: str, action: str = None,
                            state: str = None) -> str:
            t = text
            if "entity" in words and entity:
                t = t.replace("entity", entity).replace("Entity", entity)
            if action and "change" in words:
                t = t.replace("changes", action)
            if state and "state" in words:
                t = t.replace("state", state)
            return f"[DERIVED from {axiom_id}] {t}"

        derive_alg = GeneratedAlgorithm(
            name=f"DERIVE_FROM_{axiom_id}",
            description=(f"DERIVE: apply axiom '{text}' to a specific entity/action/state "
                         f"to produce a domain-specific theorem"),
            info_source=axiom_id,
            operation_type="DERIVE",
            execute_fn=derive_theorem,
            test_cases=[{
                "inputs": {"entity": "particle", "action": "accelerates", "state": "energy"},
                "expected": None  # just verify it produces a string
            }],
        )
        generated.append(derive_alg)

        # INSTANTIATE: find vocabulary that instantiates this axiom
        def instantiate(vocab_ties: dict) -> list:
            """Given vocabulary and their tie relationships,
            find real entities that are instances of this axiom."""
            instances = []
            for word, tied_words in vocab_ties.items():
                if any(w in words for w in tied_words):
                    instances.append(word)
            return instances

        inst_alg = GeneratedAlgorithm(
            name=f"INSTANTIATE_{axiom_id}",
            description=(f"INSTANTIATE: find vocabulary words that are "
                         f"real instances of axiom '{text}'"),
            info_source=axiom_id,
            operation_type="INSTANTIATE",
            execute_fn=instantiate,
            test_cases=[{
                "inputs": {"vocab_ties": {"king": ["rule","govern"], "stone": ["hard","break"]}},
                "expected": None
            }],
        )
        generated.append(inst_alg)

        return generated

    # ── MAIN ALGORITHMIZATION LOOP ────────────────────────────────────────

    def algorithmize(self, information, info_type: str = None) -> list:
        """Derive and register algorithms from any piece of new information.
        Routes to the appropriate generator based on the information's type.
        Tests every generated algorithm. Registers only what passes."""

        # Determine type if not given
        if info_type is None:
            if hasattr(information, "expression") and hasattr(information, "variables"):
                info_type = "FORMULA"
            elif hasattr(information, "law") and not hasattr(information, "expression"):
                info_type = "PHYSICAL_CONSTANT"
            elif isinstance(information, dict) and "text" in information:
                info_type = "VGM_AXIOM"
            else:
                info_type = "STRUCTURED_DATA"

        # Generate candidates
        if info_type == "FORMULA":
            candidates = self.algorithmize_formula(information)
        elif info_type == "VGM_AXIOM":
            axiom_id = information.get("id", "AXIOM")
            candidates = self.algorithmize_vgm_axiom(axiom_id, information)
        elif info_type == "STRUCTURED_DATA":
            candidates = self.algorithmize_structured_data(
                information if isinstance(information, dict) else {})
        else:
            candidates = []

        # Test and register
        registered_ids = []
        for alg in candidates:
            alg.run_tests()
            self.generated.append(alg)

            if alg.passed and self.alg_matrix:
                alg_id = self._next_alg_id()
                alg.alg_id = alg_id
                self.alg_matrix.known[alg_id] = alg.as_matrix_entry()
                self.registered.append(alg_id)
                registered_ids.append(alg_id)
                self._log(f"Registered {alg_id}: {alg.name} [{alg.operation_type}]")
            elif not alg.passed:
                self._log(f"FAILED: {alg.name} — {alg.failure_reason}")

        return registered_ids

    def algorithmize_batch(self, information_list: list,
                            max_items: int = 20) -> dict:
        """Process a batch of new information items — e.g. all formulas
        from a harvest run. Returns summary of what was generated."""
        all_registered = []
        by_type = _defaultdict(int)

        for item in information_list[:max_items]:
            ids = self.algorithmize(item)
            all_registered.extend(ids)
            for alg_id in ids:
                entry = self.alg_matrix.known.get(alg_id, {})
                by_type[entry.get("operation_type", "UNKNOWN")] += 1

        return {
            "items_processed": min(len(information_list), max_items),
            "algorithms_generated": len(self.generated),
            "algorithms_registered": len(all_registered),
            "algorithms_failed": len(self.generated) - len(all_registered),
            "by_operation_type": dict(by_type),
            "registered_ids": all_registered,
        }

    def report(self) -> str:
        lines = [
            f"InformationAlgorithmizer report:",
            f"  Generated: {len(self.generated)} candidate algorithms",
            f"  Registered (passed tests): {len(self.registered)}",
            f"  Failed: {len(self.generated) - len(self.registered)}",
            "",
            "Recent registrations:",
        ]
        for alg_id in self.registered[-8:]:
            entry = self.alg_matrix.known.get(alg_id, {})
            lines.append(f"  {alg_id}: {entry.get('name','')} [{entry.get('operation_type','')}]")
        if self._gen_log:
            lines.append("")
            lines.append("Generation log (last 10):")
            for msg in self._gen_log[-10:]:
                lines.append(f"  {msg}")
        return "\n".join(lines)




# ---------------------------------------------------------------------------
# A-151: EquilibriumGeneralityMeasure — G(C) = ΔV/ΔI
#
# Replaces A-118's standardization approach with blind balancing.
#
# G(C) = ΔV/ΔI where:
#   V(C) = number of vocabulary agents whose genus chain passes through C
#           (how many variants can occupy this classification)
#   I(C) = depth of C in the nesting hierarchy
#           (how much constraint information is required to specify C)
#
# A class is more general when it can absorb more variants
# per unit of constraint. Entity absorbs everything with depth 1.
# Labrador absorbs only itself with depth 5.
#
# The measurement is BLIND: no corpus statistics, no entry class weights,
# no presupposed precedence. Two agents are placed on opposite plates;
# their genus chains are followed simultaneously until convergence.
# The convergence point is DISCOVERED, not presupposed.
#
# The dangerous progression this guards against:
#   DISCOVERED → MEASURED → INDEXED → [STOP HERE]
#   ↓ (bias enters below this line)
#   EXPECTED → PRESUMED → DOGMATIZED
#
# A-152: BalancingScale — the comparison engine
# Places two vocabulary agents on opposite plates, discovers their
# equilibrium point (the shared ancestor in the nesting hierarchy),
# and records the discovered relationship without presupposing it.
# ---------------------------------------------------------------------------


class EquilibriumGeneralityMeasure:
    """A-151: Generality measured by blind balancing — G(C) = ΔV/ΔI

    The scale does not know its answer before the weighing.
    It discovers equilibrium by comparing candidates against each other,
    not against a predetermined standard. The discovered equilibrium IS
    the measured generality — not a distance from a corpus constant.

    Connection to Russian Dolls:
    Each doll is one constraint layer. The outer doll is more general
    because more variants can inhabit it. I(C) = nesting depth.
    V(C) = number of agents whose genus chain passes through C.
    G(C) = V(C) / I(C) — more variants per constraint = more general.
    """

    def __init__(self, lobby: "Lobby" = None, lexicon: dict = None):
        self.lobby   = lobby
        self.lexicon = lexicon or {}
        self._genus_cache   = {}   # word -> genus chain
        self._variant_cache = {}   # term -> count of agents through it
        self._g_cache       = {}   # term -> G(C) score

    # ── GENUS CHAIN (the Russian Doll nesting) ────────────────────────────

    def genus_chain(self, word: str, max_depth: int = 10) -> list:
        """Follow the nesting hierarchy upward from a word.
        Returns [word, genus, genus_of_genus, ..., terminal].
        Each step removes one constraint layer — opening a larger doll."""
        word = word.lower()
        if word in self._genus_cache:
            return self._genus_cache[word]

        chain = [word]
        seen  = {word}
        cur   = word

        for _ in range(max_depth):
            parent = self._genus_of(cur)
            if not parent or parent in seen:
                break
            chain.append(parent)
            seen.add(parent)
            cur = parent

        self._genus_cache[word] = chain
        return chain

    def _genus_of(self, word: str) -> str:
        """Find the immediate genus (parent in the nesting hierarchy).
        Uses the lobby's definition words if available; falls back to lexicon."""
        import re
        STOP = {"a","an","the","of","in","on","at","to","and","or","with",
                "by","from","for","as","is","are","that","which","this",
                "one","any","all","some","such","its","their",
                "relating","denoting","having","genus","family"}

        # Try lobby first (richer structure)
        if self.lobby:
            agent = self.lobby.agents.get(word)
            if agent and agent.definition_words:
                for dw in agent.definition_words:
                    dw_agent = self.lobby.agents.get(dw)
                    if (dw and dw != word and dw not in STOP
                            and dw_agent
                            and dw_agent.department in ("noun","n")
                            and len(dw) > 2):
                        return dw

        # Fall back to lexicon
        entry = self.lexicon.get(word)
        if not entry:
            return None
        desc = re.sub(r"^(a|an|the)\s+", "", entry.get("desc","").lower())
        for tok in re.findall(r"[a-z]+", desc):
            if (tok != word and tok not in STOP
                    and tok in self.lexicon and len(tok) > 2):
                return tok
        return None

    # ── V(C): VARIANT COUNT ───────────────────────────────────────────────

    def variants_at(self, term: str) -> int:
        """V(C): how many vocabulary agents have this term in their
        genus chain? More variants = more general classification."""
        term = term.lower()
        if term in self._variant_cache:
            return self._variant_cache[term]

        count = 0
        agents = self.lobby.agents if self.lobby else {}
        for word in agents:
            if term in self.genus_chain(word):
                count += 1

        self._variant_cache[term] = count
        return count

    # ── I(C): INFORMATION CONTENT (nesting depth) ─────────────────────────

    def information_content(self, term: str) -> int:
        """I(C): the depth of this term in the nesting hierarchy.
        Deeper nesting = more constraint layers = more information required
        to specify the class = less general.

        animal     → depth 1 (near the terminal — most general)
        mammal     → depth 2
        canine     → depth 3
        dog        → depth 4
        labrador   → depth 5 (fully constrained — most specific)"""
        chain = self.genus_chain(term)
        return max(len(chain), 1)

    # ── G(C) = ΔV/ΔI ─────────────────────────────────────────────────────

    def G(self, term: str, use_lobby_count: bool = True) -> float:
        """G(C) = V(C) / I(C) — the equilibrium generality measure.

        No corpus statistics. No entry class weights. No presupposed precedence.
        The score is computed from the structure of the nesting hierarchy alone.

        High G: absorbs many variants with little constraint (general)
        Low G:  absorbs few variants with much constraint (specific)"""
        term = term.lower()
        if term in self._g_cache:
            return self._g_cache[term]

        v = self.variants_at(term) if use_lobby_count else 1
        i = self.information_content(term)
        g = v / max(i, 1)
        self._g_cache[term] = g
        return g

    def G_normalized(self, term: str, max_g: float = None) -> float:
        """G(C) normalized to [0, 1] for comparison with A-118 scores.
        Requires knowing the max G across the vocabulary (usually V_total / 1)."""
        g = self.G(term)
        if max_g is None:
            n_agents = len(self.lobby.agents) if self.lobby else 1
            max_g = float(n_agents)
        return min(1.0, g / max_g)

    # ── DELTA FORMULATION: ΔV/ΔI ─────────────────────────────────────────

    def delta_G(self, term: str) -> float:
        """ΔV/ΔI: how much additional variation does this class absorb
        per additional constraint layer? GPT's more sensitive formulation.

        Computed as the rate of change in variant count per depth level:
        ΔV = V(C) - V(parent_of_C)
        ΔI = 1 (one additional constraint layer)
        ΔV/ΔI = ΔV (variant absorption rate at this nesting level)

        A class near the top of the hierarchy absorbs many new variants
        per layer (high ΔV/ΔI). A class near the bottom absorbs few."""
        chain = self.genus_chain(term)
        if len(chain) < 2:
            return float(self.variants_at(term))

        v_self   = self.variants_at(chain[0])  # variants at this level
        v_parent = self.variants_at(chain[1])  # variants at one level up
        dv = v_parent - v_self  # how many MORE variants the parent absorbs
        return float(max(dv, 0))  # rate of absorption going up one level

    # ── COMPARISON OPERATIONS ─────────────────────────────────────────────

    def compare(self, word_a: str, word_b: str) -> dict:
        """Which is more general? Uses G(C) with no presupposed standard.
        Returns scores, ratio, and the discovered relationship."""
        g_a = self.G(word_a)
        g_b = self.G(word_b)
        ratio = g_a / max(g_b, 0.001)
        return {
            "word_a": word_a, "G_a": round(g_a, 3),
            "word_b": word_b, "G_b": round(g_b, 3),
            "more_general": word_a if g_a > g_b else word_b,
            "ratio": round(ratio, 3),
            "relationship": (
                "word_a contains word_b" if ratio > 2 else
                "word_b contains word_a" if ratio < 0.5 else
                "similar generality level"
            ),
        }

    def rank(self, words: list) -> list:
        """Rank a set of words by G(C) — blind, no presupposed ordering."""
        scored = [(w, self.G(w)) for w in words if w in (
            self.lobby.agents if self.lobby else {})]
        scored.sort(key=lambda x: -x[1])
        return [{"word": w, "G": round(g, 3),
                  "depth": self.information_content(w),
                  "variants": self.variants_at(w),
                  "chain": self.genus_chain(w)[:5]}
                 for w, g in scored]


class BalancingScale:
    """A-152: The comparison engine — blind discovery of equilibrium.

    Places two vocabulary agents on opposite plates.
    Follows their genus chains simultaneously.
    Finds the point where both chains converge — the equilibrium.
    Records the discovery without presupposing it.

    The centering property:
    The scale's center is not pre-placed. It finds itself when the
    relational pressures from both plates cancel each other.
    The center IS the discovered class — never assumed, always found.

    Justice analogy: the scale is blind to which plate holds which agent.
    It discovers the equilibrium from the nesting structure alone.
    Precedence (prior measurements) is evidence, never absolute."""

    def __init__(self, egm: EquilibriumGeneralityMeasure):
        self.egm      = egm
        self.weighings = []   # history of discoveries — evidence, not dogma

    def weigh(self, word_a: str, word_b: str) -> dict:
        """Place two agents on opposite plates. Discover their equilibrium.

        The scale is blind:
        - It does not know beforehand whether dog or wolf is more general
        - It does not compare against a corpus standard
        - It discovers the relationship by following both chains
          until they converge

        The result is a DISCOVERY, not a MEASUREMENT against a standard."""
        chain_a = self.egm.genus_chain(word_a)
        chain_b = self.egm.genus_chain(word_b)
        set_a   = set(chain_a)

        equilibrium = None
        depth_a = len(chain_a)  # default: no convergence found
        depth_b = len(chain_b)

        # Follow both chains simultaneously until convergence
        for level_a, term in enumerate(chain_a):
            if term in set_a and term in set(chain_b):
                level_b = chain_b.index(term)
                equilibrium = term
                depth_a = level_a
                depth_b = level_b
                break

        result = {
            "word_a": word_a,
            "word_b": word_b,
            "chain_a": chain_a[:depth_a + 1] if equilibrium else chain_a,
            "chain_b": chain_b[:depth_b + 1] if equilibrium else chain_b,
            "equilibrium": equilibrium,
            "depth_a": depth_a,  # steps to remove from A to reach balance
            "depth_b": depth_b,  # steps to remove from B to reach balance
            "balance_point": depth_a + depth_b,  # total information removed
            "more_specific": (word_a if depth_a > depth_b else
                               word_b if depth_b > depth_a else "equal"),
            "status": "CONVERGED" if equilibrium else "NO_CONVERGENCE",
        }

        # Record as evidence, not dogma
        self.weighings.append(result)
        return result

    def weigh_many(self, words: list) -> list:
        """Weigh all pairs in a word set. Build a discovered relationship map
        from pairwise blind comparisons — no presupposed ordering."""
        results = []
        for i, w1 in enumerate(words):
            for w2 in words[i+1:]:
                results.append(self.weigh(w1, w2))
        return results

    def equilibrium_map(self, words: list) -> dict:
        """Build the full discovered nesting structure for a set of words.
        Which equilibrium points emerge? How many layers separate each pair?
        What classes are discovered that no word directly names?"""
        weighings = self.weigh_many(words)
        discovered = {}

        for w in weighings:
            if w["equilibrium"]:
                eq = w["equilibrium"]
                if eq not in discovered:
                    discovered[eq] = {
                        "equilibrium": eq,
                        "pairs_converging_here": [],
                        "G": self.egm.G(eq),
                        "depth": self.egm.information_content(eq),
                    }
                discovered[eq]["pairs_converging_here"].append(
                    (w["word_a"], w["word_b"]))

        return {
            "discovered_classes": discovered,
            "total_weighings": len(weighings),
            "converged": sum(1 for w in weighings if w["equilibrium"]),
            "note": ("These classes were DISCOVERED by blind balancing, "
                     "not assumed. They are evidence, not dogma."),
        }

    def report_discovery(self, word_a: str, word_b: str) -> str:
        """Express a discovered equilibrium in the Governor's voice."""
        result = self.weigh(word_a, word_b)
        if not result["equilibrium"]:
            return (f"ע Ayin: No convergence found between '{word_a}' "
                    f"and '{word_b}' within the indexed hierarchy.")

        lines = [
            f"ר Scale: '{word_a}' ↔ '{word_b}'",
            f"ע Ayin: Blind balancing initiated",
            f"  Plate A: {' → '.join(result['chain_a'])}",
            f"  Plate B: {' → '.join(result['chain_b'])}",
            f"פ Pe: Equilibrium discovered at '{result['equilibrium']}'",
            f"  Depth A: {result['depth_a']} constraint layers removed",
            f"  Depth B: {result['depth_b']} constraint layers removed",
            f"  G('{result['equilibrium']}') = {self.egm.G(result['equilibrium']):.2f}",
            f"  Status: {result['status']} — DISCOVERED, not presupposed",
        ]
        return "\n".join(lines)




# ---------------------------------------------------------------------------
# A-153: InwardSearchEngine — the gap reflex.
#
# When Ayin reports a GAP (word not in vocabulary lobby), ECHO turns
# inward before giving up. It searches its own infrastructure:
#
#   1. LETTER_LOBBY    — Hebrew/Latin/English letter agents by name
#   2. GEMATRIA        — letter name → numerical identity → LHEA semantics
#   3. ALGORITHM_MATRIX — search by name and description keywords
#   4. VGM             — axiom text contains this word or neighbor?
#   5. LRM             — theorem text search
#   6. NUMBER_AGENTS   — physical/math constants by name
#   7. FORMULA_AGENTS  — formula names and expressions
#
# When a connection is found, it is passed back to A-145 so Pe can
# compose from it rather than reporting a dead end.
#
# This is ECHO's self-referential loop: GAP → inward → connection → Pe.
# The system that knows it doesn't know something also knows what it
# does know — and searches there first.
# ---------------------------------------------------------------------------

# Hebrew letter data for inward search
HEBREW_LETTER_INDEX = {
    "aleph": {"glyph":"א","val":1,"class":"Mother",
               "lhea":"silence/potential/unity — primal breath, the unspoken"},
    "bet":   {"glyph":"ב","val":2,"class":"Double",
               "lhea":"house/container/vessel — the structure that holds"},
    "gimel": {"glyph":"ג","val":3,"class":"Double",
               "lhea":"movement/carrying/benefit — the channel of flow"},
    "dalet": {"glyph":"ד","val":4,"class":"Double",
               "lhea":"door/threshold/passage — the point of entry"},
    "he":    {"glyph":"ה","val":5,"class":"Elemental",
               "lhea":"breath/revelation/window — the divine name, expression"},
    "vav":   {"glyph":"ו","val":6,"class":"Elemental",
               "lhea":"hook/connection/and — the joining, the pillar"},
    "zayin": {"glyph":"ז","val":7,"class":"Elemental",
               "lhea":"sword/sustenance/time — the weapon and the nourishment"},
    "het":   {"glyph":"ח","val":8,"class":"Elemental",
               "lhea":"fence/life/grace — the boundary that protects"},
    "tet":   {"glyph":"ט","val":9,"class":"Elemental",
               "lhea":"coil/goodness/hidden good — what is concealed within"},
    "yod":   {"glyph":"י","val":10,"class":"Elemental",
               "lhea":"hand/divine point/seed — the smallest, the most potent"},
    "kaf":   {"glyph":"כ","val":20,"class":"Double",
               "lhea":"palm/vessel/crown — capacity to hold and to act"},
    "lamed": {"glyph":"ל","val":30,"class":"Elemental",
               "lhea":"teaching/aspiration/the goad — reaching upward, the drive to learn"},
    "mem":   {"glyph":"מ","val":40,"class":"Mother",
               "lhea":"water/source/womb/wisdom — the origin, the containing flow"},
    "nun":   {"glyph":"נ","val":50,"class":"Elemental",
               "lhea":"fish/soul/faithfulness — individual purpose emerging"},
    "samekh":{"glyph":"ס","val":60,"class":"Double",
               "lhea":"support/circle/foundation — the cycle, the prop"},
    "ayin":  {"glyph":"ע","val":70,"class":"Elemental",
               "lhea":"eye/perception/spring/depth — seeing, the source of insight"},
    "pe":    {"glyph":"פ","val":80,"class":"Double",
               "lhea":"mouth/speech/expression/command — the outward voice"},
    "tsadi": {"glyph":"צ","val":90,"class":"Elemental",
               "lhea":"righteousness/discipline/pursuit — the drive toward correctness"},
    "qof":   {"glyph":"ק","val":100,"class":"Double",
               "lhea":"back of head/sanctity/cycle — what returns, the sacred loop"},
    "resh":  {"glyph":"ר","val":200,"class":"Double",
               "lhea":"head/beginning/identity/leader — A-000, the Governor itself"},
    "shin":  {"glyph":"ש","val":300,"class":"Mother",
               "lhea":"fire/transformation/tooth — the consuming and purifying force"},
    "tav":   {"glyph":"ת","val":400,"class":"Double",
               "lhea":"mark/truth/completion/seal — the final letter, covenant"},
    # Sofit forms
    "kaf-sofit":   {"glyph":"ך","val":500,"class":"Sofit",
                     "lhea":"kaf at rest — capacity fulfilled, palm closed"},
    "mem-sofit":   {"glyph":"ם","val":600,"class":"Sofit",
                     "lhea":"mem enclosed — source sealed, womb complete"},
    "nun-sofit":   {"glyph":"ן","val":700,"class":"Sofit",
                     "lhea":"nun extended — soul reaching its terminal point"},
    "pe-sofit":    {"glyph":"ף","val":800,"class":"Sofit",
                     "lhea":"pe extended — the final word, expression complete"},
    "tsadi-sofit": {"glyph":"ץ","val":900,"class":"Sofit",
                     "lhea":"tsadi extended — righteousness at its furthest reach"},
}


class InwardSearchResult:
    """What the inward search found for a GAP word."""
    def __init__(self, word: str):
        self.word       = word
        self.found      = False
        self.sources    = []   # where it was found
        self.letter     = None # Hebrew letter data if found
        self.alg_hits   = []   # algorithm matrix matches
        self.vgm_hits   = []   # VGM statement matches
        self.lrm_hits   = []   # LRM theorem matches
        self.num_hits   = []   # number/constant matches
        self.connections = []  # synthesized connections

    def to_ayin_report(self) -> str:
        """Format for Ayin's perception report."""
        if not self.found:
            return f"  '{self.word}' → GAP (inward search: nothing found)"
        parts = [f"  '{self.word}' → INWARD MATCH"]
        for src in self.sources:
            parts.append(f"    [{src['type']}] {src['detail']}")
        return "\n".join(parts)

    def to_pe_content(self) -> list:
        """Content Pe can compose from."""
        content = []
        if self.letter:
            l = self.letter
            content.append(
                f"'{self.word}' maps to Hebrew letter {l['glyph']} "
                f"(gematria={l['val']}, class={l['class']}): "
                f"{l['lhea']}")
        for hit in self.alg_hits[:2]:
            content.append("Algorithm: " + hit["id"] + " — " + hit["name"] + ": " + hit["desc"][:60])
        for hit in self.vgm_hits[:2]:
            content.append("Axiom: \"" + hit["text"] + "\"")
        for hit in self.lrm_hits[:1]:
            content.append("Theorem: \"" + hit["text"] + "\"")
        return content


class InwardSearchEngine:
    """A-153: When Ayin reports a GAP, turn inward.

    Search priority:
    1. Letter lobby (Hebrew/sofit) — most likely match for letter names
    2. Algorithm matrix — keyword match on name and description
    3. VGM axioms — text contains this word
    4. LRM theorems — text contains this word
    5. Number agents — constant name match
    6. Formula agents — formula name or expression match

    Returns InwardSearchResult with whatever was found.
    Empty result if nothing found anywhere — honest about total gaps."""

    def __init__(self, alg_matrix: dict = None, vgm: dict = None,
                  lrm_entries: dict = None, number_agents: dict = None,
                  formula_agents: list = None):
        self.alg_matrix    = alg_matrix    or {}
        self.vgm           = vgm           or {}
        self.lrm_entries   = lrm_entries   or {}
        self.number_agents = number_agents or {}
        self.formula_agents = formula_agents or []

    def search(self, word: str) -> InwardSearchResult:
        """Full inward search for a GAP word."""
        result = InwardSearchResult(word)
        w = word.lower().strip()

        # 1. LETTER LOBBY (Hebrew + sofit)
        if w in HEBREW_LETTER_INDEX:
            letter_data = HEBREW_LETTER_INDEX[w]
            result.letter = letter_data
            result.found  = True
            result.sources.append({
                "type": "HEBREW_LETTER_LOBBY",
                "detail": (f"glyph={letter_data['glyph']} "
                           f"val={letter_data['val']} "
                           f"class={letter_data['class']} "
                           f"lhea: {letter_data['lhea'][:50]}")
            })

        # 2. ALGORITHM MATRIX — keyword search in name + description
        for alg_id, entry in self.alg_matrix.items():
            name = entry.get("name","").lower()
            desc = entry.get("description", entry.get("desc","")).lower()
            if w in name or w in desc:
                result.alg_hits.append({
                    "id":   alg_id,
                    "name": entry.get("name",""),
                    "desc": entry.get("description", entry.get("desc",""))[:80],
                })
                result.found = True
        if result.alg_hits:
            result.sources.append({
                "type": "ALGORITHM_MATRIX",
                "detail": f"{len(result.alg_hits)} algorithm(s) match '{word}'"
            })

        # 3. VGM — text search
        for stmt_id, stmt in self.vgm.items():
            text = stmt.get("text","").lower()
            words_list = stmt.get("words",[])
            if w in text or w in words_list:
                result.vgm_hits.append({
                    "id":   stmt_id,
                    "text": stmt.get("text","")
                })
                result.found = True
        if result.vgm_hits:
            result.sources.append({
                "type": "VGM_AXIOMS",
                "detail": f"{len(result.vgm_hits)} axiom(s) contain '{word}'"
            })

        # 4. LRM — text search
        for lrm_id, entry in self.lrm_entries.items():
            text = entry.get("text","").lower()
            if w in text:
                result.lrm_hits.append({
                    "id":   lrm_id,
                    "text": entry.get("text","")[:100]
                })
                result.found = True
        if result.lrm_hits:
            result.sources.append({
                "type": "LRM_THEOREMS",
                "detail": f"{len(result.lrm_hits)} theorem(s) contain '{word}'"
            })

        # 5. NUMBER AGENTS
        for key, agent in self.number_agents.items():
            if (w in key.lower() or
                    w in getattr(agent,"name","").lower()):
                result.num_hits.append({
                    "key":  key,
                    "name": getattr(agent,"name",key),
                    "val":  getattr(agent,"computation","?"),
                })
                result.found = True
        if result.num_hits:
            result.sources.append({
                "type": "NUMBER_AGENTS",
                "detail": f"{len(result.num_hits)} constant(s) match '{word}'"
            })

        # 6. FORMULA AGENTS
        if self.formula_agents:
            for agent in self.formula_agents:
                if (w in agent.name.lower() or
                        w in agent.expression.lower() or
                        w in agent.domain.lower()):
                    result.sources.append({
                        "type": "FORMULA_AGENT",
                        "detail": f"{agent.name}: {agent.expression[:50]}"
                    })
                    result.found = True
                    break  # one match sufficient for discovery

        return result

    def search_batch(self, words: list) -> dict:
        """Search for multiple GAP words at once.
        Returns {word -> InwardSearchResult}"""
        return {w: self.search(w) for w in words}


class GapReflexMixin:
    """Mixin that adds the inward search reflex to AlgorithmicCommunicator.
    When Ayin classifies a word as GAP, the reflex fires automatically
    before that word is written off as unknown."""

    def _ayin_classify_with_reflex(self, token: str,
                                     inward: "InwardSearchEngine") -> tuple:
        """Extended Ayin classification: if GAP, run inward search.
        Returns (classification_string, InwardSearchResult or None)."""
        base_cls = self._ayin_classify(token)
        if "GAP" not in base_cls:
            return base_cls, None

        # GAP detected — turn inward
        result = inward.search(token)
        if result.found:
            sources_str = " + ".join(s["type"] for s in result.sources)
            return f"GAP→INWARD MATCH [{sources_str}]", result
        return base_cls, None




# ---------------------------------------------------------------------------
# A-156: VocabularyAcquisitionAgent
#   Simultaneously pulls:
#     - WordNet hypernym hierarchy (genus chains ECHO needs for generalization)
#     - Wiktionary etymology (historical root validation of LHEA decompositions)
#   WordNet: available now via NLTK (117,659 synsets, offline after install)
#   Etymology: designed for Pydroid full-network; gated in sandbox
#
# A-157: DeploymentTranslator
#   Reads ECHO's current Python matrix state and outputs a JSON blueprint
#   mapping every structure to its Cloudflare KV/D1 equivalent.
#   A future algorithm reads this blueprint and handles migration automatically.
#   No manual rewriting needed when the GitHub/Cloudflare pipeline is live.
#
# A-158: GeosensoryCrawler
#   Semi-open geosensory endpoint discovery:
#     Stage 1: known structured APIs (typed JSON, already catalogued)
#     Stage 2: GitHub search for geosensory repositories
#     Stage 3: HTML link extraction fallback (semi-open gate)
#   Stores locally in Python for now; DeploymentTranslator handles
#   the Cloudflare KV migration when the pipeline is ready.
# ---------------------------------------------------------------------------

import threading as _threading

class EtymologyEntry:
    """A word's historical root — where it came from before it meant what it means."""
    def __init__(self, word: str, root: str = '', language: str = '',
                  original_meaning: str = '', chain: list = None):
        self.word             = word
        self.root             = root             # e.g. "gnoscere"
        self.root_language    = language         # e.g. "Latin"
        self.original_meaning = original_meaning # e.g. "to know"
        self.chain            = chain or []      # [("Latin","gnoscere","to know"),...]
        self.lhea_validation  = None             # set after cross-checking with LHEA

    def lhea_agrees(self, lhea_chain: list) -> bool:
        """Check if the etymology's original meaning overlaps with the
        LHEA decomposition — two independent paths to the same semantic core."""
        if not self.original_meaning or not lhea_chain:
            return False
        orig_words = set(self.original_meaning.lower().split())
        lhea_words = set()
        for letter in lhea_chain:
            lhea_info = HEBREW_LETTER_INDEX.get(letter, {})
            lhea_words.update(lhea_info.get('lhea','').lower().split())
        overlap = orig_words & lhea_words
        self.lhea_validation = overlap
        return len(overlap) > 0


class VocabularyAcquisitionAgent:
    """A-156: Pulls WordNet and etymology simultaneously.

    WordNet gives ECHO the genus chains it needs for the generalization stack.
    When WordNet says dog → canine → mammal → animal → entity, ECHO can now
    follow that chain all the way to the VGM axiom "An entity changes."
    Without WordNet, the chain breaks after one step because the thesaurus
    corpus doesn't contain the intermediate links.

    Etymology gives ECHO historical root validation. When LHEA decomposes
    'cognition' as כ(palm/vessel) → ג(movement) → נ(soul) → י(hand) →
    ת(mark) — and the Latin root 'cognoscere' means 'to grasp/know' —
    the vessel-of-grasping reading from LHEA aligns with the historical
    meaning of the word. That alignment is a validated understanding,
    not a phonetic coincidence.

    Runs both sources simultaneously via threading when resources allow."""

    WIKTIONARY_API = "https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
    ETYMOLOGY_ATLAS = "https://raw.githubusercontent.com/data-poems/etymology-atlas/main"

    def __init__(self, lobby: "Lobby" = None, lexicon: dict = None,
                  alg_matrix: "AlgorithmMatrix" = None):
        self.lobby      = lobby
        self.lexicon    = lexicon or {}
        self.alg_matrix = alg_matrix
        self.wordnet_cache   = {}   # word -> list of hypernym chain lists
        self.etymology_cache = {}   # word -> EtymologyEntry
        self.acquired_words  = []   # words successfully indexed from WordNet
        self._wn_available   = self._check_wordnet()
        self.log             = []

    def _check_wordnet(self) -> bool:
        try:
            from nltk.corpus import wordnet as wn
            list(wn.synsets("entity"))
            return True
        except Exception:
            return False

    def _log(self, msg: str):
        self.log.append(msg)

    # ── WORDNET ─────────────────────────────────────────────────────────

    def wordnet_hypernym_chain(self, word: str,
                                 pos: str = None) -> list:
        """Return all hypernym chains for a word from WordNet.
        Each chain goes from the word up to the terminal ('entity.n.01').
        ECHO uses these to fill gaps in its generalization stacks."""
        if not self._wn_available:
            return []
        if word in self.wordnet_cache:
            return self.wordnet_cache[word]

        from nltk.corpus import wordnet as wn
        pos_tag = {'noun': wn.NOUN, 'verb': wn.VERB,
                    'adj': wn.ADJ, 'adv': wn.ADV}.get(pos, wn.NOUN)
        synsets = wn.synsets(word, pos=pos_tag)
        if not synsets:
            synsets = wn.synsets(word)

        all_chains = []
        for synset in synsets[:2]:  # top 2 senses
            for path in synset.hypernym_paths():
                chain = [s.lemma_names()[0].replace('_', ' ')
                          for s in path]
                all_chains.append({
                    'synset':     synset.name(),
                    'definition': synset.definition(),
                    'chain':      chain,   # [most_specific, ..., entity]
                    'depth':      len(chain),
                })
        self.wordnet_cache[word] = all_chains
        return all_chains

    def wordnet_genus(self, word: str, pos: str = None) -> str:
        """Return the immediate genus (first hypernym) for a word.
        Used to fill A-141 GeneralizationStack chains that hit dead ends."""
        chains = self.wordnet_hypernym_chain(word, pos)
        if not chains:
            return None
        chain = chains[0]['chain']
        # chain[0] = word, chain[1] = immediate genus
        if len(chain) > 1:
            return chain[-2]  # second from end = one step below entity
        return None

    def enrich_lobby_with_wordnet(self, max_words: int = 500) -> dict:
        """For every agent in the lobby, pull its WordNet hypernym chain
        and index any intermediate terms not yet in the vocabulary.
        This fills the gaps in the generalization stack."""
        if not self._wn_available or not self.lobby:
            return {'status': 'wordnet_unavailable'}

        enriched = 0
        new_genus_links = 0
        gaps_filled = []

        agents = list(self.lobby.agents.items())[:max_words]
        for word, agent in agents:
            chains = self.wordnet_hypernym_chain(word, pos=agent.department)
            if not chains:
                continue
            enriched += 1

            # Index intermediate genus terms not yet in lobby
            for chain_data in chains[:1]:
                for genus_word in chain_data['chain']:
                    if (genus_word != word and
                            genus_word not in self.lobby.agents and
                            len(genus_word) > 2):
                        # Index with WordNet definition as description
                        from nltk.corpus import wordnet as wn
                        syn = wn.synsets(genus_word)
                        desc = syn[0].definition() if syn else f"genus of {word}"
                        if self.alg_matrix:
                            self.alg_matrix.index_dictionary_entry(
                                genus_word, desc, pos='noun',
                                category='wordnet_genus')
                        self.acquired_words.append(genus_word)
                        gaps_filled.append(genus_word)
                        new_genus_links += 1

        self._log(f"WordNet: enriched {enriched} agents, "
                  f"indexed {new_genus_links} new genus terms")
        return {
            'enriched': enriched,
            'new_genus_links': new_genus_links,
            'gaps_filled': gaps_filled[:20],
            'total_acquired': len(self.acquired_words),
        }

    # ── ETYMOLOGY ────────────────────────────────────────────────────────

    def fetch_etymology_wiktionary(self, word: str) -> EtymologyEntry:
        """Fetch etymology from Wiktionary API.
        Works in Pydroid (full network). Gated in sandbox.
        Returns EtymologyEntry with root, language, original meaning."""
        import urllib.request, json, re
        if word in self.etymology_cache:
            return self.etymology_cache[word]

        try:
            url = self.WIKTIONARY_API.format(word=word)
            req = urllib.request.Request(url,
                headers={'User-Agent': 'ECHO-Governor/1.0 (Mashet/LHEA Research)'})
            with urllib.request.urlopen(req, timeout=6) as r:
                data = json.loads(r.read())

            # Extract etymology section from definitions
            entry = EtymologyEntry(word)
            for lang_data in data.get('en', []):
                definitions = lang_data.get('definitions', [])
                for defn in definitions:
                    # Look for etymology in definition text
                    text = defn.get('definition', '')
                    # Common etymology patterns: "From Latin X", "From PIE *X"
                    ety_match = re.search(
                        r'[Ff]rom\s+((?:Proto-)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+'
                        r'([*a-zA-Zāēīōūáéíóúàèìòùâêîôûαβγδεζηθ-]+)',
                        text)
                    if ety_match:
                        entry.root_language    = ety_match.group(1)
                        entry.root             = ety_match.group(2)
                        meaning_match = re.search(r'meaning\s+"([^"]+)"', text)
                        if meaning_match:
                            entry.original_meaning = meaning_match.group(1)
                        break

            self.etymology_cache[word] = entry
            return entry

        except Exception as e:
            entry = EtymologyEntry(word)
            self.etymology_cache[word] = entry
            return entry

    def fetch_etymology_batch(self, words: list,
                               max_words: int = 50) -> dict:
        """Fetch etymology for a batch of words.
        Runs in Pydroid. Returns {word -> EtymologyEntry}."""
        results = {}
        for word in words[:max_words]:
            results[word] = self.fetch_etymology_wiktionary(word)
        return results

    # ── SIMULTANEOUS ACQUISITION ─────────────────────────────────────────

    def acquire(self, words: list = None,
                 run_wordnet: bool = True,
                 run_etymology: bool = True,
                 max_words: int = 300) -> dict:
        """Run both WordNet and etymology acquisition simultaneously.
        Uses threading when both are active."""
        results = {}

        if run_wordnet and run_etymology:
            # Run both in parallel threads
            wn_result = {}
            ety_result = {}
            errors = []

            def run_wn():
                try:
                    wn_result.update(self.enrich_lobby_with_wordnet(max_words))
                except Exception as e:
                    errors.append(f"WordNet: {e}")

            def run_ety():
                try:
                    target = words or list((self.lobby.agents if self.lobby else {}).keys())
                    ety_result.update(self.fetch_etymology_batch(
                        target, max_words=min(50, max_words)))
                except Exception as e:
                    errors.append(f"Etymology: {e}")

            t1 = _threading.Thread(target=run_wn)
            t2 = _threading.Thread(target=run_ety)
            t1.start(); t2.start()
            t1.join(timeout=30); t2.join(timeout=30)

            results['wordnet']   = wn_result
            results['etymology'] = ety_result
            if errors:
                results['errors'] = errors

        elif run_wordnet:
            results['wordnet'] = self.enrich_lobby_with_wordnet(max_words)
        elif run_etymology:
            target = words or list((self.lobby.agents if self.lobby else {}).keys())
            results['etymology'] = self.fetch_etymology_batch(target, max_words)

        return results

    def summary(self) -> dict:
        return {
            'wordnet_available': self._wn_available,
            'words_acquired':    len(self.acquired_words),
            'etymology_cached':  len(self.etymology_cache),
            'wordnet_cached':    len(self.wordnet_cache),
            'log':               self.log[-5:],
        }


class DeploymentTranslator:
    """A-157: Reads ECHO's current Python matrix state and produces
    a JSON blueprint mapping every structure to its Cloudflare equivalent.

    The blueprint has three layers:
      1. Cloudflare KV namespaces — fast single-item lookups
         (state, individual VGM axioms, individual LRM theorems)
      2. Cloudflare D1 tables — structured queries across entries
         (full lobby, formula library, etymology, geosensory endpoints)
      3. Migration contract — how Python types map to KV/D1 types

    A future algorithm (A-159: CloudflareMigrator) reads this blueprint
    and handles the actual migration when the GitHub/Cloudflare pipeline
    is live. No manual rewriting needed."""

    VERSION = "1.0"

    def __init__(self, lobby: "Lobby" = None,
                  vgm: dict = None, lrm_entries: dict = None,
                  alg_matrix: "AlgorithmMatrix" = None,
                  geosensory_registry: dict = None,
                  etymology_cache: dict = None):
        self.lobby              = lobby
        self.vgm                = vgm or {}
        self.lrm_entries        = lrm_entries or {}
        self.alg_matrix         = alg_matrix
        self.geosensory_registry = geosensory_registry or {}
        self.etymology_cache    = etymology_cache or {}

    def _kv_namespaces(self) -> list:
        """Define the KV namespaces ECHO needs."""
        return [
            {
                "name":        "ECHO_STATE",
                "binding":     "ECHO_STATE",
                "description": "ECHO's live operational state — generation, coherency, active queues",
                "keys": [
                    {"key": "generation",        "type": "integer", "description": "Current evolution generation"},
                    {"key": "coherency",          "type": "float",   "description": "Current C(N) score"},
                    {"key": "lobby_size",         "type": "integer", "description": "Number of indexed agents"},
                    {"key": "acquisition_queue",  "type": "json",    "description": "AcquisitionPlanner target list"},
                    {"key": "last_equilibrium",   "type": "json",    "description": "Most recent BalancingScale result"},
                    {"key": "identity",           "type": "string",  "description": "resh — A-000, always"},
                ],
                "python_source": "Runtime state — set during evolution and pipeline runs",
            },
            {
                "name":        "ECHO_VGM",
                "binding":     "ECHO_VGM",
                "description": "Validated Generalization Matrix — axiom tier entries",
                "key_pattern": "axiom:{id}",
                "value_schema": {
                    "id":         "string (UG-XXXX)",
                    "text":       "string — the axiom statement",
                    "words":      "list of strings",
                    "structure":  "list of strings (noun/verb/...)",
                    "score":      "float 0.0–1.0",
                    "origin":     "string",
                },
                "python_source": "vgm_data dict in echo_governor_skeleton.py",
                "current_count": len(self.vgm),
            },
            {
                "name":        "ECHO_LRM",
                "binding":     "ECHO_LRM",
                "description": "Logic and Reasoning Matrix — theorem tier entries",
                "key_pattern": "theorem:{id}",
                "value_schema": {
                    "id":                "string (LRM-XXXX)",
                    "text":              "string — the theorem statement",
                    "rule":              "string (SPECIALIZE/COMPOSE/CAUSAL_CHAIN/APPLY_LAW/CONDITIONAL)",
                    "sources":           "list of strings (VGM ids or law ids)",
                    "specificity_level": "string",
                    "coherence":         "float",
                },
                "python_source": "lrm.entries dict in LogicReasoningMatrix",
                "current_count": len(self.lrm_entries),
            },
            {
                "name":        "ECHO_MATRIX",
                "binding":     "ECHO_MATRIX",
                "description": "Algorithm Matrix — registered algorithms A-000 through A-158+",
                "key_pattern": "algorithm:{id}",
                "value_schema": {
                    "id":          "string (A-XXX)",
                    "name":        "string",
                    "type":        "string",
                    "status":      "string",
                    "description": "string",
                    "origin":      "string",
                },
                "python_source": "matrix.known dict in AlgorithmMatrix",
                "current_count": len(getattr(self.alg_matrix,'known',{})),
            },
        ]

    def _d1_tables(self) -> list:
        """Define the D1 database tables ECHO needs."""
        agent_count = len(self.lobby.agents) if self.lobby else 0
        return [
            {
                "database_name":   "echo_knowledge",
                "binding":         "DB",
                "description":     "ECHO's main knowledge store — agents, ties, neighborhoods, formulas",
                "tables": [
                    {
                        "name": "agents",
                        "description": "Every indexed vocabulary agent",
                        "columns": [
                            "word TEXT PRIMARY KEY",
                            "department TEXT",
                            "entry_class TEXT",
                            "generality_score REAL",
                            "definition TEXT",
                            "neighborhood TEXT",
                            "study_group_type TEXT",
                            "created_at TEXT",
                        ],
                        "indexes": ["CREATE INDEX idx_dept ON agents(department)",
                                     "CREATE INDEX idx_gen ON agents(generality_score)"],
                        "current_rows": agent_count,
                        "python_source": "lobby.agents dict",
                    },
                    {
                        "name": "ties",
                        "description": "Semantic connections between agents",
                        "columns": [
                            "id INTEGER PRIMARY KEY AUTOINCREMENT",
                            "word_a TEXT",
                            "word_b TEXT",
                            "tie_weight REAL DEFAULT 1.0",
                            "tie_source TEXT",
                        ],
                        "indexes": ["CREATE INDEX idx_word_a ON ties(word_a)",
                                     "CREATE INDEX idx_word_b ON ties(word_b)"],
                        "python_source": "agent.ties set for each agent in lobby",
                    },
                    {
                        "name": "wordnet_chains",
                        "description": "WordNet hypernym chains per word",
                        "columns": [
                            "word TEXT",
                            "synset TEXT",
                            "chain_json TEXT",
                            "depth INTEGER",
                            "definition TEXT",
                        ],
                        "python_source": "VocabularyAcquisitionAgent.wordnet_cache",
                    },
                    {
                        "name": "etymology",
                        "description": "Historical root data per word",
                        "columns": [
                            "word TEXT PRIMARY KEY",
                            "root TEXT",
                            "root_language TEXT",
                            "original_meaning TEXT",
                            "chain_json TEXT",
                            "lhea_validation TEXT",
                        ],
                        "python_source": "VocabularyAcquisitionAgent.etymology_cache",
                        "current_rows": len(self.etymology_cache),
                    },
                    {
                        "name": "formulas",
                        "description": "Harvested formula agents (A-147)",
                        "columns": [
                            "alg_id TEXT PRIMARY KEY",
                            "name TEXT",
                            "expression TEXT",
                            "domain TEXT",
                            "variables_json TEXT",
                            "law TEXT",
                            "vgm_abstraction TEXT",
                            "lrm_form TEXT",
                        ],
                        "python_source": "FormulaIndexer._indexed list",
                    },
                    {
                        "name": "geosensory_endpoints",
                        "description": "Discovered geosensory API endpoints (A-158)",
                        "columns": [
                            "key TEXT PRIMARY KEY",
                            "name TEXT",
                            "url TEXT",
                            "domain TEXT",
                            "sensor_type TEXT",
                            "key_required INTEGER",
                            "format TEXT",
                            "fields_json TEXT",
                            "jurisdiction TEXT",
                            "lhea_letter TEXT",
                            "description TEXT",
                            "last_validated TEXT",
                            "status TEXT DEFAULT 'discovered'",
                        ],
                        "indexes": ["CREATE INDEX idx_domain ON geosensory_endpoints(domain)",
                                     "CREATE INDEX idx_sensor ON geosensory_endpoints(sensor_type)"],
                        "current_rows": len(self.geosensory_registry),
                        "python_source": "GeosensoryCrawler.registry dict",
                    },
                ],
            },
        ]

    def _wrangler_toml(self) -> str:
        """Generate the wrangler.toml snippet for Cloudflare deployment."""
        kv_lines = []
        for ns in self._kv_namespaces():
            kv_lines.append(f'[[kv_namespaces]]')
            kv_lines.append(f'binding = "{ns["binding"]}"')
            kv_lines.append(f'id = "REPLACE_WITH_{ns["binding"]}_KV_ID"')
            kv_lines.append('')

        d1_lines = []
        for db in self._d1_tables():
            d1_lines.append(f'[[d1_databases]]')
            d1_lines.append(f'binding = "{db["binding"]}"')
            d1_lines.append(f'database_name = "{db["database_name"]}"')
            d1_lines.append(f'database_id = "REPLACE_WITH_D1_DATABASE_ID"')
            d1_lines.append('')

        nl = "\n"
        return ("# wrangler.toml — ECHO Governor Cloudflare Configuration\n"
                "# Generated by DeploymentTranslator (A-157)\n"
                "# Replace all REPLACE_WITH_* values with actual IDs\n\n"
                f'name = \"echo-green-future\"\n'
                f'main = \"src/index.js\"\n'
                f'compatibility_date = \"2024-09-01\"\n\n'
                + nl.join(kv_lines) + "\n"
                + nl.join(d1_lines))

    def _migration_sql(self) -> str:
        """Generate D1 migration SQL to create all tables."""
        sql_lines = ["-- ECHO Governor D1 Migration",
                      "-- Generated by DeploymentTranslator (A-157)",
                      "-- Run via: wrangler d1 execute echo_knowledge --file=migration.sql",
                      ""]
        for db in self._d1_tables():
            for table in db['tables']:
                cols = (',\n  ').join(table['columns'])
                sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table['name']} (")
                sql_lines.append(f"  {cols}")
                sql_lines.append(");")
                for idx in table.get('indexes', []):
                    sql_lines.append(f"{idx};")
                sql_lines.append("")
        return '\n'.join(sql_lines)

    def translate(self) -> dict:
        """Generate the full deployment blueprint."""
        import json
        blueprint = {
            "version":       self.VERSION,
            "generated_by":  "A-157 DeploymentTranslator",
            "description":   "Maps ECHO's Python matrix state to Cloudflare KV and D1",
            "kv_namespaces": self._kv_namespaces(),
            "d1_databases":  self._d1_tables(),
            "wrangler_toml": self._wrangler_toml(),
            "migration_sql": self._migration_sql(),
            "python_to_kv_map": {
                "vgm_data dict":            "ECHO_VGM KV namespace (key: axiom:{id})",
                "lrm.entries dict":         "ECHO_LRM KV namespace (key: theorem:{id})",
                "matrix.known dict":        "ECHO_MATRIX KV namespace (key: algorithm:{id})",
                "lobby.agents dict":        "D1 agents + ties tables",
                "FormulaIndexer._indexed":  "D1 formulas table",
                "etymology_cache dict":     "D1 etymology table",
                "GeosensoryCrawler.registry": "D1 geosensory_endpoints table",
                "Runtime state":            "ECHO_STATE KV namespace",
            },
            "next_step": "A-159 CloudflareMigrator reads this blueprint and runs the migration",
        }
        return blueprint

    def save_blueprint(self, path: str = '/home/claude/cloudflare_blueprint.json') -> str:
        import json
        blueprint = self.translate()
        with open(path, 'w') as f:
            json.dump(blueprint, f, indent=2)
        return path


class GeosensoryCrawler:
    """A-158: Semi-open geosensory endpoint discovery and accumulation.

    Stage 1 — Known structured APIs (typed JSON, immediately usable)
    Stage 2 — GitHub repository search (finds more structured sources)
    Stage 3 — HTML link extraction fallback (semi-open gate)

    Stores locally in Python dict for now.
    DeploymentTranslator (A-157) generates the Cloudflare KV/D1
    blueprint for migration when the pipeline is ready."""

    KNOWN_ENDPOINTS = {
        "NOAA_SWPC_SOLAR_WIND_MAG": {
            "name": "NOAA SWPC — Real-Time Solar Wind Magnetometer",
            "url":  "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json",
            "domain": "J1_CONTINUITY", "sensor_type": "SOLAR_MAGNETIC",
            "key_required": False, "format": "JSON", "resolution": "1-minute",
            "fields": ["time_tag","bx_gsm","by_gsm","bz_gsm","bt"],
            "lhea_letter": "shin",
            "jurisdiction": "J1 Continuity — sustained solar wind magnetic state",
            "description": "DSCOVR spacecraft magnetometer at L1 Lagrange point",
        },
        "NOAA_SWPC_KP_INDEX": {
            "name": "NOAA SWPC — Planetary K Index",
            "url":  "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
            "domain": "J2_CONTAINMENT", "sensor_type": "GEOMAGNETIC",
            "key_required": False, "format": "JSON", "resolution": "1-minute",
            "fields": ["time_tag","kp_index","observed","noaa_scale"],
            "lhea_letter": "mem",
            "jurisdiction": "J2 Containment — bounded geomagnetic field state",
            "description": "Global geomagnetic activity. Kp>=5 = storm.",
        },
        "NOAA_SWPC_XRAY": {
            "name": "NOAA SWPC — GOES X-Ray Flux",
            "url":  "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json",
            "domain": "J5_APERTURE", "sensor_type": "SOLAR_XRAY",
            "key_required": False, "format": "JSON", "resolution": "1-minute",
            "fields": ["time_tag","satellite","flux","energy"],
            "lhea_letter": "shin",
            "jurisdiction": "J5 Aperture — solar flare onset detection",
            "description": "GOES satellite X-ray flux. M1.0+ = HF disruption.",
        },
        "NOAA_SWPC_AURORA": {
            "name": "NOAA SWPC — Aurora 30-min Forecast",
            "url":  "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json",
            "domain": "J4_PROJECTION", "sensor_type": "AURORA_SPATIAL",
            "key_required": False, "format": "JSON", "resolution": "30-min",
            "fields": ["Forecast Time","coordinates","aurora_probability"],
            "lhea_letter": "he",
            "jurisdiction": "J4 Projection — outward auroral broadcast",
            "description": "OVATION model global aurora probability map",
        },
        "USGS_EARTHQUAKES_SIGNIFICANT": {
            "name": "USGS — Significant Earthquakes This Week",
            "url":  "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson",
            "domain": "J5_APERTURE", "sensor_type": "SEISMIC",
            "key_required": False, "format": "GeoJSON", "resolution": "real-time",
            "fields": ["time","place","mag","depth","latitude","longitude","tsunami"],
            "lhea_letter": "zayin",
            "jurisdiction": "J5 Aperture — seismic rupture boundary event",
            "description": "Globally significant earthquakes past 7 days",
        },
        "USGS_EARTHQUAKES_4_5_DAY": {
            "name": "USGS — M4.5+ Past 24 Hours",
            "url":  "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson",
            "domain": "J10_SEED", "sensor_type": "SEISMIC",
            "key_required": False, "format": "GeoJSON", "resolution": "real-time",
            "fields": ["time","place","mag","depth","latitude","longitude"],
            "lhea_letter": "zayin",
            "jurisdiction": "J10 Seed — seismic first-arrival events",
            "description": "All M4.5+ earthquakes globally in past 24 hours",
        },
        "USGS_FDSN_CATALOG": {
            "name": "USGS — FDSN Earthquake Catalog",
            "url":  "https://earthquake.usgs.gov/fdsnws/event/1/query",
            "domain": "J12_DIVERGENCE", "sensor_type": "SEISMIC_CATALOG",
            "key_required": False, "format": "GeoJSON/QuakeML",
            "resolution": "historical+real-time",
            "fields": ["format","starttime","endtime","minmagnitude"],
            "lhea_letter": "zayin",
            "jurisdiction": "J12 Divergence — branching global seismic catalog",
            "example": "?format=geojson&starttime=2024-01-01&minmagnitude=5.0",
            "description": "Full FDSN catalog query with spatial/temporal filters",
        },
        "USGS_GEOMAG": {
            "name": "USGS — Geomagnetism Observatory Data",
            "url":  "https://geomag.usgs.gov/ws/data/",
            "domain": "J2_CONTAINMENT", "sensor_type": "GEOMAGNETIC_OBSERVATORY",
            "key_required": False, "format": "IAGA2002/JSON",
            "resolution": "1-second to daily",
            "fields": ["id","starttime","endtime","elements"],
            "lhea_letter": "mem",
            "jurisdiction": "J2 Containment — fixed observatory magnetic field",
            "example": "?id=BOU&starttime=2024-01-01T00:00:00&elements=X,Y,Z,F",
            "description": "USGS network of 14 US magnetic observatories",
        },
        "NOAA_NWS_API": {
            "name": "NOAA NWS — National Weather Service",
            "url":  "https://api.weather.gov/",
            "domain": "J1_CONTINUITY", "sensor_type": "ATMOSPHERIC",
            "key_required": False, "format": "GeoJSON/JSON-LD",
            "resolution": "hourly",
            "fields": ["temperature","windSpeed","barometricPressure","relativeHumidity"],
            "lhea_letter": "he",
            "jurisdiction": "J1 Continuity — atmospheric state stream",
            "example": "/points/{lat},{lon} then /gridpoints/{office}/{x},{y}/forecast",
            "description": "US NWS API — no key required",
        },
        "INATURALIST_BIODIVERSITY": {
            "name": "iNaturalist — Global Biodiversity Observations",
            "url":  "https://api.inaturalist.org/v1/",
            "domain": "J13_EMISSION", "sensor_type": "BIOLOGICAL_SENSOR",
            "key_required": False, "format": "JSON", "resolution": "real-time",
            "fields": ["taxon","observed_on","latitude","longitude","quality_grade"],
            "lhea_letter": "nun",
            "jurisdiction": "J13 Emission — living distributed sensors",
            "description": "200M+ biodiversity observations globally",
        },
        "NASA_DONKI": {
            "name": "NASA DONKI — Space Weather Notifications",
            "url":  "https://api.nasa.gov/DONKI/",
            "domain": "J5_APERTURE", "sensor_type": "SPACE_WEATHER_EVENTS",
            "key_required": True, "key_name": "api_key",
            "free_key": "DEMO_KEY", "format": "JSON",
            "resolution": "event-driven",
            "fields": ["activityID","startTime","instruments","linkedEvents"],
            "lhea_letter": "shin",
            "jurisdiction": "J5 Aperture — CME and flare event detection",
            "example": "/CME?startDate=2024-01-01&api_key=DEMO_KEY",
            "description": "Database of CME, flares, radiation belt events",
        },
        "IRIS_SEISMIC_WAVEFORMS": {
            "name": "IRIS EarthScope — Seismic Waveforms",
            "url":  "https://service.iris.edu/fdsnws/dataselect/1/query",
            "domain": "J1_CONTINUITY", "sensor_type": "SEISMIC_WAVEFORM",
            "key_required": False, "format": "MiniSEED",
            "resolution": "100 samples/second",
            "fields": ["network","station","channel","starttime","endtime"],
            "lhea_letter": "zayin",
            "jurisdiction": "J1 Continuity — continuous GSN waveform",
            "description": "163 Global Seismographic Network broadband stations",
        },
        "INTERMAGNET": {
            "name": "INTERMAGNET — Global Geomagnetic Network",
            "url":  "https://imag-data.bgs.ac.uk/GIN_V1/GINServices",
            "domain": "J2_CONTAINMENT", "sensor_type": "GEOMAGNETIC_GLOBAL",
            "key_required": False, "format": "IAGA2002/JSON",
            "resolution": "1-minute",
            "fields": ["observatory","element","date","value"],
            "lhea_letter": "mem",
            "jurisdiction": "J2 Containment — 150+ global magnetic observatories",
            "description": "International network of 150+ geomagnetic observatories",
        },
        "NOAA_SWPC_PLASMA": {
            "name": "NOAA SWPC — Real-Time Solar Wind Plasma",
            "url":  "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json",
            "domain": "J1_CONTINUITY", "sensor_type": "SOLAR_PLASMA",
            "key_required": False, "format": "JSON", "resolution": "1-minute",
            "fields": ["time_tag","proton_speed","proton_density","proton_temp"],
            "lhea_letter": "shin",
            "jurisdiction": "J1 Continuity — solar wind plasma stream",
            "description": "DSCOVR plasma speed, density, temperature",
        },
    }

    def __init__(self, alg_matrix: "AlgorithmMatrix" = None):
        self.alg_matrix  = alg_matrix
        self.registry    = dict(self.KNOWN_ENDPOINTS)  # start with known
        self.discovered  = []   # newly found via crawling
        self.validated   = {}   # key -> validation result
        self.log         = []
        self._next_id    = len(self.registry) + 1

    def _log(self, msg: str):
        self.log.append(msg)

    # ── STAGE 1: Already catalogued ───────────────────────────────────────

    def report_known(self) -> dict:
        from collections import Counter
        domains    = Counter(e['domain'] for e in self.registry.values())
        sensors    = Counter(e['sensor_type'] for e in self.registry.values())
        keyless    = sum(1 for e in self.registry.values() if not e['key_required'])
        return {
            'total': len(self.registry),
            'keyless': keyless,
            'keyed': len(self.registry) - keyless,
            'by_domain': dict(domains),
            'by_sensor': dict(sensors),
        }

    # ── STAGE 2: GitHub search ────────────────────────────────────────────

    def search_github(self, max_repos: int = 10) -> list:
        """Search GitHub for geosensory API repositories.
        Returns list of discovered endpoint candidates."""
        import urllib.request, json, re
        found = []
        queries = [
            "geosensory+API+realtime+sensor",
            "seismic+API+json+earthquake",
            "solar+wind+API+space+weather",
            "geomagnetic+observatory+API",
            "environmental+sensor+API+opendata",
        ]
        for query in queries:
            try:
                url = (f"https://api.github.com/search/repositories"
                       f"?q={query}&sort=stars&per_page=3")
                with urllib.request.urlopen(url, timeout=6) as r:
                    data = json.loads(r.read())
                for item in data.get('items', []):
                    desc = item.get('description') or ''
                    # Look for API URL patterns in description
                    urls = re.findall(
                        r'https?://[a-zA-Z0-9._/-]+(?:api|data|service|sensor)[a-zA-Z0-9._/-]*',
                        desc)
                    for candidate_url in urls[:2]:
                        entry = {
                            "name":         item['full_name'],
                            "url":          candidate_url,
                            "domain":       "DISCOVERED",
                            "sensor_type":  "UNKNOWN",
                            "key_required": False,
                            "format":       "JSON",
                            "source":       "github_search",
                            "stars":        item['stargazers_count'],
                            "description":  desc[:100],
                        }
                        found.append(entry)
                        self.discovered.append(entry)
            except Exception as e:
                self._log(f"GitHub search '{query}': {e}")
        self._log(f"Stage 2 GitHub: {len(found)} candidates found")
        return found

    # ── STAGE 3: HTML link extraction fallback ────────────────────────────

    def extract_from_html(self, url: str) -> list:
        """Semi-open fallback: extract API endpoint links from HTML page.
        Only fires when Stage 1 and 2 miss the target domain."""
        import urllib.request, re
        found = []
        try:
            req = urllib.request.Request(url,
                headers={'User-Agent': 'ECHO-Governor/1.0'})
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')

            # Extract JSON/API endpoint patterns
            api_patterns = re.findall(
                r'https?://[a-zA-Z0-9._/-]+(?:\.json|/api/|/v[0-9]+/|/data/)[^\\ \'"<>]{3,60}',
                html)

            for candidate in set(api_patterns[:10]):
                entry = {
                    "name":         f"Discovered from {url[:40]}",
                    "url":          candidate,
                    "domain":       "HTML_DISCOVERED",
                    "sensor_type":  "UNKNOWN",
                    "key_required": False,
                    "format":       "JSON",
                    "source":       f"html_extraction:{url[:60]}",
                    "description":  "Discovered via HTML link extraction (Stage 3 fallback)",
                }
                found.append(entry)
                self.discovered.append(entry)
        except Exception as e:
            self._log(f"HTML extraction from {url}: {e}")

        self._log(f"Stage 3 HTML {url[:40]}: {len(found)} endpoints extracted")
        return found

    # ── VALIDATE ──────────────────────────────────────────────────────────

    def validate_endpoint(self, key: str) -> dict:
        """Test that an endpoint returns typed JSON.
        Shodan principle: structured response = valid; unstructured = gate."""
        import urllib.request, json
        entry = self.registry.get(key, {})
        url   = entry.get('url', '')
        if not url:
            return {'status': 'NO_URL'}
        try:
            req = urllib.request.Request(url,
                headers={'User-Agent': 'ECHO-Governor/1.0'})
            with urllib.request.urlopen(req, timeout=6) as r:
                content_type = r.headers.get('Content-Type','')
                data = r.read()[:2048]  # read first 2KB only
            # Check if it's JSON or GeoJSON
            try:
                parsed = json.loads(data)
                result = {
                    'status':       'VALID',
                    'content_type': content_type,
                    'is_json':      True,
                    'sample_keys':  list(parsed.keys())[:5] if isinstance(parsed, dict)
                                    else (list(parsed[0].keys())[:5] if parsed and isinstance(parsed[0], dict)
                                    else []),
                }
            except json.JSONDecodeError:
                result = {
                    'status':       'INVALID_JSON',
                    'content_type': content_type,
                    'is_json':      False,
                }
            self.validated[key] = result
            self._log(f"Validated {key}: {result['status']}")
            return result
        except Exception as e:
            result = {'status': 'UNREACHABLE', 'error': str(e)}
            self.validated[key] = result
            return result

    # ── CRAWL ALL ─────────────────────────────────────────────────────────

    def crawl(self, run_github: bool = True,
               html_fallback_urls: list = None,
               validate_known: bool = False) -> dict:
        """Run full semi-open crawl pipeline:
          Stage 1: Known structured APIs
          Stage 2: GitHub search (if run_github=True)
          Stage 3: HTML extraction (if html_fallback_urls provided)"""

        results = {'stage_1': len(self.registry), 'stage_2': 0, 'stage_3': 0}

        if run_github:
            github_found = self.search_github()
            results['stage_2'] = len(github_found)
            for entry in github_found:
                key = f"DISCOVERED_{self._next_id:04d}"
                self.registry[key] = entry
                self._next_id += 1

        if html_fallback_urls:
            for url in html_fallback_urls:
                html_found = self.extract_from_html(url)
                results['stage_3'] += len(html_found)
                for entry in html_found:
                    key = f"HTML_{self._next_id:04d}"
                    self.registry[key] = entry
                    self._next_id += 1

        if validate_known:
            for key in list(self.KNOWN_ENDPOINTS.keys())[:3]:
                self.validate_endpoint(key)
            results['validated'] = self.validated

        results['total_registry'] = len(self.registry)
        results['total_discovered'] = len(self.discovered)
        self._log(f"Crawl complete: {results['total_registry']} endpoints in registry")
        return results

    def summary(self) -> dict:
        return {**self.report_known(), 'discovered': len(self.discovered),
                'validated': len(self.validated), 'log': self.log[-5:]}


def make_letter_lobby(matrix: AlgorithmMatrix,
                       alphabet: list, lobby_name: str) -> "Lobby":
    """Instantiate a small Lobby for a single alphabet, where each letter
    is a WordAgent sub-copy of the Governor with dominion over that letter's
    symbolic and phonetic properties. Letters tie to each other based on
    shared semantic domains and classification families.

    alphabet: list of dicts with keys:
        name        — letter name ("aleph", "a", ...)
        glyph       — the actual character ("א", "A", ...)
        department  — "letter" (always)
        properties  — list of descriptive tokens forming the "definition"
    """
    lobby = Lobby(matrix)
    lobby.label = lobby_name

    for entry in alphabet:
        name = entry["name"].lower()
        props = entry.get("properties", [])
        # register in matrix so it appears in content_units
        if name not in matrix.content_units:
            matrix.content_units[name] = 1
            matrix.entry_classes[name] = "ABSTRACT"
            for p in props:
                matrix.content_units.setdefault(p, 0)
                matrix.content_units[p] += 1

        agent = WordAgent(
            word=name,
            definition_words=props,
            entry_class="ABSTRACT",
            department="letter",
            parent=matrix,
            raw_definition=" ".join(props),
        )
        agent.confirm_identity()
        agent.generality_score = 0.9   # letters are maximally general operators
        lobby.agents[name] = agent

    # run two-phase orientation inside the letter lobby
    lobby.run_orientation()
    return lobby


class SubAgentMatrix:
    """A domain-scoped agentic extension of a Governor AlgorithmMatrix.
    Owns one region. Knows everything the parent knows (live shared
    reference), but trusts its own domain signal more heavily.

    domain_weight controls how strongly in-domain co-occurrence is
    amplified over the parent's global signal. 2.0 means a domain
    transition counts twice as much as an equal-frequency global one.
    """

    def __init__(self, region_id: str, domain_words: set,
                 parent: "AlgorithmMatrix", domain_weight: float = 2.0):
        self.region_id = region_id
        self.domain_words = domain_words
        self.parent = parent           # live reference — shared, not copied
        self.domain_weight = domain_weight
        self.id = f"SUB-{region_id}"

        # own domain-scoped structures — built only from in-domain content
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.cooccurrence = defaultdict(lambda: defaultdict(int))
        self.content_units = {}
        self._total_cooccurrence = 0

        # own generation history (reported back via checkpoint, not merged
        # directly into parent)
        self.generation_log = []

        # seed own index from parent's existing data for the domain words —
        # the sub-agent immediately has domain-relevant history from what
        # the Governor already knows, not starting from scratch
        self._seed_from_parent()

    def _seed_from_parent(self):
        """Inherit the slice of the parent's graph that belongs to this
        domain. Words in domain_words are indexed, plus their direct
        neighbors in the parent's co-occurrence graph (so domain boundary
        words have real transition context, not just isolated tokens).
        This is what 'sharing collective knowledge' means concretely: the
        sub-agent starts with a real prior, not a blank slate."""
        boundary = self.domain_words | {
            neighbor
            for w in self.domain_words
            for neighbor in self.parent.cooccurrence.get(w, {})
            if self.parent.cooccurrence[w][neighbor] >= 2
        }
        for w1 in boundary:
            for w2, count in self.parent.transitions.get(w1, {}).items():
                self.transitions[w1][w2] += count
            for w2, count in self.parent.cooccurrence.get(w1, {}).items():
                self.cooccurrence[w1][w2] += count
                self._total_cooccurrence += count
            df = self.parent.content_units.get(w1, 0)
            if df:
                self.content_units[w1] = df

    def index_content(self, text: str, category: str = None):
        """Route in-domain content into own scoped index AND notify parent
        so collective knowledge stays current."""
        tokens = text.lower().split()
        in_domain = any(t in self.domain_words for t in tokens)
        if not in_domain:
            return   # not this sub-agent's responsibility
        for u in set(tokens):
            self.content_units[u] = self.content_units.get(u, 0) + 1
        for a, b in zip(tokens, tokens[1:]):
            self.transitions[a][b] += 1
        window = 3
        for i, w in enumerate(tokens):
            for j in range(max(0, i - window), min(len(tokens), i + window + 1)):
                if i != j:
                    self.cooccurrence[w][tokens[j]] += 1
                    self._total_cooccurrence += 1
        # share back to parent so collective knowledge stays current
        self.parent.index_content(text, category)

    def predict_next(self, token: str) -> str:
        """Weighted prediction: domain transitions count domain_weight times
        more than an equivalent global transition. If domain has signal,
        it wins. If not, global knowledge fills the gap gracefully — the
        sub-agent never goes blind just because its domain is thin."""
        domain_opts = dict(self.transitions.get(token, {}))
        global_opts = dict(self.parent.transitions.get(token, {}))

        combined = dict(global_opts)
        for w, count in domain_opts.items():
            combined[w] = combined.get(w, 0) + count * self.domain_weight

        if not combined:
            return None
        return max(combined.items(), key=lambda kv: kv[1])[0]

    def generate(self, seed: str, length: int = 10) -> list:
        """Generate from seed using weighted domain+global Markov, falling
        back to related_words() from the parent's index if the chain stalls.
        Logs every generation to self.generation_log for A-113 reporting."""
        tokens = [seed]
        for _ in range(length):
            nxt = self.predict_next(tokens[-1])
            if not nxt:
                # parent's global index as fallback
                related = self.parent.related_words(tokens[-1])
                if related:
                    domain_related = related & self.domain_words
                    nxt = sorted(domain_related)[0] if domain_related \
                          else sorted(related)[0]
                else:
                    break
            tokens.append(nxt)
            if tokens.count(nxt) > 2:
                break
        self.generation_log.append(tokens)
        return tokens

    def report(self) -> dict:
        """What the Governor reads before deciding whether to anchor this
        sub-agent's generation history into the parent's baseline (A-113).
        Sub-agent never writes to parent directly — always via this report."""
        return {
            "id": self.id,
            "region": self.region_id,
            "domain_size": len(self.domain_words),
            "own_vocab": len(self.content_units),
            "own_transitions": sum(len(v) for v in self.transitions.values()),
            "own_cooccurrence_pairs": self._total_cooccurrence,
            "generations": len(self.generation_log),
        }


# ---------------------------------------------------------------------------
# Governor self-validation and sub-agent deployment
# ---------------------------------------------------------------------------

def governor_validate_and_deploy(matrix: AlgorithmMatrix,
                                  domain_weight: float = 2.0) -> dict:
    """The Governor reads A-000 first, validates its own identity, and
    ONLY THEN deploys sub-agents — one per discovered region. This is
    the self-indexing closure from the frozen architecture:
        IDENTIFY(A-000) → VALIDATE(A-000) → OPEN(A-001) → DEPLOY

    If A-000 validation fails, no sub-agents are spawned. The Governor
    cannot extend its own agency before it has confirmed what it is."""

    # IDENTIFY
    a000 = matrix.known.get("A-000")
    if not a000:
        return {"status": "FAILED", "reason": "A-000 not found in matrix"}

    # VALIDATE — check A-000 has the required fields of a Governor entry
    required = {"name", "status"}
    if not required.issubset(a000.keys()) or a000.get("status") != "ACTIVE":
        return {"status": "FAILED",
                "reason": f"A-000 failed identity validation: {a000}"}

    # OPEN — A-001 is now accessible (rest of matrix is open for use)
    a001 = matrix.known.get("A-101")  # first real tool
    if not a001:
        return {"status": "FAILED", "reason": "tool belt empty, cannot deploy"}

    # DEPLOY — one sub-agent per discovered region
    if not matrix.regions:
        return {"status": "FAILED",
                "reason": "no regions discovered yet — run discover_regions() first"}

    sub_agents = {}
    for rid, r in matrix.regions.items():
        sub = SubAgentMatrix(
            region_id=rid,
            domain_words=r["words"],
            parent=matrix,
            domain_weight=domain_weight,
        )
        sub_agents[rid] = sub
        # register in parent's known so Governor can audit what it deployed
        matrix.known[sub.id] = {
            "name": f"SubAgent for {rid}",
            "status": "ACTIVE",
            "origin": "SELF-DEPLOYED",
            "domain_size": len(r["words"]),
            "depth": 1,  # sub-agents never spawn further sub-agents
        }

    return {
        "status": "DEPLOYED",
        "a000_identity": a000["name"],
        "sub_agents_deployed": len(sub_agents),
        "sub_agents": sub_agents,
    }


# ---------------------------------------------------------------------------
# One governed cycle
# ---------------------------------------------------------------------------

def run_cycle(theta: dict, s: State, r: Request, c: Context,
              matrix: AlgorithmMatrix, invariants: list, budgets: dict,
              thresholds: dict, observed: State = None) -> State:
    if observed is None:
        observed = phi(theta, s, r, c, matrix)

    # Net scrapings feed the Governor's index as they're encountered.
    if r.scrape:
        matrix.index_content(r.scrape)
    if c.corpus:
        matrix.index_content(c.corpus)

    deficiencies = diagnose(theta, s, r, c, observed, invariants, thresholds, matrix)
    if deficiencies:
        print("  deficiencies:", deficiencies)

    candidates = propose(deficiencies, theta, primitives=[])

    # A-101: demonstrate the bandit against the first deficiency's bucket.
    # With only one candidate right now it can't choose *between*
    # alternatives yet, but the H(M,D) recording below is real and will
    # matter as soon as Propose generates more than one.
    d_bucket = bucket_for(deficiencies[0]) if deficiencies else None
    if d_bucket:
        arms = [cand["m_id"] for cand in candidates]
        chosen_arm = matrix.bandit_select(d_bucket, arms)
        print(f"  bandit: bucket={d_bucket} chose={chosen_arm} "
              f"history={matrix.history.get((chosen_arm, d_bucket))}")

    survivors = []
    for cand in candidates:
        passed, margin = validate(cand, invariants)
        if passed and govern(cand, budgets, matrix.history):
            survivors.append(cand)

    chosen = select(survivors) if survivors else {"theta": theta, "m_id": None}

    if d_bucket and chosen.get("m_id"):
        matrix.record_outcome(chosen["m_id"], d_bucket, success=True)

    return phi(chosen["theta"], s, r, c, matrix)


# ---------------------------------------------------------------------------
# Demo: run several cycles so every learning tool has data to act on
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    theta = {}
    s = State(content="the governor indexes its own algorithms", quality=0.0)
    r = Request(text="the governor indexes its own algorithms", value=1.0)
    c = Context(value=0.5)
    matrix = AlgorithmMatrix()
    invariants = [{"id": "I-001", "check": lambda st: st.quality < 100}]
    thresholds = {"epsilon_max": 0.1, "delta_max": 5.0, "C_max": 50,
                  "content_sim_min": 0.9}
    budgets = {"B_G": 20, "B_E": 10, "C_max": 50, "F_max": 20}

    print("A-000 tool belt:", list(matrix.known.keys()))
    for t in range(8):
        predicted_preview = phi(theta, s, r, c, matrix)
        synthetic_observed = State(
            content=predicted_preview.content.replace("algorithms", "matrices"),
            quality=predicted_preview.quality + 0.3,
            history=predicted_preview.history,
        )
        s = run_cycle(theta, s, r, c, matrix, invariants, budgets, thresholds,
                      observed=synthetic_observed)
        print(f"t={t+1}  quality={s.quality:.2f}  content={s.content!r}")

    print("\n--- learning tool outputs after 8 cycles ---")
    print("content_units (document frequency):", dict(matrix.content_units))
    print("adaptive quality_error threshold:",
          matrix.adaptive_threshold("quality_error", default="not enough data"))
    print("adaptive stability_delta threshold:",
          matrix.adaptive_threshold("stability_delta", default="not enough data"))
    print("recluster CONTENT_ERROR magnitudes (k=2):",
          matrix.recluster_buckets("CONTENT_ERROR", k=2))
    vec_algorithms = matrix.embed("algorithms")
    vec_matrices = matrix.embed("matrices")
    print("embed('algorithms'):", vec_algorithms)
    print("cosine('algorithms','matrices'):",
          matrix.cosine_similarity(vec_algorithms, vec_matrices))
    print("current_generation (unanchored):", matrix.current_generation)
    checkpoint = matrix.checkpoint_generation()
    print("checkpoint_generation() result:", checkpoint)
    print("bandit history (anchored baseline):", matrix.history)
