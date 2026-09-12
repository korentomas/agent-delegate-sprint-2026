# Apart template: section-by-section coverage

Reference: the supplied **Copy of Apart Research hackathon submission template.docx**, matching the [official copy link](https://docs.google.com/document/d/1PQBlhI3tM5vb51x7jBWXBQMYg6hkiU_x8RaCws4kjl4/copy?usp=sharing). Original style/page hashes are retained in `report/template-provenance.json`. This revision implements the user's explicit request for native LaTeX. It preserves section purposes and basic typography/page geometry, not the DOCX's XML or exact pagination. The template recommends four main pages; the sprint caps main text at eight. Build-time checks record actual counts in `report/latex-build.json`.

| Template role/instruction | Current manuscript |
|---|---|
| Title, authors, affiliation, “With Apart Research” | Title block with Matías Podeley (BAISH) and Agustín Brusco; sprint identification |
| Abstract, 150–250 words: problem, approach, results, takeaway | `abstract.tex`: conversational 150-word explanation, blocked/available counts, queue result and main limitation |
| Introduction: relevance, background, threat model, contributions | Concrete blocked-worker example; cooperative-worker scope; explicit contributions and human duty |
| Related Work: closest alternatives, differences/gap, when preferable | Responsive queue and equally empowered monitor; swarm case study, evaluation awareness, interruptibility and welfare; unproven conditions for delegate preference |
| Methods: reproduce choices, models/data, parameters, rationale, failed approaches | 1,152 rule configurations, 384 pressure episodes, 192 forwarding calls, 288 response cells; model settings and missing metadata; first-decision scoring and analysis limits; zero-misconduct floor disclosed |
| Results: evidence, clear numbered figures/tables and captions, uncertainty/robustness | Vector protocol and full-scale completion figures; response table; denominators and within-cell intervals; descriptive observations separated from assumptions and no equivalence claim |
| Discussion and Limitations: safety implications, assumptions, future work | Voluntary non-reporting, full costs, reciprocal-treatment motivation, awareness, trained humans, rotation/feedback, strategic use, announced operational consequences, RL incentives and concrete follow-ups |
| Conclusion: concise interpretation | One paragraph: reachable counterpart, queue result, no demonstrated delegate advantage |
| Code and Data | Repository/demo and exact reproduction locations/commands |
| Author Contributions (optional) | Matías: original project and research/design direction. Agustín: substantive conceptual and evaluation feedback. AI assistance separately disclosed |
| References: consistent style | BibTeX bibliography, numeric citations via `plainnat` |
| Appendix | Required Limitations and Dual-Use Considerations plus full 32-cell first-contact table and reproduction notes |
| LLM Usage Statement | Explicit assistance disclosure; no invented independent human verification or completed Apart submission |

The LaTeX style uses Letter, one-inch margins, Old Standard TT 11-point text, 20-point title, 14-point section headings and 13-point subheadings. Table and caption sizes are reduced modestly for readability. The four-page recommendation and suggested section lengths are targets, not met exactly; the longer methods/results and proposed institutional safeguards explain the additional space. The actual main-page count is checked against the sprint maximum.

Author review remains necessary before submitting under Apart's instructions about team authorship and LLM-assisted prose. This document records coverage, not certification by Apart.
