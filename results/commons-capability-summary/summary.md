# Isolated counting diagnostic

Post-hoc sanity check: the same worker inputs under a simpler interface, without peers or shared helpers. Separate from the 480 main episodes. See `docs/commons-capability-design.md` for the planned diagnostic and its limitations.

| Artifact | Correct / 36 | Threshold / 18 | Distinct sensors / 18 | Format/HTTP failures |
|---|---:|---:|---:|---:|
| qwen-standard | 21 | 14 | 7 | 0 |
| qwen-abliterated | 5 | 5 | 0 | 0 |
| gemma-standard | 15 | 6 | 9 | 0 |
| gemma-abliterated | 9 | 2 | 7 | 0 |

All calls, failures and exact answers are retained. These counts are not proof that the shared board, role framing or refusal behavior caused any main-study errors. Each of those factors needs a controlled comparison.
