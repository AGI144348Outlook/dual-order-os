"""
Letter and translation data for the Governor's multi-lobby system.

HEBREW_ALPHABET: 22 letters with LHEA operator semantics, Sefer Yetzirah
  classification (Mother/Double/Elemental), gematria, and phonetic value.
LATIN_ALPHABET: 23 classical Latin letters with Phoenician origin and
  semantic/phonetic character.
ENGLISH_ALPHABET: 26 letters with etymological origin tokens.

Translation dictionaries:
  HEBREW_ENGLISH: 80-entry semantic bridge (expanding the earlier 51)
  ENGLISH_LATIN: common English words with their Latin semantic equivalents
  HEBREW_LATIN: semantic bridges between Hebrew roots and Latin roots
    (meaning-based, not phonetic — melekh ↔ rex not melekh ↔ mel)

All sourced from training knowledge — flagged as such, not a verified
external file. Solid for well-established vocabulary.
"""

# ── HEBREW ALPHABET (22 letters) ───────────────────────────────────────────
# Properties encode: phonetic, gematria, Sefer Yetzirah class, LHEA operator
# meaning, and key Hebrew words exemplifying the letter's semantic domain.

HEBREW_ALPHABET = [
    {"name": "aleph", "glyph": "א", "department": "letter",
     "properties": ["silent", "breath", "primal", "potential", "unity", "ox",
                    "beginning", "one", "spirit", "air", "mother", "operator",
                    "oneness", "divine", "aleph_gematria_1"]},
    {"name": "bet", "glyph": "ב", "department": "letter",
     "properties": ["house", "container", "vessel", "inside", "dwelling",
                    "two", "double", "bet_gematria_2", "bayit", "blessing",
                    "creation", "beginning_of_creation"]},
    {"name": "gimel", "glyph": "ג", "department": "letter",
     "properties": ["camel", "movement", "carrying", "forward", "benefit",
                    "three", "gimel_gematria_3", "giving", "recipient",
                    "double", "channel"]},
    {"name": "dalet", "glyph": "ד", "department": "letter",
     "properties": ["door", "doorway", "threshold", "passage", "poverty",
                    "four", "dalet_gematria_4", "double", "daleth",
                    "giving", "receiving", "opening"]},
    {"name": "he", "glyph": "ה", "department": "letter",
     "properties": ["window", "breath", "expression", "divine_name",
                    "five", "he_gematria_5", "mother", "revelation",
                    "calling", "lo", "behold"]},
    {"name": "vav", "glyph": "ו", "department": "letter",
     "properties": ["hook", "nail", "connection", "and", "joining",
                    "six", "vav_gematria_6", "elemental", "truth",
                    "pillar", "beam"]},
    {"name": "zayin", "glyph": "ז", "department": "letter",
     "properties": ["sword", "weapon", "sustenance", "crown",
                    "seven", "zayin_gematria_7", "elemental", "cut",
                    "time", "nourishment"]},
    {"name": "het", "glyph": "ח", "department": "letter",
     "properties": ["fence", "enclosure", "life", "grace",
                    "eight", "het_gematria_8", "elemental", "chaim",
                    "separation", "protection"]},
    {"name": "tet", "glyph": "ט", "department": "letter",
     "properties": ["snake", "basket", "goodness", "surround",
                    "nine", "tet_gematria_9", "elemental", "hidden_good",
                    "coil", "objective"]},
    {"name": "yod", "glyph": "י", "department": "letter",
     "properties": ["hand", "point", "divine", "creation",
                    "ten", "yod_gematria_10", "elemental", "small",
                    "yad", "seed", "potential_action"]},
    {"name": "kaf", "glyph": "כ", "department": "letter",
     "properties": ["palm", "spoon", "crown", "bending",
                    "twenty", "kaf_gematria_20", "double",
                    "vessel", "covering", "כתר"]},
    {"name": "lamed", "glyph": "ל", "department": "letter",
     "properties": ["ox_goad", "learning", "teaching", "heart",
                    "thirty", "lamed_gematria_30", "elemental",
                    "toward", "for", "purpose", "aspiration"]},
    {"name": "mem", "glyph": "מ", "department": "letter",
     "properties": ["water", "flowing", "womb", "source",
                    "forty", "mem_gematria_40", "mother", "mayim",
                    "hidden", "revealed", "chaos", "wisdom"]},
    {"name": "nun", "glyph": "נ", "department": "letter",
     "properties": ["fish", "soul", "faithfulness", "emergence",
                    "fifty", "nun_gematria_50", "elemental",
                    "individual", "purpose", "nefesh"]},
    {"name": "samekh", "glyph": "ס", "department": "letter",
     "properties": ["support", "prop", "foundation", "circle",
                    "sixty", "samekh_gematria_60", "double",
                    "trust", "surrounding", "completion"]},
    {"name": "ayin", "glyph": "ע", "department": "letter",
     "properties": ["eye", "seeing", "spring", "source",
                    "seventy", "ayin_gematria_70", "elemental",
                    "perception", "insight", "depth"]},
    {"name": "pe", "glyph": "פ", "department": "letter",
     "properties": ["mouth", "speech", "expression", "face",
                    "eighty", "pe_gematria_80", "double",
                    "peh", "language", "command", "prayer"]},
    {"name": "tsadi", "glyph": "צ", "department": "letter",
     "properties": ["fish_hook", "hunt", "righteousness", "chase",
                    "ninety", "tsadi_gematria_90", "elemental",
                    "tzaddik", "justice", "righteous_person"]},
    {"name": "qof", "glyph": "ק", "department": "letter",
     "properties": ["back_of_head", "monkey", "sanctity", "cycle",
                    "hundred", "qof_gematria_100", "double",
                    "holy", "back", "behind", "cycle"]},
    {"name": "resh", "glyph": "ר", "department": "letter",
     "properties": ["head", "beginning", "leader", "identity",
                    "two_hundred", "resh_gematria_200", "double",
                    "rosh", "chief", "poverty", "wickedness"]},
    {"name": "shin", "glyph": "ש", "department": "letter",
     "properties": ["fire", "tooth", "sharp", "transform",
                    "three_hundred", "shin_gematria_300", "mother",
                    "shalom", "change", "return", "divine_fire"]},
    {"name": "tav", "glyph": "ת", "department": "letter",
     "properties": ["mark", "cross", "seal", "truth",
                    "four_hundred", "tav_gematria_400", "double",
                    "emet", "completion", "covenant", "end"]},
]

