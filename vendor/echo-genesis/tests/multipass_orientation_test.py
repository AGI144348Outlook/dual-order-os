"""
ECHO Governor — Multi-pass orientation test.

Four orientation passes, each building on the last:
  Pass 1  — word-by-word ties (already run, same as before)
  Pass 2A — study group proposals: full definition sentence as curriculum
  Pass 2B — discovery: agents find themselves in others' entries
  Pass 3  — thesaurus enrichment: synonyms teach and learn

Shows the three membership roles that emerge:
  LEADER    — proposed the study, their definition IS the curriculum
  INVITED   — explicitly mentioned in the leader's definition (called in)
  FOUND     — found the leader's word in their OWN definition (came on their own)
  THESAURUS — arrived via synonym connection in Pass 3
"""

import sys, json, re, time
sys.path.insert(0, "/home/claude")
from echo_governor_skeleton import AlgorithmMatrix, Lobby, STOPWORDS, DEFINITION_BOILERPLATE
from import_hebrew_demo import (HEBREW_LETTERS, HEBREW_ROOTS, EN_HE_DICT,
    letter_content, root_content, dict_content)

THESAURUS = "/home/claude/en_thesaurus.jsonl"
BDB       = "/home/claude/lattice-workbench/repo/data/raw/DictBDB.json"


