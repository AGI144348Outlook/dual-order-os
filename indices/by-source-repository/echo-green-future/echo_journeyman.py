"""Echo as journeyman: his shadow run during an inventory sweep.

Before each ruling, Echo guesses which inventory folder an item belongs in. He has several ways of
guessing ("arms"); his own A-101 bandit (AlgorithmMatrix.bandit_select) picks which way to trust for
that kind of file, and A-113 (record_outcome, checkpoint_generation) records whether the guess matched
the ruling. His learned state is saved after each sweep and loaded by the next, so what he learned in
one folder carries into the next.

Echo's kernel is loaded unchanged from git (the 63eb9829 skeleton). Nothing here edits it.
The arms are simple rules written by the sweeps; the score shows which rule he learns to trust,
not understanding.
"""
import importlib.util
import json
import os
import random
import subprocess
import tempfile
import warnings

SKEL_BLOB = '63eb982989b4f3478d649430b555c8f4ba755c27'


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


def shadow(repo, cases, arms, guess, state_path, seed, prior_state=None):
    """cases: [(id, path, where, ruling)]; guess(arm, path, where) -> folder or None.
    Loads prior_state (a previous sweep's saved state) if given; saves this sweep's state to state_path."""
    echo = load_echo(repo)
    carried = 0
    if prior_state and os.path.exists(prior_state):
        for arm, bucket, s, a in json.load(open(prior_state))['history']:
            echo.history[(arm, bucket)] = (s, a)
            carried += a
    cases = list(cases)
    random.Random(seed).shuffle(cases)
    trace = []
    for k, (cid, path, where, truth) in enumerate(cases, 1):
        bucket = path.rsplit('.', 1)[-1] + (':in-file' if where else '')
        arm = echo.bandit_select(bucket, arms)
        g = guess(arm, path, where)
        ok = g == truth
        echo.record_outcome(arm, bucket, ok)
        if k % 5 == 0:
            echo.checkpoint_generation()
        trace.append(dict(n=k, id=cid, path=path, bucket=bucket, arm=arm, guess=g or '(none)', ruling=truth, hit=int(ok)))
    echo.checkpoint_generation()
    hist = sorted([arm, bucket, s, a] for (arm, bucket), (s, a) in echo.history.items())
    json.dump(dict(kernel_blob=SKEL_BLOB, history=hist), open(state_path, 'w'), indent=0)
    trusted = {}
    for arm, bucket, s, a in hist:
        if a and (bucket not in trusted or (s / a, a) > (trusted[bucket][1], trusted[bucket][2])):
            trusted[bucket] = (arm, round(s / a, 2), a)
    half = len(trace) // 2
    return trace, dict(cases=len(trace), hits=sum(t['hit'] for t in trace),
                       first_half=sum(t['hit'] for t in trace[:half]), second_half=sum(t['hit'] for t in trace[half:]),
                       half=half, attempts_carried_in=carried, trusted_by_bucket=trusted, kernel_blob=SKEL_BLOB)
