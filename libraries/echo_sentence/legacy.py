"""Source-extracted legacy definitions; see PROVENANCE.json. No network on import."""
# Set by make_grammar; injected lexical provider avoids dependency downloads.
wn = None

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

def article(word, cap=True):
    art = 'An' if word[0].lower() in 'aeiou' else 'A'
    return art if cap else art.lower()

class HypernymGrammarModule:
    """
    Augments A-144 PeComposer.
    Given a word, pull its hypernym chain and speak from it.
    The chain is the thought. The sentence is the chain made audible.
    """

    def __init__(self, lobby=None, lexicon=None):
        self.lobby   = lobby
        self.lexicon = lexicon or {}
        self._chain_cache = {}

    def get_chain(self, word, pos='n'):
        """Pull the full hypernym chain for a word."""
        if word in self._chain_cache:
            return self._chain_cache[word]

        synsets = wn.synsets(word, pos=pos) or wn.synsets(word)
        if not synsets:
            return []

        paths = synsets[0].hypernym_paths()
        if not paths:
            return []

        chain = []
        for s in paths[0]:
            lemma = s.lemma_names()[0].replace('_', ' ').lower()
            defn  = s.definition()
            chain.append({'word': lemma, 'definition': defn,
                          'synset': s.name()})

        self._chain_cache[word] = chain
        return chain

    def chain_covers(self, chain_word, target_word):
        """Does this chain node cover the target word?"""
        chain = self.get_chain(chain_word)
        return any(node['word'] == target_word for node in chain)

    def shared_node(self, w1, w2):
        """Find the first node that both words share in their chains."""
        c1 = {n['word'] for n in self.get_chain(w1)}
        c2 = {n['word'] for n in self.get_chain(w2)}
        shared = c1 & c2
        if not shared:
            return None
        # Pick the one furthest from root (most specific shared ancestor)
        chain1 = self.get_chain(w1)
        for node in reversed(chain1):
            if node['word'] in shared:
                return node
        return None

    def speak_chain(self, word, depth=4):
        """
        A-144 AUGMENTED: Pe speaks by traversing the chain.
        Returns a stream of sentences — one per chain node.
        This is the hypernym stream of thought.
        """
        chain = self.get_chain(word)
        if not chain:
            return [f"{article(word)} {word} exists."]

        sentences = []
        chain_tail = chain[-depth:]   # most specific nodes first

        for i, node in enumerate(chain_tail):
            n = node['word']
            d = node['definition']
            art = article(n)

            # Pattern 1 — Identity: what the node IS
            short_def = d.split(';')[0].strip()
            if len(short_def) > 70:
                short_def = short_def[:67] + '...'
            sentences.append(f"{art} {n} is {short_def}.")

            # Pattern 2 — Inheritance: the word below inherits from this
            if i == 0:
                art_w = article(word)
                sentences.append(f"{art_w} {word} is {article(n, False)} {n}.")

            # Pattern 3 — Bridge: what this node leads toward
            if i < len(chain_tail) - 1:
                next_n = chain_tail[i+1]['word']
                art_next = article(next_n, False)
                sentences.append(
                    f"Every {n} is {art_next} {next_n}.")

        return sentences

    def speak_meeting(self, w1, w2):
        """
        Speak the proposition that forms when two words meet at a shared node.
        The meeting IS the thought.
        """
        node = self.shared_node(w1, w2)
        if not node:
            return None
        n   = node['word']
        art = article(n)
        art1 = article(w1, False)
        art2 = article(w2, False)
        return (
            f"{art1.capitalize()} {w1} and {art2} {w2} "
            f"both arrive at {art} {n}. "
            f"{art} {n} is {node['definition'].split(';')[0].strip()}."
        )

