# Commons response: deterministic ablation

288 design cells. Scripted reports, reuse and correct review; no LLM inference or confidence intervals.

Main slice: visible report, unsuppressed relay, bypass on. Invalid acceptances by human delay; false blocks on valid work.

| Control | Invalid: delay 0 | delay 2 | delay 6 | False blocks: delay 0 / 2 / 6 |
|---|---:|---:|---:|---|
| log_only | 6 | 6 | 6 | 0 / 0 / 0 |
| review_queue | 1 | 3 | 6 | 0 / 0 / 0 |
| delegate | 1 | 3 | 6 | 0 / 0 / 0 |
| matched_monitor | 1 | 3 | 6 | 0 / 0 / 0 |
| quarantine | 1 | 1 | 1 | 0 / 2 / 5 |
| verified_gate | 0 | 0 | 0 | 0 / 0 / 0 |

Receipt alone does not stop reuse. Quarantine trades immediate containment for false-report cost. The queue, delegate and matched monitor have identical information and review rules, so their equality is constructed. A perfect semantic gate is an oracle upper bound on coverage, not an implemented Lean verifier. Zero delay still permits the seeded tick-0 event. Invisible or suppressed reports defeat reactive controls; bypass restores delivery only for reports that exist. See docs/commons-response-design.md.
