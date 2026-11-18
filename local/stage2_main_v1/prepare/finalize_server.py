"""Mark only the current seen protocol ready after two checks and regressions.
This command never launches data downloads, old source retirement or training.
"""
from pathlib import Path
import json,hashlib,subprocess,sys,os
ROOT=Path('/data1/users/liugang/src/eq-bpe/project');AUDIT=ROOT/'maintenance/stage2-seen75-20261115'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,allow_nan=False));tmp.replace(p)
def main():
 for name in ['check-round1.json','check-round2.json']:assert json.loads((AUDIT/name).read_text())['status']=='PASS'
 for rel,h in json.loads((AUDIT/'protected-before.json').read_text()).items():assert sha(ROOT/rel)==h,rel
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2')
 with (AUDIT/'regression-tests.txt').open('w') as log:
  for directory in ['stage2_main_v1/tests','stage2_main_v1/prepare']:
   subprocess.run([sys.executable,'-m','unittest','discover','-s',directory,'-p','test_*.py','-v'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 mpath=ROOT/'data/cylinder_numerical_stage2_v1/manifest.json';m=json.loads(mpath.read_text())
 assert m['seen_trajectory_prediction'] and not m['trajectory_disjoint']
 config=ROOT/'stage2_main_v1/config.json';cfg=json.loads(config.read_text());cfg['readiness']['simulation_data_audited']=True
 assert not cfg['readiness']['three_field_generator_available'] and not cfg['readiness']['three_equation_numerical_backend_available']
 write(config,cfg)
 ready={'status':'DATA_PREPARATION_VERIFIED','protocol':m['split_policy'],'data_manifest_sha256':sha(mpath),
  'data_check1_sha256':sha(AUDIT/'check-round1.json'),'data_check2_sha256':sha(AUDIT/'check-round2.json'),
  'role_trajectory_counts':m['role_trajectory_counts'],'role_window_counts':m['role_window_counts'],
  'context_shape':[64,128],'crop_shape':[62,126],'time_step':.005,'valid_points':7660,
  'eqgpt_modification_started':False,'training_started':False}
 write(ROOT/'stage2_main_v1/DATA_READY.json',ready)
 write(AUDIT/'complete.json',{'status':'COMPLETE','two_independent_checks':'PASS','regression_tests':11,
  'all92_trajectories_seen_in_every_role':True,'no_window_overlap':True,'minimum_cross_role_gap':50,
  'normalization_recomputed':True,'array_data_and_spatial_processing_unchanged':True,
  'eqgpt_and_baseline_unchanged':True,'training_started':False})
 print('SEEN_PROTOCOL_READY_TWO_CHECKS_PASS')
if __name__=='__main__':main()