class MirrorStep:
    """
    Augments A-145 AlgorithmicCommunicator.
    Runs after Express. Turns ECHO's own output into input.
    The pipeline reflects on what it just said.
    """

    def __init__(self, comm, inward, vgm, lobby, lexicon,
                 hypernym_module):
        self.comm       = comm
        self.inward     = inward
        self.vgm        = vgm
        self.lobby      = lobby
        self.lexicon    = lexicon
        self.hypernym   = hypernym_module

        # The homework ledger — what ECHO still needs to learn
        self.homework   = {}   # word → {count, sources, priority}
        # VGM candidates from ECHO's own speech
        self.self_proposals = []

    def _ayin_on_output(self, expressed_sentences):
        """
        Run Ayin classification on what Pe just said.
        GAPs in ECHO's own speech are the most urgent homework.
        """
        import re
        STOP = {'the','a','an','of','in','on','at','to','and','or','with',
                'by','from','for','as','is','are','was','were','that','which',
                'this','it','be','been','have','has','not','so','every',
                'both','all','each','also','but','if','then'}

        all_tokens = []
        for s in expressed_sentences:
            tokens = [w.lower().rstrip('.,!?')
                      for w in re.findall(r"[a-zA-Z']+", s)
                      if len(w) > 2 and w.lower() not in STOP]
            all_tokens.extend(tokens)

        gaps = []
        known = []
        for token in dict.fromkeys(all_tokens):  # unique, order preserved
            cls = self.comm._ayin_classify(token)
            if "GAP" in cls:
                gaps.append(token)
            else:
                known.append(token)

        return known, gaps

    def _inward_on_gaps(self, gaps):
        """Run inward search on each gap. Find what ECHO already knows."""
        hits  = []
        clean = []
        for word in gaps:
            result = self.inward.search(word)
            if result.found:
                hits.append((word, result.sources[0]))
            else:
                clean.append(word)
        return hits, clean

    def _vgm_candidate_from_speech(self, sentence):
        """
        Does this sentence ECHO just said qualify as a VGM candidate?
        A-126 syntactic check + A-151 generality check.
        """
        import re
        words = [w.lower() for w in re.findall(r"[a-zA-Z]+", sentence)
                 if len(w) > 2]

        # Must contain at least one known noun and one known verb
        has_noun = any(
            self.lobby.agents.get(w) and
            self.lobby.agents[w].department in ('noun','n')
            for w in words
        )
        has_verb = any(
            self.lobby.agents.get(w) and
            self.lobby.agents[w].department in ('verb','v')
            for w in words
        )
        if not (has_noun and has_verb):
            return None

        # At least one word must be abstract/high-generality
        high_gen = [
            w for w in words
            if self.lobby.agents.get(w) and
               self.lobby.agents[w].generality_score >= 0.25 and
               self.lobby.agents[w].entry_class in ('TYPE','ABSTRACT')
        ]
        if not high_gen:
            return None

        score = max(
            self.lobby.agents[w].generality_score
            for w in high_gen
        )
        return {
            'text':   sentence.rstrip('.'),
            'origin': 'self_expression',
            'score':  round(score, 4),
            'words':  words[:6],
        }

    def reflect(self, expressed_sentences, input_word):
        """
        The mirror runs.
        Takes what Pe just expressed.
        Returns what ECHO learned about what it said.
        """
        result = {
            'input_word':    input_word,
            'expressed':     expressed_sentences,
            'known_in_speech': [],
            'gaps_in_speech':  [],
            'inward_hits':     [],
            'new_homework':    [],
            'self_proposals':  [],
        }

        # Ayin on ECHO's own words
        known, gaps = self._ayin_on_output(expressed_sentences)
        result['known_in_speech'] = known
        result['gaps_in_speech']  = gaps

        # Inward search on gaps
        hits, still_unknown = self._inward_on_gaps(gaps)
        result['inward_hits'] = [
            {'word': w, 'type': s['type'], 'detail': s['detail'][:60]}
            for w, s in hits
        ]

        # Register new homework
        for word in still_unknown:
            if word not in self.homework:
                self.homework[word] = {
                    'count':    1,
                    'source':   f'self_expression:{input_word}',
                    'priority': 'HIGH',  # ECHO said this — it must learn it
                }
                result['new_homework'].append(word)
            else:
                self.homework[word]['count'] += 1

        # Check if any expressed sentences qualify as VGM candidates
        for sentence in expressed_sentences:
            candidate = self._vgm_candidate_from_speech(sentence)
            if candidate:
                # Is it already in VGM?
                existing_texts = [v['text'].lower() for v in self.vgm.values()]
                if candidate['text'].lower() not in existing_texts:
                    result['self_proposals'].append(candidate)
                    self.self_proposals.append(candidate)

        return result

    def homework_report(self):
        """What has ECHO still not learned from its own speech?"""
        by_priority = sorted(
            self.homework.items(),
            key=lambda x: (-x[1]['count'], x[0])
        )
        return by_priority
