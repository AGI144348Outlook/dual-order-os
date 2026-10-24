"""Echo's talk layer: learning to understand questions and to reply, on top of the pilot learner.

It holds no classroom words, meanings or question forms; a guard (test_course.py) scans this
file to enforce that. Word meanings are learned by the pilot learner (echo_np.Echo, unchanged).

Innate tools (disclosed in dual-order-os#14). They are operations, never word meanings:
  matching   keep the desk items whose features include every grounding of the content words
  T#         tally how many items matched (perceived as a magnitude, up to any size)
  T?         check whether any item matched (perceived as a truth value)
  T*         gesture at the matched items
  T=<c>      tell the value the matched items carry on perceptual channel c
  ask        a צ question about a word never met, or about a question form with every tool ruled out

Learned, never given:
  - which words are content words (they reliably ground to a feature, per the pilot learner)
  - which question forms call which tool (route evidence, combined naive-Bayes style across form words,
    narrowed to candidates; Echo's own kernel A-101 bandit_select picks among the candidates, and
    A-113 record_outcome / checkpoint_generation anchor or discard each generation of route outcomes)
  - the words for magnitudes, truth values and feature values he speaks

Failures (#13): a route outcome in a discarded generation is filed as a ת card; a failed combination of
question form x tool goes to the ק box. A combination with an open ק card, or that failed since the
form last succeeded, is never offered again for that form (a repeat is not a new guess). When nothing
new is left, Echo asks. Discarded failures count at FAILURE_WEIGHT in what A-101 sees.

Speech: Echo says only words his teacher has qualified (green). When he lacks a qualified word for
what a tool found, he gestures at the matched items instead.
"""
import importlib.util
import math
import os
import re
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'experiments', 'echo-neuroplasticity-pilot'))
sys.path.insert(0, os.path.join(ROOT, 'libraries'))
from echo_np import Echo                    # noqa: E402  (pilot learner, unchanged)
from catalog_box import CatalogBox          # noqa: E402

KERNEL = os.path.join(ROOT, 'vendor', 'echo-genesis', 'src', 'echo_governor_skeleton.py')
KERNEL_BLOB = '63eb982989b4f3478d649430b555c8f4ba755c27'
FAILURE_WEIGHT = 0.5
GENERATION = 5            # route outcomes per A-113 generation
NARROW = 0.25             # tools whose posterior is at least this share of the best stay candidates
MAG, TRUTH = '#', '?'     # Echo's own channels for tallies and truth values


def load_kernel():
    spec = importlib.util.spec_from_file_location('echo_kernel', KERNEL)
    mod = importlib.util.module_from_spec(spec)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        spec.loader.exec_module(mod)
    return mod.AlgorithmMatrix()


def words_of(utterance):
    return re.findall(r"[a-z0-9]+", utterance.lower()) if isinstance(utterance, str) else list(utterance)


class Boxes:
    """ת box (discarded route failures) and ק box (failed form x tool combinations)."""

    def __init__(self, folder):
        self.on = folder is not None
        self.weight = {}
        if not self.on:
            return
        os.makedirs(folder, exist_ok=True)
        self.tav = CatalogBox(os.path.join(folder, 'tav_failures.sqlite'))
        self.qof = CatalogBox(os.path.join(folder, 'qof_combinations.sqlite'))
        self.n = len(self.tav.list('cards', glyph='ת'))

    @staticmethod
    def cid(*bits):
        return re.sub(r'[^A-Za-z0-9_.:-]', '-', '.'.join(bits))[:128]

    def closed(self, form, tool):
        if not self.on:
            return False
        try:
            return self.qof.get('cards', self.cid('C', form, tool))['body']['state'] == 'open'
        except KeyError:
            return False

    def discard(self, generation, cp):
        if not self.on:
            return
        for form, tool, ok, said in generation:
            if ok:
                continue
            self.n += 1
            tid = self.cid('T', str(self.n))
            card = self.tav.put_card(tid, f'{tool} for [{form}] failed', dict(
                form=form, tool=tool, utterance=said, generation_rate=cp.get('current_rate'),
                baseline_rate=cp.get('baseline_rate'), decision=cp.get('decision')), glyph='ת',
                tags=['discarded-failure', tool], provenance=dict(selector='A-101 bandit_select',
                                                                    anchor='A-113 checkpoint_generation'))
            self.weight[(tool, form)] = self.weight.get((tool, form), 0) + FAILURE_WEIGHT
            qid = self.cid('C', form, tool)
            try:
                old = self.qof.get('cards', qid)
                body, rev = old['body'], old['revision']
            except KeyError:
                body, rev = dict(combination=dict(selector='A-101 bandit_select', tool=tool, form=form,
                                                  anchor='A-113 checkpoint_generation'),
                                 failures=0, evidence=[], state='open'), 0
            body = dict(body, failures=body['failures'] + 1, state='open',
                        evidence=body['evidence'] + [dict(box='ת', id=tid, revision=card['revision'])])
            self.qof.put_card(qid, f'{tool} for [{form}]; A-113 discarded it', body, glyph='ק',
                              tags=['failed-combination', tool], expected_revision=rev)

    def outgrow(self, form, tool):
        if not self.on:
            return
        qid = self.cid('C', form, tool)
        try:
            old = self.qof.get('cards', qid)
        except KeyError:
            return
        if old['body']['state'] == 'open':
            self.qof.put_card(qid, old['title'], dict(old['body'], state='outgrown'), glyph='ק',
                              tags=old['tags'], expected_revision=old['revision'])

    def tally(self):
        if not self.on:
            return None
        q = self.qof.list('cards', glyph='ק')
        return dict(tav=len(self.tav.list('cards', glyph='ת')), qof=len(q),
                    qof_open=sum(1 for c in q if c['body']['state'] == 'open'),
                    qof_outgrown=sum(1 for c in q if c['body']['state'] == 'outgrown'))

    def close(self):
        if self.on:
            self.tav.close()
            self.qof.close()


