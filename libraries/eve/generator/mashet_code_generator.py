#!/usr/bin/env python3
# =============================================================================
# MASHET CODE GENERATOR
#
# Implements the generative pipeline from "Mashet as Operational Practice":
# concept description -> required substrates -> candidate letters ->
# optimal coverage -> constructed word -> executable function.
#
# Self-contained, standard-library only — no dependencies, runs directly in
# Pydroid3.
#
# LETTER_SUBSTRATES below are drawn from the actual established meanings
# built up across this session's dictionary work (the 210 Aleph-Zayin
# entries + the 10 Het entries) and the ISA opcode table from earlier
# (Ayin=Perception, Tsade=Order/Alignment, etc.) — not invented fresh here.
#
# HONEST LIMITATION: this does NOT verify constructed words against real
# Hebrew vocabulary. Same caveat as the hand-authored dictionary entries —
# designed to be unlikely to collide, not verified not to. If this matters
# for a specific word, check it by hand before treating it as canon.
# =============================================================================

import re
from datetime import datetime

LETTER_SUBSTRATES = {
    'א': ['potential', 'creation', 'genesis', 'origin', 'instantiation', 'new'],
    'ב': ['house', 'internalize', 'containment', 'domestic', 'contains'],
    'ג': ['bridge', 'motion', 'transfer', 'external', 'reach', 'tension'],
    'ד': ['door', 'threshold', 'passage', 'access', 'entry', 'exit'],
    'ה': ['breath', 'respiration', 'revelation', 'activation', 'window', 'reveal'],
    'ו': ['link', 'connection', 'binding', 'joining', 'connect'],
    'ז': ['blade', 'direction', 'sharpen', 'focus', 'cutting', 'separation', 'threat'],
    'ח': ['boundary', 'wall', 'protection', 'enclosure', 'defense', 'seal_temp', 'guard'],
    'ט': ['coil', 'wrap', 'twist', 'compress', 'tight'],
    'י': ['point', 'reduce', 'singularity', 'precision', 'action', 'hand'],
    'כ': ['palm', 'grasp', 'control', 'hold', 'cover'],
    'ל': ['goad', 'elevate', 'guide', 'teach', 'lift', 'authority_soft'],
    'מ': ['matrix', 'flow', 'flood', 'liquid', 'distribution', 'propagation'],
    'נ': ['seed', 'flow_continuity', 'containment_storage', 'life', 'growth'],
    'ס': ['circle', 'loop', 'support', 'recursion', 'stabilize', 'reinforce'],
    'ע': ['perception', 'sight', 'awareness', 'observation', 'perceive', 'detect'],
    'פ': ['mouth', 'portal', 'output', 'expression', 'speech', 'signal'],
    'צ': ['order', 'alignment', 'righteousness', 'target', 'pursuit'],
    'ק': ['horizon', 'span', 'cyclical', 'time', 'distance'],
    'ר': ['command', 'authority', 'pattern', 'head', 'governance', 'response'],
    'ש': ['fire', 'transformation', 'process', 'ignition', 'consumption'],
    'ת': ['final_sign', 'seal', 'limit', 'completion', 'terminal', 'permanent', 'irreversible'],
}

LETTER_NAMES = {
    'א': 'Aleph', 'ב': 'Bet', 'ג': 'Gimel', 'ד': 'Dalet', 'ה': 'He', 'ו': 'Vav',
    'ז': 'Zayin', 'ח': 'Het', 'ט': 'Tet', 'י': 'Yod', 'כ': 'Kaf', 'ל': 'Lamed',
    'מ': 'Mem', 'נ': 'Nun', 'ס': 'Samekh', 'ע': 'Ayin', 'פ': 'Pe', 'צ': 'Tsade',
    'ק': 'Qof', 'ר': 'Resh', 'ש': 'Shin', 'ת': 'Tav',
}

TRANSLIT = {
    'א': 'a', 'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h', 'ו': 'v', 'ז': 'z',
    'ח': 'ch', 'ט': 't', 'י': 'y', 'כ': 'k', 'ל': 'l', 'מ': 'm', 'נ': 'n',
    'ס': 's', 'ע': "'", 'פ': 'p', 'צ': 'ts', 'ק': 'q', 'ר': 'r', 'ש': 'sh', 'ת': 't',
}

MASHET_OPERATIONS = {}


