"""Fresh learned-state profile; curriculum is never imported as knowledge."""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from libraries.echo_workspace import EchoWorkspace

def snapshot(workspace):
    return {
        'cards': len(workspace.box.list('cards')),
        'templates': len(workspace.box.list('templates')),
        'configurations': len(workspace.box.list('configurations')),
        'events': len(workspace.box.events()),
        'lexical_agents': len(workspace.lobby.agents),
        'indexed_entries': len(workspace.matrix.entry_classes),
        'content_units': len(workspace.matrix.content_units),
        'documents_seen': workspace.matrix.documents_seen,
        'identity_valid': workspace.identity.validate(),
        'governor_active': workspace.matrix.known['A-000']['status'] == 'ACTIVE',
    }

def create_fresh(database):
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic refusal to overwrite/reuse any existing file, populated or not.
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    return EchoWorkspace(path, capabilities=('read',))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True)
    args = parser.parse_args()
    with create_fresh(args.database) as workspace:
        print(json.dumps(snapshot(workspace), indent=2))

if __name__ == '__main__':
    main()
