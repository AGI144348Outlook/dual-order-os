"""
ECHO Governor — Self-governance test.

The Governor diagnoses its own corpus fitness, audits its pool,
optimizes its threshold, and generates a specific acquisition plan
— all without manual intervention.

Then the PipelineOrchestrator runs the full pipeline autonomously
and produces a detailed self-log.
"""
import sys, json, re, time
sys.path.insert(0, "/home/claude")
from echo_governor_skeleton import (
    AlgorithmMatrix, Lobby,
    PoolQualityAuditor, CorpusFitnessEvaluator,
    ThresholdOptimizer, AcquisitionPlanner,
    SeedSentenceGenerator, PipelineOrchestrator,
    GeneralityMatrix, OperationOrderValidator,
)
from import_hebrew_demo import (HEBREW_LETTERS, HEBREW_ROOTS, EN_HE_DICT,
    letter_content, root_content, dict_content)
from alphabet_data import (HEBREW_ENGLISH_EXPANDED, make_translation_documents)

THESAURUS = "/home/claude/en_thesaurus.jsonl"
BDB = "/home/claude/lattice-workbench/repo/data/raw/DictBDB.json"


def clean_html(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()

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

    # Build matrix (corpus ingestion — this is what A-134 would automate fetching)
    print("Building matrix...")
    matrix = AlgorithmMatrix()
    synonyms_map = {}
    with open(THESAURUS) as f:
        qualifying = [json.loads(l) for l in f if json.loads(l).get("desc")]
    lexicon = {}   # for CorpusFitnessEvaluator
    stride = max(1, len(qualifying)//2000)
    for entry in qualifying[::stride][:2000]:
        matrix.index_dictionary_entry(
            entry["word"], " ".join(entry["desc"]),
            pos=entry.get("pos"), synonyms=entry.get("synonyms",[]),
            category="thesaurus_def")
        if entry.get("synonyms"):
            synonyms_map[entry["word"].lower()] = [s.lower() for s in entry["synonyms"]]
        lexicon[entry["word"].lower()] = {
            "desc": " ".join(entry["desc"]), "pos": entry.get("pos","?")}
    with open(BDB) as f:
        bdb = json.load(f)
    for entry in bdb:
        raw = entry.get("def","")
        if "<" not in raw: continue
        hw, pos, gloss = extract_bdb(raw)
        if hw and len(gloss.split()) >= 2:
            matrix.index_dictionary_entry(hw, gloss, pos=pos, category="bdb_hebrew")
    for e in HEBREW_LETTERS: matrix.index_content(letter_content(e), category="letter")
    for e in HEBREW_ROOTS:   matrix.index_content(root_content(e), category="root")
    for e in EN_HE_DICT:     matrix.index_content(dict_content(e), category="dict")
    for doc in make_translation_documents(HEBREW_ENGLISH_EXPANDED, "hebrew", "english",
                                           "heb-eng-translation"):
        matrix.index_dictionary_entry(doc["headword"], doc["definition"],
                                       category=doc["category"])
    print(f"  {len(matrix.content_units)} vocab  {time.time()-t0:.1f}s")

    # ── A-128: OPERATION ORDER VALIDATION ────────────────────────────────
    print("\n" + "=" * 70)
    print("A-128: OPERATION ORDER VALIDATOR")
    print("=" * 70)
    oov = OperationOrderValidator()
    wrong_order = [
        "index_dictionary_entry",
        "compute_generality_scores",  # WRONG: before orientation
        "run_orientation",
    ]
    correct_order = [
        "index_dictionary_entry",
        "run_orientation",
        "compute_generality_scores",  # CORRECT: after orientation
    ]
    print(f"\nWrong order errors: "
          f"{oov.validate_sequence(wrong_order)}")
    print(f"Correct order errors: "
          f"{oov.validate_sequence(correct_order)}")

    # ── A-130: CORPUS FITNESS EVALUATION ─────────────────────────────────
    print("\n" + "=" * 70)
    print("A-130: CORPUS FITNESS EVALUATOR")
    print("Governor evaluating its own corpus before investing in orientation")
    print("=" * 70)
    fitness_eval = CorpusFitnessEvaluator(lexicon)
    fitness_result = fitness_eval.evaluate_for_primitives()
    print(f"\nCorpus fitness for philosophical primitives: {fitness_result['fitness']}")
    print(f"Diagnosis: {fitness_result['diagnosis']}")
    print(f"Terminal distribution: {fitness_result['terminal_counts']}")
    print(f"Philosophical ratio: {fitness_result['philosophical_ratio']:.1%}")
    print(f"Physical ratio: {fitness_result['physical_ratio']:.1%}")
    if fitness_result.get("chains"):
        print("\nSample abstraction chains:")
        for word, chain in list(fitness_result["chains"].items())[:5]:
            print(f"  {word}: {' → '.join(chain)}")

    # ── A-134: PIPELINE ORCHESTRATOR (full autonomous run) ─────────────
    print("\n" + "=" * 70)
    print("A-134: PIPELINE ORCHESTRATOR — Governor running itself")
    print("=" * 70)
    orchestrator = PipelineOrchestrator(matrix)
    result = orchestrator.orchestrate(synonyms_map=synonyms_map)

    print(f"\nOrchestration result: {'ABORTED' if result.get('aborted') else 'COMPLETE'}")
    if result.get("reason"):
        print(f"Reason: {result['reason']}")

    # ── A-131: THRESHOLD OPTIMIZER ───────────────────────────────────────
    print("\n" + "=" * 70)
    print("A-131: THRESHOLD OPTIMIZER — autonomous parameter tuning")
    print("=" * 70)
    if result.get("lobby"):
        lobby = result["lobby"]
        auditor = PoolQualityAuditor()
        optimizer = ThresholdOptimizer([lobby], auditor)
        opt = optimizer.optimize([0.20, 0.25, 0.30, 0.35, 0.40])
        print(f"\nBest threshold: {opt['best_threshold']} "
              f"(score={opt['best_score']:.3f})")
        print("\nFull sweep:")
        for r in opt["sweep"]:
            bar = "█" * int(r["composite_score"] * 20)
            print(f"  {r['threshold']:.2f}  {bar:20s}  {r['composite_score']:.3f}  "
                  f"pool={r['pool_size']:3d}  N={r['n_nouns']}  V={r['n_verbs']}  "
                  f"phil={r['philosophical_present']}")

    # ── A-129: POOL QUALITY AUDIT ─────────────────────────────────────────
    print("\n" + "=" * 70)
    print("A-129: POOL QUALITY AUDITOR")
    print("=" * 70)
    if result.get("lobby"):
        gm = GeneralityMatrix([result["lobby"]], 0.30)
        pool = gm.populate()
        auditor = PoolQualityAuditor()
        audit = auditor.audit(pool)
        print(f"\nPool quality: {audit['status']}")
        print(f"  Size: {audit['pool_size']}  "
              f"Nouns: {audit['n_nouns']}  "
              f"Verbs: {audit['n_verbs']}")
        print(f"  Philosophical vocabulary present: "
              f"{audit['philosophical_present']}")
        if audit["issues"]:
            print("  Issues identified by Governor:")
            for issue in audit["issues"]:
                print(f"    ! {issue}")

    # ── A-132: ACQUISITION PLANNER ───────────────────────────────────────
    print("\n" + "=" * 70)
    print("A-132: ACQUISITION PLANNER")
    print("Governor generates its own corpus acquisition targets")
    print("=" * 70)
    planner = AcquisitionPlanner()
    audit_for_plan = auditor.audit(pool) if result.get("lobby") else {"issues": [], "status": "?"}
    plan = planner.plan(audit_for_plan, fitness_result)
    print(f"\nAcquisition plan ({len(plan)} targets ranked by priority):")
    for i, target in enumerate(plan):
        print(f"\n  [{i+1}] {target['priority']}:  {target['name']}")
        print(f"       Source: {target['source'][:70]}")
        print(f"       Fixes:  {target['fixes']}")
        print(f"       Provides: {target['provides'][:4]}")
        print(f"       {target['description'][:80]}")

    # ── A-133: SEED SENTENCE GENERATOR ───────────────────────────────────
    print("\n" + "=" * 70)
    print("A-133: SEED SENTENCE GENERATOR")
    print("Governor generates its own abstraction test sentences")
    print("=" * 70)
    if result.get("lobby"):
        seed_gen = SeedSentenceGenerator(result["lobby"])
        sentences = seed_gen.generate(n=15)
        print(f"\nGovernor-generated seed sentences ({len(sentences)}):")
        for s in sentences:
            print(f"  {s}")

    # ── SELF-LOG ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("GOVERNOR SELF-LOG (what it monitored during orchestration)")
    print("=" * 70)
    for entry in orchestrator.log:
        r = entry["result"]
        print(f"\n  [{entry['stage']}]  status={r.get('status', r.get('fitness','?'))}")
        if r.get("issues"):
            for issue in r["issues"]:
                print(f"    ! {issue}")
        if r.get("recommendations"):
            for rec in r["recommendations"][:1]:
                print(f"    → {rec}")

    if result.get("acquisition_plan"):
        print("\n  Governor paused and generated acquisition plan:")
        for t in result["acquisition_plan"][:3]:
            print(f"    [{t['priority']}] {t['name']}")

    print(f"\nTotal runtime: {time.time()-t0:.1f}s")
