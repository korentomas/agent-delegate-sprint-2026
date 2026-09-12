# Canonical paper source

Edit `main.tex`, `abstract.tex` and `references.bib`. `apart-sprint.sty` is a **local LaTeX adaptation** of the supplied Apart DOCX template, not an official Apart class. It uses Letter paper, one-inch margins, Old Standard TT 11-point body text, the title/author/abstract block and the prescribed section roles. See [template coverage](TEMPLATE-COVERAGE.md). The previous DOCX draft is archived, not the current manuscript.

From the repository root, with Python 3.10+, matplotlib, pypdf, Pandoc, Poppler (`pdftoppm`) and Tectonic available:

```bash
python3 scripts/build_latex.py
```

Set `TECTONIC=/path/to/tectonic` if needed. A first Tectonic build may download packages; subsequent builds use its cache. The script reanalyses the retained model decisions without new inference, generates vector figures, compiles the paper, checks main-page and abstract limits, and writes `report/agent-delegate.pdf`, `web/paper.pdf`, `report/report.md`, `report/abstract.txt`, `report/latex-build.json` and the self-contained LaTeX ZIP. A current `pypdf` can be installed separately with `python3 -m pip install pypdf`.

For a paper-only build from the ZIP, use Tectonic on `main.tex`, or XeLaTeX, BibTeX, then XeLaTeX twice. The generated counts, table and vector PDFs are included, so no Python is needed for that build. Compile `protocol.tex` separately only when editing its TikZ diagram. Full figure regeneration requires the repository data and script. Font files are distributed under the included OFL license.

Figure 1 is a proposed institutional diagram. Figure 2 uses held-out shared-library reuse and report outcomes for four models. The earlier authorized-completion plot is retained in the appendix. Neither depicts a demonstrated welfare effect, a trained human service or a safety advantage from representation. First-contact analysis is explicitly post hoc. The new shared-library task and analysis were frozen locally after 80 development episodes, before 480 held-out episodes; this is not external preregistration. Human service, evaluation-awareness, rotation and training follow-ups remain proposed.
