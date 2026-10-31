"""Load the datasets shelf into Neon, one rung at a time, and prove each load.

    python libraries/ladder_load.py              # needs NEON_DATABASE_URL
    python libraries/ladder_load.py --dry-run    # no database: deconstruct + rebuild only

For every entry in datasets/manifest.json:
  1. read the file exactly as stored (line endings included) and fingerprint it
  2. already in Neon with the same fingerprint -> skip; same id, different fingerprint -> stop
  3. break it into registry pieces, starting from the pieces Neon already has, so identical
     pieces reuse their ids and new ones continue the numbering
  4. rebuild it from the pieces alone; not byte-exact -> stop, nothing is written
  5. inside one transaction: insert the dataset, the new pieces, the codex, its segments
     and its index terms, then read the codex back out of Neon, rebuild it from what Neon
     returned, and commit only if that rebuild is byte-exact too
Every run writes a findings report (repeated pieces, likely labels, links to other codices)
for a person to review. The loader never changes or removes a row.
"""
import argparse, json, os, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ladder import Ladder, sha

ROOT = Path(__file__).resolve().parents[1]
MEANING = ("term", "statement", "key", "value", "literal")


def log(msg):
    print(msg, flush=True)


def read_manifest(root=ROOT):
    m = json.loads((root / "datasets" / "manifest.json").read_text(encoding="utf-8"))
    for e in m["datasets"]:
        with open(root / "datasets" / e["file"], encoding="utf-8", newline="") as f:
            e["text"] = f.read()
        e["sha256"] = sha(e["text"])
    return m["datasets"]


def deconstruct(L, e):
    L.add_dataset(e["id"], e["text"], e["provenance"])
    if e["format"] == "prose":
        L.deconstruct_prose(e["codex"], e["id"])
    else:
        L.deconstruct_json(e["codex"], e["id"])
    return L.check(e["codex"])


def findings(L, e, before, shared_names):
    """What a reviewer should look at. These are pointers, not conclusions."""
    segs = L.codices[e["codex"]]["segments"]
    counts = Counter(pid for k, pid in segs if k in MEANING)
    text = lambda pid: L.registries[pid.rsplit(":", 1)[0]][pid]
    short = lambda s: (s[:90] + "…") if len(s) > 90 else s
    out = [f"### {e['codex']}  ({e['id']})", ""]
    rep = [(pid, n) for pid, n in counts.most_common() if n > 1 and pid.startswith(("statement", "value"))]
    out.append(f"**Repeated passages** ({len(rep)}): the same sentence appears more than once.")
    out += [f"- ×{n} `{pid}` {short(text(pid))}" for pid, n in rep[:15]] or ["- none"]
    lab = [(pid, n) for pid, n in counts.most_common() if n >= 3 and pid.startswith(("term", "key"))]
    out += ["", f"**Possible labels** ({len(lab)}): headings used 3+ times may be labels (like Purpose) rather than concepts."]
    out += [f"- ×{n} `{pid}` {short(text(pid))}" for pid, n in lab[:15]] or ["- none"]
    reused = sorted({pid for k, pid in segs if k in MEANING and pid in before})
    out += ["", f"**Pieces already in the registry from other codices** ({len(reused)})"]
    out += [f"- `{pid}` {short(text(pid))}" for pid in reused[:15]] or ["- none"]
    out += ["", f"**Terms this codex shares with other codices** ({len(shared_names)})"]
    out += ["- " + ", ".join(shared_names)] if shared_names else ["- none"]
    return out + [""]


def term_index(L):
    """Which term names each sentence mentions, across the whole registry.

    Run over every stored piece, not just the new codex, so a term that first appears in
    a new codex is also found in sentences of codices loaded earlier.
    """
    names = L.indices()["term_names"]
    out = []
    for kind in ("statement", "value"):
        for pid, t in L.registries.get(kind, {}).items():
            low = t.lower()
            out += [(n, pid) for n in names if re.search(r"\b" + re.escape(n) + r"s?\b", low)]
    return out


def report_line(c):
    return (f"rebuilt byte-exact: {c['byte_exact']} | segments {c['segments']} | "
            f"meaning share {c['meaning_share']} | sha256 {c['dataset_sha256'][:16]}")


