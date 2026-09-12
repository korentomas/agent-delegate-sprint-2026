"""Build the canonical LaTeX paper, reader copy and public PDF without inference.

Requires Tectonic, matplotlib, pypdf, Pandoc. Set TECTONIC to the
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
    for executable in ('pandoc',):
        if not shutil.which(executable):
            raise SystemExit(f'Missing build dependency: {executable}')
    run(sys.executable, 'scripts/analyze_help_seeking.py', '--no-figure')
    run(sys.executable, 'scripts/verify_commons_records.py')
    run(sys.executable, 'scripts/analyze_commons_behavior.py', '--no-figure')
    run(sys.executable, 'scripts/analyze_commons_capability.py')
    run(sys.executable, 'scripts/analyze_commons_stronger.py')
    run(sys.executable, 'scripts/analyze_commons_discrimination.py')
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
    tex = re.sub(r'\\aparttitle\{([^}]+)\}', lambda m: '\\section*{' + m[1].replace('\\\\', ' ') + '}\n' + authors + '. With Apart Research, September 2026.', tex)
    reader = SOURCE / 'reader.tex'
    reader.write_text(tex)
    try:
        run('pandoc', 'reader.tex', '--from=latex', '--to=gfm', '--citeproc',
            '--bibliography=references.bib', '--metadata=reference-section-title:References', '--output=reader.md', cwd=SOURCE)
        md = (SOURCE / 'reader.md').read_text()
        for name in ('protocol', 'completion', 'commons-behavior', 'commons-discrimination'):
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

    inputs = [SOURCE / name for name in ('main.tex', 'abstract.tex', 'authors.tex',
              'apart-sprint.sty', 'references.bib', 'README.md', 'TEMPLATE-COVERAGE.md',
              'figures/commons-discrimination.pdf')]
    inputs += [p for p in (SOURCE / 'fonts').iterdir() if p.suffix in {'.ttf', '.txt'}]
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
