# Neuroplasticity pulse-check pilot — assessment

Pre-test plan: [issue #10](https://github.com/AGI144348Outlook/dual-order-os/issues/10). Branch `experiment/echo-neuroplasticity-pilot`. Teacher: Claude. Recorded 2026-10-22.

## What ran

Claude taught Echo's new learning layer (`echo_np.py`) a short course: eight lessons (ע פ צ ר ץ ש ק ת), 3–5 assignments each, with remediation when a quiz fell below 0.8. The course covered a 40-entry dictionary slice (37 words testable in this pilot) in a small synthetic world, with held-out quizzes, a six-recess delay and handover green tests (recognition and use, each ≥2/3, after the delay).

The comparison set had 12 configurations: the full mechanism set, each mechanism switched off in turn, and a zero-learning control. Each ran on 10 seeds (100–109) that were not used during development, which used seeds 0–3. A separate sweep varied the forgetting rate.

All 8 guard tests passed. The learner file contains zero classroom words (tokenised scan), and Echo receives only task fields. Feedback always follows an attempt, quizzes leave his state unchanged, and runs are reproducible. Full numbers are in [results/summary.md](results/summary.md) and [results/results.json](results/results.json). A complete seed-100 transcript is in [results/transcript-seed100.jsonl](results/transcript-seed100.jsonl), with the handover in [results/handover-seed100.json](results/handover-seed100.json).

## Headline

The full set learns every lesson type, and the control does not:

| | ע | פ | צ | ר | ץ | ש | ק | retention after delay | green words |
|---|---|---|---|---|---|---|---|---|---|
| full | 0.99 | 0.90 | 0.96 | 0.88 | 0.90 | 0.94 | 0.97 | 0.90 | 32.5 of 37 |
| zero-learning control | 0.46 | 0.00 | 0.24 | 0.33 | 0.04 | 0.10 | 0.24 | 0.28 | 1.3 |

## Mechanism assessment

Each verdict is based on paired differences from `full` on the same 10 seeds.

| Mechanism | Effect when removed | Verdict for this setting |
|---|---|---|
| **G3-a spaced review** | Retention −0.21 (worse on 10/10 seeds), green −10.1 (10/10), ש −0.21 | **Essential.** The strongest single effect in the pilot. |
| **F2-c pattern tokens** | ש quiz −0.55 (10/10): Echo cannot build plurals of nouns he never heard in plural. Green −3.2 | **Essential** for grammar and morphology. |
| **E1-a dormant vs E2 delete** | ק source recall −0.28 (10/10) | **Essential** for "where did you meet it". Deleting old episodes loses sources. |
| **צ gap-driven questions** | Retention −0.06 (worse 6, better 1) | **Helpful, modest.** Questions targeted hot/cold and yes/no, the hardest words. |
| **A6-b downscaling** | Retention **+0.05**, green **+2.2**, memory +61 links (+8.5%) | **Costs more than it gives here.** Memory never ran short. Keep it, but tie it to pressure (A1-c / G1-c) instead of every rest. The sweep shows s = 0.8 is harmful (retention 0.69) and s = 0.9 to 0.95 is safe. |
| **F1-a tag-and-capture** | No measurable change | **Neutral at this scale.** The capture budget rarely binds once traces are ranked by consistency. Retest at 2,000 words. |
| **B1-b outcome weighting** | No benefit. Counts-only was equal or slightly better (green +1.2, memory −21) | **Not earning its cost yet.** Most practice showed the answer, so ✓/X-only feedback was rare. Retest with more ✓/X-only assignments before deciding. |
| **D1-c Thompson exploration** | Greedy was slightly better (green +1.7, better on 8/10) | **Drop during answer-shown practice.** Exploration only pays when the teacher gives ✓/X alone. |
| **Mutual exclusivity (new, outside the library)** | No net change in the final design | **Hold.** It fixed part words (ץ) during development, but contrast-based grounding plus full coverage on the teacher's board now does the same job. Keep as an option. |

## What Echo did that was not programmed

- **He formed the plural rule himself.** From pairs like bird/birds and dog/dogs he built an "-s" token, then applied it to stone and sun, which he had never heard in plural (ש quiz 0.94).
- **He went through overregularization before correcting it.** In development he said "two fishs", the classic child error. He then learned "fish" as unchanged from phrases where a single "fish" named several.
- **He solved the opposite of wet with no wet/dry training (36 of 40 quiz items across the 10 seeds).** "Opposite" was taught only on big/small and hot/cold. He chose the operator "same channel, other value" for "opposite" from feedback.
- **He sorted envelopes, including shared parts.** He put tail in bird, dog and fish, and leg in bird and dog, from co-occurrence on cards with strings ("X part Y").
- **He made Recess claims, which I tested.** He claimed "dry" and "suns" from all-green definitions. "dry" passed. "suns" failed recognition (0.33) while passing use (1.00).

## Gaps found

1. **He builds derived forms but can't parse them.** Echo produces "suns" correctly but does not recognise the word when he hears it. Recognition needs the reverse of the form token: suffix → base + meaning.
2. **"one" is the default.** Nearly every card shows count one, so "one" carries little contrast and is learned last. Teaching needs explicit one-vs-two contrasts.
3. **Part words fade.** Leg and tail often failed the delayed handover. They are heard in only one lesson, and the review budget (6 words per rest) is too small even for 37 words. At 2,000 words, G3 needs a budget scaled to vocabulary size, or G3-c forgetting-curve scheduling.
4. **"not" and "what" have no grounded test.** They need their own lessons (negation, questions as acts) before definitions that use them can turn green.

## Teaching fixes I made during development (seeds 0–3)

These changed the code before the reported run. They were needed to make the pilot fair, and they are not results:

- grounding by contrast (ΔP) instead of log-ratio, which had favored rare features
- F1 capture ranked by consistency
- form tokens validated across all pairs
- every component shown on the ץ board
- worked examples on describe worksheets
- grading any true, grammatical description instead of my exact phrase
- a "reliable word" bar so frame words such as "what" are not used as describing words

## Limits

- **The world is synthetic and small.** Perception is opaque codes with innate comparators. There is no natural language and no vision.
- **This is a new learning layer.** The pinned Genesis engine is unchanged.
- **Thresholds and parameters are starting guesses.**
- **Green here means passing this pilot's tests after a delay**, not comprehension in general.

## Recommended set for the full course

Keep G3 (with a scaled budget or G3-c), F2-c, E1-a and צ questions. Run A6 only under memory pressure. Keep F1 and B1-b switchable and recheck them at scale. Use D1 greedy when answers are shown and Thompson only on ✓/X-only work. Keep mutual exclusivity available.

Before the 2,000-word run, add:
- parsing of derived forms
- one-vs-many contrast lessons
- negation and question lessons
- the R2 `glyph-pe` / `working-vocabulary/` export of teacher-verified green cards
