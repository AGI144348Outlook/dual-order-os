"""Echo neuroplasticity learning layer (pilot).

What this module knows: how to perceive opaque feature codes, compare cards,
count co-occurrences, keep links, rest, review and form pattern tokens.
What it does NOT contain: any classroom vocabulary, meanings, word order
rules or inflection rules. A test (test_pilot.py) scans this file to enforce
that. Everything about specific words is acquired from lessons and feedback.

Innate perceptual priors (disclosed): cards arrive as (channel, value) codes;
the learner can test whether two cards match overall or on one channel, and
whether a word's learned grounding fits a card. These are perception tools,
not word meanings.

Mechanism flags map to the Neuroplasticity candidate library:
  b1   'a' counts only (B1-a) | 'b' outcome-weighted (B1-b)
  f1   tag while awake, capture at rest within a budget (F1-a)
  a6   multiplicative downscaling at rest, protected by use (A6-b with B3-a)
  e1   dormant instead of deleted when weak / over capacity (E1-a vs E2-a)
  g3   Leitner spaced review during rest (G3-a)
  d1   'greedy' | 'eps' (D1-a) | 'thompson' (D1-c) during practice
  f2   validated pattern tokens for order and form changes (F2-c)
  q    gap-driven questions through the tsadi tool
  me   mutual exclusivity: a feature already reliably named by another word
       is skipped when grounding a newer word (NEW candidate, not in the library)
  learn False gives the zero-learning control
"""
import math
import random
from copy import deepcopy

DEFAULTS = dict(b1='b', f1=True, a6=True, e1=True, g3=True, d1='thompson',
                f2=True, q=True, me=True, learn=True)

CAPTURE_BUDGET = 260      # links consolidated per rest (A1 budget)
DOWNSCALE = 0.9           # A6-b factor s
LINK_FLOOR = 0.35         # below this a link goes dormant or is deleted
WORD_FLOOR = 0.6          # below this a word's evidence goes dormant
EPISODE_SLOTS = 40        # A3-a active episodic slots
REVIEW_BUDGET = 6         # G3 reviews per rest
QUESTION_BUDGET = 4       # tsadi questions per assignment
TOKEN_SUPPORT = 3         # F2-c minimum support
TOKEN_CONSISTENCY = 0.85  # F2-c minimum consistency


