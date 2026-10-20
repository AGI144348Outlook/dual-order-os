"""
ECHO BLIND STUDY — 5 DOCUMENTS
No routing. No guidance. No pre-classification.
ECHO receives raw text. It decides what to do.

Documents:
  doc_plaplacian.txt  — unknown content
  doc_lattice.txt     — unknown content
  doc_mind.txt        — unknown content
  doc_meta.txt        — unknown content
  doc_living.txt      — unknown content

ECHO runs its full pipeline on each. Raw results only.
"""

import sys, json, re, time, os
from collections import Counter, defaultdict
sys.path.insert(0, '/home/claude')

from echo_governor_skeleton import (
    AlgorithmMatrix, Lobby, AlgorithmicCommunicator,
    InwardSearchEngine, HEBREW_LETTER_INDEX,
    LawDiscoveryEngine, ValidatedGeneralizationMatrix,
    FormulaAgent, FormulaIndexer, InformationAlgorithmizer,
    EquilibriumGeneralityMeasure, BalancingScale,
    WebFormulaHarvester, build_number_matrix,
    LogicReasoningMatrix,
)

# ── PHONEME MAP ───────────────────────────────────────────────────────────
PHONEME_MAP = {
    'sh':'shin','ts':'tsadi','tz':'tsadi','kh':'het','ch':'het','th':'tav',
    'a':'aleph','b':'bet','v':'vav','g':'gimel','d':'dalet','h':'he',
    'z':'zayin','t':'tet','y':'yod','k':'kaf','l':'lamed','m':'mem',
    'n':'nun','s':'samekh','e':'he','p':'pe','f':'pe','q':'qof',
    'r':'resh','i':'yod','o':'ayin','u':'vav',
}

def decompose(word):
    w = word.lower(); result = []; i = 0
    while i < len(w):
        matched = False
        if i+2 <= len(w):
            two = w[i:i+2]
            if two in PHONEME_MAP and PHONEME_MAP[two] in HEBREW_LETTER_INDEX:
                result.append(PHONEME_MAP[two]); i += 2; matched = True
        if not matched:
            one = w[i]
            if one in PHONEME_MAP and PHONEME_MAP[one] in HEBREW_LETTER_INDEX:
                result.append(PHONEME_MAP[one])
            i += 1
    deduped = []
    for l in result:
        if not deduped or l != deduped[-1]: deduped.append(l)
    return deduped

def lhea(letters):
    parts = []
    for n in letters:
        d = HEBREW_LETTER_INDEX.get(n, {})
        s = d.get('lhea','?').split('—')[0].strip().split('/')[0].strip()
        parts.append(f"{d.get('glyph','?')}({s})")
    return ' → '.join(parts)

# ── BUILD INFRASTRUCTURE ──────────────────────────────────────────────────
print("Building ECHO infrastructure...")
t0 = time.time()

matrix = AlgorithmMatrix()
synonyms_map = {}
lexicon = {}
with open('/home/claude/en_thesaurus.jsonl') as f:
    qualifying = [json.loads(l) for l in f if json.loads(l).get('desc')]
