"""Memory-mapped cropped Cylinder data, with bounded descriptors and visible halo."""
from pathlib import Path
from collections import OrderedDict
import json
import threading
import numpy as np
from .data import Window,ROLES,assert_isolation,sha256


def reconstruct_context(visible):
    """Same 64x128 observed context for EQGPT/U-Net/FNO, never future halo."""
    fields={}
    for f in ('u','v','p'):
        middle=visible[f];n,h,w=middle.shape;halo=visible['halo'][f]
        out=np.empty((n,h+2,w+2),dtype=middle.dtype)
        out[:,1:-1,1:-1]=middle
        out[:,0,:]=halo[:,:w+2];out[:,-1,:]=halo[:,w+2:2*(w+2)]
        out[:,1:-1,0]=halo[:,2*(w+2):2*(w+2)+h]
        out[:,1:-1,-1]=halo[:,2*(w+2)+h:]
        fields[f]=out
    return dict(fields,t=visible['t'],x=visible['context_x'],y=visible['context_y'])


def npy_header(path):
    with Path(path).open('rb') as stream:
        version=np.lib.format.read_magic(stream)
        reader=(np.lib.format.read_array_header_1_0 if version==(1,0)
                else np.lib.format.read_array_header_2_0)
        shape,_,dtype=reader(stream)
    if dtype.hasobject:raise ValueError('Object arrays forbidden')
    return shape,dtype


