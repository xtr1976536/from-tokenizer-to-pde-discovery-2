"""Restore every archived weight to its original project-relative path."""
import argparse,hashlib,json,os,shutil,urllib.request
from pathlib import Path
RELEASE='https://github.com/xtr1976536/from-tokenizer-to-pde-discovery-2/releases/download/archive-2026-11-18/'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--destination',type=Path,required=True);ap.add_argument('--verify-only',action='store_true');a=ap.parse_args()
 manifest=json.loads((Path(__file__).resolve().parents[1]/'manifests/server_sources.json').read_text())
 cache={};dest=a.destination.resolve()
 for r in manifest:
  if r['kind']!='weight':continue
  p=dest/r['path']
  if not p.resolve().is_relative_to(dest):raise ValueError('Unsafe path')
  if p.exists() and sha(p)==r['sha256']:cache[r['asset']]=p;continue
  if a.verify_only:raise RuntimeError('Missing or changed: '+str(p))
  p.parent.mkdir(parents=True,exist_ok=True)
  if r['asset'] in cache:
   try:os.link(cache[r['asset']],p)
   except OSError:shutil.copy2(cache[r['asset']],p)
  else:
   tmp=p.with_suffix(p.suffix+'.partial');urllib.request.urlretrieve(RELEASE+r['asset'],tmp)
   if sha(tmp)!=r['sha256']:raise RuntimeError('Checksum mismatch: '+str(tmp))
   tmp.replace(p)
  cache[r['asset']]=p;print(p,flush=True)
if __name__=='__main__':main()
