import paramiko,json,io,tarfile,hashlib
from pathlib import Path
b=Path(__file__).resolve().parent
# Reuse the live application's SSH agent when available; connection is supplied below.
def fetch(c):
 r='/data1/users/liugang/src/eq-bpe/project/runs/stage1_tuning_v96_128_160_20261116'
 code="import io,tarfile,sys;from pathlib import Path;r=Path("+repr(r)+");t=tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz');[(t.add(p,arcname=str(p.relative_to(r)))) for p in sorted(r.glob('jobs/*/*.json'))];[(t.add(r/n,arcname=n)) for n in ['queue_status.json','matrix.json','pretrain_tune.py','selection.json','launch.json']];t.close()"
 import shlex
 _,o,e=c.exec_command('/data1/users/liugang/src/eq-bpe/project/.venv/bin/python -c '+shlex.quote(code));payload=o.read();err=e.read().decode();assert o.channel.recv_exit_status()==0,err
 (b/'records.tar.gz').write_bytes(payload)
 with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as t:
  for m in t.getmembers():
   assert not m.name.startswith('/') and '..' not in Path(m.name).parts
  t.extractall(b/'records')
 (b/'provenance.json').write_text(json.dumps(dict(remote=r,archive_sha256=hashlib.sha256(payload).hexdigest(),scope='training.json COMPLETE.json and code/config only; no weights or test data'),indent=2))
 print('Fetched',len(list((b/'records/jobs').glob('*/training.json'))),'histories',len(payload),'bytes')
