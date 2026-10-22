"""Claude's classroom: eight lessons (ע פ צ ר ץ ש ק ת), 3-5 assignments each.

Teacher-side only. Answers are kept here and are given to Echo only after
Echo has responded, as feedback, never inside an item.
"""
import random
from world import (World, KINDS, COLORS, SIZES, TEMPS, WETS, COUNTS, COMPONENTS,
                   COMPONENT_WORDS, PLURAL, CHANNELS, OPPOSITE, DICTIONARY, describe_words)

CONTENT_CHANNELS = ['kind', 'color', 'size', 'temp', 'wet']
PASS = 0.8


class Classroom:
    def __init__(self, echo, seed, transcript=False):
        self.echo, self.w = echo, World(seed)
        self.rng = random.Random(5000 + seed)
        self.transcript = [] if transcript else None
        self.results = {}           # lesson -> list of assignment summaries
        self.heard_in = {}          # word -> {label: count}  (teacher's own record)
        self.green = {'who'}        # carried from the earlier branch: Who, tool scope
        self.claims = []
        self.questions = 0

    # ---------------- plumbing ----------------
    def say(self, **row):
        if self.transcript is not None:
            self.transcript.append(row)

    def hear(self, words, truths, label):
        self.echo.hear(words, [self.w.encode(t) for t in truths], label=label)
        for w in words:
            self.heard_in.setdefault(w, {}).setdefault(label, 0)
            self.heard_in[w][label] += 1
        self.say(turn='board', label=label, words=words, cards=[_plain(t) for t in truths])

    def recess(self):
        self.echo.rest()
        got = self.echo.recess(DICTIONARY, self.green)
        if got:
            self.claims += got
            self.say(turn='recess', claims=got)

    def run(self, label, items, mode):
        """mode: 'reveal' (show answer), 'check' (✓/X only) or 'quiz' (no feedback)."""
        practice = mode != 'quiz'
        self.echo.frozen = mode == 'quiz'
        score = 0.0
        for item, truth, plain in items:
            item = dict(item, label=label)
            seen = {k: v for k, v in item.items() if k != 'truth'}   # Echo never receives the truth
            resp = self.echo.attempt(seen, practice=practice)
            if 'question' in resp:
                target = resp['question']['asks_about']
                self.questions += 1
                self.answer_question(target, label)
                self.say(turn='echo-asks', label=label, tool='צ', about=target)
                resp = self.echo.attempt(dict(seen), practice=False)
            ok, part = grade(item, resp.get('answer'), truth)
            score += part
            self.say(turn='echo', label=label, task=plain, answer=_show(item, resp.get('answer')),
                     verdict='✓' if ok else 'X')
            if mode == 'reveal':
                self.echo.feedback(seen, resp, ok, reveal=truth)
            elif mode == 'check':
                self.echo.feedback(seen, resp, ok, reveal=None)
        self.echo.frozen = False
        acc = score / max(1, len(items))
        self.say(turn='grade', label=label, mode=mode, score=round(acc, 3))
        return acc

    def answer_question(self, word, label):
        """Teacher's reply to a צ question: two examples of the word."""
        for _ in range(2):
            t = self.example_of(word)
            if t is None:
                return
            self.echo.answer_from_teacher(word, [self.w.encode(t)])
            self.heard_in.setdefault(word, {}).setdefault('question', 0)
            self.heard_in[word]['question'] += 1

    def example_of(self, word):
        for ch, vals in CHANNELS.items():
            if word in vals:
                return self.w.card(**{ch: word}, count='one' if ch != 'count' else word)
        if word in COMPONENT_WORDS:
            kind = self.rng.choice([k for k, cs in COMPONENTS.items() if word in cs])
            return self.w.card(kind=kind, comps=[word])
        return None

    def lesson(self, glyph, plan):
        """plan: list of (name, builder, mode). Adds remediation if the quiz fails."""
        out = []
        for i, (name, build, mode) in enumerate(plan, 1):
            label = f'{glyph}-{i}'
            acc = build(label) if mode == 'board' else self.run(label, build(), mode)
            out.append(dict(assignment=label, name=name, mode=mode,
                            score=None if acc is None else round(acc, 3)))
            self.recess()
        quiz = [r for r in out if r['mode'] == 'quiz']
        if glyph != 'ת' and quiz and quiz[-1]['score'] < PASS and len(out) < 5:
            # Remediation: the failed quiz's practice again with answers shown, then a fresh retest.
            practice = [p for p in plan if p[2] in ('reveal', 'check')][-1]
            label = f'{glyph}-{len(out) + 1}'
            self.run(label, practice[1](), 'reveal')
            self.recess()
            acc = self.run(label + 'r', plan[-1][1](), 'quiz')
            out.append(dict(assignment=label, name='remediation + retest', mode='quiz', score=round(acc, 3)))
            self.recess()
        self.results[glyph] = out
        return out

    # ---------------- item builders ----------------
    def naming_items(self, n, channels=CONTENT_CHANNELS, heldout=False):
        items = []
        for _ in range(n):
            t = self.w.card(allow_heldout=heldout)
            ch = self.rng.choice(channels)
            right = t[ch]
            true_words = {t[c] for c in CHANNELS}
            pool = [v for c in CONTENT_CHANNELS for v in CHANNELS[c] if v not in true_words]
            opts = self.rng.sample(pool, 3) + [right]
            self.rng.shuffle(opts)
            items.append(({'type': 'pick_word', 'cards': [self.w.encode(t)], 'options': opts},
                          right, f'name the {ch} of {_plain(t)}'))
        return items

    def judge_items(self, n, heldout=False):
        items = []
        for _ in range(n):
            t = self.w.card(allow_heldout=heldout)
            if self.rng.random() < 0.5:
                u, right = dict(t, comps=list(t['comps'])), 'same'
            else:
                u, right = self.w.vary(t, self.rng.choice(CONTENT_CHANNELS)), 'different'
            items.append(({'type': 'pick_word', 'cards': [self.w.encode(t), self.w.encode(u)],
                           'options': ['same', 'different']}, right,
                          f'{_plain(t)} vs {_plain(u)}'))
        return items

    def yesno_items(self, n, heldout=False):
        items = []
        for _ in range(n):
            t = self.w.card(allow_heldout=heldout)
            ch = self.rng.choice(CONTENT_CHANNELS)
            word = t[ch] if self.rng.random() < 0.5 else self.rng.choice([v for v in CHANNELS[ch] if v != t[ch]])
            right = 'yes' if word == t[ch] else 'no'
            items.append(({'type': 'pick_word', 'query_words': [word], 'cards': [self.w.encode(t)],
                           'options': ['yes', 'no']}, right, f'{word}? {_plain(t)}'))
        return items

    def pick_card_items(self, n, words=None, heldout=True):
        items = []
        for _ in range(n):
            ch = self.rng.choice(CONTENT_CHANNELS)
            word = self.rng.choice(words) if words else self.rng.choice(CHANNELS[ch])
            ch = next(c for c, vs in CHANNELS.items() if word in vs)
            cards = [self.w.card(**{ch: word}, allow_heldout=heldout)]
            for _ in range(3):
                cards.append(self.w.card(**{ch: self.rng.choice([v for v in CHANNELS[ch] if v != word])},
                                         allow_heldout=heldout))
            self.rng.shuffle(cards)
            right = next(i for i, c in enumerate(cards) if c[ch] == word)
            items.append(({'type': 'pick_card', 'query_words': [word],
                           'options': [self.w.encode(c) for c in cards]}, right,
                          f'find {word} among {[_plain(c) for c in cards]}'))
        return items

    def binding_items(self, n):
        items = []
        for _ in range(n):
            color, kind = self.rng.choice(sorted(self.w.heldout_pairs))
            cards = [self.w.card(kind=kind, color=color, allow_heldout=True),
                     self.w.card(kind=kind, color=self.rng.choice([c for c in COLORS if c != color]), allow_heldout=True),
                     self.w.card(kind=self.rng.choice([k for k in KINDS if k != kind]), color=color, allow_heldout=True),
                     self.w.card(kind=self.rng.choice([k for k in KINDS if k != kind]),
                                 color=self.rng.choice([c for c in COLORS if c != color]), allow_heldout=True)]
            self.rng.shuffle(cards)
            right = next(i for i, c in enumerate(cards) if c['kind'] == kind and c['color'] == color)
            items.append(({'type': 'pick_card', 'query_words': [color, kind],
                           'options': [self.w.encode(c) for c in cards]}, right, f'find {color} {kind}'))
        return items

    def describe_items(self, n, channels, heldout=False, colors=None, kinds=None, counts=('one',)):
        items = []
        for _ in range(n):
            if heldout:
                color, kind = self.rng.choice(sorted(self.w.heldout_pairs))
                t = self.w.card(kind=kind, color=color, allow_heldout=True)
            else:
                t = self.w.card(color=self.rng.choice(colors) if colors else None,
                                kind=self.rng.choice(kinds) if kinds else None,
                                count=self.rng.choice(counts))
                if (t['color'], t['kind']) in self.w.heldout_pairs and 'color' in channels:
                    continue
            right = describe_words(t, set(channels))
            # worked example at the top of the worksheet: same shape, a different card
            ex = self.w.card(kind=self.rng.choice([k for k in (kinds or KINDS) if k != t['kind']] or KINDS),
                             count=t['count'] if t['count'] != 'one' else 'one')
            example = {'words': describe_words(ex, set(channels)), 'card': self.w.encode(ex)}
            items.append(({'type': 'describe', 'cards': [self.w.encode(t)], 'n': len(right), 'truth': t,
                           'example': example}, right, f'describe {_plain(t)} (example: {" ".join(example["words"])})'))
        return items

    def match_items(self, n):
        items = []
        for _ in range(n):
            kinds = self.rng.sample(KINDS, 4)
            truths = [self.w.card(kind=k, allow_heldout=True) for k in kinds]
            words = []
            for i, t in enumerate(truths):
                others = truths[:i] + truths[i + 1:]
                cand = [t[c] for c in CONTENT_CHANNELS if all(o[c] != t[c] for o in others) and t[c] not in words]
                words.append(self.rng.choice(cand))
            right = {w: i for i, w in enumerate(words)}
            items.append(({'type': 'match', 'words': list(words), 'cards': [self.w.encode(t) for t in truths]},
                          right, f'match {words} to {[_plain(t) for t in truths]}'))
        return items

    def sort_items(self, comps):
        items = []
        for c in comps:
            right = sorted(k for k, cs in COMPONENTS.items() if c in cs)
            items.append(({'type': 'relate', 'query_words': ['part', c], 'options': list(KINDS), 'multi': True},
                          right, f'{c} goes in which envelope(s)?'))
        return items

    def opposite_items(self, words):
        items = []
        for x in words:
            right = OPPOSITE[x]
            ch = next(c for c, vs in CHANNELS.items() if x in vs)
            distract = [v for c in CONTENT_CHANNELS if c != ch for v in CHANNELS[c]]
            opts = self.rng.sample(distract, 2) + [x, right]
            self.rng.shuffle(opts)
            items.append(({'type': 'relate', 'query_words': ['opposite', x], 'options': opts},
                          right, f'opposite of {x}'))
        return items

    def recall_items(self, n):
        items = []
        words = [w for w, labs in self.heard_in.items() if 'question' not in labs or len(labs) > 1]
        for _ in range(n):
            w = self.rng.choice(sorted(words))
            labs = {k: v for k, v in self.heard_in[w].items() if k != 'question'}
            if not labs:
                continue
            right = max(sorted(labs), key=lambda k: labs[k])
            others = sorted({l for v in self.heard_in.values() for l in v} - set(labs) - {'question'})
            opts = self.rng.sample(others, min(3, len(others))) + [right]
            self.rng.shuffle(opts)
            items.append(({'type': 'recall', 'query_words': [w], 'options': opts}, right,
                          f'where did you meet "{w}" most?'))
        return items

    def plural_pick_items(self, kinds):
        items = []
        for k in kinds:
            cards = [self.w.card(kind=k, count=self.rng.choice(['two', 'many']), allow_heldout=True),
                     self.w.card(kind=k, count='one', allow_heldout=True),
                     self.w.card(kind=self.rng.choice([x for x in KINDS if x != k]), count='two', allow_heldout=True)]
            self.rng.shuffle(cards)
            right = next(i for i, c in enumerate(cards) if c['kind'] == k and c['count'] != 'one')
            items.append(({'type': 'pick_card', 'query_words': [PLURAL[k]],
                           'options': [self.w.encode(c) for c in cards]}, right, f'find {PLURAL[k]}'))
        return items

    def component_pick_items(self, c, n=3):
        items = []
        kinds = [k for k, cs in COMPONENTS.items() if c in cs]
        for _ in range(n):
            k = self.rng.choice(kinds)
            yes = self.w.card(kind=k, comps=[c] + [x for x in COMPONENTS[k] if x != c], allow_heldout=True)
            no1 = self.w.card(kind=k, comps=[x for x in COMPONENTS[k] if x != c], allow_heldout=True)
            no2 = self.w.card(kind=self.rng.choice([x for x in KINDS if c not in COMPONENTS[x]]), comps='all',
                              allow_heldout=True)
            cards = [yes, no1, no2]
            self.rng.shuffle(cards)
            right = cards.index(yes)
            items.append(({'type': 'pick_card', 'query_words': [c],
                           'options': [self.w.encode(x) for x in cards]}, right, f'find the card showing {c}'))
        return items

    # ---------------- boards (passive exposure) ----------------
    def board_encounter(self, label, n=36):
        for _ in range(n):
            t = self.w.card()
            chans = set(self.rng.sample(CONTENT_CHANNELS, self.rng.choice([2, 3])))
            self.hear(describe_words(t, chans), [t], label)

    def board_demo_judge(self, label):
        for _ in range(3):
            t = self.w.card()
            self.hear(['same'], [t, dict(t, comps=list(t['comps']))], label)
            self.hear(['different'], [t, self.w.vary(t, self.rng.choice(CONTENT_CHANNELS))], label)

    def board_phrases(self, label, n=24):
        colors = [c for c in COLORS if c not in ('white', 'black')]
        for _ in range(n):
            t = self.w.card(color=self.rng.choice(colors))
            if (t['color'], t['kind']) in self.w.heldout_pairs:
                continue
            chans = {'color', 'kind'} if self.rng.random() < 0.5 else {'size', 'color', 'kind'}
            self.hear(describe_words(t, chans), [t], label)

    def board_what(self, label):
        for _ in range(4):
            t = self.w.card()
            ch = self.rng.choice(CONTENT_CHANNELS)
            self.hear(['what', t[ch]], [t], label)
        self.echo.questions_on = True

    def board_yesno(self, label):
        for _ in range(4):
            t = self.w.card()
            ch = self.rng.choice(CONTENT_CHANNELS)
            self.hear([t[ch], 'yes'], [t], label)
            other = self.rng.choice([v for v in CHANNELS[ch] if v != t[ch]])
            self.hear([other, 'no'], [t], label)

    def board_components(self, label, per_component=4):
        # every component is shown, spread over every kind that has it
        for c in COMPONENT_WORDS:
            kinds = [k for k, cs in COMPONENTS.items() if c in cs]
            for i in range(per_component):
                k = kinds[i % len(kinds)]
                t = self.w.card(kind=k, comps=[c] + [x for x in COMPONENTS[k] if x != c and self.rng.random() < 0.7])
                self.hear([c, 'part', k], [t], label)

    def board_counts(self, label, n=48):
        for _ in range(n):
            t = self.w.card(kind=self.rng.choice(['bird', 'fish', 'tree', 'dog']), count=self.rng.choice(COUNTS))
            self.hear(describe_words(t, {'count', 'kind'}), [t], label)

    def board_opposite(self, label):
        for x in ['big', 'hot']:
            ch = next(c for c, vs in CHANNELS.items() if x in vs)
            for _ in range(2):
                self.hear(['opposite', x, OPPOSITE[x]], [self.w.card(**{ch: x}), self.w.card(**{ch: OPPOSITE[x]})], label)

    def board_rest_only(self, label, cycles=6):
        for _ in range(cycles):
            self.recess()
        self.say(turn='board', label=label, words=[], cards=[], note=f'{cycles} recess cycles, no lessons')

    # ---------------- the course ----------------
    def course(self):
        b = lambda f, *a, **k: (lambda label=None: (f(label, *a, **k), None)[1])
        L = self.lesson
        L('ע', [('encounter board', b(self.board_encounter), 'board'),
                ('same/different demo', b(self.board_demo_judge), 'board'),
                ('same/different, ✓/X only', lambda: self.judge_items(20), 'check'),
                ('same/different, answers shown', lambda: self.judge_items(20), 'reveal'),
                ('quiz: same/different, new cards', lambda: self.judge_items(16, heldout=True), 'quiz')])
        L('פ', [('naming practice', lambda: self.naming_items(24), 'reveal'),
                ('phrase board', b(self.board_phrases), 'board'),
                ('describe practice', lambda: self.describe_items(12, ['color', 'kind'], colors=['red', 'green', 'yellow']), 'reveal'),
                ('quiz: describe new combinations', lambda: self.describe_items(6, ['color', 'kind'], heldout=True)
                 + self.describe_items(6, ['size', 'color', 'kind'], heldout=True), 'quiz')])
        L('צ', [('what demo (questions unlocked)', b(self.board_what), 'board'),
                ('matching columns', lambda: self.match_items(8), 'reveal'),
                ('naming with questions allowed', lambda: self.naming_items(20, ['temp', 'wet', 'size']), 'reveal'),
                ('quiz: matching columns', lambda: self.match_items(6), 'quiz')])
        L('ר', [('find the card', lambda: self.pick_card_items(20, heldout=False), 'reveal'),
                ('yes/no demo', b(self.board_yesno), 'board'),
                ('yes/no, ✓/X only', lambda: self.yesno_items(20), 'check'),
                ('quiz: two-word find + yes/no', lambda: self.binding_items(8) + self.yesno_items(8, heldout=True), 'quiz')])
        L('ץ', [('envelope board: X part Y', b(self.board_components), 'board'),
                ('sort into envelopes', lambda: self.sort_items(self.rng.sample(COMPONENT_WORDS, 6) * 2), 'reveal'),
                ('quiz: sort every component', lambda: self.sort_items(COMPONENT_WORDS * 2), 'quiz')])
        L('ש', [('count board', b(self.board_counts), 'board'),
                ('plural describe practice', lambda: self.describe_items(12, ['count', 'kind'], kinds=['bird', 'fish', 'tree', 'dog'],
                                                                          counts=COUNTS), 'reveal'),
                ('opposites board + practice', lambda: (self.board_opposite('ש-opp'), self.opposite_items(['big', 'small', 'hot', 'cold'] * 3))[1], 'reveal'),
                ('quiz: new plurals + new opposite pair', lambda: self.describe_items(6, ['count', 'kind'], kinds=['stone', 'sun'], counts=['two', 'many'])
                 + self.describe_items(2, ['count', 'kind'], kinds=['fish'], counts=['two', 'many'])
                 + self.opposite_items(['wet', 'dry', 'wet', 'dry']), 'quiz')])
        L('ק', [('where did you meet it', lambda: self.recall_items(12), 'reveal'),
                ('find a new example', lambda: self.pick_card_items(12), 'reveal'),
                ('quiz: sources + examples', lambda: self.recall_items(8) + self.pick_card_items(8), 'quiz')])
        L('ת', [('delay: recess only', b(self.board_rest_only), 'board'),
                ('retention quiz, all lesson types', lambda: self.naming_items(6, heldout=True) + self.judge_items(4, heldout=True)
                 + self.yesno_items(4, heldout=True) + self.describe_items(4, ['color', 'kind'], heldout=True)
                 + self.sort_items(self.rng.sample(COMPONENT_WORDS, 3)) + self.opposite_items(['big', 'cold', 'wet']), 'quiz'),
                ('handover: green tests', b(self.handover), 'board')])
        return self.results

    # ---------------- handover: three-part green bar after the delay ----------------
    def green_tests(self, word):
        """(recognition items, use items) or None if this pilot has no test for the word."""
        for ch, vals in CHANNELS.items():
            if word in vals:
                rec = self.pick_card_items(3, words=[word])
                use = []
                for _ in range(3):
                    t = self.w.card(**{ch: word}, allow_heldout=True) if ch != 'count' else \
                        self.w.card(count=word, allow_heldout=True)
                    true_words = {t[c] for c in CHANNELS}
                    pool = [v for c in CONTENT_CHANNELS for v in CHANNELS[c] if v not in true_words]
                    opts = self.rng.sample(pool, 3) + [word]
                    self.rng.shuffle(opts)
                    use.append(({'type': 'pick_word', 'cards': [self.w.encode(t)], 'options': opts}, word, f'name {word}'))
                return rec, use
        if word in COMPONENT_WORDS:
            return self.component_pick_items(word), self.sort_items([word] * 3)
        if word in ('same', 'different'):
            items = [i for i in self.judge_items(30, heldout=True) if i[1] == word]
            return items[:3], items[3:6]
        if word in ('yes', 'no'):
            items = [i for i in self.yesno_items(30, heldout=True) if i[1] == word]
            return items[:3], items[3:6]
        if word == 'opposite':
            return self.opposite_items(['big', 'hot', 'wet']), self.opposite_items(['small', 'cold', 'dry'])
        if word == 'part':
            return self.sort_items(['wing', 'fin', 'leaf']), self.sort_items(['tail', 'leg', 'root'])
        base = next((k for k, p in PLURAL.items() if p == word and p != k), None)
        if base:
            use = self.describe_items(3, ['count', 'kind'], kinds=[base], counts=['two', 'many'])
            return self.plural_pick_items([base] * 3), use
        return None

    def handover(self, label):
        report = {}
        vocab = sorted(DICTIONARY)
        for word in vocab:
            if word in self.green:
                report[word] = 'green (carried)'
                continue
            tests = self.green_tests(word)
            if tests is None:
                report[word] = 'untested in pilot'
                continue
            rec = self.run(label + ':' + word + ':rec', tests[0], 'quiz')
            use = self.run(label + ':' + word + ':use', tests[1], 'quiz')
            if rec >= 2 / 3 and use >= 2 / 3:
                self.green.add(word)
                report[word] = 'green'
            else:
                report[word] = f'not yet (recognition {rec:.2f}, use {use:.2f})'
        # One more recess with the new green set. Echo may claim entries whose
        # definitions are all green; the teacher tests each claim before accepting it.
        self.claims = []
        self.recess()
        self.claims_checked = {}
        for word in self.claims:
            tests = self.green_tests(word)
            if tests is None:
                self.claims_checked[word] = 'pending: no pilot test for this word'
                continue
            rec = self.run(label + ':claim:' + word + ':rec', tests[0], 'quiz')
            use = self.run(label + ':claim:' + word + ':use', tests[1], 'quiz')
            ok = rec >= 2 / 3 and use >= 2 / 3
            if ok:
                self.green.add(word)
                report[word] = 'green (claimed at recess, verified)'
            self.claims_checked[word] = 'accepted' if ok else f'rejected (recognition {rec:.2f}, use {use:.2f})'
        self.handover_report = report


