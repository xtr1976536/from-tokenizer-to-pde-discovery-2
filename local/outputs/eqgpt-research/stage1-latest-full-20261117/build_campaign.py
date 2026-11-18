from pathlib import Path
import json,shutil,hashlib
b=Path(__file__).resolve().parent;old=b.parent/'repository-update-20261115';shutil.copy2(b.parent/'stage1-v128-confirmation-20261117/pretrain_tune.py',b/'pretrain_tune.py');shutil.copy2(old/'restarts/stage01_20261113/stage1/search_code/sampler.py',b/'sampler.py')
s=(old/'scripts/search_stage1_20261113.py').read_text().replace('from math_tokenizer.eqgpt.compact_alphabet import CompactAlphabet','from compact_ast_bpe import CompactAlphabet')
s=s.replace("torch.set_num_threads(8)","torch.set_num_threads(8)")
s=s.replace("sampler_path=ROOT/'restarts/stage01_20261113/stage1/search_code/sampler.py'","sampler_path=ROOT/'sampler.py'")
start=s.index(" pre=ROOT/'restarts");end=s.index(' assert selected.is_file()',start)
s=s[:start]+''' pre=ROOT/'upstream'/str(a.scale)/a.split
 key=f'{a.scale}-{a.split}-{a.arm}-seed{a.seed}'
 checkpoint_folder=ROOT/'pretrained'/key
 assert (checkpoint_folder/'COMPLETE.json').exists(), 'Pretraining must finish before search'
 selected=checkpoint_folder/'best.pt'
 training=json.loads((checkpoint_folder/'training.json').read_text());a.epoch=training['best_epoch']
 tokenizer_path=None if a.arm=='eqgpt_reference' else pre/f'ast-bpe-{a.arm.rsplit("_",1)[1]}.json'
'''+s[end:]
s=s.replace("model=build_models({a.arm:adapter},72,a.seed", "positions=training['settings']['positions']\n model=build_models({a.arm:adapter},positions,a.seed")
s=s.replace('settings=dict(SETTINGS,epochs=a.epoch,seed=a.seed)','settings=dict(SETTINGS,epochs=a.epoch,seed=a.seed,positions=positions)')
s=s.replace("ROOT/'restarts/stage01_20261113/stage1/search'/('smoke_cosine' if a.smoke else 'results')/str(a.scale)/a.arm/mode/str(a.seed)/a.case", "ROOT/'search'/('smoke' if a.smoke else 'results')/str(a.scale)/a.split/a.arm/mode/str(a.seed)/a.case")
s=s.replace("split_sha256=sha(pre/'split.json')","split_sha256=sha(pre/'split.json'),split=a.split")
s=s.replace("dict(scale=a.scale,arm=a.arm,epoch=a.epoch,seed=a.seed,case=a.case,\n  top1", "dict(scale=a.scale,split=a.split,arm=a.arm,epoch=a.epoch,seed=a.seed,case=a.case,\n  top1")
s=s.replace("['eqgpt_reference','ast_bpe_200','ast_bpe_300','ast_bpe_450']","['eqgpt_reference','ast_bpe_96','ast_bpe_128','ast_bpe_160']")
s=s.replace("p.add_argument('--scale'", "p.add_argument('--split',choices=['811','622'],required=True);p.add_argument('--scale'")
(b/'search_case.py').write_text(s)
cases=['Wave_equation','Convection_diffusion_equation','KG_equation','Burgers_equation','Eq_6_2_12','PDE_divide','KdV_equation','Chaffee_Infante_equation']
pre=[];search=[]
for scale in [212,636]:
 for split in ['811','622']:
  for seed in [525,526,527]:
   pre.append(dict(job=f'{scale}-{split}-eqgpt_reference-seed{seed}',scale=scale,split=split,seed=seed,arm='eqgpt_reference',lr=1e-4 if scale==212 else 5e-5,l2=.001 if scale==212 else 0.,cosine=20,minimum_epochs=30,patience=15,min_delta=1e-4,maximum_epochs=80))
   for arm in ['ast_bpe_96','ast_bpe_128','ast_bpe_160','eqgpt_reference']:
    for fraction in ([.2] if arm=='eqgpt_reference' else [0.,.2]):
     for case in cases:search.append(dict(scale=scale,split=split,seed=seed,arm=arm,random_fraction=fraction,case=case))
(b/'pretrain_jobs.json').write_text(json.dumps(pre,indent=2));(b/'search_jobs.json').write_text(json.dumps(search,indent=2));assert len(search)==672
pinned=['src/math_tokenizer/eqgpt/stage1_search_20261113.py','src/math_tokenizer/eqgpt/latex_experiment.py','src/math_tokenizer/eqgpt/evaluation.py','src/math_tokenizer/eqgpt/paired_pipeline.py']
(b/'legacy_pins.json').write_text(json.dumps({p:hashlib.sha256((old/p).read_bytes()).hexdigest() for p in pinned},indent=2))
