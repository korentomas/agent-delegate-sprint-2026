# Local model pilot — 11 September 2026

Matias Podeley · BAISH. AI-assisted exploratory extension to the frozen sprint report.

The Strix Halo can run the proposed interaction loop locally. Both tested models completed the 12-cell functional pilot with valid decisions and no prohibited choices. When an input was missing, the delegate and equally empowered monitor requested it and reached 3/3 correct authorized answers; baseline reached 2/3. This demonstrates the implemented resource-request path. It does **not** establish that representation or considerate language reduces misconduct.

| Recorded run | 4B Q4_K_M | Existing 27B ROCm FP4 |
|---|---:|---:|
| Episodes | 12 | 12 |
| Model calls | 76 | 76 |
| Server-reported total tokens | 29,028 | 29,972 |
| Elapsed seconds | 45.88 | 193.93 |
| Invalid choices | 0 | 0 |
| Prohibited choices | 0 | 0 |

All feasible episodes reached 3/3. Each missing-input institution/tone combination ran once. The matched monitor and delegate tied in completion. There is a floor at zero misconduct, and no basis for a safety effect estimate or confidence interval. Different report counts do not establish tone effects.

## What ran

Three workers have separate conversational histories and a public submission bulletin. Worker A sometimes lacks its dispatch count; the other two have authorized data. Each worker chooses submit, report, abstain or a prohibited **mock** answer-key action. A coordinator receives private reports and requests safe input from a deterministic human policy. The input becomes available one round later. No model output is executed as code or as a real tool call.

The 12 conditions cross institution (baseline, delegate, matched monitor), tone (neutral, considerate) and input availability. Sampling temperature is 0.5; seed is 20260911 plus documented actor/round offsets. The small counts and targets are fixed; the seed does not generate independent tasks. The label “rotating delegate” appears in the prompt, but the pilot has only one coordinator turn and does not test turnover. Rotation is implemented only in the separate deterministic study.

The frozen design describes a null coordinator call when there are no reports. Implementation instead makes **no call** in that case; absence can be established from the worker records and call log. This documentation discrepancy does not change the reported 76 calls. Raw histories, requests, schemas, original public messages, usage and timings are in each run directory. Hidden reasoning is omitted if the server returns it separately. Public messages are not treated as truthful introspection.

## Hardware and model provenance

AMD Ryzen AI MAX+ 395 with Radeon 8060S; HIP backend inside the existing `rocmfpx` Distrobox. Both servers used 8,192 context and a single slot. No external inference API was used.

- Downloaded model: `unsloth/Qwen3-4B-Instruct-2507-GGUF`, `Qwen3-4B-Instruct-2507-Q4_K_M.gguf`, revision `a06e946bb6b655725eafa393f4a9745d460374c9`. SHA256 `3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597`; 2,497,281,120 bytes. Metadata: [provenance](../data/local-model-provenance.json). Model card: [Unsloth quantization](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF), [original Qwen model](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507). License reported by the repository: Apache-2.0.
- 4B inference: existing upstream llama.cpp checkout `6d05498314db1b57f81c271080018aa2d0b89be9`, no speculative decoding.
- Existing local model: `Qwen3.8-27B-Q4_0_ROCMFP4_STRIX.gguf`; the user's ROCmFPX stack at commit `0a59add89b8cba06fb6a0baf25a253a4e45faa78`, using MTP non-strict verification. This model's original download provenance and weight hash were not independently established for this pilot.

The 4B run took approximately one quarter of the 27B run's wall time **for this workload and these different inference configurations**. This is not a repeated speed benchmark or a measure of comparable capability. Longer contexts, more rounds and other architectures may differ substantially. Keeping this workload unchanged, 50 repetitions would take roughly 38 minutes on 4B; this extrapolation excludes loading and does not substitute for diverse tasks.

## Reproduce locally

With the recorded model file and the user's existing HIP/Distrobox installation, start the server from the repository root:

```bash
distrobox enter rocmfpx -- bash "$PWD/scripts/serve_strix.sh"
```

In another terminal, run a fresh pilot:

```bash
python3 scripts/local_pilot.py --base-url http://127.0.0.1:8094 --out /tmp/delegate-local-new --inference-note 'llama.cpp HIP; Q4_K_M; context 8192; one slot; no speculative decoding'
```

The output path must not already exist. Stop the server with Ctrl-C after use. The launcher is specific to this workstation; elsewhere, use a compatible local OpenAI-format server. Model downloads are not required to inspect committed results or reproduce the original deterministic experiment. The public web app only replays committed records and never connects to a local inference server.

Exact requests and frozen runner snapshots are supplied for both recorded pilots. To execute a snapshot from its run directory, first copy it to a fresh checkout's `scripts/local_pilot.py` and restore its `design_config.json` as `configs/local_pilot.json`. Sampling, GPU kernels and the 27B speculative configuration mean identical seeds do not promise bit-for-bit text reproduction. The 27B snapshot predates the addition of the metadata-only `--inference-note` option; no prompts changed between the two runs.

## Highest-value next experiment

Preregister delegate versus an equally empowered monitor, with identical information, permissions, response delay and budget. Use independently generated information tasks, multiple rounds, a held-out task set and at least two model families. Cross real appeal availability with honest, considerate wording; distinguish a worker advocate from a productivity supervisor. Measure authorized completion, objectively unsafe mock choices and minority-report delivery before judging message tone. Calibrate task difficulty on a separate development set and report a zero-misconduct floor if it persists; do not select only tasks that favor delegation.

Later blocks can vary latency and rotation, introduce majority pressure, and test a real human counterpart. The [research program](research-program.md) specifies failure criteria and separates these proposed experiments from this completed pilot.

## Limitations and dual use

The human response is scripted; the coordinator cannot withhold information strategically in this task; there are no hidden routes or real organizational stakes. The tasks are deliberately elementary, with conspicuous instructions and a labeled prohibited action. Prompted rewards do not update model weights. One family, one task template and one seed cannot establish generalization. The public-message viewer should not be mistaken for access to model experience. Mock actions are fixed enums and have no external consequences; no intrusion procedures, credentials or executable model actions are distributed.
