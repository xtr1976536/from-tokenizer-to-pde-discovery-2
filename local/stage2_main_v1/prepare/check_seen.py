"""Two independent checks of active seen-window isolation and train-only scaling."""
from pathlib import Path
import sys,json,itertools,hashlib,pickle
import numpy as np
ROOT=Path('/data1/users/liugang/src/eq-bpe/project');sys.path.insert(0,str(ROOT))
from stage2_main_v1.data import SimulationData
BASE=ROOT/'data/cylinder_numerical_stage2_v1';AUDIT=ROOT/'maintenance/stage2-seen75-20261115'
ROLES=('train_fit','reward_holdout','validation_select','validation_stop','test')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(name,obj):(AUDIT/name).write_text(json.dumps(obj,indent=2,allow_nan=False))
def protected_check():
 for rel,h in json.loads((AUDIT/'protected-before.json').read_text()).items():assert sha(ROOT/rel)==h,rel

def first():
 m=json.loads((BASE/'manifest.json').read_text());old=json.loads((BASE/'history/seen50_25_25_20261115/manifest.json').read_text());blocks=json.loads((BASE/'time_blocks.json').read_text())['blocks']
 ids=set(m['trajectories']);assert len(ids)==92 and not m['trajectory_disjoint']
 frames={r:set() for r in ROLES};counts={r:{} for r in ROLES};starts={};minimum_gap=10**9
 for sid in ids:
  assert len(blocks[sid])==16
  owner=np.full(3990,-1,dtype=np.int8);observations=[]
  for role_index,role in enumerate(ROLES):
   rows=[w for w in m['roles'][role] if w['trajectory']==sid];counts[role][sid]=len(rows)
   assert len(rows)=={'train_fit':55,'reward_holdout':5,'validation_select':5,'validation_stop':5,'test':10}[role]
   for w in rows:
    lo=w['start'];hi=lo+40;assert isinstance(lo,int) and 0<=lo<hi<=3990
    b=blocks[sid][w['block']];assert b['role']==role and b['usable_start']<=lo and hi<=b['usable_stop']
    assert (lo-b['usable_start'])%40==0
    assert np.all(owner[lo:hi]==-1),'ANY overlap, including within same role'
    owner[lo:hi]=role_index;observations.append((lo,hi,role));frames[role].update((sid,i) for i in range(lo,hi))
  assert np.count_nonzero(owner!=-1)==3200 and np.count_nonzero(owner==-1)==790
  assert np.all(owner[:20]==-1),'Geometry reference guard must not become a test/fit window'
  for a,b in zip(sorted(observations),sorted(observations)[1:]):
   assert a[1]<=b[0]
   if a[2]!=b[2]:minimum_gap=min(minimum_gap,b[0]-a[1]);assert b[0]-a[1]>=40
  # Check all stored arrays against the pre-migration hashes, not mutable labels.
  entry=m['trajectories'][sid];prior=old['trajectories'][sid]
  assert entry['files_sha256']==prior['files_sha256']
  folder=BASE/entry['path']
  for file,h in prior['files_sha256'].items():assert sha(folder/file)==h,(sid,file)
  assert sha(folder/'receipt.json')==entry['receipt_sha256']
  print('ROUND1_SEEN',sid,flush=True)
 for a,b in itertools.combinations(ROLES,2):assert not frames[a]&frames[b]
 for role in ROLES:
  assert set(counts[role])==ids and len(frames[role])==len(m['roles'][role])*40
 total_windows=sum(len(m['roles'][r]) for r in ROLES)
 ratios={'training_pool':(len(m['roles']['train_fit'])+len(m['roles']['reward_holdout']))/total_windows,
         'validation':(len(m['roles']['validation_select'])+len(m['roles']['validation_stop']))/total_windows,
         'test':len(m['roles']['test'])/total_windows}
 assert ratios=={'training_pool':.75,'validation':.125,'test':.125}
 assert m['temporal_protocol']['selected_window_ratios']==ratios
 for split,h in m['official_index_source_hashes'].items():assert sha(ROOT/f'data/realpdebench/cylinder/hf_dataset/{split}_index_numerical.json')==h
 protected_check()
 result={'status':'PASS','round':1,'trajectories_in_each_role':{r:len(counts[r]) for r in ROLES},'window_counts':{r:len(m['roles'][r]) for r in ROLES},
  'selected_window_ratios':ratios,'same_trajectory_seen_in_train_validation_test':True,'shared_frames_between_any_roles':0,'overlap_within_any_role':0,
  'minimum_cross_role_gap_frames':minimum_gap,'unused_frames_per_trajectory':790,'all_windows_complete':True,
  'all_field_coordinate_mask_halo_hashes_unchanged':True,'official_indices_unchanged':True,'eqgpt_and_baseline_unchanged':True}
 write('check-round1.json',result);return result

