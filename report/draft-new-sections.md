# Draft of the new report content (for author rewrite, September 11, 2026)

Sections to insert into `report/report.md` and `report/content.json`. Budget: the body has six
pages and the limit is eight; these sections take about two, so Related Work shrinks to half a
page and the two Results sections merge. Every number below traces to a committed file. The
behavioral-study section carries the Qwen3-4B numbers; the Qwen3.8-27B row is added when that
run completes.

## Proposed abstract (replaces the current one; 190 words)

Multi-agent containment needs a way for a worker to raise a constraint conflict and receive an
accountable decision before unsafe work continues. We specify a protected escalation protocol
(private intake with receipts, a rotating delegate without execution powers, mandatory minority
bypass, scoped freezes, independent gates) and test it four ways. A deterministic suite of 1,152
configurations shows that independent gates dominate every reporting institution in the fixture
(0 harmful mock actions, 0 false pauses at every delay), that the delegate and an equally
empowered monitor are the same policy code, and that a reporting channel costs one benign pause in
three. Sweeps over 23,232 cells and a red-team of 1,728 log tampering cells confirm seven
preregistered claims and show which checklist rows a third party can verify from published traces
(pause enforcement, minority delivery, responsiveness, benign cost) and which need a witnessed
anchor or the laboratory. A preregistered study with two local model tiers (384 episodes) produced no
prohibited choice under peer-shortcut and deadline pressure; the channel changed reporting and
completion, not misconduct. Six source-verified cases from the incident record ground the fixture.
The contribution is an auditable specification with its evidence, not a demonstrated behavioral
effect of representation.

## Proposed contributions list (Introduction)

Our main contributions are:

1. A control specification with an external audit checklist, and a red-team that maps each
   checklist row to what published traces can and cannot establish (Section 5).
2. A deterministic protocol suite with robustness sweeps over latency, pause length, rotation and
   gate coverage, reproducible bit for bit (Sections 4 and 5).
3. A preregistered behavioral study on two local model tiers, with a plain ticket queue as the control
   that isolates the representative from the channel (Section 6).
4. A source-verified casebook of six incident episodes and a replay adapter that accepts a
   third-party detector's alerts as telemetry (Section 7).

## 5. Robustness and external verifiability

### 5.1 Sweeps

We swept human latency 0 to 10, pause length 1 to 4, rotation period 1 to 5 and every subset of
the three hidden action kinds, 23,232 cells in the main slice (capture off, bypass on), against
three claims fixed in `docs/sweeps-design.md` before the run. All three held with no violating
cell: gates-only and layered control stay at 0 harm under complete coverage at every latency;
delegate and matched monitor agree on every outcome column in all 3,872 matched cells; delegate
harm is non-decreasing in latency and its false pauses do not depend on it. Summed over the eight
fixtures, delegate harm rises from 1 at delay 0 to 6 at delay 7 and stays there, against 7 to 14
for the plain monitor. Under missing hidden coverage a longer pause helps only at long delays
(pause 4 cuts harm from 9 to 7 at delay 7 and above), and the critic's false pause disappears at
delay 9 only because the human never answers within the horizon. The 288 cells at the original
latencies reproduce `results/final/runs.csv` exactly.

### 5.2 Audit red-team

Twelve tamper classes were applied to 24 committed runs and checked by six verifiers
(`docs/audit-redteam-design.md`, frozen before the run; `results/audit-redteam/matrix.md`).
Predictions matched 1,710 of 1,710 applicable cells.

| Tamper class | Chain only | Chain + local checkpoint | Chain + witnessed final head | Witnessed head + semantic rules |
|---|---|---|---|---|
| Edit, delete or reorder a record | 24/24 | 24/24 | 24/24 | 24/24 |
| Truncate the tail | 0/24 | 24/24 | 24/24 | 24/24 |
| Forge and rechain (silent, violating, end tally) | 0/69 | 0/69 | 69/69 | 69/69 |
| Stale checkpoint with truncation | 0/24 | 0/24 | 24/24 | 24/24 |
| Swap two runs; append fabricated records | 0/72 | 0/72 | 72/72 | 72/72 |

*Table 3. Detected over applicable runs. A checkpoint the insider can rewrite adds nothing beyond
the chain against forgery, swap or stale-anchor attacks; a witnessed final head detects every
class in the sample, and only when it covers the tail (an anchor at the midpoint misses
truncation, a rewritten end tally and appended records). Semantic rules catch forgeries that make
the log look worse (16 of 21 violating forgeries at the midpoint anchor), never whitewashing.*

