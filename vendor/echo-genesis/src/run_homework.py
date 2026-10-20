"""Library -> Echo derives its own homework -> librarians -> recursion -> measure."""
import sys, json, re, time, os
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/home/claude/x/echo-governor/tests")
sys.path.insert(0, "/home/claude/relay")
from echo_governor_skeleton import (Lobby, LobbyEvolutionGovernor,
                                    HypothesisSandbox, STOPWORDS, DEFINITION_BOILERPLATE)
from governor_exchange import build_governor
from homework import (LibraryMatrix, HomeworkMatrix, ThesaurusLibrarian,
                      derive_homework, do_homework, WORD)
from wiki_crawler import refresh_regions

THESAURUS = "/home/claude/en_thesaurus.jsonl"
LATEX_NOISE = {"rightarrow", "leftrightarrow", "boxed", "text", "frac", "mathbb"}
EXTRA = {"their", "there", "they", "them", "then", "when", "what", "while",
         "would", "about", "more", "most", "some", "also", "because", "just",
         "that's", "it's", "don't", "doesn't", "isn't", "than", "very", "much"}
STOP = set(STOPWORDS) | set(DEFINITION_BOILERPLATE) | LATEX_NOISE | EXTRA

t0 = time.time()
matrix, _ = build_governor()

pre_known = set(matrix.content_units)   # what Echo knew BEFORE the Library

# ── LIBRARY: what we give it ─────────────────────────────────────────────
library = LibraryMatrix()
for did, title, path in [
    ("L1", "Dual-Order OS RFC", "/home/claude/relay/Dual_Ordering_OS_.txt"),
    ("L2", "Dimensionality transcript", "/home/claude/relay/Dimensionality_.txt"),
    ("L3", "A Priori Proposal", "/home/claude/relay/A_Priori_Proposal_.txt"),
]:
    library.add(did, title, open(path, encoding="utf-8", errors="ignore").read())
for d in library.docs.values():
    for p in re.split(r"\n\s*\n", d["text"]):
        p = re.sub(r"\s+", " ", p).strip()
        if len(p.split()) >= 4:
            matrix.index_content(p, category="library")


def content_words():
    return {w for w in library.word_freq() if len(w) >= 4 and w not in STOP}


post_lib = None
done_words = set()


def measure(label):
    cw = content_words()
    grounded = set(pre_known)
    if post_lib is not None:      # words that arrived through homework
        grounded |= (set(matrix.content_units) - post_lib) | done_words
    known = sum(1 for w in cw if w in grounded)
    reg = sum(1 for w in cw if matrix.word_to_region.get(w))
    print(f"  [{label}] Library content words: {len(cw)} | grounded {known} "
          f"({100*known/len(cw):.1f}%) | in a region {reg} ({100*reg/len(cw):.1f}%) "
          f"| vocabulary {len(matrix.content_units)}")
    return known, reg


post_lib = set(matrix.content_units)
print("\nMEASURE 0 — Library given, no homework  (grounded = had an entry BEFORE the Library or arrived via homework)")
base = measure("baseline")

# ── ECHO OBSERVES ITSELF AND DERIVES A GAP HYPOTHESIS ────────────────────
synonyms_map = {}
with open(THESAURUS) as f:
    q = [json.loads(l) for l in f if json.loads(l).get("desc")]
stride = max(1, len(q) // 2000)
for e in q[::stride][:2000]:
    if e.get("synonyms"):
        synonyms_map[e["word"].lower()] = [s.lower() for s in e["synonyms"]]
lobby = Lobby(matrix); lobby.label = "library"
lobby.populate(); lobby.compute_generality_scores(); lobby.run_orientation()
lobby.run_typed_study_groups(); lobby.run_discovery(); lobby.run_thesaurus(synonyms_map)
cands = lobby.propose_from_study_groups(min_total=3, max_total=60)
lobby.commit(lobby.scrutinize(cands, min_coherence=0.2, min_generality_span=0.02))
evgov = LobbyEvolutionGovernor([lobby], label="library")
evgov.evolve(max_generations=5, budget_per_iter=20, target_composite=0.50, verbose=False)
sandbox = HypothesisSandbox(lobby, matrix, evgov)
obs = sandbox.observe()
hyps = sandbox.hypothesize(obs)
print("\nECHO'S OWN OBSERVATION: bottleneck =", obs["bottleneck"],
      "| hypotheses it derived:", [h["name"] for h in hyps])
acq = next((h for h in hyps if h["strategy"] == "DATA_ACQUISITION"), None)
echo_targets = acq["parameters"]["target_words"] if acq else []
if acq:
    print("  Echo's acquisition hypothesis:", acq["name"])
    print("  its target words:", echo_targets, "| isolated words:",
          acq["parameters"]["isolation_count"])
else:
    print("  Echo derived no data-acquisition hypothesis this time.")

# ── ECHO WRITES HOMEWORK, LIBRARIANS DO IT, RECURSION RUNS ───────────────
homework = HomeworkMatrix()
derive_homework(matrix, library, homework, STOP, top_n=40,
                echo_targets=echo_targets,
                echo_origin=acq["id"] if acq else "echo-hypothesis",
                known_before=pre_known)
print(f"\nHOMEWORK MATRIX written: {len(homework.rows)} rows "
      f"(by origin: { {k: len(v) for k, v in homework.by_origin.items()} })")
top = homework.pending()[:10]
for r in top:
    print(f"  {r['id']} {r['word']:<16} {r['reason']:<10} prio={r['priority']:<5} "
          f"neighbors={r['neighbors'][:4]}")

print("\nLIBRARIAN: full thesaurus (Wikipedia offline in this sandbox)")
libn = ThesaurusLibrarian(THESAURUS)
if os.environ.get("NOHW"):
    print("  CONTROL RUN: homework skipped")
else:
    do_homework(matrix, homework, [libn], STOP, max_depth=2, budget_per_depth=30)

st = {k: len(v) for k, v in homework.by_status.items() if v}
print("\nHOMEWORK STATUS:", st)
done = [r for r in homework.rows.values() if r["status"] == "DONE"]
done_words |= {r["word"] for r in done}
print("Completed examples:", [(r["word"], r["depth"], r["vocab_added"]) for r in done[:8]])
nosrc = [r["word"] for r in homework.rows.values() if r["status"] == "NO_SOURCE"]
print("No source found (waiting on Wikipedia librarian):", nosrc[:20])

print("\nMEASURE 1 — after homework (regions not yet rebuilt)")
m1 = measure("after homework")
n = refresh_regions(matrix)
print(f"Regions rebuilt: {n}")
m2 = measure("after region rebuild")
print(f"\nRuntime {time.time()-t0:.1f}s")
