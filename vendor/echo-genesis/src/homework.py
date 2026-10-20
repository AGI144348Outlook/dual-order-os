"""
ECHO Governor — Library Matrix, Homework Matrix, librarians, recursion.

Roles (as specified by Timothy):
  LIBRARY   = bodies of information WE give the Governor (documents).
  HOMEWORK  = what the Governor must seek out for itself. Rows are written
              by the Governor from its own gaps, not by us.
  LIBRARIANS = the executors that go and fetch (full thesaurus now, Wikipedia
              when the network allows), so homework rows can be completed.

Matrix/Index rule (dual-order-os RFC §2): every part is reachable both ways.
  HomeworkMatrix rows are indexed by word, by status and by origin.
Repeat activation, not repeat nodes (RFC §5.5): re-assigning a word that
already has a row logs an activation on that row instead of adding a copy.

The recursion: finished homework can reveal new unknown words (in the
definitions / articles it just read) -> new rows one level deeper, until the
depth cap, the per-level budget, or no-new-gaps stops it.
"""
import json
import re
from collections import Counter, defaultdict

WORD = re.compile(r"[a-z][a-z'-]{2,}")


# ── LIBRARY: what we give it ─────────────────────────────────────────────
class LibraryMatrix:
    def __init__(self):
        self.docs = {}                      # doc_id -> {"title","text","given_by"}

    def add(self, doc_id: str, title: str, text: str, given_by: str = "user"):
        self.docs[doc_id] = {"title": title, "text": text, "given_by": given_by}

    def word_freq(self) -> Counter:
        c = Counter()
        for d in self.docs.values():
            c.update(WORD.findall(d["text"].lower()))
        return c

    def context_neighbors(self, word: str, known, window: int = 3,
                          stop=frozenset()) -> list:
        """Known words that sit next to `word` in the Library — the
        neighbors that will be assigned to study it with the word."""
        near = Counter()
        for d in self.docs.values():
            toks = WORD.findall(d["text"].lower())
            for i, t in enumerate(toks):
                if t == word:
                    for u in toks[max(0, i - window): i + window + 1]:
                        if u != word and u in known and u not in stop and len(u) > 3:
                            near[u] += 1
        return [w for w, _ in near.most_common(6)]


# ── HOMEWORK: what it must seek out ──────────────────────────────────────
class HomeworkMatrix:
    def __init__(self):
        self.rows = {}
        self.by_word = {}
        self.by_status = defaultdict(set)
        self.by_origin = defaultdict(set)
        self._n = 0

    def assign(self, word, reason, origin, depth=0, parent=None,
               neighbors=None, priority=0.0):
        if word in self.by_word:                      # repeat activation
            row = self.rows[self.by_word[word]]
            row["activations"] += 1
            row["priority"] = max(row["priority"], priority)
            return row["id"]
        self._n += 1
        rid = f"HW-{self._n:04d}"
        row = {"id": rid, "word": word, "reason": reason, "origin": origin,
               "depth": depth, "parent": parent, "neighbors": neighbors or [],
               "priority": priority, "status": "PENDING", "activations": 1,
               "source": None, "vocab_added": 0}
        self.rows[rid] = row
        self.by_word[word] = rid
        self.by_status["PENDING"].add(rid)
        self.by_origin[origin].add(rid)
        return rid

    def set_status(self, rid, status, **fields):
        row = self.rows[rid]
        self.by_status[row["status"]].discard(rid)
        row["status"] = status
        row.update(fields)
        self.by_status[status].add(rid)

    def pending(self, depth=None):
        rows = [self.rows[r] for r in self.by_status["PENDING"]]
        if depth is not None:
            rows = [r for r in rows if r["depth"] == depth]
        return sorted(rows, key=lambda r: -r["priority"])


