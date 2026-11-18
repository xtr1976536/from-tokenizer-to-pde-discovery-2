import sys,json,shlex,time
from pathlib import Path
sys.path.insert(0,'/tmp')
from accept_remote import connect,BASE
b=Path(__file__).resolve().parent;old=BASE+'/runs/stage1_tuning_20261116';new=BASE+'/runs/stage1_tuning_v96_128_160_20261116'
c=connect()
code=r'''import os,signal,time,json
from pathlib import Path
root=Path(OLD);targets=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:args=(p/'cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if any(x.decode(errors='replace')==str(root/'tuning_queue.py') for x in args):targets.append(int(p.name))
for pid in targets:os.kill(pid,signal.SIGTERM)
time.sleep(.5)
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:args=(p/'cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if str(root/'pretrain_tune.py').encode() in args:
  pid=int(p.name);os.kill(pid,signal.SIGTERM);targets.append(pid)
time.sleep(1)
alive=[]
for pid in targets:
 try:
  if (Path('/proc')/str(pid)/'cmdline').read_bytes():alive.append(pid)
 except OSError:pass
assert not alive,alive
receipt=dict(status='CANCELLED_SUPERSEDED',pids=targets,reason='User fixed vocabularies to 96,128,160; restart from scratch',replacement=NEW,time=time.time())
(root/'CANCELLED.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''
_,o,e=c.exec_command(BASE+'/.venv/bin/python -c '+shlex.quote('OLD='+repr(old)+'\nNEW='+repr(new)+'\n'+code));out=o.read().decode();err=e.read().decode();print(out,err);assert o.channel.recv_exit_status()==0
(b/'CANCELLED.json').write_text(out)
# Same matrix and schedule, replacing representative vocabulary only.
jobs=json.loads((b/'matrix.json').read_text())
for j in jobs:j['job']=j['job'].replace('v288','v128')
(b/'matrix-v128.json').write_text(json.dumps(jobs,indent=2));queue=(b/'tuning_queue.py').read_text().replace('ast_bpe_288','ast_bpe_128');(b/'tuning_queue-v128.py').write_text(queue)
setup="from pathlib import Path;import shutil;r=Path("+repr(new)+");o=Path("+repr(old)+");r.mkdir(exist_ok=False);[(r/n).symlink_to(o/n,target_is_directory=True) for n in ['src','upstream','native','data','eqgpt_original']];[(shutil.copy2(o/n,r/n)) for n in ['pretrain_tune.py','compact_ast_bpe.py']];print(r)"
_,o,e=c.exec_command(BASE+'/.venv/bin/python -c '+shlex.quote(setup));print(o.read().decode(),e.read().decode());assert o.channel.recv_exit_status()==0
s=c.open_sftp();s.put(str(b/'matrix-v128.json'),new+'/matrix.json');s.put(str(b/'tuning_queue-v128.py'),new+'/tuning_queue.py')
selection=dict(selected=[96,128,160],selection='explicit user instruction; supersedes metric-derived selection',representative=128,other_settings='unchanged; four cohorts; 76 initial tuning jobs; selected settings verified on 96 and160')
(b/'selection.json').write_text(json.dumps(selection,indent=2));s.put(str(b/'selection.json'),new+'/selection.json');s.close()
# Preflight every chosen tokenizer in every cohort before restart.
checks=[]
for scale in [212,636]:
 for split in ['811','622']:
  for vocab in [96,128,160]:checks.append(f'{BASE}/.venv/bin/python pretrain_tune.py --campaign {new} --job preflight --scale {scale} --split {split} --arm ast_bpe_{vocab} --seed 525 --prepare-only')
command=f'cd {new} && export CUDA_VISIBLE_DEVICES=1 PYTHONPATH={new}/src OPENBLAS_NUM_THREADS=1; '+' && '.join(checks)
_,o,e=c.exec_command(command);print(o.read().decode(),e.read().decode());assert o.channel.recv_exit_status()==0
# Detach using Popen so SSH channel closure is independent of the supervisor.
launch="import subprocess,os,json;from pathlib import Path;r=Path("+repr(new)+");env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='1',STAGE1_WORKER_CAP_GIB='8',PYTHONPATH=str(r/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='4');f=(r/'queue.log').open('w');p=subprocess.Popen(["+repr(BASE+'/.venv/bin/python')+",'-u',str(r/'tuning_queue.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);d=dict(pid=p.pid,root=str(r),gpu=1,jobs=76,vocabularies=[96,128,160],representative=128);(r/'launch.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))"
_,o,e=c.exec_command(BASE+'/.venv/bin/python -c '+shlex.quote(launch));out=o.read().decode();print(out,e.read().decode());assert o.channel.recv_exit_status()==0;(b/'launch.json').write_text(out);c.close()
