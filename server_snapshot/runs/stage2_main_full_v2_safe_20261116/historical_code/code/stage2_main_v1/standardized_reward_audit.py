"""Fixed seven candidates, same windows, production z-score reward verification."""
import argparse,json
from pathlib import Path
import numpy as np
from .data import SimulationData
from .implicit_backend import ImplicitBackend
from .scoring import prediction_score,fit_score,penalty
from .acceptance import write
from .contracts import InvalidCandidate

class Persistence:
 def fit(self,*_):return None,None
 def forecast(self,system,coeff,visible,times,mask):
  return np.broadcast_to(np.stack([visible[f][-1] for f in ['u','v','p']],-1),(len(times),)+mask.shape+(3,)).copy()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);a=ap.parse_args()
 out=a.root/'standardized-reward';out.mkdir(exist_ok=False)
 cfg=json.loads(Path(__file__).with_name('config.json').read_text());data=SimulationData(a.manifest,cfg)
 data.roles={r:v[:1] for r,v in data.roles.items()};scale=data.training_scale()
 previous=json.loads((a.root/'reward-audit/result.json').read_text());backend=ImplicitBackend(max_seconds=15,max_calls=5000,max_nfev=20)
 base=prediction_score(None,Persistence(),data,'reward_holdout',scale);records=[]
 for row in previous['records']:
  rec={k:row[k] for k in ['split','vocab','index','text']}
  try:
   system=backend.parse(row['text']);fit=fit_score(system,backend,data,data.roles['train_fit']);pred=prediction_score(system,backend,data,'reward_holdout',scale)
   assert np.isclose(fit,row['fit_score']);sparsity=penalty(backend.term_counts(system),.2)
   rec.update(status='PASS',r_fit=fit,prediction=pred,penalty=sparsity,relative_to_persistence_sse_improvement=1-np.sum(pred['standardized_sse_by_channel'])/np.sum(base['standardized_sse_by_channel']),reward_by_lambda={str(w):sparsity*(w*fit+(1-w)*pred['prediction_score']) for w in [.5,.2,0.]})
  except InvalidCandidate as error:rec.update(status='REJECTED',error=str(error))
  records.append(rec);write(out/'progress.json',records)
 write(out/'result.json',dict(status='STANDARDIZED_REWARD_AUDITED',normalization_source='frozen92trajectory train_fit visible history only',mean=data.training_mean().tolist(),scale=scale.tolist(),persistence=base,records=records,access=data.access,test_read=False,training_started=False,policy='train_fit_zscore_energy_v2; Rfit, sparsity and lambdas unchanged'))
 data.close()
if __name__=='__main__':main()