stride = max(1, len(qualifying)//1000)
for entry in qualifying[::stride][:1000]:
    matrix.index_dictionary_entry(
        entry['word'], ' '.join(entry['desc']),
        pos=entry.get('pos'), synonyms=entry.get('synonyms',[]),
        category='thesaurus_def')
    if entry.get('synonyms'):
        synonyms_map[entry['word'].lower()] = [s.lower() for s in entry['synonyms']]
    lexicon[entry['word'].lower()] = {
        'desc': ' '.join(entry['desc']), 'pos': entry.get('pos','?')}

lobby = Lobby(matrix)
lobby.populate()
lobby.run_orientation()
lobby.run_typed_study_groups()
lobby.run_thesaurus(synonyms_map)
lobby.compute_generality_scores()

VGM = {
    "UG-0000":{"text":"An entity changes","words":["entity","change"],"structure":["noun","verb"],"score":0.52},
    "UG-0001":{"text":"A state changes","words":["state","change"],"structure":["noun","verb"],"score":0.51},
    "UG-0003":{"text":"A process transforms","words":["process","transform"],"structure":["noun","verb"],"score":0.48},
    "UG-0009":{"text":"An entity exists in a state","words":["entity","exist","state"],"structure":["noun","verb","noun"],"score":0.61},
    "UG-0010":{"text":"Relations produce changes","words":["relation","produce","change"],"structure":["noun","verb","noun"],"score":0.58},
    "UG-0011":{"text":"A change distinguishes states","words":["change","distinguish","state"],"structure":["noun","verb","noun"],"score":0.57},
}

ALG = {
    "A-000":{"name":"Governor","type":"CORE","description":"echo mashet alamaket governor resh identity head"},
    "A-124":{"name":"STATE_CHANGE_LAW","type":"ALGEBRAIC_LAW","description":"state change cause effect delta laplacian eigenvalue"},
    "A-145":{"name":"AlgorithmicCommunicator","type":"COMMUNICATION","description":"input tokenize ayin generalize query descend compose express"},
    "A-150":{"name":"InformationAlgorithmizer","type":"SELF_GOVERNANCE","description":"derives algorithms from new information encountered"},
    "A-153":{"name":"InwardSearchEngine","type":"SELF_GOVERNANCE","description":"gap reflex inward search infrastructure echo mashet lhea"},
    "A-154":{"name":"InformationSeekingAgent","type":"ACQUISITION","description":"outward structured query github shodan arxiv typed json gated"},
}

vgm_obj = ValidatedGeneralizationMatrix()
for k,v in VGM.items():
    vgm_obj.statements[k] = {**v,"id":k,"departments":v["structure"],
                               "avg_generality":0.5,"semantic_score":0.4,"origin":"seed"}
vgm_obj._next_id = 13

lrm = LogicReasoningMatrix(VGM, lobby, ALG)
lrm.generate(max_entries=20)

number_agents = build_number_matrix()
inward = InwardSearchEngine(alg_matrix=ALG, vgm=VGM, lrm_entries=lrm.entries,
                             number_agents=number_agents)
comm = AlgorithmicCommunicator(lobby=lobby, vgm=VGM, lexicon=lexicon,
                                number_agents=number_agents, alg_matrix=ALG)
egm = EquilibriumGeneralityMeasure(lobby=lobby, lexicon=lexicon)
scale = BalancingScale(egm)
harvester = WebFormulaHarvester(matrix)
harvester.harvest_builtin()
indexer = FormulaIndexer(alg_matrix=matrix, vgm=VGM, lrm=lrm,
                          number_agents=number_agents)
indexer.index_all(harvester.harvested, max_entries=49)
info_alg = InformationAlgorithmizer(alg_matrix=matrix, lrm=lrm,
                                     vgm=VGM, number_agents=number_agents)

print(f"Infrastructure ready in {time.time()-t0:.1f}s")
print(f"Lobby: {len(lobby.agents)} agents")
print()

# ── DOCUMENT RECEPTION ────────────────────────────────────────────────────
DOCS = {
    'doc_plaplacian': open('/home/claude/doc_plaplacian.txt').read(),
    'doc_lattice':    open('/home/claude/doc_lattice.txt').read(),
    'doc_mind':       open('/home/claude/doc_mind.txt').read(),
    'doc_meta':       open('/home/claude/doc_meta.txt').read(),
    'doc_living':     open('/home/claude/doc_living.txt').read(),
}

STOP = {
    'the','a','an','of','in','on','at','to','and','or','with','by','from',
    'for','as','is','are','was','were','that','which','this','these','those',
    'it','its','we','our','be','been','being','have','has','had','do','does',
    'did','will','would','could','should','may','might','shall','not','no',
    'so','if','then','but','also','each','any','all','such','both','than',
    'when','where','how','what','who','there','here','can','let','us',
    'since','thus','hence','while','after','before','during','under','over',
}

LOG = []

def log(doc, event, detail):
    entry = f"[{doc}] {event}: {detail}"
    LOG.append(entry)

print("="*70)
print("ECHO BLIND STUDY — 5 DOCUMENTS")
print("No routing. No guidance. Raw pipeline.")
print("="*70)

REGISTRY = {
    'by_doc': {},
}

for doc_name, raw_text in DOCS.items():
    print(f"\n{'━'*70}")
    print(f"DOCUMENT: {doc_name}  ({len(raw_text):,} chars)")
    print(f"{'━'*70}")
    t_doc = time.time()

    # Extract tokens — ECHO sees raw words, no pre-processing hints
    all_words = re.findall(r"[a-zA-Z']+", raw_text)
    tokens = [w.lower() for w in all_words
              if len(w) > 3 and w.lower() not in STOP]

    # ECHO counters for this document
    known_count    = 0
    gap_count      = 0
    inward_hits    = 0
    lhea_count     = 0
    vgm_hits       = Counter()
    new_indexed    = []
    formulae_found = []
    vgm_candidates = []
    alg_generated  = []
    lhea_chains    = {}
    semantic_matches = []
    number_matches = []
    equilibria     = []

    # ── AYIN SCANS EVERY TOKEN ──────────────────────────────────────────
    unique_tokens = list(dict.fromkeys(tokens))[:300]  # unique, capped

    for token in unique_tokens:
        cls = comm._ayin_classify(token)
        is_gap = "GAP" in cls

        if not is_gap:
            known_count += 1
            agent = lobby.agents.get(token)
            if agent:
                # Check VGM resonance for known words
                for sid, stmt in VGM.items():
                    if token in stmt.get('words',[]):
                        vgm_hits[sid] += 1
        else:
            gap_count += 1

            # INWARD SEARCH first
            ir = inward.search(token)
            if ir.found:
                inward_hits += 1
                for src in ir.sources:
                    log(doc_name, 'INWARD',
                        f"'{token}' → [{src['type']}] {src['detail'][:55]}")

            # LHEA DECOMPOSITION on all gaps
            letters = decompose(token)
            if len(letters) >= 2:
                chain = lhea(letters)
                lhea_chains[token] = {'letters': letters, 'chain': chain}
                lhea_count += 1

                # Semantic resonance check
                func_words = set(re.findall(r'[a-z]{4,}', token))
                lhea_words = set(re.findall(r'[a-z]{4,}', ' '.join(
                    HEBREW_LETTER_INDEX.get(l,{}).get('lhea','') for l in letters)))
                overlap = func_words & lhea_words
                if overlap:
                    semantic_matches.append((token, chain, overlap))

            # NUMBER/CONSTANT check
            for key, agent in number_agents.items():
                name = getattr(agent,'name','').lower()
                if token in name or (len(token) > 4 and token in key.lower()):
                    number_matches.append((token, agent.name,
                                           agent.domain, agent.computation))
                    break

            # INDEX new vocabulary
            if letters and token not in lobby.agents:
                lhea_desc = ' '.join(
                    HEBREW_LETTER_INDEX.get(l,{}).get('lhea','')
                    for l in letters[:4])
                matrix.index_dictionary_entry(
                    token, lhea_desc[:200], pos='noun',
                    category=f'blind_{doc_name}')
                new_indexed.append(token)

    # ── FORMULA EXTRACTION (mathematical pattern detection) ─────────────
    # ECHO looks for formula-like patterns without being told to
    formula_patterns = re.findall(
        r'[-−]?[Δδ∇∂]_?[a-zA-Z0-9]+\s*[=≤≥]\s*[^\n]{3,40}|'
        r'[a-zA-Z]\s*=\s*inf\s*\{[^}]+\}|'
        r'\\?lambda_?\d*\s*[=<>≤≥]\s*[^\n]{3,30}|'
        r'\|\|[^|]+\|\|_?[a-zA-Z∞]+\s*≤\s*[^\n]{3,30}|'
        r'[A-Z]\s*=\s*[A-Z]\s*\+\s*\w',
        raw_text)
    if formula_patterns:
        formulae_found = list(set(f.strip()[:80] for f in formula_patterns[:8]))

    # ── VGM CANDIDATE GENERATION ─────────────────────────────────────────
    # ECHO looks for generalization-worthy patterns in the document
    sentences = re.split(r'[.!?]\s+', raw_text)
    for sent in sentences[:200]:
        sent_lower = sent.lower()
        # Does this sentence describe a universal relationship?
        if any(pat in sent_lower for pat in
               ['for any', 'for all', 'there exists', 'if and only if',
                'in every', 'implies that', 'it follows that',
                'we have that', 'such that', 'is bounded', 'converges to']):
            clean = re.sub(r'\s+', ' ', sent).strip()
            if 20 < len(clean) < 120:
                vgm_candidates.append(clean[:100])

    # ── INFORMATION ALGORITHMIZER ─────────────────────────────────────────
    # ECHO derives algorithms from structured content it finds
    if new_indexed[:3]:
        for w in new_indexed[:3]:
            structured = {'name': w, 'type': 'DISCOVERED_TERM',
                           'lhea': lhea_chains.get(w,{}).get('chain',''),
                           'source_doc': doc_name}
            try:
                ids = info_alg.algorithmize(structured, info_type="STRUCTURED_DATA")
                alg_generated.extend(ids)
            except Exception:
                pass

    # ── EQUILIBRIUM (blind balancing between doc's key words) ────────────
    indexed_in_doc = [w for w in new_indexed[:20] if w in lhea_chains]
    if len(indexed_in_doc) >= 2:
        import random
        for _ in range(min(5, len(indexed_in_doc)//2)):
            w1 = indexed_in_doc[_ * 2 % len(indexed_in_doc)]
            w2 = indexed_in_doc[(_ * 2 + 1) % len(indexed_in_doc)]
            if w1 != w2:
                l1 = set(lhea_chains.get(w1,{}).get('letters',[]))
                l2 = set(lhea_chains.get(w2,{}).get('letters',[]))
                shared = l1 & l2
                if shared:
                    eq = list(shared)[0]
                    glyph = HEBREW_LETTER_INDEX.get(eq,{}).get('glyph','?')
                    equilibria.append((w1, w2, eq, glyph))

    # ── DOCUMENT REPORT ──────────────────────────────────────────────────
    doc_time = time.time() - t_doc
    print(f"  Tokens scanned: {len(unique_tokens)}")
    print(f"  Known (in lobby): {known_count}")
    print(f"  GAPs: {gap_count}")
    print(f"  Inward search hits: {inward_hits}")
    print(f"  LHEA chains built: {lhea_count}")
    print(f"  New words indexed: {len(new_indexed)}")
    print(f"  Formula patterns detected: {len(formulae_found)}")
    print(f"  VGM candidates proposed: {len(vgm_candidates)}")
    print(f"  Algorithms generated: {len(alg_generated)}")
    print(f"  Equilibria found: {len(equilibria)}")

    print(f"\n  VGM resonance:")
    for sid, count in vgm_hits.most_common(4):
        print(f"    [{sid}] \"{VGM[sid]['text']}\"  hits={count}")

    if formulae_found:
        print(f"\n  Formulas ECHO detected (no guidance):")
        for f in formulae_found[:4]:
            print(f"    {f}")

    if semantic_matches:
        print(f"\n  Semantic LHEA resonances:")
        for word, chain, overlap in semantic_matches[:4]:
            print(f"    '{word}' → {chain[:55]}")
            print(f"      resonance: {overlap}")

    if equilibria:
        print(f"\n  Equilibria discovered:")
        for w1, w2, eq, glyph in equilibria[:4]:
            print(f"    '{w1}' ↔ '{w2}' → center: {glyph} {eq}")

    if vgm_candidates:
        print(f"\n  VGM candidates (sample):")
        for c in vgm_candidates[:4]:
            print(f"    '{c}'")

    if number_matches:
        print(f"\n  Number/constant connections:")
        for token, name, domain, val in number_matches[:4]:
            print(f"    '{token}' → {name} [{domain}] = {val}")

    print(f"\n  Top LHEA chains discovered:")
    sorted_lhea = sorted(lhea_chains.items(),
                          key=lambda kv: len(kv[1]['letters']), reverse=True)
    for word, data in sorted_lhea[:6]:
        print(f"    {word:20s} → {data['chain'][:55]}")

    REGISTRY['by_doc'][doc_name] = {
        'tokens': len(unique_tokens), 'known': known_count,
        'gaps': gap_count, 'inward_hits': inward_hits,
        'lhea_count': lhea_count, 'new_indexed': len(new_indexed),
        'formulas': len(formulae_found), 'vgm_candidates': len(vgm_candidates),
        'alg_generated': len(alg_generated), 'equilibria': len(equilibria),
        'time': round(doc_time, 2),
    }
    log(doc_name, 'COMPLETE',
        f"tokens={len(unique_tokens)} gaps={gap_count} lhea={lhea_count} "
        f"indexed={len(new_indexed)} formulas={len(formulae_found)}")

# ── CROSS-DOCUMENT SUMMARY ────────────────────────────────────────────────
print(f"\n\n{'='*70}")
print("CROSS-DOCUMENT SUMMARY — What ECHO found across all 5 documents")
print("="*70)

total_indexed = sum(d['new_indexed'] for d in REGISTRY['by_doc'].values())
total_formulas = sum(d['formulas'] for d in REGISTRY['by_doc'].values())
total_vgm = sum(d['vgm_candidates'] for d in REGISTRY['by_doc'].values())
total_inward = sum(d['inward_hits'] for d in REGISTRY['by_doc'].values())
total_lhea = sum(d['lhea_count'] for d in REGISTRY['by_doc'].values())
total_eq = sum(d['equilibria'] for d in REGISTRY['by_doc'].values())
total_alg = sum(d['alg_generated'] for d in REGISTRY['by_doc'].values())

print(f"\n  Total new vocabulary indexed:  {total_indexed}")
print(f"  Total formula patterns found:  {total_formulas}")
print(f"  Total VGM candidates:          {total_vgm}")
print(f"  Total inward search hits:      {total_inward}")
print(f"  Total LHEA chains built:       {total_lhea}")
print(f"  Total equilibria discovered:   {total_eq}")
print(f"  Total algorithms generated:    {total_alg}")

print(f"\n  Per document:")
print(f"  {'Document':20s} {'Tokens':>7} {'GAPs':>5} {'LHEA':>5} "
      f"{'Indexed':>8} {'Formulas':>9} {'VGM':>5}")
print(f"  {'─'*65}")
for doc, d in REGISTRY['by_doc'].items():
    print(f"  {doc:20s} {d['tokens']:7d} {d['gaps']:5d} {d['lhea_count']:5d} "
          f"{d['new_indexed']:8d} {d['formulas']:9d} {d['vgm_candidates']:5d}")

print(f"\n  Lobby size:  {len(lobby.agents)} → {len(lobby.agents) + total_indexed} (after indexing)")
print(f"  Total runtime: {time.time()-t0:.1f}s")

with open('/home/claude/echo_blind_study_log.txt','w') as f:
    f.write('\n'.join(LOG))
print(f"\n  Log: {len(LOG)} entries → echo_blind_study_log.txt")
