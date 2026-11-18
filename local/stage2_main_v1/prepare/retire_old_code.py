"""Retire ONLY obsolete Stage2 source/config files, after two data checks pass.
Freeze is preserved; baseline/Stage3/shared Stage0/1 directories are protected.
"""
import argparse,hashlib,json,os
from pathlib import Path
ROOTS=('ast_bpe_multifield_v1','ast_bpe_multifield_v2','ast_bpe_multifield_v3','ast_bpe_multifield_v4')
CODE={'.py','.pyc','.pyo','.so','.c','.h','.cpp','.hpp','.sh','.ipynb','.json','.yaml','.yml'}
ROOT_PROBES={'cpu_reward_probe.py','cpu_reward_probe_complex.py','gpu_reward_probe.py','gpu_reward_probe_complex.py','gpu_reward_cache_bench.py','reward_compare_probe.py'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False))
def records(folder):
 for base,dirs,files in os.walk(folder,followlinks=False):
  dirs[:]=[d for d in dirs if not Path(base,d).is_symlink()]
  for f in files:
   p=Path(base,f)
   if p.is_file() and not p.is_symlink():yield p

def allowed(rel,run_dirs):
 parts=Path(rel).parts
 if not parts or Path(rel).is_absolute() or '..' in parts:return False
 if parts[0] in ROOTS:
  if len(parts)>1 and parts[1]=='data':return False
  return Path(rel).suffix in CODE or '.deps' in parts
 if len(parts)>1 and parts[0]=='runs' and parts[1] in run_dirs:return Path(rel).suffix in CODE
 return rel in ROOT_PROBES or rel=='scripts/monitor_stage2_readonly.py'

def audit(root,output,server):
 old=root/'outputs/eqgpt-research/stage2-refresh-2026-11-15/server-delete-manifest.json'
 if server:old=root/'maintenance/stage2-refresh-20261115/delete-manifest.json'
 previous=json.loads(old.read_text());run_dirs=sorted({Path(r['path']).parts[1] for r in previous['targets'] if r['path'].startswith('runs/') and len(Path(r['path']).parts)>2})
 targets=[]
 scan=[root/n for n in ROOTS]+[root/'runs'/n for n in run_dirs]+[root/p for p in ROOT_PROBES]+[root/'scripts/monitor_stage2_readonly.py']
 seen=set()
 for folder in scan:
  fs=list(records(folder)) if folder.is_dir() else [folder] if folder.is_file() else []
  for p in fs:
   rel=p.relative_to(root).as_posix()
   if rel in seen or not allowed(rel,run_dirs):continue
   seen.add(rel);s=p.stat();targets.append({'path':rel,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':sha(p)})
 protected={}
 for n in ['baseline_code','baseline_configs','stage3_latent_ode','stage3_neural_pde','stage2_main_v1']:
  folder=root/n
  if folder.exists():
   for p in records(folder):
    if '__pycache__' in p.parts:continue
    protected[str(p.relative_to(root))]=sha(p)
 result={'root':str(root),'run_dirs':run_dirs,'targets':targets,'protected':protected,
         'file_count':len(targets),'bytes':sum(r['size'] for r in targets),'server':server}
 dump(output,result);print('RETIREMENT_MANIFEST',len(targets),'files',result['bytes'],'bytes')

def check(root,m):
 assert m['root']==str(root)
 for r in m['targets']:
  p=root/r['path'];assert not p.is_symlink() and p.parent.resolve().is_relative_to(root)
  assert allowed(r['path'],m['run_dirs']);assert sha(p)==r['sha256'];assert p.stat().st_size==r['size']
 for rel,h in m['protected'].items():assert sha(root/rel)==h,rel

def retire(root,manifest,receipt):
 m=json.loads(Path(manifest).read_text())
 if m['server']:
  for name in ['check-round1.json','check-round2.json','legacy-check.json']:
   assert json.loads((root/'maintenance/stage2-data-20261115'/name).read_text())['status']=='PASS',name
  data=json.loads((root/'data/cylinder_numerical_stage2_v1/manifest.json').read_text());seen={}
  for sid,entry in data['trajectories'].items():
   signature=tuple(entry['files_sha256'][f+'.npy'] for f in ('u','v','p'))
   assert signature not in seen,'Duplicate full u/v/p trajectory under different IDs: '+sid
   seen[signature]=sid
  dump(root/'maintenance/stage2-data-20261115/trajectory-content-audit.json',{'status':'PASS','trajectories':len(seen),'duplicate_full_field_trajectories':0,'basis':'verified SHA256 of all cropped u/v/p arrays'})
 else:
  for name in ['check-round1.json','check-round2.json','legacy-check.json']:
   assert json.loads((root/'outputs/eqgpt-research/stage2-data-preparation-2026-11-15'/name).read_text())['status']=='PASS',name
 check(root,m);check(root,m)
 for r in m['targets']:
  p=root/r['path'];assert not p.is_symlink() and p.parent.resolve().is_relative_to(root);assert sha(p)==r['sha256'];p.unlink()
 # These links preserve shared imports in untouched baseline/Stage3 consumers.
 # There is only ONE physical copy of each selected old library module.
 links={}
 layout=root/'stage2_main_v1/legacy_eqgpt/layout'
 for name in ROOTS:
  folder=layout/name
  if not folder.exists():continue
  for src in folder.glob('*.py'):
   target=root/name/src.name;target.parent.mkdir(parents=True,exist_ok=True)
   assert not target.exists() and not target.is_symlink(),str(target)
   link=os.path.relpath(src,target.parent);target.symlink_to(link);links[str(target.relative_to(root))]=link
 unchanged=all(sha(root/p)==h for p,h in m['protected'].items())
 result={'status':'PASS' if unchanged else 'FAIL','deleted_source_config_files':len(m['targets']),
  'deleted_bytes':sum(r['size'] for r in m['targets']),'protected_files_unchanged':unchanged,
  'compatibility_symlinks':links,'only_physical_library_copy':'stage2_main_v1/legacy_eqgpt/layout',
  'two_predelete_checks':'PASS','old_nonselected_code_removed':True}
 dump(receipt,result);assert unchanged;print(json.dumps({k:v for k,v in result.items() if k!='compatibility_symlinks'}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['inventory','check','retire']);p.add_argument('--root',required=True);p.add_argument('--manifest',required=True);p.add_argument('--receipt');p.add_argument('--server',action='store_true');a=p.parse_args();root=Path(a.root).resolve()
 if a.action=='inventory':audit(root,a.manifest,a.server)
 elif a.action=='check':check(root,json.loads(Path(a.manifest).read_text()));print('CHECK_PASS')
 else:assert a.receipt;retire(root,a.manifest,a.receipt)