class Echo:
    def __init__(self, seed=0, identity=None, **flags):
        self.cfg = dict(DEFAULTS, **flags)
        self.rng = random.Random(seed)
        self.identity = identity            # Genesis A-000 anchor record, if supplied
        # word -> feat -> [count, trace, wins, losses, dormant]
        self.links = {}
        # word -> dict(n, trace_n, nwin, nloss, protect, dormant, box, forms)
        self.words = {}
        self.nfeat, self.N = {}, 0.0        # background perceptual statistics
        self.objco, self.objn = {}, {}      # within-card feature co-occurrence
        self.routes = {}                    # word -> relation operator -> [wins, losses]
        self.phrases = []                   # heard word sequences with card context
        self.order_tokens, self.form_tokens, self.form_same = {}, [], set()
        self.shape_tokens = {}
        self.episodes = []                  # ק event cards: dict(label, words, feats, dormant)
        self.tombstones = 0
        self.rests = 0
        self.frozen = False
        self.questions_left = QUESTION_BUDGET
        self.questions_on = False
        self.marks = {}                     # word -> 'met' (ע stamp) | 'claimed' (pending)
        self.log = []
        self._version, self._gcache = 0, {}

    # ---------------- perception (innate) ----------------
    @staticmethod
    def feats(card):
        return frozenset(tuple(f) for f in card['feats'])

    def view(self, cards, query_words=()):
        """Percept for a task: card features plus comparator results."""
        fs = set()
        cs = [self.feats(c) for c in cards]
        for c in cs:
            fs |= c
        if len(cs) == 2:
            a, b = cs
            fs.add(('cmp', 'all', a == b))
            chans = {f[0] for f in a | b}
            for ch in chans:
                va = {f for f in a if f[0] == ch}
                vb = {f for f in b if f[0] == ch}
                fs.add(('cmp', ch, va == vb))
        if len(cs) == 1:
            for u in query_words:
                if self._known(u):
                    fs.add(('fit', self.fit(u, cs[0]) > 0))
        return frozenset(fs)

    # ---------------- evidence ----------------
    def _known(self, w):
        s = self.words.get(w)
        return s is not None and not s['dormant'] and (s['n'] + s['trace_n']) > 0

    def _word(self, w):
        if w not in self.words:
            self.words[w] = dict(n=0.0, trace_n=0.0, nwin=0.0, nloss=0.0,
                                 protect=0.0, dormant=False, box=1)
            self.links[w] = {}
        return self.words[w]

    def _bump(self, w, fs, field, amount=1.0):
        """field: 0 count, 2 wins, 3 losses. Traces (index 1) if F1 is on."""
        self._version += 1
        s = self._word(w)
        lk = self.links[w]
        use_trace = self.cfg['f1'] and field == 0
        for f in fs:
            row = lk.setdefault(f, [0.0, 0.0, 0.0, 0.0, False])
            row[4] = False                  # re-encounter restores a dormant link
            row[1 if use_trace else field] += amount
        if field == 0:
            if use_trace:
                s['trace_n'] += amount
            else:
                s['n'] += amount
        elif field == 2:
            s['nwin'] += amount
        else:
            s['nloss'] += amount
        s['dormant'] = False

    def _background(self, fs):
        self._version += 1
        self.N += 1
        for f in fs:
            self.nfeat[f] = self.nfeat.get(f, 0.0) + 1

    def _objstats(self, cards):
        for c in cards:
            cs = sorted(self.feats(c))
            for f in cs:
                self.objn[f] = self.objn.get(f, 0.0) + 1
                for g in cs:
                    if g != f:
                        self.objco[(f, g)] = self.objco.get((f, g), 0.0) + 1

    def p_word(self, w, f, sample=False):
        s, row = self.words[w], self.links[w].get(f)
        if row is None or row[4]:
            c = 0.0
        else:
            c = row[0] + row[1]
            if self.cfg['b1'] == 'b':
                c += row[2]
        n = s['n'] + s['trace_n'] + (s['nwin'] if self.cfg['b1'] == 'b' else 0)
        if sample:
            return self.rng.betavariate(c + 1, max(n - c, 0) + 1)
        return (c + 1) / (n + 2)

    def p_bg(self, f):
        return (self.nfeat.get(f, 0.0) + 1) / (self.N + 2)

    def score(self, w, percept, sample=False):
        """Naive-Bayes log-likelihood ratio that word w fits percept."""
        if not self._known(w):
            return None
        total = 0.0
        active = {f for f, r in self.links[w].items() if not r[4]}
        for f in percept:
            if self.nfeat.get(f, 0) < 1 and f not in active:
                continue                    # never-perceived feature: ignore
            p = self.p_word(w, f, sample)
            total += math.log(p / self.p_bg(f))
            if self.cfg['b1'] == 'b':
                row = self.links[w].get(f)
                s = self.words[w]
                if row is not None and not row[4] and s['nloss'] > 0:
                    pl = (row[3] + 1) / (s['nloss'] + 2)
                    total -= 0.5 * max(0.0, math.log(pl / self.p_bg(f)))
        for f in active - percept:
            if f[0] == 'cmp' or f[0] == 'fit':
                continue
            if not any(g[0] == f[0] for g in percept):
                continue                    # channel absent from view: uninformative
            p = self.p_word(w, f, sample)
            total += math.log(max(1e-6, 1 - p) / max(1e-6, 1 - self.p_bg(f)))
        return total

    def fit(self, w, fs):
        """Innate fit test: is word w's grounding among these card features?"""
        g = self.grounding(w)
        if g is None:
            return -1.0
        return 1.0 if g in fs else -1.0

    def _raw_grounding(self, w):
        best, bestv = None, 0.0
        for f, row in self.links[w].items():
            if row[4] or f[0] in ('cmp', 'fit'):
                continue
            v = self.p_word(w, f) - self.p_bg(f)      # contrast (delta-P)
            if v > bestv:
                best, bestv = f, v
        return best

    def grounding(self, w):
        """Most diagnostic perceptual feature of a word (card features only)."""
        if not self._known(w):
            return None
        key = (w, self._version)
        if key in self._gcache:
            return self._gcache[key]
        if not self.cfg['me']:
            g = self._raw_grounding(w)
        else:
            owned = set()
            nw = self.words[w]['n'] + self.words[w]['trace_n']
            for v in self.words:
                if v == w or not self._known(v):
                    continue
                gv = self._raw_grounding(v)
                if gv is None:
                    continue
                nv = self.words[v]['n'] + self.words[v]['trace_n']
                if self.p_word(v, gv) >= 0.6 and self.p_word(v, gv) > self.p_word(w, gv) - 1e-9 and nv >= nw:
                    owned.add(gv)
            best, bestv = None, 0.0
            for f, row in self.links[w].items():
                if row[4] or f[0] in ('cmp', 'fit') or f in owned:
                    continue
                val = self.p_word(w, f) - self.p_bg(f)
                if val > bestv:
                    best, bestv = f, val
            g = best if best is not None else self._raw_grounding(w)
        if len(self._gcache) > 5000:
            self._gcache.clear()
        self._gcache[key] = g
        return g

    # ---------------- relation operators (innate) on groundings ----------------
    def _ops(self, x, y):
        gx, gy = self.grounding(x), self.grounding(y)
        if gx is None or gy is None:
            return None
        co = self.objco.get((gx, gy), 0.0) / max(1.0, self.objn.get(gx, 0.0))
        return {
            'chan_eq_val_ne': float(gx[0] == gy[0] and gx != gy),
            'val_eq': float(gx == gy),
            'chan_ne': float(gx[0] != gy[0]),
            'obj_co': co,
        }

    def _route_weight(self, u, op):
        w, l = self.routes.get(u, {}).get(op, (0.0, 0.0))
        return max(0.0, (w + 1) / (w + l + 2) - 0.5)

    def relate_scores(self, query, options):
        out = {}
        for y in options:
            total = 0.0
            for u in query:
                for x in query:
                    if x == u:
                        continue
                    ops = self._ops(x, y)
                    if ops is None:
                        continue
                    for op, v in ops.items():
                        total += self._route_weight(u, op) * v
            out[y] = total
        return out

    # ---------------- hearing (passive lesson exposure) ----------------
    def hear(self, words, cards, label=None):
        if self.frozen or not self.cfg['learn']:
            return
        percept = self.view(cards, words)
        self._background(percept)
        self._objstats(cards)
        for w in words:
            self._bump(w, percept, 0)
            if self.marks.get(w) is None:
                self.marks[w] = 'met'       # ע stamp: encountered
        if len(words) > 1:
            self.phrases.append((tuple(words), percept))
            self.phrases = self.phrases[-400:]
        self._episode(label, words, percept)

    def _episode(self, label, words, percept):
        self.episodes.append(dict(label=label, words=tuple(words), feats=percept, dormant=False))
        active = [e for e in self.episodes if not e['dormant']]
        while len(active) > EPISODE_SLOTS:
            old = active.pop(0)
            if self.cfg['e1']:
                old['dormant'] = True       # E1-a: kept, costs zero working slots
            else:
                self.episodes.remove(old)   # E2-a: discarded with a tombstone
                self.tombstones += 1

    # ---------------- answering ----------------
    def _pick(self, scored, practice):
        items = [(v, k) for k, v in scored.items() if v is not None]
        if not items:
            keys = list(scored)
            return self.rng.choice(keys) if keys else None
        if practice and self.cfg['d1'] == 'eps' and self.rng.random() < 0.15:
            return self.rng.choice(list(scored))
        best = max(v for v, _ in items)
        top = [k for v, k in items if v == best]
        return self.rng.choice(top)

    def attempt(self, item, practice=False):
        """Return a response. The item never contains the answer."""
        if not self.cfg['learn']:
            return self._random(item)
        sample = practice and self.cfg['d1'] == 'thompson'
        t = item['type']
        if t == 'pick_word':
            percept = self.view(item['cards'], item.get('query_words', ()))
            scored = {w: self.score(w, percept, sample) for w in item['options']}
            q = self._maybe_ask(scored, practice)
            if q:
                return q
            return {'answer': self._pick(scored, practice)}
        if t == 'pick_card':
            scored = {}
            for i, c in enumerate(item['options']):
                percept = self.view([c])
                parts = [self.score(w, percept, sample) for w in item['query_words']]
                scored[i] = None if any(p is None for p in parts) else sum(parts)
            return {'answer': self._pick(scored, practice)}
        if t == 'relate':
            scored = self.relate_scores(item['query_words'], item['options'])
            if item.get('multi'):
                best = max(scored.values()) if scored else 0
                pick = sorted(y for y, v in scored.items() if best > 0 and v >= 0.5 * best)
                return {'answer': pick}
            return {'answer': self._pick(scored, practice)}
        if t == 'match':
            return {'answer': self._match(item)}
        if t == 'describe':
            return {'answer': self._describe(item['cards'][0], item['n'], item.get('example'))}
        if t == 'recall':
            return {'answer': self._recall(item['query_words'][0], item['options'])}
        raise ValueError('unknown task type')

    def _random(self, item):
        t = item['type']
        if t in ('pick_word', 'relate', 'recall'):
            opts = item['options']
            if t == 'relate' and item.get('multi'):
                return {'answer': sorted(self.rng.sample(opts, self.rng.randint(1, len(opts))))}
            return {'answer': self.rng.choice(opts)}
        if t == 'pick_card':
            return {'answer': self.rng.randrange(len(item['options']))}
        if t == 'match':
            idx = list(range(len(item['cards'])))
            self.rng.shuffle(idx)
            return {'answer': dict(zip(item['words'], idx))}
        if t == 'describe':
            pool = sorted(self.words) or ['?']
            return {'answer': [self.rng.choice(pool) for _ in range(item['n'])]}
        raise ValueError('unknown task type')

    def _maybe_ask(self, scored, practice):
        """Gap-driven tsadi question: ask about the weakest option worth knowing."""
        if not (practice and self.cfg['q'] and self.questions_on and self.questions_left > 0):
            return None
        vals = sorted((v for v in scored.values() if v is not None), reverse=True)
        unknown = [w for w, v in scored.items() if v is None]
        if unknown:
            target = sorted(unknown)[0]
        elif len(vals) >= 2 and vals[0] - vals[1] < 1.0:
            target = max(scored, key=lambda w: scored[w])
        else:
            return None
        self.questions_left -= 1
        self.log.append(('ask', target))
        return {'question': {'tool': 'צ', 'asks_about': target}}

    def _match(self, item):
        pairs = []
        for w in item['words']:
            for i, c in enumerate(item['cards']):
                s = self.score(w, self.view([c]))
                pairs.append((s if s is not None else -1e9, w, i))
        pairs.sort(reverse=True)
        used_w, used_c, out = set(), set(), {}
        for s, w, i in pairs:
            if w in used_w or i in used_c:
                continue
            out[w] = i
            used_w.add(w)
            used_c.add(i)
        return out

    def _channel_of(self, w):
        base = self._base_of(w)
        g = self.grounding(base if base else w)
        return None if g is None else g[0]

    def _base_of(self, w):
        """If w is a derived form under a learned form token, its base word."""
        if not self.cfg['f2']:
            return None
        for tok in self.form_tokens:
            sfx = tok['suffix']
            if w.endswith(sfx) and w[:-len(sfx)] in self.words:
                return w[:-len(sfx)]
        return None

    def _reliable(self, w):
        """A word that reliably signals one card feature (learned statistic)."""
        g = self.grounding(w)
        return g is not None and self.p_word(w, g) >= 0.6 and self.p_word(w, g) - self.p_bg(g) >= 0.3

    def _describe(self, card, n, example=None):
        percept = self.view([card])
        derived = self._derived_forms()
        best_by_chan = {}
        for w in self.words:
            if not self._known(w) or (self.cfg['f2'] and w in derived) or not self._reliable(w):
                continue                    # with form tokens, build forms instead of recalling them
            ch = self._channel_of(w)
            s = self.score(w, percept)
            if s is None:
                continue
            g = self.grounding(w)
            visible = g in percept               # learned meaning is on the card
            key = (visible, (self.p_word(w, g) - self.p_bg(g)) if visible else s)
            if ch not in best_by_chan or key > best_by_chan[ch][0]:
                best_by_chan[ch] = (key, w)
        shape = None
        if example:                         # copy the shape of a worked example
            ex = [self._channel_of(w) for w in example['words']]
            if None not in ex and len(ex) == n:
                shape = ex
        if shape is None and self.cfg['f2']:
            shape = self._shape_for(n, percept)
        if shape is not None and all(ch in best_by_chan for ch in shape):
            words = [best_by_chan[ch][1] for ch in shape]
        else:
            ranked = sorted(best_by_chan.items(), key=lambda kv: kv[1][0], reverse=True)[:n]
            words = self._order([w for _, (_, w) in ranked])
        return self._inflect(words, percept)

    def _shape_for(self, n, percept):
        """F2 phrase-shape token: which channel sequence fits a phrase of length n here."""
        best, bestv = None, None
        for seq, tok in self.shape_tokens.get(n, {}).items():
            v = math.log(tok['count'])
            for f in percept:
                if f[0] in ('cmp', 'fit'):
                    continue
                v += math.log((tok['feat'].get(f, 0) + 0.5) / (tok['count'] + 1))
            if bestv is None or v > bestv:
                best, bestv = seq, v
        return best

    def _derived_forms(self):
        out = set()
        for tok in self.form_tokens:
            for w in self.words:
                if w.endswith(tok['suffix']) and w[:-len(tok['suffix'])] in self.words:
                    out.add(w)
        return out

    # ---------------- F2: order and form tokens ----------------
    def _order(self, words):
        if self.cfg['f2'] and self.order_tokens:
            def before(a, b):
                ca, cb = self._channel_of(a), self._channel_of(b)
                return self.order_tokens.get((ca, cb), 0) - self.order_tokens.get((cb, ca), 0)
            out = []
            for w in words:
                i = 0
                while i < len(out) and before(out[i], w) > 0:
                    i += 1
                out.insert(i, w)
            return out
        # fallback: per-word mean position from heard phrases
        pos = {}
        for seq, _ in self.phrases:
            for i, w in enumerate(seq):
                a = pos.setdefault(w, [0.0, 0])
                a[0] += i / max(1, len(seq) - 1)
                a[1] += 1
        key = lambda w: (pos[w][0] / pos[w][1]) if w in pos else self.rng.random()
        return sorted(words, key=key)

    def _inflect(self, words, percept):
        if not (self.cfg['f2'] and self.form_tokens):
            return words
        out = []
        for w in words:
            new = w
            for tok in self.form_tokens:
                if self._channel_of(w) == tok['chan'] and tok['trigger'] & percept:
                    if w in self.form_same:
                        new = w
                    else:
                        new = w + tok['suffix']
                    break
            out.append(new)
        return out

    def _form_tokens(self):
        """F2-c form tokens: a suffix whose added meaning shifts the SAME channel
        in every supporting pair (validated across pairs, so one-off noise drops out)."""
        heard = [w for w in self.words if self._known(w)]
        candidates = {}
        for b in heard:
            gb = self.grounding(b)
            if gb is None:
                continue
            for v in heard:
                if v == b or not v.startswith(b) or not 1 <= len(v) - len(b) <= 3:
                    continue
                if self.p_word(v, gb) < 0.6:
                    continue                    # derived form must still show the base's referent
                shift = set()
                for f in set(self.links[v]) | set(self.links[b]):
                    if f[0] in ('cmp', 'fit'):
                        continue
                    if self.p_word(v, f) - self.p_word(b, f) > 0.25:
                        shift.add(f)
                if shift:
                    candidates.setdefault((v[len(b):], gb[0]), []).append(shift)
        tokens = []
        for (suffix, chan), shifts in candidates.items():
            if len(shifts) < 2:
                continue
            chans = set.intersection(*({f[0] for f in sh} for sh in shifts))
            trigger = frozenset(f for sh in shifts for f in sh if f[0] in chans)
            if trigger:
                tokens.append(dict(suffix=suffix, chan=chan, trigger=trigger, support=len(shifts)))
        self.form_tokens = tokens
        # unchanged forms: phrases where a base word itself named the referent
        # while a trigger feature was present (heard evidence, e.g. a count shown)
        self.form_same = set()
        for tok in tokens:
            for seq, percept in self.phrases:
                if not (tok['trigger'] & percept):
                    continue
                for w in seq:
                    if w in self.words and self._base_of(w) is None and \
                            self._channel_of(w) == tok['chan'] and (w + tok['suffix']) not in self.words:
                        self.form_same.add(w)

    def _shape_tokens(self):
        shapes = {}
        for seq, percept in self.phrases:
            chans = tuple(self._channel_of(w) for w in seq)
            if None in chans or len(set(chans)) != len(chans):
                continue
            tok = shapes.setdefault(len(seq), {}).setdefault(chans, {'count': 0, 'feat': {}})
            tok['count'] += 1
            for f in percept:
                tok['feat'][f] = tok['feat'].get(f, 0) + 1
        self.shape_tokens = {n: {c: t for c, t in d.items() if t['count'] >= TOKEN_SUPPORT}
                             for n, d in shapes.items()}

    def _order_tokens(self):
        counts = {}
        for seq, _ in self.phrases:
            chans = [self._channel_of(w) for w in seq]
            for i in range(len(seq)):
                for j in range(i + 1, len(seq)):
                    if chans[i] and chans[j] and chans[i] != chans[j]:
                        counts[(chans[i], chans[j])] = counts.get((chans[i], chans[j]), 0) + 1
        tokens = {}
        for (a, b), c in counts.items():
            r = counts.get((b, a), 0)
            if c >= TOKEN_SUPPORT and c / (c + r) >= TOKEN_CONSISTENCY:
                tokens[(a, b)] = c
        self.order_tokens = tokens

    # ---------------- ק recall ----------------
    def _recall(self, w, options):
        hits = {}
        for e in self.episodes:
            if w in e['words'] and e['label'] in options:
                hits[e['label']] = hits.get(e['label'], 0) + 1
        if not hits:
            return self.rng.choice(options)
        return max(sorted(hits), key=lambda k: hits[k])

    # ---------------- feedback ----------------
    def feedback(self, item, response, ok, reveal=None):
        """ok: teacher's ✓/X. reveal: correct answer when the teacher shows it."""
        if self.frozen or not self.cfg['learn']:
            return
        t = item['type']
        ans = response.get('answer')
        if t == 'pick_word':
            percept = self.view(item['cards'], item.get('query_words', ()))
            if reveal is not None:
                self._background(percept)
                self._bump(reveal, percept, 0)
                if ans is not None and ans != reveal:
                    self._bump(ans, percept, 3)
            elif self.cfg['b1'] == 'b' and ans is not None:
                self._bump(ans, percept, 2 if ok else 3)
            self._use(ans, ok)
        elif t == 'pick_card':
            if reveal is not None:
                c = item['options'][reveal]
                percept = self.view([c])
                self._background(percept)
                for w in item['query_words']:
                    self._bump(w, percept, 0)
                if ans is not None and ans != reveal:
                    wrong = self.view([item['options'][ans]])
                    for w in item['query_words']:
                        self._bump(w, wrong, 3)
            elif self.cfg['b1'] == 'b' and ans is not None:
                percept = self.view([item['options'][ans]])
                for w in item['query_words']:
                    self._bump(w, percept, 2 if ok else 3)
            for w in item['query_words']:
                self._use(w, ok)
        elif t == 'relate':
            self._route_feedback(item, ans, ok, reveal)
        elif t == 'match' and reveal is not None:
            for w, i in reveal.items():
                percept = self.view([item['cards'][i]])
                self._background(percept)
                self._bump(w, percept, 0)
                self._use(w, ans.get(w) == i)
        elif t == 'describe' and reveal is not None:
            self.hear(list(reveal), item['cards'], label=item.get('label'))
        elif t == 'recall' and reveal is not None:
            pass                                # episodic memory is not rewritten

    def _route_feedback(self, item, ans, ok, reveal):
        q, opts = item['query_words'], item['options']
        for u in q:
            table = self.routes.setdefault(u, {})
            for x in q:
                if x == u:
                    continue
                vals = {y: self._ops(x, y) for y in opts}
                if any(v is None for v in vals.values()):
                    continue
                for op in next(iter(vals.values())):
                    col = {y: vals[y][op] for y in opts}
                    if reveal is not None:
                        want = set(reveal) if item.get('multi') else {reveal}
                        best = max(col.values())
                        top = {y for y, v in col.items() if best > 0 and v >= 0.5 * best} if item.get('multi') \
                            else {y for y, v in col.items() if v == best and best > 0}
                        good = top == want
                    elif self.cfg['b1'] == 'b' and ans is not None and not item.get('multi'):
                        fired = col[ans] > 0 and col[ans] == max(col.values())
                        if not fired:
                            continue
                        good = ok
                    else:
                        continue
                    row = table.setdefault(op, [0.0, 0.0])
                    row[0 if good else 1] += 1

    def _use(self, w, ok):
        if w in self.words and ok:
            s = self.words[w]
            s['protect'] = min(0.9, s['protect'] + 0.05)   # B3-a: use raises protection

    def answer_from_teacher(self, word, cards):
        """The teacher's reply to a tsadi question: an example of the word."""
        self.hear([word], cards, label='question')

    # ---------------- rest / recess ----------------
    def rest(self):
        if not self.cfg['learn']:
            return
        self.rests += 1
        self._version += 1
        self._capture()
        if self.cfg['a6']:
            self._downscale()
        self._dormancy()
        if self.cfg['g3']:
            self._review()
            self._version += 1
        if self.cfg['f2']:
            self._order_tokens()
            self._shape_tokens()
            self._form_tokens()
        self.questions_left = QUESTION_BUDGET

    def _capture(self):
        """F1-a: tagged traces compete for a consolidation budget; the rest fade."""
        if not self.cfg['f1']:
            return
        tagged = []
        for w, lk in self.links.items():
            tn = max(1.0, self.words[w]['trace_n'])
            for f, row in lk.items():
                if row[1] > 0:
                    tagged.append((row[1] / tn + row[2], w, f))
        tagged.sort(key=lambda t: -t[0])
        keep = {(w, f) for _, w, f in tagged[:CAPTURE_BUDGET]}
        for _, w, f in tagged:
            row = self.links[w][f]
            if (w, f) in keep:
                row[0] += row[1]
            row[1] = 0.0
        for s in self.words.values():
            s['n'] += s['trace_n']
            s['trace_n'] = 0.0

    def _downscale(self):
        for w, s in self.words.items():
            k = DOWNSCALE + (1 - DOWNSCALE) * s['protect']
            s['n'] *= k
            s['nwin'] *= k
            s['nloss'] *= k
            for row in self.links[w].values():
                row[0] *= k
                row[2] *= k
                row[3] *= k
        self.N *= DOWNSCALE
        for f in self.nfeat:
            self.nfeat[f] *= DOWNSCALE

    def _dormancy(self):
        for w, s in self.words.items():
            for f in list(self.links[w]):
                row = self.links[w][f]
                if not row[4] and row[0] + row[2] < LINK_FLOOR and row[1] == 0:
                    if self.cfg['e1']:
                        row[4] = True
                    else:
                        del self.links[w][f]
                        self.tombstones += 1
            if s['n'] < WORD_FLOOR and s['trace_n'] == 0:
                s['dormant'] = True

    def _review(self):
        """G3-a Leitner: box b is reviewed every 2**(b-1) rests, within a budget."""
        due = [w for w, s in self.words.items()
               if self.rests % (2 ** (s['box'] - 1)) == 0]
        due.sort(key=lambda w: (self.words[w]['box'], w))
        for w in due[:REVIEW_BUDGET]:
            eps = [e for e in self.episodes if w in e['words']]
            if not eps:
                continue
            e = eps[-1]
            e['dormant'] = False                     # rehydrate if dormant
            s = self.words[w]
            # self-check before rehearsal: does w still win its own episode?
            rivals = [v for v in e['words'] if v != w and self._known(v)]
            mine = self.score(w, e['feats']) if self._known(w) else None
            passed = mine is not None and mine > 0 and all(
                (self.score(v, e['feats']) or -1e9) <= mine for v in rivals if self._channel_of(v) == self._channel_of(w))
            s['box'] = min(5, s['box'] + 1) if passed else 1
            # rehearsal: replay the stored episode (no new outside information)
            for f in e['feats']:
                row = self.links[w].setdefault(f, [0.0, 0.0, 0.0, 0.0, False])
                row[4] = False
                row[0] += 0.5
            s['n'] += 0.5
            s['dormant'] = False
            s['protect'] = min(0.9, s['protect'] + 0.15)

    def recess(self, dictionary, qualified):
        """Last-priority Recess: browse entries; claim ones whose definitions
        consist only of teacher-qualified words. Claims are pending until handover."""
        if not self.cfg['learn']:
            return []
        claims = []
        budget = 3
        for head in sorted(dictionary):
            if budget == 0:
                break
            if head in qualified or self.marks.get(head) == 'claimed':
                continue
            body = dictionary[head]
            if body and all(t in qualified for t in body):
                self.marks[head] = 'claimed'
                claims.append(head)
                budget -= 1
        return claims

    # ---------------- bookkeeping ----------------
    def memory_size(self):
        links = sum(1 for lk in self.links.values() for r in lk.values() if not r[4])
        dormant = sum(1 for lk in self.links.values() for r in lk.values() if r[4])
        eps = sum(1 for e in self.episodes if not e['dormant'])
        return dict(active_links=links, dormant_links=dormant, active_episodes=eps,
                    stored_episodes=len(self.episodes), tombstones=self.tombstones)

    def snapshot(self):
        return deepcopy(dict(words=self.words, routes=self.routes,
                             order_tokens={f'{a}>{b}': c for (a, b), c in self.order_tokens.items()},
                             form_tokens=[dict(t, trigger=sorted(map(list, t['trigger']))) for t in self.form_tokens],
                             form_same=sorted(self.form_same), marks=self.marks))
