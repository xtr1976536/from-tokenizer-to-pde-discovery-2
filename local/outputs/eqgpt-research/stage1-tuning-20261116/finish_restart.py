import sys,shlex,json
from pathlib import Path
sys.path.insert(0,'/tmp')
from accept_remote import connect,BASE
b=Path(__file__).resolve().parent;r=BASE+'/runs/stage1_tuning_v96_128_160_20261116';c=connect();s=c.open_sftp()
p=r+'/pretrain_tune.py';text=s.open(p).read().decode().replace('ts,vs=encode(tr),encode(va);assert max(map(len,ts+vs))<=72','ts,vs=encode(tr),encode(va);positions=max(72,max(map(len,ts+vs)))').replace('build_models({a.arm:adapter},72,','build_models({a.arm:adapter},positions,').replace('layers=6,positions=72','layers=6,positions=positions')
with s.open(p,'w') as f:f.write(text)
s.close()
checks=[]
for scale in [212,636]:
 for split in ['811','622']:
  for vocab in [96,128,160]:checks.append(f'{BASE}/.venv/bin/python pretrain_tune.py --campaign {r} --job preflight --scale {scale} --split {split} --arm ast_bpe_{vocab} --seed 525 --prepare-only')
_,o,e=c.exec_command(f'cd {r} && export CUDA_VISIBLE_DEVICES=1 PYTHONPATH={r}/src OPENBLAS_NUM_THREADS=1; '+' && '.join(checks));print(o.read().decode(),e.read().decode());assert o.channel.recv_exit_status()==0
launch="import subprocess,os,json;from pathlib import Path;r=Path("+repr(r)+");env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='1',STAGE1_WORKER_CAP_GIB='8',PYTHONPATH=str(r/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='4');f=(r/'queue.log').open('w');p=subprocess.Popen(["+repr(BASE+'/.venv/bin/python')+",'-u',str(r/'tuning_queue.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);d=dict(pid=p.pid,root=str(r),gpu=1,jobs=76,vocabularies=[96,128,160],representative=128);(r/'launch.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))"
_,o,e=c.exec_command(BASE+'/.venv/bin/python -c '+shlex.quote(launch));out=o.read().decode();print(out,e.read().decode());assert o.channel.recv_exit_status()==0;(b/'launch.json').write_text(out);c.close()
