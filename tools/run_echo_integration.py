"""Bounded combined evaluation; blocked historical runs remain visible."""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from libraries.echo_workspace import genesis
from tools.materialize_genesis import verify


def main():
    os.chdir(ROOT)
    out = ROOT / 'reports/echo-integration'
    out.mkdir(parents=True, exist_ok=True)
    count = verify()
    suite = unittest.defaultTestLoader.discover('tests')
    with (out / 'tests.txt').open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    source = ROOT / 'vendor/echo-genesis'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(source / 'src'), PYTHONHASHSEED='42')
    scripts = ['tests/number_integration_test.py', 'src/echo_governor_skeleton.py',
               'tests/echo_500round_run.py', 'tests/echo_blind_study.py',
               'tests/multipass_orientation_test.py', 'tests/pe_ayin_resh_communication.py',
               'tests/self_governance_test.py']
    historical = []
    for script in scripts:
        p = subprocess.run([sys.executable, '-B', str(source / script)], env=env,
                           cwd=source, capture_output=True, text=True, timeout=120)
        missing = next((line.strip() for line in p.stderr.splitlines() if 'FileNotFoundError:' in line), None)
        historical.append({'script': script, 'exit_code': p.returncode,
                           'status': 'completed' if p.returncode == 0 else 'blocked' if missing else 'failed',
                           'missing_input': missing})
    e = genesis()
    vgm = {'a': {'text': 'entity is connected', 'words': ['entity', 'connected']},
           'b': {'text': 'entity is not connected', 'words': ['entity', 'connected']}}
    contradiction = e.LogicReasoningMatrix(vgm, e.Lobby(e.AlgorithmMatrix())).derive_compose('a', 'b')
    diagnostic = {
        'generic_validation_still_permissive': e.validate({}, [lambda *args: False])[0],
        'generic_govern_still_permissive': e.govern({}, {'max_cost': 0}, {}),
        'contradiction_still_returned_as_theorem_candidate': contradiction is not None,
        'raw_glyph_tokenizer_still_drops_glyphs': e.AlgorithmicCommunicator()._tokenize('ר צ פ ע ק ש ת') == [],
        'interpretation': 'These are preserved baseline limitations, not passing reasoning benchmarks.'}
    cabinet = source / 'integration-inbox/group-canvas-file-cabinet/source'
    cabinet_tests = sorted(str(p) for part in ('hierarchy-tower', 'session-towers', 'card-chat')
                           for p in (cabinet / 'experiments' / part).glob('*.test.js'))
    if shutil.which('node'):
        node = subprocess.run(['node', '--test', *cabinet_tests], cwd=cabinet,
                              capture_output=True, text=True, timeout=120)
        (out / 'cabinet-tests.txt').write_text(node.stdout + node.stderr)
        match = re.search(r'# tests (\d+)', node.stdout)
        cabinet_result = {'status': 'completed' if node.returncode == 0 else 'failed',
                          'tests': int(match[1]) if match else None, 'exit_code': node.returncode}
    else:
        cabinet_result = {'status': 'blocked', 'reason': 'Node.js is unavailable'}
    demo = subprocess.run([sys.executable, '-m', 'libraries.echo_demo'], cwd=ROOT,
                          env=env, capture_output=True, text=True, timeout=60)
    if demo.returncode:
        raise RuntimeError('Integrated persistence demo failed')
    # Parsing also checks that the complete demo output is a valid structured response.
    (out / 'demo.json').write_text(json.dumps(json.loads(demo.stdout), ensure_ascii=False, indent=2) + '\n')
    report = {'source_files_verified': count, 'unit_tests': result.testsRun,
              'test_failures': len(result.failures), 'test_errors': len(result.errors),
              'historical_runs': historical, 'baseline_diagnostics': diagnostic,
              'archived_cabinet_tests': cabinet_result,
              'demo': 'completed', 'cloud_deployment': False, 'source_modified': False}
    (out / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not result.wasSuccessful() or any(r['status'] == 'failed' for r in historical) or cabinet_result['status'] == 'failed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
