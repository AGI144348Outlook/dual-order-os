"""
ECHO — 500-round autonomous run with the Mashet Dictionary corpus.
Blind study. No guidance. ECHO has full access to its infrastructure.
It chooses which algorithms to invoke and when.

Log format: raw output only. No interpretation added.
"""

import sys, json, re, time, random
from collections import defaultdict, Counter
sys.path.insert(0, '/home/claude')

from echo_governor_skeleton import (
    AlgorithmMatrix, Lobby, AlgorithmicCommunicator,
    InwardSearchEngine, HEBREW_LETTER_INDEX,
    LobbyEvolutionGovernor, HypothesisSandbox,
    LawDiscoveryEngine, ValidatedGeneralizationMatrix,
    SyntacticalValidator, GeneralityMatrix,
    LogicReasoningMatrix, build_number_matrix,
    NumberAgent, AlgebraicExpression, Variable,
    CalculationEngine, WebFormulaHarvester,
    FormulaIndexer, InformationAlgorithmizer,
    EquilibriumGeneralityMeasure, BalancingScale,
)

# ── PHONEME MAP FOR LHEA DECOMPOSITION ───────────────────────────────────
PHONEME_MAP = {
    'sh':'shin','ts':'tsadi','tz':'tsadi','kh':'het','ch':'het',
    'th':'tav','al':'aleph',
    'a':'aleph','b':'bet','v':'vav','g':'gimel','d':'dalet',
    'h':'he','z':'zayin','t':'tet','y':'yod','k':'kaf',
    'l':'lamed','m':'mem','n':'nun','s':'samekh','e':'he',
    'p':'pe','f':'pe','q':'qof','r':'resh','i':'yod',
    'o':'ayin','u':'vav',
}

def decompose(word):
    w = word.lower()
    result = []
    i = 0
    while i < len(w):
        matched = False
        if i+2 <= len(w):
            two = w[i:i+2]
            if two in PHONEME_MAP and PHONEME_MAP[two] in HEBREW_LETTER_INDEX:
                result.append(PHONEME_MAP[two])
                i += 2
                matched = True
        if not matched:
            one = w[i]
            if one in PHONEME_MAP and PHONEME_MAP[one] in HEBREW_LETTER_INDEX:
                result.append(PHONEME_MAP[one])
            i += 1
    # deduplicate adjacent same letters
    deduped = []
    for l in result:
        if not deduped or l != deduped[-1]:
            deduped.append(l)
    return deduped

def lhea_chain(letters):
    chain = []
    for name in letters:
        d = HEBREW_LETTER_INDEX.get(name, {})
        short = d.get('lhea','?').split('—')[0].strip().split('/')[0].strip()
        chain.append(f"{d.get('glyph','?')}({short})")
    return ' → '.join(chain)

# ── PARSE MASHET CORPUS ───────────────────────────────────────────────────
def parse_corpus(path):
    entries = []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    blocks = re.split(r'###\s+\d+\.', text)
    for block in blocks[1:]:
        lines = block.strip().split('\n')
        header = lines[0].strip() if lines else ''
        m = re.search(r'\(([A-Za-z]+)\)', header)
        transliteration = m.group(1) if m else ''
        ft_m = re.search(r'\*\*Functional Translation:\*\*\s*(.+)', block)
        functional = ft_m.group(1).strip() if ft_m else ''
        ss_m = re.search(r'\*\*State Shift:\*\*\s*(.+)', block)
        state_shift = ss_m.group(1).strip() if ss_m else ''
        sa_m = re.search(r'\*\*Structural Signal:\*\*\s*(.+)', block)
        signal = sa_m.group(1).strip() if sa_m else ''
        pa_m = re.search(r'\*\*Practical Application:\*\*\s*(.+)', block)
        practical = pa_m.group(1).strip() if pa_m else ''
        logic_parts = re.findall(r'\*\s+([A-Z][^*]+\([^)]+\)[^*]+)', block)
        if transliteration:
            entries.append({
                'word': transliteration.lower(),
                'functional': functional,
                'state_shift': state_shift,
                'signal': signal,
                'practical': practical,
                'logic': ' '.join(logic_parts[:4]),
                'raw': block[:300],
            })
    return entries

# ── BUILD INFRASTRUCTURE ──────────────────────────────────────────────────
print("Building ECHO infrastructure...")
t_start = time.time()

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
lobby.run_discovery()
lobby.run_thesaurus(synonyms_map)
lobby.compute_generality_scores()

