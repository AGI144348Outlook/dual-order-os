"""Teacher side. Echo never imports this module.

Echo's world is his own repository, Echo_Green_Future: every file is an item. Its plain-word truth
(kind, format, size, place, spread, name parts) is worked out here from the frozen census snapshot,
then encoded as opaque (channel, value) codes re-randomised for every seed, so Echo never sees a string.
"""
import json
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))

FORMAT = {  # extension -> (format word, kind word)
    'py': ('python', 'code'), 'pyc': ('python', 'code'), 'js': ('javascript', 'code'), 'mjs': ('javascript', 'code'),
    'cjs': ('javascript', 'code'), 'jsx': ('javascript', 'code'), 'sh': ('shell', 'code'), 'css': ('css', 'code'),
    'md': ('markdown', 'document'), 'txt': ('text', 'document'), 'pdf': ('pdf', 'document'),
    'tsv': ('tsv', 'table'), 'csv': ('csv', 'table'),
    'json': ('json', 'data'), 'jsonl': ('jsonl', 'data'), 'npy': ('numpy', 'data'), 'parquet': ('parquet', 'data'),
    'b64': ('base', 'data'), 'glb': ('model', 'data'), 'wasm': ('wasm', 'data'),
    'yml': ('yaml', 'config'), 'toml': ('toml', 'config'), 'webmanifest': ('manifest', 'config'),
    'gitignore': ('git', 'config'), 'gitattributes': ('git', 'config'),
    'html': ('html', 'page'), 'gz': ('gzip', 'archive'), 'zip': ('zip', 'archive'),
    'png': ('png', 'picture'), 'jpeg': ('jpeg', 'picture'), 'jpg': ('jpeg', 'picture'), 'svg': ('svg', 'picture'),
    'mp4': ('mp4', 'video'), 'diff': ('diff', 'patch'),
}
PLACE = {  # top folder -> place word (folders with at least 10 files; the rest are 'elsewhere')
    'Datasets': 'datasets', 'code_library_registry': 'codelib', 'contract-000': 'contract',
    'experiments': 'experiments', 'integration-inbox': 'inbox', 'LZ-branches': 'lz', '': 'top', 'pwa': 'pwa',
    'ECHO_AutonomousAgency': 'agency', 'Business': 'business', '.github': 'github', 'core-lexicon': 'lexicon',
    'docs': 'docs', 'Library': 'library', 'L2-library': 'shelves', 'echo': 'echo', 'research-registry': 'research',
    'lobbies': 'lobbies', 'ECHO_GlyphRegistry': 'glyphs', 'results': 'results', 'src': 'src',
    'dev-suite': 'devsuite', 'matrices': 'matrices', 'tests': 'tests', 'Algorithms': 'algorithms',
    'Workshop': 'workshop', 'IVS': 'ivs', 'source-transcriptions': 'transcriptions',
}
NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
YESNO = ['no', 'yes']
SIZES = ['small', 'big']
SPREADS = ['rare', 'common']
BIG_BYTES = 2285          # census median: above it a file is big
# Words of the teacher's question frames; never used as name parts so a word has one meaning here.
FRAME_WORDS = set('''how many are there count the do you see show me point to which ones find is a any file files
of what kind format where folder in size named about this it that'''.split())
MIN_NAME_FILES = 6


def split_name(path):
    stem = path.split('/')[-1].split('.')[0]
    stem = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
    return {t for t in re.split(r'[^a-z]+', stem.lower()) if len(t) >= 3}


def ext_of(path):
    name = path.split('/')[-1]
    if name.startswith('.') and name.count('.') == 1:
        return name[1:]
    return name.rsplit('.', 1)[-1].lower() if '.' in name else ''


def load_snapshot():
    return json.load(open(os.path.join(HERE, 'world_snapshot.json')))


