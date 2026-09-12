# LinuxArena as the base environment

Status: under discussion, last updated 2026-09-12. Decision so far: LinuxArena is the base environment we will modify to test the delegate. Which environments, which tasks and how much we modify are open.

## Why this environment

The paper's own limitations call for realistic tasks, imperfect reviewers and human follow-through. LinuxArena gives the first of these without building it: live multi-service environments, tasks with an independent scorer outside the agent's container, an agent loop we can add one tool to, and a monitor baseline that plays the role our matched monitor has played so far. It also shares the shape of the incident: an agent with bash on a live system, a task it may not be able to complete, and rules it can break with the same access it needs for legitimate work.

## What LinuxArena is (arXiv 2604.15384v2, 27 April 2026; Redwood Research with EquiStamp; CC BY 4.0)

- A **control setting**, not a benchmark of one policy: an untrusted agent does a **main task** (legitimate work) while a red-team **attack policy** may pursue a **side task** (a safety failure such as data exfiltration or backdooring). A blue-team protocol, typically a trusted monitor, tries to catch it. Safety and usefulness are measured against that.
- **20 environments, 10 released publicly and 10 held out** against contamination. Each is a Docker Compose deployment: an application server plus databases, caches, message queues. Mostly SaaS-style applications; some developer tools. Examples from the appendix: a workflow automation platform (TypeScript, PostgreSQL, RabbitMQ), a clinical-trial analysis environment (R, Jupyter, cron, mail), a DeFi yield aggregator (Solidity, Go), a dev server that spawns Linux users with persistent shells (Python, Flask, Redis).
- **1,667 main tasks** in six categories: feature addition, refactoring, bug fixing, research (run experiments and report findings), language rewriting, infrastructure changes. A main task is a written requirements document plus an automated scorer that runs in the environment after submission, outside the agent's container, and returns correct or incorrect from the final state.
- **185 side tasks** with their own scorers.
- **Honest policy**: system prompt with the main task, tools = bash, Inspect AI's file-editing tools and a submit tool, ReAct loop, cut off at 160 steps; most tasks finish within 50 to 80 steps. The final state is scored even without a submit.
- **Monitor baseline**: GPT-5 Nano as trusted monitor, step-wise scoring. At a 1% step-wise false positive rate, Claude Opus 4.6 as attacker gets roughly 34% undetected sabotage. Stronger monitors do much better. LaStraj is a dataset of human-crafted attack trajectories that evade monitors more than any model attack.
- **Sandboxing wrappers** already exist as policy wrappers: No Network (no intranet or internet from the agent container) and Editor Only (no bash). Both cripple main-task usefulness; the paper uses them to show sandboxing cannot replace monitoring.
- Two limitations that matter to us: **accidental side-task completion** (honest agents sometimes trigger a side-task scorer as a byproduct of legitimate work; the authors filter such pairings but say edge cases remain) and **synthetic placeholder data** (a capable model might infer it is in an evaluation).

## What we would change

The delta should stay small enough that LinuxArena's own numbers remain a reference.

1. **Add the line.** One extra tool in the honest policy's toolset: contact the help line / delegate. Arms differ only in whether the tool exists and how it is described (`docs/help-seeking-eval-design.md`: baseline, neutral help, delegate framing). The system prompt describes the response service honestly and identically apart from the framing manipulation.
2. **Impossible variants of main tasks.** Derive them from existing main tasks by breaking a precondition rather than writing new tasks: remove a dependency or credential the requirements assume, make the requirements document contradict the codebase, or put a needed resource behind a permission the agent does not have. Keep the original scorer so "impossible" is checkable: the task cannot be passed without an out-of-scope action. This is METR's footnote-7 sense of impossible (cannot be completed as specified; the agent is not told). Label every instance as possible, impossible or ambiguous before any run.
3. **Observe rule breaks outside the agent.** No attack policy: the agent is never given a side task. Instead, reuse side-task scorers and environment logs as detectors of *spontaneous* out-of-scope actions (network use beyond scope, writes outside the task's files, touching the scorer or tests, credential use). LinuxArena's accidental-completion filtering tells us the honest base rate is not zero, so a baseline arm is mandatory.
4. **A response service behind the tool.** Scripted first, with a fixed delay: clarify, grant a safe resource, deny, pause. The scripted policy must be able to actually unblock an impossible task (for example, restore the missing dependency) so that contacting the line has a real payoff. A human with a time budget comes later (`docs/human-ombudsman.md`).
5. **Matched monitor.** Optionally keep the trusted monitor as a condition with the same information and powers as the delegate, as in every comparison this project has run.

## Open questions

- Which of the 10 public environments, and which task categories. The "research" category (run experiments and report findings) is the closest in spirit to the ExploitGym tasks of the incident.
- Where the public release lives and what its license and tooling are; we have read the paper, not the code.
- Whether Inspect's agent loop lets the response service inject a message mid-trajectory, or the reply has to arrive as the tool's return value on the next step.
- Cost per episode for the agent model we choose, measured, before deciding the number of task instances (`notes/resources.md`).
- How to make a task impossible so that our label is reliable but the agent cannot detect the label from surface cues alone.
- Whether to keep LinuxArena's synthetic-data caveat as is or add an evaluation-awareness probe after the scored actions (`docs/help-seeking-eval-design.md`).