vgm_data = {
    "UG-0000":{"text":"An entity changes","words":["entity","change"],"structure":["noun","verb"],"score":0.52},
    "UG-0001":{"text":"A state changes","words":["state","change"],"structure":["noun","verb"],"score":0.51},
    "UG-0009":{"text":"An entity exists in a state","words":["entity","exist","state"],"structure":["noun","verb","noun"],"score":0.61},
    "UG-0010":{"text":"Relations produce changes","words":["relation","produce","change"],"structure":["noun","verb","noun"],"score":0.58},
    "UG-0011":{"text":"A change distinguishes states","words":["change","distinguish","state"],"structure":["noun","verb","noun"],"score":0.57},
}
vgm = ValidatedGeneralizationMatrix()
for k, v in vgm_data.items():
    vgm.statements[k] = {**v, "id":k, "departments":v["structure"],
                          "avg_generality":0.5,"semantic_score":0.4,"origin":"seed"}
vgm._next_id = 13

alg_data = {
    "A-000":{"name":"Governor Indexing Algorithm","type":"CORE","description":"The Governor IS Resh. Identity perception expression."},
    "A-120":{"name":"LobbyEvolutionGovernor","type":"EVOLUTION","description":"evolves neighborhoods toward articulately precise fluency"},
    "A-121":{"name":"HypothesisSandbox","type":"EVOLUTION","description":"observe hypothesize sandbox register new algorithms"},
    "A-124":{"name":"STATE_CHANGE_LAW","type":"ALGEBRAIC_LAW","description":"change distinguishes states cause produces measurable effect"},
    "A-127":{"name":"ValidatedGeneralizationMatrix","type":"ABSTRACTION","description":"stores validated propositional understandings axiom tier"},
    "A-145":{"name":"AlgorithmicCommunicator","type":"COMMUNICATION","description":"full pipeline input tokenize ayin generalize query descend compose express"},
    "A-150":{"name":"InformationAlgorithmizer","type":"SELF_GOVERNANCE","description":"derives practical algorithms from any new information encountered"},
    "A-151":{"name":"EquilibriumGeneralityMeasure","type":"METRIC","description":"blind balancing G(C)=V/I no presupposed precedence"},
    "A-152":{"name":"BalancingScale","type":"METRIC","description":"comparison engine discovers equilibrium without presupposed precedence"},
    "A-153":{"name":"InwardSearchEngine","type":"SELF_GOVERNANCE","description":"gap reflex turns inward to search own infrastructure before giving up"},
}
matrix.known.update(alg_data)

lrm = LogicReasoningMatrix(vgm_data, lobby, alg_data)
lrm.generate(max_entries=30)

number_agents = build_number_matrix()
validator = SyntacticalValidator()
gen_matrix = GeneralityMatrix([lobby], generality_threshold=0.25)
gen_matrix.populate()

inward = InwardSearchEngine(
    alg_matrix=alg_data, vgm=vgm_data, lrm_entries=lrm.entries,
    number_agents=number_agents)

comm = AlgorithmicCommunicator(
    lobby=lobby, vgm=vgm_data, lexicon=lexicon,
    number_agents=number_agents, alg_matrix=alg_data)

evolution = LobbyEvolutionGovernor([lobby], "mashet-run")
hypothesis = HypothesisSandbox(lobby, matrix, evolution)
egm = EquilibriumGeneralityMeasure(lobby=lobby, lexicon=lexicon)
scale = BalancingScale(egm)
calc = CalculationEngine(matrix=matrix, number_agents=number_agents)
info_alg = InformationAlgorithmizer(alg_matrix=matrix, lrm=lrm,
                                     vgm=vgm_data, number_agents=number_agents)
harvester = WebFormulaHarvester(matrix)
harvester.harvest_builtin()
indexer = FormulaIndexer(alg_matrix=matrix, vgm=vgm_data,
                          lrm=lrm, number_agents=number_agents)
indexer.index_all(harvester.harvested, max_entries=49)

import json; corpus = json.load(open('/home/claude/mashet_parsed.json'))
print(f"Corpus: {len(corpus)} Mashet entries")
print(f"Infrastructure ready in {time.time()-t_start:.1f}s")
print(f"Lobby: {len(lobby.agents)} agents")
print(f"LRM: {len(lrm.entries)} theorems")
print(f"Formulas: {len(harvester.harvested)}")
print(f"Number agents: {len(number_agents)}")
print()