def plain_items():
    """Plain-word truth for every file of the snapshot. Files with an extension outside FORMAT are left out."""
    snap = load_snapshot()
    raw = []
    for it in snap['items']:
        e = ext_of(it['path'])
        if e not in FORMAT:
            continue
        fmt, kind = FORMAT[e]
        top = it['path'].split('/')[0] if '/' in it['path'] else ''
        raw.append(dict(path=it['path'], kind=kind, format=fmt, size=SIZES[it['bytes'] > BIG_BYTES],
                        place=PLACE.get(top, 'elsewhere'), spread=SPREADS[it['branches'] > 1],
                        parts=split_name(it['path'])))
    taken = set(FRAME_WORDS) | set(NUMBERS) | set(YESNO) | set(SIZES) | set(SPREADS) | set(PLACE.values()) | \
        {f for f, _ in FORMAT.values()} | {k for _, k in FORMAT.values()} | {'elsewhere', 'gz', 'json', 'raw'}
    counts = {}
    for it in raw:
        for t in it['parts']:
            counts[t] = counts.get(t, 0) + 1
    names = sorted(t for t, c in counts.items() if c >= MIN_NAME_FILES and t not in taken)
    for it in raw:
        it['parts'] = sorted(t for t in it['parts'] if t in names)
    return raw, names, snap['commit']


ITEMS, NAMES, COMMIT = plain_items()
KINDS = sorted({it['kind'] for it in ITEMS})
FORMATS = sorted({it['format'] for it in ITEMS})
PLACES = sorted({it['place'] for it in ITEMS} - {'elsewhere'})
CHANNELS = dict(kind=KINDS, format=FORMATS, size=SIZES, place=PLACES + ['elsewhere'], spread=SPREADS)
CONTENT_WORDS = dict(kind=KINDS, format=FORMATS, size=SIZES, place=PLACES, spread=SPREADS, name=NAMES)


class World:
    """One seed's encoding of the repository, with items split into a teaching pool and a test pool."""

    def __init__(self, seed):
        self.rng = random.Random(7000 + seed)
        used = set()

        def code(prefix):
            while True:
                c = prefix + str(self.rng.randrange(10 ** 6))
                if c not in used:
                    used.add(c)
                    return c
        self.chan = {ch: code('c') for ch in list(CHANNELS) + ['name']}
        self.val = {(ch, v): code('v') for ch, vals in CHANNELS.items() for v in vals}
        self.val.update({('name', t): code('v') for t in NAMES})
        self.items = []
        for i, it in enumerate(ITEMS):
            feats = [(self.chan[ch], self.val[(ch, it[ch])]) for ch in CHANNELS]
            feats += [(self.chan['name'], self.val[('name', t)]) for t in it['parts']]
            self.items.append(dict(it, id=i, card=dict(feats=feats)))
        idx = list(range(len(self.items)))
        self.rng.shuffle(idx)
        half = set(idx[:len(idx) // 2])
        self.teach_pool = [self.items[i] for i in sorted(half)]
        self.test_pool = [self.items[i] for i in sorted(set(idx) - half)]

    def feature(self, channel, word):
        """The opaque feature a content word names (teacher's answer key)."""
        return (self.chan[channel], self.val[(channel, word)])

    @staticmethod
    def has(item, channel, word):
        return word in item['parts'] if channel == 'name' else item[channel] == word

    def desk(self, pool, n, rng, must=()):
        """A desk of n items, drawn so one folder does not swamp it; `must` items are included."""
        groups = {}
        for it in pool:
            groups.setdefault((it['place'], it['kind']), []).append(it)
        keys = sorted(groups)
        out = {it['id']: it for it in must}
        while len(out) < n:
            g = groups[rng.choice(keys)]
            it = rng.choice(g)
            out[it['id']] = it
        d = list(out.values())
        rng.shuffle(d)
        return d


def channel_of(word):
    for ch, words in CONTENT_WORDS.items():
        if word in words:
            return ch
    return None
