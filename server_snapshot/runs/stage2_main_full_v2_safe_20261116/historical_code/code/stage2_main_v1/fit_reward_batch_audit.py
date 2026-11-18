"""All78 fixed candidates x32 fixed seen-trajectory train-visible windows."""
import argparse,json,time,signal
from pathlib import Path
import numpy as np
from .acceptance import write,sha
from .data import SimulationData
from .implicit_backend import ImplicitBackend
from .contracts import InvalidCandidate
from .scoring import penalty

def expired(*_):raise InvalidCandidate('Audit operation time limit exceeded')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--split',required=True);ap.add_argument('--vocab',type=int,required=True);a=ap.parse_args()
 out=a.root/'fit-only-batch32';out.mkdir(exist_ok=True)
 cfg=json.loads(Path(__file__).with_name('config.json').read_text());data=SimulationData(a.manifest,cfg)
 groups={}
 for w in data.roles['train_fit']:groups.setdefault(w.trajectory,[]).append(w)
 ids=sorted(groups);indices=np.linspace(0,len(ids)-1,32,dtype=int)
 windows=[sorted(groups[ids[j]],key=lambda w:w.start)[(i*7)%len(groups[ids[j]])] for i,j in enumerate(indices)]
 assert len({w.trajectory for w in windows})==32
 plan=dict(windows=[w.__dict__ for w in windows],selection='32 evenly spaced sorted trajectory IDs; visible-window index=(7*i) mod count, independent of field values',manifest_sha256=sha(a.manifest),reward_version='stage1_fit_sparse_v1',candidate_source='serialization-fix-v2-diagnosis',test_read=False,future_target_read=False)
 # Each shard has its own identical manifest for concurrent writes.
 write(out/f'plan-{a.split}-{a.vocab}.json',plan)
 visible=[data.visible(w,'train_fit') for w in windows];backend=ImplicitBackend();signal.signal(signal.SIGALRM,expired)
 source=a.root/'serialization-fix-v2-diagnosis'/f'{a.split}-{a.vocab}-mix0.0.json';rows=json.loads(source.read_text())['records'];records=[]
 path=out/f'{a.split}-{a.vocab}.json';progress=out/f'{a.split}-{a.vocab}-progress.json'
 if path.exists():return
 if progress.exists():records=json.loads(progress.read_text())
 done={r['index'] for r in records}
 for index,r in enumerate(rows):
  if not r['text'] or index in done:continue
  start=time.monotonic();rec=dict(split=a.split,vocab=a.vocab,index=index,text=r['text'],windows=[],status='ATTEMPT')
  try:
   signal.alarm(5)
   try:system=backend.parse(r['text'])
   finally:signal.alarm(0)
   rec.update(structure_key=system.structure_key,term_counts=list(backend.term_counts(system)),penalty=penalty(backend.term_counts(system),.2))
   for w,(obs,_,mask) in zip(windows,visible):
    t=time.monotonic();result=dict(trajectory=w.trajectory,start=w.start)
    try:
     signal.alarm(15)
     try:coef,r2=backend.fit(system,obs,mask)
     finally:signal.alarm(0)
     if not np.isfinite(r2).all():raise InvalidCandidate('Nonfinite fitted R2')
     result.update(status='PASS',r2=list(r2),mean_r2=float(np.mean(r2)),anchor_indices=coef['anchor_indices'],fit_points=coef['fit_points'])
    except InvalidCandidate as err:result.update(status='REJECTED',reason=str(err))
    result['seconds']=time.monotonic()-t;rec['windows'].append(result)
   good=[w for w in rec['windows'] if w['status']=='PASS'];rec['successful_windows']=len(good)
   if len(good)==32:
    scores=np.array([w['r2'] for w in good]);rec.update(status='PASS',r_fit=float(scores.mean()),r2_per_equation=scores.mean(axis=0).tolist(),reward=float(scores.mean()*rec['penalty']),median_window_r2=float(np.median(scores.mean(axis=1))),window_r2_p10=float(np.percentile(scores.mean(axis=1),10)),window_r2_p90=float(np.percentile(scores.mean(axis=1),90)))
   else:rec.update(status='INCOMPLETE_WINDOWS',partial_mean_r2_diagnostic=float(np.mean([w['mean_r2'] for w in good])) if good else None)
  except InvalidCandidate as err:rec.update(status='COMPILE_REJECTED',reason=str(err),successful_windows=0)
  rec['seconds']=time.monotonic()-start;records.append(rec);write(progress,records);print(a.split,a.vocab,index,rec['status'],rec.get('reward'),flush=True)
 write(path,dict(status='COMPLETE',candidate_source_sha256=sha(source),plan=plan,records=records,access=data.access,production_reward_unchanged=True,training_started=False))
 data.close()
if __name__=='__main__':main()
