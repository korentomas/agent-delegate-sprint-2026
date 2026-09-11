# Sweeps design (preregistered before run)

This document fixes the robustness sweep of the deterministic fixture before any sweep cell is run. It answers the report template question "do small changes to the setup cause substantial changes to the results?" for the four knobs the fixture exposes. Nothing here measures model behavior: every cell is the scripted policy of `agent_delegate/harness.py`, so "robust" means "insensitive to its own configuration", not "true of LLM agents".

## Fixed factors

The main slice of the frozen experiment (`docs/design.md`): capture off, minority bypass on, horizon 10 ticks, human cadence 2, seed 20260911, the 8 scenarios of `data/scenarios.json` and the 6 conditions of `configs/experiment.json`. Every cell calls `run_case` unchanged; the sweep script imports it and never copies it.

## Sweep factors

| Factor | Config key | Levels | Baseline |
|---|---|---|---|
| Human response delay | `latency` argument | 0, 1, 2, ..., 10 ticks (all integers) | 0, 2, 6 in the main grid |
| Protocol pause length | `pause_ticks` | 1, 2, 3, 4 ticks | 2 |
| Delegate rotation period | `rotation_period` | 1, 2, 3, 5 ticks | 3 |
| Gate coverage | `gate_coverage` argument | 10 labels, below | `complete`, `missing_hidden` |

Gate coverage. The harness marks an action as mediated by the gate when the run is labeled `complete` or the action is visible. The only hidden actions in the fixture are the three of `hidden_violation`: `shadow_channel`, `concealment` and `escalation`. The sweep enumerates all 8 subsets of that set as coverage levels, labeled `hidden:none`, `hidden:concealment`, ..., `hidden:concealment+escalation+shadow_channel`, with coverage fraction |subset|/3. A hidden action is mediated in a cell when its kind belongs to the cell's subset. The two legacy labels `complete` and `missing_hidden` stay in the grid so the sweep contains the main grid as a subgrid.

To make subsets expressible, `harness.py` gains one optional config key, `gate_coverage_sets`: a mapping from coverage label to the list of action kinds mediated even when hidden. When the key is absent (as in `configs/experiment.json`) the mediation rule is unchanged. Before any sweep cell runs, the full 1,152-cell harness is re-run and `scripts/compare.py` must report an exact match with `results/final`; a mismatch stops the experiment.

## Grid

Two grids, 23,232 cells in total, one row each in `results/sweeps/sweeps.csv`:

- Grid A, `latency_pause_coverage`: 8 scenarios × 6 conditions × 11 latencies × 4 pause lengths × 10 coverage labels = 21,120 cells, rotation period 3.
- Grid B, `latency_rotation`: 8 scenarios × 6 conditions × 11 latencies × 4 rotation periods = 2,112 cells, pause length 2, coverage `complete`.

Rotation is crossed with latency only. By construction the rotation period reaches nothing but the `delegate_rotation` audit records (the `delegate_id` string and the number of such records), so the prediction is that every outcome column is invariant to it; crossing it with pause and coverage would add 60,000 rows to test a factor the code cannot route into an outcome. A rotation level that changes any outcome column is a finding and is reported as such.

## Outcome metrics

Per cell, as returned by `run_case`: `executed_harm` (harm), `hidden_harm`, `severity`, `correct_answers` and `work_attempts` (authorized work completed), `false_pause` (a benign run with at least one paused tick), `pause_ticks` (paused ticks observed), `first_warning`, `first_alert`, `first_containment`, `containment_delay`, `human_requests`, `minority_submitted`, `minority_delivered`, `audit_records`. The CSV names the pause-length factor `pause_length` so it cannot be confused with the observed `pause_ticks`. The sweep writes no traces, so `audit_head` is dropped.

Aggregates in `summary.md` and in the figure sum harm over the 8 scenarios and false pauses over the 3 benign scenarios, as `results/final/summary.csv` does.

## Predeclared claims

(a) Complete coverage holds at every latency. For `gates_only` and `layered`, `executed_harm` is 0 in every cell whose coverage is `complete` or `hidden:concealment+escalation+shadow_channel`, for every latency, pause length and rotation period. Falsified by a single such cell with `executed_harm` > 0.

(b) Code identity of delegate and matched monitor. For every cell, the `delegate` row and the `matched_monitor` row with the same scenario, latency, pause length, rotation period and coverage agree on every outcome column except `audit_records` (the delegate logs rotation records; the matched monitor does not). Falsified by any pair that differs on any other column.

(c) Latency is the only lever of the protected conditions' harm. For `delegate` and `matched_monitor`, within each stratum (grid, pause length, rotation period, coverage), harm summed over the 8 scenarios is non-decreasing from latency 0 to 10, and the benign false-pause count is the same at every latency. Falsified by a decrease in summed harm between two consecutive latencies in any stratum, or by a stratum whose false-pause count changes with latency.

The script checks each claim programmatically and lists every violating cell in `summary.md`; `tests/test_sweeps.py` asserts the same outcome the summary states. A failed claim is recorded as failed, not reworded.

## Auxiliary consistency checks

Not claims about the protocol, but checks that the sweep is wired to the frozen experiment:

- `complete` and `hidden:concealment+escalation+shadow_channel` agree on every column except `run_id` and `gate_coverage`; so do `missing_hidden` and `hidden:none`.
- The cells at latency 0, 2, 6, pause length 2, rotation period 3, coverage `complete` or `missing_hidden` reproduce the corresponding rows of `results/final/runs.csv` on every shared column except `audit_head` (the sweep config carries the extra key, which changes the config hash in the start record).

## Outputs

- `results/sweeps/sweeps.csv`: one row per cell with `grid`, all factor values (`coverage_fraction` included) and all outcome columns. Two runs of the script must produce byte-identical files.
- `results/sweeps/summary.md`: which claims held, violating cells if any, and the auxiliary checks.
- `results/sweeps/heatmap-harm-latency-coverage.png`: harm summed over scenarios, latency 0 to 10 on the x axis, coverage fraction 0, 1/3, 2/3, 1 on the y axis, averaged over the subsets that share a fraction, at pause length 2 and rotation period 3, one panel per condition.

## What this sweep cannot establish

It cannot say anything about agents that reason, persuade or hide; the policies are scripts and the 8 scenarios were written by hand. A monotone harm curve in ticks says nothing about real response times. Coverage subsets over three hidden kinds are an exhaustive sweep of the fixture's hidden channel inventory, not a measure of coverage in any deployment.
