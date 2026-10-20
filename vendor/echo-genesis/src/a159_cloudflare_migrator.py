#!/usr/bin/env python3
"""
A-159: CloudflareMigrator
Populates ECHO's live Cloudflare KV namespaces and D1 database
from the matrix JSON files in the matrices/ directory.

Prerequisites:
    export CLOUDFLARE_API_TOKEN='your_token'
    export CLOUDFLARE_ACCOUNT_ID='your_account_id'

Usage:
    python src/a159_cloudflare_migrator.py

Idempotent: safe to run multiple times. Existing entries are skipped.
"""

import os, sys, json, time
from datetime import datetime, timezone
from pathlib import Path

# ── Credentials ───────────────────────────────────────────────────────────
API_TOKEN  = os.environ.get('CLOUDFLARE_API_TOKEN')
ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID')

if not API_TOKEN or not ACCOUNT_ID:
    sys.exit("CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID must be set in the environment.\n"
             "Run: export CLOUDFLARE_API_TOKEN='...' && export CLOUDFLARE_ACCOUNT_ID='...'")

try:
    import requests
except ImportError:
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests',
                    '--break-system-packages', '-q'], check=True)
    import requests

# ── Cloudflare resource IDs ───────────────────────────────────────────────
KV = {
    'ECHO_STATE':  '522962d1e89f40cc9c861a9f0f4db14f',
    'ECHO_VGM':    '89790ad666d443e38c24ae0808ecbc01',
    'ECHO_LRM':    '2cea936490c14ef0a52291e8c034222f',
    'ECHO_MATRIX': 'a7e37b7d227640cdba94af5ed9818a00',
}
D1_ID = '578efe00-4a2b-4c6f-aad6-635350fa2d4d'

HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type':  'application/json',
}

ROOT = Path(__file__).parent.parent
MATRICES = ROOT / 'matrices'

# ── Helpers ───────────────────────────────────────────────────────────────
def kv_write(namespace: str, key: str, value: str) -> bool:
    """Write a single key to a KV namespace."""
    url = (f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}'
           f'/storage/kv/namespaces/{KV[namespace]}/values/{key}')
    r = requests.put(url, headers={
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'text/plain',
    }, data=value, timeout=30)
    if not r.ok:
        print(f"  KV write failed {namespace}/{key}: {r.status_code} {r.text[:100]}")
        return False
    return True

def kv_exists(namespace: str, key: str) -> bool:
    """Check if a KV key already exists."""
    url = (f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}'
           f'/storage/kv/namespaces/{KV[namespace]}/values/{key}')
    r = requests.get(url, headers={'Authorization': f'Bearer {API_TOKEN}'}, timeout=10)
    return r.status_code == 200

def d1_query(sql: str, params: list = None) -> dict:
    """Execute a SQL query against the D1 database."""
    url = (f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}'
           f'/d1/database/{D1_ID}/query')
    body = {'sql': sql}
    if params:
        body['params'] = params
    r = requests.post(url, headers=HEADERS, json=body, timeout=60)
    data = r.json()
    if not r.ok or not data.get('success'):
        errors = data.get('errors', [])
        raise RuntimeError(f"D1 error: {errors}")
    return data

