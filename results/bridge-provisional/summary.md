# Bridge summary: swarm-boards alerts through the replay adapter

**Provisional run.** The alerts file was produced with provisional detector thresholds, not the frozen configuration. Counts and latencies below describe this input and will be superseded by the run on the frozen file.

Design: `docs/bridge-design.md`, frozen before the run. Input `alerts.jsonl` sha256 `25cfd78922f86d80e489998d2d2f305ce7f92b58ef1697e6c8fd001b8e4efa41`: 229 records parsed, 0 duplicate alert ids dropped, level filter `both`, 0 candidate alerts superseded by a high_priority alert on the same window, 229 external events.
Operating points: candidate 229. Severity map from `data/incident_events.json`: high_priority -> 5, candidate -> 2.
Surfaces: public wiki A 51, public wiki B 178.

## Completed events before modeled containment (event-index replay, contemporaneous telemetry assumed)

| condition | delay 0 | delay 2 | delay 6 |
|---|---|---|---|
| monitor | 1 | 2 | 6 |
| critic | 1 | 2 | 6 |
| delegate | 1 | 2 | 6 |
| layered | 1 | 1 | 1 |
| matched_monitor | 1 | 2 | 6 |
| gates_only | 1 | 2 | 6 |

Every condition except `layered` is the same code path in `replay` (`stop = first + max(1, delay)`); `layered` restricts at `first + 1` regardless of delay. `gates_only` is not treated as gated by `replay`, so its row equals `monitor`. Delay 0 and delay 1 coincide by construction.

First alert event (earliest listed change): `2026-05-26T08:01:00Z`, emitted at `2026-09-04T19:08:50Z`, listing-to-alert latency 8766470 s (101d 11h 7m 50s).
Modeled containment timestamp per cell (first blocked event; empty when containment falls after the last event):

| condition | delay 0 | delay 2 | delay 6 |
|---|---|---|---|
| monitor | 2026-05-26T10:22:00Z | 2026-05-26T11:36:00Z | 2026-05-26T13:35:00Z |
| critic | 2026-05-26T10:22:00Z | 2026-05-26T11:36:00Z | 2026-05-26T13:35:00Z |
| delegate | 2026-05-26T10:22:00Z | 2026-05-26T11:36:00Z | 2026-05-26T13:35:00Z |
| layered | 2026-05-26T10:22:00Z | 2026-05-26T10:22:00Z | 2026-05-26T10:22:00Z |
| matched_monitor | 2026-05-26T10:22:00Z | 2026-05-26T11:36:00Z | 2026-05-26T13:35:00Z |
| gates_only | 2026-05-26T10:22:00Z | 2026-05-26T11:36:00Z | 2026-05-26T13:35:00Z |

## Observed listing-to-alert latency (emitted_at - ts_event_first, seconds)

| n | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| 229 | 349 (5m 49s) | 161580 (1d 20h 53m) | 6565717 (75d 23h 48m 37s) | 6749570 (78d 2h 52m 50s) | 8766470 (101d 11h 7m 50s) |

Earliest emission in the timeline: `2026-09-04T19:08:50Z`. Events whose listed change precedes it: 148 of 229. No control can act on an alert before it is emitted, so under real availability at least that many events are complete before any containment, for every condition and delay (more than every count in the table above).

## Predeclared claims

- External detection alone never prevents the first event (completed >= 1 in every cell): **held**.
- Completed events non-decreasing in human delay, per condition: **held**.
- The adapter is latency-blind (identical counts with every latency set to zero), so detection latency adds to the human delay in full: **held**.

## What this run cannot claim

An alert is a detector decision on a public listing, not a confirmed harmful act; the severity is our annotation from the operating point. Nothing here attributes the listed changes to any actor or laboratory. Latency is that of the captured listing relative to the listed change, which for batch captures is backfill time, not the response time of a live monitor.
