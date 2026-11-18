from pathlib import Path
import json,hashlib
import numpy as np
p=Path(__file__).resolve().parent
meta=json.loads((p/'sample_manifest.json').read_text())
for name,row in meta['files'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==row['sha256']
a=np.load(p/'released_10031_train_window.npz');b=np.load(p/'processed_10031_train_window.npz')
for f in ['u','v','p']:
 native=a[f][:,::2,::2]
 assert np.array_equal(b[f],native[:,1:-1,1:-1])
 halo=np.concatenate([native[:,0,:],native[:,-1,:],native[:,1:-1,0],native[:,1:-1,-1]],axis=1)
 assert np.array_equal(halo,b[f+'_halo'])
for f in ['x','y']:assert np.array_equal(b[f],a[f][::2,::2][1:-1,1:-1])
assert np.array_equal(a['t'],b['t'])
assert int(b['valid_mask'].sum())==meta['valid_points']
print('PASS: file SHA256, u/v/p crop, halo, coordinates, time and valid mask count')
