import os
import paramiko,json,shlex
from pathlib import Path
b=Path(__file__).resolve().parent;r='/data1/users/liugang/src/eq-bpe/project/runs/stage1_latest_full_20261117';base='/data1/users/liugang/src/eq-bpe/project';c=paramiko.SSHClient();c.load_system_host_keys();c.connect('81.70.169.155',username='liugang',password=os.environ["PDE_SSH_PASSWORD"],look_for_keys=False,allow_agent=False,timeout=15);s=c.open_sftp()
for n in ['eqgpt_pure_case.py','eqgpt_pure_queue.py','eqgpt_pure_jobs.json']:s.put(str(b/n),r+'/'+n)
s.close()
# Verify the 12 final EqGPT checkpoints before any model is loaded.
check="from pathlib import Path;import json,hashlib;r=Path("+repr(r)+");v=json.loads((r/'EQGPT_VERIFIED_SOURCE.json').read_text());c=json.loads((r/'FINAL_EQGPT_CONFIG.json').read_text());h={x['path']:x['sha256'] for x in v};assert len(c['selected_model_records'])==12\nfor x in c['selected_model_records']:\n p=Path(x['directory'])/'best.pt';assert hashlib.sha256(p.read_bytes()).hexdigest()==h[str(p)]\nprint('CHECKPOINTS_VERIFIED',len(h))"
_,o,e=c.exec_command(base+'/.venv/bin/python -c '+shlex.quote(check));print(o.read().decode(),e.read().decode());assert o.channel.recv_exit_status()==0
launch="import subprocess,os,json,time;from pathlib import Path;r=Path("+repr(r)+");env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='GPU-ba72db90-47e9-38fd-0e9e-905c3b1798b5',PYTHONPATH=str(r/'src'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4');f=(r/'eqgpt-pure-supervisor.log').open('w');p=subprocess.Popen(["+repr(base+'/.venv/bin/python')+",'-u',str(r/'eqgpt_pure_queue.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);d=dict(pid=p.pid,root=str(r),gpu=3,tasks=96,concurrency=4,sampling='pure_model',time=time.time());(r/'eqgpt_pure_launch.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))"
_,o,e=c.exec_command(base+'/.venv/bin/python -c '+shlex.quote(launch));out=o.read().decode();print(out,e.read().decode());assert o.channel.recv_exit_status()==0;(b/'eqgpt_pure_launch.json').write_text(out);c.close()
