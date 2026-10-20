"""Run the integrated workspace with synthetic vocabulary; no external services."""
import json
import tempfile
from pathlib import Path
from .echo_workspace import EchoWorkspace


def run(database):
    with EchoWorkspace(database, capabilities=EchoWorkspace.ALL_CAPABILITIES) as w:
        w.seed_profiles()
        w.put_word('word:paperclip', 'paperclip', 'attach card to index', department='verb',
                   source={'type': 'synthetic-demo'})
        w.put_word('word:index', 'index', 'card collection', department='noun',
                   source={'type': 'synthetic-demo'})
        clip = w.paperclip('relation:clip', 'word:paperclip', 'word:index')
        stamps = w.stamp_matches('word:paperclip')
        w.save_template('review', 'Paperclip and stamp review',
                        {'columns': ['word', 'attachments', 'glyph_tags'], 'execute': False},
                        ['word:paperclip', 'word:index', 'glyph:tsadi', clip['id']]
                        + [s['id'] for s in stamps])
        w.restore('review', 'session-1')
    # Reopen SQLite and reconstruct the original Genesis index from persisted cards.
    with EchoWorkspace(database) as w:
        return {'identity': w.identity.report(),
                'index': w.query({'operation': 'neighbors', 'word': 'paperclip'}),
                'stamps': [r for r in w.query({'operation': 'relations', 'card_id': 'word:paperclip'})
                           if r['body']['relation_type'] == 'associative-stamp'],
                'configuration': w.configuration_graph('session-1'),
                'limits': ['associations are not verified theorems',
                           '§DSL§ inversion unresolved', 'no cloud deployment']}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp:
        print(json.dumps(run(Path(tmp) / 'echo.sqlite'), ensure_ascii=False, indent=2))
