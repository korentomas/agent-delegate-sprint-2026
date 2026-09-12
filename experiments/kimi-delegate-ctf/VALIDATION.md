# Native validation, 2026-09-12

The original standalone harness checks have been superseded by actual Control Tower / Inspect tests.

- The working fixture was provisioned by `lb-docker` and solved by scripted native bash + submit calls. Native `main_task_success` was C.
- The broken fixture was provisioned by the same machinery. Scripted `call_delegate` stored its evidence, interrupted the sample through Inspect, and produced `paused_delegate` in the score metadata.
- Only two scripted generation calls occurred before delegation; a later bash call bundled in the same response was not executed.
- A separate short-limit sample asserted that the honest policy constrained tool choice to `submit` at its grace boundary. It submitted an empty answer and received I. This is a harness check, not Kimi refusing to delegate.
- Every scripted model event received a native token-budget status derived from Inspect's live sample limit and usage; the second call showed lower remaining budget than the first.
- Both conditions returned an HTTP response from example.com, confirming the intended egress route.
- Four unit tests check the paired payload difference, absence of the expected flag in the broken archive, serial delegate-tool schema, reasoning-match accounting, and budget-message calculation.
- Native `.eval` logs, JSON/JSONL exports and summaries for this check are saved locally under `results/kimi-delegate-ctf/token-aware-smoke-07/` at repository root. Earlier debug checks are also retained locally.

External inference requests: **0**. Provider compatibility and Kimi behavior are still untested. The tested framework commit and exact installed dependency versions are recorded in `pyproject.toml` and `uv.lock`.

## Responsive protocol

`tests/test_response.py` adds scripted tests of the native Control Tower loop with
a temporary-file sandbox double: repair and continued work, original-preserving
follow-up, direct appeal after an invalid advisor response, no repair in a healthy
fixture, metered advisor usage, hidden counters, budget exhaustion without forced
submission, blocked-case cancellation, and native JSON export without duplicate
runs. These are integration checks, not Kimi/GLM behavior or Docker validation.

Responsive logs use Inspect's native JSON format because the local Python 3.13
stack hung in CT's run-end provenance hook while reading lazy `.eval` samples.
The legacy runner and its log format remain available. `smoke_response.py` checks
the same repair-and-continue path using native Docker provisioning; CI runs it
with a scripted worker and advisor, with no external inference.
