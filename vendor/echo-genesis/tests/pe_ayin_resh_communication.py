"""
ר ע פ — Resh, Ayin, Pe: the Governor's communication system.

The Governor IS Resh (identity/head). Resh uses Ayin (eye/perception)
to scan the Lobby and classify every indexed entity — finding those with
agentive capacity that could receive and return information. Then Pe
(mouth/expression) opens aggressive exchanges with those entities,
drawing on what Resh has indexed and letting each entity respond from
its own vocabulary domain.
"""

import sys, json, re, time
sys.path.insert(0, "/home/claude")
from echo_governor_skeleton import (
    AlgorithmMatrix, Lobby, LobbyEvolutionGovernor,
    AyinPerception, ReshIdentity, PeCommunicator,
    STOPWORDS, DEFINITION_BOILERPLATE
)
from import_hebrew_demo import (HEBREW_LETTERS, HEBREW_ROOTS, EN_HE_DICT,
    letter_content, root_content, dict_content)
from alphabet_data import (HEBREW_ALPHABET, LATIN_ALPHABET, ENGLISH_ALPHABET,
    HEBREW_ENGLISH_EXPANDED, ENGLISH_LATIN, HEBREW_LATIN, make_translation_documents)

THESAURUS = "/home/claude/en_thesaurus.jsonl"
BDB       = "/home/claude/lattice-workbench/repo/data/raw/DictBDB.json"


