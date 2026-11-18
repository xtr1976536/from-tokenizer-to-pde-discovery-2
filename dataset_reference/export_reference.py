from pathlib import Path
import json,hashlib
import numpy as np
import pyarrow as pa,pyarrow.ipc as ipc
base=Path('/data1/users/liugang/src/eq-bpe/project');raw=base/'data/realpdebench/cylinder/hf_dataset/numerical';processed=base/'data/cylinder_numerical_stage2_v1'
out=base/'exports/dataset-reference-samples';out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((processed/'manifest.json').read_text());sid='10031.h5'
w=next(w for w in manifest['roles']['train_fit'] if w['trajectory']==sid);start=w['start'];stop=start+40
path=raw/'data-00000-of-00092.arrow';mapping=pa.memory_map(str(path),'r');table=ipc.open_stream(mapping).read_all();row={n:table[n][0] for n in table.column_names};assert row['sim_id'].as_py()==sid
shape=tuple(row[k].as_py() for k in ['shape_t','shape_h','shape_w'])
def read(k,shape):
 data=row[k].as_buffer();dtype='<f4' if len(data)==np.prod(shape)*4 else '<f8';return np.frombuffer(data,dtype).reshape(shape)
a={f:read(f,shape)[start:stop].copy() for f in ['u','v','p']};a.update(x=read('x',shape[1:]).copy(),y=read('y',shape[1:]).copy(),t=read('t',(shape[0],))[start:stop].copy())
np.savez_compressed(out/'released_10031_train_window.npz',**a)
p=processed/'trajectories/10031';b={f:np.load(p/(f+'.npy'),mmap_mode='r')[start:stop].copy() for f in ['u','v','p','t','u_halo','v_halo','p_halo']}
b.update({f:np.load(p/(f+'.npy')) for f in ['x','y','context_x','context_y','solid_mask','valid_mask']})
np.savez_compressed(out/'processed_10031_train_window.npz',**b)
checks={}
for f in ['u','v','p']:
 native=a[f][:,::2,::2];checks[f+'_exact_crop']=bool(np.array_equal(b[f],native[:,1:-1,1:-1]))
 halo=np.concatenate([native[:,0,:],native[:,-1,:],native[:,1:-1,0],native[:,1:-1,-1]],axis=1)
 checks[f+'_exact_halo']=bool(np.array_equal(b[f+'_halo'],halo))
assert all(checks.values())
meta=dict(trajectory=sid,role='train_fit',start_frame_0based=start,stop_frame_exclusive=stop,input_frames=20,output_frames=20,raw_full_shape=shape,excerpt=True,revision=manifest['revision'],source_shard=path.name,source_sha256=json.loads((p/'receipt.json').read_text())['source_sha256'],checks=checks,valid_points=int(b['valid_mask'].sum()),license='CC BY-NC 4.0; see upstream dataset',upstream='https://huggingface.co/datasets/AI4Science-WestlakeU/RealPDEBench')
meta['files']={f.name:dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in out.glob('*.npz')}
(out/'sample_manifest.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