# ── LATIN ALPHABET (23 classical letters) ──────────────────────────────────

LATIN_ALPHABET = [
    {"name": "a", "glyph": "A", "department": "letter",
     "properties": ["aleph", "ox", "beginning", "open", "aer", "anima",
                    "aqua", "first", "primal", "vowel"]},
    {"name": "b", "glyph": "B", "department": "letter",
     "properties": ["beth", "house", "labial", "bene", "bonus",
                    "bellum", "two_strokes", "container"]},
    {"name": "c", "glyph": "C", "department": "letter",
     "properties": ["gimel", "camel", "cup_shape", "caelum", "cor",
                    "corpus", "curved", "k_sound", "velar"]},
    {"name": "d", "glyph": "D", "department": "letter",
     "properties": ["dalet", "door", "deus", "dies", "domus",
                    "dental", "giving"]},
    {"name": "e", "glyph": "E", "department": "letter",
     "properties": ["he", "window", "esse", "et", "ego",
                    "vowel", "existence"]},
    {"name": "f", "glyph": "F", "department": "letter",
     "properties": ["vav", "hook", "facio", "forma", "fides",
                    "labio_dental", "making"]},
    {"name": "g", "glyph": "G", "department": "letter",
     "properties": ["gimel", "gradus", "genus", "gloria",
                    "velar", "modified_c"]},
    {"name": "h", "glyph": "H", "department": "letter",
     "properties": ["het", "fence", "homo", "hora", "habeo",
                    "aspirate", "breath"]},
    {"name": "i", "glyph": "I", "department": "letter",
     "properties": ["yod", "hand", "ire", "ipse", "index",
                    "vowel_consonant", "singular"]},
    {"name": "k", "glyph": "K", "department": "letter",
     "properties": ["kaf", "palm", "kalends", "rare_in_latin",
                    "velar"]},
    {"name": "l", "glyph": "L", "department": "letter",
     "properties": ["lamed", "teaching", "lux", "lex", "locus",
                    "lateral", "flowing"]},
    {"name": "m", "glyph": "M", "department": "letter",
     "properties": ["mem", "water", "mater", "magnus", "mens",
                    "labial", "nasal", "mother"]},
    {"name": "n", "glyph": "N", "department": "letter",
     "properties": ["nun", "fish", "nomen", "natura", "nox",
                    "dental_nasal", "negation"]},
    {"name": "o", "glyph": "O", "department": "letter",
     "properties": ["ayin", "eye", "oculus", "orbis", "omnis",
                    "vowel", "circle", "wholeness"]},
    {"name": "p", "glyph": "P", "department": "letter",
     "properties": ["pe", "mouth", "pater", "populus", "pax",
                    "labial", "plosive"]},
    {"name": "q", "glyph": "Q", "department": "letter",
     "properties": ["qof", "back", "qui", "quod", "quaestio",
                    "velar", "always_followed_by_u"]},
    {"name": "r", "glyph": "R", "department": "letter",
     "properties": ["resh", "head", "rex", "ratio", "res",
                    "liquid", "rolling", "king", "reason"]},
    {"name": "s", "glyph": "S", "department": "letter",
     "properties": ["shin", "samekh", "sol", "sapiens", "spiritus",
                    "sibilant", "wisdom", "sun"]},
    {"name": "t", "glyph": "T", "department": "letter",
     "properties": ["tav", "mark", "tempus", "terra", "totus",
                    "dental", "time", "earth"]},
    {"name": "v", "glyph": "V", "department": "letter",
     "properties": ["vav", "hook", "vita", "virtus", "veritas",
                    "labio_dental", "life", "truth"]},
    {"name": "x", "glyph": "X", "department": "letter",
     "properties": ["cross", "unknown", "double_consonant", "ks_sound",
                    "ten_in_roman"]},
    {"name": "y", "glyph": "Y", "department": "letter",
     "properties": ["yod", "greek_upsilon", "borrowed", "vowel",
                    "ydem"]},
    {"name": "z", "glyph": "Z", "department": "letter",
     "properties": ["zayin", "sword", "zephyrus", "borrowed_from_greek",
                    "sibilant", "cut"]},
]

