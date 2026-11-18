import sys,json,tarfile,shlex
from pathlib import Path
sys.path.insert(0,'/tmp')
from accept_remote import connect,BASE
b=Path(__file__).resolve().parent;r=BASE+'/runs/stage1_tuning_20261116'
with tarfile.open(b/'upstream.tar.gz','w:gz') as t:t.add(b/'upstream',arcname='upstream')
c=connect();s=c.open_sftp();s.put('stage2_main_v1/corpus_work/compact_ast_bpe.py',r+'/compact_ast_bpe.py')
for name in ['upstream.tar.gz','matrix.json','tuning_queue.py','pretrain_tune.py','selection.json','UPSTREAM_TABLES.md']:s.put(str(b/name),r+'/'+name)
s.close()
cmd=f'cd {r} && tar xzf upstream.tar.gz && ln -sfn {BASE}/native native && ln -sfn {BASE}/data data && CUDA_VISIBLE_DEVICES=1 PYTHONPATH={r}/src OPENBLAS_NUM_THREADS=1 {BASE}/.venv/bin/python pretrain_tune.py --campaign {r} --job revised-preflight --scale 212 --split 811 --arm ast_bpe_288 --seed 525 --prepare-only'
_,o,e=c.exec_command(cmd);print(o.read().decode());print(e.read().decode());assert o.channel.recv_exit_status()==0
cmd=f'cd {r} && nohup env CUDA_VISIBLE_DEVICES=1 STAGE1_WORKER_CAP_GIB=8 PYTHONPATH={r}/src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 {BASE}/.venv/bin/python -u tuning_queue.py > revised-queue.log 2>&1 < /dev/null & echo $!'
_,o,e=c.exec_command(cmd);pid=o.read().decode().strip();print('PID',pid);(b/'launch.json').write_text(json.dumps(dict(remote=r,pid=pid,stage='revised 4-cohort tuning',jobs=76,gpu=1),indent=2));c.close()
