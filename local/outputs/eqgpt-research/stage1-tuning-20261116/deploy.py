from pathlib import Path
import sys,tarfile,shlex,json,hashlib
sys.path.insert(0,'/tmp')
from accept_remote import connect,BASE
b=Path(__file__).resolve().parent;src=Path('outputs/eqgpt-research/repository-update-20261115');remote=BASE+'/runs/stage1_tuning_20261116'
with tarfile.open(b/'source.tar.gz','w:gz') as t:
 t.add(src/'src',arcname='src')
c=connect();s=c.open_sftp()
_,o,e=c.exec_command('mkdir -p '+remote);assert o.channel.recv_exit_status()==0
for name in ['source.tar.gz','matrix.json','tuning_queue.py','pretrain_tune.py']:s.put(str(b/name),remote+'/'+name)
for scale in (212,636):
 _,o,e=c.exec_command(f'mkdir -p {remote}/corpora/{scale}');assert o.channel.recv_exit_status()==0
 for name in ['sources.jsonl']:s.put(str(src/f'restarts/stage01_20261113/stage1/corpora/{scale}'/name),f'{remote}/corpora/{scale}/{name}')
 s.put(str(src/f'restarts/stage01_20261113/stage1/{scale}/split.json'),f'{remote}/corpora/{scale}/expected_split.json')
s.put(str(src/'restarts/stage01_20261113/stage1/assets/legacy_alphabet_212.json'),remote+'/legacy_alphabet_212.json');s.close()
cmd=f'cd {remote} && tar xzf source.tar.gz && CUDA_VISIBLE_DEVICES=1 PYTHONPATH={remote}/src {BASE}/.venv/bin/python pretrain_tune.py --campaign {remote} --job preflight --scale 212 --arm ast_bpe_300 --seed 525 --prepare-only && CUDA_VISIBLE_DEVICES=1 PYTHONPATH={remote}/src {BASE}/.venv/bin/python pretrain_tune.py --campaign {remote} --job preflight --scale 636 --arm ast_bpe_300 --seed 525 --prepare-only'
_,o,e=c.exec_command(cmd);print(o.read().decode());print(e.read().decode());assert o.channel.recv_exit_status()==0
# Exact historical split equivalence before any optimization.
check="import json;from pathlib import Path;r=Path("+repr(remote)+");assert all(json.loads((r/f'prepared/{s}/split.json').read_text())==json.loads((r/f'corpora/{s}/expected_split.json').read_text()) for s in [212,636]);print('HISTORICAL_SPLITS_MATCH')"
_,o,e=c.exec_command(BASE+'/.venv/bin/python -c '+shlex.quote(check));print(o.read().decode());print(e.read().decode());assert o.channel.recv_exit_status()==0
cmd=f'cd {remote} && nohup env CUDA_VISIBLE_DEVICES=1 STAGE1_WORKER_CAP_GIB=8 PYTHONPATH={remote}/src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 {BASE}/.venv/bin/python -u tuning_queue.py > queue.log 2>&1 < /dev/null & echo $!'
_,o,e=c.exec_command(cmd);pid=o.read().decode().strip();print('QUEUE_PID',pid);(b/'launch.json').write_text(json.dumps(dict(remote=remote,pid=pid,gpu=1,jobs=38,concurrency=2),indent=2));c.close()
