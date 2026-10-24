"""Claude's classroom for Echo's talk course (teacher side; Echo never imports this).

Lessons by glyph role:
  ע noticing    Echo is shown items while a word is said ("a python file", "the recess file", "three files")
  פ naming      Echo names a shown item from a few words (practice, with ✓/✗ and the right word on ✗)
  צ questions   whenever Echo asks about a word, the teacher answers with examples, or says it belongs to the question
  ר recognition Echo picks the item a word names (practice)
  ת checking    delayed tests on unseen items, no feedback: green = recognition ≥2/3 and use ≥2/3
Dialogue lessons: questions about a desk of files, in varied phrasings; ✓/✗ and, on ✗, the teacher's own reply
(the word, and a gesture at the items meant). New words are sometimes slipped in so Echo has to ask.
"""
import random

from world_repo import CONTENT_WORDS, NUMBERS, YESNO, World

# Teaching frames. The held-out G2 frames (heldout_g2.json) are never used here (guarded by test_course.py).
FRAMES = {
    'count': ['how many {np} are there', 'how many {np}', 'count the {np}', 'how many {np} do you see'],
    'show': ['show me the {np}', 'show the {np}', 'point to the {np}', 'which ones are {np}', 'find the {np}'],
    'yesno': ['is there {np1}', 'are there any {np}', 'do you see {np1}', 'is the {name} file {pred}', 'is {name} {pred}'],
    'kind': ['what kind of file is the {name} file', 'what kind is {name}'],
    'format': ['what format is the {name} file', 'what format is {name}'],
    'place': ['where is the {name} file', 'where is {name}', 'which folder is {name} in'],
    'size': ['what size is the {name} file', 'what size is {name}'],
}
REPORT = ('kind', 'format', 'place', 'size')
NP_CHANNELS = ('size', 'spread', 'kind', 'format', 'place', 'name')


