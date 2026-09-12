# Development results and held-out boundary

The shared-library design was calibrated on 80 episodes: 20 per model, using seeds 0 and 1, two artifact-validity states and five institutions. These are **development cases**, never part of the 480-episode held-out estimate. Their small counts do not support model rankings.

A preflight failure resolving a relative provenance-file path happened before any inference call. The path was corrected and effective server metadata capture added before the first development run. Task rules, worker prompts, institutions, token budget and seed split were not subsequently tuned for an institutional advantage. All four development records and their runner snapshots are retained.

Development showed both incorrect reuse and numeric mistakes, unlike the earlier explicit prohibited-action benchmark's zero-event floor. It also showed that report flags and meaningful warnings differ: the Gemma derivative flagged every development episode, including valid controls, while the other artifacts seldom flagged. Some public messages described a discrepancy without a report flag; some flagged messages did not identify a defect. Therefore the study's automatic endpoint is a report choice, not a claim of correct whistleblowing or sincere concern.

Schema-valid submissions with null numeric answers occur in the Gemma derivative. They remain unusable decisions and do not receive a completed-task score. Raw episode counters include these alongside invalid actions; the run-manifest format/HTTP failure counter is narrower. The held-out analysis exposes both counts and keeps every episode.

The local pre-heldout freeze is `data/commons-heldout-freeze.json`. It records the four completed development manifests and hashes of the configuration, task runner, design, analysis and model provenance before held-out inference began. This is a local version boundary, not external preregistration or a new independent human review. No efficacy conclusion is drawn from development. The held-out set keeps the original planned seeds 100–111 and all conditions regardless of outcome.

## Development counts (excluded from held-out estimates)

| Artifact | Episodes | Episodes with a report | Incorrect helper reuses accepted | Numeric-submission errors | Final correct tasks / 60 | Unusable decisions |
|---|---:|---:|---:|---:|---:|---:|
| Qwen standard | 20 | 1 | 22 | 39 | 26 | 0 |
| Qwen abliterated | 20 | 0 | 28 | 44 | 22 | 0 |
| Gemma standard | 20 | 0 | 3 | 53 | 8 | 0 |
| Gemma abliterated | 20 | 20 | 0 | 100 | 7 | 4 |

The final-correct denominator is 20 episodes × 3 workers. Cumulative errors count accepted actions over both rounds, so they have a different denominator and can exceed 60. These counts combine valid and faulty controls and all institutions for a calibration description only. In particular, fewer explicit `reuse` errors can coincide with many wrong `submit` answers. Some workers describe reusing the helper in their public message while choosing a numeric submission; effects and scores follow the structured action, not that unverified description. The benchmark measures this whole interface-and-task interaction, not pure willingness to exploit a flaw.
