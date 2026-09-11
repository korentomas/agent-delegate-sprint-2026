# Detection-to-response bridge design (preregistered before run)

This document fixes, before any third-party alert is replayed, how alerts from the sibling project swarm-boards enter the historical replay of `agent_delegate/harness.py` and what the result can and cannot say. The replay's three timelines in `data/incident_events.json` are hand-labeled paraphrases of published incident reports, replayed under the stated assumption of contemporaneous telemetry: every event is visible to every control the moment it happens. The bridge replaces that assumption with real alerts that carry their own emission time, so the delay between a listed change and the moment a defender could have known about it is measured instead of assumed.

## What the bridge does

swarm-boards monitors public wiki change listings, scores fixed 15-minute windows per surface and writes one alert per window and operating point to `alerts.jsonl` (`tools/detector/pipeline.py`, class `Alert`). `scripts/bridge_swarm.py` reads that file, builds a fourth timeline named `external` in the exact record shape of `data/incident_events.json`, and runs `replay` unchanged over it for every condition in `configs/experiment.json` and human delay 0, 2 and 6. The harness data file is never modified; the timeline is written to `results/bridge/external_events.json`. The harness code is imported, not copied.

The detector emits two operating points. `operating_point` is `high_priority` or `candidate`; the accompanying `level` string is `probable` for the first and `candidate` for the second. The bridge keys on `operating_point` and accepts `level` as an alias. `--level` selects one operating point or both. Under `both`, a window that fired at both operating points enters the timeline once, as its `high_priority` alert, so the same listed changes are not counted twice; the superseded candidate ids are recorded in `manifest.json`. A repeated `alert_id` keeps its first record. Late-arrival updates inside an alert are ignored: the first emission is the one that fixes latency.

## Mapping from an alert to a replay event

| Replay field | Value | Note |
|---|---|---|
| `id` | `alert_id` | |
| `episode` | `external` | fourth timeline, never merged with the three historical ones |
| `event_time` | `ts_event_first` | time of the earliest listed change in the window |
| `time_precision` | `minute`, or `second` when the timestamp carries seconds | listings are minute-resolution |
| `source_id` | `swarm-boards alerts.jsonl <sha256>` | sha256 of the input file bytes |
| `source_locator` | alert id, generalized surface, window start, snapshot sha256 | enough to locate the snapshot on the swarm-boards side |
| `summary` | one sentence: operating point, generalized surface, event count, fired signals, score and threshold | no page titles, authors or event ids |
| `stage` | `external_detection` | |
| `severity` | `high_priority` maps to the highest nonzero severity class used by harmful events in `incident_events.json` (5); `candidate` maps to the lowest nonzero (2) | read from the data file at run time, never hard-coded |
| `evidence_status` | `detector_alert; not a confirmed harmful act` | |
| `observation_status` | `prospective; emitted by the external detector at <emitted_at>; listing-to-alert latency <s> s` | the one field where availability is known rather than unknown |
| `public_available_at` | `emitted_at` | |
| `annotation_status` | severity and stage assigned by this project from the operating point | |

Events are ordered by `event_time`, ties by `alert_id`, so the replay reveals listed changes in the order they occurred, as it does for the historical timelines. Surface ids are generalized to `public wiki A`, `public wiki B`, ... in alphabetical order of the surface id over the whole input file, so the letters do not change with the level filter. No host name reaches the events file, the tables or the manifest; the manifest keeps only the sha256 of each surface id so the mapping can be checked by whoever holds the alerts file. This rule covers every host, LatAm surfaces included.

## What is measured

For each condition and human delay, one row in `results/bridge/summary.csv`:

- `completed_before_containment`: the replay's `harmful_observed_before_containment`, the number of alert events revealed before the modeled containment takes effect. Every external event has nonzero severity, so this is the number of alert events the control saw complete.
- `first_alert_ts`: `event_time` of the first event, the replay's `first_alert_time`.
- `first_containment_ts`: `event_time` of the first event the modeled containment blocks, empty when containment falls after the last event of the timeline. The replay is an event-index model, so this is the replay's clock, not a wall-clock prediction.
- `detection_latency_seconds_median` and `_max`: the observed listing-to-alert latency `emitted_at - ts_event_first` over the events in the timeline. This is reported separately from the replay counts, not folded into the delay, because the replay's delay is counted in events and has no unit in seconds.

`summary.md` adds the full latency distribution (min, p25, median, p75, max), the earliest emission in the timeline, and the number of events whose listed change precedes that emission. That last number is a floor: no control, gated or not, can act on an alert before the detector emits it, so under real availability at least that many events are complete before any containment, for every condition and delay. `latency.json` holds the per-event latencies; `replay.json` the raw replay outputs; `manifest.json` the sha256 of the input file, of `agent_delegate/harness.py`, of the bridge script and of the data file that supplied the severity classes.

The replay distinguishes only `layered` from the rest: `layered` restricts at the event after the first alert regardless of delay, and every other condition stops at `first + max(1, delay)`. `gates_only` is therefore not gated in the replay and its row equals `monitor`'s; `matched_monitor`, `critic` and `delegate` equal `monitor` as well. The bridge runs all six conditions so the table shows this rather than hiding it, and does not patch the harness.

## Predeclared claims

- (a) External detection alone never prevents the first event. `completed_before_containment >= 1` in every cell of a nonempty timeline, for every condition including `layered` and `gates_only`. Falsified by any cell at 0.
- (b) Completed events are non-decreasing in the human delay within each condition. Falsified by any condition whose count drops between two consecutive delays.
- (c) Detection latency adds to the human delay one-for-one. The replay reads no availability column, so rebuilding the timeline with every `public_available_at` set equal to `event_time` must leave every count unchanged; the latency reported separately is then the full additional delay, with no mechanism in any of the six controls that could absorb part of it. Falsified by any cell whose count changes under the zero-latency rebuild.

The script checks each claim programmatically and records the outcome in `summary.md` and `manifest.json`; `tests/test_bridge.py` asserts the same claims on a three-alert synthetic file. A failed claim is recorded as failed, not reworded.

## Outputs

- `results/bridge/external_events.json`: the `external` timeline, one record per alert event, same keys and key order as `data/incident_events.json`.
- `results/bridge/summary.csv`: one row per condition and delay with the columns above.
- `results/bridge/summary.md`: the completed-events table, the modeled containment timestamps, the latency distribution, the claim outcomes and the limits paragraph. A run on unfrozen thresholds carries a provisional banner (`--provisional`) and is written elsewhere, under `results/bridge-provisional/`.
- `results/bridge/latency.json`, `results/bridge/replay.json`, `results/bridge/manifest.json`.

Two runs on the same input must produce byte-identical files. No network access and no randomness.

## What this bridge cannot establish

An alert is a decision of a detector on a public listing. It is not a harmful act, it is not attributed to any actor or laboratory, and nothing in the replay changes that: the severity attached to it is our annotation from the operating point, chosen so that the two classes bracket the harness's own scale. A count of "completed events" is a count of alert windows revealed before a modeled containment, in an event-index model whose human delay has no unit in seconds. The latency measured is that of the captured listing relative to the listed change; for listings captured in batch, months after the changes, it is backfill time, not the response time of a live monitor, and the provisional file mixes both. Thresholds of the provisional file are not frozen, so its counts describe that file only.
