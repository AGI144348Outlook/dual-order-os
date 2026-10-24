"""Echo as journeyman: his shadow run during an inventory sweep.

Before each ruling, Echo guesses which inventory folder an item belongs in. He has several ways of
guessing ("arms"); his own A-101 bandit (AlgorithmMatrix.bandit_select) picks which way to trust for
that kind of file, and A-113 (record_outcome, checkpoint_generation) records whether the guess matched
the ruling. His learned state is saved after each sweep and loaded by the next, so what he learned in
one folder carries into the next.

Failures catalog boxes (Timothy, 2026-10-24; pre-test entry dual-order-os#13). When A-113 discards a
generation as a collapse, its failures are not forgotten:
  ת box  one card per failed attempt in a discarded generation (the evidence)
  ק box  one card per combination of algorithms that failed at an attempt: A-101 chose way of guessing
         X for kind of file Y, and A-113 discarded the generation. It names the task attempted, counts
         the failures and points at their ת cards. Revised to `outgrown` when the same combination later
         succeeds in an anchored generation. Nothing is ever deleted.
A-101 reads the ת box through this harness: just before each choice, discarded failures are added to the
history it sees at FAILURE_WEIGHT of an attempt (no success), then the true history is restored. So a way
of guessing with discarded failures no longer looks untried, and A-113's anchored history is untouched.

Echo's kernel is loaded unchanged from git (the 63eb9829 skeleton). Nothing here edits it.
The arms are simple rules written by the sweeps; the score shows which rule he learns to trust,
not understanding.
"""
import importlib.util
import json
import os
import random
import re
import subprocess
import tempfile
import warnings

from catalog_box import CatalogBox

SKEL_BLOB = '63eb982989b4f3478d649430b555c8f4ba755c27'
FAILURE_WEIGHT = 0.5      # proposed by Claude; Timothy did not choose a weight


def load_echo(repo):
    src = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', SKEL_BLOB], capture_output=True, check=True).stdout
    path = os.path.join(tempfile.mkdtemp(), 'echo_governor_skeleton.py')
    open(path, 'wb').write(src)
    spec = importlib.util.spec_from_file_location('echo_kernel', path)
    kernel = importlib.util.module_from_spec(spec)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        spec.loader.exec_module(kernel)
    return kernel.AlgorithmMatrix()


class FailureBoxes:
    """The ת failures box and the ק combination-notes box, each a CatalogBox (SQLite, append-only revisions)."""

    def __init__(self, folder, sweep):
        os.makedirs(folder, exist_ok=True)
        self.folder, self.sweep = folder, re.sub(r'[^A-Za-z0-9_.-]', '-', sweep)
        self.tav = CatalogBox(os.path.join(folder, 'tav_failures.sqlite'))
        self.qof = CatalogBox(os.path.join(folder, 'qof_combinations.sqlite'))
        self.weight = {}
        for card in self.tav.list('cards', glyph='ת'):
            k = (card['body']['way'], card['body']['kind'])
            self.weight[k] = self.weight.get(k, 0) + FAILURE_WEIGHT

    @staticmethod
    def _cid(*parts):
        return re.sub(r'[^A-Za-z0-9_.:-]', '-', '.'.join(parts))[:128]

    def file_discarded(self, generation, attempts, cp):
        """attempts: [(n, item, path, kind, way, guess, ruling, hit)] of a DISCARDED generation."""
        by_combo = {}
        for n, item, path, kind, way, guess, ruling, hit in attempts:
            if hit:
                continue
            tid = self._cid('T', self.sweep, str(n))
            card = self.tav.put_card(tid, f'{way} guessed {guess} for {path}', dict(
                sweep=self.sweep, n=n, item=item, path=path, kind=kind, way=way, guess=guess, ruling=ruling,
                generation=generation, generation_rate=cp.get('current_rate'), baseline_rate=cp.get('baseline_rate'),
                decision=cp.get('decision')), glyph='ת', tags=['discarded-failure', kind, way],
                provenance=dict(selector='A-101 bandit_select', anchor='A-113 checkpoint_generation'))
            self.weight[(way, kind)] = self.weight.get((way, kind), 0) + FAILURE_WEIGHT
            by_combo.setdefault((way, kind), []).append(dict(box='ת', id=tid, revision=card['revision'], n=n, sweep=self.sweep))
        for (way, kind), refs in by_combo.items():
            qid = self._cid('C', way, kind)
            try:
                old = self.qof.get('cards', qid)
                body, rev = old['body'], old['revision']
            except KeyError:
                body, rev = dict(combination=dict(selector='A-101 bandit_select', way=way, anchor='A-113 checkpoint_generation',
                                                  decision='DISCARDED'),
                                 task=f'place a {kind} file in its inventory folder', failures=0, evidence=[],
                                 status='open', first_seen=f'{self.sweep}:{refs[0]["n"]}'), 0
            body = dict(body, failures=body['failures'] + len(refs), evidence=body['evidence'] + refs, status='open',
                        last_seen=f'{self.sweep}:{refs[-1]["n"]}')
            self.qof.put_card(qid, f'A-101 chose {way} for {kind}; A-113 discarded it', body, glyph='ק',
                              tags=['failed-combination', kind, way], expected_revision=rev)

    def note_anchored(self, attempts):
        """After an ANCHORED generation: a ק combination that now succeeds is revised to outgrown (kept)."""
        for n, item, path, kind, way, guess, ruling, hit in attempts:
            if not hit:
                continue
            qid = self._cid('C', way, kind)
            try:
                old = self.qof.get('cards', qid)
            except KeyError:
                continue
            if old['body']['status'] == 'open':
                self.qof.put_card(qid, old['title'], dict(old['body'], status='outgrown', outgrown_at=f'{self.sweep}:{n}'),
                                  glyph='ק', tags=old['tags'], expected_revision=old['revision'])

    def export(self):
        for name, box in (('tav_failures', self.tav), ('qof_combinations', self.qof)):
            json.dump(box.list('cards'), open(os.path.join(self.folder, name + '.json'), 'w'), ensure_ascii=False, indent=1)
        self.tav.close()
        self.qof.close()