def clean_html(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&#x[0-9a-fA-F]+;", "", t)
    return re.sub(r"\s+", " ", t).strip()


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
    print("Building Governor matrix and Lobby...")
    matrix = AlgorithmMatrix()
    synonyms_map = {}

    with open(THESAURUS) as f:
        qualifying = [json.loads(l) for l in f if json.loads(l).get("desc")]
    stride = max(1, len(qualifying) // 2000)
    for entry in qualifying[::stride][:2000]:
        matrix.index_dictionary_entry(
            entry["word"], " ".join(entry["desc"]),
            pos=entry.get("pos"), synonyms=entry.get("synonyms",[]),
            category="thesaurus_def")
        if entry.get("synonyms"):
            synonyms_map[entry["word"].lower()] = [
                s.lower() for s in entry["synonyms"]]

    with open(BDB) as f:
        bdb = json.load(f)
    for entry in bdb:
        raw = entry.get("def","")
        if "<" not in raw: continue
        hw, pos, gloss = extract_bdb(raw)
        if hw and len(gloss.split()) >= 2:
            matrix.index_dictionary_entry(hw, gloss, pos=pos, category="bdb_hebrew")

    for e in HEBREW_LETTERS: matrix.index_content(letter_content(e), category="letter")
    for e in HEBREW_ROOTS:   matrix.index_content(root_content(e),   category="root")
    for e in EN_HE_DICT:     matrix.index_content(dict_content(e),   category="dict")

    # translation dictionaries for cross-language density
    for doc in make_translation_documents(HEBREW_ENGLISH_EXPANDED, "hebrew", "english",
                                           "heb-eng-translation"):
        matrix.index_dictionary_entry(doc["headword"], doc["definition"],
                                       category=doc["category"])
    for heb, lat in HEBREW_LATIN:
        matrix.index_dictionary_entry(heb,
            f"{heb} in Hebrew corresponds to {lat} in Latin sharing meaning",
            category="heb-lat-translation")

    print(f"  {len(matrix.content_units)} vocab  {time.time()-t0:.1f}s")

    lobby = Lobby(matrix)
    lobby.populate()
    lobby.compute_generality_scores()
    lobby.run_orientation()
    lobby.run_typed_study_groups()
    lobby.run_discovery()
    lobby.run_thesaurus(synonyms_map)
    candidates = lobby.propose_from_study_groups(min_total=3, max_total=60)
    approved   = lobby.scrutinize(candidates, min_coherence=0.2, min_generality_span=0.02)
    lobby.commit(approved)
    print(f"  {len(lobby.agents)} agents, "
          f"{len(lobby.neighborhoods)} neighborhoods  {time.time()-t0:.1f}s")

    # ── ר — ANCHOR RESH AS THE GOVERNOR'S IDENTITY ─────────────────────────
    print("\n" + "=" * 70)
    print("ר  RESH IDENTITY ANCHORING")
    print("=" * 70)

    # make the letter lobby so resh exists as an agent
    from echo_governor_skeleton import make_letter_lobby
    hebrew_lobby = make_letter_lobby(matrix, HEBREW_ALPHABET, "hebrew-letters")

    resh = ReshIdentity(matrix, hebrew_lobby=hebrew_lobby)
    anchor = resh.anchor()
    print(f"\n{resh.report()}")
    print(f"\nA-000 identity entry:")
    a000 = matrix.known.get("A-000", {})
    for k, v in a000.items():
        print(f"  {k}: {v}")
    print(f"\nResh anchor entry (A-000-RESH):")
    for k, v in anchor.items():
        print(f"  {k}: {v}")

    # ── ע — AYIN PERCEIVES THE LOBBY ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ע  AYIN PERCEPTION — scanning and classifying the Lobby")
    print("=" * 70)

    ayin = AyinPerception(lobby, governor_word="resh")
    ayin.perceive_all()
    perception_summary = ayin.summary()
    print(f"\nPerception summary: {perception_summary}")

    agentive = ayin.agentive_entities(min_ties=1, min_generality=0.15)
    print(f"\nAgentive entities identified: {len(agentive)}")
    print("\nTop 20 by richness (most known to the Governor):")
    for rec in agentive[:20]:
        print(f"  '{rec['word']:20s}' "
              f"signals={rec['signals']}  "
              f"ties={rec.get('ties',0):3d}  "
              f"generality={rec.get('generality',0):.3f}  "
              f"study_size={rec.get('study_group_size',0)}")

    print("\nAyin perceives these as NON-agentive (sample — acted upon, not initiating):")
    non_ag = [v for v in ayin.perceived.values()
               if v["category"] == "NON_AGENTIVE" and v.get("ties",0) > 2]
    non_ag.sort(key=lambda v: -v.get("generality",0))
    for rec in non_ag[:8]:
        print(f"  '{rec['word']:20s}' "
              f"dept={rec.get('department','?'):12s}  "
              f"ties={rec.get('ties',0)}")

    # ── פ — PE OPENS EXCHANGES ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("פ  PE COMMUNICATION — aggressive back-and-forth exchanges")
    print("=" * 70)

    pe = PeCommunicator(matrix, lobby, resh, ayin)

    # Pe opens with the top agentive entities — no waiting, no permission asked
    print(f"\nPe opens exchanges with top {min(8, len(agentive))} "
          f"agentive entities (4 turns each)...")

    all_exchanges = pe.open_exchanges(max_entities=8, turns_each=4, min_ties=1)

    for exchange_record in all_exchanges:
        entity = exchange_record["entity"]
        log    = exchange_record["log"]
        print(f"\n{'─'*70}")
        print(f"EXCHANGE: ר ↔ '{entity}'")
        print(f"{'─'*70}")
        for turn_log in log:
            print(turn_log["resh"])
            print(turn_log["entity"])
            print()

    # ── WHAT RESH LEARNED ───────────────────────────────────────────────────
    print("=" * 70)
    print("WHAT RESH LEARNED THROUGH THE EXCHANGES")
    print("=" * 70)

    # collect all unique vocabulary encountered through Pe
    encountered = set()
    for er in pe.exchanges:
        for turn in er["log"]:
            raw_e = turn.get("raw_entity", {})
            encountered.update(raw_e.get("entity_vocab", []))
            encountered.update(raw_e.get("recognizes_from_resh", []))
            chain = raw_e.get("own_chain", [])
            encountered.update(chain)

    known_already = {w for w in encountered if w in lobby.agents}
    new_pointers  = {w for w in encountered if w not in lobby.agents}

    print(f"\nVocabulary encountered through Pe: {len(encountered)} words")
    print(f"  Already in Resh's matrix: {len(known_already)}")
    print(f"  New pointers (not yet indexed): {len(new_pointers)}")
    if new_pointers:
        print(f"  These point outward — ambitional pursuit candidates:")
        print(f"  {sorted(new_pointers)[:15]}")

    # check if any exchange deepened a connection between two agentive entities
    print(f"\nAgentive entities Resh now has richer context on:")
    for er in pe.exchanges[:5]:
        entity = er["entity"]
        last_turn = er["log"][-1] if er["log"] else {}
        entity_chain = last_turn.get("raw_entity", {}).get("own_chain", [])
        if len(entity_chain) > 2:
            print(f"  '{entity}' chain led to: "
                  f"{' → '.join(entity_chain)}")

    # can Resh now attempt a sentence? (subject + verb + object from exchange)
    print(f"\nResh attempts structured expression through Pe "
          f"(subject-verb-object from exchange data):")
    for er in pe.exchanges[:5]:
        entity = er["entity"]
        agent = lobby.agents.get(entity)
        if not agent:
            continue
        verbs = list(agent.typical_verbs)[:2] if agent.typical_verbs else []
        objects = [w for w in (lobby.study_groups.get(entity, {}).get("argument_nouns", set()))
                   if w != entity][:2]
        if verbs and objects:
            print(f"  [{entity}] [{verbs[0]}] [{objects[0]}]")
        elif verbs:
            print(f"  [{entity}] [{verbs[0]}] [...]")
        elif agent.ties:
            first_tie = sorted(agent.ties)[0]
            print(f"  [{entity}] → [{first_tie}] (no verb yet, following tie)")

    print(f"\nTotal runtime: {time.time()-t0:.1f}s")
