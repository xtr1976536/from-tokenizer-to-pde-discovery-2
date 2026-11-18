"""Real Cylinder visible-only probe; failures remain explicit, no target templates."""
import argparse,json,time,signal

def deadline(*_):raise InvalidCandidate("Candidate hard time budget exceeded (30s)")
from pathlib import Path
import numpy as np
from .acceptance import write
from .data import SimulationData
from .implicit_backend import ImplicitBackend
from .contracts import InvalidCandidate

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--split',choices=['811','622'],required=True);ap.add_argument('--vocab',type=int,required=True);a=ap.parse_args()
 config=json.loads(Path(__file__).with_name('config.json').read_text());data=SimulationData(a.manifest,config)
 selected={r:data.roles[r][:1] for r in ['train_fit','reward_holdout','validation_select','validation_stop']}
 backend=ImplicitBackend(max_seconds=15,max_calls=5000,max_nfev=20);fitw=selected['train_fit'][0]
 visible,times,mask=data.visible(fitw,'train_fit');records=[]
 progress=a.output/f'probe-{a.split}-{a.vocab}-progress.json'
 if progress.exists():records=json.loads(progress.read_text())
 completed={(r['split'],r['vocab'],r['index']) for r in records}
 for split in [a.split]:
  for vocab in [a.vocab]:
   path=a.output/'serialization-fix-v2-diagnosis'/f'{split}-{vocab}-mix0.0.json'
   if not path.exists():raise RuntimeError('Wait for all generation batches')
   d=json.loads(path.read_text())
   for i,r in enumerate(d['records']):
    if not r.get('numeric_parse') or (split,vocab,i) in completed:continue
    start=time.monotonic();rec=dict(split=split,vocab=vocab,index=i,text=r['text'],status='ATTEMPT')
    try:
     signal.signal(signal.SIGALRM,deadline);signal.alarm(30)
     system=backend.parse(r['text']);coef,r2=backend.fit(system,visible,mask);rec.update(fit_pass=True,r2=list(r2),coefficients=coef)
     rw=selected['reward_holdout'][0];rv,rt,rm=data.visible(rw,'reward_holdout');rc,_=backend.fit(system,rv,rm)
     prediction=backend.forecast(system,rc,rv,rt,rm)
     target,tm=data.target(rw,'reward_holdout');sse=float(np.sum((prediction[:,tm]-target[:,tm])**2));energy=float(np.sum(target[:,tm]**2))
     rec.update(status='PASS',prediction_score=1/(1+sse/energy),diagnostics=backend.last_diagnostics)
    except InvalidCandidate as error:rec.update(status='REJECTED',error=str(error))
    finally:signal.alarm(0)
    rec['seconds']=time.monotonic()-start;records.append(rec);write(progress,records)
 write(a.output/f'probe-{a.split}-{a.vocab}.json',dict(grid=list(mask.shape),valid_points=int(mask.sum()),generated_candidates=len(records),fit_pass=sum(r.get('fit_pass',False) for r in records),forecast_pass=sum(r['status']=='PASS' for r in records),records=records,access=data.access,test_fields_read=False,formal_search_started=False))
 data.close()
if __name__=='__main__':main()
