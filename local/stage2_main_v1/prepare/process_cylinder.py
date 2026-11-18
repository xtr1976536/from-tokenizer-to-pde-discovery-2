"""Streaming, lossless-in-value Cylinder numerical crop, mask and split preparation.
No temporal filter, interpolation, pressure dropout, noise or model fitting.
"""
import sys
from pathlib import Path
ROOT=Path('/data1/users/liugang/src/eq-bpe/project');sys.path.insert(0,str(ROOT))
import hashlib,json,time
import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc
from scipy.ndimage import label,binary_dilation
try:from .index_policy import released_audit,POLICY
except ImportError:from index_policy import released_audit,POLICY
from stage2_main_v1.data import valid_region
REV='0ae4426085d250787f96d5456bc0d30ce5f277d2'
RAW=ROOT/'data/realpdebench/cylinder/hf_dataset/numerical'
OUT=ROOT/'data/cylinder_numerical_stage2_v1'
AUDIT=ROOT/'maintenance/stage2-data-20261115'


def write(p,value):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False));tmp.replace(p)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def read_shard(path):
 memory=pa.memory_map(str(path),'r');table=ipc.open_stream(memory).read_all()
 if len(table)!=1:raise ValueError('Pinned dataset requires exactly one complete trajectory/shard')
 row={n:table[n][0] for n in table.column_names};shape=tuple(row[k].as_py() for k in ['shape_t','shape_h','shape_w'])
 def array(key,shape):
  if not row[key].is_valid:raise ValueError('Missing '+key)
  buf=row[key].as_buffer();size=int(np.prod(shape));dtype='<f4' if len(buf)==size*4 else '<f8' if len(buf)==size*8 else None
  if dtype is None:raise ValueError('Binary byte count mismatch: '+key)
  if key in ('u','v','p') and dtype!='<f4':raise ValueError('Unexpected field dtype')
  return np.frombuffer(buf,dtype=dtype).reshape(shape)
 fields={f:array(f,shape) for f in ('u','v','p')}
 fields.update(x=array('x',shape[1:]),y=array('y',shape[1:]),t=array('t',(shape[0],)))
 return row['sim_id'].as_py(),fields,memory,table


def infer_geometry(fields):
 # Static zero-velocity body support inferred from first 20 frames of TRAIN ONLY.
 z=np.all((fields['u'][:20]==0)&(fields['v'][:20]==0),axis=0)
 components,n=label(z)
 sizes=np.bincount(components.ravel());sizes[0]=0
 if n<1 or sizes.max()<10:raise ValueError('No closed stationary cylinder support')
 support=components==int(sizes.argmax());yy,xx=np.where(support)
 if min(xx.min(),yy.min())==0 or xx.max()==z.shape[1]-1 or yy.max()==z.shape[0]-1:raise ValueError('Body support touches outer frame')
 x,y=fields['x'],fields['y'];cx=float(x[support].mean());cy=float(y[support].mean());radius=.015
 # Official Cylinder diameter is 30 mm. Coordinates in the release are metres.
 if np.max(np.hypot(x[support]-cx,y[support]-cy))>radius+max(np.ptp(x)/x.shape[1],np.ptp(y)/y.shape[0]):
  raise ValueError('Body support inconsistent with 30-mm cylinder')
 return {'center_x_m':cx,'center_y_m':cy,'radius_m':radius,
         'center_source':'centroid of largest closed exact-zero u/v support in first 20 training frames',
         'diameter_source':'official Cylinder geometry, D=30mm',
         'raw_zero_support_points':int(support.sum()),'raw_zero_bounds':[int(xx.min()),int(xx.max()),int(yy.min()),int(yy.max())]}


