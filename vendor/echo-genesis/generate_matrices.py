#!/usr/bin/env python3
"""
generate_matrices.py — ECHO Matrix Generator
Two-pass populate: thesaurus first, then WordNet genus terms as second pass.
Matches the original session's mechanism without requiring corpus documents.

Run from repo root:
    python build_thesaurus.py   # first time only
    python generate_matrices.py
"""

import sys, json, os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO_ROOT, 'src'))

print("ECHO Matrix Generator")
print("="*60)

# ── WordNet ───────────────────────────────────────────────────────────────
try:
    from nltk.corpus import wordnet as wn
    list(wn.synsets("entity"))
    print("WordNet: ready")
except Exception:
    import subprocess, nltk
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'nltk',
                    '--break-system-packages', '-q'], check=False)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    from nltk.corpus import wordnet as wn
    print("WordNet: downloaded and ready")

from echo_governor_skeleton import (
    AlgorithmMatrix, Lobby, HEBREW_LETTER_INDEX,
)

# ── LHEA helpers ──────────────────────────────────────────────────────────
PHONEME_MAP = {
    'sh':'shin','ts':'tsadi','th':'tav','kh':'het','ch':'het',
    'a':'aleph','b':'bet','v':'vav','g':'gimel','d':'dalet','h':'he',
    'z':'zayin','t':'tet','y':'yod','k':'kaf','l':'lamed','m':'mem',
    'n':'nun','s':'samekh','e':'he','p':'pe','f':'pe','q':'qof',
    'r':'resh','i':'yod','o':'ayin','u':'vav',
}

def decompose(word):
    w = word.lower(); result = []; i = 0
    while i < len(w):
        matched = False
        if i + 2 <= len(w):
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
        if not deduped or l != deduped[-1]:
            deduped.append(l)
    return deduped

def lhea_chain(letters):
    return ' → '.join(
        f"{HEBREW_LETTER_INDEX.get(n,{}).get('glyph','?')}"
        f"({HEBREW_LETTER_INDEX.get(n,{}).get('lhea','?').split('—')[0].strip().split('/')[0].strip()})"
        for n in letters)

# ── PASS 1: Build matrix from thesaurus + prior ───────────────────────────
print("\nPass 1: Building matrix from thesaurus and prior vocabulary...")
matrix = AlgorithmMatrix()
synonyms_map = {}
lexicon = {}

