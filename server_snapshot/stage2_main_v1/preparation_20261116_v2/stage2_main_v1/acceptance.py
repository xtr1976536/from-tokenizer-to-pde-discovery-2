"""Frozen six-model evaluation; no test-driven model or parameter selection."""
import argparse,json,time,hashlib,shutil,os
from pathlib import Path
from collections import Counter
import torch
from .generator import ASTBPEGenerator
from .corpus_work.constrained_sampling import sample_batch
from .implicit_backend import ImplicitBackend
from .contracts import InvalidCandidate

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n');q.replace(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--models',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--phase',choices=['freeze','evaluate','generate'],required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];prep=root/'outputs/eqgpt-research/stage2-preparation-2026-11-16';out=a.output;out.mkdir(parents=True,exist_ok=True)
 if a.phase=='freeze':
  assert not (out/'frozen.json').exists(),'Freeze already exists'
  entries=[]
  for split in ['811','622']:
   for v in [128,192,320]:
    run=a.models/split/f'vocab_{v}';folder=out/'models'/split/str(v);folder.mkdir(parents=True)
    checkpoint=run/'best.pt';source=sha(checkpoint);shutil.copy2(checkpoint,folder/'best.pt');assert sha(folder/'best.pt')==source
    for path in [prep/split/f'upstream/ast-bpe-{v}.json',prep/split/f'upstream/ast-bpe-{v}.backend.json']:
     shutil.copy2(path,folder/path.name)
    train=json.loads((run/'training.json').read_text());complete=json.loads((run/'COMPLETE.json').read_text());assert complete['best_epoch']==train['best_epoch']
    payload=torch.load(folder/'best.pt',map_location='cpu',weights_only=True);assert payload['training_state']['best_epoch']==complete['best_epoch']
    assert payload['training_state']['best_loss']==complete['best_validation_loss'] if 'best_validation_loss' in complete else payload['training_state']['best_loss']==train['best_loss']
    write(folder/'selection.json',dict(best_epoch=complete['best_epoch'],settings=complete['settings'],source=str(checkpoint)))
    entries.append(dict(split=split,vocab=v,folder=str(folder),checkpoint_sha256=source,tokenizer_sha256=sha(folder/f'ast-bpe-{v}.json'),backend_sha256=sha(folder/f'ast-bpe-{v}.backend.json'),train_sha256=sha(prep/split/'frozen/train.jsonl'),validation_sha256=sha(prep/split/'frozen/validation.jsonl'),test_sha256=sha(prep/split/'frozen/test.jsonl'),split_sha256=sha(prep/split/'frozen/split-manifest.json'),best_epoch=complete['best_epoch']))
  write(out/'frozen.json',dict(status='FROZEN_BEFORE_TEST',models=entries,configuration_selection='128/192/320 for both splits; fixed before heldout evaluation',code_sha256={str(p.relative_to(root)):sha(p) for p in (root/'stage2_main_v1').glob('*.py')}));return
 frozen=json.loads((out/'frozen.json').read_text())
 torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.18)
 for e in frozen['models']:
  split=e['split'];v=e['vocab'];folder=Path(e['folder']);dest=out/'results'/split/str(v);dest.mkdir(parents=True,exist_ok=True)
  name='test.json' if a.phase=='evaluate' else 'generation.json'
  if (dest/name).exists():continue
  assert sha(folder/'best.pt')==e['checkpoint_sha256']
  g=ASTBPEGenerator(folder/f'ast-bpe-{v}.json',device='cuda',positions=2048);g.load(folder/'best.pt');g.optimizer=None
  if a.phase=='evaluate':
   assert sha(prep/split/'frozen/test.jsonl')==e['test_sha256']
   rows=[json.loads(l) for l in (prep/split/'frozen/test.jsonl').read_text().splitlines()];texts=[r['normalized']['text'] for r in rows]
   from .corpus_work.run_upstream import evaluate
   metrics=evaluate(g.adapter.tokenizer,rows);loss=g._epoch(texts,dict(batch_size=16,token_budget=4096,gradient_clip=1.),False,0)
   write(dest/name,dict(status='PASS',formulas=len(texts),loss=loss,tokenizer=metrics,checkpoint_unchanged=sha(folder/'best.pt')==e['checkpoint_sha256'],no_selection_after_test=True))
  else:
   attempts=32;records=[];backend=ImplicitBackend();start=time.monotonic()
   for batch in range(4):
    values=sample_batch(g.model,g.adapter,seed=20261116+batch,batch=8,max_tokens=256,random_fraction=.2)
    for text in values:
     rec=dict(text=text,task_valid=text is not None,numerics_parsed=False)
     if text:
      try:
       system=backend.parse(text);rec.update(numerics_parsed=True,structure_key=system.structure_key,term_counts=system.term_counts)
      except InvalidCandidate as err:rec['rejection']=str(err)
     records.append(rec)
    write(dest/'generation-progress.json',dict(attempts=len(records),records=records))
   valid=[r for r in records if r['task_valid']];parsed=[r for r in records if r['numerics_parsed']];unique={r['structure_key'] for r in parsed}
   write(dest/name,dict(attempts=attempts,task_valid=len(valid),numerics_parsed=len(parsed),unique_structures=len(unique),duplicate_fraction=1-len(unique)/len(parsed) if parsed else None,seconds=time.monotonic()-start,max_tokens=256,random_fraction=.2,records=records,sampling_scope='32 task-masked attempts; no hand-coded fallback, numeric admission distinct from solvability'))
  del g;torch.cuda.empty_cache();print(a.phase,split,v,'DONE',flush=True)
if __name__=='__main__':main()
