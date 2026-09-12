# Resources for the follow-up

Status: under discussion, last updated 2026-09-12.

## Compute

- **More than 10 hours of H100** available to the team. Purpose not yet allocated. Proposed use, to be decided: serve a stronger open-weight agent model for the LinuxArena episodes, since the 4B and 27B local runs failed the competence gate on much simpler tasks (see the paper and `docs/commons-stronger-screen.md`). Not for iteration: measure throughput per episode in a short pilot first, decide the model and the number of task instances from that, and hold back a reserve for the held-out run. LinuxArena episodes run up to 160 agent steps, so cost per episode is dominated by the agent model, not by the environment.
- **Strix Halo** (Matías): Ryzen AI Max+ 395, 96 GB unified memory, about half reserved for the GPU, llama.cpp with HIP. Every model run in this repo so far ran there. Models on disk with recorded provenance: Qwen3-4B-Instruct-2507, Gemma-3-4B-IT, their public abliterated derivatives (all Q4_K_M) and Qwen3.8-27B (UD-Q4_K_XL); see `data/commons-model-*.json` and `data/local-model-provenance.json`. Good for developing the environment and the prompts; not the machine for the held-out run if the agent needs to be frontier-class.
- **API budget**: none recorded. LinuxArena's own reference agents are frontier API models. If we want a comparable agent, this is a separate cost to estimate.

## People

- Matías Podeley: project lead and experimental design; hardware; repo owner.
- Agustín Brusco: evaluation design, analysis, this branch.
- Mateo: builds the LinuxArena variant (design and product; author of the Fast Timeline Builder, BAISWARM project #5).

## Time

The sprint deadline is 2026-09-13 23:59 AoE. Everything here is post-hackathon. No calendar has been set for the follow-up; the research program in `docs/research-program.md` sketched four weeks for a smaller version of this work.

## Open

- Who provides the H100 hours, on what platform, and whether they expire.
- Whether a frontier API agent is in scope at all, or the study is defined over open-weight agents only.
