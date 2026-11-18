"""Read-only candidate diagnostics: fixed validation windows, no model updates."""
import os,json,time,sys
from pathlib import Path
import numpy as np
from stage2_main_v1.data import SimulationData
from stage2_main_v1.safe_backend import SafeBackend
from stage2_main_v1.contracts import InvalidCandidate
root=Path('/data1/users/liugang/src/eq-bpe/project/runs/stage2_main_full_v2_safe_20261116')
out=Path('/data1/users/liugang/src/eq-bpe/project/runs/stage2_independent_rollout_20261117');out.mkdir(exist_ok=False)
def write(name,d):(out/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
cfg=json.loads((root/'configs/811-v320-seed525.json').read_text());models=json.loads((root/'matrix.json').read_text())['jobs'];chosen=[]
for job in models:
 folder=root/job/'output/batches'
 if not folder.exists():continue
 files=sorted(folder.glob('*.json'));allrows=[]
 for path in files:
  for rank,r in enumerate(json.loads(path.read_text())['top10'],1):allrows.append(dict(job=job,batch=path.name,rank=rank,**r))
 if not allrows:continue
 best=max(allrows,key=lambda r:r['reward']);best['selection_reason']='highest saved training reward within model';chosen.append(best)
 latest=json.loads(files[-1].read_text())['top10'];balanced=max(latest,key=lambda r:min(r['r2_per_equation']))
 if balanced['structure_key']!=best['structure_key'] and len(chosen)<6:
  chosen.append(dict(job=job,batch=files[-1].name,selection_reason='latest batch most balanced three-equation R2',**balanced))
# Limit to six, giving every running model its highest reward before extras.
primary=[r for r in chosen if r['selection_reason'].startswith('highest')];extra=[r for r in chosen if not r['selection_reason'].startswith('highest')];chosen=(primary+extra)[:6]
write('candidates.json',chosen)
data=SimulationData(models and json.loads((root/'matrix.json').read_text())['manifest'],cfg)
by={}
for w in data.roles['validation_select']:by.setdefault(w.trajectory,w)
names=sorted(by);windows=[by[names[i]] for i in np.linspace(0,len(names)-1,3,dtype=int)]
write('scope.json',dict(candidates=len(chosen),windows=[w.__dict__ for w in windows],role='validation_select',input_frames=20,output_frames=20,selection_uses_future=False,test_read=False,training_modified=False,cpu_only=True))
scale=data.training_scale();backend=SafeBackend(**cfg['numerics'],**cfg['resource_limits']);records=[]
for ci,row in enumerate(chosen):
 try:system=backend.parse(row['text'])
 except InvalidCandidate as error:
  records.append(dict(candidate=ci,status='COMPILE_REJECTED',error=str(error)));write('progress.json',records);continue
 for wi,w in enumerate(windows):
  start=time.monotonic();rec=dict(candidate=ci,window=wi,trajectory=w.trajectory,start=w.start)
  visible,times,mask=data.visible(w,'validation_select')
  # Baseline uses no future information. Targets are read after forecast attempt.
  persistence=np.broadcast_to(np.stack([visible[f][-1] for f in ['u','v','p']],-1),(20,*mask.shape,3)).copy()
  pred=None
  try:
   coef,r2=backend.fit(system,visible,mask);rec['visible_fit_r2']=list(r2)
   pred=backend.forecast(system,coef,visible,times,mask);rec.update(status='PASS',diagnostics=backend.last_diagnostics)
  except InvalidCandidate as error:rec.update(status='REJECTED',error=str(error))
  target,tm=data.target(w,'validation_select');assert np.array_equal(mask,tm)
  def metrics(p):
   mse=np.mean(((p-target)[:,mask,:]/scale)**2,axis=(0,1));return dict(nrmse_channels=np.sqrt(mse).tolist(),joint_nrmse=float(np.sqrt(mse.mean())))
  rec['persistence']=metrics(persistence)
  arrays=dict(truth=target,persistence=persistence,mask=mask,scale=scale,times=times,x=visible['x'],y=visible['y'],last_visible=np.stack([visible[f][-1] for f in ['u','v','p']],-1))
  if pred is not None:
   rec['prediction']=metrics(pred);rec['skill_vs_persistence']=1-(rec['prediction']['joint_nrmse']/rec['persistence']['joint_nrmse'])**2
   arrays['prediction']=pred
  np.savez_compressed(out/f'candidate{ci}_window{wi}.npz',**arrays)
  rec['seconds']=time.monotonic()-start;records.append(rec);write('progress.json',records)
  print(ci,wi,rec['status'],round(rec['seconds'],2),flush=True)
backend.close();data.close();write('result.json',dict(records=records,test_read=False,training_modified=False,access=data.access));print('COMPLETE',flush=True)
