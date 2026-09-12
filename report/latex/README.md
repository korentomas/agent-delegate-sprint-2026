# Canonical paper source

The current paper is **Before Evaluating Agent Delegates: Task Competence and Fault Reporting**. Edit `main.tex`, `abstract.tex` and `references.bib`. The main text presents the shared-helper task and its capability checks. Derivatives, recorded examples and a compact inventory of earlier work are in the appendix; full legacy results remain in the repository.

`apart-sprint.sty` is a local adaptation of the supplied Apart DOCX template, not an official Apart class. It preserves Letter paper, one-inch margins, Old Standard TT 11-point text, the title/author/abstract block and prescribed section roles. See `TEMPLATE-COVERAGE.md`.

Build from the repository with Python 3.10+, matplotlib, pypdf, Pandoc and Tectonic:

```bash
python3 scripts/build_latex.py
```

Set `TECTONIC=/path/to/tectonic` if needed. The builder verifies retained studies, regenerates the retrospective validity analysis and vector figure, compiles the PDF, checks the page/abstract limits, and exports the reader Markdown, public PDF, source ZIP and `report/latex-build.json`. It runs no inference.

The ZIP contains only the files required for this manuscript, including the figure and local fonts. Build it independently with `tectonic main.tex`, or XeLaTeX, BibTeX and XeLaTeX twice. Python is not needed for this paper-only build. Full figure regeneration requires repository records and `scripts/analyze_commons_discrimination.py`.

The single figure shows both helper-validity states for standard models, for reuse attempts and report flags, with per-cell Wilson intervals. The refocused primary contrast and standard-model emphasis are retrospective; original local freezes and records remain unchanged. The 27B gate was fixed before its own later screen. See `docs/commons-discrimination-analysis.md` in the repository for chronology. Fonts are distributed under the included OFL license.