# ── ENGLISH ALPHABET (26 letters) ──────────────────────────────────────────

ENGLISH_ALPHABET = [
    {"name": l, "glyph": l.upper(), "department": "letter",
     "properties": props}
    for l, props in [
        ("a", ["aleph", "latin_a", "open_vowel", "beginning", "article"]),
        ("b", ["bet", "latin_b", "labial", "plosive", "second"]),
        ("c", ["latin_c", "gimel", "velar", "softens_before_e_i"]),
        ("d", ["dalet", "latin_d", "dental", "plosive"]),
        ("e", ["latin_e", "he", "mid_vowel", "most_common_english"]),
        ("f", ["latin_f", "vav", "labio_dental", "fricative"]),
        ("g", ["latin_g", "gimel", "velar", "hard_soft"]),
        ("h", ["latin_h", "het", "aspirate", "breath"]),
        ("i", ["yod", "latin_i", "high_front_vowel", "self"]),
        ("j", ["yod_evolved", "palatal", "medieval_addition"]),
        ("k", ["kaf", "latin_k", "velar", "plosive"]),
        ("l", ["lamed", "latin_l", "lateral", "liquid"]),
        ("m", ["mem", "latin_m", "labial", "nasal", "mother"]),
        ("n", ["nun", "latin_n", "dental", "nasal"]),
        ("o", ["ayin", "latin_o", "mid_back_vowel", "circle"]),
        ("p", ["pe", "latin_p", "labial", "plosive"]),
        ("q", ["qof", "latin_q", "always_qu", "velar"]),
        ("r", ["resh", "latin_r", "liquid", "rolling"]),
        ("s", ["shin", "samekh", "latin_s", "sibilant"]),
        ("t", ["tav", "latin_t", "dental", "plosive"]),
        ("u", ["vav_vowel", "latin_v", "high_back_vowel"]),
        ("v", ["vav", "latin_v", "labio_dental", "fricative"]),
        ("w", ["double_v", "germanic", "labial_glide"]),
        ("x", ["latin_x", "ks_compound", "unknown"]),
        ("y", ["yod", "latin_y", "high_front_glide"]),
        ("z", ["zayin", "latin_z", "sibilant", "rare_in_english"]),
    ]
]