def clean_html(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&#x[0-9a-fA-F]+;", "", text)
    text = re.sub(r"&amp;", "and", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_bdb(raw):
    clean = clean_html(raw)
    m = re.match(r"H\d+\.\s+(\w+)\s+(\w+)\s+([\w\s]+)", clean)
    if m:
        hw = m.group(1)
        pos = m.group(2) if m.group(2) in ("verb","noun","adj") else None
        gloss = re.sub(r"\b[A-Z]{2,}\b", "", m.group(3)).strip()
    else:
        words = clean.split()
        hw = words[1] if len(words) > 1 else ""
        pos, gloss = None, " ".join(words[2:10])
    return hw, pos, gloss


if __name__ == "__main__":
    t0 = time.time()
    matrix = AlgorithmMatrix()
    synonyms_map = {}   # word -> [synonyms] — collected during thesaurus ingestion

    # ── INGEST ALL CORPORA ───────────────────────────────────────────────
    print("Ingesting corpora...")

    with open(THESAURUS) as f:
        qualifying = [json.loads(l) for l in f if json.loads(l).get("desc")]
    stride = max(1, len(qualifying) // 2000)
    for entry in qualifying[::stride][:2000]:
        matrix.index_dictionary_entry(
            entry["word"], " ".join(entry["desc"]),
            pos=entry.get("pos"), synonyms=entry.get("synonyms", []),
            category="thesaurus_def")
        # collect synonyms for Pass 3
        if entry.get("synonyms"):
            synonyms_map[entry["word"].lower()] = [
                s.lower() for s in entry["synonyms"]]

    with open(BDB) as f:
        bdb = json.load(f)
    for entry in bdb:
        raw = entry.get("def", "")
        if "<" not in raw: continue
        hw, pos, gloss = extract_bdb(raw)
        if hw and len(gloss.split()) >= 2:
            matrix.index_dictionary_entry(hw, gloss, pos=pos,
                                           category="bdb_hebrew")

    for e in HEBREW_LETTERS:
        matrix.index_content(letter_content(e), category="letter")
    for e in HEBREW_ROOTS:
        matrix.index_content(root_content(e), category="root")
    for e in EN_HE_DICT:
        matrix.index_content(dict_content(e), category="dict")

    print(f"  {len(matrix.content_units)} vocab, {time.time()-t0:.1f}s")

    # ── LOBBY SETUP ──────────────────────────────────────────────────────
    lobby = Lobby(matrix)
    n = lobby.populate()
    lobby.compute_generality_scores()   # needed before study proposals
    print(f"  {n} agents instantiated")

    # ── PASS 1: WORD-BY-WORD TIES ────────────────────────────────────────
    print("\n── PASS 1: word-by-word orientation ──")
    t1 = time.time()
    n_ties = lobby.run_orientation()
    print(f"  {n_ties} ties formed in {time.time()-t1:.3f}s")
    isolated = sum(1 for a in lobby.agents.values() if len(a.ties) == 0)
    print(f"  Isolated agents: {isolated}/{n}")

    # ── PASS 2A: STUDY GROUP PROPOSALS ───────────────────────────────────
    print("\n── PASS 2A: study group proposals (full definition as curriculum) ──")
    t2 = time.time()
    n_groups = lobby.run_study_proposals()
    print(f"  {n_groups} study groups proposed in {time.time()-t2:.3f}s")

    # show largest proposed groups (by INVITED size only — Pass 2B not yet run)
    top_invited = sorted(
        lobby.study_groups.items(),
        key=lambda kv: len(kv[1]["invited"]), reverse=True)[:8]
    print("  Largest study groups by invited count:")
    for word, g in top_invited:
        print(f"    LEADER='{word:20s}' invited={len(g['invited']):4d}  "
              f"dept={g['department']:12s}  curriculum: "
              f"'{g['curriculum'][:60]}...'")

    # ── PASS 2B: DISCOVERY ───────────────────────────────────────────────
    print("\n── PASS 2B: discovery (agents find themselves in others' entries) ──")
    t3 = time.time()
    join_counts = lobby.run_discovery()
    print(f"  Discovery complete in {time.time()-t3:.3f}s")
    found_agents = [(w, c) for w, c in join_counts.items() if c > 0]
    found_agents.sort(key=lambda kv: -kv[1])
    print(f"  Agents who FOUND their way into study groups: {len(found_agents)}")
    print("  Most active discoverers (joined the most study groups):")
    for w, c in found_agents[:10]:
        a = lobby.agents.get(w)
        dept = a.department if a else "?"
        print(f"    '{w:20s}' joined {c:3d} groups  dept={dept}")

    # show a few groups now with their FOUND members
    print("\n  Sample groups after Pass 2B (INVITED + FOUND):")
    for word, g in top_invited[:4]:
        print(f"    '{word}' INVITED={sorted(g['invited'])[:8]}  "
              f"FOUND={sorted(g['found'])[:8]}")

    # ── PASS 3: THESAURUS ENRICHMENT ─────────────────────────────────────
    print("\n── PASS 3: thesaurus enrichment (synonyms teach and learn) ──")
    t4 = time.time()
    stats = lobby.run_thesaurus(synonyms_map)
    print(f"  Synonyms processed: {stats['synonyms_processed']} in {time.time()-t4:.3f}s")
    print(f"  TEACH joins (synonym leads a group → joined as student): {stats['teach_joins']}")
    print(f"  LEARN joins (synonym found in group → discovered it too): {stats['learn_joins']}")

    # ── FULL MEMBERSHIP SNAPSHOTS ─────────────────────────────────────────
    print("\n── FULL STUDY GROUP MEMBERSHIP SNAPSHOTS ──")
    # pick a mix: a large one, a Hebrew/English crossover, a verb, an abstract
    snapshot_words = []
    # largest by total size
    top_total = sorted(lobby.study_groups.items(),
                        key=lambda kv: (1 + len(kv[1]["invited"]) +
                                        len(kv[1]["found"]) +
                                        len(kv[1]["thesaurus"])), reverse=True)
    snapshot_words = [w for w, _ in top_total[:6]]

    for sw in snapshot_words:
        info = lobby.study_group_members(sw)
        print(f"\n  STUDY GROUP: '{info['topic']}'  "
              f"(dept={info['department']}, generality={info['generality']})")
        print(f"    Curriculum: '{info['curriculum']}'")
        print(f"    LEADER:    '{info['leader']}'")
        print(f"    INVITED:   {info['invited']}")
        print(f"    FOUND:     {info['found']}")
        print(f"    THESAURUS: {info['thesaurus']}")
        print(f"    Total size: {info['total_size']}")

    # ── PROPOSE NEIGHBORHOODS FROM STUDY GROUPS ──────────────────────────
    print("\n── PROPOSING NEIGHBORHOODS FROM STUDY GROUPS ──")
    candidates = lobby.propose_from_study_groups(min_total=3, max_total=60)
    print(f"  {len(candidates)} neighborhood candidates from study groups")

    approved = lobby.scrutinize(candidates, min_coherence=0.2,
                                 min_generality_span=0.02)
    print(f"  {len(approved)} approved after scrutiny")

    committed = lobby.commit(approved)
    print(f"  {len(committed)} neighborhoods committed")

    print("\n  Committed neighborhoods:")
    for nid in committed[:10]:
        n = lobby.neighborhoods[nid]
        g = n.get("generality", {})
        print(f"  {nid} size={n['size']} coherence={n['coherence']:.2f} "
              f"span={g.get('span','?')} cross_gram={g.get('cross_grammatical','?')}")
        print(f"    {sorted(n['members'])[:15]}")

    # ── COMPARISON: study group neighborhoods vs pass-1 only ─────────────
    print("\n── WHAT DID THE MULTI-PASS ADD? ──")
    sg_sizes = [1 + len(g["invited"]) + len(g["found"]) + len(g["thesaurus"])
                for g in lobby.study_groups.values()]
    pass1_sizes = [len(a.ties) for a in lobby.agents.values()]
    print(f"  After Pass 1 only — avg ties per agent: "
          f"{sum(pass1_sizes)/len(pass1_sizes):.2f}")
    print(f"  After all passes — avg study group size: "
          f"{sum(sg_sizes)/len(sg_sizes):.2f}")
    print(f"  Groups with FOUND members (arrived uninvited, came on their own): "
          f"{sum(1 for g in lobby.study_groups.values() if g['found'])}")
    print(f"  Groups enriched by thesaurus (Pass 3): "
          f"{sum(1 for g in lobby.study_groups.values() if g['thesaurus'])}")
    print(f"  Total runtime: {time.time()-t0:.1f}s")
