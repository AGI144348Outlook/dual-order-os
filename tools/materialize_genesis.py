"""Copy and verify every pinned Genesis file, including binary inbox archives."""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd):
    p = subprocess.run(['git', *args], cwd=cwd, capture_output=True)
    if p.returncode:
        raise RuntimeError('Git source operation failed: ' + args[0])
    return p.stdout


def verify(root=ROOT):
    manifest = json.loads((root / 'matrices/echo-integration/source-manifest.json').read_text())
    directory = root / manifest['destination']
    expected = {f['path']: f for f in manifest['files']}
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()
              and '__pycache__' not in p.parts}
    if actual != set(expected):
        raise ValueError('Snapshot file inventory differs from pinned source')
    for name, f in expected.items():
        p = directory / name
        if p.is_symlink():
            raise ValueError('Unexpected snapshot symlink')
        data = p.read_bytes()
        digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if digest != f['sha'] or len(data) != f['size']:
            raise ValueError('Source identity mismatch: ' + name)
    return len(expected)


def materialize():
    manifest = json.loads((ROOT / 'matrices/echo-integration/source-manifest.json').read_text())
    if manifest['repository'] != 'AGI144348Outlook/Echo_Green_Future':
        raise ValueError('Unexpected source repository')
    dest = ROOT / 'vendor/echo-genesis'
    if manifest['destination'] != 'vendor/echo-genesis':
        raise ValueError('Unexpected destination')
    with tempfile.TemporaryDirectory() as tmp:
        git('init', '-q', cwd=tmp)
        git('remote', 'add', 'origin', 'https://github.com/' + manifest['repository'] + '.git', cwd=tmp)
        git('fetch', '--depth=1', 'origin', manifest['commit'], cwd=tmp)
        for f in manifest['files']:
            name = Path(f['path'])
            if name.is_absolute() or '..' in name.parts or f['mode'] not in ('100644', '100755'):
                raise ValueError('Unsupported source entry')
            data = git('show', manifest['commit'] + ':' + f['path'], cwd=tmp)
            digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if digest != f['sha'] or len(data) != f['size']:
                raise ValueError('Pinned source mismatch')
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() != data:
                raise ValueError('Refusing to overwrite changed snapshot: ' + f['path'])
            target.write_bytes(data)
            target.chmod(0o755 if f['mode'] == '100755' else 0o644)
    print('Verified complete Genesis snapshot:', verify(), 'files')


if __name__ == '__main__':
    materialize()
