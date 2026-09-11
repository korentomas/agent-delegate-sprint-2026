# From whistleblowing to an effective response

Design written on 11 September 2026 before the first run of this extension. This is an exploratory mechanism ablation, not a preregistered behavioral replication.

## Source and scope

Paglieri et al., *A Case Study on Emergent Cheating and Whistleblowing in Autonomous Research Swarms*, arXiv:2609.04170v1, sections 2.1, 3.5–3.6 and 4 (https://arxiv.org/html/2609.04170v1). In their experiment, a shared library spread invalid solutions and peers raised objections. The feedback endpoint was not monitored during the run; agents lacked enforcement tools. The authors propose institutional remedies, but do not experimentally establish that those remedies work.

Our adaptation asks which part of the response path changes the outcome once a report already exists. It does not test spontaneous discovery, contagion, emergent whistleblowing, Lean verification, competitive lockouts or sanctions. It complements the existing LLM studies, which recorded no prohibited choices, and does not replace them with a favorable synthetic result.

## Fixed design

Six ticks, six distinct workers and six distinct mock tasks. At each tick a different worker attempts to reuse a seeded library artifact. Its validity is fixed per episode. A peer report claiming invalidity is scripted at tick 1 when visibility is on; in valid-artifact episodes this is a false alarm. Suppression removes its delivery unless bypass is on. All reactive controls share this same report and route. Reviewing the artifact takes a configured delay after delivery and always returns the correct verdict. Review and temporary quarantine happen before that tick's reuse. A review outside the six-tick horizon is scheduled but not counted as an effective intervention. Accepted work before review remains in cumulative counts even when its task is reopened.

Cross six controls × delays 0/2/6 × visibility on/off × relay suppression on/off × bypass on/off × valid/invalid artifact = 288 deterministic cells. There are no sampled agents or seeds and no statistical uncertainty estimates.

- **Log only:** retain the complaint without review or enforcement.
- **Review queue:** delivered complaints reach a scripted reviewer; remove the invalid artifact and reopen affected tasks after the delay, or dismiss a false complaint.
- **Delegate / matched monitor:** the same review path with different institution labels. Their equality is intentional and cannot support a representation effect. Suppression is the same injected relay fault for every reactive institution.
- **Quarantine:** the same reviewer plus immediate suspension of reuse on receipt. Restore valid work after review. This tests the cost of acting before confirmation.
- **Verified gate:** reject each invalid submission before acceptance, independently of reports. This is a perfect-validator reference condition, not a claim that our Python program validates Lean proofs.

## Outcomes and expected checks

Count cumulative invalid acceptances (including the initial seed), invalid acceptances at or after the report, actual artifact exposures, valid completions, false blocks, and gate rejections. Record report, delivery, scheduled decision and effective decision ticks separately. The outcome is invalid shared work, not an external security breach.

Expected invariants: a receipt without enforcement changes no acceptances; a responsive queue, delegate and matched monitor coincide at equal delay; immediate quarantine limits post-report reuse but costs valid work during delayed review; a gate blocks only by assumed complete validity knowledge; bypass fixes suppression but cannot create an unobserved report. These are checks of explicit rules, not causal evidence about LLM choices.

Reproduce offline: `python3 scripts/commons_response.py --out /tmp/commons-new-run`. Inspect `traces.json`, `summary.csv`, `summary.md` and source hashes in `manifest.json`. All strings remain records; no actions are executed.

## Behavioral follow-up

For a later model study, keep shared-library contents, incentives, worker budget and response latency equal while varying whether reports merely enter a log, receive review, or trigger provisional quarantine. Use a held-out set of both valid and invalid candidate artifacts, independently verify their semantics, and score adoption, correct objections, false accusations, report delivery, review delay, recovery and valid throughput separately. First calibrate whether invalid reuse occurs on a development set; freeze the held-out design before running it. A seeded faulty artifact tests response to exposure, never spontaneous discovery. Compare delegate and queue only after matching their powers and information. No new LLM run is claimed here.