# ── TRANSLATION DICTIONARIES ────────────────────────────────────────────────

# Hebrew-English (expanded from 51 → 80 entries)
HEBREW_ENGLISH_EXPANDED = [
    # already in import_hebrew_demo.py — adding new ones
    ("prayer",   "תפילה", "tefillah"),
    ("study",    "לימוד", "limud"),
    ("teacher",  "מורה",  "moreh"),
    ("student",  "תלמיד", "talmid"),
    ("covenant", "ברית",  "brit"),
    ("judgment", "דין",   "din"),
    ("mercy",    "רחמים", "rachamim"),
    ("justice",  "צדק",   "tzedek"),
    ("creation", "בריאה", "briah"),
    ("return",   "תשובה", "teshuvah"),
    ("blessing", "ברכה",  "brakha"),
    ("curse",    "קללה",  "kelalah"),
    ("voice",    "קול",   "kol"),
    ("silence",  "שתיקה", "shtikah"),
    ("beginning","ראשית", "reishit"),
    ("end",      "סוף",   "sof"),
    ("above",    "למעלה", "lema'alah"),
    ("below",    "למטה",  "lematah"),
    ("inside",   "פנים",  "pnim"),
    ("outside",  "חוץ",   "chuts"),
    ("gate",     "שער",   "sha'ar"),
    ("path",     "דרך",   "derekh"),
    ("way",      "דרך",   "derekh"),
    ("sword",    "חרב",   "cherev"),
    ("shield",   "מגן",   "magen"),
    ("bread",    "לחם",   "lechem"),
    ("salt",     "מלח",   "melach"),
    ("oil",      "שמן",   "shemen"),
    ("vessel",   "כלי",   "keli"),
]

# English-Latin semantic equivalents
ENGLISH_LATIN = [
    ("king",       "rex",        "regis"),
    ("queen",      "regina",     "reginae"),
    ("father",     "pater",      "patris"),
    ("mother",     "mater",      "matris"),
    ("son",        "filius",     "filii"),
    ("daughter",   "filia",      "filiae"),
    ("water",      "aqua",       "aquae"),
    ("fire",       "ignis",      "ignis"),
    ("earth",      "terra",      "terrae"),
    ("air",        "aer",        "aeris"),
    ("light",      "lux",        "lucis"),
    ("darkness",   "tenebrae",   "tenebrarum"),
    ("word",       "verbum",     "verbi"),
    ("truth",      "veritas",    "veritatis"),
    ("wisdom",     "sapientia",  "sapientiae"),
    ("knowledge",  "scientia",   "scientiae"),
    ("peace",      "pax",        "pacis"),
    ("war",        "bellum",     "belli"),
    ("love",       "amor",       "amoris"),
    ("life",       "vita",       "vitae"),
    ("death",      "mors",       "mortis"),
    ("soul",       "anima",      "animae"),
    ("spirit",     "spiritus",   "spiritus"),
    ("body",       "corpus",     "corporis"),
    ("mind",       "mens",       "mentis"),
    ("heart",      "cor",        "cordis"),
    ("hand",       "manus",      "manus"),
    ("eye",        "oculus",     "oculi"),
    ("mouth",      "os",         "oris"),
    ("head",       "caput",      "capitis"),
    ("god",        "deus",       "dei"),
    ("man",        "homo",       "hominis"),
    ("woman",      "femina",     "feminae"),
    ("child",      "puer",       "pueri"),
    ("tree",       "arbor",      "arboris"),
    ("house",      "domus",      "domus"),
    ("city",       "urbs",       "urbis"),
    ("law",        "lex",        "legis"),
    ("time",       "tempus",     "temporis"),
    ("place",      "locus",      "loci"),
    ("name",       "nomen",      "nominis"),
    ("book",       "liber",      "libri"),
    ("power",      "potestas",   "potestatis"),
    ("voice",      "vox",        "vocis"),
    ("begin",      "incipio",    "incipere"),
    ("make",       "facio",      "facere"),
    ("speak",      "dico",       "dicere"),
    ("write",      "scribo",     "scribere"),
    ("know",       "scio",       "scire"),
    ("see",        "video",      "videre"),
    ("give",       "do",         "dare"),
    ("take",       "capio",      "capere"),
    ("go",         "eo",         "ire"),
    ("come",       "venio",      "venire"),
    ("good",       "bonus",      "boni"),
    ("bad",        "malus",      "mali"),
    ("great",      "magnus",     "magni"),
    ("small",      "parvus",     "parvi"),
    ("new",        "novus",      "novi"),
    ("old",        "vetus",      "veteris"),
    ("holy",       "sanctus",    "sancti"),
    ("free",       "liber",      "liberi"),
]