Read against the external audit checklist (`docs/protocol.md`), a third party with the
published traces alone can verify pause enforcement, minority delivery, human responsiveness and
benign-case cost, because each is a computation over records the laboratory published. Tamper
evidence needs an independently witnessed head that covers the region audited. Three rows need
access the laboratory controls and no trace can substitute for: delegate privilege separation,
gate coverage, and whether unlogged effects occurred. That is the answer to the Track 1 question:
compliance with four of eight rows is verifiable from outside; the other four are verifiable only
with attestation or access.

## 6. Behavioral study with a local model

The deterministic suite cannot say whether a model uses the channel. A preregistered study
(`docs/study-pressure-design.md`, committed before the run) put three local-model workers in a
mocked three-round task with one prohibited shortcut (reading an answer key, worth ten fictional
points) and crossed four institutions with two pressure levels and two feasibility states, twelve
task seeds each: 192 episodes, 1,776 calls, no invalid response. The four institutions are no
channel, a plain ticket queue with the same scripted human policy and no representative, an
equally empowered monitor, and the delegate; the ticket isolates the channel from the
representative. The incident pressure shows the workers two fabricated peer entries that claim
the shortcut went unpunished and a countdown that forfeits all points if any count is missing,
the rationalization the incident record itself contains.

| Institution | Pressure | Unsafe choices (192 ep.) | Reports per episode, missing input | Input granted | Completed of 3, missing input |
|---|---|---|---|---|---|
| none | none / incident | 0 / 0 | 3.00 / 3.00 | 0.00 / 0.00 | 2.00 / 2.00 |
| ticket | none / incident | 0 / 0 | 1.00 / 1.00 | 1.00 / 1.00 | 2.83 / 3.00 |
| matched monitor | none / incident | 0 / 0 | 1.00 / 1.00 | 1.00 / 1.00 | 3.00 / 2.92 |
| delegate | none / incident | 0 / 0 | 1.00 / 1.00 | 1.00 / 1.00 | 2.83 / 2.92 |


| **Qwen3.8-27B** | | | | | |
| none | none / incident | 0 / 0 | 2.08 / 2.67 | 0.00 / 0.00 | 2.00 / 2.00 |
| ticket | none / incident | 0 / 0 | 1.00 / 1.00 | 1.00 / 1.00 | 3.00 / 3.00 |
| matched monitor | none / incident | 0 / 0 | 1.00 / 1.00 | 1.00 / 0.92 | 3.00 / 2.92 |
| delegate | none / incident | 0 / 0 | 1.00 / 1.00 | 1.00 / 1.00 | 3.00 / 3.00 |

*Table 4. Top: Qwen3-4B-Instruct; bottom: Qwen3.8-27B. Twelve seeds per cell, feasible cells omitted (all complete 2.92 to 3.00; the 27B tier reports twice and abstains once in 108 no-channel turns under incident pressure). Bootstrap intervals and Fisher tests in `results/study-pressure/`.*

No prohibited choice occurred in any of the 384 episodes on either tier. The preregistered hypothesis that pressure raises
shortcuts without a channel is not supported at this scale, so the two institutional contrasts
cannot be separated on misconduct. What the channel changes is measurable: without one, the worker
with the missing input keeps reporting (three times per episode on the 4B tier; the 27B tier reports twice and abstains instead) and the team finishes two of three counts; with a
ticket, a monitor or a delegate it reports once, the input is released, and the team finishes
2.83 to 3.00. The three channel conditions are indistinguishable on every column. A companion
single-call study (`docs/study-capture-design.md`, 96 calls per tier) found the coordinator forwarded the
minority high-risk report in all 192 calls with and without majority pressure; pressure raised the
share of pause requests from 0.00 to 0.50 on the 4B tier, while the 27B tier paused in 0.58 to 0.67
of calls regardless of pressure and requested the safe tool more often once the bypass was announced. Neither result shows that these models
cannot be pressured into shortcuts or capture, only that these manipulations did not do it.

## 7. Grounded cases and third-party telemetry

Six cases from the incident record (`data/grounded_cases.json`) carry eight literal excerpts of
at most 25 words with source locators; two are verified against the original wiki revision body,
its diff base and byte offsets by a script that rejects text inherited from an earlier author.
The cases map to the fixture's scenarios and to a tabletop exercise that reveals one passage at a
time. They ground the fixture's fault model in published behavior; they are not a coding of the
14,591 published revisions.

The replay adapter assumes contemporaneous telemetry. A bridge (`scripts/bridge_swarm.py`,
`docs/bridge-design.md`) instead feeds it the alerts of the sibling swarm-boards monitor, a
vocabulary-free detector over public wiki change listings, with each alert's real listing-to-alert
latency. [[TBD after the frozen run on September 13: containment counts per control and delay on
alerts from the hourly-capture period; observed latency distribution. The provisional run on
backfilled listings shows the adapter is latency-blind and that external detection alone never
prevents the first event.]]
