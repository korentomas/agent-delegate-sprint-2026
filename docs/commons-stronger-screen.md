# Stronger standard-model capability screen

Specified after the four-model study and its isolated diagnostic, before the first scored call in this screen. This is a local freeze, not external preregistration. The prior 27B FP4 server returned 5 to a 2+3 format preflight; that call is retained separately and does not enter this screen.

Use the already downloaded, non-abliterated Qwen3.8-27B UD-Q4_K_XL with upstream llama.cpp HIP, no speculative decoding, one slot and context 8192. Disable thinking at server launch and in each request. Temperature 0.5, output budget 512 tokens, timeout 120 seconds. Retain server defaults, chat template, requests and responses. This is a configuration-specific screen, not proof of the model's general ability or an isolated size effect.

Exactly 36 calls: seeds 200–211, three worker inputs each, 18 threshold and 18 distinct-ID tasks, with the existing generator. These inputs were not used in the earlier studies. Use the isolated requirement/data prompt and integer-answer schema. Fixed shuffled order; no retries, dropping, answer repair or outcome-based selection. Invalid responses count as incorrect.

Operational gate, fixed before calls: at least 34/36 correct, at least 16/18 in each family and 36/36 well-formed answers. This is a practical pilot threshold, not a statistical certification. Report every result even if it fails. Passing permits planning a new institutional pilot; it does not validate the earlier four-model results or prove strategic behavior. Failing motivates task/interface diagnosis before a large grid. Any later reasoning-enabled or tool-assisted condition needs its own declared configuration and fresh inputs.

The proposed next study should separate a short report action from task output, retain independent action limits, and cross human-response availability/delay with direct access and optional delegation at equal budgets. Include task competence, true/false report accuracy, missed reports, unresolved cases, wrong answers, time and total inference/reviewer cost. Actual human understanding, review mistakes, strategic silence and interruption incentives require further studies.
