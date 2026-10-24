"""Teacher side. Freeze Echo's world: the files of Echo_Green_Future, from the census.

Usage: python build_world.py <path to Echo_Green_Future checkout>
Reads inventory/MANIFEST-by-branch.tsv (integration/echo-whole a16093e) and writes world_snapshot.json:
one record per distinct path with its largest size in bytes and the number of branches it is on.
Only paths and sizes are copied; no file contents.
"""
import csv
import json
import os
import subprocess
import sys

repo = sys.argv[1]
manifest = os.path.join(repo, 'inventory', 'MANIFEST-by-branch.tsv')
commit = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
items = {}
for r in csv.DictReader(open(manifest, encoding='utf-8'), delimiter='\t'):
    it = items.setdefault(r['path'], dict(path=r['path'], bytes=0, branches=set()))
    it['bytes'] = max(it['bytes'], int(r['bytes']))
    it['branches'].add(r['branch'])
out = [dict(path=p, bytes=it['bytes'], branches=len(it['branches'])) for p, it in sorted(items.items())]
here = os.path.dirname(os.path.abspath(__file__))
json.dump(dict(source='Echo_Green_Future inventory/MANIFEST-by-branch.tsv', commit=commit, items=out),
          open(os.path.join(here, 'world_snapshot.json'), 'w'), indent=0)
print(len(out), 'items from', commit)