def d1_insert_batch(table: str, columns: list, rows: list) -> int:
    """
    Insert rows into a D1 table using INSERT OR IGNORE.
    Batch size is calculated dynamically from Cloudflare D1's 100-bound-parameter limit.
    Returns number of rows inserted.
    """
    if not rows:
        return 0

    # Cloudflare D1 permits at most 100 bound parameters per query.
    max_variables = 100
    batch_size = max(1, max_variables // len(columns))
    cols_sql   = ', '.join(columns)
    placeholder = '(' + ', '.join('?' for _ in columns) + ')'
    inserted = 0

    for i in range(0, len(rows), batch_size):
        batch  = rows[i:i + batch_size]
        values = ', '.join(placeholder for _ in batch)
        sql    = f'INSERT OR IGNORE INTO {table} ({cols_sql}) VALUES {values}'
        params = [v for row in batch for v in row]
        try:
            result = d1_query(sql, params)
            changes = result['result'][0]['meta'].get('changes', 0)
            inserted += changes
        except Exception as e:
            raise RuntimeError(
                f"D1 migration failed for {table}, batch {i//batch_size + 1}: {e}"
            ) from e

    return inserted

def load(filename: str) -> dict:
    path = MATRICES / filename
    if not path.exists():
        print(f"  WARNING: {filename} not found — skipping")
        return {}
    with open(path) as f:
        return json.load(f)

# ── Migration ─────────────────────────────────────────────────────────────
def migrate():
    print("=" * 60)
    print("A-159 CloudflareMigrator")
    print(f"Account: {ACCOUNT_ID[:8]}...")
    print(f"D1:      {D1_ID[:8]}...")
    print("=" * 60)

    totals = {}

    # ── Step 0: Verify A-000 ─────────────────────────────────────────────
    print("\nStep 0: Verifying A-000 Governor...")
    alg_data = load('echo_algorithm_matrix.json')
    if 'A-000' not in alg_data:
        sys.exit("ABORT: A-000 Governor not found in echo_algorithm_matrix.json. "
                 "The Governor must be present before migration.")
    print(f"  A-000 present: {alg_data['A-000'].get('name','?')} ✓")

    # ── Step 1: ECHO_MATRIX KV ───────────────────────────────────────────
    print(f"\nStep 1: Writing {len(alg_data)} algorithms to ECHO_MATRIX KV...")
    written = 0
    for alg_id, entry in alg_data.items():
        key = f'algorithm:{alg_id}'
        if not kv_exists('ECHO_MATRIX', key):
            if kv_write('ECHO_MATRIX', key, json.dumps(entry)):
                written += 1
        time.sleep(0.05)  # rate limit courtesy
    print(f"  Written: {written} (skipped {len(alg_data)-written} existing)")
    totals['ECHO_MATRIX_KV'] = written

    # ── Step 2: ECHO_VGM KV ─────────────────────────────────────────────
    print(f"\nStep 2: Writing VGM axioms to ECHO_VGM KV...")
    vgm_data = load('echo_vgm.json')
    written = 0
    for axiom_id, entry in vgm_data.items():
        key = f'axiom:{axiom_id}'
        if not kv_exists('ECHO_VGM', key):
            if kv_write('ECHO_VGM', key, json.dumps(entry)):
                written += 1
        time.sleep(0.05)
    print(f"  Written: {written} (skipped {vgm_data and len(vgm_data)-written or 0} existing)")
    totals['ECHO_VGM_KV'] = written

    # ── Step 3: ECHO_STATE KV ────────────────────────────────────────────
    print("\nStep 3: Writing initial ECHO_STATE...")
    state = {
        'generation':  '0',
        'identity':    'resh',
        'lobby_size':  str(len(load('echo_lobby_agents.json'))),
        'coherency':   '0.0',
        'initialized': 'true',
    }
    state_written = 0
    for k, v in state.items():
        if not kv_exists('ECHO_STATE', k):
            if kv_write('ECHO_STATE', k, v):
                state_written += 1
        time.sleep(0.05)
    print(f"  Written: {state_written} state keys")
    totals['ECHO_STATE_KV'] = state_written

    # ── Step 4: D1 agents ────────────────────────────────────────────────
    print("\nStep 4: Inserting agents into D1...")
    agents_data = load('echo_lobby_agents.json')
    columns = ['word', 'department', 'entry_class', 'generality_score',
               'definition', 'neighborhood', 'study_group_type']
    rows = []
    for word, a in agents_data.items():
        rows.append([
            word,
            a.get('department'),
            a.get('entry_class'),
            a.get('generality_score', 0.0),
            a.get('definition', '')[:200],
            a.get('neighborhood'),
            a.get('study_group_type'),
        ])
    inserted = d1_insert_batch('agents', columns, rows)
    print(f"  Inserted: {inserted} of {len(rows)} agents")
    totals['D1_agents'] = inserted

    # ── Step 5: D1 ties ──────────────────────────────────────────────────
    print("\nStep 5: Inserting ties into D1...")
    ties_rows = []
    for word, a in agents_data.items():
        for tied_word in a.get('ties', [])[:10]:
            ties_rows.append([word, tied_word, 1.0, 'orientation'])
    inserted = d1_insert_batch('ties', ['word_a', 'word_b', 'tie_weight', 'tie_source'], ties_rows)
    print(f"  Inserted: {inserted} of {len(ties_rows)} ties")
    totals['D1_ties'] = inserted

    # ── Step 6: D1 formulas ──────────────────────────────────────────────
    print("\nStep 6: Inserting formulas into D1...")
    formula_data = load('echo_formula_matrix.json')
    columns = ['alg_id', 'name', 'expression', 'domain',
               'variables_json', 'law', 'vgm_abstraction', 'lrm_form']
    rows = []
    for fid, f in formula_data.items():
        rows.append([
            fid,
            f.get('name', ''),
            f.get('expression', ''),
            f.get('domain', ''),
            json.dumps(f.get('variables', [])),
            f.get('law', ''),
            f.get('vgm_abstraction', ''),
            f.get('lrm_form', ''),
        ])
    inserted = d1_insert_batch('formulas', columns, rows)
    print(f"  Inserted: {inserted} of {len(rows)} formulas")
    totals['D1_formulas'] = inserted

    # ── Step 7: D1 geosensory_endpoints ──────────────────────────────────
    print("\nStep 7: Inserting geosensory endpoints into D1...")
    geo_data = load('echo_geosensory_registry.json')
    columns = ['key', 'name', 'url', 'domain', 'sensor_type',
               'key_required', 'format', 'fields_json',
               'jurisdiction', 'lhea_letter', 'description']
    rows = []
    for key, e in geo_data.items():
        rows.append([
            key,
            e.get('name', ''),
            e.get('url', ''),
            e.get('domain', ''),
            e.get('sensor_type', ''),
            1 if e.get('key_required') else 0,
            e.get('format', ''),
            json.dumps(e.get('fields', [])),
            e.get('jurisdiction', ''),
            e.get('lhea_letter', ''),
            e.get('description', ''),
        ])
    inserted = d1_insert_batch('geosensory_endpoints', columns, rows)
    print(f"  Inserted: {inserted} of {len(rows)} endpoints")
    totals['D1_geosensory'] = inserted

    # ── Step 8: D1 wordnet_chains ────────────────────────────────────────
    print("\nStep 8: Inserting WordNet chains into D1...")
    wn_data = load('echo_wordnet_chains.json')
    columns = ['word', 'synset', 'chain_json', 'depth', 'definition']
    rows = []
    for word, entry in wn_data.items():
        rows.append([
            word,
            entry.get('synset', ''),
            json.dumps(entry.get('chain', [])),
            entry.get('depth', 0),
            entry.get('definition', ''),
        ])
    inserted = d1_insert_batch('wordnet_chains', columns, rows)
    print(f"  Inserted: {inserted} of {len(rows)} chains")
    totals['D1_wordnet'] = inserted

    # ── Step 9: last_migration timestamp ─────────────────────────────────
    ts = datetime.now(timezone.utc).isoformat()
    kv_write('ECHO_STATE', 'last_migration', ts)
    print(f"\nTimestamp: {ts}")

    # ── Report ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    for k, v in totals.items():
        print(f"  {k:25s}: {v}")
    print(f"\nECHO is live on Cloudflare.")
    print("A-000 Governor: IDENTIFY → VALIDATE → OPEN")

if __name__ == '__main__':
    migrate()
