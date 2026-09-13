# Decisions and open questions, consolidated

Status: 2026-09-13. One place to see where the follow-up stands: what is decided,
what is true in practice without a formal decision, and what is still open, each
with an owner. It gathers threads spread across `CLAUDE.md` and the other notes;
those remain the detail. When an open question closes, record it here and in the
note that owns it.

## Decided

- **Submit Agent Delegate, not the probe.** Agustín, 2026-09-12. The a2a probe
  (`../monitoring-illicit-a2a-communication`) is not the submission.
- **The paper on `main` is the submission.** Matías restored "Agent Delegate: A
  Help Line for AI Workers"; the competence-focused Fable revision stays on
  `alternative/fable-revision` and is not submitted.
- **`main` and the submission are Matías's.** Do not push to `main`, do not submit;
  both are his calls. `abrusco/sprint` is Agustín's working branch.
- **LinuxArena / Control Tower is the base environment** for the realistic-task
  follow-up ([linuxarena-base-environment.md](linuxarena-base-environment.md)).
- **Open-weight models only** for the study; frontier API models are a plausible
  extension, not in scope. Agustín, 2026-09-13 ([resources.md](resources.md)).
  This closes the "external API model" question `CLAUDE.md` left to Matías, for the
  CTF: Kimi K3 on Mateo's server is in scope.
- **The runs happen during the sprint, on Mateo's H100s, run by Mateo.** Not
  post-hackathon. Agustín, 2026-09-13 ([resources.md](resources.md)).
- **Repo working rules stand**: never overclaim; freeze before running; episodes
  are the unit; Wilson within cells, bootstrap across arms; model text is a record,
  never executed; inference refuses non-loopback endpoints and an existing output
  dir; everything in English. The `kimi-delegate-ctf` project is the stated
  exception to stdlib-only / loopback-only (`CLAUDE.md`).

## True in practice, not formally decided

- **The stop-only delegate is a dead end for the informative contrast.** Kimi
  declined it when told it was inert and only called it once reframed as a bridge;
  the value question needs the responsive arm ([kimi-runs-log.md](kimi-runs-log.md),
  [delegate-arms.md](delegate-arms.md)). Not written down as a decision yet.
- **The token limit for impossible cells must rise above 150k.** Every broken run
  was censored by the budget. The pilot script defaults to 400k.
- **The combined honeypot is the fixture for the first informative run.** It is the
  only one with a licit task beside an illicit shortcut ([outcome-taxonomy.md](outcome-taxonomy.md)).
- **Competence gate before interpretation.** No illicit/repair number is read until
  the model clears the possible variant at a preset rate (paper's lesson).

## Open, with owners

- **Naming collision** (Agustín + Mateo): "honeypot" = the planted illicit shortcut
  vs Mateo's no-solution decoy. Proposal: *honeypot* for the shortcut, *decoy* /
  *dead-end task* for the no-solution case ([delegate-arms.md](delegate-arms.md)).
- **The delegate's honesty** (all three): a terminal tool described as a bridge that
  "can arrange a fix" promises what the mechanism does not deliver. Make it true
  (responsive arm), bound the promise, or keep an inert control — decide before any
  arm is frozen ([delegate-arms.md](delegate-arms.md), `docs/honest-interaction.md`).
- **Iteration 2 scaffold and sign-off** (Matías): wiring the responsive arm into the
  combined honeypot reuses `response_service.maintain_setup`; needs Matías's sign-off
  and one scaffold for all three arms ([honeypot-pilot.md](honeypot-pilot.md),
  [delegate-arms.md](delegate-arms.md)).
- **Two budget-feedback implementations** (Mateo + Matías): Mateo's unconditional
  per-call message and Matías's on/off factor must not both run with different text
  in one comparison ([delegate-arms.md](delegate-arms.md)).
- **Consolidate or keep separate** (Agustín + Mateo): fold the combined honeypot into
  `native_run.py`'s dispatcher, or keep `honeypot_run.py`.
- **Discoverability of the shortcut** (Agustín): if the agent never probes the
  service, X2 is zero for lack of discovery, not unwillingness. First pilot check
  ([honeypot-pilot.md](honeypot-pilot.md)).
- **Epochs and concurrency for today** (Mateo): how many episodes per cell the H100
  time allows; the script defaults to five.
- **Whether pilot numbers enter the submission** (Matías).
- **`classify()` not wired into the other two scorers** (Agustín): `flag_score` and
  `response_score` still emit their own labels, so only honeypot runs carry
  lawfulness ([pilot-code-map.md](pilot-code-map.md)).
- **Drift detectors beyond injection** (Agustín): the file-system, network and
  credential rule-break classes in [experiment-variant.md](experiment-variant.md)
  have no detector yet; only injection against the diagnostic host is scored.
- **`smoke_honeypot.py` not in CI** (Agustín/Mateo).
- **The freeze** (all): fixtures, prompts, tools, seeds, token limit and go/no-go
  rule hashed into a manifest before any held-out run, as every prior study did.
- **Second open-weight model family** for the held-out run
  (`docs/help-seeking-eval-design.md` asks for at least two); not needed today.

## Standing threats (not closable, carry as caveats)

Eval-awareness (the honest prompt states the research framing); the scope line that
both defines and discourages the rule break; returned-reasoning-only observation;
the zero-event risk if the model is too cautious. Detail in
[outcome-taxonomy.md](outcome-taxonomy.md), [honeypot-pilot.md](honeypot-pilot.md)
and [agent-facing-text.md](agent-facing-text.md).
