"""Cache original publisher HTML and its literal source TeX, without rewriting it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup
from curation import OUT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('cache_id')
    parser.add_argument('url')
    parser.add_argument('--source-group',required=True)
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9._-]+',args.cache_id):
        raise ValueError('Cache ID must be a plain filename stem')
    if not args.url.startswith('https://'):
        raise ValueError('Use the original HTTPS publisher URL')
    path=OUT/'sources'/(args.cache_id+'.html')
    if not path.exists():
        response=requests.get(args.url,timeout=40)
        response.raise_for_status()
        path.write_bytes(response.content)
    soup=BeautifulSoup(path.read_text(),'html.parser')
    text_path=path.with_suffix('.txt')
    text_path.write_text(soup.get_text(' ',strip=True))
    registry_path=OUT/'publisher-source-registry.json'
    registry=json.loads(registry_path.read_text()) if registry_path.exists() else {}
    registry[args.cache_id]={
        'url':args.url,'source_group':args.source_group,
        'title':soup.title.get_text(' ',strip=True) if soup.title else args.cache_id,
        'html_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'text_sha256':hashlib.sha256(text_path.read_bytes()).hexdigest(),
        'literal_tex_spans':len(soup.select('.tex-math')),
        'status':'CACHED_PRIMARY_SOURCE_NOT_AUTOMATIC_CORPUS_ADMISSION',
    }
    registry_path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(registry[args.cache_id],ensure_ascii=False))


if __name__=='__main__':
    main()
