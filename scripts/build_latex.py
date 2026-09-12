"""Build the canonical LaTeX paper, reader copy and public PDF without inference.

Requires Tectonic, matplotlib, pypdf, Pandoc and pdftoppm. Set TECTONIC to the
executable path when it is not on PATH. Tectonic may fetch packages on first use.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'report/latex'


def run(*args, cwd=ROOT):
    subprocess.run([str(a) for a in args], cwd=cwd, check=True)


def main():
    from pypdf import PdfReader
    tectonic = os.environ.get('TECTONIC') or shutil.which('tectonic')
    if not tectonic:
        raise SystemExit('Install Tectonic or set TECTONIC to its executable path.')
    for executable in ('pandoc', 'pdftoppm'):
        if not shutil.which(executable):
            raise SystemExit(f'Missing build dependency: {executable}')
    run(sys.executable, 'scripts/analyze_help_seeking.py')
    svg = SOURCE / 'figures/completion.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    run(sys.executable, 'scripts/verify_commons_records.py')
    run(sys.executable, 'scripts/analyze_commons_behavior.py')
    run(sys.executable, 'scripts/analyze_commons_capability.py')
    run(sys.executable, 'scripts/analyze_commons_stronger.py')
    diagnostic = json.loads((ROOT / 'results/commons-capability-summary/summary.json').read_text())
    table = [r'\begin{table}[htbp]', r'\centering\small',
             r'\begin{tabular}{@{}lrrrr@{}}',
             r'\toprule Artifact & Correct / 36 & Threshold / 18 & Distinct / 18 & Invalid\\\midrule']
    for row in diagnostic['rows']:
        label = row['model'].replace('qwen', 'Qwen').replace('gemma', 'Gemma').replace('-', ' ')
        table.append(' & '.join([label] + [str(row[k]) for k in
                     ('correct', 'threshold_correct', 'distinct_correct', 'invalid_calls')]) + r' \\')
    table += [r'\bottomrule\end{tabular}',
              r'\caption{Post-hoc isolated counting diagnostic. The same worker inputs use a simpler prompt and answer-only schema, without peers or helpers. These 144 calls are separate from the main 480 episodes and do not isolate a peer effect. Invalid format/HTTP responses count as incorrect.}',
              r'\label{tab:capability}', r'\end{table}']
    (SOURCE / 'generated/capability-table.tex').write_text('\n'.join(table) + '\n')
    run(tectonic, '--keep-logs', 'protocol.tex', cwd=SOURCE)
    shutil.copy2(SOURCE / 'protocol.pdf', SOURCE / 'figures/protocol.pdf')
    run('pdftoppm', '-png', '-scale-to', '1800', '-singlefile',
        SOURCE / 'figures/protocol.pdf', SOURCE / 'figures/protocol')
    run(tectonic, '--keep-logs', 'main.tex', cwd=SOURCE)
    log = (SOURCE / 'main.log').read_text()
    if re.search(r'Overfull|undefined references|Missing character:', log):
        raise SystemExit('Review LaTeX overflow, reference or glyph warnings before publishing.')
    pdf = PdfReader(SOURCE / 'main.pdf')
    main_pages = next(i for i, p in enumerate(pdf.pages)
                      if p.extract_text().lstrip().startswith('References'))
    if main_pages > 8:
        raise SystemExit(f'Paper has {main_pages} main pages; sprint maximum is 8.')
    abstract = (SOURCE / 'abstract.tex').read_text().strip()
    words = len(abstract.split())
    if not 150 <= words <= 250:
        raise SystemExit(f'Abstract has {words} words; template requires 150–250.')
    shutil.copy2(SOURCE / 'main.pdf', ROOT / 'report/agent-delegate.pdf')
    shutil.copy2(SOURCE / 'main.pdf', ROOT / 'web/paper.pdf')
    (ROOT / 'report/abstract.txt').write_text(abstract + '\n')

    # A reader export of the same source; the PDF remains authoritative for layout.
    # Expand the local title macro explicitly for Pandoc (not a second paper source).
    tex = (SOURCE / 'main.tex').read_text()
    authors = (SOURCE / 'authors.tex').read_text().strip().replace('\\\\', '; ')
    tex = re.sub(r'\\aparttitle\{([^}]+)\}', lambda m: '\\section*{' + m[1] + '}\n' + authors + '. With Apart Research, September 2026.', tex)
    reader = SOURCE / 'reader.tex'
    reader.write_text(tex)
    try:
        run('pandoc', 'reader.tex', '--from=latex', '--to=gfm', '--citeproc',
            '--bibliography=references.bib', '--metadata=reference-section-title:References', '--output=reader.md', cwd=SOURCE)
        md = (SOURCE / 'reader.md').read_text()
        for name in ('protocol', 'completion', 'commons-behavior'):
            md = md.replace(f'figures/{name}.pdf', f'latex/figures/{name}.png')
        # GitHub does not render PDF embeds or figure wrappers in Markdown.
        def figure(match):
            body = match[0]
            src = re.search(r'(?:src)="([^"]+)"', body)[1]
            caption = re.search(r'<figcaption>(.*?)</figcaption>', body, re.S)[1]
            caption = re.sub(r'\s+', ' ', caption).strip()
            return f'![{caption}]({src})\n\n*{caption}*'
        md = re.sub(r'<figure\b.*?</figure>', figure, md, flags=re.S)
        # Longtable repeats the heading across PDF pages; keep it once in a reader table.
        lines, header = [], None
        for line in md.splitlines():
            if line.startswith(('| Tier |', '| Model |')):
                if header == line:
                    continue
                header = line
            lines.append(line)
        md = '\n'.join(lines) + '\n'
        (ROOT / 'report/report.md').write_text('<!-- Generated from report/latex/main.tex; edit the LaTeX source. -->\n\n' + md)
    finally:
        reader.unlink(missing_ok=True)
        (SOURCE / 'reader.md').unlink(missing_ok=True)

    inputs = [p for p in SOURCE.rglob('*') if p.is_file()
              and p.suffix in {'.tex', '.sty', '.bib', '.ttf', '.txt', '.md', '.pdf'}
              and p.name not in {'main.pdf', 'protocol.pdf'}]
    # Protocol figure is needed for a one-command main.tex compile in a source editor.
    inputs.append(SOURCE / 'figures/protocol.pdf')
    inputs = sorted(set(inputs))
    archive = ROOT / 'report/agent-delegate-latex.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in inputs:
            info = zipfile.ZipInfo(str(p.relative_to(SOURCE)), date_time=(2026, 9, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
    proof = {'canonical_source': 'report/latex/main.tex', 'main_pages': main_pages,
             'total_pages': len(pdf.pages), 'abstract_words': words,
             'template_adaptation': 'Local LaTeX adaptation; not the official class or byte-identical DOCX',
             'pdf_sha256': hashlib.sha256((ROOT / 'report/agent-delegate.pdf').read_bytes()).hexdigest(),
             'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
    (ROOT / 'report/latex-build.json').write_text(json.dumps(proof, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: proof[k] for k in ('main_pages', 'total_pages', 'abstract_words')}))


if __name__ == '__main__':
    main()