class PreparedSimulationData:
    LARGE=('u','v','p','u_halo','v_halo','p_halo')
    SMALL=('x','y','t','context_x','context_y','solid_mask','valid_mask')
    CACHE_TRAJECTORIES=4
    def __init__(self,manifest_path,config):
        self.path=Path(manifest_path).resolve();self.meta=json.loads(self.path.read_text());m=self.meta
        if m['branch']!='numerical' or m['revision']!=config['dataset_revision']:
            raise ValueError('Data branch/revision mismatch')
        for key in ('official_indices_audited','geometry_frozen','split_policy_frozen','source_alignment_verified','pressure_gauge_frozen'):
            if m.get(key) is not True:raise ValueError('Missing audit: '+key)
        if m.get('format')!='npy_directory_v1':raise ValueError('Unsupported prepared data format')
        if config['input_frames']!=20 or config['output_frames']!=20 or tuple(config['fields'])!=('u','v','p'):
            raise ValueError('Prepared v1 task dimensions do not match configuration')
        if config['region']['outer_cells']!=1 or config['region']['solid_interface_cells']!=1:
            raise ValueError('Prepared v1 mask is frozen at outer1/interface1; reprocess before changing it')
        self.roles={r:[Window(w['trajectory'],int(w['start'])) for w in m['roles'][r]] for r in ROLES}
        assert_isolation(self.roles,m['isolation_gap_frames'])
        self.role_sets={r:set(v) for r,v in self.roles.items()};self.trajectories={};self.access=[];self.test_unlocked=False
        self._cache=OrderedDict();self._cache_lock=threading.RLock()
        expected_files={f+'.npy' for f in self.LARGE+self.SMALL}
        # Verify every file, but read array headers only and do not retain 1196 mmaps.
        for sid,entry in m['trajectories'].items():
            folder=(self.path.parent/entry['path']).resolve()
            if not folder.is_relative_to(self.path.parent):raise ValueError('Trajectory escapes data root')
            if sha256(folder/'receipt.json')!=entry['receipt_sha256']:raise ValueError('Receipt mismatch')
            if set(entry['files_sha256'])!=expected_files:raise ValueError('Prepared v1 array set mismatch')
            for name,expected in entry['files_sha256'].items():
                if sha256(folder/name)!=expected:raise ValueError('Processed data hash mismatch: '+sid+'/'+name)
            for f in self.LARGE:
                shape,dtype=npy_header(folder/(f+'.npy'))
                expected=(3990,380) if f.endswith('_halo') else (3990,62,126)
                if shape!=expected or dtype!=np.dtype('float32'):raise ValueError('Field/halo header mismatch')
            small={f:np.load(folder/(f+'.npy'),allow_pickle=False) for f in self.SMALL}
            if small['valid_mask'].shape!=(62,126) or small['valid_mask'].dtype!=np.bool_ or not small['valid_mask'].any():raise ValueError('Mask shape/type mismatch')
            if small['solid_mask'].shape!=(62,126) or small['t'].shape!=(3990,):raise ValueError('Geometry/time shape mismatch')
            if any(small[f].shape!=(62,126) for f in ('x','y')):raise ValueError('Cropped coordinate shape mismatch')
            if any(small[f].shape!=(64,128) for f in ('context_x','context_y')):raise ValueError('Context coordinate shape mismatch')
            self.trajectories[sid]={'folder':folder,'shape':(3990,62,126),'small':small}
        for rows in self.roles.values():
            for w in rows:
                if w.start+40>self.trajectories[w.trajectory]['shape'][0]:raise ValueError('Incomplete window')
    def _arrays(self,sid):
        # Called under the lock; returned public observations are always copies.
        if sid in self._cache:
            self._cache.move_to_end(sid);return self._cache[sid]
        item=self.trajectories[sid]
        arrays={f:np.load(item['folder']/(f+'.npy'),mmap_mode='r',allow_pickle=False) for f in self.LARGE}
        arrays.update(item['small']);self._cache[sid]=arrays
        while len(self._cache)>self.CACHE_TRAJECTORIES:
            # Releasing the last memmap references closes their mappings/descriptors;
            # no private NumPy close API is used and no exposed view can be invalidated.
            self._cache.popitem(last=False)
        return arrays
    def _check(self,w,role):
        if role not in self.role_sets or w not in self.role_sets[role]:raise ValueError('Role mismatch')
        if role=='test' and not self.test_unlocked:raise ValueError('Test data locked')
    def visible(self,w,role):
        self._check(w,role)
        with self._cache_lock:
            a=self._arrays(w.trajectory);sl=slice(w.start,w.start+20)
            visible={f:np.asarray(a[f][sl]).copy() for f in ('u','v','p','t')}
            visible.update({f:np.asarray(a[f]).copy() for f in ('x','y','context_x','context_y')})
            visible['halo']={f:np.asarray(a[f+'_halo'][sl]).copy() for f in ('u','v','p')}
            visible['_cache_key']=(str(self.path),w.trajectory,w.start)
            times=np.asarray(a['t'][w.start+20:w.start+40]).copy();mask=np.asarray(a['valid_mask']).copy()
            self.access.append({'role':role,'part':'visible','trajectory':w.trajectory,'start':w.start})
        return visible,times,mask
    def target(self,w,role):
        self._check(w,role)
        with self._cache_lock:
            a=self._arrays(w.trajectory)
            target=np.stack([a[f][w.start+20:w.start+40] for f in ('u','v','p')],-1)
            mask=np.asarray(a['valid_mask']).copy()
            self.access.append({'role':role,'part':'target','trajectory':w.trajectory,'start':w.start})
        return target,mask
    def training_scale(self):
        scale=np.asarray(self.meta['normalization']['scale'],dtype=float)
        if scale.shape!=(3,) or not np.isfinite(scale).all() or (scale<=0).any():raise ValueError('Invalid training scale')
        return scale
    def training_mean(self):
        mean=np.asarray(self.meta['normalization']['mean'],dtype=float)
        if mean.shape!=(3,) or not np.isfinite(mean).all():raise ValueError('Invalid training mean')
        return mean
    def close(self):
        with self._cache_lock:self._cache.clear()
    def __getstate__(self):
        state=self.__dict__.copy();state['_cache']=OrderedDict();state.pop('_cache_lock',None);return state
    def __setstate__(self,state):
        self.__dict__.update(state);self._cache_lock=threading.RLock()
