"""Bounded, resumable HTTP range downloads of the pinned Cylinder shards only."""
import concurrent.futures as cf
import hashlib,json,os,threading,time
from pathlib import Path
import requests
ROOT=Path('/data1/users/liugang/src/eq-bpe/project')
AUDIT=ROOT/'maintenance/stage2-data-20261115';DEST=ROOT/'data/realpdebench'
REV='0ae4426085d250787f96d5456bc0d30ce5f277d2'
PARTS=DEST/'.cylinder-numerical-parts';CHUNK=64*1024*1024
lock=threading.Lock();urls={};local=threading.local()

def session():
 if not hasattr(local,'s'):local.s=requests.Session()
 return local.s

def url_for(row,refresh=False):
 name=row['path']
 with lock:
  if not refresh and name in urls:return urls[name]
 resolve=f'https://hf-mirror.com/datasets/AI4Science-WestlakeU/RealPDEBench/resolve/{REV}/{name}'
 r=session().get(resolve,headers={'Range':'bytes=0-0'},stream=True,timeout=(20,90));r.raise_for_status();url=r.url;r.close()
 with lock:urls[name]=url
 return url

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def part(row,start,end):
 folder=PARTS/Path(row['path']).name;folder.mkdir(parents=True,exist_ok=True)
 path=folder/f'{start:012d}.part';size=end-start+1
 if path.exists() and path.stat().st_size==size:return row['path'],start
 tmp=path.with_suffix('.partial')
 for attempt in range(8):
  try:
   url=url_for(row,refresh=attempt>0)
   offset=tmp.stat().st_size if tmp.exists() else 0
   if offset>size:tmp.unlink();offset=0
   if offset==size:tmp.replace(path);return row['path'],start
   actual_start=start+offset
   with session().get(url,headers={'Range':f'bytes={actual_start}-{end}'},stream=True,timeout=(20,120)) as r:
    if r.status_code!=206 or r.headers.get('Content-Range')!=f'bytes {actual_start}-{end}/{row["size"]}':raise ValueError(f'Wrong range response: {r.status_code}')
    with tmp.open('ab' if offset else 'wb') as f:
     for chunk in r.iter_content(1024*1024):f.write(chunk)
   if tmp.stat().st_size!=size:raise ValueError('Truncated chunk')
   tmp.replace(path)
   return row['path'],start
  except Exception as e:
   print('RANGE_RETRY',Path(row['path']).name,start,attempt,type(e).__name__,flush=True)
   if attempt==7:raise
   time.sleep(min(attempt+1,8))

def finish(row):
 target=DEST/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
 receipt=AUDIT/('verified_'+target.name+'.json')
 if target.exists() and target.stat().st_size==row['size'] and sha(target)==row['sha256']:
  receipt.write_text(json.dumps(row));return
 folder=PARTS/target.name;tmp=target.with_suffix('.assembling')
 h=hashlib.sha256()
 with tmp.open('wb') as out:
  for start in range(0,row['size'],CHUNK):
   with (folder/f'{start:012d}.part').open('rb') as inp:
    for b in iter(lambda:inp.read(8*1024*1024),b''):h.update(b);out.write(b)
 if h.hexdigest()!=row['sha256']:raise ValueError('Full shard LFS SHA256 mismatch')
 tmp.replace(target);receipt.write_text(json.dumps(row))
 for p in folder.iterdir():p.unlink()
 folder.rmdir();print('VERIFIED',target.name,row['size'],flush=True)

if __name__=='__main__':
 rows=[r for r in json.loads((AUDIT/'remote-files.json').read_text()) if r['path'].endswith('.arrow')]
 pending=[]
 for row in rows:
  path=DEST/row['path'];receipt=AUDIT/('verified_'+path.name+'.json')
  if receipt.exists() and path.exists() and path.stat().st_size==row['size']:continue
  pending.append(row)
 # Recover complete chunks from the previous contiguous HF transfer.
 for row in pending:
  if not row['path'].endswith('data-00000-of-00092.arrow'):continue
  for old in (DEST/'.cache/huggingface/download/cylinder/hf_dataset/numerical').glob('*.incomplete'):
   if row['sha256'] not in old.name:continue
   folder=PARTS/Path(row['path']).name;folder.mkdir(parents=True,exist_ok=True)
   with old.open('rb') as inp:
    for start in range(0,old.stat().st_size-CHUNK+1,CHUNK):
     path=folder/f'{start:012d}.part'
     if not path.exists():path.write_bytes(inp.read(CHUNK))
     else:inp.seek(CHUNK,1)
 print('START_RANGES',len(pending),'workers=128',flush=True)
 byname={r['path']:r for r in pending};remaining={r['path']:(r['size']+CHUNK-1)//CHUNK for r in pending}
 with cf.ThreadPoolExecutor(max_workers=128) as pool:
  futures=[pool.submit(part,r,start,min(start+CHUNK,r['size'])-1) for r in pending for start in range(0,r['size'],CHUNK)]
  done=0
  for future in cf.as_completed(futures):
   name,start=future.result();remaining[name]-=1;done+=1
   if done%32==0:print('CHUNKS',done,'/',len(futures),flush=True)
   if remaining[name]==0:finish(byname[name])
 # Metadata uses normal small-file download separately; never fetch real/other scenarios.
 (AUDIT/'download_complete.json').write_text(json.dumps({'revision':REV,'shards':len(rows),'status':'COMPLETE'}))
 print('DOWNLOAD_COMPLETE',flush=True)
