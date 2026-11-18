from pathlib import Path
import json,os,signal,time,shutil
r=Path(ROOT);launch=json.loads((r/'launch.json').read_text());pid=launch['pid'];proc=Path('/proc')/str(pid)
if proc.exists():
 args=(proc/'cmdline').read_bytes().split(b'\0');assert str(r/'supervise.py').encode() in args;os.kill(pid,signal.SIGSTOP)
# Freeze orchestration before taking the final state; stop only this campaign's EqGPT workers.
targets=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:a=(p/'cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if (str(r/'pretrain_tune.py').encode() in a or str(r/'search_case.py').encode() in a) and b'eqgpt_reference' in a:
  os.kill(int(p.name),signal.SIGTERM);targets.append(int(p.name))
if proc.exists():os.kill(pid,signal.SIGKILL)
time.sleep(1)
for pid in targets:
 p=Path('/proc')/str(pid)/'cmdline'
 if p.exists() and p.read_bytes():
  os.kill(pid,signal.SIGKILL)
time.sleep(.5)
for pid in targets:
 p=Path('/proc')/str(pid)/'cmdline';assert not p.exists() or not p.read_bytes()
removed=[];freed=0
# Scope: only EqGPT artifacts created in the newest campaign, never shared surrogate caches.
paths=list((r/'jobs').glob('*eqgpt_reference*'))+list((r/'pretrained').glob('*eqgpt_reference*'))+list((r/'logs').glob('*eqgpt_reference*'))
paths+=list((r/'search').glob('*/*/*/eqgpt_reference'))
for p in paths:
 if p.is_symlink():p.unlink()
 elif p.is_dir():
  freed+=sum(f.stat().st_size for f in p.rglob('*') if f.is_file());shutil.rmtree(p)
 elif p.exists():freed+=p.stat().st_size;p.unlink()
 removed.append(str(p.relative_to(r)))
for name in ['pretrain_status.json','queue_status.json','CAMPAIGN_FAILED.json','ALL_COMPLETE.json','pretrain_jobs.json']:
 p=r/name
 if p.exists():p.unlink();removed.append(name)
jobs=json.loads((r/'search_jobs.json').read_text());jobs=[j for j in jobs if j['arm']!='eqgpt_reference'];assert len(jobs)==576
(r/'search_jobs.json').write_text(json.dumps(jobs,indent=2))
receipt=dict(time=time.time(),status='EQGPT_CANCELLED_AND_REMOVED',stopped_pids=targets,removed=removed,bytes_removed=freed,ast_models_retained=36,ast_search_cases=576,shared_surrogates_preserved=True,old_archives_preserved=True)
(r/'eqgpt_cleanup_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
