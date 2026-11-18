"""Explicit stage-2 cleanup: inventory -> inspect manifest -> two checks -> unlink.
Never recursively remove a directory, follow a symlink, or delete source code.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

SOURCE={'.py','.pyi','.sh','.bash','.zsh','.c','.h','.cpp','.hpp','.cu','.ipynb','.m','.pde','.so','.dylib','.yaml','.yml','.toml'}
RUN_NAMES='''backend_diagnosis_20261110_v1 baselines_clean baselines_seen_v1 experiments_v2_preparation formal_first_experiment_20261111 formal_nopinn_batch32_20261111 full_validation_baselines_20261110_v1 general_relation_audit_20261109 generation_quality_fixed_weights_20261110_v1 group_size_frozen84_20261111 handbuilt_velocity_pde_20261113 highdiff_joint_C_20261112 highdiff_structure_20261112 matrix26_batch1 mlp92_validation_20261110_v1 mlp_chain_repair_20261110_v1 nopinn_pair_acceptance_20261111 order2_acceptance_20261110_v1 order2_acceptance_20261110_v2 order2_final_audit_20261110_v1 order2_full_single_gpu2_20261110_second_v1 order2_full_single_gpu2_20261110_v1 order3_acceptance_20261110_v1 order3_acceptance_20261110_v2 order3_acceptance_20261110_v3 postfilter_reward_review_20261110_v1 predictor_pinn_upgrade_20261110_v1 realworld_full_gpu1_20261108 realworld_full_gpu1_20261108_v2 realworld_full_gpu1_20261108_v3 realworld_full_gpu1_20261108_v4 realworld_full_gpu1_20261108_v5 realworld_full_gpu1_20261108_v6 realworld_full_gpu1_20261108_v7 realworld_full_gpu1_20261108_v8 realworld_full_gpu1_preflight realworld_gpu_reward_one_cycle_20261108 realworld_gpu_reward_one_cycle_20261108_v2 reward_direction_audit_20261110_v1 reward_parallel_acceptance_20261109_v1 reward_parallel_acceptance_20261109_v2 reward_parallel_full_20261109_v1 reward_screening_full_gpu1_20261109 reward_screening_v1 reward_top1_validation_comparison_20261109_v1 reward_v3_forecast_20261110_v1 seen_acceptance_20261111 seen_server_task1_accept_v1 single_trajectory_gpu2_20261109_v1 strict_formula_one_cycle_20261108 strict_formula_one_cycle_20261108_v2 strict_formula_one_cycle_20261108_v3 strict_plus_one_cycle_20261108 test4_no_front_mlp_20261110_v1 two_window_baselines_20261110_v1 validation_fields_rank01_20261109 validation_only400_20261113 validation_reward_pair_20261112'''.split()
ARTIFACT_SUFFIX={'.pt','.pth','.npz','.npy','.h5','.hdf5','.arrow','.log','.json','.jsonl','.png','.jpg','.jpeg','.pdf','.csv','.tsv','.pkl','.pickle','.bin','.zip','.gz','.txt','.out','.err','.pyc'}
REPORTS={'audit_pass1.json','audit_pass2.json','comparison.json','completion_audit.json','improvement_validation.json','matched_validation_comparison.json','multitrajectory_completion_audit.json','reward_pool_comparison.json','equivalence_regression.json'}

def dump(path,obj):
 Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):
 s=p.lstat();return {'size':s.st_size,'mtime_ns':s.st_mtime_ns,'inode':s.st_ino}
def within(rel,root):return rel==root or rel.startswith(root+'/')
def source(p):
 return (p.suffix in SOURCE or p.suffix in {'.md','.rst'} or p.name in {'requirements.txt','LICENSE','NOTICE','Makefile'}
         or p.name in {'config.json','configuration.json'} or 'config' in p.name.lower()
         or p.name.startswith('requirements'))
def reason(rel):
 p=Path(rel)
 if source(p):return None
 # Shared equation corpora, Stage 0/1, Stage 3 and all baseline source/config remain protected.
 if rel.startswith(('stage3_','stage2_main_v1/','baseline_code/','baseline_configs/')):return None
 if within(rel,'data/realpdebench/cylinder/hf_dataset/real'):return 'old Cylinder real Arrow dataset'
 if rel.startswith('data/realpdebench/cylinder/') and (p.name.endswith('_real.json') or p.name=='mean_std.pt'):return 'old Cylinder real metadata/statistics'
 if rel.startswith('data/realpdebench/.cache/') and ('/real/' in rel or '_real.json' in rel):return 'old Cylinder real download cache'
 if within(rel,'ast_bpe_multifield_v2/data/cylinder'):return 'local old Cylinder real data and windows'
 if any(within(rel,f'ast_bpe_multifield_v{v}/data') for v in (3,4)):
  return 'old Cylinder window export/cache'
 if rel=='research/realpdebench/protocol_audit_20261108/10031_raw.h5':return 'old Cylinder raw trajectory sample'
 if any(within(rel,'data/'+n) for n in ('baselines_clean','baselines_seen_v1')):return 'old real Cylinder baseline data adapter'
 if within(rel,'baseline_logs'):return 'old baseline training logs/cache'
 for n in RUN_NAMES:
  if within(rel,'runs/'+n) or rel=='runs/'+n+'.log':return 'verified Stage 2 old run/baseline artifact'
 if rel.startswith('runs/') and p.name in {'full_nopinn_controller_20261111.log','full_nopinn_controller_exp1.log','full_nopinn_controller_exp2.log','full_nopinn_controller_grouped_20261111.log','group_size10_frozen84_controller.log','group_size2_frozen84_controller.log','group_size4_frozen84_controller.log','trajectory_preview.npz'}:return 'Stage 2 controller log/preview'
 if p.parent==Path('.') and p.suffix=='.log' and p.name.startswith(('cpu_reward_','gpu_reward_')):return 'Stage 2 reward benchmark log'
 for v in (1,2,3,4):
  prefix=f'ast_bpe_multifield_v{v}'
  if not within(rel,prefix):continue
  if '__pycache__' in p.parts or within(rel,prefix+'/runs') or within(rel,prefix+'/artifacts'):
   if p.suffix in ARTIFACT_SUFFIX or p.name.startswith('events.out.tfevents'):return 'old Stage 2 generated artifact/cache'
  if v==4:
   if any(within(rel,prefix+'/'+n) for n in ('clean_real_v1','strict40_indices','seen_tasks/prepared','seen_tasks/smoke_indices','seen_tasks/server_acceptance')) and p.suffix in ARTIFACT_SUFFIX:return 'old Cylinder real derived split/audit metadata'
   if p.parent==Path(prefix+'/seen_tasks') and p.name in {'frozen84_manifest.json','audit2_results.json'}:return 'old Cylinder real derived split/audit metadata'
   if p.suffix=='.log' or (p.parent==Path(prefix) and p.name in REPORTS):return 'old Stage 2 output/report'
   if within(rel,prefix+'/seen_tasks') and (p.suffix in {'.npz','.pt','.pth','.pyc'} or p.name.endswith('.provenance.json') or p.name.endswith('_results.json')):return 'old Cylinder exported trajectory/training cache'
   if any(within(rel,prefix+'/'+n) for n in ('full_data_preflight','experiment_audit_3rounds')) and p.suffix in ARTIFACT_SUFFIX:return 'old Stage 2 audit result'
   if any(within(rel,prefix+'/'+n) for n in ('experiments_v2','seen_tasks','reward_lab_20261109')) and p.suffix in {'.pt','.pth','.log','.npz','.npy'}:return 'old Stage 2 numerical/training cache'
 if any(within(rel,n) for n in ('outputs/stage2_monitor','outputs/validation_fields_rank01_20261109','outputs/current_model_report_20261110')):return 'old Stage 2 monitor/result export'
 return None

def walk(root):
 for base,dirs,files in os.walk(root,followlinks=False):
  for d in dirs:
   p=Path(base,d)
   if p.is_symlink() and str(p.relative_to(root)).startswith(('data/baselines_clean/','data/baselines_seen_v1/')):yield p
  dirs[:]=[d for d in dirs if d not in {'.git','.venv','.hf-download-venv','.deps','node_modules'} and not Path(base,d).is_symlink()]
  for f in files:
   p=Path(base,f)
   if not p.is_symlink():yield p
   elif str(p.relative_to(root)).startswith(('data/baselines_clean/','data/baselines_seen_v1/')):yield p

def inventory(root,manifest):
 targets=[];protected={};sizes={};symlinks=[]
 for p in walk(root):
  rel=p.relative_to(root).as_posix();st=info(p);why=reason(rel)
  top='/'.join(Path(rel).parts[:2]);sizes[top]=sizes.get(top,0)+st['size']
  if why:
   targets.append({'path':rel,'reason':why,'symlink':p.is_symlink(),'link_target':os.readlink(p) if p.is_symlink() else None,**st})
  elif source(p) or rel.startswith(('baseline_code/','baseline_configs/','data/formulas/','data/tokenizers/','data/realpdebench/cylinder/hf_dataset/numerical/')) or rel in {'data/realpdebench/version.json','data/realpdebench/cylinder/channels.json'} or (rel.startswith('data/realpdebench/cylinder/hf_dataset/') and p.name.endswith('_numerical.json')):
   protected[rel]={'sha256':digest(p),**st}
 result={'root':str(root),'targets':targets,'protected':protected,'sizes':sizes,
         'target_bytes':sum(r['size'] for r in targets),'target_files':len(targets),
         'policy':'explicit stage2 allowlist; preserve source/config/docs, Stage3 and shared formula data'}
 dump(manifest,result);print(json.dumps({'files':len(targets),'GiB':result['target_bytes']/2**30,'protected_files':len(protected)}))

def check(root,m):
 assert str(root)==m['root'],'Root mismatch'
 for row in m['targets']:
  p=root/row['path'];assert p.is_symlink()==row['symlink'] and p.parent.resolve().is_relative_to(root)
  if p.is_symlink():assert os.readlink(p)==row['link_target']
  assert reason(row['path'])==row['reason'],'Policy mismatch'
  assert info(p)=={k:row[k] for k in ('size','mtime_ns','inode')},f'Target changed: {p}'
 for rel,row in m['protected'].items():
  assert (root/rel).is_file() and digest(root/rel)==row['sha256'],f'Protected file changed: {rel}'

def delete(root,manifest,receipt):
 m=json.loads(Path(manifest).read_text());check(root,m);check(root,m)
 removed=[]
 for row in m['targets']:
  p=root/row['path'];assert p.is_symlink()==row['symlink'] and p.parent.resolve().is_relative_to(root)
  if p.is_symlink():assert os.readlink(p)==row['link_target']
  assert info(p)=={k:row[k] for k in ('size','mtime_ns','inode')}
  p.unlink();removed.append(row['path'])
 # Do not prune directories: some are importable packages or old source layouts.
 preserved=all((root/rel).is_file() and digest(root/rel)==row['sha256'] for rel,row in m['protected'].items())
 result={'deleted_files':len(removed),'deleted_logical_bytes':sum(r['size'] for r in m['targets']),
         'all_targets_absent':all(not os.path.lexists(root/r) for r in removed),
         'protected_source_and_baseline_unchanged':preserved,'two_predelete_checks':'PASS',
         'removed':removed}
 dump(receipt,result);print(json.dumps({k:v for k,v in result.items() if k!='removed'}));assert preserved

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['inventory','check','delete']);p.add_argument('--root',required=True);p.add_argument('--manifest',required=True);p.add_argument('--receipt');a=p.parse_args();root=Path(a.root).resolve()
 if a.action=='inventory':inventory(root,a.manifest)
 elif a.action=='check':check(root,json.loads(Path(a.manifest).read_text()));print('CHECK PASS')
 else:
  assert a.receipt;delete(root,a.manifest,a.receipt)
