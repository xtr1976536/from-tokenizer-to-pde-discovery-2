"""Cache a small explicit primary-source shortlist, with checkpointed provenance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/eqgpt-research/stage2-corpus-2026-11-15'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ids', nargs='+')
    args = parser.parse_args()
    registry_path = OUT / 'focused-source-registry.json'
    registry = json.loads(registry_path.read_text()) if registry_path.exists() else {}
    for ident in args.ids:
        if not re.fullmatch(r'\d{4}\.\d{4,5}(?:v\d+)?', ident):
            raise ValueError('Expected a modern arXiv ID')
        path = OUT / 'sources' / (ident + '.html')
        url = 'https://arxiv.org/html/' + ident
        if not path.exists():
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                path.write_text(response.text)
            except requests.RequestException as error:
                registry[ident] = {'url': url, 'status': 'unavailable', 'error': str(error)}
                registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n')
                print(ident, 'UNAVAILABLE', flush=True)
                time.sleep(3)
                continue
            time.sleep(3)
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        title = soup.title.get_text(' ', strip=True) if soup.title else ident
        for math in soup.find_all('math'):
            if math.get('alttext'):
                math.replace_with(' $' + math['alttext'] + '$ ')
        text_path = path.with_suffix('.txt')
        text_path.write_text(soup.get_text(' ', strip=True))
        registry[ident] = {'url': url, 'status': 'cached', 'title': title,
                           'html_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'text_sha256': hashlib.sha256(text_path.read_bytes()).hexdigest()}
        registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n')
        print(ident, 'CACHED', flush=True)


if __name__ == '__main__':
    main()
