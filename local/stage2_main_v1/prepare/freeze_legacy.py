"""Freeze an unchanged, dependency-complete old EQGPT before retiring old runners."""
import ast,hashlib,json,shutil
from pathlib import Path
ROOT=Path('/data1/users/liugang/src/eq-bpe/project')
DEST=ROOT/'stage2_main_v1/legacy_eqgpt'
LAYOUT=DEST/'layout'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False))
def main():
 if (DEST/'REFERENCE.json').exists():raise RuntimeError('Reference already frozen; do not overwrite')
 dirs=['ast_bpe_multifield_v1','ast_bpe_multifield_v2','ast_bpe_multifield_v4']
 modules={p.stem:p for d in dirs for p in (ROOT/d).glob('*.py') if not p.name.startswith('._')}
 # Newest old two-equation search plus shared runtime required by preserved stage3.
 roots=['generator','generator_search_optimized','runtime','multitrajectory_data','single_reward_v2','model','pipeline','compact_tokenizer']
 selected=set();todo=[modules[n] for n in roots]
 while todo:
  p=todo.pop()
  if p in selected:continue
  selected.add(p)
  tree=ast.parse(p.read_text())
  for node in ast.walk(tree):
   names=([node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else [a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else [])
   todo.extend(modules[n] for n in names if n in modules and modules[n] not in selected)
 for p in selected:
  target=LAYOUT/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 # The exact count-only sampler used by generator_search_optimized.
 for name in ['two_equation_sampling.py']:
  p=ROOT/'ast_bpe_multifield_v4/seen_tasks'/name
  target=LAYOUT/'ast_bpe_multifield_v4'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 # Historical training code is reference only: it is not the new training protocol.
 target=DEST/'reference_training/pretrain_v5.py';target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/'experiments/corpus_retrain_20261110/train_compare.py',target)
 for folder in ['分词器-pde发现/src','分词器-pde发现/native','分词器-pde发现/eqgpt_original/code']:
  for p in (ROOT/folder).rglob('*'):
   if p.is_file() and p.suffix in {'.py','.c','.h'} and not p.name.startswith('._'):
    target=LAYOUT/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 # Preserve original 200-formula corpus for dependency compatibility.
 source=ROOT/'ast_bpe_multifield_v2/data/corpus/multifield200/coefficient_free'
 shutil.copytree(source,LAYOUT/source.relative_to(ROOT),ignore=shutil.ignore_patterns('._*','__pycache__'))
 # Most recent surviving mutually matched PDE corpus/tokenizer/checkpoint (v5).
 corpus=ROOT/'outputs/corpus-retrain-20261110/base200_v5/augmented_vocab'
 shutil.copytree(corpus,DEST/'training_corpus')
 for name in ['equations.jsonl','splits.json','revision.json','verification.json','equivalent_split_audit.json']:
  shutil.copy2(corpus.parent/name,DEST/'training_corpus'/name)
 checkpoint=ROOT/'runs/corpus_retrain_20261110/production_ab_v5/augmented_vocab'
 (DEST/'checkpoint').mkdir(parents=True)
 for name in ['model.pt','training.json']:shutil.copy2(checkpoint/name,DEST/'checkpoint'/name)
 meta=json.loads((DEST/'checkpoint/training.json').read_text())
 assert digest(DEST/'training_corpus/tokenizer300.json')==meta['tokenizer_sha256']
 assert digest(DEST/'training_corpus/encoded.jsonl')==meta['encoded_sha256']
 # Native extension cache is an environment dependency of the unmodified tokenizer.
 cache=LAYOUT/'分词器-pde发现/.native_cache';cache.mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'分词器-pde发现/.native_cache').glob('*.so'):shutil.copy2(p,cache/p.name)
 files={str(p.relative_to(DEST)):digest(p) for p in DEST.rglob('*') if p.is_file()}
 source_hashes={str(p.relative_to(ROOT)):digest(p) for p in selected}
 write(DEST/'REFERENCE.json',{'version':'old-two-field-eqgpt-frozen-20261115','fields':['u','v'],'equation_count':2,
  'selected_generator':'layout/ast_bpe_multifield_v4/generator_search_optimized.py',
  'selected_sampler':'layout/ast_bpe_multifield_v4/two_equation_sampling.py',
  'corpus_source':str(corpus.relative_to(ROOT)),'checkpoint_source':str(checkpoint.relative_to(ROOT)),
  'selection_reason':'latest surviving hash-matched spatial-PDE v5 augmented corpus/tokenizer/checkpoint; later base100 checkpoint is mixed ODE corpus, not this PDE pair',
  'unchanged_old_architecture':True,'new_uvp_eqgpt_started':False,
  'new_training_protocol_not_yet_implemented':True,'shared_runtime_source_hashes':source_hashes,'files_sha256':files})
 print('FROZEN',len(files),'files; shared library',len(selected),'modules')
if __name__=='__main__':main()
