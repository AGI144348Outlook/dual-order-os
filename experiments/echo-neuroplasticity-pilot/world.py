"""Teacher-side micro-world. Echo never imports this module.

Cards are built from plain-word truth here, then encoded as opaque
(channel, value) codes that are re-randomised for every seed.
"""
import random

KINDS = ['bird', 'fish', 'tree', 'dog', 'stone', 'sun']
COLORS = ['red', 'green', 'yellow', 'white', 'black']
SIZES = ['big', 'small']
TEMPS = ['hot', 'cold']
WETS = ['wet', 'dry']
COUNTS = ['one', 'two', 'many']
COMPONENTS = {'bird': ['wing', 'tail', 'leg'], 'fish': ['fin', 'tail'],
              'tree': ['leaf', 'root'], 'dog': ['tail', 'leg'], 'stone': [], 'sun': []}
COMPONENT_WORDS = ['wing', 'tail', 'leg', 'fin', 'leaf', 'root']
PLURAL = {'bird': 'birds', 'fish': 'fish', 'tree': 'trees', 'dog': 'dogs',
          'stone': 'stones', 'sun': 'suns'}
CHANNELS = {'kind': KINDS, 'color': COLORS, 'size': SIZES, 'temp': TEMPS,
            'wet': WETS, 'count': COUNTS}
FRAME_WORDS = ['same', 'different', 'yes', 'no', 'opposite', 'part', 'what']
OPPOSITE = {'big': 'small', 'small': 'big', 'hot': 'cold', 'cold': 'hot',
            'wet': 'dry', 'dry': 'wet'}


class World:
    def __init__(self, seed):
        self.rng = random.Random(1000 + seed)
        used = set()

        def code(prefix):
            while True:
                c = prefix + str(self.rng.randrange(10 ** 6))
                if c not in used:
                    used.add(c)
                    return c
        self.chan = {ch: code('c') for ch in list(CHANNELS) + ['comp']}
        self.val = {}
        for ch, vals in CHANNELS.items():
            for v in vals:
                self.val[(ch, v)] = code('v')
        for c in COMPONENT_WORDS:
            self.val[('comp', c)] = code('v')
        # colour x kind pairs never shown together before quizzes
        pairs = [(c, k) for c in COLORS for k in KINDS]
        self.rng.shuffle(pairs)
        self.heldout_pairs = set(pairs[:9])

    def card(self, kind=None, color=None, size=None, temp=None, wet=None, count='one',
             comps='random', allow_heldout=False):
        r = self.rng
        while True:
            t = dict(kind=kind or r.choice(KINDS), color=color or r.choice(COLORS),
                     size=size or r.choice(SIZES), temp=temp or r.choice(TEMPS),
                     wet=wet or r.choice(WETS), count=count)
            if allow_heldout or (t['color'], t['kind']) not in self.heldout_pairs or (color and kind):
                break
        avail = COMPONENTS[t['kind']]
        if comps == 'random':
            t['comps'] = [c for c in avail if r.random() < 0.7]
        elif comps == 'all':
            t['comps'] = list(avail)
        else:
            t['comps'] = [c for c in comps if c in avail]
        return t

    def encode(self, t):
        feats = [(self.chan[ch], self.val[(ch, t[ch])]) for ch in CHANNELS]
        feats += [(self.chan['comp'], self.val[('comp', c)]) for c in t['comps']]
        self.rng.shuffle(feats)
        return {'feats': feats}

    def vary(self, t, channel):
        """Copy of truth t that differs on exactly one channel."""
        u = dict(t, comps=list(t['comps']))
        u[channel] = self.rng.choice([v for v in CHANNELS[channel] if v != t[channel]])
        if channel == 'kind':
            u['comps'] = [c for c in COMPONENTS[u['kind']] if self.rng.random() < 0.7]
        return u


def describe_words(t, channels):
    """Teacher's speaking convention: size, color, kind; counts lead with plurals."""
    order = ['count', 'size', 'temp', 'wet', 'color', 'kind']
    out = []
    for ch in order:
        if ch in channels:
            if ch == 'kind' and t['count'] != 'one' and 'count' in channels:
                out.append(PLURAL[t['kind']])
            else:
                out.append(t[ch])
    return out


# Silicon kids' dictionary slice: every definition word is itself an entry.
DICTIONARY = {
    'bird': ['wing', 'tail', 'leg'], 'fish': ['fin', 'tail'], 'tree': ['leaf', 'root'],
    'dog': ['tail', 'leg'], 'stone': ['dry', 'cold'], 'sun': ['big', 'hot', 'yellow'],
    'wing': ['bird', 'part'], 'fin': ['fish', 'part'], 'leaf': ['tree', 'part'],
    'root': ['tree', 'part'], 'tail': ['bird', 'fish', 'dog', 'part'], 'leg': ['bird', 'dog', 'part'],
    'red': [], 'green': [], 'yellow': [], 'white': [], 'black': [],
    'big': ['opposite', 'small'], 'small': ['opposite', 'big'],
    'hot': ['opposite', 'cold'], 'cold': ['opposite', 'hot'],
    'wet': ['opposite', 'dry'], 'dry': ['opposite', 'wet'],
    'one': [], 'two': ['one', 'one'], 'many': ['two', 'two'],
    'birds': ['two', 'bird'], 'trees': ['two', 'tree'], 'dogs': ['two', 'dog'],
    'stones': ['two', 'stone'], 'suns': ['two', 'sun'],
    'same': ['not', 'different'], 'different': ['not', 'same'],
    'yes': ['not', 'no'], 'no': ['not', 'yes'], 'not': [], 'opposite': ['different'],
    'part': [], 'what': [], 'who': [],
}