class Talker:
    def __init__(self, seed=0, boxes_dir=None, learn_routes=True, **flags):
        self.echo = Echo(seed=seed, **flags)
        self.kernel = load_kernel()
        self.boxes = Boxes(boxes_dir)
        self.learn_routes = learn_routes
        self.ev = {}              # form cue -> tool -> route examples with that cue
        self.nt = {}              # tool -> route examples
        self.met_form = set()     # words met only inside questions
        self.failed = {}          # form -> tools failed since that form last succeeded
        self.generation, self.since = [], 0
        self.qualified = set()
        self.last = None
        self.events = []

    # ---------------- perception of scenes (innate) ----------------
    @staticmethod
    def scene_card(scene):
        """Scenes the teacher can show: one item, a group (perceived as a magnitude),
        or a word held against an item (perceived as a truth value by the matching tool)."""
        if 'card' in scene:
            return scene['card']
        if 'group' in scene:
            return dict(feats=[(MAG, len(scene['group']))])
        raise ValueError('unknown scene')

    def perceive(self, scene):
        """Like scene_card, and a held word against an item (scene with 'probe') becomes a truth value."""
        if 'probe' in scene:
            p = scene['probe']
            fits = self.content(p) and self.echo.fit(p, self.echo.feats(scene['against'])) > 0
            return self.truth_card(fits)
        return self.scene_card(scene)

    def truth_card(self, value):
        return dict(feats=[(TRUTH, bool(value))])

    # ---------------- word knowledge ----------------
    def met(self, w):
        return self.echo.marks.get(w) is not None or w in self.met_form

    def content(self, w):
        e = self.echo
        return e._known(w) and e._reliable(w)

    def word_for(self, feat):
        """Best qualified word whose grounding is this feature."""
        best, bestv = None, -1.0
        for w in self.qualified:
            if self.content(w) and self.echo.grounding(w) == feat:
                v = self.echo.p_word(w, feat)
                if v > bestv:
                    best, bestv = w, v
        return best

    # ---------------- lessons on words (passed to the pilot learner) ----------------
    def hear(self, words, scene):
        self.echo.hear(words_of(words), [self.perceive(scene)])

    def hear_check(self, probe, card, words):
        """The teacher holds a word against an item and then speaks: Echo perceives whether
        the probe word's grounding fits the item, and hears the spoken words with that truth value."""
        fits = self.echo.fit(probe, self.echo.feats(card)) > 0 if self.content(probe) else None
        if fits is not None:
            self.echo.hear(words_of(words), [self.truth_card(fits)])
        return fits

    def recognise(self, word, scenes, practice=False):
        item = dict(type='pick_card', query_words=[word], options=[self.perceive(s) for s in scenes])
        self.last = ('pick_card', item)
        return self.echo.attempt(item, practice)

    def name(self, scene, options, practice=False):
        item = dict(type='pick_word', cards=[self.perceive(scene)], options=list(options))
        self.last = ('pick_word', item)
        return self.echo.attempt(item, practice)

    def word_feedback(self, response, ok, reveal=None):
        _, item = self.last
        self.echo.feedback(item, response, ok, reveal)

    def told(self, word, scenes):
        """Teacher's reply to a צ question about a word: examples of it."""
        for s in scenes:
            self.echo.answer_from_teacher(word, [self.perceive(s)])

    def told_form(self, word):
        """Teacher's reply to a צ question about a word with no example: it belongs to the question."""
        self.met_form.add(word)

    def qualify(self, words):
        self.qualified = set(words)

    def questions(self, on):
        self.echo.questions_on = on

    def rest(self):
        self.echo.rest()

    # ---------------- understanding a question ----------------
    def tools(self, desk):
        chans = sorted({f[0] for c in desk for f in self.echo.feats(c)})
        return ['T#', 'T*', 'T?'] + ['T=' + c for c in chans]

    def parse(self, words):
        """Content words become groundings; the rest is the question's form. Form cues (innate, disclosed):
        each form word, the first position, and adjacent pairs, with content words seen as an open slot."""
        cons, seq = [], []
        for w in words:
            if self.content(w):
                cons.append(w)
                if not seq or seq[-1] != '_':
                    seq.append('_')
            else:
                seq.append(w)
        cues = [w for w in seq if w != '_'] + ['^' + seq[0]] if seq else []
        cues += [a + '+' + b for a, b in zip(seq, seq[1:])]
        return [self.echo.grounding(w) for w in cons], cons, cues, ' '.join(seq)

    def posterior(self, cues, tools):
        """Naive Bayes over route examples: P(tool) times P(cue present | tool) for each cue met before.
        Cues never seen with any tool are skipped (they carry nothing yet)."""
        total = sum(self.nt.get(t, 0.0) for t in tools)
        logp = {t: math.log((self.nt.get(t, 0.0) + 1) / (total + len(tools))) for t in tools}
        for u in set(cues):
            row = self.ev.get(u)
            if not row:
                continue
            for t in tools:
                logp[t] += math.log((row.get(t, 0.0) + 0.5) / (self.nt.get(t, 0.0) + 1.0))
        m = max(logp.values())
        p = {t: math.exp(v - m) for t, v in logp.items()}
        s = sum(p.values())
        return {t: v / s for t, v in p.items()}

    def matches(self, desk, groundings):
        return [i for i, c in enumerate(desk) if all(g in self.echo.feats(c) for g in groundings)]

    def run_tool(self, tool, desk, hits):
        if tool == 'T#':
            return ('feat', (MAG, len(hits)))
        if tool == 'T?':
            return ('feat', (TRUTH, bool(hits)))
        if tool == 'T*':
            return ('gesture', hits)
        ch = tool[2:]
        vals = {}
        for i in hits:
            for f in self.echo.feats(desk[i]):
                if f[0] == ch:
                    vals[f] = vals.get(f, 0) + 1
        if not vals:
            return ('gesture', hits)
        return ('feat', max(sorted(vals), key=lambda f: vals[f]))

    def reply(self, utterance, desk):
        """desk: list of cards. Returns dict(say=[...]) | dict(gesture=[...]) | dict(ask=word)."""
        words = words_of(utterance)
        unmet = [w for w in words if not self.met(w)]
        if unmet:
            self.last = ('ask', dict(word=unmet[0], words=words))
            return dict(ask=unmet[0])
        groundings, cons, forms, form = self.parse(words)
        tools = self.tools(desk)
        post = self.posterior(forms, tools)
        best = max(post.values())
        ranked = sorted(tools, key=lambda t: (-post[t], t))
        cand = [t for t in ranked if post[t] >= NARROW * best
                and t not in self.failed.get(form, set()) and not self.boxes.closed(form, t)]
        if not cand:
            self.last = ('ask_question', dict(form=form, forms=forms, words=words))
            return dict(ask_question=form)
        tool = self.select(form, cand)
        hits = self.matches(desk, groundings)
        kind, out = self.run_tool(tool, desk, hits)
        resp = None
        if kind == 'feat':
            w = self.word_for(out)
            resp = dict(say=[w]) if w else dict(gesture=hits)
        else:
            resp = dict(gesture=out)
        self.last = ('reply', dict(words=words, form=form, forms=forms, cons=cons, tool=tool, desk=desk,
                                   hits=hits, resp=resp))
        return resp

    def select(self, form, cand):
        if len(cand) == 1:      # nothing to choose; also avoids the kernel's log(total) with total < 1
            return cand[0]
        k = self.kernel
        saved = {key: k.history.get(key) for key in [(t, form) for t in cand]}
        for t in cand:
            w = self.boxes.weight.get((t, form), 0)
            if w:
                s_, a_ = k.history.get((t, form), (0, 0))
                k.history[(t, form)] = (s_, a_ + w)
        tool = k.bandit_select(form, cand)
        for key, val in saved.items():
            if val is None:
                k.history.pop(key, None)
            else:
                k.history[key] = val
        return tool

    # ---------------- feedback on a reply ----------------
    def tool_of(self, reveal, desk):
        """Which tool would give the teacher's shown answer: read from the grounding of the word said."""
        say = reveal.get('say')
        if not say:
            return 'T*'
        g = self.echo.grounding(say[0]) if self.content(say[0]) else None
        if g is None:
            return None
        if g[0] == MAG:
            return 'T#'
        if g[0] == TRUTH:
            return 'T?'
        return 'T=' + g[0]

    def credit(self, cues, tool):
        self.nt[tool] = self.nt.get(tool, 0.0) + 1
        for u in set(cues):
            row = self.ev.setdefault(u, {})
            row[tool] = row.get(tool, 0.0) + 1

    def shown(self, reveal):
        """Teacher's reply to a צ question about a question form: a demonstration of the answer."""
        kind, ctx = self.last
        if kind != 'ask_question' or not self.learn_routes:
            return
        right = self.tool_of(reveal, None)
        if right is None:
            return
        self.credit(ctx['forms'], right)
        self.failed.pop(ctx['form'], None)
        self.boxes.outgrow(ctx['form'], right)

    def feedback(self, ok, reveal=None):
        """ok: teacher's ✓/✗ on the reply. reveal: the teacher's own reply, dict(say=[...], gesture=[...])."""
        kind, ctx = self.last
        if kind != 'reply' or not self.learn_routes:
            return
        form, tool, desk = ctx['form'], ctx['tool'], ctx['desk']
        right = tool if ok else (self.tool_of(reveal, desk) if reveal else None)
        route_ok = ok or (right == tool)
        if right is not None:
            self.credit(ctx['forms'], right)
            self.boxes.outgrow(form, right)
        if ok:                                   # B3-a: words used in a reply judged right gain protection
            for w in ctx['cons'] + (ctx['resp'].get('say') or []):
                self.echo._use(w, True)
        if route_ok:
            self.failed.pop(form, None)
        elif right is not None or reveal is None:
            self.failed.setdefault(form, set()).add(tool)
        self.kernel.record_outcome(tool, form, route_ok)
        self.generation.append((form, tool, route_ok, ' '.join(ctx['words'])))
        if reveal:
            self.learn_from_reveal(ctx, reveal)
        self.since += 1
        if self.since >= GENERATION:
            self.close_generation()

    def learn_from_reveal(self, ctx, reveal):
        """Words of the question that were met in word lessons are heard with the items the teacher
        gestured at; a word said for a tally is heard with that magnitude."""
        desk, pts = ctx['desk'], reveal.get('gesture') or []
        lesson_words = [w for w in ctx['words'] if self.echo.marks.get(w) is not None]
        if lesson_words:
            for i in pts:
                self.echo.hear(lesson_words, [desk[i]])
        say = reveal.get('say')
        right = self.tool_of(reveal, desk)
        if say and right == 'T#':
            self.echo.hear(say, [dict(feats=[(MAG, len(pts))])])

    def close_generation(self):
        cp = self.kernel.checkpoint_generation()
        if cp.get('decision') == 'DISCARDED':
            self.boxes.discard(self.generation, cp)
        self.events.append(dict(decision=cp.get('decision'), rate=cp.get('current_rate'),
                                baseline=cp.get('baseline_rate'), attempts=cp.get('attempts')))
        self.generation, self.since = [], 0

    def snapshot(self):
        return dict(routes={u: dict(r) for u, r in self.ev.items()}, met_form=sorted(self.met_form),
                    qualified=sorted(self.qualified),
                    kernel_history=sorted([t, f, s, a] for (t, f), (s, a) in self.kernel.history.items()),
                    generations=self.events, boxes=self.boxes.tally(), kernel_blob=KERNEL_BLOB)
