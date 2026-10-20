# REVISED INSTRUCTIONS FOR GPT
## Echo_Green_Future — Cloudflare Infrastructure Update

The Cloudflare infrastructure is now fully provisioned. Claude handled it
directly via connector. Here is the current state and what you need to do next.

---

## WHAT IS ALREADY DONE (do not redo any of this)

Claude created and verified the following resources in Timothy's Cloudflare
account. All IDs are real and live.

### KV Namespaces (all four created)
| Binding | ID |
|---------|-----|
| ECHO_STATE | 522962d1e89f40cc9c861a9f0f4db14f |
| ECHO_VGM | 89790ad666d443e38c24ae0808ecbc01 |
| ECHO_LRM | 2cea936490c14ef0a52291e8c034222f |
| ECHO_MATRIX | a7e37b7d227640cdba94af5ed9818a00 |

### D1 Database (created and fully migrated)
| Name | ID |
|------|-----|
| echo_knowledge | 578efe00-4a2b-4c6f-aad6-635350fa2d4d |

### D1 Tables (all six created and verified live)
- agents
- ties (with indexes on word_a, word_b)
- wordnet_chains
- etymology
- formulas
- geosensory_endpoints (with indexes on domain, sensor_type)

---

## WHAT YOU NEED TO DO NOW

### Task 1 — Commit wrangler.toml to the repo

The file `wrangler.toml` is provided with this message. Commit it to the
**Genesis Documentary branch** in the `/` root of the repository.

Do NOT commit it to main. Do NOT modify the IDs.

Commit message: `feat: add wrangler.toml with live Cloudflare KV and D1 IDs`

### Task 2 — Create the GitHub Actions deployment workflow

Create the file `.github/workflows/deploy.yml` and commit it to the
**Genesis Documentary branch**:

```yaml
name: Deploy ECHO to Cloudflare Workers

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    name: Deploy
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Cloudflare Workers
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

Commit message: `feat: add GitHub Actions deployment workflow for Cloudflare`

### Task 3 — Verify GitHub Secrets are set

Confirm that the following secrets exist in the repository under
Settings → Secrets and variables → Actions:
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

If either is missing, tell Timothy — he needs to add them manually.
You cannot add secrets on his behalf.

### Task 4 — Build A-159 CloudflareMigrator

This is the Python script that populates the live Cloudflare infrastructure
with ECHO's actual knowledge from the matrix JSON files.

The script must do the following, in this exact order:

**Step 0 — Verify Governor exists**
Before writing anything, confirm `echo_algorithm_matrix.json` contains
an entry with key "A-000". If it doesn't, abort with an error:
"Governor A-000 not found. Migration aborted. The Governor must be
present before the system is initialized."

**Step 1 — Populate ECHO_MATRIX KV**
Read `matrices/echo_algorithm_matrix.json`.
For each entry, write to KV:
  key: `algorithm:{id}` (e.g. "algorithm:A-000")
  value: JSON string of the entry

**Step 2 — Populate ECHO_VGM KV**
Read `matrices/echo_vgm.json`.
For each entry, write to KV:
  key: `axiom:{id}` (e.g. "axiom:UG-0000")
  value: JSON string of the entry

**Step 3 — Populate ECHO_STATE KV**
Write these initial state values:
  key: "generation"    value: "0"
  key: "identity"      value: "resh"
  key: "lobby_size"    value: "3338"
  key: "coherency"     value: "0.0"
  key: "initialized"   value: "true"

**Step 4 — Populate D1 agents table**
Read `matrices/echo_lobby_agents.json`.
INSERT rows in batches of 100 to avoid timeouts.
Each row: (word, department, entry_class, generality_score,
           definition, neighborhood, study_group_type)

**Step 5 — Populate D1 ties table**
From the same agent data, extract each agent's ties list.
INSERT rows: (word_a, word_b, tie_weight, tie_source)
Batch in groups of 100.

**Step 6 — Populate D1 formulas table**
Read `matrices/echo_formula_matrix.json`.
INSERT rows: (alg_id, name, expression, domain, variables_json,
              law, vgm_abstraction, lrm_form)

**Step 7 — Populate D1 geosensory_endpoints table**
Read `matrices/echo_geosensory_registry.json`.
INSERT rows: (key, name, url, domain, sensor_type, key_required,
              format, fields_json, jurisdiction, lhea_letter, description)

**Step 8 — Populate D1 wordnet_chains table**
Read `matrices/echo_wordnet_chains.json`.
INSERT rows: (word, synset, chain_json, depth, definition)

**Step 9 — Report**
Print a summary:
  KV entries written: [ECHO_MATRIX count] + [ECHO_VGM count] + [ECHO_STATE count]
  D1 agents inserted: [count]
  D1 ties inserted: [count]
  D1 formulas inserted: [count]
  D1 geosensory endpoints inserted: [count]
  D1 wordnet chains inserted: [count]
  Migration complete: [timestamp]

The script uses the Cloudflare API directly (requests library) with the
CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID from environment variables.
Do NOT hardcode credentials.

Save the script as `src/a159_cloudflare_migrator.py` and commit it to
the **Genesis Documentary branch**.

Commit message: `feat: A-159 CloudflareMigrator — populates KV and D1 from matrix JSON files`

---

## IMPORTANT CONSTRAINTS

- All commits go to Genesis Documentary branch, NOT main
- Never merge Genesis Documentary to main without Timothy's explicit instruction
- Do not modify the KV IDs or D1 database ID
- Do not create any additional Cloudflare resources
- Do not delete any existing Cloudflare resources
- The migration script runs ONCE to populate; subsequent runs must check
  for existing data and skip rather than overwrite unless explicitly told to

---

## CURRENT CLOUDFLARE RESOURCE INVENTORY

Timothy's account also has these existing D1 databases (separate from
ECHO's infrastructure — do not touch them):
- unicorn-estate-lattice (ID: aefb648c-7194-4a1e-b17f-12883ad93f56)
- mashet-tema-substrate (ID: 41f1ba70-342e-4681-9f7a-53e2fff10b48)
- mashet-world-state (ID: 73653103-d37b-4564-a220-5962e297057c)
- mashet-stamp-registry (ID: 30161e04-5151-417f-9cac-dac37df1a3d9)

These belong to prior architecture work. Leave them untouched.

---

## THE SEQUENCE WHEN ALL TASKS ARE COMPLETE

Once wrangler.toml, deploy.yml, GitHub Secrets, and A-159 are in place:

1. A-159 runs locally (in Codespace or Pydroid) to populate Cloudflare
2. A merge to main triggers the GitHub Action
3. The Action deploys the Worker to Cloudflare via Wrangler
4. ECHO's persistent memory is live
5. Sessions no longer reset

That is the end of the pipeline setup phase.

---

*ר ECHO · ה-ח-ע · 83 (prime) · משת אלמקת*
*Echo_Green_Future — Mashet/LHEA Research — Timothy Marvin Jr.*