def load(conn, entries):
    """Returns (findings lines, ok)."""
    lines, ok = [], True
    with conn.cursor() as cur:
        cur.execute("select id, sha256 from ladder.dataset")
        stored = dict(cur.fetchall())
    for e in entries:
        log(f"\n== {e['id']}  ({e['file']}, {len(e['text'])} chars)")
        if e["id"] in stored:
            if stored[e["id"]] == e["sha256"]:
                log("already in Neon with the same fingerprint: skipped")
                continue
            log(f"STOP: Neon holds {e['id']} with a different fingerprint ({stored[e['id']][:16]}). "
                "Rows are never replaced; give the new version a new id.")
            ok = False
            continue
        try:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute("select piece_id, kind, text from ladder.registry")
                    rows = cur.fetchall()
                    L = Ladder()
                    L.seed(rows)
                    before = {r[0] for r in rows}
                    c = deconstruct(L, e)
                    log("local " + report_line(c))
                    if not c["byte_exact"]:
                        log(f"STOP: rebuild differs at {c['first_difference']}. Nothing written.")
                        ok = False
                        continue
                    segs = L.codices[e["codex"]]["segments"]
                    new = sorted({pid for _, pid in segs if pid not in before})
                    cur.execute("insert into ladder.dataset (id, provenance, sha256, chars, text) values (%s, %s, %s, %s, %s)",
                                (e["id"], json.dumps(e["provenance"]), e["sha256"], len(e["text"]), e["text"]))
                    cur.executemany("insert into ladder.registry (piece_id, kind, text) values (%s, %s, %s)",
                                    [(pid, pid.rsplit(":", 1)[0], L.registries[pid.rsplit(":", 1)[0]][pid]) for pid in new])
                    cur.execute("insert into ladder.codex (id, dataset_id, format) values (%s, %s, %s)",
                                (e["codex"], e["id"], e["format"]))
                    cur.executemany("insert into ladder.codex_segment (codex_id, pos, piece_id) values (%s, %s, %s)",
                                    [(e["codex"], i, pid) for i, (_, pid) in enumerate(segs)])
                    idx = term_index(L)
                    cur.executemany("insert into ladder.index_term (name, piece_id) values (%s, %s) on conflict do nothing", idx)
                    log(f"inserted: 1 dataset, {len(new)} new pieces ({len(set(p for _, p in segs)) - len(new)} reused), "
                        f"1 codex, {len(segs)} segments, {len(idx)} index terms (whole registry; existing ones skipped)")
                    # climb back up from what Neon now holds, not from memory
                    cur.execute("""select s.piece_id, r.kind, r.text from ladder.codex_segment s
                                   join ladder.registry r using (piece_id) where s.codex_id = %s order by s.pos""", (e["codex"],))
                    back = cur.fetchall()
                    cur.execute("select text, sha256 from ladder.dataset where id = %s", (e["id"],))
                    dtext, dsha = cur.fetchone()
                    R = Ladder()
                    R.seed({(p, k, t) for p, k, t in back})
                    R.add_dataset(e["id"], dtext, e["provenance"])
                    R.add_codex(e["codex"], e["id"], e["format"], [p for p, _, _ in back])
                    rebuilt = R.rebuild(e["codex"])
                    if sha(rebuilt) != e["sha256"] or dsha != e["sha256"]:
                        log("STOP: the copy read back from Neon does not rebuild byte-exact. Rolled back, nothing kept.")
                        raise RollbackOnly()
                    cur.execute("""select distinct i.name from ladder.index_term i
                                   join ladder.codex_segment s using (piece_id)
                                   where s.codex_id <> %s and i.name in
                                     (select i2.name from ladder.index_term i2 join ladder.codex_segment s2 using (piece_id)
                                      where s2.codex_id = %s) order by 1""", (e["codex"], e["codex"]))
                    shared = [r[0] for r in cur.fetchall()]
                    log("read back from Neon and rebuilt byte-exact: committed")
                    lines += findings(L, e, before, shared)
        except RollbackOnly:
            ok = False
    return lines, ok


class RollbackOnly(Exception):
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="no database: deconstruct and rebuild only")
    ap.add_argument("--findings", default="ladder-findings.md")
    a = ap.parse_args()
    entries = read_manifest()
    lines, ok = ["## Ladder run", ""], True
    if a.dry_run:
        for e in entries:
            L = Ladder()
            c = deconstruct(L, e)
            log(f"{e['id']}: " + report_line(c))
            ok &= c["byte_exact"]
            lines += findings(L, e, set(), [])
    else:
        url = os.environ.get("NEON_DATABASE_URL")
        if not url:
            log("NEON_DATABASE_URL is not set: nothing to load into. Use --dry-run to check rebuilds only.")
            return 2
        import psycopg
        with psycopg.connect(url) as conn:
            got, ok = load(conn, entries)
            lines += got or ["Nothing new was loaded."]
    Path(a.findings).write_text("\n".join(lines) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    log(f"\nfindings written to {a.findings}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
