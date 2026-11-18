"""Migrate active metadata to leakage-free per-trajectory seen temporal blocks.
No raw Arrow, field array, mask, EqGPT asset or baseline code is modified.
"""
from pathlib import Path
import sys,json,hashlib,shutil,datetime
import numpy as np
ROOT=Path('/data1/users/liugang/src/eq-bpe/project');sys.path.insert(0,str(ROOT))
try:from .index_policy import seen_windows,POLICY,QUOTAS
except ImportError:from index_policy import seen_windows,POLICY,QUOTAS
from stage2_main_v1.data import Window,assert_isolation
BASE=ROOT/'data/cylinder_numerical_stage2_v1';AUDIT=ROOT/'maintenance/stage2-seen75-20261115'

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False));tmp.replace(path)
def protected():
 found={}
 for name in ['baseline_code','baseline_configs','stage2_main_v1/legacy_eqgpt']:
  for p in (ROOT/name).rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts:found[str(p.relative_to(ROOT))]=sha(p)
 return found

def build_seen(root=ROOT):
 global ROOT,BASE,AUDIT
 ROOT=Path(root).resolve();BASE=ROOT/'data/cylinder_numerical_stage2_v1';AUDIT=ROOT/'maintenance/stage2-seen75-20261115';AUDIT.mkdir(parents=True,exist_ok=True)
 old=json.loads((BASE/'manifest.json').read_text())
 if old.get('split_policy')==POLICY:raise RuntimeError('Seen metadata already active; verify it instead of overwriting')
 history=BASE/'history/seen50_25_25_20261115'
 if history.exists():raise RuntimeError('History already exists; inspect any partial migration before retrying')
 history.mkdir(parents=True)
 cfg_path=ROOT/'stage2_main_v1/config.json';ready_path=ROOT/'stage2_main_v1/DATA_READY.json'
 for path in [BASE/'manifest.json',BASE/'normalization.json',BASE/'trajectory_roles.json',BASE/'time_blocks.json',cfg_path,ready_path]:
  if path.exists():shutil.copy2(path,history/path.name)
 (history/'receipts').mkdir()
 for sid,entry in old['trajectories'].items():shutil.copy2(BASE/entry['path']/'receipt.json',history/'receipts'/(sid+'.json'))
 write(history/'HISTORY.json',{'active':False,'purpose':'superseded seen50/25/25 metadata only; arrays remain at original data root','source_policy':old.get('split_policy'),'original_data_root':str(BASE),'manifest_sha256':sha(history/'manifest.json')})
 write(AUDIT/'protected-before.json',protected())
 cfg=json.loads(cfg_path.read_text());cfg['readiness']['simulation_data_audited']=False;write(cfg_path,cfg)
 write(ready_path,{'status':'SEEN_REPARTITION_PENDING_TWO_CHECKS','training_started':False,'eqgpt_modification_started':False})
 ids=sorted(old['trajectories'],key=lambda s:float(s[:-3]));lengths={sid:3990 for sid in ids}
 roles,blocks=seen_windows(lengths,525)
 assert_isolation({r:[Window(w['trajectory'],w['start']) for w in rows] for r,rows in roles.items()},40)
 count=0;total=np.zeros(3);squares=np.zeros(3);visible_counts={}
 for sid in ids:
  folder=BASE/old['trajectories'][sid]['path'];mask=np.load(folder/'valid_mask.npy')
  frames=sorted({i for w in roles['train_fit'] if w['trajectory']==sid for i in range(w['start'],w['start']+20)})
  visible_counts[sid]=len(frames);assert len(frames)==1100
  arrays=[np.load(folder/(f+'.npy'),mmap_mode='r') for f in ('u','v','p')]
  for lo in range(0,len(frames),64):
   x=np.stack([np.asarray(a[frames[lo:lo+64]][:,mask],dtype=np.float64) for a in arrays],-1).reshape(-1,3)
   total+=x.sum(0);squares+=(x*x).sum(0);count+=len(x)
  del arrays
  print('SEEN_STATS',sid,flush=True)
 mean=total/count;scale=np.sqrt(squares/count-mean**2)
 assert np.isfinite(scale).all() and np.all(scale>0)
 norm={'mean':mean.tolist(),'scale':scale.tolist(),'point_count':count,'source':'new seen train_fit visible prefixes only; no reward/validation/test/guard frames',
       'unique_visible_frames_per_trajectory':visible_counts,'fields':['u','v','p'],'split_policy':POLICY}
 # Receipts describe immutable data, not an obsolete trajectory-level assignment.
 entries={}
 for sid,entry in old['trajectories'].items():
  folder=BASE/entry['path'];receipt_path=folder/'receipt.json';receipt=json.loads(receipt_path.read_text())
  receipt.pop('role',None);receipt['split_membership']='defined only by active manifest.roles; every trajectory has all five temporal roles'
  write(receipt_path,receipt);entries[sid]=dict(entry,receipt_sha256=sha(receipt_path))
 new=dict(old)
 new.update(version='stage2-seen75-v2-20261115',split_policy=POLICY,split_policy_frozen=True,trajectory_disjoint=False,seen_trajectory_prediction=True,
  roles=roles,trajectories=entries,normalization=norm,role_trajectory_counts={r:len(ids) for r in roles},role_window_counts={r:len(v) for r,v in roles.items()},
  temporal_protocol={'block_length':250,'blocks_per_trajectory':16,'guard_left':20,'guard_right':20,'minimum_cross_role_gap':40,
   'actual_minimum_cross_role_gap':50,'window_length':40,'input_frames':20,'output_frames':20,'window_stride_all_roles':40,
   'block_quotas':QUOTAS,'selected_window_ratios':{'training_pool':.75,'validation':.125,'test':.125},
   'within_role_windows_overlap':False,'block_assignment':'independent per-trajectory seeded random permutation, as seen-style temporal blocks; not globally chronological'},
  trajectory_receipts_split_independent=True,baseline_protocol={'training_roles':['train_fit','reward_holdout'],'training_trajectory_count':92,'training_window_count':5520,
   'checkpoint_selection_role':'validation_stop','test_role':'test','normalization':'same new seen train_fit-visible statistics for all methods','original_baseline_source_and_optimizer_budget_unchanged':True})
 write(BASE/'time_blocks.json',{'policy':POLICY,'seed':525,'blocks':blocks})
 write(BASE/'trajectory_roles.json',{'policy':POLICY,'groups':{r:ids for r in roles},'note':'Trajectory IDs are shared by all roles; complete windows/frames are disjoint'})
 write(BASE/'normalization.json',norm);write(BASE/'manifest.json',new)
 cfg['version']='stage2-main-seen75-v2-20261115';cfg['assets']['split_policy']=POLICY
 cfg['baseline']['training_roles']=['train_fit','reward_holdout'];cfg['baseline']['checkpoint_selection_role']='validation_stop'
 write(cfg_path,cfg)
 write(AUDIT/'migration.json',{'status':'METADATA_MIGRATED_PENDING_CHECKS','split_policy':POLICY,'trajectory_count':len(ids),
  'role_window_counts':new['role_window_counts'],'physical_arrays_modified':False,'spatial_processing_changed':False,
  'raw_data_modified':False,'eqgpt_modified':False,'baseline_code_modified':False,'training_started':False})
 print('SEEN_METADATA_WRITTEN',new['role_window_counts'],flush=True)
 return new
if __name__=='__main__':build_seen()