# ── LIBRARIANS: executors ────────────────────────────────────────────────
class ThesaurusLibrarian:
    """Looks a word up in the FULL WordNet-derived thesaurus (the Governor
    normally indexes only a 2,000-entry sample of it)."""
    name = "thesaurus"

    def __init__(self, path: str):
        self.by_word = defaultdict(list)
        with open(path, encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                if e.get("desc"):
                    self.by_word[e["word"].lower()].append(e)

    def fetch_into(self, matrix, word: str):
        """Ingest entries for `word`. Returns (texts_read, n_entries)."""
        entries = self.by_word.get(word, [])
        texts = []
        for e in entries[:4]:
            desc = " ".join(e["desc"])
            matrix.index_dictionary_entry(
                e["word"], desc, pos=e.get("pos"),
                synonyms=e.get("synonyms", []), category="homework_thesaurus")
            texts.append(desc + " " + " ".join(e.get("synonyms", [])))
        return texts, len(entries)


class WikiLibrarian:
    """Fetches an article via wiki_crawler.WikiCrawler and indexes its
    paragraphs. Needs network access to en.wikipedia.org."""
    name = "wikipedia"

    def __init__(self, crawler):
        self.crawler = crawler

    def fetch_into(self, matrix, word: str):
        from wiki_crawler import clean_extract
        page = self.crawler.get_page(word)
        if page is None:
            return [], 0
        canon, extract, _ = page
        paras = clean_extract(extract)
        for p in paras:
            matrix.index_content(p, category=f"homework_wiki:{canon}")
        return paras, len(paras)


# ── THE GOVERNOR WRITES ITS OWN HOMEWORK ────────────────────────────────
def derive_homework(matrix, library, homework, stopwords, top_n=40,
                    echo_targets=None, echo_origin="echo-hypothesis",
                    known_before=None):
    """Rows written from the Governor's own state:
      * echo_targets — target words from its own DATA_ACQUISITION hypothesis
      * UNKNOWN      — words in the Library it has no entry for
      * NO_REGION    — words it knows but that sit in no region (no partners)
    Priority = frequency in the Library (what we actually gave it)."""
    freq = library.word_freq()
    known = set(matrix.content_units)
    gap_ref = known_before if known_before is not None else known
    for w in (echo_targets or []):
        homework.assign(w, "ECHO_DERIVED_GAP", echo_origin,
                        neighbors=library.context_neighbors(w, known, stop=stopwords),
                        priority=freq.get(w, 0) + 1)
    cands = []
    for w, n in freq.items():
        if len(w) < 4 or w in stopwords:
            continue
        if w not in gap_ref:
            cands.append((n, w, "UNKNOWN"))
        elif not matrix.word_to_region.get(w):
            cands.append((n * 0.5, w, "NO_REGION"))
    cands.sort(reverse=True)
    for n, w, why in cands[:top_n]:
        homework.assign(w, why, "library-gap",
                        neighbors=library.context_neighbors(w, known, stop=stopwords),
                        priority=n)


# ── RECURSION ────────────────────────────────────────────────────────────
def do_homework(matrix, homework, librarians, stopwords, max_depth=2,
                budget_per_depth=30, log=print):
    """Depth-limited recursion over the Homework Matrix."""
    for depth in range(max_depth + 1):
        todo = homework.pending(depth)[:budget_per_depth]
        if not todo:
            log(f"  depth {depth}: nothing pending -> stop")
            break
        log(f"  depth {depth}: {len(todo)} assignments")
        spawned = Counter()
        for row in todo:
            before = len(matrix.content_units)
            got, src = [], None
            for lib in librarians:
                try:
                    texts, n = lib.fetch_into(matrix, row["word"])
                except Exception as e:                  # network etc.
                    homework.set_status(row["id"], "ERROR", source=lib.name,
                                        error=str(e)[:80])
                    texts, n = [], 0
                    continue
                if n:
                    got, src = texts, lib.name
                    break
            if not got:
                if row["status"] == "PENDING":
                    homework.set_status(row["id"], "NO_SOURCE")
                continue
            added = len(matrix.content_units) - before
            homework.set_status(row["id"], "DONE", source=src,
                                vocab_added=added)
            if depth < max_depth:                       # recursion: new gaps
                known = set(matrix.content_units)
                for t in got:
                    for w in WORD.findall(t.lower()):
                        if len(w) >= 4 and w not in stopwords and w not in known:
                            spawned[w] += 1
        for w, n in spawned.most_common(budget_per_depth):
            homework.assign(w, "UNKNOWN_IN_HOMEWORK", "recursion",
                            depth=depth + 1, parent=f"depth{depth}",
                            priority=n)
        log(f"    spawned {min(len(spawned), budget_per_depth)} deeper assignments")
