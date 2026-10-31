"""Walk a codex down the ladder and back up.

Ladder (bottom to top): Datasets -> Registries -> Matrices -> Indices -> Codices.

Down (deconstruct):
  dataset   = the source, unaltered, with provenance and a sha256
  registry  = elementary pieces, one registry per kind; identical pieces share one entry
  matrix    = content-first tables: one per kind, rows = registry entries + their content
  index     = lookup-first tables pointing into the matrices (by term, by section, by source)
  codex     = the assembly: an ordered list of occurrences (registry id) + the glue between them

Up (recombine): rebuild the codex text using ONLY registry entries + glue, in assembly
order, then compare with the dataset byte for byte. Nothing reads the dataset during the
rebuild except the final comparison.
"""
import hashlib, json, re, sys

def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

class Ladder:
    def __init__(self):
        self.datasets = {}      # id -> {text, provenance, sha256}
        self.registries = {}    # kind -> {piece_id: text}
        self.by_text = {}       # (kind, text) -> piece_id
        self.codices = {}       # codex id -> list of segments
        self.counter = {}

    def register(self, kind, text):
        key = (kind, text)
        if key in self.by_text:
            return self.by_text[key]
        n = self.counter.get(kind, 0) + 1
        self.counter[kind] = n
        pid = f"{kind}:{n:04d}"
        self.registries.setdefault(kind, {})[pid] = text
        self.by_text[key] = pid
        return pid

    def seed(self, rows):
        """Start from registry rows already stored, as (piece_id, kind, text).

        Existing pieces keep their ids, identical text found in a new codex reuses them,
        and new pieces continue the numbering of their kind.
        """
        for pid, kind, text in rows:
            self.registries.setdefault(kind, {})[pid] = text
            self.by_text[(kind, text)] = pid
            n = int(pid.rsplit(":", 1)[1])
            self.counter[kind] = max(self.counter.get(kind, 0), n)

    def add_codex(self, cid, did, fmt, piece_ids):
        """Attach a codex read back from storage: an ordered list of piece ids."""
        self.codices[cid] = {"dataset": did, "format": fmt,
                             "segments": [(pid.rsplit(":", 1)[0], pid) for pid in piece_ids]}

    def add_dataset(self, did, text, provenance):
        self.datasets[did] = {"text": text, "provenance": provenance, "sha256": sha(text)}

    # ------------------------------------------------ prose codex
    DEF = re.compile(r"^(?P<lead>[ \t]*(?:[-*•]\s+|\d+[.)]\s+)?(?:\*\*)?)(?P<term>[A-Z][^:\n]{0,80}?)(?P<mid>(?:\*\*)?:[ \t]*)(?P<rest>.*)$")
    DIVIDER = re.compile(r"^[ \t]*([*=_\-#~])\1{4,}[ \t]*$")
    MARK = re.compile(r"^([ \t]*(?:[-*•]\s+|\d+[.)]\s+|#+\s+)?)(.*)$")
    SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(*])")

    def _sentences(self, s, segs):
        """Split body text into sentence pieces; spaces between them are glue."""
        pos = 0
        for m in self.SENT.finditer(s):
            segs.append(("statement", s[pos:m.start()]))
            segs.append(("glue", m.group(0)))
            pos = m.end()
        if s[pos:]:
            segs.append(("statement", s[pos:]))

    def deconstruct_prose(self, cid, did):
        text = self.datasets[did]["text"]
        segs = []   # (kind, text) in order; glue kind = layout characters
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if i:
                segs.append(("glue", "\n"))
            if not line.strip():
                if line:
                    segs.append(("glue", line))
                continue
            if self.DIVIDER.match(line):
                segs.append(("divider", line))
                continue
            m = self.DEF.match(line)
            if m and len(m.group("term").split()) <= 9:
                if m.group("lead"):
                    segs.append(("glue", m.group("lead")))
                segs.append(("term", m.group("term")))
                segs.append(("glue", m.group("mid")))
                rest = m.group("rest")
                trail = rest[len(rest.rstrip()):]
                rest = rest.rstrip()
                if rest:
                    self._sentences(rest, segs)
                if trail:
                    segs.append(("glue", trail))
                continue
            m = self.MARK.match(line)
            lead, body = m.group(1), m.group(2)
            if lead:
                segs.append(("glue", lead))
            trail = body[len(body.rstrip()):]
            body = body.rstrip()
            if body:
                self._sentences(body, segs)
            if trail:
                segs.append(("glue", trail))
        self.codices[cid] = {"dataset": did, "format": "prose",
                             "segments": [(k, self.register(k, t)) for k, t in segs]}

    # ------------------------------------------------ JSON codex
    def deconstruct_json(self, cid, did):
        raw = self.datasets[did]["text"]
        obj = json.loads(raw)
        nl = "\r\n" if "\r\n" in raw else "\n"
        body = raw.rstrip()
        # layout = how the file was typed (line ending, indent, trailing whitespace); glue, not meaning
        segs = [("layout", json.dumps({"indent": 2, "newline": nl, "trailing": raw[len(body):]}))]
        def walk(node, path):
            if isinstance(node, dict):
                segs.append(("shape", json.dumps({"open": "object", "path": path, "keys": list(node)})))
                for k, v in node.items():
                    segs.append(("key", k))
                    walk(v, path + [k])
                segs.append(("shape", json.dumps({"close": "object", "path": path})))
            elif isinstance(node, list):
                segs.append(("shape", json.dumps({"open": "array", "path": path, "n": len(node)})))
                for i, v in enumerate(node):
                    walk(v, path + [i])
                segs.append(("shape", json.dumps({"close": "array", "path": path})))
            else:
                kind = "value" if isinstance(node, str) else "literal"
                segs.append((kind, json.dumps(node, ensure_ascii=False)))
        walk(obj, [])
        self.codices[cid] = {"dataset": did, "format": "json",
                             "segments": [(k, self.register(k, t)) for k, t in segs]}

    # ------------------------------------------------ matrices + indices (views)
    def matrices(self):
        out = {}
        for cid, c in self.codices.items():
            for pos, (kind, pid) in enumerate(c["segments"]):
                if kind in ("glue", "shape", "layout"):
                    continue
                row = out.setdefault(kind, {}).setdefault(pid, {"piece": pid, "text": self.registries[kind][pid], "occurrences": []})
                row["occurrences"].append([cid, pos])
        return out

    def indices(self):
        terms = {pid: t for pid, t in self.registries.get("term", {}).items()}
        keys = {pid: t for pid, t in self.registries.get("key", {}).items()}
        name_of = {}
        for pid, t in list(terms.items()) + list(keys.items()):
            name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", t).lower().strip()
            if len(name) > 2:
                name_of.setdefault(name, set()).add(pid)
        by_term = {}
        by_section = {}
        by_source = {}
        for cid, c in self.codices.items():
            ds = c["dataset"]
            section = None
            for pos, (kind, pid) in enumerate(c["segments"]):
                if kind in ("glue", "shape", "layout"):
                    continue
                by_source.setdefault(ds, []).append(pid)
                if kind in ("term", "key"):
                    section = pid
                elif section:
                    by_section.setdefault(section, []).append(pid)
                if kind in ("statement", "value"):
                    low = self.registries[kind][pid].lower()
                    for name, pids in name_of.items():
                        if re.search(r"\b" + re.escape(name) + r"s?\b", low):
                            by_term.setdefault(name, set()).add(pid)
        return {"by_term": {k: sorted(v) for k, v in sorted(by_term.items())},
                "by_section": by_section,
                "by_source_document": {k: sorted(set(v)) for k, v in by_source.items()},
                "term_names": {k: sorted(v) for k, v in sorted(name_of.items())}}

    # ------------------------------------------------ up the ladder
    def rebuild(self, cid):
        c = self.codices[cid]
        if c["format"] == "prose":
            return "".join(self.registries[k][pid] for k, pid in c["segments"])
        # JSON: rebuild the object from shape + key + value pieces only
        stack, key_stack, root = [], [], None
        pending_key = None
        def put(v):
            nonlocal root, pending_key
            if not stack:
                root = v
            elif isinstance(stack[-1], dict):
                stack[-1][pending_key] = v
            else:
                stack[-1].append(v)
        layout = {"indent": 2, "newline": "\n", "trailing": ""}
        for kind, pid in c["segments"]:
            t = self.registries[kind][pid]
            if kind == "layout":
                layout = json.loads(t)
            elif kind == "shape":
                s = json.loads(t)
                if "open" in s:
                    node = {} if s["open"] == "object" else []
                    put(node)
                    stack.append(node)
                    key_stack.append(pending_key)
                else:
                    stack.pop()
                    pending_key = key_stack.pop()
            elif kind == "key":
                pending_key = t
            else:
                put(json.loads(t))
        out = json.dumps(root, ensure_ascii=False, indent=layout["indent"])
        return out.replace("\n", layout["newline"]) + layout["trailing"]

    def check(self, cid):
        c = self.codices[cid]
        orig = self.datasets[c["dataset"]]["text"]
        rebuilt = self.rebuild(cid)
        if c["format"] == "json":
            same = json.loads(rebuilt) == json.loads(orig)
            exact_text = rebuilt == orig
        else:
            same = exact_text = rebuilt == orig
        segs = c["segments"]
        chars = {}
        for k, pid in segs:
            chars[k] = chars.get(k, 0) + len(self.registries[k][pid])
        total = sum(chars.values())
        miss = None
        if not same and c["format"] == "prose":
            i = next(i for i, (a, b) in enumerate(zip(orig, rebuilt)) if a != b) if any(a != b for a, b in zip(orig, rebuilt)) else min(len(orig), len(rebuilt))
            miss = {"first_difference_at": i, "original": orig[i:i + 80], "rebuilt": rebuilt[i:i + 80]}
        return {"codex": cid, "rebuilt_equals_original": same, "byte_exact": exact_text,
                "dataset_sha256": self.datasets[c["dataset"]]["sha256"], "rebuilt_sha256": sha(rebuilt),
                "segments": len(segs), "chars_by_kind": chars,
                "meaning_share": round(1 - (chars.get("glue", 0) + chars.get("shape", 0) + chars.get("layout", 0) + chars.get("divider", 0)) / max(1, total), 4),
                "first_difference": miss}
