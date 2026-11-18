"""Verify published git files and Release weight size / GitHub SHA-256 digests."""
import hashlib,json,urllib.request,argparse,os
from pathlib import Path
REPO='xtr1976536/from-tokenizer-to-pde-discovery-2'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--release',action='store_true');a=ap.parse_args();root=Path(__file__).resolve().parents[1]
 errors=[]
 for row in json.loads((root/'manifests/published_files.json').read_text()):
  p=root/row['path']
  if not p.is_file():errors.append('missing '+row['path']);continue
  if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('changed '+row['path'])
 if a.release:
  assets={};page=1
  req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/releases/tags/archive-2026-11-18')
  token=os.environ.get('GH_TOKEN')
  if token:req.add_header('Authorization','Bearer '+token)
  release=json.load(urllib.request.urlopen(req))
  while True:
   req=urllib.request.Request(release['assets_url']+f'?per_page=100&page={page}')
   if token:req.add_header('Authorization','Bearer '+token)
   items=json.load(urllib.request.urlopen(req))
   if not items:break
   assets.update({x['name']:x for x in items});page+=1
  for row in json.loads((root/'manifests/server_sources.json').read_text()):
   if row['kind']!='weight':continue
   asset=assets.get(row['asset'])
   if not asset:errors.append('missing asset '+row['asset']);continue
   if asset['size']!=row['bytes']:errors.append('size '+row['asset'])
   if asset.get('digest')!='sha256:'+row['sha256']:errors.append('digest '+row['asset'])
 print(json.dumps({'errors':errors,'status':'PASS' if not errors else 'FAIL'},indent=2))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
