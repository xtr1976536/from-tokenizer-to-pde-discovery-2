"""Fixed-budget inference comparison on immutable pretrained checkpoints."""
import json,time,argparse
from pathlib import Path
from collections import Counter
import torch
import signal

def parse_timeout(*_):raise InvalidCandidate("Numeric compile budget exceeded (5s)")

from .generator import ASTBPEGenerator
from .acceptance import sha,write
from .corpus_work.constrained_sampling import sample_batch
from .implicit_backend import ImplicitBackend
from .contracts import InvalidCandidate

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--frozen',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 freeze=json.loads(a.frozen.read_text());torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.18)
 for entry in freeze['models']:
  folder=Path(entry['folder']);v=entry['vocab'];split=entry['split'];g=ASTBPEGenerator(folder/f'ast-bpe-{v}.json',device='cuda');g.load(folder/'best.pt');g.optimizer=None
  assert sha(folder/'best.pt')==entry['checkpoint_sha256'];backend=ImplicitBackend()
  for mixture in [0.]:
   path=a.output/f'{split}-{v}-mix{mixture}.json'
   if path.exists():continue
   start=time.monotonic();rows=[]
   for b in range(4):
    recs=sample_batch(g.model,g.adapter,20261116+b,batch=8,max_tokens=256,random_fraction=mixture,return_records=True,residual_zero_rhs=True)
    for r in recs:
     r['numeric_parse']=False
     if r['text']:
      try:
       signal.signal(signal.SIGALRM,parse_timeout);signal.alarm(5)
       try:system=backend.parse(r['text'])
       finally:signal.alarm(0)
       r.update(numeric_parse=True,structure_key=system.structure_key)
      except InvalidCandidate as error:r['numeric_error']=str(error)
    rows.extend(recs)
   valid=[r for r in rows if r['text']];parsed=[r for r in rows if r['numeric_parse']]
   write(path,dict(split=split,vocab=v,mixture=mixture,attempts=32,task_valid=len(valid),numeric_parse=len(parsed),unique=len({r['structure_key'] for r in parsed}),reasons=dict(Counter(r['reason'] for r in rows)),seconds=time.monotonic()-start,records=rows,checkpoint_unchanged=sha(folder/'best.pt')==entry['checkpoint_sha256']))
   print(path.name,'valid',len(valid),'parsed',len(parsed),flush=True)
  del g;torch.cuda.empty_cache()
if __name__=='__main__':main()
