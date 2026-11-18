"""Reduced-budget real-data chain using previously generated, immutable candidates.

This is replay acceptance, not a successful fresh400-candidate search claim.
"""
import argparse,json,time,copy,hashlib
from pathlib import Path
import torch,numpy as np
from .acceptance import write,sha
from .generator import ASTBPEGenerator
from .data import SimulationData
from .implicit_backend import ImplicitBackend
from .contracts import InvalidCandidate
from .scoring import reward,prediction_score,penalty

def weights(g):
 h=hashlib.sha256()
 for k,v in g.model.state_dict().items():h.update(k.encode());h.update(v.detach().cpu().numpy().tobytes())
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);a=ap.parse_args();out=a.root/'real-chain-smoke';out.mkdir(exist_ok=False)
 cfg=json.loads(Path(__file__).with_name('config.json').read_text());data=SimulationData(a.manifest,cfg)
 data.roles={r:values[:1] for r,values in data.roles.items()} # membership barriers remain from full manifest
 frozen=json.loads((a.root/'frozen.json').read_text());e=next(x for x in frozen['models'] if x['split']=='811' and x['vocab']==128);folder=Path(e['folder'])
 torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.18)
 g=ASTBPEGenerator(folder/'ast-bpe-128.json',device='cuda',random_fraction=0.);g.load(folder/'best.pt');g.optimizer=None
 backend=ImplicitBackend(max_seconds=15,max_calls=5000,max_nfev=20);scale=data.training_scale();rows=[]
 for path in sorted(a.root.glob('probe-*-*.json')):
  if 'progress' in path.name:continue
  for rec in json.loads(path.read_text())['records']:
   if rec['status']=='PASS':rows.append(rec)
 write(out/'scope.json',dict(kind='one batch / one epoch reduced candidate replay',source_candidates=len(rows),roles={r:[w.__dict__ for w in values] for r,values in data.roles.items()},future_test_read=False,formal_400_budget=False))
 scores=[]
 for r in rows:
  try:scores.append(dict(text=r['text'],**reward(backend.parse(r['text']),backend,data,data.roles['train_fit'],scale,.5,.2)))
  except InvalidCandidate as error:write(out/f'reject-{len(scores)}.json',dict(error=str(error)))
 if not scores:write(out/'result.json',dict(status='FAILED_REWARD',access=data.access));return
 top=sorted(scores,key=lambda r:r['reward'],reverse=True)[:10];before=weights(g)
 sft=g.sft([r['text'] for r in top],cfg['sft']);after=weights(g);assert before!=after
 g.save(out/'post-sft.pt');g.load(out/'post-sft.pt');assert weights(g)==after and g.random_fraction==0.
 write(out/'sft.json',dict(source_scores=scores,selected=top,sft=sft,before=before,after=after,restore_equal=True,frozen_checkpoint_unchanged=sha(folder/'best.pt')==e['checkpoint_sha256']))
 selected=[]
 for r in top:
  try:
   system=backend.parse(r['text']);m=prediction_score(system,backend,data,'validation_select',scale);selected.append(dict(text=r['text'],score=penalty(backend.term_counts(system),.2)*m['prediction_score'],metrics=m))
  except InvalidCandidate as err:continue
 if not selected:write(out/'result.json',dict(status='FAILED_VALIDATION_SELECTION',sft_passed=True,access=data.access));return
 best=max(selected,key=lambda r:r['score'])
 try:
  stop=prediction_score(backend.parse(best['text']),backend,data,'validation_stop',scale)
  write(out/'selected.json',dict(selection=best,stop=stop,test_read=False))
  write(out/'result.json',dict(status='PASS_REDUCED_REPLAY_CHAIN',candidates=len(rows),reward_pass=len(scores),sft_epochs=sft['epochs'],restore_equal=True,validation_selection=True,independent_stop_evaluation=True,test_read=False,access=data.access,limitations='Replay of generated structures on one window per role; no400 candidate search, no repeated epoch early-stop validation, no fresh postSFT generation'))
 except InvalidCandidate as err:write(out/'result.json',dict(status='FAILED_STOP_EVALUATION',error=str(err),access=data.access))
 data.close()
if __name__=='__main__':main()
