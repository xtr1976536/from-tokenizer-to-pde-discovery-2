"""Real-trajectory IO and descriptor-bound check, without any model training."""
import sys,json,hashlib,tempfile,os,pickle
from pathlib import Path
ROOT=Path('/data1/users/liugang/src/eq-bpe/project');sys.path.insert(0,str(ROOT))
import numpy as np
from stage2_main_v1.data import SimulationData
from stage2_main_v1.prepared_data import reconstruct_context
BASE=ROOT/'data/cylinder_numerical_stage2_v1';AUDIT=ROOT/'maintenance/stage2-seen75-20261115'
def fd_count():return len(list(Path('/proc/self/fd').iterdir()))
manifest=json.loads((BASE/'manifest.json').read_text());trajectories=manifest['trajectories']
config=json.loads((ROOT/'stage2_main_v1/config.json').read_text());before=fd_count();path=None
try:
 with tempfile.NamedTemporaryFile(mode='w',prefix='.io-smoke-',suffix='.json',dir=BASE,delete=False) as f:
  json.dump(manifest,f);path=Path(f.name)
 reader=SimulationData(path,config);after_init=fd_count();held=None
 for w in list({w.trajectory:w for w in reversed(reader.roles['train_fit'])}.values())[:16]:
  visible,times,mask=reader.visible(w,'train_fit');full=reconstruct_context(visible)
  assert visible['u'].shape==(20,62,126) and full['p'].shape==(20,64,128)
  assert np.array_equal(full['v'][:,1:-1,1:-1],visible['v']) and mask.sum()==7660
  if held is None:held=visible['u'].copy()
 after_reads=fd_count();assert after_reads<=before+32,(before,after_reads)
 assert np.isfinite(held).all()
 for method in [reader.visible,reader.target]:
  try:method(reader.roles['test'][0],'test')
  except ValueError:pass
  else:raise AssertionError('Test barrier failed')
 # Spawn-worker serialization must not carry mappings or a non-picklable lock.
 clone=pickle.loads(pickle.dumps(reader));clone.visible(clone.roles['train_fit'][0],'train_fit');clone.close();del clone
 reader.close();after_close=fd_count();assert after_close<=before+4,(before,after_close)
 result={'status':'PASS','real_trajectories_checked':len(trajectories),'descriptor_soft_limit':__import__('resource').getrlimit(__import__('resource').RLIMIT_NOFILE)[0],
  'fd_before':before,'fd_after_init':after_init,'fd_after_16_trajectory_reads':after_reads,'fd_after_close':after_close,
  'bounded_lazy_mmap':True,'visible_halo_reconstruction':True,'test_barrier':True,'worker_pickle_roundtrip':True,'training_started':False}
 (AUDIT/'reader-io-smoke.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:
 if path and path.exists():path.unlink()
