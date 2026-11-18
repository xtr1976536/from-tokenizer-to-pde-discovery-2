"""Audit released 40-frame windows; deterministic Re-stratified trajectory split."""
import hashlib,json
from pathlib import Path
import numpy as np
ROLES=('train_fit','reward_holdout','validation_select','validation_stop','test')

def released_audit(folder,frames=3990):
 indices={s:json.loads((Path(folder)/f'{s}_index_numerical.json').read_text()) for s in ('train','val','test')}
 report={'splits':{},'cross_split_shared_frames':{},'source_hashes':{}}
 coverage={}
 for split,rows in indices.items():
  pairs=[(str(w['sim_id']),int(w['time_id'])) for w in rows]
  coverage[split]={(sid,start+i) for sid,start in pairs for i in range(40)}
  report['source_hashes'][split]=hashlib.sha256((Path(folder)/f'{split}_index_numerical.json').read_bytes()).hexdigest()
  report['splits'][split]={'windows':len(rows),'trajectories':len({p[0] for p in pairs}),
   'duplicate_windows':len(pairs)-len(set(pairs)),
   'incomplete_windows':sum(start<0 or start+40>frames for sid,start in pairs)}
 for a,b in [('train','val'),('train','test'),('val','test')]:
  report['cross_split_shared_frames'][a+'__'+b]=len(coverage[a]&coverage[b])
 report['leakage_detected']=any(report['cross_split_shared_frames'].values())
 return report,sorted({str(w['sim_id']) for rows in indices.values() for w in rows},key=lambda s:float(s[:-3]))

POLICY='seen_temporal_blocks250_guard20_each_side_stride40_train75_val12p5_test12p5_v2'
QUOTAS={'train_fit':11,'reward_holdout':1,'validation_select':1,'validation_stop':1,'test':2}

def seen_windows(lengths,seed=525):
 """Per-trajectory random time blocks, preserving seen conditions in every role.
 Official Cylinder block length250 is retained; training-pool/validation/test
 quotas are75/12.5/12.5 with strict full-window guards.
 """
 roles={r:[] for r in ROLES};blocks={}
 for sid in sorted(lengths,key=lambda s:float(s[:-3])):
  n=int(lengths[sid]);count=(n+249)//250
  if count!=16 or n!=3990:raise ValueError('This frozen seen protocol expects3990frames/16blocks')
  rng=np.random.default_rng(np.random.SeedSequence([seed,int(sid[:-3])]))
  order=rng.permutation(count).tolist();assigned={};offset=0
  for role,q in QUOTAS.items():
   for block in order[offset:offset+q]:assigned[block]=role
   offset+=q
  records=[]
  for b in range(count):
   lo=b*250;hi=min((b+1)*250,n);role=assigned[b];start=lo+20;stop=hi-20
   records.append({'block':b,'frame_start':lo,'frame_stop':hi,'usable_start':start,'usable_stop':stop,'role':role})
   for i in range(start,stop-39,40):roles[role].append({'trajectory':sid,'start':i,'block':b})
  blocks[sid]=records
 return roles,blocks

if __name__=='__main__':
 root=Path('/data1/users/liugang/src/eq-bpe/project');audit=root/'maintenance/stage2-seen75-20261115';audit.mkdir(parents=True,exist_ok=True)
 report,ids=released_audit(root/'data/realpdebench/cylinder/hf_dataset')
 roles,blocks=seen_windows({sid:3990 for sid in ids})
 (audit/'proposed-seen-blocks.json').write_text(json.dumps({'policy':POLICY,'seed':525,'blocks':blocks},indent=2))
 print({r:len(v) for r,v in roles.items()})
