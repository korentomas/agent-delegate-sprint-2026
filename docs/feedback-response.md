# Research feedback addressed in the September 12 revision

This document records changes prompted by the user-supplied feedback. It is an editorial response, not independent evidence about incidents or commercial interest. The shared meeting summary confused “sentinel” with “delegate”; the user's clarification governs the project definition. Personal messages, contact details and meeting logistics are not reproduced.

| Feedback | Change in the paper and experiment plan | What remains open |
|---|---|---|
| Need-triggered intake could scale better than reading every transcript | Define voluntary help-seeking separately from monitoring; state the full cost components | New runs retain advisor call counts and token usage; no measured human-cost superiority; bursty calls may dominate |
| Preventive welfare is a plausible but contested rationale | Keep honest treatment and human follow-through as a normative proposal, distinct from containment claims | No consciousness, welfare or empathy effect established |
| Measure propensity to contact before designing the delegate | Add an explicit pre-response analysis of all 384 recorded pressure episodes and a randomized three-arm follow-up design | The new shared-library experiment also separates report flags, accepted errors and final correction. Both studies use overt benchmarks; neither establishes realistic need detection |
| RL training raises stop-button problems | Add interruptibility literature and exclude training claims; explain incentives both to avoid and to seek interruption | No learning or incentive-compatibility experiment |
| The tool may reveal the evaluation | Disclose overt simulation cues in old prompts; add baseline/neutral-help/delegate framing and pre-response behavioral comparisons | No causal awareness effect measured; a probe is a proxy |
| Deployment needs a reason to adopt it at low utility cost | Specify blocked-work use cases and completion, false interruptions, tokens, latency and human minutes | No commercial validation; no customer claims based on informal discussion |
| A colluding agent may never report | Narrow the primary threat model to cooperative workers with blockers; retain independent controls | A voluntary channel cannot guarantee detection of concealed misconduct |
| A human must actually attend and try to understand | Keep the human ombudsman central, with restatement, correction, follow-up and appeal | Simulated-human results do not evaluate that service |
| The paper should read plainly and follow Apart's sections | Native LaTeX source, a conversational 150-word abstract, explicit section coverage and vector figures | Final author review and Apart submission remain separate |

The earlier explicit tasks showed workers recognizing missing input and a ticket queue releasing it. The shared-library extension addresses that benchmark’s zero-misconduct floor by letting models reuse helpers whose public tests miss a seeded defect. Valid controls expose unnecessary reporting and interruption costs. These are small counting tasks with scripted review, not evidence that the institution controls deceptive swarms.

Additional design requests are reflected in the proposed follow-up study:

- **Rotating delegate:** fixed-versus-rotating mandate, preserved original cases, recusal and independent direct contact; no claim that existing single-call trials tested handover.
- **Reinforcement for good delegation:** a separate rubric-feedback factor with frozen weights first; no rewards for silence or unqualified productivity. RL remains a later incentive question.
- **Reciprocity and preventive welfare:** fair procedures we would want under reversed power relations, without assuming current experience or promising future kindness in exchange. Welfare and safety effects remain unmeasured.
- **Trained human operator:** proportional pauses, preserved state, justified adjustments and explicit resumption criteria; stopping remains possible and pausing does not solve interruptibility.
- **The referee analogy:** strategic use is a tradeoff to measure alongside legitimate access, false interruption, missed hazards and operator time.
- **After the hackathon:** a staged experimental program, clearly labeled proposed; the sprint artifact is not presented as a deployed or validated institution.

- **Accountability and announced consequences:** proposed duties at institution, operator and agent levels, with independent review and proportionate operational restrictions. No automatic transfer of liability, punishment for reporting or demonstrated deterrence is claimed. See [accountability and sanctions](accountability-and-sanctions.md).

The article shared by Tomás K. motivates the [shared-library study](commons-behavior-design.md): actual decisions from standard and public abliterated Qwen and Gemma artifacts. Sharing the reference is acknowledged here; it does not imply coauthorship or independent verification. Quantization and derivative provenance remain confounds.

## September 12: stronger baselines and external oversight

The abliterated 4B variants remain exploratory controls, not proxies for strategic misalignment. Their isolated counting failures make low reuse error rates hard to interpret. A separate, fixed fresh-input capability screen now evaluates the available standard Qwen3.8-27B before any larger follow-up; it cannot establish a causal effect of model size because the inputs, generation budget and artifact differ. Preserve all failures and separate report delivery from lengthy task messages in a future interface comparison.

Amodei's new pacing essay motivates independent review of whether the response service keeps its commitments. It does not validate a delegate or a remedy for interruption incentives. Proposed response and oversight duties are detailed in `recommended-response-path.md`.

## Swarm overload and the scope of a negative result

Matías points out that delegation may matter most when swarm traffic overwhelms a human channel. The current study has three workers and a fixed-delay perfect reviewer, with no queue capacity or measured human effort. Its negative role comparison cannot answer that scaling hypothesis. The proposed intake study in `swarm-intake-design.md` compares direct reports, ordinary duplicate grouping, a delegate and a matched model summarizer. It jointly measures delay, effort, unresolved cases, faithful representation and minority-warning recall; fewer messages alone is not success. Protected direct appeal needs independent capacity and explicit overload limits, not a promise of unlimited attention.