def process(path,geometry,groups):
 sid,a,memory,table=read_shard(path)
 if a['u'].shape!=(3990,128,256):raise ValueError('Pinned shape differs from audited first shard')
 if not np.all(np.diff(a['t'])>0) or not np.allclose(np.diff(a['t']),.005,atol=1e-10,rtol=1e-6):raise ValueError('Time step mismatch')
 x=a['x'][::2,::2];y=a['y'][::2,::2]
 if not np.allclose(x,x[:1,:]) or not np.allclose(y,y[:,:1]):raise ValueError('Expected rectilinear grid')
 if not np.all(np.diff(x[0])>0) or not np.all(np.diff(y[:,0])>0):raise ValueError('Grid orientation mismatch')
 solid=(x-geometry['center_x_m'])**2+(y-geometry['center_y_m'])**2<=geometry['radius_m']**2
 valid=valid_region(solid,1,1);cropped_mask=valid[1:-1,1:-1]
 folder=OUT/'trajectories'/sid[:-3];folder.mkdir(parents=True,exist_ok=True)
 receipt=folder/'receipt.json'
 if receipt.exists():
  old=json.loads(receipt.read_text())
  if old['source_sha256']!=sha(path):raise ValueError('Raw shard changed')
  print('PROCESSED_EXISTS',sid,flush=True);return old
 np.save(folder/'x.npy',x[1:-1,1:-1]);np.save(folder/'y.npy',y[1:-1,1:-1]);np.save(folder/'t.npy',a['t'])
 np.save(folder/'solid_mask.npy',solid[1:-1,1:-1]);np.save(folder/'valid_mask.npy',cropped_mask)
 # Geometry plus the removed spatial halo allows all models to access exactly
 # the same 64x128 input context, while loss/evaluation use the cropped region.
 np.save(folder/'context_x.npy',x);np.save(folder/'context_y.npy',y)
 field_ranges={}
 for f in ('u','v','p'):
  data=a[f];out=np.lib.format.open_memmap(folder/(f+'.npy'),mode='w+',dtype='<f4',shape=(3990,62,126))
  halo=np.lib.format.open_memmap(folder/(f+'_halo.npy'),mode='w+',dtype='<f4',shape=(3990,2*128+2*62))
  low=float('inf');high=-float('inf')
  for start in range(0,3990,64):
   native=data[start:start+64,::2,::2]
   if not np.isfinite(native).all():raise ValueError('Nonfinite '+f)
   out[start:start+64]=native[:,1:-1,1:-1]
   halo[start:start+64]=np.concatenate([native[:,0,:],native[:,-1,:],native[:,1:-1,0],native[:,1:-1,-1]],axis=1)
   low=min(low,float(native[:,valid].min()));high=max(high,float(native[:,valid].max()))
  out.flush();halo.flush();del out,halo
  field_ranges[f]=[low,high]
 role=next(r for r,ids in groups.items() if sid in ids)
 files={p.name:sha(p) for p in folder.glob('*.npy')}
 result={'trajectory':sid,'role':role,'source_path':str(path.relative_to(ROOT)),
  'source_sha256':sha(path),'raw_shape':[3990,128,256],'context_shape':[3990,64,128],
  'shape':[3990,62,126],'time_step':.005,'time_range':[float(a['t'][0]),float(a['t'][-1])],
  'spatial_subsample_stride':2,'outer_cells_removed':1,'valid_points':int(cropped_mask.sum()),
  'solid_points':int(solid[1:-1,1:-1].sum()),'ranges':field_ranges,'files_sha256':files,
  'added_temporal_filter':False,'pressure_policy':'as_released_no_dropout_no_gauge_transform',
  'u_v_p_alignment':'same Arrow row, same frame/spatial slicing',
  'format':'npy_directory_v1'}
 write(receipt,result);print('PROCESSED',sid,role,result['valid_points'],flush=True)
 del a,table;memory.close();return result


def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'manifest.json').exists():
  active=json.loads((OUT/'manifest.json').read_text())
  if active.get('split_policy')==POLICY:
   print('SEEN_SPATIAL_DATA_ALREADY_PREPARED; use check_seen.py for verification');return
  raise RuntimeError('Existing spatial data: migrate metadata with seen_split.py; do not regenerate old trajectory split')
 official,ids=released_audit(RAW.parent)
 groups={'all_seen_trajectories':ids}
 write(OUT/'official_index_audit.json',official)
 geometry_path=OUT/'geometry.json';geometry=json.loads(geometry_path.read_text()) if geometry_path.exists() else None
 completed={}
 while len(completed)<92:
  for path in sorted(RAW.glob('*.arrow')):
   if not (AUDIT/('verified_'+path.name+'.json')).exists() or path.name in completed:continue
   if geometry is None:
    sid,a,memory,table=read_shard(path)
    if sid!='10031.h5':continue
    geometry=infer_geometry(a);geometry['training_reference_trajectory']=sid
    geometry['reference_frames']=[0,20];geometry['reference_use']='static domain metadata; these frames are guards in seen split'
    write(geometry_path,geometry);del a,table;memory.close()
   completed[path.name]=process(path,geometry,groups)
  if len(completed)<92:time.sleep(10)
 records={r['trajectory']:r for r in completed.values()};assert set(records)==set(ids)
 trajectories={sid:{'path':'trajectories/'+sid[:-3],'format':'npy_directory_v1','files_sha256':r['files_sha256'],'receipt_sha256':sha(OUT/'trajectories'/sid[:-3]/'receipt.json')} for sid,r in records.items()}
 manifest={'revision':REV,'branch':'numerical','format':'npy_directory_v1','split_policy':'spatial_artifacts_pending_seen',
  'official_indices_audited':True,'geometry_frozen':True,'source_alignment_verified':True,'pressure_gauge_frozen':True,
  'pressure_gauge_policy':'as_released_no_gauge_transform','isolation_gap_frames':40,'fields':['u','v','p'],
  'input_frames':20,'output_frames':20,'context_shape':[64,128],'crop_shape':[62,126],
  'trajectories':trajectories,'official_index_source_hashes':official['source_hashes']}
 write(OUT/'manifest.json',manifest)
 try:from .seen_split import build_seen
 except ImportError:from seen_split import build_seen
 build_seen(ROOT)
 print('SPATIAL_AND_SEEN_METADATA_PREPARED; run check_seen.py twice-pass audit before marking ready')
if __name__=='__main__':main()