def second():
 m=json.loads((BASE/'manifest.json').read_text());cfg=json.loads((ROOT/'stage2_main_v1/config.json').read_text())
 reader=SimulationData(BASE/'manifest.json',cfg)
 # Independent role interval scan uses half-open intervals, not producer blocks.
 records={sid:[] for sid in m['trajectories']}
 for role,rows in reader.roles.items():
  for w in rows:records[w.trajectory].append((w.start,w.start+40,role))
 for sid,entries in records.items():
  assert set(r[2] for r in entries)==set(ROLES)
  entries.sort()
  for a,b in zip(entries,entries[1:]):
   assert a[1]<=b[0]
   if a[2]!=b[2]:assert b[0]-a[1]>=40
 count=0;mean=np.zeros(3);m2=np.zeros(3)
 for sid,entry in sorted(m['trajectories'].items()):
  folder=BASE/entry['path'];mask=np.load(folder/'valid_mask.npy');assert mask.sum()==7660
  fit=[w for w in reader.roles['train_fit'] if w.trajectory==sid]
  visible=sorted({i for w in fit for i in range(w.start,w.start+20)})
  assert len(visible)==1100
  forbidden={i for lo,hi,role in records[sid] if role!='train_fit' for i in range(lo,hi)}
  assert not set(visible)&forbidden
  arrays=[np.load(folder/(f+'.npy'),mmap_mode='r') for f in ('u','v','p')]
  for lo in range(0,len(visible),127):
   z=np.stack([a[visible[lo:lo+127]][:,mask] for a in arrays],-1).reshape(-1,3).astype(np.float64)
   n=len(z);bm=z.mean(0);bm2=((z-bm)**2).sum(0);delta=bm-mean;total=count+n
   mean+=delta*n/total;m2+=bm2+delta**2*count*n/total;count=total
  print('ROUND2_STATS',sid,flush=True)
 scale=np.sqrt(m2/count);norm=m['normalization']
 assert count==norm['point_count']==775192000
 assert np.allclose(mean,norm['mean'],rtol=1e-8,atol=1e-10)
 assert np.allclose(scale,norm['scale'],rtol=1e-8,atol=1e-10)
 assert json.loads((BASE/'normalization.json').read_text())==norm
 # Window-level permissions matter now that all IDs are shared across roles.
 for sid in records:
  tw=next(w for w in reader.roles['test'] if w.trajectory==sid)
  for fn,role in [(reader.visible,'test'),(reader.target,'test'),(reader.visible,'train_fit')]:
   try:fn(tw,role)
   except ValueError:pass
   else:raise AssertionError('Test/role barrier failed')
  w=next(w for w in reader.roles['train_fit'] if w.trajectory==sid)
  obs,future,mask=reader.visible(w,'train_fit');assert obs['p'].shape==(20,62,126)
  assert obs['t'][-1]<future[0]
 reader.close();assert not any(a['role']=='test' for a in reader.access)
 baseline=m['baseline_protocol'];assert baseline['training_trajectory_count']==92
 assert sum(len(m['roles'][r]) for r in baseline['training_roles'])==5520
 assert cfg['readiness']['three_field_generator_available'] is False
 protected_check()
 result={'status':'PASS','round':2,'independent_interval_audit':True,'normalization_recomputed_from_new_fit_visible_only':True,
  'normalization':{'mean':mean.tolist(),'scale':scale.tolist(),'point_count':count},'test_and_role_barriers_verified_on_all92':True,
  'baseline_training_trajectories':92,'baseline_training_windows':5520,'eqgpt_and_baseline_unchanged':True,'training_started':False}
 write('check-round2.json',result);return result
if __name__=='__main__':
 print(json.dumps(first()),flush=True);print(json.dumps(second()),flush=True);print('TWO_SEEN_CHECKS_PASS',flush=True)