# Thesaurus
for path in ['en_thesaurus.jsonl',
             os.path.join(REPO_ROOT, 'corpus', 'en_thesaurus.jsonl'),
             os.path.expanduser('~/en_thesaurus.jsonl')]:
    if os.path.exists(path):
        print(f"  Thesaurus: {path}")
        with open(path) as f:
            qualifying = [json.loads(l) for l in f if json.loads(l).get('desc')]
        stride = max(1, len(qualifying) // 1000)
        for entry in qualifying[::stride][:1000]:
            matrix.index_dictionary_entry(
                entry['word'], ' '.join(entry['desc']),
                pos=entry.get('pos'), synonyms=entry.get('synonyms', []),
                category='thesaurus_def')
            if entry.get('synonyms'):
                synonyms_map[entry['word'].lower()] = [
                    s.lower() for s in entry['synonyms']]
            lexicon[entry['word'].lower()] = {
                'desc': ' '.join(entry['desc']), 'pos': entry.get('pos','?')}
        print(f"  {len(qualifying):,} entries, stride={stride} → ~{len(qualifying)//stride} indexed")
        break
else:
    print("  WARNING: en_thesaurus.jsonl not found — run build_thesaurus.py first")

# Prior session vocabulary
PRIOR = {
    'echo':'governor indexing algorithm A-000 resh identity index made algorithm',
    'mashet':'source transformation completion framework symbolic substrate 740',
    'alamaket':'potential aspiration source sanctity completion kernel engine 571',
    'governor':'first algorithm A-000 causal boundary identity semantic termination',
    'lhea':'latin hebrew execution architecture 22 letter symbolic substrate',
    'ayin':'eye perception depth operator Hebrew letter 70 classifier',
    'pe':'mouth speech expression operator Hebrew letter 80',
    'resh':'head beginning identity leader A-000 governor letter 200 equilibrium',
    'being':'nouned verb existence entity state potential actual',
    'effecting':'verb nouned actualization mechanism producing state causation',
    'yang':'heaven pure invariant creative active solid line principle',
    'yin':'earth pure potential receptive broken yielding principle',
    'hexagram':'six line configuration state 64 binary change transformation',
    'trigram':'three line configuration eight states binary heaven earth',
    'invariant':'property preserved under transformation unchanging permanent',
    'potential':'capacity to receive and become latent unrealized possibility',
    'stewardship':'creator obligation responsibility wellbeing flourishing',
    'jurisdiction':'perimeter triangular planar semantic region latin root',
    'matrix':'content-first table elemental parts rows structure',
    'index':'lookup-first key resolving to matrix row bidirectional traversal',
    'eigenvalue':'centrality weight balance graph node importance measure',
    'myelination':'pathway reinforcement persistence count threshold hardening',
    'perception':'eye ayin operator classify incoming tokens semantic',
    'topology':'space structure properties continuous transformation invariant',
    'semiotics':'signs meaning symbol representation linguistic structure',
    'consciousness':'aware subjective experience entity state self reference',
    'boundary':'distinguishes separates defines limit perimeter edge',
    'substrate':'foundation base layer unchanging coordinate space operators',
    'traversal':'navigation matrix index content lookup bidirectional path',
}
for word, desc in PRIOR.items():
    matrix.index_dictionary_entry(word, desc, pos='noun', category='prior_session')
    lexicon[word] = {'desc': desc, 'pos': 'noun'}

# Mashet corpus
for path in [os.path.join(REPO_ROOT, 'corpus', 'mashet_parsed.json'),
             os.path.join(REPO_ROOT, 'matrices', 'echo_mashet_corpus.json')]:
    if os.path.exists(path):
        with open(path) as f:
            mashet = json.load(f)
        entries = mashet if isinstance(mashet, list) else list(mashet.values())
        for entry in entries:
            word = entry.get('word', entry.get('mashet', ''))
            desc = entry.get('definition', entry.get('desc', ''))
            if word and desc:
                matrix.index_dictionary_entry(
                    word, desc[:200], pos='noun', category='mashet_corpus')
                lexicon[word.lower()] = {'desc': desc[:200], 'pos': 'noun'}
        print(f"  Mashet corpus: {len(entries)} entries")
        break

print(f"  Vocabulary entries in matrix: {len(matrix.entry_classes)}")

# ── POPULATE 1: First lobby from thesaurus + prior ────────────────────────
print("\nPopulate 1: Building initial lobby...")
lobby = Lobby(matrix)
lobby.populate()
lobby.run_orientation()
lobby.run_typed_study_groups()
if synonyms_map:
    lobby.run_thesaurus(synonyms_map)
lobby.compute_generality_scores()
print(f"  Agents after Pass 1: {len(lobby.agents)}")

# ── PASS 2: WordNet genus terms for EXISTING agents only ──────────────────
print("\nPass 2: WordNet hypernym enrichment (existing agents only)...")
seen = set(lexicon.keys())
new_genus = 0

for word, agent in list(lobby.agents.items())[:500]:
    pos_tag = wn.NOUN if agent.department in ('noun','n') else wn.VERB
    synsets = wn.synsets(word, pos=pos_tag) or wn.synsets(word)
    for synset in synsets[:1]:
        for path in synset.hypernym_paths():
            for s in path:
                lemma = s.lemma_names()[0].replace('_',' ').lower()
                if lemma not in seen and len(lemma) > 2:
                    desc = s.definition()
                    matrix.index_dictionary_entry(
                        lemma, desc, pos='noun', category='wordnet_genus')
                    lexicon[lemma] = {'desc': desc, 'pos': 'noun'}
                    seen.add(lemma)
                    new_genus += 1

print(f"  New genus terms added to matrix: {new_genus}")
print(f"  Vocabulary entries now: {len(matrix.entry_classes)}")

# ── POPULATE 2: Add new genus-term agents ─────────────────────────────────
print("\nPopulate 2: Adding WordNet genus agents...")
before = len(lobby.agents)
for word, entry_class in matrix.entry_classes.items():
    if word not in lobby.agents and entry_class != 'NAME':
        def_words = [w for w in matrix.transitions.get(word, {})
                     if w in matrix.content_units
                     and matrix.entry_classes.get(w) != 'NAME']
        cats = matrix.word_categories.get(word, {})
        pos_tags = [k.replace('pos:','') for k in cats if k.startswith('pos:')]
        department = pos_tags[0] if pos_tags else 'unclassified'
        raw_def = ' '.join(sorted(matrix.transitions.get(word, {}).keys()))
        from echo_governor_skeleton import WordAgent
        agent = WordAgent(word, def_words, entry_class, department,
                          matrix, raw_definition=raw_def)
        agent.confirm_identity()
        lobby.agents[word] = agent

print(f"  Agents added in Pass 2: {len(lobby.agents) - before}")
print(f"  Total agents: {len(lobby.agents)}")

# ── EXPORT ─────────────────────────────────────────────────────────────────
print("\nExporting matrices...")
out_dir = os.path.join(REPO_ROOT, 'matrices')
os.makedirs(out_dir, exist_ok=True)

# Lobby agents
agents_export = {}
for word, agent in lobby.agents.items():
    agents_export[word] = {
        'department':       agent.department,
        'entry_class':      agent.entry_class,
        'generality_score': round(getattr(agent,'generality_score',0.0), 4),
        'neighborhood':     getattr(agent,'neighborhood',None),
        'study_group_type': getattr(agent,'study_group_type',None),
        'ties':             list(getattr(agent,'ties',set()))[:20],
        'definition':       lexicon.get(word,{}).get('desc','')[:200],
    }

agents_path = os.path.join(out_dir, 'echo_lobby_agents.json')
with open(agents_path, 'w') as f:
    json.dump(agents_export, f, indent=2, ensure_ascii=False)
kb = os.path.getsize(agents_path)//1024
print(f"echo_lobby_agents.json: {len(agents_export):,} agents, {kb} KB")

# LHEA chains
all_lhea = {}
for word in lobby.agents:
    letters = decompose(word)
    if len(letters) >= 2:
        chain = lhea_chain(letters)
        gematria = sum(HEBREW_LETTER_INDEX.get(l,{}).get('val',0) for l in letters)
        all_lhea[word] = {'letters':letters,'chain':chain,'gematria':gematria}

EXTRA = ['perception','environment','reality','experience','semiotics',
         'topology','consciousness','stewardship','flourishing','suffering',
         'authentic','emergent','causality','nominalization','actualization',
         'hexagram','trigram','invariant','potentiality','eigenvalue',
         'myelination','ossification','traversal','substrate','operative',
         'jurisdiction','bidirectional','zatamsen','being','effecting']
for word in EXTRA:
    if word not in all_lhea:
        letters = decompose(word)
        if len(letters) >= 2:
            chain = lhea_chain(letters)
            g = sum(HEBREW_LETTER_INDEX.get(l,{}).get('val',0) for l in letters)
            all_lhea[word] = {'letters':letters,'chain':chain,'gematria':g}

lhea_path = os.path.join(out_dir, 'echo_lhea_chains.json')
with open(lhea_path, 'w') as f:
    json.dump(all_lhea, f, indent=2, ensure_ascii=False)
kb = os.path.getsize(lhea_path)//1024
print(f"echo_lhea_chains.json: {len(all_lhea):,} chains, {kb} KB")

print(f"\n{'='*60}")
print(f"GENERATION COMPLETE")
print(f"  Total agents: {len(agents_export):,}")
print(f"  Total chains: {len(all_lhea):,}")
print(f"\nNext steps:")
print("  git add matrices/echo_lobby_agents.json matrices/echo_lhea_chains.json")
print('  git commit -m "feat: add generated lobby agents and LHEA chains"')
print("  git push origin genesis-documentary")