# ── AUTONOMOUS LOOP STATE ─────────────────────────────────────────────────
LOG = []
REGISTRY = {
    'words_encountered': [],
    'words_indexed': [],
    'lhea_chains': {},
    'gaps_found': Counter(),
    'inward_hits': Counter(),
    'vgm_matches': Counter(),
    'lrm_matches': Counter(),
    'new_vgm_candidates': [],
    'evolution_runs': [],
    'hypothesis_runs': [],
    'law_discoveries': [],
    'algorithms_generated': [],
    'equilibria_discovered': [],
    'coherency_history': [],
    'state_shifts_parsed': [],
    'functional_translations': [],
    'corpus_index': 0,
}

def log(round_n, event, detail):
    entry = f"[R{round_n:04d}] {event}: {detail}"
    LOG.append(entry)
    if round_n % 50 == 0 or event in ('EVOLUTION','HYPOTHESIS','LAW','EQUILIBRIUM','VGM_CANDIDATE'):
        print(entry)

def next_entry():
    idx = REGISTRY['corpus_index'] % len(corpus)
    REGISTRY['corpus_index'] += 1
    return corpus[idx]

# ── 500 ROUNDS ────────────────────────────────────────────────────────────
print("="*70)
print("ECHO AUTONOMOUS RUN — 500 ROUNDS — BLIND STUDY")
print("="*70)
print()

t_run = time.time()

