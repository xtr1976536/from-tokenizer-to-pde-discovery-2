import os
import paramiko,shlex,json,tarfile,hashlib
from pathlib import Path
b=Path(__file__).resolve().parent;repo=b.parent/'repository-update-20261115';base='/data1/users/liugang/src/eq-bpe/project';r=base+'/runs/stage1_latest_full_20261117'
with tarfile.open(b/'legacy_source.tar.gz','w:gz') as t:t.add(repo/'src',arcname='src')
c=paramiko.SSHClient();c.load_system_host_keys();c.connect('81.70.169.155',username='liugang',password=os.environ["PDE_SSH_PASSWORD"],look_for_keys=False,allow_agent=False,timeout=15)
setup=r'''from pathlib import Path
import json,os,shutil,hashlib
r=Path(ROOT);base=Path(BASE);r.mkdir(exist_ok=False);(r/'logs').mkdir();(r/'pretrained').mkdir()
for name in ['data','eqgpt_original','native']:(r/name).symlink_to(base/name,target_is_directory=True)
previous=base/'runs/stage1_v96_v160_validation_20261117';ref=base/'runs/stage1_v128_confirmation_20261117'
(r/'upstream').symlink_to((previous/'upstream').resolve(),target_is_directory=True)
shutil.copy2(previous/'compact_ast_bpe.py',r/'compact_ast_bpe.py')
manifest=[]
for scale in [212,636]:
 for split in ['811','622']:
  for vocab in [96,128,160]:
   for seed in [525,526,527]:
    source=(ref/'jobs'/f'{scale}-{split}-v128-seed{seed}') if vocab==128 else (previous/'jobs'/f'{scale}-{split}-v{vocab}-selected-seed{seed}')
    t=json.loads((source/'training.json').read_text());complete=json.loads((source/'COMPLETE.json').read_text());s=t['settings']
    assert complete['epochs']==len(t['history']) and t['arm']==f'ast_bpe_{vocab}' and s['seed']==seed and s['lr']==(1e-4 if scale==212 else 5e-5) and s['l2_matrix']==(.001 if scale==212 else 0.)
    key=f'{scale}-{split}-ast_bpe_{vocab}-seed{seed}';target=r/'pretrained'/key;target.symlink_to(source,target_is_directory=True)
    manifest.append(dict(key=key,source=str(source),best_epoch=t['best_epoch'],sha256=hashlib.sha256((source/'best.pt').read_bytes()).hexdigest(),positions=s['positions']))
(r/'reused_checkpoints.json').write_text(json.dumps(manifest,indent=2));print('VERIFIED_REUSED',len(manifest))
for case in ['Wave_equation','Convection_diffusion_equation','KG_equation','Burgers_equation','Eq_6_2_12','PDE_divide','KdV_equation','Chaffee_Infante_equation']:
 folder=base/'data/mlp_cache'/case;quality=json.loads((folder/'surrogate_quality.json').read_text());assert hashlib.sha256((folder/'surrogate_cache.pt').read_bytes()).hexdigest()==quality['cache_sha256'];print('SURROGATE_HASH_PASS',case)
'''
_,o,e=c.exec_command(base+'/.venv/bin/python -c '+shlex.quote('ROOT='+repr(r)+'\nBASE='+repr(base)+'\n'+setup));print(o.read().decode(),e.read().decode());assert o.channel.recv_exit_status()==0
s=c.open_sftp()
for n in ['legacy_source.tar.gz','pretrain_tune.py','search_case.py','sampler.py','full_queue.py','pretrain_jobs.json','search_jobs.json','legacy_pins.json']:s.put(str(b/n),r+'/'+n)
s.close()
check=r'''from pathlib import Path
import json,hashlib,os
r=Path(ROOT);pins=json.loads((r/'legacy_pins.json').read_text())
for name,digest in pins.items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==digest,name
# Runtime-only atomic compilation publication; tokenizer behavior unchanged.
p=r/'src/math_tokenizer/frontend_v6.py';s=p.read_text();old="    if not target.exists():subprocess.run(['cc','-O3','-fPIC','-shared',str(source),'-o',str(target)],check=True,capture_output=True)"
new="    if not target.exists():\n        temporary=target.with_name(target.name+'.'+str(os.getpid())+'.tmp')\n        subprocess.run(['cc','-O3','-fPIC','-shared',str(source),'-o',str(temporary)],check=True,capture_output=True)\n        os.replace(temporary,target)"
assert old in s;p.write_text(s.replace(old,new));print('LEGACY_CORE_HASH_PASS',len(pins))
'''
_,o,e=c.exec_command('cd '+r+' && tar xzf legacy_source.tar.gz && '+base+'/.venv/bin/python -c '+shlex.quote('ROOT='+repr(r)+'\n'+check));print(o.read().decode(),e.read().decode());assert o.channel.recv_exit_status()==0
# Actual old budget loop, reward, checkpoint loading and 5-epoch continuation on GPU1.
cmd=f'cd {r} && CUDA_VISIBLE_DEVICES=GPU-e857f4d0-daa6-f33d-3dc8-927f15ab7d59 OPENBLAS_NUM_THREADS=4 PYTHONPATH={r}/src {base}/.venv/bin/python -u search_case.py --scale 212 --split 811 --seed 525 --arm ast_bpe_96 --random-fraction 0 --case Wave_equation --smoke'
_,o,e=c.exec_command(cmd);out=o.read().decode();err=e.read().decode();print(out,err);(b/'smoke.log').write_text(out+err);assert o.channel.recv_exit_status()==0
(b/'remote.json').write_text(json.dumps(dict(remote=r,base=base),indent=2));c.close()