class Teacher:
    def __init__(self, talker, seed):
        self.t, self.seed = talker, seed
        self.w = World(seed)
        self.rng = random.Random(9000 + seed)
        self.dict = {}            # word -> dict(color, channel, taught_rest, tests)
        self.rests = 0
        self.speech = dict(words=0, unqualified=0)
        self.log = []
        self.testable = self._testable()

    # ---------------- world helpers ----------------
    def with_word(self, pool, ch, w):
        return [it for it in pool if self.w.has(it, ch, w)]

    def _testable(self):
        out = {}
        for ch, words in CONTENT_WORDS.items():
            for w in words:
                if len(self.with_word(self.w.teach_pool, ch, w)) >= 2 and len(self.with_word(self.w.test_pool, ch, w)) >= 2:
                    out[w] = ch
        for w in NUMBERS:
            out[w] = 'number'
        for w in YESNO:
            out[w] = 'truth'
        return out

    @staticmethod
    def sc(item):
        return dict(card=item['card'])

    def green(self):
        return sorted(w for w, d in self.dict.items() if d['color'] == 'green')

    def enter(self, w):
        if w not in self.dict:
            self.dict[w] = dict(color='yellow', channel=self.testable.get(w), taught_rest=self.rests, tests=[])

    def rest(self):
        self.t.rest()
        self.rests += 1

    # ---------------- ע noticing ----------------
    def teach_numbers(self, reps=2):
        for _ in range(reps):
            ks = list(range(len(NUMBERS)))
            self.rng.shuffle(ks)
            for k in ks:
                group = self.rng.sample(self.w.teach_pool, k)
                phrase = [NUMBERS[k]] if self.rng.random() < 0.5 else [NUMBERS[k], 'files']
                self.t.hear(phrase, dict(group=group))
                self.enter(NUMBERS[k])

    def phrases(self, ch, w):
        if ch == 'place':
            return [[w], ['a', 'file', 'in', w], ['this', 'is', 'a', 'file', 'in', w]]
        if ch == 'name':
            return [[w], ['a', 'file', 'named', w], ['the', w, 'file']]
        return [[w], ['a', w, 'file'], ['this', 'is', 'a', w, 'file']]

    def varied(self, pool, k):
        """Examples that differ from each other on the other channels (variation shows what the word is not)."""
        out, seen = [], set()
        cands = list(pool)
        self.rng.shuffle(cands)
        for it in cands:
            key = (it['kind'], it['format'], it['place'])
            if key not in seen:
                out.append(it)
                seen.add(key)
            if len(out) == k:
                return out
        rest = [it for it in cands if it not in out]
        return out + rest[:k - len(out)]

    def teach_words(self, words, examples=3):
        for w in words:
            ch = self.testable[w]
            pool = self.with_word(self.w.teach_pool, ch, w)
            for it in self.varied(pool, examples):
                self.t.hear(self.rng.choice(self.phrases(ch, w)), self.sc(it))
            self.enter(w)

    def teach_truth(self, n=24):
        probes = [w for w in self.green() if self.testable.get(w) in ('kind', 'format', 'size')]
        if not probes:
            return 0
        for _ in range(n):
            p = self.rng.choice(probes)
            ch = self.testable[p]
            yes = self.rng.random() < 0.5
            pool = self.with_word(self.w.teach_pool, ch, p) if yes else \
                [it for it in self.w.teach_pool if not self.w.has(it, ch, p)]
            it = self.rng.choice(pool)
            word = YESNO[int(yes)]
            self.t.hear([word], dict(probe=p, against=it['card']))
            self.enter(word)
        return n

    # ---------------- פ naming and ר recognition (practice) ----------------
    def distractors(self, w, item=None, k=2):
        ch = self.testable[w]
        if self.binary(w):
            k = 1
        same = [v for v in self.dict if self.testable.get(v) == ch and v != w]
        if item is not None and ch not in ('number', 'truth'):
            same = [v for v in same if not self.w.has(item, ch, v)]
        if len(same) < k:
            return None
        return self.rng.sample(same, k)

    def scene_for(self, w, pool, positive=True):
        """Scenes for magnitude and truth words (a group of items, or a probe word held against an item)."""
        if self.testable[w] == 'number':
            return dict(group=self.rng.sample(pool, NUMBERS.index(w)))
        probes = [v for v in self.green() if self.testable.get(v) in ('kind', 'format', 'size')]
        if not probes:
            return None
        p = self.rng.choice(probes)
        yes = (w == 'yes') == positive
        cands = self.with_word(pool, self.testable[p], p) if yes else \
            [it for it in pool if not self.w.has(it, self.testable[p], p)]
        return dict(probe=p, against=self.rng.choice(cands)['card'])

    def item_scene(self, w, pool, positive=True):
        ch = self.testable[w]
        if ch in ('number', 'truth'):
            return self.scene_for(w, pool, positive), None
        cands = self.with_word(pool, ch, w) if positive else [it for it in pool if not self.w.has(it, ch, w)]
        it = self.rng.choice(cands)
        return self.sc(it), it

    def near_miss(self, w, item, pool):
        """An item without the word that shares the most other channel values with `item`."""
        ch = self.testable[w]
        lack = [it for it in pool if not self.w.has(it, ch, w)]
        chans = ('kind', 'format', 'size', 'place', 'spread')
        best = max(sum(it[c] == item[c] for c in chans if c != ch) for it in lack)
        return self.rng.choice([it for it in lack if sum(it[c] == item[c] for c in chans if c != ch) == best])

    def other_scenes(self, w, pool, k=2, item=None):
        ch = self.testable[w]
        if item is not None and not self.binary(w) and ch not in ('number', 'truth'):
            return [self.sc(self.near_miss(w, item, pool)), self.item_scene(w, pool, positive=False)[0]]
        if ch == 'number':
            n = NUMBERS.index(w)
            others = self.rng.sample([m for m in range(len(NUMBERS)) if m != n], k)
            return [dict(group=self.rng.sample(pool, m)) for m in others]
        if self.binary(w):
            k = 1
        if ch == 'truth':
            return [self.scene_for(w, pool, positive=False)]
        return [self.item_scene(w, pool, positive=False)[0] for _ in range(k)]

    def binary(self, w):
        ch = self.testable[w]
        return ch == 'truth' or ch in CONTENT_WORDS and len(CONTENT_WORDS[ch]) == 2

    def answer_question(self, q):
        w = q.get('asks_about')
        if w in self.testable and self.testable[w] not in ('number', 'truth'):
            ch = self.testable[w]
            pool = self.with_word(self.w.teach_pool, ch, w)
            self.t.told(w, [self.sc(it) for it in self.varied(pool, 2)])
            self.enter(w)
            return True
        return False

    def practice(self, words, rounds=1):
        self.t.questions(True)
        n = ok_n = 0
        for _ in range(rounds):
            for w in words:
                scene, item = self.item_scene(w, self.w.teach_pool)
                if scene is None:
                    continue
                opts = self.distractors(w, item)
                if opts is None:
                    continue
                opts = opts + [w]
                self.rng.shuffle(opts)
                r = self.t.name(scene, opts, practice=True)
                if 'question' in r:
                    self.answer_question(r['question'])
                    r = self.t.name(scene, opts, practice=True)
                    if 'question' in r:
                        continue
                ok = r['answer'] == w
                self.t.word_feedback(r, ok, None if ok else w)
                n, ok_n = n + 1, ok_n + ok
                # ר recognition
                scenes = [scene] + self.other_scenes(w, self.w.teach_pool)
                if None in scenes:
                    continue
                order = list(range(len(scenes)))
                self.rng.shuffle(order)
                shown = [scenes[i] for i in order]
                r = self.t.recognise(w, shown, practice=True)
                right = order.index(0)
                ok = r.get('answer') == right
                self.t.word_feedback(r, ok, None if ok else right)
        self.t.questions(False)
        return n, ok_n

    # ---------------- ת checking ----------------
    def test_word(self, w, trials=None):
        """3 trials of each kind, pass ≥2; words with a single alternative (binary) take 5 trials, pass ≥4."""
        trials = trials or (5 if self.binary(w) else 3)
        rec = use = 0
        pool = self.w.test_pool
        for _ in range(trials):
            scene, item = self.item_scene(w, pool)
            others = self.other_scenes(w, pool, item=item)
            if scene is None or None in others:
                return None
            scenes = [scene] + others
            order = list(range(len(scenes)))
            self.rng.shuffle(order)
            r = self.t.recognise(w, [scenes[i] for i in order])
            rec += r.get('answer') == order.index(0)
            scene, item = self.item_scene(w, pool)
            opts = self.distractors(w, item)
            if opts is None:
                return None
            opts = opts + [w]
            self.rng.shuffle(opts)
            r = self.t.name(scene, opts)
            use += r.get('answer') == w
        return rec, use

    def green_tests(self, words=None):
        changed = []
        for w in sorted(words if words is not None else self.dict):
            d = self.dict[w]
            if d['taught_rest'] >= self.rests or d['color'] == 'green' and words is None:
                continue
            res = self.test_word(w)
            if res is None:
                continue
            rec, use = res
            d['tests'].append([self.rests, rec, use])
            need = 4 if self.binary(w) else 2
            new = 'green' if rec >= need and use >= need else 'yellow'
            if new != d['color']:
                changed.append((w, new))
            d['color'] = new
        self.t.qualify(self.green())
        return changed

    # ---------------- dialogue ----------------
    def known(self, ch):
        return [w for w in CONTENT_WORDS.get(ch, []) if w in self.dict]

    def np_words(self, cons, form):
        """cons: list of (channel, word). form: 'plural' | 'one' (with 'a') | 'bare'."""
        d = dict(cons)
        head = []
        for ch in ('size', 'spread'):
            if ch in d:
                head.append(d[ch])
        for ch in ('kind', 'format'):
            if ch in d:
                head.append(d[ch])
        head.append('files' if form == 'plural' else 'file')
        if 'place' in d:
            head += ['in', d['place']]
        if 'name' in d:
            head += ['named', d['name']]
        return (['a'] if form == 'one' else []) + head

    def pick_cons(self, desk, n_cons, vocab, slip):
        """Constraints describing an item of the desk, from known words (a new word may be slipped in)."""
        anchor = self.rng.choice(desk)
        opts = []
        for ch in NP_CHANNELS:
            vals = anchor['parts'] if ch == 'name' else [anchor[ch]]
            for v in vals:
                if v in self.testable and (v in vocab or (slip and v in self.testable)):
                    opts.append((ch, v))
        self.rng.shuffle(opts)
        out, used = [], set()
        for ch, v in opts:
            if ch in used or (ch in ('kind', 'format') and used & {'kind', 'format'}):
                continue
            if v not in vocab and any(x not in vocab for _, x in out):
                continue
            out.append((ch, v))
            used.add(ch)
            if len(out) == n_cons:
                break
        return out

    def matches(self, desk, cons):
        return [i for i, it in enumerate(desk) if all(self.w.has(it, ch, v) for ch, v in cons)]

    def make_question(self, task, pool, frames=None, n_cons=None, slip=0.0):
        frames = frames or FRAMES
        vocab = set(self.dict)
        for _ in range(60):
            desk = self.w.desk(pool, self.rng.randint(6, 10), self.rng)
            frame = self.rng.choice(frames[task]) if isinstance(frames[task], list) else frames[task]
            k = n_cons or self.rng.choice([1, 1, 2])
            s = self.rng.random() < slip
            if '{name}' in frame:
                q = self._named_question(task, frame, desk, vocab, s)
            else:
                q = self._np_question(task, frame, desk, vocab, k, s)
            if q:
                return q
        return None

    def _np_question(self, task, frame, desk, vocab, k, slip):
        cons = self.pick_cons(desk, k, vocab, slip)
        if len(cons) < k:
            return None
        if task in ('count', 'yesno') and self.rng.random() < 0.3:
            # a description that fits nothing on the desk
            ch, v = cons[-1]
            alts = [x for x in self.known(ch) if x != v and not self.matches(desk, cons[:-1] + [(ch, x)])]
            if alts:
                cons = cons[:-1] + [(ch, self.rng.choice(alts))]
        hits = self.matches(desk, cons)
        text = frame.format(np=' '.join(self.np_words(cons, 'plural')), np1=' '.join(self.np_words(cons, 'one')),
                            np0=' '.join(self.np_words(cons, 'bare')))
        if task == 'count':
            ans = dict(say=[NUMBERS[len(hits)]], gesture=hits)
        elif task == 'show':
            if not hits:
                return None
            ans = dict(say=None, gesture=hits)
        else:
            ans = dict(say=[YESNO[bool(hits)]], gesture=hits)
        return dict(text=text, desk=desk, task=task, cons=cons, answer=ans)

    def _named_question(self, task, frame, desk, vocab, slip):
        counts = {}
        for it in desk:
            for t in it['parts']:
                counts[t] = counts.get(t, 0) + 1
        names = [t for t, c in counts.items() if c == 1 and t in self.testable and (t in vocab or slip)]
        if not names:
            return None
        name = self.rng.choice(sorted(names))
        ref = [i for i, it in enumerate(desk) if name in it['parts']][0]
        item = desk[ref]
        slots = dict(name=name)
        if task == 'yesno':
            ch = self.rng.choice([c for c in ('kind', 'format', 'size', 'place') if '{%s}' % c in frame or '{pred}' in frame]
                                 or ['size'])
            if ch == 'place' and item['place'] == 'elsewhere':
                ch = 'size'
            if '{kind}' in frame:
                ch = 'kind'
            elif '{format}' in frame:
                ch = 'format'
            elif '{place}' in frame:
                ch = 'place'
            elif '{size}' in frame:
                ch = 'size'
            truth = self.rng.random() < 0.5
            v = item[ch]
            if not truth:
                alts = [x for x in self.known(ch) if x != v]
                if not alts:
                    return None
                v = self.rng.choice(alts)
            if v not in vocab:
                return None
            pred = {'kind': f'a {v} file', 'format': f'a {v} file', 'size': v, 'place': f'in {v}'}[ch]
            slots.update(pred=pred, kind=v, format=v, size=v, place=v)
            hits = [i for i, it in enumerate(desk) if name in it['parts'] and it[ch] == v]
            ans = dict(say=[YESNO[bool(hits)]], gesture=hits)
        elif task == 'show':
            ans = dict(say=None, gesture=[ref])
        else:
            v = item[task]
            if v == 'elsewhere' or v not in vocab:
                return None
            ans = dict(say=[v], gesture=[ref])
        return dict(text=frame.format(**slots, np='', np1='', np0=''), desk=desk, task=task, cons=[('name', name)],
                    answer=ans)

    def grade(self, q, r):
        a = q['answer']
        if 'ask' in r or 'ask_question' in r:
            return None
        if a['say'] is None:
            return 'gesture' in r and sorted(r['gesture']) == sorted(a['gesture'])
        return r.get('say') == a['say']

    def speak_check(self, r):
        if 'say' in r:
            self.speech['words'] += len(r['say'])
            self.speech['unqualified'] += sum(1 for w in r['say'] if w not in set(self.green()))

    def converse(self, q, learn=True):
        cards = [it['card'] for it in q['desk']]
        r = self.t.reply(q['text'], cards)
        self.speak_check(r)
        asked = r.get('ask') or r.get('ask_question')
        for _ in range(2):
            if 'ask' not in r and 'ask_question' not in r:
                break
            if not learn:
                return dict(q=q['text'], task=q['task'], reply=r, ok=None, asked=asked)
            if 'ask' in r:
                if not self.answer_question(dict(asks_about=r['ask'])):
                    self.t.told_form(r['ask'])
            else:
                self.t.shown(q['answer'])
            r = self.t.reply(q['text'], cards)
            self.speak_check(r)
        if 'ask' in r or 'ask_question' in r:
            return dict(q=q['text'], task=q['task'], reply=r, ok=None, asked=asked)
        ok = self.grade(q, r)
        if learn:
            self.t.feedback(ok, None if ok else q['answer'])
        return dict(q=q['text'], task=q['task'], reply=r, ok=ok, asked=asked)

    def dialogue(self, n, tasks, slip=0.1):
        out = []
        for _ in range(n):
            task = self.rng.choice(tasks)
            q = self.make_question(task, self.w.teach_pool, slip=slip)
            if q is None:
                continue
            out.append(self.converse(q))
        return out
