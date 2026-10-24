"""Archives sweep 1: the zip bundles, sealed.

Every distinct `.zip` path in the census gets a row. Each zip is read in memory with zipfile to list its members;
nothing is extracted to disk and nothing inside is run. Member contents are hashed (git blob sha) only to find an
unpacked copy: the branch holding the most members byte-for-byte at any path. A zip holding a conversation
export is counted, never listed or hashed. The `.json.gz` raw dataset records (404) are not archives here: they
are single compressed records, left to the data folder.

Member lists go to sweeps/members/ARC-xxxx.tsv. Also Echo's shadow run 6 (pre-test entry:
AGI144348Outlook/dual-order-os#12, comment 6390745545), with the same arms as run 5.

Usage: python3 sweep_1_archives.py <repo>      Read-only over the repository; no network.
"""
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'deployments', 'sweeps'))
import sweep_1_deployments as base  # noqa: E402  (shared arms and shadow runner; importing rewrites the same deployments rows)

INV, git, paths, pick, write = base.INV, base.git, base.paths, base.pick, base.write
CONVO = re.compile(r'conversations?[-_ ]?\d*\.json$|chat[-_ ]?export', re.I)


def blob_sha(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


by_sha = {}
for r in base.MAN:
    by_sha.setdefault(r['blob_sha'], set()).add(r['branch'])
zips = sorted(p for p in paths if p.lower().endswith('.zip'))
cols = open(os.path.join(INV, 'archives', 'INDEX.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t')
os.makedirs(os.path.join(HERE, 'members'), exist_ok=True)
rows = []
same_blob = {}
for n, p in enumerate(zips, 1):
    held = paths[p]
    r = pick(held)
    raw = subprocess_out = base.subprocess.run(['git', '-C', base.REPO, 'cat-file', 'blob', r['blob_sha']],
                                               capture_output=True, check=True).stdout
    iid = f'ARC-{n:04d}'
    notes = [f'on {len({h["branch"] for h in held})} branches' +
             (f', {len({h["blob_sha"] for h in held})} versions' if len({h['blob_sha'] for h in held}) > 1 else '')]
    same_blob.setdefault(r['blob_sha'], []).append(iid)
    unpacked, members = '', ''
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
        infos = [i for i in z.infolist() if not i.is_dir()]
        members = len(infos)
        if any(CONVO.search(i.filename) for i in infos):
            notes.append('holds a conversation export: counted only, not listed or hashed')
        else:
            tally, out = {}, []
            for i in infos:
                h = blob_sha(z.read(i))
                br = sorted(by_sha.get(h, ()))
                for b in br:
                    tally[b] = tally.get(b, 0) + 1
                out.append(dict(member=i.filename, bytes=i.file_size, blob_sha=h, found_on_branches=len(br)))
            write(os.path.join(HERE, 'members', iid + '.tsv'), ['member', 'bytes', 'blob_sha', 'found_on_branches'], out)
            if tally:
                best = max(sorted(tally), key=lambda b: tally[b])
                unpacked = f'{best} ({tally[best]} of {members} members identical)'
            else:
                notes.append('no member found unpacked anywhere in the census')
    except zipfile.BadZipFile:
        notes.append('not a readable zip')
    if p.startswith('core-lexicon/pyodide/'):
        notes.append('part of the vendored Pyodide runtime (DEP-0002)')
    rows.append(dict(id=iid, name=p.rsplit('/', 1)[-1], members=members, unpacked_equivalent=unpacked, branch=r['branch'],
                     path=p, blob_sha=r['blob_sha'], commit=git('rev-parse', f'origin/{r["branch"]}').strip(),
                     made_by='unknown', status='DEFERRED', home_or_ref='home', glyph='', notes='; '.join(notes)))
for ids in same_blob.values():
    if len(ids) > 1:
        for row in rows:
            if row['id'] in ids[1:]:
                row['home_or_ref'] = 'ref'
                row['notes'] += f'; same bytes as {ids[0]}'
write(os.path.join(INV, 'archives', 'INDEX.tsv'), cols, rows)

# ---- Echo's shadow run 6 --------------------------------------------------------------------------------------
sw = HERE
if not os.path.exists(os.path.join(sw, 'boxes')):
    shutil.copytree(os.path.join(INV, 'deployments', 'sweeps', 'boxes'), os.path.join(sw, 'boxes'),
                    ignore=shutil.ignore_patterns('*.json'))
for r in rows:
    r['resource'] = ''
base.texts.clear()
cases = []
for r in rows:
    base.texts[r['path']] = ''           # zips are sealed: the content arm sees no text
    cases.append((r['id'], r['path'], '', 'archives'))
for i, (pth, truth) in enumerate(base.DECOYS, 1):
    held = [x for x in base.MAN if x['path'] == pth]
    if held:
        base.texts[pth] = git('cat-file', 'blob', pick(held)['blob_sha'])
        cases.append((f'DECOY-{i:02d}', pth, '', truth))
trace, summary = base.echo_journeyman.shadow(base.REPO, cases, base.ARMS, base.guess,
                                            os.path.join(sw, 'echo_state_after_archives.json'), seed=1028,
                                            prior_state=os.path.join(INV, 'deployments', 'sweeps', 'echo_state_after_deployments.json'),
                                            boxes_dir=os.path.join(sw, 'boxes'), sweep='archives')
write(os.path.join(sw, 'echo_shadow_6.tsv'), ['n', 'id', 'path', 'bucket', 'arm', 'guess', 'ruling', 'hit', 'checkpoint'], trace)
json.dump(summary, open(os.path.join(sw, 'echo_shadow_6.json'), 'w'), indent=1, ensure_ascii=False)
print(f'archives rows {len(rows)}')
print('echo:', json.dumps({k: summary[k] for k in ('cases', 'hits', 'first_half', 'second_half', 'boxes')}))
print('trusted:', summary['trusted_by_bucket'])