def shadow(repo, cases, arms, guess, state_path, seed, prior_state=None, boxes_dir=None, sweep=''):
    """cases: [(id, path, where, ruling)]; guess(arm, path, where) -> folder or None.
    Loads prior_state (a previous sweep's saved state) if given; saves this sweep's state to state_path.
    With boxes_dir, discarded failures go to the ת and ק boxes there, and A-101 sees them (see module doc)."""
    echo = load_echo(repo)
    boxes = FailureBoxes(boxes_dir, sweep) if boxes_dir else None
    carried = 0
    if prior_state and os.path.exists(prior_state):
        for arm, bucket, s, a in json.load(open(prior_state))['history']:
            echo.history[(arm, bucket)] = (s, a)
            carried += a
    cases = list(cases)
    random.Random(seed).shuffle(cases)
    trace, checkpoints, generation, gen_no = [], [], [], 0
    for k, (cid, path, where, truth) in enumerate(cases, 1):
        bucket = path.rsplit('.', 1)[-1] + (':in-file' if where else '')
        if boxes:                                     # let A-101 see discarded failures, then restore
            saved = {key: echo.history.get(key) for key in [(a, bucket) for a in arms]}
            for a in arms:
                w = boxes.weight.get((a, bucket), 0)
                if w:
                    s_, a_ = echo.history.get((a, bucket), (0, 0))
                    echo.history[(a, bucket)] = (s_, a_ + w)
            arm = echo.bandit_select(bucket, arms)
            for key, val in saved.items():
                if val is None:
                    echo.history.pop(key, None)
                else:
                    echo.history[key] = val
        else:
            arm = echo.bandit_select(bucket, arms)
        g = guess(arm, path, where)
        ok = g == truth
        echo.record_outcome(arm, bucket, ok)
        generation.append((k, cid, path, bucket, arm, g or '(none)', truth, int(ok)))
        cp = echo.checkpoint_generation() if k % 5 == 0 or k == len(cases) else None
        if cp:
            gen_no += 1
            checkpoints.append(dict(after=k, **{key: cp.get(key) for key in ('decision', 'current_rate', 'baseline_rate', 'attempts')}))
            if boxes and cp.get('decision') == 'DISCARDED':
                boxes.file_discarded(gen_no, generation, cp)
            elif boxes and cp.get('decision') == 'ANCHORED':
                boxes.note_anchored(generation)
            generation = []
        trace.append(dict(n=k, id=cid, path=path, bucket=bucket, arm=arm, guess=g or '(none)', ruling=truth, hit=int(ok),
                          checkpoint=cp['decision'] if cp else ''))
    hist = sorted([arm, bucket, s, a] for (arm, bucket), (s, a) in echo.history.items())
    json.dump(dict(kernel_blob=SKEL_BLOB, history=hist), open(state_path, 'w'), indent=0)
    trusted = {}
    for arm, bucket, s, a in hist:
        if a and (bucket not in trusted or (s / a, a) > (trusted[bucket][1], trusted[bucket][2])):
            trusted[bucket] = (arm, round(s / a, 2), a)
    box_summary = None
    if boxes:
        q = boxes.qof.list('cards', glyph='ק')
        box_summary = dict(tav_cards=len(boxes.tav.list('cards', glyph='ת')), qof_cards=len(q),
                           qof_open=sum(1 for c in q if c['body']['status'] == 'open'),
                           qof_outgrown=sum(1 for c in q if c['body']['status'] == 'outgrown'), failure_weight=FAILURE_WEIGHT)
        boxes.export()
    half = len(trace) // 2
    return trace, dict(cases=len(trace), hits=sum(t['hit'] for t in trace),
                       first_half=sum(t['hit'] for t in trace[:half]), second_half=sum(t['hit'] for t in trace[half:]),
                       half=half, attempts_carried_in=carried, trusted_by_bucket=trusted, kernel_blob=SKEL_BLOB,
                       checkpoints=checkpoints, boxes=box_summary)
