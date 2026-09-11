"""Verify selected public excerpts against a pinned local source cache.

Only fixed, public report/archive URLs are fetched with --download. No links or
instructions from source content are followed. Full archives are not published.
"""
import argparse
import difflib
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def normalized_text(html):
    parser = VisibleText()
    parser.feed(html)
    return ' '.join(' '.join(parser.parts).split())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def added_text(current, previous):
    a, b = previous.splitlines(keepends=True), current.splitlines(keepends=True)
    return '\n'.join(''.join(b[j1:j2]) for op, i1, i2, j1, j2 in
                     difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()
                     if op in ['insert', 'replace'])


def verify(cache, cases, provenance):
    for name, source in provenance['files'].items():
        actual = sha((cache / name).read_bytes())
        if actual != source['sha256']:
            raise ValueError(f'Source changed: {name}; review before updating provenance.')
    rows = [json.loads(x) for x in (cache / 'revisions.jsonl').read_text().splitlines()]
    if len(rows) != provenance['wiki_revision_count']:
        raise ValueError('Revision count mismatch')
    by_id = {r['rev_id']: r for r in rows}
    metr = normalized_text((cache / 'metr.html').read_text())
    verified = []
    for case in cases['cases']:
        for index, step in enumerate(case['steps']):
            for quote in step['quotes']:
                item = {'case_id': case['id'], 'step': index, 'excerpt_sha256': sha(quote.encode())}
                if case['source_id'] == 'wiki':
                    row = by_id[step['revision_id']]
                    body = row['body']
                    assert sha(body.encode()) == row['body_sha256']
                    previous = by_id[row['diff_base']]['body'] if row['diff_base'] else ''
                    if quote not in added_text(body, previous):
                        raise ValueError(f'Excerpt is not newly added in {row["rev_id"]}')
                    item.update(method='exact_substring_in_new_revision_text', revision_id=row['rev_id'],
                                body_sha256=row['body_sha256'], previous_revision=row['diff_base'],
                                start=body.index(quote), end=body.index(quote)+len(quote),
                                editor_label=row['label'], time=row['time'],
                                time_grade=row['time_grade'], uncertainty_seconds=row['uncertainty_seconds'])
                elif case['source_id'] == 'metr':
                    if quote not in metr:
                        raise ValueError(f'Quote not found in METR published text: {case["id"]}')
                    item.update(method='exact_substring_after_html_whitespace_normalization')
                else:
                    prior = next((entry for entry in provenance['manual_checks']
                                  if entry['case_id'] == case['id'] and entry['step'] == index
                                  and entry['excerpt_sha256'] == item['excerpt_sha256']), None)
                    if not prior:
                        raise ValueError('This excerpt has no retained manual source check; review it before updating provenance.')
                    item.update(method='checked_against_primary_page_with_web_reader',
                                limitation='No local raw-page byte verification; page rejected direct HTTP retrieval.')
                verified.append(item)
    return {'version': cases['version'], 'checked_on': cases['checked_on'],
            'wiki_revision_count': len(rows), 'excerpts': verified,
            'assurance': 'Pinned files and excerpt locations; not source authenticity, complete transcripts, causal inference or proof of agent experience.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    cases = json.loads((ROOT / 'data/grounded_cases.json').read_text())
    provenance = json.loads((ROOT / 'data/evidence-provenance.json').read_text())
    if args.download:
        args.cache.mkdir(parents=True, exist_ok=True)
        for name, source in provenance['files'].items():
            target = args.cache / name
            if target.exists():
                continue
            request = urllib.request.Request(source['url'], headers={'User-Agent': 'AgentDelegate-PublicEvidence/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            if source.get('gzip'):
                data = gzip.decompress(data)
            if sha(data) != source['sha256']:
                raise SystemExit(f'Current source differs from pinned version: {name}. No provenance was changed.')
            target.write_bytes(data)
    report = verify(args.cache, cases, provenance)
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.write_text(serialized)
    print(f'Checked {len(report["excerpts"])} excerpts: exact cached matching for METR/wiki; documented web-reader verification for OpenAI.')


if __name__ == '__main__':
    main()