def grade(item, ans, truth):
    t = item['type']
    if t == 'match':
        if not isinstance(ans, dict):
            return False, 0.0
        hits = sum(1 for w, i in truth.items() if ans.get(w) == i)
        return hits == len(truth), hits / len(truth)
    if t == 'relate' and item.get('multi'):
        ok = sorted(ans or []) == sorted(truth)
        return ok, float(ok)
    if t == 'describe':
        # Any true description with correct grammar passes: right length, every word true
        # of the card, kind word last, convention order, plural form when count > one.
        ok = _good_description(item, list(ans or []), list(truth))
        return ok, float(ok)
    ok = ans == truth
    return ok, float(ok)


def _good_description(item, ans, truth):
    """True of the card, kind word last, convention order, plural kind when count > one."""
    t = item['truth']
    if len(ans) != len(truth) or not ans:
        return False
    order = ['count', 'size', 'temp', 'wet', 'color', 'kind']
    kind_form = PLURAL[t['kind']] if t['count'] != 'one' else t['kind']
    chans = []
    for w in ans:
        hit = 'kind' if w == kind_form else next((ch for ch in order[:-1] if t[ch] == w), None)
        if hit is None:
            return False
        chans.append(hit)
    if chans[-1] != 'kind' or len(set(chans)) != len(chans):
        return False
    return [order.index(c) for c in chans] == sorted(order.index(c) for c in chans)


def _plain(t):
    s = f"{t['count']} {t['size']} {t['temp']} {t['wet']} {t['color']} {t['kind']}"
    return s + (f" [{', '.join(t['comps'])}]" if t['comps'] else '')


def _show(item, ans):
    if item['type'] == 'pick_card' and isinstance(ans, int):
        return f'card {ans}'
    return ans
