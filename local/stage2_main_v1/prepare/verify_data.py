"""Independent two-pass audit of every raw shard, processed value and split.
Pass1: LFS/content hashes, full raw-to-crop equality, masks and visible halos.
Pass2: independent processed-array/role integrity + train-only normalization.
"""
from pathlib import Path
import hashlib,json,time,itertools,sys
import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc
from scipy.ndimage import binary_dilation
ROOT=Path('/data1/users/liugang/src/eq-bpe/project')
BASE=ROOT/'data/cylinder_numerical_stage2_v1';AUDIT=ROOT/'maintenance/stage2-seen75-20261115';AUDIT.mkdir(parents=True,exist_ok=True)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(name,result):
 (AUDIT/name).write_text(json.dumps(result,indent=2,allow_nan=False))
def raw_row(path):
 mmap=pa.memory_map(str(path),'r');table=ipc.open_stream(mmap).read_all()
 assert len(table)==1
 row={n:table[n][0] for n in table.column_names}
 return row,mmap,table

def first_pass():
 manifest=json.loads((BASE/'manifest.json').read_text());geo=json.loads((BASE/'geometry.json').read_text())
 remote={r['path']:r for r in json.loads((ROOT/'maintenance/stage2-data-20261115/remote-files.json').read_text()) if r['path'].endswith('.arrow')}
 receipts={json.loads(p.read_text())['source_path']:p for p in (BASE/'trajectories').glob('*/receipt.json')}
 assert len(remote)==len(receipts)==92
 done=[]
 for name,r in sorted(remote.items()):
  raw=ROOT/'data/realpdebench'/name;assert raw.stat().st_size==r['size'];assert sha(raw)==r['sha256']
  rec_path=receipts[str(raw.relative_to(ROOT))];rec=json.loads(rec_path.read_text());folder=rec_path.parent
  row,mmap,table=raw_row(raw);sid=row['sim_id'].as_py();assert sid==rec['trajectory']
  shape=tuple(row[k].as_py() for k in ('shape_t','shape_h','shape_w'));assert shape==(3990,128,256)
  x=np.frombuffer(row['x'].as_buffer(),'<f8').reshape(shape[1:])[::2,::2]
  y=np.frombuffer(row['y'].as_buffer(),'<f8').reshape(shape[1:])[::2,::2]
  t=np.frombuffer(row['t'].as_buffer(),'<f8');assert t.shape==(3990,);assert np.allclose(np.diff(t),.005,rtol=1e-7,atol=1e-12)
  assert np.array_equal(np.load(folder/'x.npy'),x[1:-1,1:-1]);assert np.array_equal(np.load(folder/'y.npy'),y[1:-1,1:-1]);assert np.array_equal(np.load(folder/'t.npy'),t)
  raw_x=np.frombuffer(row['x'].as_buffer(),'<f8').reshape(shape[1:]);raw_y=np.frombuffer(row['y'].as_buffer(),'<f8').reshape(shape[1:])
  uz=np.frombuffer(row['u'].as_buffer(),'<f4').reshape(shape)[:20]
  vz=np.frombuffer(row['v'].as_buffer(),'<f4').reshape(shape)[:20]
  support=np.all((uz==0)&(vz==0),axis=0)
  from scipy.ndimage import label
  labels,n=label(support);sizes=np.bincount(labels.ravel());sizes[0]=0;body=labels==int(sizes.argmax())
  assert body.sum()>10
  assert abs(float(raw_x[body].mean())-geo['center_x_m'])<.0015
  assert abs(float(raw_y[body].mean())-geo['center_y_m'])<.0015
  assert np.max(np.hypot(raw_x[body]-geo['center_x_m'],raw_y[body]-geo['center_y_m']))<.0165
  del uz,vz
  solid=(x-geo['center_x_m'])**2+(y-geo['center_y_m'])**2<=geo['radius_m']**2
  expected=~binary_dilation(solid,structure=np.ones((3,3),bool));expected=expected[1:-1,1:-1]
  assert np.array_equal(np.load(folder/'valid_mask.npy'),expected)
  assert np.array_equal(np.load(folder/'solid_mask.npy'),solid[1:-1,1:-1])
  for f in ('u','v','p'):
   source=np.frombuffer(row[f].as_buffer(),'<f4').reshape(shape)
   crop=np.load(folder/(f+'.npy'),mmap_mode='r');halo=np.load(folder/(f+'_halo.npy'),mmap_mode='r')
   assert crop.shape==(3990,62,126) and halo.shape==(3990,380)
   for i in range(0,3990,64):
    native=source[i:i+64,::2,::2]
    assert np.array_equal(crop[i:i+64],native[:,1:-1,1:-1])
    assert np.array_equal(halo[i:i+64],np.concatenate([native[:,0,:],native[:,-1,:],native[:,1:-1,0],native[:,1:-1,-1]],1))
   del source,crop,halo
  for filename,h in rec['files_sha256'].items():assert sha(folder/filename)==h
  assert sha(rec_path)==manifest['trajectories'][sid]['receipt_sha256']
  done.append(sid);print('ROUND1_VERIFIED',sid,flush=True)
  del row,table;mmap.close()
 result={'status':'PASS','round':1,'trajectories':len(done),'raw_shards_lfs_hash_verified':92,
  'all_processed_values_equal_expected_slice':True,'all_halos_match_visible_source':True,
  'all_geometry_masks_independently_recomputed':True,'all_saved_hashes_match':True}
 write('spatial-check.json',result)
 return result

def main():
 # The active task is seen prediction; the superseded whole-trajectory checker
 # must never overwrite current verification receipts or assume disjoint IDs.
 try:from .check_seen import first,second
 except ImportError:from check_seen import first,second
 if '--spatial' in sys.argv:
  first_pass()
 print(json.dumps(first()),flush=True);print(json.dumps(second()),flush=True)
if __name__=='__main__':main()
