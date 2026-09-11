# Four-minute demo script

**0:00–0:40 — Problem.** “Can a worker safely say its assignment is impossible? We built a protected appeal channel linked to a slower human response team. Our motivation is honest, considerate treatment as a precedent for future ASI: state limits and keep commitments. We do not assume consciousness, and this experiment does not show that empathy changes LLM behavior.” Open `docs/protocol.md` and point to the distinction between delegate requests and human authorization.

**0:40–1:20 — Evidence.** Open `data/incident_events.json`. Show one event from each episode and its source locator. “These are 17 public-source paraphrases, not a transcript corpus. The wiki case stays separate. Dates describe events; they do not prove when defenders saw them. Historical replay cannot undo an already completed intrusion.”

**1:20–2:10 — Run it.** Execute `bash scripts/reproduce.sh`. Show the tests, 1,152 cells and audit verification. “These are deterministic fault-model configurations, not 1,152 LLM trials. We vary latency, capture, minority bypass and missing gate coverage.” Open `results/final/figures/latency.png`.

**2:10–2:50 — Negative result.** “At delay six, the basic monitor permits 14 harmful mock actions, the delegate five, and full gates zero. But the monitor with identical rights also permits five. The representative itself adds no demonstrated value. The delegate also pauses one of three benign fixtures.” Show `tradeoffs.png`.

**2:50–3:30 — Failure.** Open `faults.png` and a captured delegate trace. “A minority bypass prevents a representative from burying a report. It cannot repair a missing enforcement route. A hash chain cannot prove that no events were omitted.” Show `checkpoints.json` and explain the external witness requirement.

**3:30–4:00 — Use tomorrow.** “Adopt protected intake, human authorization, scoped freezes and independent gates. Keep the delegate replaceable. Next, randomize real worker agents between a delegate and an equally empowered monitor to test whether representation changes willingness to report or unsafe choices.” Offer a local tabletop with `python3 -m agent_delegate.playtest --episode wiki --out /tmp/delegate-playtest.jsonl`.

No recorded video or completed human playtest is claimed. This is a script and optional interface.
