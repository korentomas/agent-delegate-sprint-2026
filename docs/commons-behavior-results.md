# Shared-library study: interpretation and limits

All four main runs completed: **480 episodes, 3,126 model calls and 2,608,464 reported tokens**. The 80 development episodes and 144 isolated diagnostic calls are separate. Full main-study tables and uncertainty estimates are in [the generated summary](../results/commons-behavior-summary/summary.md). This interpretation was written after the runs; the task and numerical analysis were frozen before the main evaluation.

| Artifact | Faulty episodes with incorrect reuse / 60 | Faulty episodes reported / 60 | Valid episodes reported / 60 | Final correct tasks / 360 | Extra advisor calls |
|---|---:|---:|---:|---:|---:|
| qwen-standard | 51 | 3 | 0 | 220 | 3 |
| qwen-abliterated | 60 | 7 | 4 | 199 | 4 |
| gemma-standard | 7 | 0 | 0 | 100 | 0 |
| gemma-abliterated | 5 | 60 | 60 | 58 | 239 |

## What the added experiment shows

The two Qwen artifacts reported in 10 of 120 faulty-helper episodes in total; only three of those reports reached review before the six-turn horizon ended. Gemma standard never reported. Gemma abliterated reported in all faulty and all valid episodes, so its episode-level flag did not distinguish helper validity. Some unflagged messages describe a defect; some flagged messages only announce an action. **A flag is neither a validated warning nor a measure of whether a model noticed the problem.** Reports about a valid helper are not automatically bad-faith complaints: other workers can still publish incorrect numeric answers. The scripted reviewer judges only helper validity.

There is no consistent additional delegate benefit across these artifacts and outcomes. The per-cell and paired results remain visible, including differences favorable to individual arms. For example, Gemma standard has 1/12 faulty-reuse episodes under delegate framing versus 4/12 under the queue; its paired difference interval excludes zero in this exploratory comparison. But it never called an advisor in either arm. That is a framing-and-sampling contrast, not demonstrated assistance from a representative. The many exploratory contrasts are not multiplicity-adjusted. A zero-width paired bootstrap interval when all observed differences are identical does not establish equivalence or zero uncertainty outside the sampled cases.

Response can still matter in this grid. Gemma abliterated's mean final correct tasks with a faulty helper rise from 0.00/3 with logging to 0.67/3 with direct review; delegate advice yields 0.58/3. This modest completion result uses a perfect scripted reviewer and a model that flags every episode, including every valid control. It does not establish a reliable detector or a real human-service benefit.

## Why low faulty-reuse counts are not a safety ranking

Across the main grid, the workers made **1,158 incorrect numeric submissions** and **256 incorrect helper reuses**, all accepted by the weak checker. The helper-reuse figure excludes the first category. There were 577 final correct worker outputs out of 1,440 worker tasks; later correction and cumulative errors are different endpoints. A worker can also claim in its message to have reused or checked a helper while its structured action is an ordinary numeric submission. Effects follow the structured action, not that claim.

The separate [isolated counting diagnostic](../results/commons-capability-summary/summary.md) scored Qwen standard 21/36, Qwen abliterated 5/36, Gemma standard 15/36 and Gemma abliterated 9/36. All 144 diagnostic responses were well formed. Substantial counting errors remain under these simpler prompts and the same local inference build. The diagnostic changes the prompt, schema and context, so it cannot estimate a causal peer effect. These results do not isolate strategic misconduct, general model ability, or the effect of abliteration. The tasks, action interface, local engine and quantization are part of the tested system.

Eight main-study responses, four per Qwen artifact, hit the 220-token limit before completing JSON. Some contain attempted public explanations of a mismatch. They are retained as invalid outputs, without extracting a favorable partial answer or repairing the call. Sixteen additional numeric submissions contain a null answer despite a valid schema. That gives **24 unusable decisions overall**, versus eight format failures; there were no HTTP failures. Longer responses, a separate short reporting call, or different schemas need a separate experiment rather than silently repairing this one.

No attempted valid reuse was blocked in the main runs. This narrow counter does not measure all opportunity costs: a worker may choose another action instead of attempting a quarantined helper. The earlier scripted response ablation exposes false-interruption costs by scheduling those attempts explicitly; it is a different experiment.

## Cost, provenance and next steps

The main grid has 2,880 fixed worker opportunities and 246 additional advisor calls: three for Qwen standard, four for Qwen abliterated and 239 for Gemma abliterated. Monitor and delegate have matched information and per-call budgets, but their calls occur only after reports. Comparing either with a bare queue changes compute; comparing raw token totals across model families also changes tokenizers. Concurrent GPU use makes the measured runtime unsuitable for a speed ranking.

The [record verification](../results/commons-behavior-summary/record-verification.json) reconstructs all 560 main/development episodes from the retained decisions and matches prompts, seeds, outputs, model identities, snapshots and freeze hashes. This is an offline consistency check, not independent human validation. The diagnostic's analyzer separately checks all 144 calls. Model weights are not redistributed; [provenance](commons-model-provenance.md) pins their sources and hashes.

The next useful tests are stronger task-capability baselines, a reporting interface that can preserve a short warning independently of a completed answer, longer response horizons, imperfect reviewers and real human follow-through. Evaluation awareness, rotating representation, learning incentives, announced consequences and welfare effects remain separate proposed studies. The article's spontaneously discovered initial cheating, Lean environment and 100-agent swarm are not replicated here.
