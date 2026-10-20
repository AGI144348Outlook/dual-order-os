"""Verify adopted source files against pinned branch blob identities."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def verify():
    provenance=json.loads((ROOT/'matrices/echo-integration/branch-components.json').read_text())
    for item in provenance['files']:
        path=ROOT/item['path'];data=path.read_bytes()
        digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if digest!=item['sha']:
            raise ValueError('Recovered branch file changed: '+item['path'])
    return len(provenance['files'])


if __name__=='__main__':print('Verified branch component source files:',verify())
