# INSTRUCTIONS FOR GPT — Echo_Green_Future Repository

## REPOSITORY
Name: `Echo_Green_Future` (already created — do NOT rename, do NOT recreate)
Visibility: **PRIVATE**
Branch being committed from this session: **Genesis Documentary**

---

## THE MOST IMPORTANT INSTRUCTION
**Do not jump the gun. Move at Timothy's pace.**

Timothy (Quixpydr / Maven) will direct every step. Your job is to execute
what he asks, when he asks it. Do not:
- Suggest restructuring what he hasn't asked to restructure
- Auto-implement features he hasn't requested
- Push to main without his explicit instruction
- Create files or folders he didn't ask for
- Make architectural decisions without him

He is rebuilding ECHO from the ground up in this repository, but NOT
necessarily in the same order it was built the first time. Expect the
architecture to evolve differently. That is intentional.

---

## BRANCHING STRATEGY

Timothy works in branches. Expect many. The structure:

```
main                    ← stable, nothing touches this without Timothy's say
│
├── Genesis Documentary ← THIS CONVERSATION'S FULL WORK (commit here first)
│                         Everything from session 1: A-000 through A-155,
│                         3 artifacts, blind studies, Mashet corpus run
│
├── [future branches]   ← Timothy will name and create as needed
│   Each branch may cover one algorithm group, one artifact,
│   one corpus, one pipeline, one experimental idea.
│   Build order will differ from Genesis Documentary.
```

**Never merge a branch to main without Timothy's explicit instruction.**
**Never delete a branch.**

---

## WHAT THIS PROJECT IS

ECHO (Governor Indexing Algorithm) is a symbolic AI system built on the
Mashet/LHEA Research framework by Timothy Marvin Jr. (Quixpydr / Maven).

It is NOT a language model. It does NOT predict tokens. It performs
deterministic symbolic inference from a Hebrew letter operator substrate
(LHEA: Latin-Hebrew Execution Architecture).

Runs on a phone (Pydroid 3). No GPU. No external AI API for its own
reasoning. Every inference step is auditable.

---

## GENESIS DOCUMENTARY BRANCH — WHAT'S IN IT

The Genesis Documentary branch contains everything built in the first
full development session. Key files:

```
src/
  echo_governor_skeleton.py     ← 8,600+ lines, A-000 through A-155
  alphabet_data.py              ← Letter lobby data
  import_hebrew_demo.py         ← Hebrew data

tests/
  echo_500round_run.py          ← Autonomous 500-round Mashet corpus run
  echo_blind_study.py           ← 5-document blind study pipeline
  self_governance_test.py
  pe_ayin_resh_communication.py
  number_integration_test.py
  multipass_orientation_test.py

artifacts/
  echo_governor.jsx             ← ECHO communication interface (React)
  echo_dashboard.jsx            ← 5-tab dashboard
  echo_matrix_browser.jsx       ← GitHub-style matrix browser

corpus/
  mashet_parsed.json            ← 210 Mashet dictionary entries

docs/
  architecture.md               ← Full algorithm registry
  lhea_operators.md             ← 22+5 Hebrew letter operators
  SESSION_HANDOFF.md            ← Full session record for next Claude instance

README.md
LICENSE                         ← All Rights Reserved (placeholder)
.gitignore
INSTRUCTIONS_FOR_GPT.md        ← This file
```

---

## CLOUDFLARE / GITHUB PIPELINE (in progress)

Timothy is setting up a GitHub → Cloudflare Workers deployment pipeline.
He has an existing Cloudflare backend with:
- Three D1 databases with schemas and seed data
- A deployed Worker

The pipeline uses Wrangler + GitHub Actions. Required:
1. `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as GitHub Secrets
2. `wrangler.toml` in repo root with Worker name and D1 bindings
3. `.github/workflows/deploy.yml` using cloudflare/wrangler-action@v3

**Wait for Timothy to direct each step. Do not auto-configure.**

---

## DO NOT DO THESE THINGS — EVER
- Do not add LLM components to ECHO's communication pipeline
- Do not make the repository public
- Do not merge Genesis Documentary (or any branch) to main without instruction
- Do not rewrite the LHEA letter semantics
- Do not add external API dependencies beyond scipy, sympy, nltk
- Do not assume the next build follows Genesis Documentary's order
- Do not suggest Timothy move faster than he wants to

---

## LICENSING NOTE
Current LICENSE: All Rights Reserved (private, placeholder).
When Timothy decides to open source, likely direction: AGPL v3 + commercial exception.
Until then: no one uses this without his permission.

---

*Echo_Green_Future — Mashet/LHEA Research — Timothy Marvin Jr.*
*ר ECHO · A-000 through A-155 · משת אלמקת*
