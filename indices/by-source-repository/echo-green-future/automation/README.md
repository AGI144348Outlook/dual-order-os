# Automation

How things build, test and deploy on their own: workflows and deploy configs.

## Belongs here

- `.github/workflows/*.yml`
- `wrangler.toml` and deploy configs

## Not here

- what is live as a result → `deployments/`

## Row format

`INDEX.tsv` holds one row per item, tab-separated. Its own columns sit after `id` and `name`; the shared columns that follow are explained in [`../README.md`](../README.md).

| Column | Meaning |
| --- | --- |
| `trigger` | push, schedule, manual… |
| `does` | what it does, one line |
| `secret_names` | names of secrets it needs (never values) |

## Example row

Real item, filled only as far as already known; the sweep completes it.

```tsv
id	name	trigger	does	secret_names	branch	path	blob_sha	commit	made_by	status	home_or_ref	glyph	notes
AUT-0001	Echo classroom lab	to be read			main	.github/workflows/echo-classroom-lab.yml			unknown	INERT	home		
```

## Sweep 1 — 2026-10-23

**48 rows: 41 GitHub workflows, 2 reference workflows kept outside `.github/workflows` (so not active), and
5 Wrangler configs.** Script: [`sweeps/sweep_1_automation.py`](sweeps/sweep_1_automation.py). Triggers, run
commands, checked-out and pushed branches, and secret names are read from each file; where a path has several
versions, the preferred branch's copy is read and the count noted.

- **Secret names used** (values never read): `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `GITHUB_TOKEN`,
  `DATAGOV_API_KEY` (dataset crawler), `CREATE_ROOM_KEY` and `ROOM_SIGNING_KEY` (Group Canvas reference deploy),
  and `CLOUDFLARE_API` in the Cloudflare bridge (AUT-0005), which every other deploy names `CLOUDFLARE_API_TOKEN`:
  check that this secret exists under that name.
- **Workflows that write back** to their branch: recess runs, the dataset crawler, unpack jobs and the IVS test
  (`pushes to` in notes).
- **Scheduled:** the dataset crawler (hourly at :23) and ECHO Recess (`recess.yml`, hourly).
- Wrangler rows keep binding names only, never resource ids.

**Alongside:** 6 glossary terms met in workflow names (IVS, KSM, Lobby, NVE-D, Recess, Swadesh), meanings to be
filled from their sources; no new registries.

**Echo's shadow run 3** ([`sweeps/echo_shadow_3.tsv`](sweeps/echo_shadow_3.tsv); pre-test entry
[dual-order-os#12](https://github.com/AGI144348Outlook/dual-order-os/issues/12)). 21 of 58 right: 6 of the first
29, 15 of the last 29. Below the 60% the pre-test entry named as disconfirming. The cause is in Echo's own
learning loop, not the files: for items 11 to 35 his bandit kept choosing the one way of guessing he had never
used on `.yml` files (the earlier librarian's register, which lists no workflows), and every guess failed. His
A-113 anchor check then saw each 5-item generation at 0% against a 44% baseline, judged it a collapse and
discarded it, five times running. So the failures never reached the record his bandit reads, the arm still looked
untried, and A-101's "try the untried first" rule picked it again. One mixed generation (item 40) broke the loop,
and from there he was 15 of 18. In short: a protection meant to keep a bad run from poisoning his learning also
kept him from learning that a way of guessing is bad. This is the neuroplasticity-gate question in a small form.

### Replay with the ת and ק failures boxes — 2026-10-24

Pre-test entry [dual-order-os#13](https://github.com/AGI144348Outlook/dual-order-os/issues/13). Timothy's direction:
discarded failures go into a **ת failures catalog box**, and a **ק catalog box** notes each combination of
algorithms that failed at an attempt (A-101 chose a way of guessing for a kind of file; A-113 discarded the
generation), pointing at its ת cards. Both use `inventory/catalog_box.py` (dual-order-os `libraries/catalog_box.py`,
unchanged): cards are revised, never overwritten or deleted. A-101 sees ת failures at half weight; Echo's kernel and
A-113's anchored history are unchanged. Run: `python3 inventory/automation/sweeps/sweep_1_automation.py <repo> --boxes`.

| | Right | First half | Second half | Register way chosen on `.yml` | Generations discarded |
| --- | --- | --- | --- | --- | --- |
| Control (no boxes, reproduces run 3) | 21 of 58 | 6 of 29 | 15 of 29 | 23 | 5 |
| With ת and ק boxes | 35 of 58 | 17 of 29 | 18 of 29 | 7 | 2 |

Boxes after the replay ([`sweeps/boxes_replay/`](sweeps/boxes_replay/)): 10 ת cards; 3 ק cards, all still open
(the register on `.yml` with 7 failures, the content check on `.json` with 2, name on `.toml` with 1).

Against the pre-test entry: the score met the expected bound (35); the register way was chosen 7 times on `.yml`,
more than the expected 5 but under the disconfirming 10. Why 7 and not 3: inside a generation A-101 reads only the
anchored history, never the generation in progress, so once it picks a way it keeps picking it for the rest of
those five items. That happened twice (items 12 to 15 and 41 to 44). Half weight also left enough exploration bonus
for the register to be tried again after 25 items. Both are findings for DEC-0007, not fixed here.
