"""Run one paired search case from a retained stage-one epoch checkpoint."""
import argparse,gc,gzip,hashlib,json,os,sys,time,importlib.util
from pathlib import Path
import torch
from math_tokenizer.corpus import ROOT
from math_tokenizer.eqgpt.models import build_models
from compact_ast_bpe import CompactAlphabet
from math_tokenizer.eqgpt.latex_tokenizers import LatexAdapter
from math_tokenizer.eqgpt.tokenizer_adapters import Adapter
from math_tokenizer.eqgpt.existing_surrogate import load_existing
from math_tokenizer.eqgpt.shared8_config import SHARED8_CASES
from math_tokenizer.eqgpt.author import tensor_hash
from math_tokenizer.eqgpt.expanded_corpus import sha
from math_tokenizer.eqgpt.paired_pipeline import fingerprint

GPU_IDS={'GPU-e857f4d0-daa6-f33d-3dc8-927f15ab7d59':1,'GPU-ba72db90-47e9-38fd-0e9e-905c3b1798b5':3}
SETTINGS=dict(seed=525,layers=6,batch_size=128,positions=72,search_limit=70,
 learning_rate=1e-4,cycles=5,attempts=400,attempt_cap=5000,continuation_epochs=5,continuation_lr=1e-5,continuation_min_lr=1e-7,epi=.2)

def dump(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(d,indent=2));q.replace(p)

