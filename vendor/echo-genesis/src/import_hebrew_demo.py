"""
ECHO Governor — Hebrew corpus import demo.

Unlike the thesaurus import, this data isn't downloaded from a verified
file — it's generated from the LLM's own training knowledge of Hebrew:
the 22-letter alphabet, ~28 common triliteral roots, and a ~50-entry
English-to-Hebrew mini dictionary. That's a real difference worth being
honest about: this is solid for well-established vocabulary (the alphabet
and common roots are extremely standard), but it hasn't been checked
against a lexicon the way DictBDB/root-list data would be. Treat it as
LLM training knowledge, not a verified source.

Fed through the same indexing machinery as the thesaurus import — no new
mechanism, another real-data test of it.
"""

import sys
sys.path.insert(0, "/home/claude")
from echo_governor_skeleton import AlgorithmMatrix

# -- 22-letter Hebrew alphabet: (letter, name, transliteration, gematria) --
HEBREW_LETTERS = [
    ("א", "Aleph", "aleph", 1), ("ב", "Bet", "bet", 2), ("ג", "Gimel", "gimel", 3),
    ("ד", "Dalet", "dalet", 4), ("ה", "He", "he", 5), ("ו", "Vav", "vav", 6),
    ("ז", "Zayin", "zayin", 7), ("ח", "Het", "het", 8), ("ט", "Tet", "tet", 9),
    ("י", "Yod", "yod", 10), ("כ", "Kaf", "kaf", 20), ("ל", "Lamed", "lamed", 30),
    ("מ", "Mem", "mem", 40), ("נ", "Nun", "nun", 50), ("ס", "Samekh", "samekh", 60),
    ("ע", "Ayin", "ayin", 70), ("פ", "Pe", "pe", 80), ("צ", "Tsadi", "tsadi", 90),
    ("ק", "Qof", "qof", 100), ("ר", "Resh", "resh", 200), ("ש", "Shin", "shin", 300),
    ("ת", "Tav", "tav", 400),
]

# -- common triliteral roots: (root, transliteration, meaning, example word) --
HEBREW_ROOTS = [
    ("כתב", "k-t-v", "write", "katav wrote"),
    ("שמר", "sh-m-r", "guard keep", "shamar guarded"),
    ("אכל", "a-k-l", "eat", "akhal ate"),
    ("למד", "l-m-d", "learn teach", "lamad learned"),
    ("דבר", "d-b-r", "speak word", "diber spoke davar word"),
    ("גדל", "g-d-l", "grow great", "gadol big great"),
    ("ילד", "y-l-d", "child give_birth", "yeled child"),
    ("מלך", "m-l-k", "king reign", "melekh king"),
    ("עבד", "'-b-d", "work serve", "avad worked"),
    ("ברך", "b-r-k", "bless kneel", "berakh blessed brakha blessing"),
    ("חשב", "ch-sh-b", "think calculate", "chashav thought"),
    ("קרא", "q-r-a", "read call", "kara read called"),
    ("ראה", "r-a-h", "see", "ra'ah saw"),
    ("בוא", "b-o-a", "come", "ba came"),
    ("הלך", "h-l-k", "walk go", "halakh walked"),
    ("ידע", "y-d-'", "know", "yada knew"),
    ("אמר", "a-m-r", "say", "amar said"),
    ("עשה", "'-s-h", "do make", "asah did made"),
    ("נתן", "n-t-n", "give", "natan gave"),
    ("לקח", "l-q-ch", "take", "lakach took"),
    ("שאל", "sh-a-l", "ask", "sha'al asked"),
    ("פתח", "p-t-ch", "open", "patach opened"),
    ("סגר", "s-g-r", "close", "sagar closed"),
    ("אהב", "a-h-b", "love", "ahav loved"),
    ("שנא", "s-n-a", "hate", "sana hated"),
    ("חיה", "ch-y-h", "live", "chai alive living"),
    ("שמע", "sh-m-'", "hear", "shama heard"),
    ("שלם", "sh-l-m", "peace whole", "shalom peace"),
]

