"""Download and restore full processed Cylinder archives with checksums."""
import argparse,json,hashlib,urllib.request,tarfile,os
from pathlib import Path
BASE='https://github.com/xtr1976536/from-tokenizer-to-pde-discovery-2/releases/download/processed-cylinder-v1/'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);p.add_argument('--trajectory',action='append');a=p.parse_args()
 manifest=json.loads((Path(__file__).parent/'full_dataset_manifest.json').read_text());dest=a.destination.resolve();dest.mkdir(parents=True,exist_ok=True)
 for row in manifest['archives']:
  if a.trajectory and row['trajectory']!='metadata' and row['trajectory'] not in a.trajectory:continue
  archive=dest/row['asset'];tmp=archive.with_suffix('.partial')
  if not archive.exists() or digest(archive)!=row['sha256']:
   urllib.request.urlretrieve(BASE+row['asset'],tmp)
   if digest(tmp)!=row['sha256']:raise RuntimeError('Archive hash mismatch')
   tmp.replace(archive)
  with tarfile.open(archive) as t:
   for item in t.getmembers():
    if not (dest/item.name).resolve().is_relative_to(dest) or item.issym() or item.islnk():raise ValueError('Unsafe archive member')
   t.extractall(dest)
  for f in row['files']:
   path=dest/'cylinder_numerical_stage2_v1'/f['path']
   if digest(path)!=f['sha256']:raise RuntimeError('File hash mismatch: '+str(path))
  archive.unlink();print('Verified',row['trajectory'],flush=True)
if __name__=='__main__':main()
