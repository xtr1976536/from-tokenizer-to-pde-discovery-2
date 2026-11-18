"""Read-only score audit on fixed real-data candidates; no changes to policy."""
import argparse,json,time
from pathlib import Path
import numpy as np
from .implicit_backend import ImplicitBackend
from .data import SimulationData
from .contracts import InvalidCandidate
from .acceptance import write

class Capture(ImplicitBackend):
 def fit(self,*args):
  self.columns=[];return super().fit(*args)
 def _evaluate(self,term,provider,shape,validity=None):
  value=super()._evaluate(term,provider,shape,validity)
  if len(shape)==3:
   indices=np.flatnonzero(validity);indices=indices[::max(1,int(np.ceil(len(indices)/self.max_fit_points)))];self.columns.append(value.ravel()[indices].copy())
  return value

def metrics(pred,target,mask,scale,previous):
 err=(pred[:,mask]-target[:,mask]).astype(float);y=target[:,mask].astype(float);persist=(previous[:,mask]-target[:,mask]).astype(float)
 sse=(err**2).sum(axis=(0,1));energy=(y*y).sum(axis=(0,1));center=((y-y.mean(axis=(0,1),keepdims=True))**2).sum(axis=(0,1));psse=(persist**2).sum(axis=(0,1))
 n=y.shape[0]*y.shape[1]
 return dict(sse=sse.tolist(),energy=energy.tolist(),energy_fractions=(energy/energy.sum()).tolist(),centered_energy=center.tolist(),raw_prediction_score=1/(1+sse.sum()/energy.sum()),normalized_joint_rmse=float(np.sqrt(np.mean(sse/n/scale**2))),per_channel_rmse=np.sqrt(sse/n).tolist(),persistence_relative_skill=float(1-sse.sum()/psse.sum()),channel_persistence_skill=(1-sse/psse).tolist(),centered_prediction_score=float(1/(1+sse.sum()/center.sum())),scale_balanced_prediction_score=float(1/(1+np.mean(sse/n/scale**2))))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);a=ap.parse_args();out=a.root/'reward-audit';out.mkdir(exist_ok=False)
 cfg=json.loads(Path(__file__).with_name('config.json').read_text());data=SimulationData(a.manifest,cfg);fw=data.roles['train_fit'][0];rw=data.roles['reward_holdout'][0];visible,_,mask=data.visible(fw,'train_fit');rv,rt,rm=data.visible(rw,'reward_holdout');scale=data.training_scale()
 sources=[]
 for p in sorted(a.root.glob('probe-*-*.json')):
  if 'progress' in p.name:continue
  sources.extend(r for r in json.loads(p.read_text())['records'] if r['status']=='PASS')
 records=[];backend=Capture(max_seconds=15,max_calls=5000,max_nfev=20)
 for i,r in enumerate(sources):
  system=backend.parse(r['text']);coeff,r2=backend.fit(system,visible,mask);cols=list(backend.columns);offset=0;eq=[]
  for row,coef,score in zip(system.rows,coeff['rows'],r2):
   A=np.column_stack(cols[offset:offset+len(row)]);offset+=len(row);rms=np.sqrt(np.mean(A*A,axis=0));B=A/rms;anchors=[]
   for j in range(A.shape[1]):
    if np.var(A[:,j])<1e-20:continue
    others=[k for k in range(A.shape[1]) if k!=j]
    beta=np.linalg.lstsq(B[:,others],-B[:,j],rcond=1e-10)[0];res=B[:,j]+B[:,others]@beta
    anchors.append(dict(index=j,r2=float(1-np.sum(res**2)/np.sum((B[:,j]-B[:,j].mean())**2))))
   # SVD on column-scaled residual basis is a diagnostic, not replacement scoring.
   singular=np.linalg.svd(B,compute_uv=False)
   current=np.sum(A*np.asarray(coef),axis=1);j=coeff['anchor_indices'][len(eq)];reproduced=1-np.sum(current**2)/np.sum((A[:,j]-A[:,j].mean())**2)
   assert np.isclose(reproduced,score)
   eq.append(dict(terms=len(row),anchor_index=j,reported_r2=score,reproduced_r2=float(reproduced),all_nonconstant_anchor_r2=anchors,minimum_to_maximum_singular_ratio=float(singular[-1]/singular[0]),rms_condition_span=float(rms.max()/rms.min()),anchor_mean_to_sd=float(abs(A[:,j].mean())/max(A[:,j].std(),1e-20))))
  rec=dict(split=r['split'],vocab=r['vocab'],index=r['index'],text=r['text'],fit_score=float(np.mean(r2)),equations=eq)
  try:
   rc,_=backend.fit(system,rv,rm);pred=backend.forecast(system,rc,rv,rt,rm)
   y,tm=data.target(rw,'reward_holdout');previous=np.broadcast_to(np.stack([rv[f][-1] for f in ['u','v','p']],-1),y.shape)
   rec['prediction']=metrics(pred,y,tm,scale,previous);rec['persistence']=metrics(previous,y,tm,scale,previous)
   rec['reward_by_lambda']={str(w):(1-.2*np.log10(sum(system.term_counts)))*(w*rec['fit_score']+(1-w)*rec['prediction']['raw_prediction_score']) for w in [.5,.2,0.]}
  except InvalidCandidate as error:rec['repeat_error']=str(error)
  records.append(rec);write(out/'progress.json',records)
 write(out/'result.json',dict(status='AUDIT_COMPLETE',records=records,access=data.access,test_read=False,policy_changed=False,alternative_metrics_diagnostic_only=True))
 data.close()
if __name__=='__main__':main()