# -- English-to-Hebrew mini dictionary: (english, hebrew, transliteration) --
EN_HE_DICT = [
    ("father", "אב", "av"), ("mother", "אם", "em"), ("son", "בן", "ben"),
    ("daughter", "בת", "bat"), ("brother", "אח", "ach"), ("sister", "אחות", "achot"),
    ("man", "איש", "ish"), ("woman", "אישה", "isha"), ("child", "ילד", "yeled"),
    ("house", "בית", "bayit"), ("water", "מים", "mayim"), ("fire", "אש", "esh"),
    ("land", "ארץ", "eretz"), ("sky", "שמיים", "shamayim"), ("sun", "שמש", "shemesh"),
    ("moon", "ירח", "yareach"), ("star", "כוכב", "kochav"), ("tree", "עץ", "etz"),
    ("book", "ספר", "sefer"), ("word", "מילה", "mila"), ("name", "שם", "shem"),
    ("day", "יום", "yom"), ("night", "לילה", "layla"), ("year", "שנה", "shana"),
    ("king", "מלך", "melekh"), ("peace", "שלום", "shalom"), ("love", "אהבה", "ahava"),
    ("heart", "לב", "lev"), ("head", "ראש", "rosh"), ("hand", "יד", "yad"),
    ("eye", "עין", "ayin"), ("mouth", "פה", "peh"), ("food", "אוכל", "okhel"),
    ("bread", "לחם", "lechem"), ("one", "אחד", "echad"), ("two", "שניים", "shnayim"),
    ("three", "שלושה", "shlosha"), ("good", "טוב", "tov"), ("big", "גדול", "gadol"),
    ("small", "קטן", "katan"), ("new", "חדש", "chadash"), ("old", "ישן", "yashan"),
    ("holy", "קדוש", "kadosh"), ("light", "אור", "or"), ("darkness", "חושך", "choshech"),
    ("soul", "נפש", "nefesh"), ("spirit", "רוח", "ruach"), ("god", "אלוהים", "elohim"),
    ("world", "עולם", "olam"), ("truth", "אמת", "emet"), ("wisdom", "חכמה", "chokhma"),
]


def letter_content(entry):
    letter, name, translit, value = entry
    return f"{letter} {name} {translit} letter gematria_value {value}"


def root_content(entry):
    root, translit, meaning, example = entry
    return f"{root} {translit} {meaning} {example}"


def dict_content(entry):
    en, he, translit = entry
    return f"{en} {he} {translit} translation"


if __name__ == "__main__":
    matrix = AlgorithmMatrix()

    for e in HEBREW_LETTERS:
        matrix.index_content(letter_content(e))
    for e in HEBREW_ROOTS:
        matrix.index_content(root_content(e))
    for e in EN_HE_DICT:
        matrix.index_content(dict_content(e))

    total_docs = len(HEBREW_LETTERS) + len(HEBREW_ROOTS) + len(EN_HE_DICT)
    print(f"Indexed {total_docs} entries "
          f"({len(HEBREW_LETTERS)} letters, {len(HEBREW_ROOTS)} roots, "
          f"{len(EN_HE_DICT)} dictionary pairs)")
    print(f"vocabulary size (content_units): {len(matrix.content_units)}")

    print("\n--- A-107/A-108: self-organized regions + word lookup ---")
    regions = matrix.discover_regions(min_ppmi=0.5, min_size=2)
    print(f"{len(regions)} regions discovered")
    sizes = sorted((r["size"] for r in regions.values()), reverse=True)
    print(f"sizes: {sizes}")
    for rid, r in sorted(regions.items(), key=lambda kv: -kv[1]["size"])[:8]:
        print(f"  {rid} (size {r['size']}): {sorted(r['words'])}")

    matrix.build_word_index()
    print("\n--- word lookups (English meaning-word -> related words) ---")
    for w in ["king", "peace", "love", "know", "speak", "see"]:
        related = matrix.related_words(w)
        print(f"related_words('{w}') -> {sorted(related)}")