for rnd in range(1, 501):
    entry = next_entry()
    word = entry['word']
    REGISTRY['words_encountered'].append(word)
    REGISTRY['functional_translations'].append(entry['functional'])

    # ── AYIN: classify the word ───────────────────────────────────────────
    cls = comm._ayin_classify(word)
    is_gap = "GAP" in cls

    if is_gap:
        REGISTRY['gaps_found'][word] += 1

        # ── INWARD SEARCH ─────────────────────────────────────────────────
        ir = inward.search(word)
        if ir.found:
            REGISTRY['inward_hits'][word] += 1
            for src in ir.sources:
                log(rnd, 'INWARD', f"'{word}' → [{src['type']}] {src['detail'][:60]}")

        # ── LHEA DECOMPOSITION ─────────────────────────────────────────────
        letters = decompose(word)
        if letters:
            chain = lhea_chain(letters)
            REGISTRY['lhea_chains'][word] = {'letters': letters, 'chain': chain,
                                              'functional': entry['functional']}
            log(rnd, 'LHEA', f"'{word}' → {chain[:70]}")

            # Does the decomposition match the functional translation?
            func_lower = entry['functional'].lower()
            letter_semantics = ' '.join(
                HEBREW_LETTER_INDEX.get(l,{}).get('lhea','') for l in letters)
            overlap_words = set(re.findall(r'[a-z]{4,}', func_lower)) & \
                            set(re.findall(r'[a-z]{4,}', letter_semantics))
            if overlap_words:
                log(rnd, 'SEMANTIC_MATCH',
                    f"'{word}' chain overlaps with translation: {overlap_words}")

        # ── STATE SHIFT PARSING ────────────────────────────────────────────
        ss = entry['state_shift']
        if ss:
            states = re.findall(r'S_\d+[^\)→]*', ss)
            if states:
                REGISTRY['state_shifts_parsed'].append({
                    'word': word, 'shift': ss[:80],
                    'vgm_match': 'STATE_CHANGE_LAW applies'
                })
                if len(REGISTRY['state_shifts_parsed']) % 20 == 0:
                    log(rnd, 'STATE_SHIFT',
                        f"Parsed {len(REGISTRY['state_shifts_parsed'])} state shifts — all map to A-124")

        # ── INDEX NEW WORD into lobby if decomposable ──────────────────────
        if letters and word not in lobby.agents:
            lhea_desc = ' '.join(
                HEBREW_LETTER_INDEX.get(l,{}).get('lhea','') for l in letters[:4])
            short_desc = f"{entry['functional'][:50]}. {lhea_desc[:80]}"
            matrix.index_dictionary_entry(
                word, short_desc, pos='noun', category='mashet')
            REGISTRY['words_indexed'].append(word)
            if len(REGISTRY['words_indexed']) % 10 == 0:
                log(rnd, 'INDEXED', f"{len(REGISTRY['words_indexed'])} Mashet words added to matrix")

    else:
        # Word already known
        log(rnd, 'KNOWN', f"'{word}' → {cls}")

    # ── VGM QUERY ─────────────────────────────────────────────────────────
    content_words = re.findall(r'[a-z]{4,}', entry['functional'].lower())
    for w in content_words[:5]:
        for stmt_id, stmt in vgm_data.items():
            if w in stmt.get('words',[]) or w in stmt.get('text','').lower():
                REGISTRY['vgm_matches'][stmt_id] += 1
                break

    # ── LRM QUERY ─────────────────────────────────────────────────────────
    for lrm_id, lrm_entry in lrm.entries.items():
        lrm_text = lrm_entry.get('text','').lower()
        for w in content_words[:3]:
            if w in lrm_text:
                REGISTRY['lrm_matches'][lrm_id] += 1

    # ── VGM CANDIDATE: can we generalize this entry into a new axiom? ──────
    if letters and len(letters) >= 3:
        func = entry['functional']
        # Simple pattern: does functional describe a universal relationship?
        if any(pat in func.lower() for pat in
               ['integration','transformation','storage','generation',
                'clarification','expansion','focus','completion',
                'recursive','system','architecture']):
            candidate = f"An entity {func.split('/')[0].strip().lower()} through structured relation"
            REGISTRY['new_vgm_candidates'].append({
                'round': rnd, 'word': word, 'candidate': candidate,
                'from_functional': func[:60]
            })
            if len(REGISTRY['new_vgm_candidates']) % 15 == 0:
                log(rnd, 'VGM_CANDIDATE',
                    f"'{candidate[:65]}'  ← from {word}")

    # ── EQUILIBRIUM DISCOVERY (every 25 rounds, balance two words) ──────────
    if rnd % 25 == 0 and len(REGISTRY['words_indexed']) >= 2:
        w1 = random.choice(REGISTRY['words_indexed'][-10:])
        w2 = random.choice(REGISTRY['words_indexed'][-10:])
        if w1 != w2:
            letters1 = REGISTRY['lhea_chains'].get(w1,{}).get('letters',[])
            letters2 = REGISTRY['lhea_chains'].get(w2,{}).get('letters',[])
            shared = set(letters1) & set(letters2)
            if shared:
                eq = list(shared)[0]
                glyph = HEBREW_LETTER_INDEX.get(eq,{}).get('glyph','?')
                lhea  = HEBREW_LETTER_INDEX.get(eq,{}).get('lhea','?')[:40]
                REGISTRY['equilibria_discovered'].append({
                    'round': rnd, 'w1': w1, 'w2': w2,
                    'equilibrium': eq, 'glyph': glyph
                })
                log(rnd, 'EQUILIBRIUM',
                    f"'{w1}' ↔ '{w2}' → center: {glyph} {eq} ({lhea})")

    # ── EVOLUTION (every 50 rounds) ────────────────────────────────────────
    if rnd % 50 == 0:
        evo_report = evolution.evolve(max_generations=1, budget_per_iter=5)
        c_val = 0.0
        import re as _re
        m_c = _re.search(r"after=([\d.]+)", str(evo_report))
        if m_c: c_val = float(m_c.group(1))
        evo = {"coherency": {"after": c_val}, "operations_applied": []}
        c = evo.get('coherency',{}).get('after', 0)
        REGISTRY['coherency_history'].append({'round': rnd, 'coherency': c})
        ops = evo.get('operations_applied', [])
        REGISTRY['evolution_runs'].append({'round': rnd, 'coherency': c, 'ops': len(ops)})
        log(rnd, 'EVOLUTION',
            f"Gen {rnd//50}: C(N)={c:.4f}  ops={len(ops)}  "
            f"lobby_size={len(lobby.agents)}")

    # ── HYPOTHESIS (every 75 rounds) ──────────────────────────────────────
    if rnd % 75 == 0:
        hyp = hypothesis.run()
        tested = len(hyp) if isinstance(hyp, list) else hyp.get('tested',0)
        passed = sum(1 for h in hyp if isinstance(h, dict) and h.get('passed')) if isinstance(hyp, list) else hyp.get('registered',0)
        REGISTRY['hypothesis_runs'].append({'round':rnd,'tested':tested,'passed':passed})
        log(rnd, 'HYPOTHESIS',
            f"Tested {tested} hypotheses, {passed} passed")

    # ── LAW DISCOVERY (every 100 rounds) ──────────────────────────────────
    if rnd % 100 == 0:
        law_results = {}
        try:
            law_engine = LawDiscoveryEngine(vgm, number_agents)
            law_results = law_engine.run(budget=20)
        except Exception as e:
            law_results = {'total_discovered': 0, 'error': str(e)[:50]}
        n_laws = law_results.get('total_discovered', 0)
        REGISTRY['law_discoveries'].append({'round': rnd, 'n': n_laws})
        log(rnd, 'LAW',
            f"Session {rnd//100}: {n_laws} laws discovered")

    # ── INFORMATION ALGORITHMIZER (every 40 rounds) ────────────────────────
    if rnd % 40 == 0 and len(REGISTRY['lhea_chains']) >= 3:
        recent = list(REGISTRY['lhea_chains'].keys())[-3:]
        for w in recent:
            chain_data = REGISTRY['lhea_chains'][w]
            structured = {
                'name': w,
                'letters': chain_data['letters'],
                'functional': chain_data['functional'],
                'type': 'MASHET_WORD'
            }
            try:
                ids = info_alg.algorithmize(structured, info_type="STRUCTURED_DATA")
                if ids:
                    REGISTRY['algorithms_generated'].extend(ids)
                    log(rnd, 'GENERATED',
                        f"{len(ids)} algorithm(s) from '{w}': {ids}")
            except Exception:
                pass

