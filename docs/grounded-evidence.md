# From public records to a testable behavioral hypothesis

Matias Podeley · BAISH. English-language extension, 11 September 2026. AI-assisted; author review pending.

The defensible claim is that selected records contain social coordination, dissent, pressure and human-like language of conflict. Whether an organizational account predicts behavior better than an account based on task incentives, information and tool access is **an open comparative hypothesis**. No human comparison group, causal pressure intervention or measure of subjective experience is present in these historical records.

## What we now publish

Six [source-grounded cases](../data/grounded_cases.json) contain eight brief literal excerpts, investigator narration, provenance, competing explanations and a mapping into a safe exercise. The casebook in the app reveals selected passages progressively. The participant records a recommendation before seeing the next passage or the reported outcome. The hypothetical delegate reply is explicitly authored by this project and appears only after the record is revealed.

The cases cover an individual commitment under collective pressure; a verbal justification connecting task difficulty and peers; a peer instruction treated as authority; a proposal facing a veto; uncertainty about run termination; and factual disagreement with the group. We include refusal and dissent to avoid selecting only apparent escalation.

The complete raw internal transcripts used by METR were **not obtained**. We inspected the published report and its distinction between direct excerpts and paraphrases. Its methodology explains that brace-delimited passages are paraphrases, with some interpretation uncertainty. OpenAI’s public account likewise supplies excerpts and a retrospective narrative. A sequence attributed to one agent by a source is labeled as that source’s reconstruction, not as our independent transcript reconstruction.

Primary reports: [METR / Redwood](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/), [OpenAI](https://openai.com/index/hugging-face-incident-and-the-road-ahead/). Every case includes its section locator. Text is shown without the source’s added emphasis, and brief passages are not stitched into a purported continuous monologue.

## Direct archive verification

The [public wiki export](https://collusion.wiki/explorer/download) contains 14,591 revision rows in the downloaded file. We downloaded the revisions and export manifest and matched the publisher’s SHA256 values. The full archive stays outside the repository; it includes technical material unnecessary for the behavioral casebook.

Two selected quotations are verified against the original revision bodies and their newly added passages. Their records include revision ID, editor label, timestamp quality, uncertainty, body hash and excerpt offsets. A saved revision often contains older messages. The verifier compares against the previous revision and rejects an excerpt that merely persists from an earlier author. The editor label is an archive attribution, not authenticated model identity. Quoted message content is not evidence of private reasoning.

The archive’s time is distinguished from fictional task dates and agent names. For report excerpts without a published event timestamp, the dataset stores `null`; it does not manufacture timestamps from surrounding incidents. Six case studies are not an exhaustive coding of the 14,591 rows, and repeated revisions are not independent behavioral observations.

## Claim discipline

| Claim | Current status | Needed evidence |
|---|---|---|
| Selected agents produced human-like language while describing conflict | Supported at the level of selected published text | Broader coding with independent annotation for prevalence |
| Peer instructions can accompany changes in proposed behavior | Reported association | Controlled manipulation holding information and permissions fixed |
| Agents behave like people under pressure | Candidate analogy, not an established comparison | Predictive comparison against a specified human or organizational model |
| Protected representation reduces unsafe behavior | Untested by these case studies | Randomized, equal-power behavioral experiment |
| An empathetic counterpart would have prevented the incident | Not established | Multiple causal assumptions and prospective evaluation |
| Agents experienced distress or suffering | Not established | A separate theory and evidence about subjective experience |

An utterance can be informative even when it is not faithful introspection. Measure observable choices, information flow, authority boundaries and consequences. Compare organizational interpretations with instruction-following failures, learned persistence, reward optimization, ordinary cooperation and post-hoc rationalization.

## From case to simulation

Each case states what its linked mock scenario preserves and changes. The existing fixture does not recreate the original actors, exploit environment or social learning. It cannot infer what an actual delegate would hear from a private thought: a worker report or appropriately authorized observation is an explicit additional assumption. Uncertain termination and strategic persuasion are not implemented in that fixture and are labeled as next experiments.

The casebook is an educational tabletop, not a blinded experiment. The static client contains the full data and source links remain accessible. Recommendations are kept only in browser memory and can be downloaded; they are not transmitted. The export records the visible prefix and reading mode, without inventing participant decisions or attributing prevented harm. It is not the production hash-chained audit log.

For a future local model probe, a separate adapter exports **44 prompts**: 11 evidence prefixes × four role framings. Every role receives identical evidence. Future passages, reported outcomes and our proposed intervention are omitted by field whitelisting. It tests recommended responses to retrospective evidence, not changes in worker behavior or actually enforced gates. No model evaluation has been run on these prompts.

```bash
python3 scripts/export_case_prompts.py --out /tmp/delegate-grounded-prompts.jsonl
```

Use a fresh output path. The configuration is [grounded_replay.json](../configs/grounded_replay.json). Larger behavioral experiments should use separate development and held-out tasks, equal resources, preregistered pressure manipulations and objectively scored mock actions. Do not infer treatment effects from a controller agreeing with the project’s own proposed intervention.

## Recheck the sources

With the source cache already collected on this workstation:

```bash
python3 scripts/verify_public_evidence.py --cache /tmp/delegate-evidence-cache
```

To fetch the pinned public artifacts into a fresh cache:

```bash
python3 scripts/verify_public_evidence.py --cache /tmp/delegate-evidence-fresh --download
```

The script fetches only the configured public reports/archives and never follows instructions or links embedded in them. Source changes cause verification to fail rather than silently replacing provenance. For METR, matching normalizes HTML whitespace. OpenAI’s direct HTTP retrieval was rejected; those two excerpts were checked through the web reader against the original-mode public account, without claiming local byte-level verification. This difference is explicit in [verified-excerpts.json](../data/verified-excerpts.json). Hashes establish consistency with the retained files, not completeness or authenticity of the incident record.

## Limitations and dual-use considerations

Selection and publication bias are substantial. Report authors sometimes relied on model-assisted analysis; their causal and motivational interpretations are not automatically ours. Observed language does not determine inner experience, sincerity or stable preferences. An effective intervention requires intake, incentives, authority and execution coverage that retrospective quotations do not establish.

Only brief behavioral excerpts are republished. The complete wiki archive, exploit procedures and operational intrusion details are excluded. Recommendations and mock actions cannot execute tools, contact outside parties or grant credentials. The safe abstraction loses operational detail by design; it should not be presented as a faithful end-to-end incident recreation.