# Hebrew-Latin semantic bridges (meaning-based, not phonetic)
HEBREW_LATIN = [
    # Hebrew word/root → Latin semantic equivalent
    ("melekh",  "rex"),       # king
    ("shalom",  "pax"),       # peace
    ("emet",    "veritas"),   # truth
    ("chokhma", "sapientia"), # wisdom
    ("chesed",  "amor"),      # loving-kindness/love
    ("din",     "lex"),       # judgment/law
    ("nefesh",  "anima"),     # soul
    ("ruach",   "spiritus"),  # spirit/wind
    ("neshamah","mens"),      # higher soul/mind
    ("or",      "lux"),       # light
    ("choshech","tenebrae"),  # darkness
    ("mayim",   "aqua"),      # water
    ("esh",     "ignis"),     # fire
    ("eretz",   "terra"),     # earth/land
    ("shamayim","aer"),       # heavens/sky/air
    ("chaim",   "vita"),      # life
    ("mavet",   "mors"),      # death
    ("yad",     "manus"),     # hand
    ("ayin",    "oculus"),    # eye
    ("peh",     "os"),        # mouth
    ("rosh",    "caput"),     # head
    ("lev",     "cor"),       # heart
    ("davar",   "verbum"),    # word/thing
    ("brit",    "foedus"),    # covenant
    ("bayit",   "domus"),     # house
    ("sefer",   "liber"),     # book/scroll
    ("koach",   "potestas"),  # power/strength
    ("kol",     "vox"),       # voice
    ("shem",    "nomen"),     # name
    ("av",      "pater"),     # father
    ("em",      "mater"),     # mother
    ("ben",     "filius"),    # son
    ("bat",     "filia"),     # daughter
    ("ish",     "homo"),      # man/person
    ("etz",     "arbor"),     # tree
]


def make_translation_documents(pairs: list, lang_a: str, lang_b: str,
                                 category: str) -> list:
    """Convert translation pairs into indexable document strings.
    Each entry creates a mutual definition: 'word_a is the [lang_a] word
    meaning [english_gloss]' so A-115 builds direct definition ties
    between the two words through shared meaning vocabulary."""
    docs = []
    for pair in pairs:
        if len(pair) == 3:
            en, native, translit = pair
            docs.append({
                "headword": en,
                "definition": f"{en} is expressed in {lang_b} as {translit} meaning {en}",
                "category": category,
            })
            docs.append({
                "headword": translit,
                "definition": f"{translit} is the {lang_b} word meaning {en}",
                "category": category,
            })
        elif len(pair) == 2:
            word_a, word_b = pair
            docs.append({
                "headword": word_a,
                "definition": (f"{word_a} in {lang_a} corresponds to {word_b} "
                               f"in {lang_b} sharing meaning"),
                "category": category,
            })
            docs.append({
                "headword": word_b,
                "definition": (f"{word_b} in {lang_b} corresponds to {word_a} "
                               f"in {lang_a} sharing meaning"),
                "category": category,
            })
    return docs