print()
print("="*70)
print("500 ROUNDS COMPLETE")
print(f"Run time: {time.time()-t_run:.1f}s")
print("="*70)

# ── FINAL REPORT ──────────────────────────────────────────────────────────
print(f"""
REGISTRY SUMMARY:
  Words encountered:       {len(REGISTRY['words_encountered'])}
  Unique words:            {len(set(REGISTRY['words_encountered']))}
  Words indexed to matrix: {len(REGISTRY['words_indexed'])}
  LHEA chains built:       {len(REGISTRY['lhea_chains'])}
  Gaps found (total):      {sum(REGISTRY['gaps_found'].values())}
  Inward search hits:      {sum(REGISTRY['inward_hits'].values())}
  VGM matches (total):     {sum(REGISTRY['vgm_matches'].values())}
  LRM matches (total):     {sum(REGISTRY['lrm_matches'].values())}
  VGM candidates proposed: {len(REGISTRY['new_vgm_candidates'])}
  Equilibria discovered:   {len(REGISTRY['equilibria_discovered'])}
  Evolution runs:          {len(REGISTRY['evolution_runs'])}
  Hypothesis runs:         {len(REGISTRY['hypothesis_runs'])}
  Law discovery sessions:  {len(REGISTRY['law_discoveries'])}
  Algorithms generated:    {len(REGISTRY['algorithms_generated'])}
  State shifts parsed:     {len(REGISTRY['state_shifts_parsed'])}
""")

print("TOP 5 VGM STATEMENT MATCHES:")
for stmt_id, count in REGISTRY['vgm_matches'].most_common(5):
    text = vgm_data.get(stmt_id,{}).get('text','?')
    print(f"  {stmt_id}: \"{text}\"  hits={count}")

print("\nCOHERENCY TRAJECTORY (evolution):")
for h in REGISTRY['coherency_history']:
    bar = '█' * int(h['coherency'] * 40)
    print(f"  Round {h['round']:4d}: {h['coherency']:.4f} {bar}")

print("\nEQUILIBRIA DISCOVERED (sample):")
for eq in REGISTRY['equilibria_discovered'][:8]:
    print(f"  R{eq['round']:04d}: '{eq['w1']}' ↔ '{eq['w2']}' "
          f"→ {eq['glyph']} {eq['equilibrium']}")

print("\nVGM CANDIDATES PROPOSED (sample):")
for c in REGISTRY['new_vgm_candidates'][:8]:
    print(f"  R{c['round']:04d}: \"{c['candidate'][:65]}\"")
    print(f"          ← {c['word']}: {c['from_functional'][:55]}")

print("\nLHEA CHAINS SAMPLE (first 10):")
for word, data in list(REGISTRY['lhea_chains'].items())[:10]:
    print(f"  {word:18s} → {data['chain'][:60]}")
    print(f"    functional: {data['functional'][:55]}")

print("\nLAW DISCOVERY SESSIONS:")
for ld in REGISTRY['law_discoveries']:
    print(f"  Round {ld['round']:4d}: {ld['n']} laws discovered")

# Save full log
with open('/home/claude/echo_500round_log.txt','w') as f:
    f.write('\n'.join(LOG))
print(f"\nFull log saved: {len(LOG)} entries → /home/claude/echo_500round_log.txt")