class MashetCodeGenerator:
    def __init__(self, letter_substrates=None):
        self.substrates = letter_substrates or LETTER_SUBSTRATES

    STOPWORDS = {'a', 'an', 'the', 'that', 'this', 'and', 'or', 'but', 'in', 'on',
                 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were', 'be',
                 'been', 'it', 'its', 'as', 'by', 'from'}

    def _stem_variants(self, word):
        """Return multiple plausible stems, not just one — naive single-rule
        stemming missed 'perceives' -> 'perceive' (stripping 'es' gave
        'perceiv', which doesn't match the tag 'perceive'). Checking several
        candidate stems fixes that without needing a full stemmer library."""
        variants = {word}
        for suffix in ('ies', 'es', 'ed', 'ing', 's'):
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                variants.add(word[:-len(suffix)])
                variants.add(word[:-len(suffix)] + 'e')  # perceives -> perceiv -> perceive
        return variants

    def analyze_concept(self, concept_description):
        """Step 1: match keywords in the description against substrate tags."""
        words = re.findall(r"[a-zA-Z_]+", concept_description.lower())
        words = [w for w in words if w not in self.STOPWORDS and len(w) >= 3]

        word_stems = set()
        for w in words:
            word_stems |= self._stem_variants(w)

        matched = set()
        all_tags = {tag for tags in self.substrates.values() for tag in tags}
        for tag in all_tags:
            tag_stems = self._stem_variants(tag)
            if word_stems & tag_stems:
                matched.add(tag)
        return matched

    def find_participating_letters(self, required_substrates):
        """Step 2: which letters carry at least one required substrate."""
        candidates = {}
        for letter, tags in self.substrates.items():
            hit = required_substrates.intersection(tags)
            if hit:
                candidates[letter] = hit
        return candidates

    def optimize_coverage(self, candidate_letters, required_substrates, max_letters=6):
        """Step 3: greedy set-cover — repeatedly pick the letter covering
        the most still-uncovered required substrates, until covered or
        max_letters reached."""
        uncovered = set(required_substrates)
        chosen = []
        remaining = dict(candidate_letters)

        while uncovered and remaining and len(chosen) < max_letters:
            best_letter = max(remaining, key=lambda l: len(remaining[l] & uncovered))
            best_cover = remaining[best_letter] & uncovered
            if not best_cover:
                break
            chosen.append(best_letter)
            uncovered -= best_cover
            del remaining[best_letter]

        return chosen, uncovered  # uncovered = anything we couldn't find a letter for

    def construct_word(self, letters):
        """Step 4: chain letters into a pronounceable constructed word,
        following the vowel-pattern style of the existing dictionary
        entries (Chalamnish, Chatamran, etc.) — alternating letter with a
        simple vowel, ending on a closing consonant."""
        vowel_cycle = ['a', 'a', 'e', 'o', 'e', 'i']
        pieces = []
        for i, letter in enumerate(letters):
            pieces.append(TRANSLIT[letter])
            if i < len(letters) - 1:
                pieces.append(vowel_cycle[i % len(vowel_cycle)])
        transliteration = ''.join(pieces).capitalize()
        hebrew_word = ''.join(letters)  # unvocalized consonant skeleton
        return hebrew_word, transliteration

    def generate_function(self, hebrew_word, transliteration, letters, concept_description, matched_substrates):
        """Step 5: emit an executable function stub with a real,
        substrate-derived docstring — Functional Translation, Structural
        Logic per letter, State Shift, ready to register and call."""
        func_name = re.sub(r"[^a-z_]", "", transliteration.lower())

        logic_lines = []
        for letter in letters:
            tags = self.substrates[letter]
            relevant = [t for t in tags if t in matched_substrates] or [tags[0]]
            logic_lines.append(f"    * {LETTER_NAMES[letter]} ({letter}) contributes: {', '.join(relevant)}")

        docstring = (
            f"{hebrew_word} ({transliteration}) — generated for: \"{concept_description}\"\n\n"
            f"    Structural Logic:\n" + "\n".join(logic_lines) + "\n\n"
            f"    State Shift: (S_0) Unresolved Concept -> (S_1) {transliteration} Activated.\n"
            f"    Generated: {datetime.now().isoformat(timespec='seconds')}"
        )

        function_code = f'''
def {func_name}(data, context=None):
    """
    {docstring}
    """
    substrates_activated = {sorted(matched_substrates)}
    letters_used = {letters}
    return {{
        "word": "{hebrew_word}",
        "transliteration": "{transliteration}",
        "substrates": substrates_activated,
        "letters": letters_used,
        "data": data,
        "context": context,
    }}
'''
        namespace = {}
        exec(compile(function_code, f'<mashet_generated:{func_name}>', 'exec'), namespace)
        generated_fn = namespace[func_name]
        MASHET_OPERATIONS[hebrew_word] = generated_fn
        return generated_fn, function_code

    def generate_operation_for_concept(self, concept_description, max_letters=6, verbose=True):
        """The full pipeline, steps 1-5, run end to end."""
        matched = self.analyze_concept(concept_description)
        if verbose:
            print(f"Concept: \"{concept_description}\"")
            print(f"Matched substrates: {sorted(matched)}")

        if not matched:
            print("  No substrates matched — try different wording.")
            return None

        candidates = self.find_participating_letters(matched)
        if verbose:
            print(f"Candidate letters: {[(l, sorted(s)) for l, s in candidates.items()]}")

        chosen, uncovered = self.optimize_coverage(candidates, matched, max_letters)
        if verbose:
            print(f"Chosen letters (in order): {[(l, LETTER_NAMES[l]) for l in chosen]}")
            if uncovered:
                print(f"  (substrates not coverable with available letters: {uncovered})")

        if not chosen:
            print("  Could not construct a word — no covering letters found.")
            return None

        hebrew_word, translit = self.construct_word(chosen)
        fn, code = self.generate_function(hebrew_word, translit, chosen, concept_description, matched)

        if verbose:
            print(f"\nGENERATED WORD: {hebrew_word} ({translit})")
            print(f"\n--- Generated function ---{code}")

        return fn


if __name__ == "__main__":
    generator = MashetCodeGenerator()

    print("=" * 78)
    print(" MASHET CODE GENERATOR — test run")
    print("=" * 78)
    print()

    # A genuinely NEW concept, not already in the 220 hand-authored entries —
    # the real test of whether this generates something plausible on its own.
    new_op = generator.generate_operation_for_concept(
        "A mechanism that perceives an external threat and seals the boundary permanently in response"
    )

    if new_op:
        print("\n--- Calling the generated function ---")
        result = new_op("incoming_intrusion_event")
        for k, v in result.items():
            print(f"  {k}: {v}")
