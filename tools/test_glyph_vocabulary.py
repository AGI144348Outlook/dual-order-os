"""Explicit, sense-specific vocabulary clipping experiment; no semantic promotion."""
import argparse
import json
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from libraries.echo_sentence_cards import SentenceCards, lexicon_from_zip, sense_id, LEXICON_BLOB
from libraries.echo_workspace import EchoWorkspace

# Human-selected source senses, not an automatic semantic discovery algorithm.
SELECTIONS = {'ayin': [('see', 0), ('look', 0), ('hear', 0), ('sense', 1)],
              'resh': [('match', 0)]}
PENDING = {'ayin': ['perceive', 'observe', 'notice', 'detect', 'distinguish'],
           'resh': ['identify', 'recognize', 'classify', 'compare', 'verify']}

def experiment(archive, database):
    dictionary = lexicon_from_zip(archive)
    selected_words = {w for selections in SELECTIONS.values() for w, _ in selections}
    cards = SentenceCards(database)
    cards.ingest({w: dictionary[w] for w in sorted(selected_words)},
                 source={'archive_git_blob': LEXICON_BLOB, 'member': 'core-lexicon/words.json'})
    cards.close()
    workspace = EchoWorkspace(database, capabilities=EchoWorkspace.ALL_CAPABILITIES)
    try:
        workspace.seed_profiles()
        profiles = {g: workspace.box.get('cards', 'glyph:' + g) for g in SELECTIONS}
        clipped = []
        for glyph, selections in SELECTIONS.items():
            for word, index in selections:
                cid = sense_id(word, index)
                relation = workspace.paperclip('vocabclip:' + glyph + ':' + cid,
                                              cid, 'glyph:' + glyph)
                clipped.append({'glyph': glyph, 'word': word, 'sense_index': index,
                                'definition': dictionary[word]['senses'][index]['def'],
                                'relation': relation['id']})
        unchanged = all(workspace.box.get('cards', 'glyph:' + g) == c for g, c in profiles.items())
        before = workspace.box.list('cards')
    finally:
        workspace.close()
    restored = EchoWorkspace(database)
    try:
        persistence = restored.box.list('cards') == before
        permission_blocked = False
        try:
            restored.paperclip('forbidden:test', sense_id('see', 0), 'glyph:ayin')
        except PermissionError:
            permission_blocked = True
    finally:
        restored.close()
    return {'selection_author': 'Codex, provisional task-scoped associations requested by Timothy',
            'source_git_blob': LEXICON_BLOB, 'clipped': clipped,
            'pending_not_clipped': {g: [{'word': w, 'present_in_dictionary': w in dictionary}
                                      for w in words] for g, words in PENDING.items()},
            'profiles_unchanged': unchanged, 'cards_restored': persistence,
            'read_only_write_blocked': permission_blocked,
            'excluded_senses': ['look:noun (facial expression)', 'sense:noun (awareness)',
                                'match:noun (fire-lighting object)'],
            'workflow_hypothesis': 'ע observation -> ר candidate recognition -> פ naming / ת labeling',
            'limits': ['No perception or recognition implementation was added.',
                       'Match is supporting comparison vocabulary, not sufficient proof of identity.',
                       'Missing words require sourced senses or separately approved working definitions.',
                       'This task-scoped order is not asserted as a universal prerequisite of identification.',
                       'No glyph profile, tokenizer, VGM truth, or Algorithm 000 authority was changed.']}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True)
    parser.add_argument('--output', default='reports/echo-glyph-vocabulary/results.json')
    parser.add_argument('--database', help='Keep the experimental catalog at this SQLite path')
    args = parser.parse_args()
    if args.database:
        result = experiment(args.archive, Path(args.database))
    else:
        with tempfile.TemporaryDirectory() as d:
            result = experiment(args.archive, Path(d) / 'cards.sqlite')
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