def run(a):
 gpu_uuid=os.environ.get('CUDA_VISIBLE_DEVICES')
 assert gpu_uuid in GPU_IDS and torch.cuda.device_count()==1
 torch.cuda.set_per_process_memory_fraction((6 if a.smoke else float(os.environ.get('STAGE1_SEARCH_CAP_GIB','14')))*1024**3/torch.cuda.get_device_properties(0).total_memory)
 assert a.case in SHARED8_CASES
 torch.set_num_threads(8)
 sampler_path=ROOT/'sampler.py'
 spec=importlib.util.spec_from_file_location('stage1_sampler',sampler_path);sampler=importlib.util.module_from_spec(spec);spec.loader.exec_module(sampler)
 from math_tokenizer.eqgpt import stage1_search_20261113 as study3_search
 def sample_and_evaluate(*args,**kwargs):
  kwargs['random_fraction']=.2 if a.arm=='eqgpt_reference' else a.random_fraction
  kwargs['max_attempts']=15000
  return sampler.sample_and_evaluate(*args,**kwargs)
 study3_search.sample_and_evaluate=sample_and_evaluate
 pre=ROOT/'upstream'/str(a.scale)/a.split
 key=f'{a.scale}-{a.split}-{a.arm}-seed{a.seed}'
 checkpoint_folder=ROOT/'pretrained'/key
 assert (checkpoint_folder/'COMPLETE.json').exists(), 'Pretraining must finish before search'
 selected=checkpoint_folder/'best.pt'
 training=json.loads((checkpoint_folder/'training.json').read_text());a.epoch=training['best_epoch']
 tokenizer_path=None if a.arm=='eqgpt_reference' else pre/f'ast-bpe-{a.arm.rsplit("_",1)[1]}.json'
 assert selected.is_file() and (tokenizer_path is None or tokenizer_path.is_file())
 if tokenizer_path is not None:
  tokenizer_hashes={tokenizer_path.name:sha(tokenizer_path),f'{tokenizer_path.stem}.backend.json':sha(tokenizer_path.with_name(f'{tokenizer_path.stem}.backend.json'))}
  adapter=LatexAdapter('ast_bpe',CompactAlphabet.load(tokenizer_path))
 else:
  tokenizer_hashes={};adapter=Adapter('eqgpt')
 positions=training['settings']['positions']
 model=build_models({a.arm:adapter},positions,a.seed,'cuda',n_layers=6)[0][a.arm]
 model.load_state_dict(torch.load(selected,map_location='cpu',weights_only=True))
 before=tensor_hash(model.state_dict());settings=dict(SETTINGS,epochs=a.epoch,seed=a.seed,positions=positions)
 if a.smoke:settings.update(cycles=1,attempts=4,continuation_epochs=5)
 mode='legacy' if a.arm=='eqgpt_reference' else ('model' if a.random_fraction==0 else 'mix20')
 destination=ROOT/'search'/('smoke' if a.smoke else 'results')/str(a.scale)/a.split/a.arm/mode/str(a.seed)/a.case
 if (destination/'complete.json').exists():
  for name,digest in json.loads((destination/'complete.json').read_text())['files'].items():assert sha(destination/name)==digest
  return
 assert not destination.exists(),'Unexpected incomplete final directory'
 work=destination.with_name(destination.name+f'.partial_{os.getpid()}');work.mkdir(parents=True)
 cache=ROOT/'data/mlp_cache'/a.case/'surrogate_cache.pt';cache_hash=sha(cache)
 identity=dict(scale=a.scale,arm=a.arm,epoch=a.epoch,seed=a.seed,case=a.case,settings=settings,pretrained_sha256=sha(selected),pretrained_tensor_sha256=before,
  gpu_uuid=gpu_uuid,tokenizer_sha256=tokenizer_hashes,split_sha256=sha(pre/'split.json'),split=a.split,surrogate_sha256=cache_hash,code=fingerprint(),runner_sha256=sha(Path(__file__)),sampling_sha256=sha(sampler_path),search_sha256=sha(ROOT/'src/math_tokenizer/eqgpt/stage1_search_20261113.py'),random_fraction=.2 if a.arm=='eqgpt_reference' else a.random_fraction,sft_schedule='cosine_per_cycle_1e-5_to_1e-7_5epochs')
 dump(work/'RUN.json',identity)
 cache_seed=int(json.loads((cache.parent/'shared_manifest.json').read_text())['seed'])
 identity['surrogate_seed']=cache_seed;identity['search_seed']=a.seed;dump(work/'RUN.json',identity)
 _,net,db,_,_=load_existing(cache.parent,a.case,'cuda',cache_seed,10000)
 report=study3_search.search(model if a.arm=='eqgpt_reference' else model.core,adapter,net,db,a.case,work,'cuda',reference=a.arm=='eqgpt_reference',pretrained_path=selected,settings=settings)
 for cycle in range(1,settings['cycles']+1):
  rows=[r for r in report['attempts'] if r['cycle']==cycle];n=sum(r['status']=='evaluated' for r in rows)
  assert 1<=n<=settings['attempts']
 assert sha(selected)==identity['pretrained_sha256'] and sha(cache)==cache_hash
 assert all(h['before_sha256']!=h['after_sha256'] for h in report['history'] if h['continuation_sequences'])
 with gzip.open(work/'candidates.jsonl.gz','wt') as f:
  for row in report['attempts']:f.write(json.dumps(row)+'\n')
 dump(work/'history.json',dict(history=report['history'],search_seconds=report['search_seconds']))
 dump(work/'mechanism.json',study3_search.mechanism_summary(report,a.case))
 # Remove only this case's temporary search weights; keep source best.pt immutable.
 result=json.loads((work/'result.json').read_text())
 dump(work/'result.json',dict(scale=a.scale,split=a.split,arm=a.arm,epoch=a.epoch,seed=a.seed,case=a.case,
  top1=result['top1'],top10=result['top10']))
 for p in list(work.iterdir()):
  if p.is_file() and p.name not in {'RUN.json','result.json','complete.json','candidates.jsonl.gz','history.json','mechanism.json'}:p.unlink()
 dump(work/'complete.json',dict(status='PASS',files={p.name:sha(p) for p in work.iterdir() if p.is_file() and p.name!='complete.json'}))
 work.rename(destination)
 print('CASE_COMPLETE',a.scale,a.arm,a.epoch,a.seed,a.case,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--split',choices=['811','622'],required=True);p.add_argument('--scale',type=int,choices=[212,318,424,530,636],required=True);p.add_argument('--arm',choices=['eqgpt_reference','ast_bpe_96','ast_bpe_128','ast_bpe_160'],required=True);p.add_argument('--seed',type=int,choices=[525,526,527],required=True);p.add_argument('--random-fraction',type=float,choices=[0.,.2],default=.2);p.add_argument('--case',required=True);p.add_argument('--smoke',action='store_true');run(p.parse_args())
